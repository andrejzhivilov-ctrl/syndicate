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
from src.outage_phrases import say

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


def _stem(word: str) -> str:
    word = word.lower()
    return word[:-2] if len(word) > 5 else word


def oblast_of(town: str) -> Optional[str]:
    """The oblast of a city or community named the way people say it («Вінниця», «Жмеринка»).

    Looked up in the Ukraine Alarm region tree: communities first, the shortest matching name
    wins, then its oblast. None when nothing matches.
    """
    from src.alert_watch import NAMES, STATES, UP, _lineage

    stems = [_stem(word) for word in town.replace(",", " ").split() if len(word) > 2]
    if not stems:
        return None
    def starts(name: str) -> bool:  # «Марс» must not match the middle of a word (caught by a test)
        words = name.lower().replace("'", " ").replace("’", " ").split()
        return all(any(word.startswith(stem) for word in words) for stem in stems)

    found = [region for region, name in NAMES.items() if starts(name)]
    found.sort(key=lambda region: (UP.get(region) is None, len(NAMES[region])))
    return STATES.get(_lineage(found[0])[-1]) if found else None


def resolve(text: str) -> Tuple[Optional[str], str, str]:
    """(power source, place label, oblast name) for an oblast or a city / community."""
    source = find_source(text)
    if source:
        return source, "", SOURCES[source][0]
    oblast = oblast_of(text)
    if oblast is None:
        return None, "", ""
    key = next((key for key, (name, _url) in SOURCES.items()
                if oblast == name or oblast.startswith(name + " ")), None)
    return key, text.strip()[:60], oblast


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


def place() -> str:
    """The city or community Andrii named with his group, only as a label."""
    return str(_read("choice.json").get("place") or "")


def _where(source: str, group: str) -> str:
    town = place()
    return f"{SOURCES[source][0]}{', ' + town if town else ''}, черга {group}"


def schedule_text(source: str, group: str, data: Dict[str, Any], now: datetime) -> str:
    plan = schedule(data, group, now)
    head = f"{ICON} Світло, {_where(source, group)}"
    lines = [f"{_day_name(date, now)}: {describe(spans)}" for date, spans in sorted(plan.items())]
    if not lines:
        lines = [f"черги {group} у графіку немає; перевір номер на сайті обленерго"]
    stamp = updated_at(data)
    if stamp is None or now - stamp > timedelta(hours=STALE_AFTER_H):
        lines.append("⚠️ дані давно не оновлювались, графік може бути неактуальний")
    return "\n".join([head, *lines])


# ── the watch ─────────────────────────────────────────────────────────────────────────────


def _event(kind: str, start: int, end: int, certain: bool) -> str:
    """One notice: Alice's phrase, then the times from the schedule (never from the phrase)."""
    maybe = " (можливе відключення)" if not certain else ""
    times = {"soon": f"О {_clock(start)} вимкнення, до {_clock(end)}{maybe}.",
             "off": f"За графіком до {_clock(end)}{maybe}.",
             "on": f"Відключення {_clock(start)}–{_clock(end)} за графіком закінчилось."}[kind]
    arrow = {"soon": "⬇️", "off": "🌑", "on": "⬆️"}[kind]
    return f"{ICON}{arrow} {say('power_' + kind)}\n{times}"


def _due(kind: str, start: int, end: int, date: str, now: datetime) -> bool:
    """Whether a notice falls into this round: before the start, at the start, at the end."""
    midnight = datetime.fromisoformat(date).replace(tzinfo=KYIV)
    window = timedelta(seconds=INTERVAL_S + 60)
    if kind == "soon":
        return timedelta(0) < midnight + timedelta(minutes=start) - now <= timedelta(minutes=WARN_BEFORE_MIN)
    moment = midnight + timedelta(minutes=start if kind == "off" else end)
    return timedelta(0) <= now - moment < window


def _warnings(plan: Dict[str, List[Interval]], now: datetime, sent: List[str]) -> List[Tuple[str, str]]:
    """(key, text) for the soon / off / on notices due now and not sent yet."""
    out = []
    for date, spans in plan.items():
        for start, end, certain in spans:
            for kind in ("soon", "off", "on"):
                key = f"{date}T{start}:{kind}"
                if key not in sent and _due(kind, start, end, date, now):
                    out.append((key, _event(kind, start, end, certain)))
    return out


def _current(plan: Dict[str, List[Interval]], now: datetime) -> Optional[Dict[str, Any]]:
    """The outage we are in right now, if any."""
    minute = now.hour * 60 + now.minute
    for start, end, _certain in plan.get(now.date().isoformat(), []):
        if start <= minute < end:
            return {"date": now.date().isoformat(), "start": start, "end": end}
    return None


def _extension(before: Optional[Dict[str, Any]], now_in: Optional[Dict[str, Any]]) -> Optional[str]:
    """An outage that was running and now ends later: Alice says it was extended."""
    if not before or not now_in or before.get("date") != now_in["date"] or before.get("start") != now_in["start"]:
        return None
    if now_in["end"] <= int(before.get("end", 0)):
        return None
    return f"{ICON}⏳ {say('power_extended')}\nТепер за графіком до {_clock(now_in['end'])}."


def check(source: str, group: str, data: Dict[str, Any], now: datetime) -> List[str]:
    """Messages for this round; the state remembers what was already said."""
    state = _read("state.json")
    plan = schedule(data, group, now)
    running = _current(plan, now)
    extended = _extension(state.get("current"), running)
    signature = json.dumps({"choice": [source, group], "plan": plan}, sort_keys=True)
    messages = []
    if extended:
        messages.append(extended)  # in the dark, the new end time matters more than the whole table
    elif signature != state.get("signature"):
        text = schedule_text(source, group, data, now)
        messages.append(text.replace(f"{ICON} Світло", f"{ICON} {say('power_changed')}\nСвітло", 1))
    sent = [key for key in state.get("warned", []) if key[:10] >= now.date().isoformat()]
    for key, text in _warnings(plan, now, sent):
        messages.append(text)
        sent.append(key)
    _write("state.json", {"signature": signature, "warned": sent, "current": running})
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
        "/svitlo Вінниця — місто, громада чи область (Аліса знайде область сама)\n"
        "/svitlo 3.1 — черга; її показує сайт обленерго за адресою\n"
        "/svitlo Вінниця 3.1 — усе одразу\n"
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
    """A city, community or oblast and the group, in any order; either may come in a separate message.

    ``/svitlo Вінниця`` remembers the place and asks for the group, ``/svitlo 3.1`` adds the group,
    ``/svitlo Вінниця 3.1`` or ``/svitlo Вінницька 3.1 Вінниця`` does both.
    """
    groups = [word for word in words if word.replace(".", "").isdigit()]
    rest = " ".join(word for word in words if word not in groups)
    saved = _read("choice.json")
    if rest:
        source, town, oblast = _place_from(rest)
        if source is None:
            reason = f"для області «{oblast}» відкритих графіків поки немає" if oblast else f"не знайшов «{rest}»"
            return {"status": "completed", "reply": f"{ICON} {reason[0].upper() + reason[1:]}.\n{HELP}"}
        saved = {"source": source, "place": town, "group": saved.get("group", "") if not groups else ""}
    if groups:
        saved["group"] = groups[0]
    if saved.get("source") not in SOURCES:
        return {"status": "completed", "reply": f"{ICON} Спершу місто, громада чи область: /svitlo Вінниця\n{HELP}"}
    _write("choice.json", saved)
    _write("state.json", {})
    if not saved.get("group"):
        where = saved.get("place") or SOURCES[saved["source"]][0]
        return {"status": "completed", "reply": f"{ICON} Записав: {where} ({SOURCES[saved['source']][0]}). "
                                                "Тепер черга: /svitlo 3.1 — її показує сайт обленерго за адресою."}
    return {"status": "completed",
            "reply": f"{ICON} Стежу за світлом: {_where(saved['source'], saved['group'])}. Графік прийде протягом 6 хв."}


def _place_from(text: str) -> Tuple[Optional[str], str, str]:
    """An oblast first («Вінницька Вінниця»: oblast + label), else a city or community."""
    words = text.split()
    for cut in range(len(words), 0, -1):
        source = find_source(" ".join(words[:cut]))
        if source:
            return source, " ".join(words[cut:])[:60], SOURCES[source][0]
    return resolve(text)
