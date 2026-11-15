"""NEPTUN's open API: placed threats as signs, channel forecasts as urgent notices (15.11.2026)."""

from __future__ import annotations

import asyncio
import json

import httpx

from src import neptun
from src import threat_watch as tw

THREATS = {"threats": [
    {"type": "uav", "title": "БпЛА", "region": "Дніпропетровська область", "lat": 48.46, "lon": 35.04,
     "confidenceLevel": "medium", "status": "active"},
    {"type": "uav", "title": "Реактивний БпЛА", "region": "Дніпропетровська область", "lat": 48.53, "lon": 35.87,
     "confidenceLevel": "high", "status": "active"},
    {"type": "kab", "region": "Дніпропетровська область", "lat": 47.9, "lon": 33.4, "confidenceLevel": "high"},
    {"type": "missile", "region": "Дніпропетровська область", "lat": 48.0, "lon": 35.0, "confidenceLevel": "low"},
    {"type": "ballistic", "region": "Дніпропетровська область", "lat": 48.4, "lon": 35.0,
     "confidenceLevel": "high", "areaOnly": True},
    {"type": "fpv", "region": "Дніпропетровська область", "lat": 47.58, "lon": 34.42, "confidenceLevel": "high"},
    {"type": "uav", "region": "Дніпропетровська область", "lat": 48.1, "lon": 35.1, "confidenceLevel": "high",
     "status": "resolved"},
    {"type": "uav", "region": "Чернігівська область", "lat": 51.8, "lon": 31.5, "confidenceLevel": "high"},
]}
MESSAGES = {"messages": [
    {"channel": "@monitor_ukr", "text": "Ймовірна масована атака вночі, будьте уважні", "date": "2026-11-15T19:00:00Z"},
    {"channel": "@radar_top_ua", "text": "ймовірна масована атака вночі — будьте уважні!", "date": "2026-11-15T19:01:00Z"},
    {"channel": "Повітряні Сили ЗСУ", "text": "Загроза масованого удару", "date": "2026-11-15T19:02:00Z"},
    {"channel": "@kharkivlife", "text": "Очікується атака на Харківщину КАБами", "date": "2026-11-15T19:03:00Z"},
    {"channel": "@kudy_letyt", "text": "🛵 БпЛА курсом на Павлоград", "date": "2026-11-15T19:04:00Z"},
]}


def _api(threats=THREATS, messages=MESSAGES):
    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.host == "neptun.in.ua":
            body = threats if request.url.path.endswith("/threats") else messages
            return httpx.Response(200, json=body)
        return httpx.Response(200, text="<html></html>")  # t.me: no posts
    return httpx.MockTransport(handle)


class _Gateway:
    def __init__(self):
        self.sent, self.photos = [], []

    async def owner_user_id(self):
        return "1"

    async def send(self, bot, chat, text):
        self.sent.append(text)
        return True

    async def send_photo(self, bot, chat, png, caption=""):
        self.photos.append(caption)
        return True


class _Alerts:
    @staticmethod
    def level_of(_place):
        return "N"


def test_only_placed_confident_active_threats_of_the_oblast_become_signs():
    signs = neptun.markers(THREATS, "Дніпропетровська область")
    assert [(s.kind, s.lat) for s in signs] == [("drone", 48.46), ("jet", 48.53), ("kab", 47.9)]
    assert neptun.markers(None, "Дніпропетровська область") is None  # no answer: the Air Force signs instead
    assert neptun.markers({"threats": []}, "Дніпропетровська область") == []  # an answer of nothing is nothing


def test_forecasts_are_new_unofficial_and_said_once_across_channels():
    found, seen = neptun.forecasts(MESSAGES, [])
    assert [m["channel"] for m in found] == ["@monitor_ukr", "@kharkivlife"]  # same words twice -> once
    again, _seen = neptun.forecasts(MESSAGES, seen)
    assert again == []
    text = neptun.forecast_notice(found[0], tw.URGENT_HEADING)
    # 15.11: no channel, no link — only the short credit NEPTUN's terms require.
    assert text == ("❗❗❗ НЕГАЙНЕ ПОВІДОМЛЕННЯ ❗❗❗\n⚠️ Неофіційно — Ймовірна масована атака вночі, будьте уважні\n"
                    f"{neptun.ATTRIBUTION}") and "@" not in text


def test_the_watch_sends_forecasts_after_the_first_read_and_maps_use_neptun(tmp_path, monkeypatch):
    tw._live.update(at=0.0, data=None)
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    gateway = _Gateway()
    watch = tw.ThreatWatch(gateway, "alice", _Alerts(), transport=_api(messages={"messages": []}))
    asyncio.run(watch.run_once(["332"], now=1000.0))
    assert gateway.sent == []  # first read: nothing old is replayed
    watch._transport = _api()
    asyncio.run(watch.run_once(["332"], now=1060.0))
    assert len(gateway.sent) == 1 and "масована атака вночі" in gateway.sent[0]  # the Харківщина one is not ours
    tw._markers.clear()
    signs, credit = tw.map_markers("9", now=1060.0)
    assert len(signs) == 3 and credit == neptun.CREDIT
    stale, credit = tw.map_markers("9", now=1060.0 + tw.LIVE_TTL_S)
    assert stale == [] and credit == ""  # an old snapshot is not shown as now
    assert json.loads((tmp_path / "threat_watch" / "neptun.json").read_text())["ready"] is True


def test_forecasts_are_capped_per_hour(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    many = {"messages": [{"channel": f"@c{i}", "text": f"Ймовірна масована атака {i} хвиля"} for i in range(10)]}
    gateway = _Gateway()
    watch = tw.ThreatWatch(gateway, "alice", _Alerts(), transport=_api(messages={"messages": []}))
    asyncio.run(watch.run_once(None))
    watch._transport = _api(messages=many)
    asyncio.run(watch.run_once(None))
    assert len([t for t in gateway.sent if "НЕГАЙНЕ" in t]) == tw.FORECASTS_PER_HOUR
