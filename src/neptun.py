"""Threat positions and channel forecasts from NEPTUN's open API (neptun.in.ua), 15.11.2026.

NEPTUN aggregates the Air Force, the official alert API and 89 monitoring channels and publishes
them through a free, keyless, read-only API. Andrii accepted its terms on 15.11.2026: a visible
«Дані: NEPTUN» next to the data, polling no more often than every 5 seconds (we poll once a
minute), and saying plainly that it is not an official alert. What is used here:

* ``/api/v1/threats`` — active threats with coordinates. A threat with no point of its own
  (``areaOnly``), a low-confidence one, or one no longer active gets no sign: never a guessed place.
* ``/api/v1/messages`` — the channels' feed. Only posts that forecast or warn of an attack
  («ймовірна масована атака», «очікується», «готуються до удару») are used, sent once, word for word,
  marked unofficial, with the channel's name.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx
import structlog

from src.alert_map import Marker

logger = structlog.get_logger(__name__)

BASE = "https://neptun.in.ua"
ATTRIBUTION = "Дані: Карта повітряних тривог — NEPTUN (neptun.in.ua), не офіційна тривога"
#: NEPTUN's type -> our sign. FPV and reconnaissance are front-line noise for a home map: no sign.
KINDS = {"uav": "drone", "missile": "missile", "ballistic": "missile", "kab": "kab"}
CONFIDENT = {"medium", "high"}
OFFICIAL_CHANNELS = {"повітряні сили зсу", "@kpszsu", "@ukrainealarmsignal"}  # read directly, or alerts
#: A forecast or warning of an attack, not a report of one in flight.
FORECAST = re.compile(
    r"ймовірн\w*\s+(?:\w+\s+)?(?:масован|атак|удар|пуск)|очіку\w*\s+(?:\w+\s+)?(?:масован|атак|удар|пуск)|"
    r"можлив\w*\s+(?:\w+\s+)?(?:масован|атак|удар|пуск)|готу\w*\s+(?:до\s+)?(?:масован|атак|удар|пуск)|"
    r"прогноз\w*\s+(?:\w+\s+)?(?:атак|удар)|масован\w*\s+(?:атак|удар|комбінован)|загроз\w*\s+масован",
    re.IGNORECASE)


async def _get(path: str, transport: Any = None) -> Optional[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=20, transport=transport, follow_redirects=False) as client:
            response = await client.get(f"{BASE}{path}")
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, dict) else None
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("neptun_fetch_failed", path=path, error_type=type(exc).__name__)
        return None


def _kind(threat: Dict[str, Any]) -> Optional[str]:
    kind = KINDS.get(str(threat.get("type")))
    words = f"{threat.get('title') or ''} {threat.get('explanationShort') or ''}".lower()
    return "jet" if kind == "drone" and "реактив" in words else kind


def markers(data: Optional[Dict[str, Any]], oblast_name: str) -> Optional[List[Marker]]:
    """Signs for one oblast («Дніпропетровська область»); None when NEPTUN gave nothing usable."""
    if not data or not isinstance(data.get("threats"), list):
        return None
    out = []
    for threat in data["threats"]:
        kind = _kind(threat)
        placed = isinstance(threat.get("lat"), (int, float)) and isinstance(threat.get("lon"), (int, float))
        if (kind and placed and threat.get("region") == oblast_name and not threat.get("areaOnly")
                and threat.get("status", "active") == "active" and threat.get("confidenceLevel") in CONFIDENT):
            out.append(Marker(kind, float(threat["lon"]), float(threat["lat"])))
    return out


async def threats(transport: Any = None) -> Optional[Dict[str, Any]]:
    return await _get("/api/v1/threats", transport)


def _key(message: Dict[str, Any]) -> str:
    text = re.sub(r"\W+", " ", str(message.get("text") or "")).lower().strip()[:120]
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def forecasts(data: Optional[Dict[str, Any]], seen: List[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """New unofficial forecasts (not seen before, the same text from several channels once)."""
    if not data or not isinstance(data.get("messages"), list):
        return [], seen
    known, found = set(seen), []
    for message in data["messages"]:
        text, channel = str(message.get("text") or ""), str(message.get("channel") or "")
        if channel.lower() in OFFICIAL_CHANNELS or not FORECAST.search(text):
            continue
        key = _key(message)
        if key not in known:
            known.add(key)
            found.append(message)
    return found, (seen + [_key(m) for m in found])[-500:]


def forecast_notice(message: Dict[str, Any], heading: str) -> str:
    return (f"{heading}\n⚠️ Неофіційно — {message.get('channel')}:\n{message.get('text')}\n{ATTRIBUTION}")


async def messages(transport: Any = None) -> Optional[Dict[str, Any]]:
    return await _get("/api/v1/messages", transport)
