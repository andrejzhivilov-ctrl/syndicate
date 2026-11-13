"""Photos and videos to Alex: seen through the gateway, capped, never stored or guessed (06.11.2026)."""
from __future__ import annotations

import asyncio
import base64
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx

from src import media_vision as vision
from src.hermes_tools import DailyLimit
from src.telegram_gateway import extract_message

OWNER = "523"
RUNTIME = str(Path(__file__).resolve().parent.parent / "deploy" / "runtime")
if RUNTIME not in sys.path:
    sys.path.insert(0, RUNTIME)  # agent_runner lives there; do not rely on another test module's import


def _update(**media):
    message = {"message_id": 7, "from": {"id": int(OWNER)}, "chat": {"id": int(OWNER), "type": "private"}, **media}
    return {"update_id": 3, "message": message}


def test_photos_videos_and_captions_reach_the_agent_as_file_references():
    photo = extract_message(_update(photo=[{"file_id": "small", "file_size": 900}, {"file_id": "big", "file_size": 90000}],
                                    caption="Скільки білка?"))
    assert photo["kind"] == "media" and photo["file_id"] == "big" and photo["mime"] == "image/jpeg"
    assert photo["text"] == "Скільки білка?" and photo["file_size"] == 90000

    video = extract_message(_update(video={"file_id": "v", "mime_type": "video/quicktime", "duration": 40}))
    assert video["mime"] == "video/quicktime" and video["duration"] == 40 and video["text"] == ""
    assert extract_message(_update(video_note={"file_id": "round", "duration": 20}))["mime"] == "video/mp4"
    assert extract_message(_update(document={"file_id": "d", "mime_type": "image/png"}))["mime"] == "image/png"

    assert extract_message(_update(document={"file_id": "d", "mime_type": "application/pdf"})) is None
    assert extract_message(_update(document={"file_id": "d"})) is None  # no type is not guessed
    assert extract_message(_update(sticker={"file_id": "s"})) is None
    assert extract_message(_update(text="привіт"))["kind"] == "message"


def test_only_alex_sees_media_and_too_big_files_are_refused_before_download():
    assert vision.sees_media("trainer") and not vision.sees_media("fin")
    assert vision.refusal("fin", {"mime": "image/jpeg"}) == vision.NO_MEDIA
    assert vision.refusal("trainer", {"mime": "image/jpeg", "file_size": 100}) is None
    assert vision.refusal("trainer", {"mime": "image/heic"}) == vision.UNSUPPORTED
    assert vision.refusal("trainer", {"mime": "video/mp4", "file_size": 25_000_000}) == vision.TOO_BIG
    assert vision.refusal("trainer", {"mime": "video/mp4", "duration": 600}) == vision.TOO_BIG


def test_vision_call_sends_the_file_and_the_masked_caption_and_returns_what_was_seen(tmp_path):
    seen = {}

    def provider(request):
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"choices": [{"message": {"content": "Йогурт грецький 2%, білок 8,5 г на 100 г."}}],
                                         "usage": {"cost": 0.0004}})

    limit = DailyLimit(tmp_path / "use.json")
    done = asyncio.run(vision.describe("trainer", b"jpeg-bytes", "image/jpeg", "пиши на test@example.com", "key",
                                       limit=limit, transport=httpx.MockTransport(provider)))
    assert done == {"status": "ok", "description": "Йогурт грецький 2%, білок 8,5 г на 100 г."}
    body = seen["body"]
    assert body["model"] == "google/gemini-3.8-flash"
    text, image = body["messages"][0]["content"]
    assert image == {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(b"jpeg-bytes").decode()}}
    assert "не вигадуй" in text["text"] and "test@example.com" not in text["text"] and "Підпис Андрія" in text["text"]

    asyncio.run(vision.describe("trainer", b"mov", "video/quicktime", "", "key", limit=limit,
                                transport=httpx.MockTransport(provider)))
    video = seen["body"]["messages"][0]["content"][1]
    assert video["type"] == "video_url" and video["video_url"]["url"].startswith("data:video/mov;base64,")
    assert "Підпис Андрія" not in seen["body"]["messages"][0]["content"][0]["text"]


def test_vision_failures_are_honest_and_the_day_is_capped(tmp_path):
    limit = DailyLimit(tmp_path / "use.json", {vision.MEDIA: 1})
    down = httpx.MockTransport(lambda request: httpx.Response(500))
    assert asyncio.run(vision.describe("trainer", b"x", "image/png", "", "key", limit=limit, transport=down)) == {
        "status": "unavailable", "reason": "vision_failed"}
    assert asyncio.run(vision.describe("trainer", b"x", "image/png", "", "key", limit=limit))["reason"] == "daily_limit_reached"
    assert asyncio.run(vision.describe("trainer", b"x", "image/png", "", ""))["reason"] == "model_key_unavailable"
    assert asyncio.run(vision.describe("fin", b"x", "image/png", "", "key"))["reason"] == "agent_has_no_vision"


class _Gateway:
    def __init__(self, data=b"jpeg"):
        self.data, self.sent, self.downloads = data, [], []

    async def download_file(self, agent_id, file_id, max_bytes):
        self.downloads.append((file_id, max_bytes))
        return self.data

    async def send(self, agent_id, chat_id, text):
        self.sent.append(text)
        return True


class _Orch:
    def __init__(self):
        self.payloads = []

    async def handle_webhook(self, source, payload):
        self.payloads.append(payload)
        return {"status": "completed", "result": {"response": "У 100 г 8,5 г білка, це добрий перекус."}}

    def openrouter_key(self):
        return "key"


def test_the_runner_shows_alex_the_description_with_the_caption(monkeypatch):
    import agent_runner

    async def described(agent, data, mime, caption, key):
        return {"status": "ok", "description": "Етикетка: білок 8,5 г на 100 г."}

    monkeypatch.setattr(agent_runner.media_vision, "describe", described)
    gw, orch = _Gateway(), _Orch()
    state = SimpleNamespace(telegram_gateway=gw, orchestrator=orch)
    photo = extract_message(_update(photo=[{"file_id": "big", "file_size": 9000}], caption="Скільки білка?"))
    asyncio.run(agent_runner._telegram_media(state, "trainer", photo))
    sent_to_alex = orch.payloads[0]["text"]
    assert "Етикетка: білок 8,5 г" in sent_to_alex and "Скільки білка?" in sent_to_alex and "довідка" in sent_to_alex
    assert gw.sent == ["У 100 г 8,5 г білка, це добрий перекус."]
    assert gw.downloads == [("big", vision.MAX_IMAGE_BYTES)]


def test_the_runner_never_stays_silent(monkeypatch):
    import agent_runner

    async def blind(agent, data, mime, caption, key):
        return {"status": "unavailable", "reason": "vision_failed"}

    monkeypatch.setattr(agent_runner.media_vision, "describe", blind)
    photo = extract_message(_update(photo=[{"file_id": "big"}]))
    for agent, gateway, expected in (("fin", _Gateway(), vision.NO_MEDIA), ("trainer", _Gateway(), vision.NOT_SEEN),
                                     ("trainer", _Gateway(data=None), "⚠️ Не вдалося отримати файл з Telegram.")):
        orch = _Orch()
        asyncio.run(agent_runner._telegram_media(SimpleNamespace(telegram_gateway=gateway, orchestrator=orch), agent, photo))
        assert gateway.sent == [expected] and orch.payloads == []
