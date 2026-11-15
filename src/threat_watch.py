"""Air Force messages about the chosen oblast, through Alice, with signs on the map (15.11.2026).

The Air Force of the Armed Forces of Ukraine posts every threat on Telegram (@kpszsu) as a short
text: «🏍 Чернігівщина: Реактивний БпЛА курсом на Олишівку/Козелець», «💣 КАБи на
Дніпропетровщину». This module reads the channel's public web preview (no account, no key), keeps
the posts about the oblasts of the alert choice (``/regions``), quotes each new one once with its
link, and puts a sign on the map at the settlement it names. The text is never rewritten. A sign
is placed only at a settlement the message names; no direction is drawn. A country-wide warning
(a massed attack, strategic bombers, MiG-31K) goes at once in its own «НЕГАЙНЕ ПОВІДОМЛЕННЯ».
None of it is a measured track, and the caption says so.
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Tuple

import structlog

from src import alert_map, neptun, water_outages
from src.alert_map import Marker
from src.data_paths import ensure_dir

logger = structlog.get_logger(__name__)

CHANNEL = "kpszsu"
INTERVAL_S = 60
MAP_GAP_S = 50  # a map after every card; rounds are a minute apart, so this only stops doubles
MARKER_TTL_S = 30 * 60
PLACES_PATH = Path(__file__).with_name("alert_places.json")

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
#: The Air Force's own signs first: 🛵 a Shahed, 🏍 a jet Shahed («Реактивний БпЛА»).
KINDS = (("💣", "kab"), ("КАБ", "kab"), ("🚀", "missile"), ("ракет", "missile"), ("🏍", "jet"),
         ("Реактивний БпЛА", "jet"), ("🛵", "drone"), ("БпЛА", "drone"), ("шахед", "drone"))
#: Warnings for the whole country, sent at once in their own message, whatever region is chosen
#: (operator, 15.11.2026): a massed attack, strategic or long-range bombers, MiG-31K (Kinzhal), launches.
URGENT = re.compile(r"масован|МіГ-?31|Ту-?95|Ту-?160|Ту-?22|стратегічн\w* авіац|Кинджал|"
                    r"пуск\w* (?:крилатих|балістичн|ракет)|по всій території", re.IGNORECASE)
URGENT_HEADING = "❗❗❗ НЕГАЙНЕ ПОВІДОМЛЕННЯ ❗❗❗"
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


def is_urgent(text: str) -> bool:
    """A warning for the whole country: a massed attack, strategic bombers, MiG-31K, launches."""
    return bool(URGENT.search(text))


def urgent_notice(number: int, text: str) -> str:
    return f"{URGENT_HEADING}\n{text}"  # no link or source (operator, 15.11.2026)


def marker(text: str, oblast: str) -> Optional[Marker]:
    """A sign at the settlement the message names; no direction is drawn (operator, 15.11.2026)."""
    named = settlement(text, oblast)
    if named is None:
        return None  # an oblast alone is no place for a sign: the text is quoted, nothing is pinned
    point = named[1]
    return Marker(kind_of(text), point[0], point[1])


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
    """The oblasts of the alert choice; with no choice (all Ukraine) none — Alice sends a summary instead."""
    found = [alert_map.oblast_of(place) for place in chosen or []]
    return sorted({oblast for oblast in found if oblast})


KIND_ICONS = {"drone": "🛵", "jet": "🏍", "missile": "🚀", "kab": "💣", "other": "⚠️"}
SUMMARY_GAP_S = 300  # with no oblast chosen: one short list at most every five minutes


@lru_cache(maxsize=1)
def _city_pattern() -> Tuple[Optional[Pattern[str]], Dict[str, str]]:
    """Every city of Ukraine (status «місто»), to place a post that names only a city («Харків: …»)."""
    owner: Dict[str, str] = {}
    for oblast in alert_map.oblasts():
        for name, _lon, _lat in alert_map.cities(oblast):
            if len(name) >= _MIN_NAME:
                owner.setdefault(name, oblast)
    if not owner:
        return None, {}
    names = sorted(owner, key=len, reverse=True)
    return re.compile(r"(?<!\w)(" + "|".join(re.escape(name) for name in names) + r")(?!\w)"), owner


def oblasts_named(text: str) -> List[str]:
    """The oblasts a post is about: named directly, or through a city when no oblast is named."""
    named = named_oblasts(text)
    if named:
        return named
    pattern, owner = _city_pattern()
    found = pattern.search(text) if pattern else None
    return [owner[found.group(1)]] if found else []


def summary(posts: List[Tuple[int, str]]) -> Optional[str]:
    """«🛵 Чернігівська, Житомирська» per kind of threat, from the posts' own words; None when none names a place."""
    by_kind: Dict[str, List[str]] = {}
    for _number, text in posts:
        for oblast in oblasts_named(text):
            names = by_kind.setdefault(kind_of(text), [])
            name = alert_map.short_name(oblast)
            if name not in names:
                names.append(name)
    if not by_kind:
        return None
    lines = [f"{KIND_ICONS[kind]} {', '.join(names)}" for kind, names in by_kind.items()]
    return ("⚠️ УВАГА! ЗАГРОЗИ ЗАРАЗ:\n" + "\n".join(lines) +
            "\nОбери область у /regions — і я надсилатиму картку з картою.")


def new_posts(page: str, last: Optional[int]) -> Tuple[List[Tuple[int, str]], Optional[int]]:
    """Posts newer than the mark; the first read only sets it, so old posts are not replayed."""
    found = [(number, text) for channel, number, text in water_outages.posts(page)
             if channel.lower() == CHANNEL and text]
    newest = max((number for number, _t in found), default=last)
    if last is None:
        return [], newest
    return [(number, text) for number, text in found if number > last], newest


FORECASTS_PER_HOUR = 6  # unofficial forecasts repeat across channels: a cap keeps the urgent ones urgent


def _neptun_path() -> Path:
    return ensure_dir("threats") / "neptun.json"


def _read_neptun() -> Dict[str, Any]:
    try:
        data = json.loads(_neptun_path().read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _write_neptun(data: Dict[str, Any]) -> None:
    path = _neptun_path()
    spare = path.with_suffix(".tmp")
    spare.write_text(json.dumps(data), encoding="utf-8")
    spare.replace(path)


LIVE_TTL_S = 3 * 60  # NEPTUN's snapshot is fetched every round; older than this it is not shown
_live: Dict[str, Any] = {"at": 0.0, "data": None}


async def refresh_live(transport: Any = None, now: Optional[float] = None) -> None:
    """Keep NEPTUN's latest threat snapshot for the maps; a failed fetch keeps the old one to age out."""
    data = await neptun.threats(transport)
    if data is not None:
        _live.update(at=time.time() if now is None else now, data=data)


def map_markers(oblast: str, now: Optional[float] = None) -> Tuple[List[Marker], str]:
    """The Air Force signs of the last half hour plus NEPTUN's placed threats when its snapshot is fresh.

    The second value is the credit printed small inside the picture: NEPTUN's terms ask for it
    whenever its data is shown; the message itself carries no source (operator, 15.11.2026).
    """
    now = time.time() if now is None else now
    signs = recent_markers(oblast, now)
    live = neptun.markers(_live["data"], alert_map.full_name(oblast)) if now - _live["at"] < LIVE_TTL_S else None
    if not live:
        return signs, ""
    near = {(sign.kind, round(sign.lon, 1), round(sign.lat, 1)) for sign in signs}
    extra = [sign for sign in live if (sign.kind, round(sign.lon, 1), round(sign.lat, 1)) not in near]
    return signs + extra, neptun.CREDIT


LEVEL_HEADINGS = {"R": "🔴 УВАГА! ПОВІТРЯНА ТРИВОГА — ЧЕРВОНИЙ РІВЕНЬ", "Y": "🟡 УВАГА! НЕБЕЗПЕКА — ЖОВТИЙ РІВЕНЬ",
                  "P": "🟡 УВАГА! НЕБЕЗПЕКА — ЖОВТИЙ РІВЕНЬ", "N": "⚠️ УВАГА! ЗАГРОЗА"}


def threat_card(level: str, territory: str, texts: List[str], phrase: str) -> str:
    """The threat as one card, like the alert cards: level, the watched territory, what flies, a phrase.

    The Air Force's words are kept as they are; no link, no source, no explanation (operator, 15.11.2026).
    """
    flying = "\n".join(texts)
    return f"{LEVEL_HEADINGS.get(level, LEVEL_HEADINGS['N'])}\n📍 {territory}\n{flying}\n💬 {phrase}"



class ThreatWatch:
    def __init__(self, gateway: Any, bot: str, alerts: Any, transport: Any = None) -> None:
        self._gateway, self._bot, self._alerts, self._transport = gateway, bot, alerts, transport
        self._map_sent_at = 0.0
        self._summary_sent_at = 0.0
        self._waiting: List[Tuple[int, str]] = []  # posts for the next summary, when no oblast is chosen
        self._forecast_times: List[float] = []

    async def run_once(self, chosen: Optional[List[str]], now: Optional[float] = None) -> int:
        oblasts = watched_oblasts(chosen)
        await refresh_live(self._transport, now)
        forecast_count = await self._send_forecasts(oblasts)
        page = await water_outages.fetch_channel(CHANNEL, self._transport)
        if page is None:
            return forecast_count
        posts, newest = new_posts(page, _last_seen())
        if newest is not None:
            _save_last(newest)
        urgent = [(number, text) for number, text in posts if is_urgent(text)]
        posts = [post for post in posts if post not in urgent]
        sent = forecast_count + await self._send_urgent(urgent)
        if not oblasts:
            return sent + await self._summarise(posts, now)
        relevant = [(number, text, oblast) for number, text in posts for oblast in oblasts if concerns(text, oblast)]
        if not relevant:
            return sent
        owner = await self._gateway.owner_user_id()
        if not owner:
            return sent
        for _number, text, oblast in relevant:
            sign = marker(text, oblast)
            if sign:
                remember(oblast, sign, now)
        for oblast in sorted({oblast for _n, _t, oblast in relevant}):  # a card, then its map
            places = [place for place in chosen or [] if alert_map.oblast_of(place) == oblast]
            texts = [text for _n, text, home in relevant if home == oblast]
            await self._gateway.send(self._bot, owner, self._card(oblast, places, texts))
            await self._send_map(owner, [oblast], now, places)
        return sent + len(relevant)

    def _card(self, oblast: str, places: List[str], texts: List[str]) -> str:
        from src.alert_phrases import DEFAULT_BAG
        from src.alert_watch import _label

        order = {"N": 0, "P": 1, "Y": 2, "R": 3}
        level = max((self._alerts.level_of(place) for place in places or [oblast]), key=lambda lv: order.get(lv, 0))
        territory = ", ".join(_label(place) for place in places) or alert_map.full_name(oblast)
        return threat_card(level, territory, texts, DEFAULT_BAG.draw("red" if level == "R" else "yellow"))

    async def _send_urgent(self, urgent: List[Tuple[int, str]]) -> int:
        """Each country-wide warning at once, in its own message, whatever region is chosen."""
        owner = await self._gateway.owner_user_id() if urgent else None
        if not owner:
            return 0
        for number, text in urgent:
            await self._gateway.send(self._bot, owner, urgent_notice(number, text))
        return len(urgent)

    async def _summarise(self, posts: List[Tuple[int, str]], now: Optional[float]) -> int:
        """No oblast chosen: gather the posts and send the list of oblasts at most every SUMMARY_GAP_S."""
        now = time.time() if now is None else now
        self._waiting += posts
        if not self._waiting or now - self._summary_sent_at < SUMMARY_GAP_S:
            return 0
        text, count = summary(self._waiting), len(self._waiting)
        self._waiting = []
        owner = await self._gateway.owner_user_id() if text else None
        if not owner:
            return 0
        self._summary_sent_at = now
        await self._gateway.send(self._bot, owner, text)
        return count

    async def _send_map(self, owner: str, oblasts: List[str], now: Optional[float], chosen: List[str]) -> None:
        """The picture right after the card, with no caption; credits are printed small inside it."""
        now = time.time() if now is None else now
        send = getattr(self._gateway, "send_photo", None)
        if send is None or now - self._map_sent_at < MAP_GAP_S:
            return
        self._map_sent_at = now
        for oblast in oblasts:
            signs, credit = map_markers(oblast, now)
            try:
                png = await asyncio.to_thread(alert_map.render, self._alerts.level_of, oblast, chosen, signs,
                                              None, credit)
            except Exception as exc:  # noqa: BLE001 - the card has gone; a map is extra
                logger.warning("threat_map_failed", error_type=type(exc).__name__)
                continue
            if png:
                await send(self._bot, owner, png, "")

    async def _send_forecasts(self, oblasts: List[str]) -> int:
        """Unofficial forecasts of attacks from NEPTUN's channel feed, each as an urgent notice.

        The first read only remembers what is there. A forecast naming only other oblasts than the
        chosen ones is skipped; one naming no place concerns everyone. At most FORECASTS_PER_HOUR.
        """
        data = await neptun.messages(self._transport)
        state = _read_neptun()
        found, seen = neptun.forecasts(data, state.get("seen", []))
        _write_neptun({"seen": seen, "ready": True})
        if not state.get("ready"):
            return 0
        now = time.time()
        self._forecast_times = [t for t in self._forecast_times if now - t < 3600]
        wanted = [m for m in found if not oblasts or not oblasts_named(str(m.get("text")))
                  or set(oblasts_named(str(m.get("text")))) & set(oblasts)]
        wanted = wanted[: max(FORECASTS_PER_HOUR - len(self._forecast_times), 0)]
        owner = await self._gateway.owner_user_id() if wanted else None
        if not owner:
            return 0
        for message in wanted:
            await self._gateway.send(self._bot, owner, neptun.forecast_notice(message, URGENT_HEADING))
            self._forecast_times.append(now)
        return len(wanted)

    async def loop(self, chosen_places: Any) -> None:
        logger.info("threat_watch_started", interval_s=INTERVAL_S)
        while True:
            try:
                await self.run_once(chosen_places())
            except Exception as exc:  # noqa: BLE001 - one bad round must not end the watch
                logger.warning("threat_watch_round_failed", error_type=type(exc).__name__)
            await asyncio.sleep(INTERVAL_S)
