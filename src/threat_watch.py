"""Air Force messages about the chosen oblast, through Alice, with signs on the map (15.11.2026).

The Air Force of the Armed Forces of Ukraine posts every threat on Telegram (@kpszsu) as a short
text: «🏍 Чернігівщина: Реактивний БпЛА курсом на Олишівку/Козелець», «💣 КАБи на
Дніпропетровщину». This module reads the channel's public web preview (no account, no key), keeps
the posts about the oblasts of the alert choice (``/regions``), quotes each new one once with its
link, and puts a sign on the map at the settlement it names. The text is never rewritten. A sign
is placed only at a settlement the message names; a direction («з півночі», «з Київщини») becomes
an arrow. None of it is a measured track, and the caption says so.
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from functools import lru_cache
from math import cos, radians
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Tuple

import structlog

from src import alert_map, water_outages
from src.alert_map import Marker
from src.data_paths import ensure_dir

logger = structlog.get_logger(__name__)

CHANNEL = "kpszsu"
INTERVAL_S = 60
MAP_GAP_S = 180  # at most one threat map this often, however busy the night
MARKER_TTL_S = 30 * 60
OFFSET_DEG = 0.35  # how far back an arrow starts when only a side («з півночі») is given
PLACES_PATH = Path(__file__).with_name("alert_places.json")
ICON = "🛰️"
NOTE = "Значки — за повідомленнями Повітряних сил; напрямки приблизні, це не трек."

#: Oblast alarm id -> how the Air Force names it («на Дніпропетровщину», «з Київщини», «Буковина»).
REGION_STEMS: Dict[str, Tuple[str, ...]] = {
    "4": ("Вінниччин", "Вінницьк"), "8": ("Волин",), "9": ("Дніпропетровщин", "Дніпропетровськ"),
    "10": ("Житомирщин", "Житомирськ"), "11": ("Закарпатт",), "12": ("Запорізьк",),
    "13": ("Прикарпатт", "Івано-Франківщин", "Франківщин"), "14": ("Київщин",),
    "15": ("Кіровоградщин", "Кропивниччин"), "16": ("Луганщин",), "17": ("Миколаївщин",),
    "18": ("Одещин",), "19": ("Полтавщин",), "20": ("Сумщин",), "21": ("Тернопільщин",),
    "22": ("Харківщин",), "23": ("Херсонщин",), "24": ("Черкащин",), "25": ("Чернігівщин",),
    "26": ("Буковин", "Чернівеччин"), "27": ("Львівщин",), "28": ("Донеччин",), "3": ("Хмельниччин",),
    "5": ("Рівненщин",), "9999": ("Крим",),
}
#: «з півночі» — where it comes from, as (east, north).
FROM_SIDE = {"північного сходу": (1, 1), "північного заходу": (-1, 1), "південного сходу": (1, -1),
             "південного заходу": (-1, -1), "півночі": (0, 1), "півдня": (0, -1), "сходу": (1, 0),
             "заходу": (-1, 0)}
#: «курсом на південь» — where it heads, so it comes from the opposite side.
HEADING = {"північний схід": (1, 1), "північний захід": (-1, 1), "південний схід": (1, -1),
           "південний захід": (-1, -1), "північ": (0, 1), "південь": (0, -1), "схід": (1, 0), "захід": (-1, 0)}
KINDS = (("💣", "kab"), ("КАБ", "kab"), ("🚀", "missile"), ("ракет", "missile"), ("🛵", "drone"),
         ("🏍", "drone"), ("БпЛА", "drone"), ("шахед", "drone"))
_MIN_NAME = 4  # shorter settlement names are too easily ordinary words

_markers: List[Tuple[float, str, Marker]] = []  # (when, oblast, marker), kept MARKER_TTL_S


def _region_pattern(oblast: str) -> Pattern[str]:
    stems = "|".join(re.escape(stem) for stem in REGION_STEMS.get(oblast, ()))
    return re.compile(rf"(?<!\w)(?:{stems})\w*", re.IGNORECASE) if stems else re.compile(r"(?!)")


@lru_cache(maxsize=1)
def places() -> Dict[str, Dict[str, List[float]]]:
    try:
        return json.loads(PLACES_PATH.read_text(encoding="utf-8"))["places"]
    except (OSError, ValueError, KeyError) as exc:
        logger.warning("threat_places_unreadable", error_type=type(exc).__name__)
        return {}


@lru_cache(maxsize=64)
def _settlements(oblast: str) -> Optional[Pattern[str]]:
    names = sorted((name for name in places().get(oblast, {}) if len(name) >= _MIN_NAME), key=len, reverse=True)
    if not names:
        return None
    return re.compile(r"(?<!\w)(" + "|".join(re.escape(name) for name in names) + r")(?!\w)")


def named_oblasts(text: str) -> List[str]:
    return [oblast for oblast in REGION_STEMS if _region_pattern(oblast).search(text)]


def settlement(text: str, oblast: str) -> Optional[Tuple[str, List[float]]]:
    """The first settlement of this oblast the text names (nominative, as the Air Force writes)."""
    pattern = _settlements(oblast)
    found = pattern.search(text) if pattern else None
    return (found.group(1), places()[oblast][found.group(1)]) if found else None


def concerns(text: str, oblast: str) -> bool:
    """About this oblast: it is named, or one of its settlements is and no other oblast is named."""
    named = named_oblasts(text)
    if oblast in named:
        return True
    return not named and settlement(text, oblast) is not None


def kind_of(text: str) -> str:
    return next((kind for sign, kind in KINDS if sign in text), "other")


def _origin(text: str, target: List[float]) -> Optional[Tuple[float, float]]:
    """Where an arrow starts: a named oblast it comes from, a side, or the opposite of its heading."""
    source = re.search(r"(?<!\w)з\s+(\w+щини|Криму|Буковини|Волині|Закарпаття|Прикарпаття)", text, re.IGNORECASE)
    if source:
        for oblast in named_oblasts(source.group(1)):
            point = alert_map.label_point(oblast)
            if point:
                return point
    side = _vector(text, r"(?<!\w)(?:з|зі)\s+(?:{})", FROM_SIDE, 1)
    side = side or _vector(text, r"курсом\s+на\s+(?:{})(?!\w)", HEADING, -1)
    if side is None:
        return None
    stretch = max(cos(radians(target[1])), 0.3)
    return target[0] + side[0] * OFFSET_DEG / stretch, target[1] + side[1] * OFFSET_DEG


def _vector(text: str, template: str, table: Dict[str, Tuple[int, int]], sign: int) -> Optional[Tuple[int, int]]:
    words = "|".join(sorted(table, key=len, reverse=True))
    found = re.search(template.format(words), text, re.IGNORECASE)
    if not found:
        return None
    word = next(word for word in sorted(table, key=len, reverse=True) if word in found.group(0).lower())
    east, north = table[word]
    return sign * east, sign * north


def marker(text: str, oblast: str) -> Optional[Marker]:
    named = settlement(text, oblast)
    if named is None:
        return None  # an oblast alone is no place for a sign: the text is quoted, nothing is pinned
    point = named[1]
    return Marker(kind_of(text), point[0], point[1], _origin(text, point))


def remember(oblast: str, sign: Marker, now: Optional[float] = None) -> None:
    now = time.time() if now is None else now
    _markers[:] = [entry for entry in _markers if now - entry[0] < MARKER_TTL_S] + [(now, oblast, sign)]


def recent_markers(oblast: str, now: Optional[float] = None) -> List[Marker]:
    now = time.time() if now is None else now
    return [sign for when, home, sign in _markers if home == oblast and now - when < MARKER_TTL_S]


# ── state and the loop ────────────────────────────────────────────────────────────────────


def _state_path() -> Path:
    return ensure_dir("threats") / "state.json"


def _last_seen() -> Optional[int]:
    try:
        value = json.loads(_state_path().read_text(encoding="utf-8")).get("last")
        return int(value) if value is not None else None
    except (OSError, ValueError, TypeError):
        return None


def _save_last(number: int) -> None:
    path = _state_path()
    spare = path.with_suffix(".tmp")
    spare.write_text(json.dumps({"last": number}), encoding="utf-8")
    spare.replace(path)


def watched_oblasts(chosen: Optional[List[str]]) -> List[str]:
    """The oblasts of the alert choice; with no choice (all Ukraine) nothing — that would be every post."""
    found = [alert_map.oblast_of(place) for place in chosen or []]
    return sorted({oblast for oblast in found if oblast})


def new_posts(page: str, last: Optional[int]) -> Tuple[List[Tuple[int, str]], Optional[int]]:
    """Posts newer than the mark; the first read only sets it, so old posts are not replayed."""
    found = [(number, text) for channel, number, text in water_outages.posts(page)
             if channel.lower() == CHANNEL and text]
    newest = max((number for number, _t in found), default=last)
    if last is None:
        return [], newest
    return [(number, text) for number, text in found if number > last], newest


def quote(number: int, text: str) -> str:
    return f"{ICON} Повітряні сили:\n{text}\nhttps://t.me/{CHANNEL}/{number}"


class ThreatWatch:
    def __init__(self, gateway: Any, bot: str, alerts: Any, transport: Any = None) -> None:
        self._gateway, self._bot, self._alerts, self._transport = gateway, bot, alerts, transport
        self._map_sent_at = 0.0

    async def run_once(self, chosen: Optional[List[str]], now: Optional[float] = None) -> int:
        oblasts = watched_oblasts(chosen)
        if not oblasts:
            return 0
        page = await water_outages.fetch_channel(CHANNEL, self._transport)
        if page is None:
            return 0
        posts, newest = new_posts(page, _last_seen())
        if newest is not None:
            _save_last(newest)
        relevant = [(number, text, oblast) for number, text in posts for oblast in oblasts if concerns(text, oblast)]
        if not relevant:
            return 0
        owner = await self._gateway.owner_user_id()
        if not owner:
            return 0
        await self._gateway.send(self._bot, owner, "\n\n".join(quote(number, text) for number, text, _o in relevant))
        for _number, text, oblast in relevant:
            sign = marker(text, oblast)
            if sign:
                remember(oblast, sign, now)
        await self._send_map(owner, sorted({oblast for _n, _t, oblast in relevant}), now)
        return len(relevant)

    async def _send_map(self, owner: str, oblasts: List[str], now: Optional[float]) -> None:
        now = time.time() if now is None else now
        send = getattr(self._gateway, "send_photo", None)
        if send is None or now - self._map_sent_at < MAP_GAP_S:
            return
        self._map_sent_at = now
        for oblast in oblasts:
            try:
                png = await asyncio.to_thread(alert_map.render, self._alerts.level_of, oblast, (),
                                              recent_markers(oblast, now))
            except Exception as exc:  # noqa: BLE001 - the quotes have gone; a map is extra
                logger.warning("threat_map_failed", error_type=type(exc).__name__)
                continue
            if png:
                await send(self._bot, owner, png, f"{alert_map.caption(oblast)}\n{NOTE}")

    async def loop(self, chosen_places: Any) -> None:
        logger.info("threat_watch_started", interval_s=INTERVAL_S)
        while True:
            try:
                await self.run_once(chosen_places())
            except Exception as exc:  # noqa: BLE001 - one bad round must not end the watch
                logger.warning("threat_watch_round_failed", error_type=type(exc).__name__)
            await asyncio.sleep(INTERVAL_S)
