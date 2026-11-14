"""Planned power outages for Andrii's group, through Alice, marked 💡 (14.11.2026).

No oblenergo gives a key-free API, but volunteers mirror the schedules of 17 regions as
public JSON on GitHub (the sources Home Assistant's "Svitlo Yeah" uses). The format is the
same everywhere: ``fact.data[day][GPV<group>][hour] = yes | no | first | second`` (first or
second half of the hour without power; ``m…``/``maybe`` = possible outage).

- Andrii picks the region and the group in Alice's chat: ``/svitlo Вінницька 3.1``.
- Every 6 minutes the chosen file is read; a changed schedule for today or tomorrow is sent,
  and 30 minutes before an outage starts Alice warns once.
- Data older than a day is said to be old, never shown as current (AGENTS.md §1).
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple
from zoneinfo import ZoneInfo

import httpx
import structlog

from src.data_paths import ensure_dir

logger = structlog.get_logger(__name__)

KYIV = ZoneInfo("Europe/Kyiv")
INTERVAL_S = 360
WARN_BEFORE_MIN = 30
STALE_AFTER_H = 24
ICON = "💡"
_RAW = "https://raw.githubusercontent.com"
_BASK = f"{_RAW}/Baskerville42/outage-data-ua/main/data"
_YAR = f"{_RAW}/yaroslav2901/OE_OUTAGE_DATA/main/data"
#: key -> (name Andrii types, source URL). Region names match the oblast names Alice uses for alerts.
SOURCES: Dict[str, Tuple[str, str]] = {
    "kyiv": ("м. Київ", f"{_BASK}/kyiv.json"),
    "kyiv-region": ("Київська", f"{_BASK}/kyiv-region.json"),
    "dnipro": ("Дніпропетровська", f"{_BASK}/dnipro.json"),
    "odesa": ("Одеська", f"{_BASK}/odesa.json"),
    "vinnytsia": ("Вінницька", f"{_RAW}/vn-progr/gpv-voe-vinnytsia/main/data/Vinnytsiaoblenerho.json"),
    "cherkasy": ("Черкаська", f"{_YAR}/Cherkasyoblenergo.json"),
    "chernihiv": ("Чернігівська", f"{_YAR}/Chernihivoblenergo.json"),
    "kharkiv": ("Харківська", f"{_YAR}/Kharkivoblenerho.json"),
    "khmelnytskyi": ("Хмельницька", f"{_YAR}/Khmelnytskoblenerho.json"),
    "lviv": ("Львівська", f"{_YAR}/Lvivoblenerho.json"),
    "poltava": ("Полтавська", f"{_YAR}/Poltavaoblenergo.json"),
    "ivano-frankivsk": ("Івано-Франківська", f"{_YAR}/Prykarpattiaoblenerho.json"),
    "rivne": ("Рівненська", f"{_YAR}/Rivneoblenergo.json"),
    "ternopil": ("Тернопільська", f"{_YAR}/Ternopiloblenerho.json"),
    "zakarpattia": ("Закарпатська", f"{_YAR}/Zakarpattiaoblenerho.json"),
    "zaporizhzhia": ("Запорізька", f"{_YAR}/Zaporizhzhiaoblenergo.json"),
    "zhytomyr": ("Житомирська", f"{_YAR}/Zhytomyroblenergo.json"),
}
#: hour value -> (minutes off from, to) within the hour, and whether it is certain.
_OFF = {"no": (0, 60, True), "first": (0, 30, True), "second": (30, 60, True),
        "maybe": (0, 60, False), "mfirst": (0, 30, False), "msecond": (30, 60, False)}

Interval = Tuple[int, int, bool]  # minutes from midnight: start, end, certain


# ── the schedule ──────────────────────────────────────────────────────────────────────────


def day_intervals(hours: Mapping[str, Any]) -> List[Interval]:
    """Off intervals of one day for one group, neighbours of the same certainty merged."""
    spans: List[Interval] = []
    for hour in range(1, 25):
        value = str(hours.get(str(hour), "yes")).lower()
        if value not in _OFF:
            continue
        start, end, certain = _OFF[value]
        piece = ((hour - 1) * 60 + start, (hour - 1) * 60 + end, certain)
        if spans and spans[-1][1] == piece[0] and spans[-1][2] == certain:
            spans[-1] = (spans[-1][0], piece[1], certain)
        else:
            spans.append(piece)
    return spans


def group_key(group: str) -> str:
    return "GPV" + group.strip().upper().removeprefix("GPV")


def schedule(data: Mapping[str, Any], group: str, today: datetime) -> Dict[str, List[Interval]]:
    """Today's and tomorrow's off intervals, by local date; a missing day stays missing."""
    days = ((data.get("fact") or {}).get("data") or {}) if isinstance(data, Mapping) else {}
    wanted = {today.date().isoformat(), (today + timedelta(days=1)).date().isoformat()}
    out: Dict[str, List[Interval]] = {}
    for epoch, groups in days.items():
        try:
            date = datetime.fromtimestamp(int(epoch), KYIV).date().isoformat()
        except (TypeError, ValueError, OSError):
            continue
        hours = (groups or {}).get(group_key(group)) if isinstance(groups, Mapping) else None
        if date in wanted and isinstance(hours, Mapping):
            out[date] = day_intervals(hours)
    return out


def updated_at(data: Mapping[str, Any]) -> Optional[datetime]:
    raw = data.get("lastUpdated") if isinstance(data, Mapping) else None
    try:
        if isinstance(raw, (int, float)) or str(raw).isdigit():
            return datetime.fromtimestamp(int(raw), KYIV)
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00")).astimezone(KYIV)
    except (TypeError, ValueError, OSError):
        return None


def _clock(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def describe(intervals: List[Interval]) -> str:
    if not intervals:
        return "відключень немає"
    return ", ".join(f"{_clock(a)}–{_clock(b)}" + ("" if certain else " (можливо)") for a, b, certain in intervals)


# ── the choice and the state ──────────────────────────────────────────────────────────────


def _dir() -> Path:
    return ensure_dir("power")


def _read(name: str) -> Dict[str, Any]:
    try:
        data = json.loads((_dir() / name).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _write(name: str, data: Dict[str, Any]) -> None:
    path = _dir() / name
    spare = path.with_suffix(".tmp")
    spare.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    spare.replace(path)


def choice() -> Optional[Tuple[str, str]]:
    saved = _read("choice.json")
    source, group = saved.get("source"), saved.get("group")
    return (source, group) if source in SOURCES and group else None


def find_source(text: str) -> Optional[str]:
    wanted = text.strip().lower().replace("область", "").strip()
    for key, (name, _url) in SOURCES.items():
        if wanted and (wanted == key or wanted in name.lower()):
            return key
    return None


# ── reading ───────────────────────────────────────────────────────────────────────────────


async def fetch(source: str, transport: Any = None) -> Optional[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=20, transport=transport) as client:
            response = await client.get(SOURCES[source][1])
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("power_fetch_failed", source=source, error_type=type(exc).__name__)
        return None
    return data if isinstance(data, dict) else None


def _day_name(date: str, today: datetime) -> str:
    return "сьогодні" if date == today.date().isoformat() else "завтра"


def schedule_text(source: str, group: str, data: Dict[str, Any], now: datetime) -> str:
    plan = schedule(data, group, now)
    head = f"{ICON} Світло, {SOURCES[source][0]}, черга {group}"
    lines = [f"{_day_name(date, now)}: {describe(spans)}" for date, spans in sorted(plan.items())]
    if not lines:
        lines = [f"черги {group} у графіку немає; перевір номер на сайті обленерго"]
    stamp = updated_at(data)
    if stamp is None or now - stamp > timedelta(hours=STALE_AFTER_H):
        lines.append("⚠️ дані давно не оновлювались, графік може бути неактуальний")
    return "\n".join([head, *lines])


# ── the watch ─────────────────────────────────────────────────────────────────────────────


def _warnings(plan: Dict[str, List[Interval]], now: datetime, sent: List[str]) -> List[Tuple[str, str]]:
    """(key, text) for outages that start within WARN_BEFORE_MIN and were not warned about."""
    out = []
    for date, spans in plan.items():
        for start, end, certain in spans:
            begins = datetime.fromisoformat(date).replace(tzinfo=KYIV) + timedelta(minutes=start)
            key = f"{date}T{start}"
            if key not in sent and timedelta(0) < begins - now <= timedelta(minutes=WARN_BEFORE_MIN):
                maybe = " можливе" if not certain else ""
                out.append((key, f"{ICON}⬇️ О {_clock(start)}{maybe} вимкнення світла, до {_clock(end)}."))
    return out


def check(source: str, group: str, data: Dict[str, Any], now: datetime) -> List[str]:
    """Messages for this round; the state remembers what was already said."""
    state = _read("state.json")
    plan = schedule(data, group, now)
    signature = json.dumps({"choice": [source, group], "plan": plan}, sort_keys=True)
    messages = []
    if signature != state.get("signature"):
        messages.append(schedule_text(source, group, data, now).replace(f"{ICON} Світло", f"{ICON} Графік світла", 1))
    sent = [key for key in state.get("warned", []) if key[:10] >= now.date().isoformat()]
    for key, text in _warnings(plan, now, sent):
        messages.append(text)
        sent.append(key)
    _write("state.json", {"signature": signature, "warned": sent})
    return messages


async def run_once(gateway: Any, bot: str, transport: Any = None, now: Optional[datetime] = None) -> int:
    chosen = choice()
    if chosen is None:
        return 0
    data = await fetch(chosen[0], transport)
    if data is None:
        return 0
    messages = check(chosen[0], chosen[1], data, now or datetime.now(KYIV))
    owner = await gateway.owner_user_id() if messages else None
    for text in messages if owner else []:
        await gateway.send(bot, owner, text)
    return len(messages)


async def loop(gateway: Any, bot: str) -> None:
    logger.info("power_watch_started", interval_s=INTERVAL_S)
    while True:
        try:
            await run_once(gateway, bot)
        except Exception as exc:  # noqa: BLE001 - one bad round must not end the watch
            logger.warning("power_watch_round_failed", error_type=type(exc).__name__)
        await asyncio.sleep(INTERVAL_S)


# ── Alice's /svitlo ───────────────────────────────────────────────────────────────────────

HELP = ("/svitlo — графік твоєї черги на сьогодні й завтра\n"
        "/svitlo Вінницька 3.1 — вибрати область і чергу\n"
        "/svitlo список — області, для яких є графіки\n"
        "/svitlo вимкнути — не надсилати графіки")


async def reply(text: str, transport: Any = None) -> Dict[str, Any]:
    words = text.split()
    if words[:1] == ["список"]:
        return {"status": "completed", "reply": "Області з графіками:\n" + "\n".join(
            f"• {name}" for name, _url in sorted(SOURCES.values()))}
    if words[:1] == ["вимкнути"]:
        _write("choice.json", {})
        return {"status": "completed", "reply": f"{ICON} Графіки світла більше не надсилатиму."}
    if words:
        return _choose(words)
    chosen = choice()
    if chosen is None:
        return {"status": "completed", "reply": f"{ICON} Черга не вибрана.\n{HELP}"}
    data = await fetch(chosen[0], transport)
    if data is None:
        return {"status": "unavailable", "reply": f"{ICON} Джерело графіка зараз не відповідає, спробуй пізніше."}
    return {"status": "completed", "reply": schedule_text(chosen[0], chosen[1], data, datetime.now(KYIV))}


def _choose(words: List[str]) -> Dict[str, Any]:
    group = words[-1] if len(words) > 1 else ""
    source = find_source(" ".join(words[:-1])) if group else None
    if source is None or not group.replace(".", "").isdigit():
        return {"status": "completed", "reply": f"Не зрозумів. Приклад: /svitlo Вінницька 3.1\n{HELP}"}
    _write("choice.json", {"source": source, "group": group})
    _write("state.json", {})
    return {"status": "completed",
            "reply": f"{ICON} Стежу за світлом: {SOURCES[source][0]}, черга {group}. Графік прийде протягом 6 хв."}
