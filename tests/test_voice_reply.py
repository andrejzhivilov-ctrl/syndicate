"""Owner's voice notes: OpenAI STT with local fallback, Respeecher voice replies."""
from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

import httpx

from src.telegram_gateway import TelegramGateway, extract_message
from src.voice_reply import (
    TTS_MAX_CHARS,
    RespeecherTTS,
    pronounceable,
    spoken_text,
    transcribe,
    voice_for,
    wants_voice,
)

OWNER = "523"


def _voice_update(duration=4, file_size=9000):
    return {"update_id": 2, "message": {"message_id": 9, "from": {"id": int(OWNER)},
                                       "chat": {"id": int(OWNER), "type": "private"},
                                       "voice": {"file_id": "AwAD-voice", "duration": duration,
                                                 "file_size": file_size, "mime_type": "audio/ogg"}}}


def test_voice_note_is_extracted_as_a_file_reference_only():
    message = extract_message(_voice_update())
    assert message["kind"] == "voice" and message["file_id"] == "AwAD-voice"
    assert message["text"] == "" and message["duration"] == 4
    assert extract_message({"message": {"from": {"id": 1}, "chat": {"id": 1}, "sticker": {}}}) is None


def test_openai_transcribes_first_with_the_registry_model():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"text": " Привіт, Фіне "})

    text, provider = asyncio.run(transcribe(b"ogg", {"openai_api_key": "sk-test"}, transport=httpx.MockTransport(handler)))
    assert (text, provider) == ("Привіт, Фіне", "openai")
    assert seen[0].url.host == "api.openai.com" and b"gpt-4o-mini-transcribe" in seen[0].content
    assert seen[0].headers["Authorization"] == "Bearer sk-test"


def test_local_whisper_is_the_fallback_and_total_failure_is_none():
    def flaky(request: httpx.Request) -> httpx.Response:
        if request.url.host == "api.openai.com":
            return httpx.Response(500)
        return httpx.Response(200, json={"text": "з локального"})

    assert asyncio.run(transcribe(b"ogg", {"openai_api_key": "k"}, transport=httpx.MockTransport(flaky))) == (
        "з локального", "whisper_local")
    down = httpx.MockTransport(lambda request: httpx.Response(503))
    assert asyncio.run(transcribe(b"ogg", {}, transport=down)) == (None, "none")


def test_each_agent_keeps_one_voice_matching_its_gender():
    voices = [{"id": "olena", "gender": "female"}, {"id": "oksana", "gender": "female"},
              {"id": "taras", "gender": "male"}, {"id": "ivan", "gender": "male"}]
    assert voice_for("kira", voices) in {"olena", "oksana"}
    assert voice_for("oscar", voices) in {"taras", "ivan"}
    assert voice_for("oscar", voices) == voice_for("oscar", list(reversed(voices)))
    assert voice_for("eva", []) is None


def test_agents_speak_with_the_voices_the_operator_picked():
    # Respeecher's ua-rt /voices has no gender field: the old gender filter fell
    # through to a hash over all voices, so agents got arbitrary voices.
    voices = [{"id": v, "full_name": v} for v in (
        "olesia-media", "mariia-audiobook", "yevhen-audiobook", "ihoreo-conversation",
        "oleksandr-commercial", "yevhen-commercial", "dmytro-conversation")]
    assert voice_for("eva", voices) == "olesia-media"
    assert voice_for("kira", voices) == "mariia-audiobook"
    assert voice_for("sam", voices) == "yevhen-audiobook"
    assert voice_for("trainer", voices) == "ihoreo-conversation"
    assert voice_for("jack", voices) == "oleksandr-commercial"
    assert voice_for("fin", voices) == "yevhen-commercial"
    assert voice_for("oscar", voices) == "yevhen-commercial"
    # A retired voice still gets a real one, never silence or fake audio.
    assert voice_for("eva", [{"id": "dmytro-conversation"}]) == "dmytro-conversation"


def test_replies_are_text_unless_the_owner_asks_for_voice():
    for asked in ("Відповідай мені голосом, що по системі?", "скажи голосом погоду", "озвуч звіт",
                  "Voice on, будь ласка", "Голосове повідомлення чекаю"):
        assert wants_voice(asked), asked
    for plain in ("Що по системі?", "Запиши ідею про голосування", "", "покажи звіт"):
        assert not wants_voice(plain), plain


def test_english_terms_are_spelled_for_the_ukrainian_voice():
    spoken = spoken_text("Звіт у Obsidian і Google Drive, API працює, CI зелений, OKR не чіпаємо.")
    assert "Обсідіан" in spoken and "Ґуґл Драйв" in spoken and "ей-пі-ай" in spoken and "сі-ай" in spoken
    assert "OKR" in spoken  # not in the dictionary: left as is, never guessed
    assert pronounceable("APIs і n8n-флоу") == "APIs і n8n-флоу"  # only whole words


def test_respeecher_uses_the_ukrainian_model_and_never_fakes_audio():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if request.url.path.endswith("/voices"):
            return httpx.Response(200, json=[{"id": "olena", "gender": "female"}])
        return httpx.Response(200, content=b"RIFFwav")

    tts = RespeecherTTS("rk", transport=httpx.MockTransport(handler))
    assert asyncio.run(tts.synthesize("eva", "Добрий ранок")) == b"RIFFwav"
    assert all("/tts/ua-rt/" in str(c.url) and c.headers["X-API-Key"] == "rk" for c in calls)
    assert json.loads(calls[-1].content) == {"transcript": "Добрий ранок", "voice": {"id": "olena"}}

    empty = RespeecherTTS("rk", transport=httpx.MockTransport(lambda r: httpx.Response(200, json=[])))
    assert asyncio.run(empty.synthesize("eva", "Привіт")) is None
    failing = RespeecherTTS("rk", transport=httpx.MockTransport(lambda r: httpx.Response(402)))
    assert asyncio.run(failing.synthesize("eva", "Привіт")) is None


def test_voiced_text_is_capped_for_cost():
    long_reply = "слово " * 1000
    voiced = spoken_text(long_reply)
    assert len(voiced) <= TTS_MAX_CHARS and voiced.endswith("у повідомленні вище.")
    assert spoken_text(" Коротко. ") == "Коротко."


class _Vault:
    async def get_secret(self, path):
        return {"bot_token": "123:abc"} if path.endswith("/telegram/fin") else {}


def test_gateway_downloads_voice_within_the_size_limit_and_sends_voice():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        if request.url.path.endswith("/getFile"):
            return httpx.Response(200, json={"ok": True, "result": {"file_path": "voice/f.oga", "file_size": 7}})
        if "/file/bot" in request.url.path:
            return httpx.Response(200, content=b"oggdata")
        return httpx.Response(200, json={"ok": True})

    gw = TelegramGateway(_Vault(), transport=httpx.MockTransport(handler))
    assert asyncio.run(gw.download_file("fin", "AwAD", max_bytes=100)) == b"oggdata"
    assert asyncio.run(gw.download_file("fin", "AwAD", max_bytes=3)) is None
    assert asyncio.run(gw.download_file("eva", "AwAD", max_bytes=100)) is None  # no token
    assert asyncio.run(gw.send_voice("fin", OWNER, b"ogg")) is True
    assert seen[-1].endswith("/sendVoice")


class _Gateway:
    def __init__(self, audio=b"ogg"):
        self.audio, self.sent, self.voices = audio, [], []

    async def download_file(self, agent_id, file_id, max_bytes):
        return self.audio

    async def send(self, agent_id, chat_id, text):
        self.sent.append(text)
        return True

    async def send_voice(self, agent_id, chat_id, ogg):
        self.voices.append(ogg)
        return True


class _Orch:
    def __init__(self):
        self.payloads = []

    async def handle_webhook(self, source, payload):
        self.payloads.append(payload)
        return {"status": "completed", "result": {"response": "Бюджет — 370 доларів."}}


def _state(gateway, keys):
    class Vault:
        async def get_secret(self, path):
            return keys

    return SimpleNamespace(telegram_gateway=gateway, orchestrator=_Orch(), vault_client=Vault(), respeecher=None)


def test_voice_note_gets_transcript_text_reply_and_voice_reply(monkeypatch):
    import agent_runner

    async def fake_transcribe(audio, keys):
        return "Який бюджет?", "openai"

    class FakeTTS:
        def __init__(self, key):
            self.key = key

        async def synthesize(self, agent_id, text):
            return b"wav:" + text.encode()

    async def fake_ogg(wav):
        return b"ogg:" + wav

    monkeypatch.setattr(agent_runner, "transcribe", fake_transcribe)
    monkeypatch.setattr(agent_runner, "RespeecherTTS", FakeTTS)
    monkeypatch.setattr(agent_runner, "wav_to_ogg_opus", fake_ogg)
    gw = _Gateway()
    state = _state(gw, {"respeecher_api_key": "rk"})
    asyncio.run(agent_runner._telegram_voice(state, "fin", extract_message(_voice_update())))
    assert state.orchestrator.payloads[0]["text"] == "Який бюджет?"
    assert gw.sent == ["🎙 «Який бюджет?»\n\nБюджет — 370 доларів."]
    assert gw.voices == ["ogg:wav:Бюджет — 370 доларів.".encode()]


def test_without_respeecher_key_the_reply_stays_text(monkeypatch):
    import agent_runner

    async def fake_transcribe(audio, keys):
        return "Привіт", "whisper_local"

    monkeypatch.setattr(agent_runner, "transcribe", fake_transcribe)
    gw = _Gateway()
    asyncio.run(agent_runner._telegram_voice(_state(gw, {}), "fin", extract_message(_voice_update())))
    assert len(gw.sent) == 1 and gw.voices == []


def test_unheard_or_too_long_notes_get_an_honest_text_and_no_agent_call(monkeypatch):
    import agent_runner

    async def nothing(audio, keys):
        return None, "none"

    monkeypatch.setattr(agent_runner, "transcribe", nothing)
    gw = _Gateway()
    state = _state(gw, {})
    asyncio.run(agent_runner._telegram_voice(state, "fin", extract_message(_voice_update())))
    asyncio.run(agent_runner._telegram_voice(state, "fin", extract_message(_voice_update(duration=900))))
    assert state.orchestrator.payloads == []
    assert gw.sent[0].startswith("⚠️ Не вдалося розпізнати") and gw.sent[1].startswith("⚠️ Голосове задовге")
