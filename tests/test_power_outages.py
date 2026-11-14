"""Power outage schedules for the chosen region and group, through Alice, marked 💡."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

import httpx

from src import power_outages as po

NOW = datetime(2026, 11, 14, 15, 40, tzinfo=po.KYIV)
TODAY = int(datetime(2026, 11, 14, tzinfo=po.KYIV).timestamp())
TOMORROW = int(datetime(2026, 11, 15, tzinfo=po.KYIV).timestamp())


def _hours(off):
    return {str(h): off.get(h, "yes") for h in range(1, 25)}


DATA = {
    "lastUpdated": NOW.isoformat(),
    "fact": {"data": {
        str(TODAY): {"GPV3.1": _hours({17: "no", 18: "no", 19: "first", 22: "maybe"}),
                     "GPV1.1": _hours({})},
        str(TOMORROW): {"GPV3.1": _hours({6: "second", 7: "no"})},
    }},
}


def test_hours_become_merged_intervals_with_halves_and_maybes():
    plan = po.schedule(DATA, "3.1", NOW)
    assert plan["2026-11-14"] == [(16 * 60, 18 * 60 + 30, True), (21 * 60, 22 * 60, False)]
    assert plan["2026-11-15"] == [(5 * 60 + 30, 7 * 60, True)]
    assert po.describe(plan["2026-11-14"]) == "16:00–18:30, 21:00–22:00 (можливо)"
    assert po.describe(po.schedule(DATA, "1.1", NOW)["2026-11-14"]) == "відключень немає"


def test_choice_by_region_name_and_group(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    assert po.find_source("Вінницька область") == "vinnytsia" and po.find_source("Київська") == "kyiv-region"
    answer = asyncio.run(po.reply("Вінницька 3.1"))
    assert "Вінницька, черга 3.1" in answer["reply"] and po.choice() == ("vinnytsia", "3.1")
    assert "Не зрозумів" in asyncio.run(po.reply("Марс 3.1"))["reply"]
    assert "Вінницька" in asyncio.run(po.reply("список"))["reply"]
    asyncio.run(po.reply("вимкнути"))
    assert po.choice() is None


def test_a_changed_schedule_is_sent_once_and_a_warning_30_minutes_before(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    asyncio.run(po.reply("Вінницька 3.1"))
    first = po.check("vinnytsia", "3.1", DATA, NOW)
    assert first[0].startswith("💡 Графік світла, Вінницька, черга 3.1") and "сьогодні: 16:00–18:30" in first[0]
    assert any("⬇️ О 16:00" in line for line in first)  # starts in 20 minutes
    assert po.check("vinnytsia", "3.1", DATA, NOW + timedelta(minutes=6)) == []  # nothing new, no repeat


def test_old_data_is_called_old(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    old = {**DATA, "lastUpdated": 1700000000}
    assert "давно не оновлювались" in po.schedule_text("vinnytsia", "3.1", old, NOW)


def test_the_watch_sends_through_alice_and_a_dead_source_sends_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    asyncio.run(po.reply("Вінницька 3.1"))

    class _Gateway:
        sent = []

        async def owner_user_id(self):
            return "1"

        async def send(self, bot, chat, text):
            self.sent.append((bot, text))
            return True

    gateway = _Gateway()
    dead = httpx.MockTransport(lambda request: httpx.Response(503))
    assert asyncio.run(po.run_once(gateway, "alice", dead, NOW)) == 0 and gateway.sent == []
    alive = httpx.MockTransport(lambda request: httpx.Response(200, json=DATA))
    assert asyncio.run(po.run_once(gateway, "alice", alive, NOW)) >= 1
    assert gateway.sent[0][0] == "alice" and gateway.sent[0][1].startswith("💡")
