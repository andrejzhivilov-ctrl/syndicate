"""All-Ukraine alerts from the keyless siren.pp.ua mirror; a failed read is silence, not calm."""

from __future__ import annotations

import asyncio

import httpx

from src import alert_poll
from src.alert_watch import STATES, AlertWatch

KYIV = next(key for key, name in STATES.items() if name == "м. Київ")
SAMPLE = [
    {"regionId": KYIV, "regionType": "State", "activeAlerts": [
        {"regionId": KYIV, "type": "AIR", "activeAlertLevels": [{"alertLevel": "Red"}]}]},
    {"regionId": "1313", "regionType": "Community", "activeAlerts": [
        {"regionId": "1313", "type": "AIR", "activeAlertLevels": [{"alertLevel": "Yellow"}]},
        {"regionId": "1313", "type": "ARTILLERY", "activeAlertLevels": [{"alertLevel": "Red"}]}]},
    {"regionId": "77", "regionType": "District", "activeAlerts": []},
]


class _Gateway:
    def __init__(self):
        self.sent = []

    async def owner_user_id(self):
        return "1"

    async def send(self, bot, chat, text):
        self.sent.append((bot, text))
        return True


def test_air_levels_keep_only_air_raids_red_wins():
    assert alert_poll.air_levels(SAMPLE) == {KYIV: "R", "1313": "Y"}
    assert alert_poll.air_levels([None, {"activeAlerts": [None]}]) == {}


def test_a_read_delivers_the_whole_picture_and_alice_speaks(tmp_path):
    def handler(request):
        assert request.url.host == "siren.pp.ua" and "SYNDICATE" in request.headers["User-Agent"]
        return httpx.Response(200, json=SAMPLE)

    gateway = _Gateway()
    watch = AlertWatch(gateway, path=tmp_path / "state.json")
    assert asyncio.run(alert_poll.poll_once(watch, httpx.MockTransport(handler))) is True
    asyncio.run(watch.flush())
    assert gateway.sent and gateway.sent[0][0] == "alice" and "Київ" in gateway.sent[0][1]


def test_a_failed_read_delivers_nothing_and_silence_is_reported(tmp_path):
    def handler(request):
        return httpx.Response(503)

    watch = AlertWatch(_Gateway(), path=tmp_path / "state.json")
    delivered = []
    watch.handle_relay = lambda payload: delivered.append(payload)
    assert asyncio.run(alert_poll.poll_once(watch, httpx.MockTransport(handler))) is False
    assert delivered == []
    watch.accept_poll()
    watch.check_silence(now=10**12)
    assert any("немає подій" in line for line in watch._pending)


def test_the_poll_can_be_switched_off(monkeypatch):
    monkeypatch.setenv("ALERT_POLL", "off")
    assert alert_poll.enabled() is False
    monkeypatch.delenv("ALERT_POLL")
    assert alert_poll.enabled() is True
