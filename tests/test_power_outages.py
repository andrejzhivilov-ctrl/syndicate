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
    assert "Не знайшов «Марс»" in asyncio.run(po.reply("Марс 3.1"))["reply"]  # wording since 14.11
    assert "Вінницька" in asyncio.run(po.reply("список"))["reply"]
    asyncio.run(po.reply("вимкнути"))
    assert po.choice() is None


def test_a_changed_schedule_is_sent_once_and_a_warning_30_minutes_before(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    asyncio.run(po.reply("Вінницька 3.1"))
    first = po.check("vinnytsia", "3.1", DATA, NOW)
    assert first[0].startswith("💡 ") and "Світло, Вінницька, черга 3.1" in first[0]
    # 15.11: the whole day in turns, 🔴 off and 🟢 on.
    assert "Сьогодні:\n🟢 00:00–16:00\n🔴 16:00–18:30\n🟢 18:30–21:00\n🔴 21:00–22:00 (можливо)\n🟢 22:00–24:00" in first[0]
    assert any(line.startswith("💡⬇️") and "О 16:00 вимкнення, до 18:30" in line for line in first)  # in 20 min
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


def test_off_and_back_on_come_with_alices_phrases_once_each(tmp_path, monkeypatch):
    """14.11.2026: three notices per outage — soon, off, on — each a phrase plus the schedule times."""
    from src import outage_phrases

    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    asyncio.run(po.reply("Вінницька 3.1 Вінниця"))
    po.check("vinnytsia", "3.1", DATA, NOW)  # schedule + soon
    at_start = po.check("vinnytsia", "3.1", DATA, NOW.replace(hour=16, minute=2))
    assert len(at_start) == 1 and at_start[0].startswith("💡🌑") and "до 18:30" in at_start[0]
    assert any(phrase in at_start[0] for phrase in outage_phrases.POWER_OFF)
    at_end = po.check("vinnytsia", "3.1", DATA, NOW.replace(hour=18, minute=33))
    assert len(at_end) == 1 and at_end[0].startswith("💡⬆️") and "16:00–18:30" in at_end[0]
    assert po.check("vinnytsia", "3.1", DATA, NOW.replace(hour=18, minute=36)) == []


def test_the_city_or_community_is_kept_with_the_group(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    answer = asyncio.run(po.reply("Вінницька 3.1 Жмеринська громада"))
    assert "Вінницька, Жмеринська громада, черга 3.1" in answer["reply"]
    assert po.choice() == ("vinnytsia", "3.1") and po.place() == "Жмеринська громада"


def test_city_first_then_group_finds_the_oblast_itself(tmp_path, monkeypatch):
    """14.11.2026: «/svitlo Вінниця», then «/svitlo 3.1»; or both at once."""
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    first = asyncio.run(po.reply("Вінниця"))["reply"]
    assert "Вінниця (Вінницька)" in first and "Тепер черга" in first and po.choice() is None
    second = asyncio.run(po.reply("3.1"))["reply"]
    assert "Вінницька, Вінниця, черга 3.1" in second and po.choice() == ("vinnytsia", "3.1")
    assert po.resolve("Жмеринка")[0] == "vinnytsia"
    both = asyncio.run(po.reply("Жмеринка 2.2"))["reply"]
    assert "Вінницька, Жмеринка, черга 2.2" in both
    nowhere = asyncio.run(po.reply("Ковель 1.1"))["reply"]  # Volyn: no open schedule yet
    assert "графіків поки немає" in nowhere


def test_an_extended_outage_is_said_with_the_new_end(tmp_path, monkeypatch):
    """14.11.2026: in the dark, a later end replaces the schedule table with «extended»."""
    from src import outage_phrases

    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    asyncio.run(po.reply("Вінницька 3.1"))
    inside = NOW.replace(hour=16, minute=30)
    po.check("vinnytsia", "3.1", DATA, inside)
    longer = {**DATA, "fact": {"data": {str(TODAY): {"GPV3.1": _hours({17: "no", 18: "no", 19: "no", 20: "no"})},
                                        str(TOMORROW): DATA["fact"]["data"][str(TOMORROW)]}}}
    said = po.check("vinnytsia", "3.1", longer, inside.replace(minute=36))
    assert said[0].startswith("💡⏳") and "до 20:00" in said[0]
    assert any(phrase in said[0] for phrase in outage_phrases.POWER_EXTENDED)


def test_the_schedule_is_sent_again_only_when_the_groups_hours_really_change(tmp_path, monkeypatch):
    # Operator, 15.11.2026: «один раз відправила графік … тільки якщо змінився і правда графік».
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    asyncio.run(po.reply("Вінницька 3.1"))
    early = NOW - timedelta(hours=10)  # before the 30-minute warning
    assert len(po.check("vinnytsia", "3.1", DATA, early)) == 1
    another_group_changed = {**DATA, "fact": {"data": {
        str(TODAY): {**DATA["fact"]["data"][str(TODAY)], "GPV1.1": _hours({10: "no"})},
        str(TOMORROW): DATA["fact"]["data"][str(TOMORROW)]}}}
    assert po.check("vinnytsia", "3.1", another_group_changed, early) == []  # other queues changed, not ours
    next_morning = datetime(2026, 11, 15, 1, 0, tzinfo=po.KYIV)
    assert po.check("vinnytsia", "3.1", DATA, next_morning) == []  # tomorrow became today: no news
    moved = {**DATA, "fact": {"data": {str(TOMORROW): {"GPV3.1": _hours({9: "no"})}}}}
    assert "🔴 08:00–09:00" in po.check("vinnytsia", "3.1", moved, next_morning)[0]  # the hours moved: news
    assert po.day_lines([]) == ["🟢 весь день без відключень"]
