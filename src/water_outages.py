"""Water supply notices for the chosen region, through Alice, marked 🚰 (14.11.2026).

No water utility in Ukraine publishes outages as data, and no national source exists. They post
them on Telegram. This module reads the public web preview (t.me/s/<channel>, no account, no
key) of the region's water utility where one was found, and of the regional military
administration, keeps only posts about water outages, accidents or pressure, and sends each new
one once with its link. Nothing is summarised or rewritten: the post is quoted and linked.

Channels were checked live on 14.11.2026 (title and a post that day). Lookalike channels with
Russian names (for example "Sumy_ODA") are deliberately absent. Regions without a verified
channel are listed as unavailable, never guessed.
"""
from __future__ import annotations

import asyncio
import html
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
import structlog

from src.data_paths import ensure_dir
from src.outage_phrases import say

logger = structlog.get_logger(__name__)

INTERVAL_S = 420
ICON = "🚰"
QUOTE_CHARS = 600
#: Region name Andrii types -> channels, the water utility first. Verified 14.11.2026.
CHANNELS: Dict[str, Tuple[str, ...]] = {
    "Вінницька": ("vinvoda_info", "VinnytsiaODA"),
    "Волинська": ("volynskaODA",),
    "Дніпропетровська": ("dnipropetrovskaODA",),
    "Донецька": ("donetskaODA",),
    "Житомирська": ("zhytomyrskaODA",),
    "Закарпатська": ("zakarpatskaODA",),
    "Запорізька": ("zoda_gov_ua",),
    "Івано-Франківська": ("onyshchuksvitlana",),
    "м. Київ": ("KyivCityOfficial",),
    "Київська": ("kyivoda",),
    "Кіровоградська": ("kirovogradskaODA",),
    "Луганська": ("luhanskaVTSA",),
    "Львівська": ("kozytskyy_maksym_official",),
    "Одеська": ("infoxvodokanal", "odeskaODA"),
    "Полтавська": ("poltavskaODA",),
    "Тернопільська": ("ternopilskaODA",),
    "Харківська": ("synegubov",),
    "Херсонська": ("khersonskaODA",),
    "Хмельницька": ("khmelnytskaODA",),
    "Черкаська": ("cherkaskaODA",),
    "Чернівецька": ("vodokanal_cv_ua", "chernivetskaODA"),
    "Чернігівська": ("chernigivskaODA",),
}
#: Regions without a verified channel yet: said plainly instead of guessed.
MISSING = ("Миколаївська", "Рівненська", "Сумська")
#: Water utility channels: every water post counts, the place filter applies to administrations only.
WATER_UTILITIES = {"vinvoda_info", "vodokanal_cv_ua", "infoxvodokanal"}
_WATER = re.compile(r"вод(а|и|у|ою|опостач|опровід|оканал)|без води", re.IGNORECASE)
_OUTAGE = re.compile(r"відключ|припин|не буде|немає|відсутн|аварі|пориву|тиск|ремонт|обмежен|графік|подач",
                     re.IGNORECASE)
_ID = re.compile(r'^(?P<channel>[^"/]+)/(?P<number>\d+)"')
_TEXT = re.compile(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(?P<text>.*?)</div>', re.S)


def about_water(text: str) -> bool:
    return bool(_WATER.search(text) and _OUTAGE.search(text))


def _plain(fragment: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", fragment)
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def posts(page: str) -> List[Tuple[str, int, str]]:
    """(channel, post id, text) of the posts on a t.me/s page, oldest first."""
    out = []
    for chunk in page.split('data-post="')[1:]:  # one chunk per post: its text never leaks into another
        ident, text = _ID.match(chunk), _TEXT.search(chunk)
        if ident:
            out.append((ident.group("channel"), int(ident.group("number")), _plain(text.group("text")) if text else ""))
    return out


# ── choice and state ──────────────────────────────────────────────────────────────────────


def _path(name: str) -> Path:
    return ensure_dir("water") / name


def _read(name: str) -> Dict[str, Any]:
    try:
        data = json.loads(_path(name).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _write(name: str, data: Dict[str, Any]) -> None:
    path = _path(name)
    spare = path.with_suffix(".tmp")
    spare.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    spare.replace(path)


def choice() -> Optional[str]:
    region = _read("choice.json").get("region")
    return region if region in CHANNELS else None


def find_region(text: str) -> Optional[str]:
    wanted = text.strip().lower().replace("область", "").strip()
    if not wanted:
        return None
    for region in list(CHANNELS) + list(MISSING):
        if wanted == region.lower() or wanted in region.lower():
            return region
    return None


# ── reading ───────────────────────────────────────────────────────────────────────────────


async def fetch_channel(channel: str, transport: Any = None) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=20, transport=transport, follow_redirects=False) as client:
            response = await client.get(f"https://t.me/s/{channel}")
        response.raise_for_status()
        return response.text
    except httpx.HTTPError as exc:
        logger.warning("water_fetch_failed", channel=channel, error_type=type(exc).__name__)
        return None


def place() -> str:
    return str(_read("choice.json").get("place") or "")


_GENERIC = {"громада", "міська", "селищна", "сільська", "територіальна", "місто", "м.", "смт", "село"}


def stems(town: str) -> List[str]:
    """Word stems of a city or community name, so «Вінниця» also matches «Вінниці», «Вінницею»."""
    words = [word for word in re.split(r"[\s,]+", town.lower()) if word and word not in _GENERIC]
    return [word[:-2] if len(word) > 5 else word for word in words]


def relevant(channel: str, text: str) -> bool:
    """A water post; from a regional administration it must also name the chosen place."""
    if not about_water(text):
        return False
    wanted = stems(place())
    return channel in WATER_UTILITIES or not wanted or any(stem in text.lower() for stem in wanted)


def _quote(region: str, channel: str, number: int, text: str) -> str:
    body = text if len(text) <= QUOTE_CHARS else text[:QUOTE_CHARS].rsplit(" ", 1)[0] + "…"
    where = f"{region}, {place()}" if place() else region
    return f"{ICON} {say('water')}\n{where} (@{channel}):\n{body}\nhttps://t.me/{channel}/{number}"


async def new_notices(region: str, transport: Any = None) -> List[str]:
    """Water posts newer than the last seen one per channel; the first read only sets the mark."""
    state = _read("state.json")
    seen = state.get("seen", {}) if state.get("region") == region else {}
    messages = []
    for channel in CHANNELS[region]:
        page = await fetch_channel(channel, transport)
        if page is None:
            continue
        found = posts(page)
        last = seen.get(channel)
        if last is not None:
            messages += [_quote(region, channel, number, text) for chan, number, text in found
                         if number > last and relevant(channel, text) and chan.lower() == channel.lower()]
        if found:
            seen[channel] = max(number for _c, number, _t in found)
    _write("state.json", {"region": region, "seen": seen})
    return messages


async def run_once(gateway: Any, bot: str, transport: Any = None) -> int:
    region = choice()
    if region is None:
        return 0
    messages = await new_notices(region, transport)
    owner = await gateway.owner_user_id() if messages else None
    for text in messages if owner else []:
        await gateway.send(bot, owner, text)
    return len(messages)


async def loop(gateway: Any, bot: str) -> None:
    logger.info("water_watch_started", interval_s=INTERVAL_S)
    while True:
        try:
            await run_once(gateway, bot)
        except Exception as exc:  # noqa: BLE001 - one bad round must not end the watch
            logger.warning("water_watch_round_failed", error_type=type(exc).__name__)
        await asyncio.sleep(INTERVAL_S)


# ── Alice's /voda ─────────────────────────────────────────────────────────────────────────

HELP = ("/voda — останні повідомлення про воду в твоїй області\n"
        "/voda Вінницька Вінниця — область і (за бажанням) місто чи громада\n"
        "/voda список — області з джерелами\n"
        "/voda вимкнути — не надсилати")


async def recent(region: str, transport: Any = None, limit: int = 3) -> List[str]:
    found: List[str] = []
    for channel in CHANNELS[region]:
        page = await fetch_channel(channel, transport)
        found += [_quote(region, channel, number, text) for chan, number, text in posts(page or "")
                  if relevant(channel, text) and chan.lower() == channel.lower()]
    return found[-limit:]


async def reply(text: str, transport: Any = None) -> Dict[str, Any]:
    words = text.split()
    if words[:1] == ["список"]:
        lines = [f"• {region}" for region in sorted(CHANNELS)] + [f"• {region} — джерело ще не знайдено"
                                                                    for region in MISSING]
        return {"status": "completed", "reply": "Області:\n" + "\n".join(lines)}
    if words[:1] == ["вимкнути"]:
        _write("choice.json", {})
        return {"status": "completed", "reply": f"{ICON} Повідомлення про воду більше не надсилатиму."}
    if words:
        return _choose(" ".join(words))
    region = choice()
    if region is None:
        return {"status": "completed", "reply": f"{ICON} Область не вибрана.\n{HELP}"}
    found = await recent(region, transport)
    body = "\n\n".join(found) if found else f"{ICON} Свіжих повідомлень про воду в {region} не знайдено."
    return {"status": "completed", "reply": body}


def _region_of_town(text: str) -> Optional[str]:
    """The water region of a city or community, through the alert region tree («Дніпро», «Павлоград»)."""
    from src.power_outages import oblast_of

    oblast = oblast_of(text)
    if oblast is None:
        return None
    name = oblast.replace(" область", "")
    return next((region for region in list(CHANNELS) + list(MISSING) if region == name), None)


def _choose(text: str) -> Dict[str, Any]:
    """The region first, then optionally the city or community (``/voda Вінницька Вінниця``)."""
    words = text.split()
    region, town = find_region(words[0]) if words else None, " ".join(words[1:])[:60]
    if region is not None and not re.search(rf"(?<!\w){re.escape(words[0].lower())}(?!\w)", region.lower()):
        region, town = None, ""  # «Дніпро» is a city, not «Дніпропетровська» (live 14.11.2026)
    if region is None:
        region, town = find_region(text), ""
    if region is None:
        region, town = _region_of_town(text), text.strip()[:60]
    if region is None:
        return {"status": "completed", "reply": f"Не знайшов «{text}».\n{HELP}"}
    if region in MISSING:
        return {"status": "unavailable", "reply": f"{ICON} Для області «{region}» ще немає перевіреного джерела."}
    _write("choice.json", {"region": region, "place": town})
    _write("state.json", {})
    where = f"{region}, {town}" if town else region
    return {"status": "completed",
            "reply": f"{ICON} Стежу за водою: {where}. Нові повідомлення приходитимуть з посиланням."}
