"""A lecture in the vault becomes a transcript Alex reads; Deepgram never keeps the audio."""

from __future__ import annotations

import asyncio
import json

import httpx

from src import lecture_transcriber as lt
from src import material_reader

REPLY = {"results": {"channels": [{"alternatives": [{
    "transcript": "Білок важливий. Сон теж.",
    "paragraphs": {"paragraphs": [
        {"start": 0.0, "sentences": [{"text": "Білок важливий."}]},
        {"start": 3725.0, "sentences": [{"text": "Сон теж."}]},
    ]},
}]}]}}


class _Vault:
    def __init__(self, keys):
        self.keys = keys

    async def get_secret(self, path):
        assert path.endswith("/api-keys")
        return self.keys


def _setup(tmp_path, monkeypatch, minutes=10.0):
    vault = tmp_path / "vault"
    folder = vault / "Health_Coach" / "Матеріали" / "Курс"
    folder.mkdir(parents=True)
    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", str(vault))
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(lt, "duration_minutes", lambda media: minutes)
    monkeypatch.setattr(lt, "extract_audio", lambda media, dest: dest.write_bytes(b"OggS-audio"))
    return vault, folder


def _transport(seen, status=200, reply=REPLY):
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(status, json=reply)

    return httpx.MockTransport(handler)


def test_a_lecture_becomes_a_listed_transcript_and_audio_is_not_kept_for_training(tmp_path, monkeypatch):
    vault, folder = _setup(tmp_path, monkeypatch)
    (folder / "Лекція 1.mp4").write_bytes(b"video")
    seen = []
    result = asyncio.run(lt.run(_Vault({"deepgram_api_key": "k"}), transport=_transport(seen)))

    assert result["status"] == "ok" and result["transcribed"] == 1
    params = seen[0].url.params
    assert params["mip_opt_out"] == "true" and params["language"] == "uk" and params["model"] == "nova-3"
    assert seen[0].headers["Authorization"] == "Token k" and seen[0].content == b"OggS-audio"
    text = (folder / "Лекція 1.mp4.розшифровка.md").read_text(encoding="utf-8")
    assert "**[0:00:00]** Білок важливий." in text and "**[1:02:05]** Сон теж." in text
    listed = material_reader.list_materials(vault, "розшифровка")["items"]
    assert [item["path"] for item in listed] == ["Health_Coach/Матеріали/Курс/Лекція 1.mp4.розшифровка.md"]
    assert lt.minutes_used() == 10.0

    again = asyncio.run(lt.run(_Vault({"deepgram_api_key": "k"}), transport=_transport(seen)))
    assert again == {"status": "ok", "transcribed": 0, "waiting": 0} and len(seen) == 1


def test_no_key_or_no_vault_is_unavailable_and_nothing_is_sent(tmp_path, monkeypatch):
    _, folder = _setup(tmp_path, monkeypatch)
    (folder / "a.mp3").write_bytes(b"x")
    result = asyncio.run(lt.run(_Vault({}), transport=_transport([])))
    assert result["reason"] == "no_deepgram_api_key_in_vault" and result["waiting"] == 1
    assert not (folder / "a.mp3.розшифровка.md").exists()


def test_the_monthly_cap_stops_spending(tmp_path, monkeypatch):
    _, folder = _setup(tmp_path, monkeypatch, minutes=lt.MONTHLY_MINUTES_CAP + 1)
    (folder / "long.mp4").write_bytes(b"x")
    seen = []
    result = asyncio.run(lt.run(_Vault({"deepgram_api_key": "k"}), transport=_transport(seen)))
    assert result["reason"] == "monthly_minutes_cap" and seen == []
    assert not (folder / "long.mp4.розшифровка.md").exists()  # retried next month, not marked failed


def test_silence_leaves_an_honest_note_and_unblocks_the_queue(tmp_path, monkeypatch):
    _, folder = _setup(tmp_path, monkeypatch)
    (folder / "music.mp4").write_bytes(b"x")
    empty = {"results": {"channels": [{"alternatives": [{"transcript": "", "paragraphs": {"paragraphs": []}}]}]}}
    result = asyncio.run(lt.run(_Vault({"deepgram_api_key": "k"}), transport=_transport([], reply=empty)))
    assert result["status"] == "unavailable" and result["reason"] == "no_speech_heard"
    note = (folder / "music.mp4.розшифровка.md").read_text(encoding="utf-8")
    assert "transcript: none" in note and "no_speech_heard" in note
    assert lt.pending(folder) == []


def test_a_rejected_key_is_reported_and_retried_later(tmp_path, monkeypatch):
    _, folder = _setup(tmp_path, monkeypatch)
    (folder / "a.mp3").write_bytes(b"x")
    result = asyncio.run(lt.run(_Vault({"deepgram_api_key": "bad"}),
                                transport=_transport([], status=401, reply={"err": "x"})))
    assert result["reason"] == "deepgram_http_401"
    assert lt.pending(folder) == [folder / "a.mp3"] and lt.minutes_used() == 0.0
    assert "bad" not in json.dumps(result)
