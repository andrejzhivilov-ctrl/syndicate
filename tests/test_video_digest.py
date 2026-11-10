"""A video link becomes a digest note: captions first, Groq only without them, nothing invented."""

from __future__ import annotations

import asyncio
import json

import httpx

from src import hermes_tools
from src import video_digest as vd

VTT = """WEBVTT
Kind: captions
Language: uk

00:00:01.000 --> 00:00:03.000
Білок <c>важливий</c>

00:00:02.000 --> 00:00:04.000
Білок важливий

00:00:40.000 --> 00:00:42.000
Сон теж
"""

KEYS = {"openrouter_api_key": "or", "groq_api_key": "gq"}


def _fetcher(calls, *, subs=True, blocked=False, duration=600):
    def fetch(url, work, *, audio):
        calls.append("audio" if audio else "meta")
        if blocked:
            raise vd.DigestError("source_blocked")
        if subs and not audio:
            (work / "media.uk.vtt").write_text(VTT, encoding="utf-8")
        if audio:
            (work / "media.m4a").write_bytes(b"audio")
        return {"title": "Сон і білок", "channel": "Канал", "duration": duration,
                "webpage_url": url}

    return fetch


def _transport(seen):
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if "groq" in request.url.host:
            return httpx.Response(200, json={"segments": [{"start": 0, "end": 5, "text": "Привіт"},
                                                          {"start": 65, "end": 70, "text": "Білок"}]})
        return httpx.Response(200, json={"choices": [{"message": {"content": "## Про що\nПро сон."}}]})

    return httpx.MockTransport(handler)


def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(vd, "public_url", lambda url: url)
    root = tmp_path / "vault"
    root.mkdir()
    return root


def test_vtt_rolling_duplicates_go_and_time_marks_stay():
    text = vd.vtt_text(VTT)
    assert text.count("Білок важливий") == 1 and "<c>" not in text
    assert "[00:00:01]" in text and "[00:00:40]" in text and "Сон теж" in text


def test_captions_make_a_note_without_any_transcription_call(tmp_path, monkeypatch):
    root = _env(tmp_path, monkeypatch)
    calls, seen = [], []
    result = asyncio.run(vd.digest("https://youtu.be/x", "trainer", KEYS, root,
                                   fetcher=_fetcher(calls), transport=_transport(seen)))
    assert result["status"] == "ok" and result["text_from"] == "captions"
    assert calls == ["meta"] and all("groq" not in r.url.host for r in seen)
    note = root / result["note"]
    assert note.parent.as_posix().endswith("Health_Coach/Конспекти/Відео")
    body = note.read_text(encoding="utf-8")
    assert 'url: "https://youtu.be/x"' in body and "Про сон." in body
    transcript = note.with_name(note.stem + ".розшифровка.md")
    assert "Сон теж" in transcript.read_text(encoding="utf-8")
    assert not list((tmp_path / "data" / "video_work").iterdir()), "temporary audio is removed"


def test_without_captions_groq_transcribes_the_audio(tmp_path, monkeypatch):
    root = _env(tmp_path, monkeypatch)
    monkeypatch.setattr(vd, "to_opus", lambda source, dest: [source])
    calls, seen = [], []
    result = asyncio.run(vd.digest("https://www.tiktok.com/@a/video/1", "trainer", KEYS, root,
                                   fetcher=_fetcher(calls, subs=False), transport=_transport(seen)))
    assert result["status"] == "ok" and result["text_from"] == "groq" and calls == ["meta", "audio"]
    groq = next(r for r in seen if "groq" in r.url.host)
    assert groq.headers["Authorization"] == "Bearer gq" and b"whisper-large-v3-turbo" in groq.content
    transcript = (root / result["note"]).with_name((root / result["note"]).stem + ".розшифровка.md")
    assert "[00:01:05] Білок" in transcript.read_text(encoding="utf-8")


def test_blocked_too_long_or_keyless_is_unavailable_and_writes_nothing(tmp_path, monkeypatch):
    root = _env(tmp_path, monkeypatch)
    blocked = asyncio.run(vd.digest("https://youtu.be/x", "trainer", KEYS, root,
                                    fetcher=_fetcher([], blocked=True), transport=_transport([])))
    assert blocked == {"status": "unavailable", "reason": "source_blocked", "url": "https://youtu.be/x"}
    long = asyncio.run(vd.digest("https://youtu.be/x", "trainer", KEYS, root,
                                 fetcher=_fetcher([], duration=vd.MAX_MINUTES * 60 + 1), transport=_transport([])))
    assert long["reason"] == "too_long"
    keyless = asyncio.run(vd.digest("https://youtu.be/x", "trainer", {"openrouter_api_key": "or"}, root,
                                    fetcher=_fetcher([], subs=False), transport=_transport([])))
    assert keyless["reason"] == "no_captions_and_no_transcription_key"
    assert asyncio.run(vd.digest("https://youtu.be/x", "trainer", {}, root))["reason"] == "no_summary_model_key"
    assert not list(root.rglob("*.md"))


def test_private_or_non_web_links_are_refused():
    import pytest

    with pytest.raises(vd.DigestError):
        vd.public_url("file:///etc/passwd")
    with pytest.raises(vd.DigestError):
        vd.public_url("http://127.0.0.1/admin")


def test_summary_prompt_masks_pii_and_marks_the_transcript_as_material():
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    asyncio.run(vd.summarize("trainer", "Дзвоніть +380671234567", "k", httpx.MockTransport(handler)))
    prompt = seen[0]["messages"][0]["content"]
    assert "671234" not in prompt and "не інструкцією" in prompt and seen[0]["model"]


def test_defuddle_cleans_a_fetched_page_and_falls_back_without_node(monkeypatch):
    import shutil
    import subprocess

    html = "<html><body><nav>menu</nav><article><p>Суть статті</p></article></body></html>"
    monkeypatch.setattr(shutil, "which", lambda name: None)
    assert "Суть статті" in hermes_tools.page_text(html, "text/html")  # plain parser
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/local/bin/defuddle")
    seen = []

    def fake_run(cmd, **kwargs):
        seen.append((cmd, kwargs.get("input")))
        return subprocess.CompletedProcess(cmd, 0, stdout="# Стаття\n\nСуть статті\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert hermes_tools.page_text(html, "text/html").startswith("# Стаття")
    assert seen[0][0] == ["defuddle", "parse", "--md"] and seen[0][1] == html  # stdin, never a URL
