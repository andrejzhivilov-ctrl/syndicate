"""The power group (черга) by street and house from Yasno, and CEK's schedule (14.11.2026)."""

from __future__ import annotations

import asyncio
import json

import httpx

from src import power_address as pa
from src import power_outages as po


def _yasno(request: httpx.Request) -> httpx.Response:
    """Yasno's address API as seen live 14.11.2026: Dnipro is city 6, Гоголя is street 604 in DnEM only."""
    path, q = request.url.path.rsplit("/", 1)[-1], request.url.params
    dso = q.get("dsoId")
    if path == "cities":
        return httpx.Response(200, json=[{"id": 4, "value": "м. Верхньодніпровськ"}, {"id": 6, "value": "м. Дніпро"},
                                         {"id": 188, "value": "с. Дніпрове"}])
    if path == "streets":
        assert q.get("cityId") == "6"
        found = [{"id": 604, "value": "вул. Гоголя"}, {"id": 2311, "value": "пров. Гоголя Миколи"}]
        return httpx.Response(200, json=found if dso == "301" else [])
    if path == "houses":
        return httpx.Response(200, json=[{"id": 25349, "value": "1/прим121"}, {"id": 25353, "value": "5"},
                                         {"id": 25355, "value": "6"}])
    if path == "group":
        house = q.get("houseId")
        return httpx.Response(200, json={"group": 5, "subgroup": 1} if house != "25355" else {"group": 2, "subgroup": 2})
    return httpx.Response(404, json={})


TRANSPORT = httpx.MockTransport(_yasno)


def test_address_parts_and_names_without_prefixes():
    assert pa.split_address("Дніпро, вул. Гоголя 5") == ("Дніпро", "вул. Гоголя", "5")
    assert pa.split_address("Гоголя 15А") == ("", "Гоголя", "15А")
    assert pa.split_address("Гоголя") == ("", "Гоголя", "")
    assert pa.pick([(1, "вул. Гоголя"), (2, "вул. Гоголя Миколи")], "Гоголя") == [(1, "вул. Гоголя")]
    assert pa.pick([(2, "вул. Гоголя Миколи")], "миколи гоголя") == [(2, "вул. Гоголя Миколи")]


def test_a_house_gets_its_group_and_a_ready_command(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    answer = asyncio.run(po.reply("адреса Дніпро, Гоголя 5", TRANSPORT))
    assert "вул. Гоголя 5 — черга 5.1 (мережа ДнЕМ)" in answer["reply"]
    assert "/svitlo Дніпро 5.1" in answer["reply"]
    missing = asyncio.run(po.reply("адреса Дніпро, Гоголя 99", TRANSPORT))["reply"]
    assert "Будинку 99" in missing and "1/прим121, 5, 6" in missing


def test_a_whole_street_lists_houses_by_group(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(pa, "PAUSE_S", 0)
    text = asyncio.run(po.reply("адреса Дніпро, Гоголя", TRANSPORT))["reply"]
    assert "• 2.2: 6" in text and "• 5.1: 1/прим121, 5" in text


def test_the_saved_city_is_used_and_regions_without_lookup_say_so(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    asyncio.run(po.reply("Дніпро"))
    assert "черга 5.1" in asyncio.run(po.reply("вулиця Гоголя 5", TRANSPORT))["reply"]
    other = asyncio.run(po.reply("адреса Вінниця, Соборна 5", TRANSPORT))
    assert other["status"] == "unavailable" and "сайт обленерго" in other["reply"]
    assert asyncio.run(po.reply("райони"))["status"] == "unavailable"


def test_ceks_slots_become_the_mirrors_hours():
    # Live 14.11.2026: CEK's schedule differs from DnEM's, so it is its own source.
    day = {"date": "2026-11-15T00:00:00+02:00", "status": "ScheduleApplies",
           "slots": [{"start": 0, "end": 90, "type": "Definite"}, {"start": 90, "end": 1440, "type": "NotPlanned"}]}
    waiting = {"date": "2026-11-14T00:00:00+02:00", "status": "WaitingForSchedule", "slots": []}
    data = po.from_yasno({"1.1": {"today": waiting, "tomorrow": day, "updatedOn": "2026-11-14T20:11:49+00:00"}})
    days = data["fact"]["data"]
    assert len(days) == 1  # a day whose schedule does not apply is missing, not "no outages"
    hours = next(iter(days.values()))["GPV1.1"]
    assert hours["1"] == "no" and hours["2"] == "first" and hours["3"] == "yes"
    assert po.find_source("Дніпропетровська") == "dnipro" and po.find_source("ЦЕК") == "dnipro-cek"
    assert json.dumps(data)  # stored as JSON like the mirrors


def test_ukrainian_command_spellings_reach_the_commands():
    # Live 14.11.2026: «/світло Дніпро» was answered with Alice's role text.
    from src.agent_chat import pool_command

    assert pool_command({"text": "/світло Дніпро"}) == ("/svitlo", "Дніпро")
    assert pool_command({"text": "/Вода Дніпропетровська"}) == ("/voda", "Дніпропетровська")
    assert pool_command({"text": "/тривоги"}) == ("/alerts", "")
