"""Air-raid alerts for all of Ukraine without a key (13.11.2026).

Ukraine Alarm answers our server with 403 and its webhook never delivered, and Andrii's one
API key belongs to his Viber bot, which must not share it. siren.pp.ua is the public, keyless
mirror of the same Ukraine Alarm data (the Home Assistant integration uses it), with the same
region ids, down to districts and communities. Once a minute this module reads the full
picture and hands it to AlertWatch, the same path the relay Worker would have used, so the
place Andrii watches is chosen later in Alice's chat (/regions) from the whole country.

A failed read sends nothing: AlertWatch notices the silence and says so, it never reads as a
calm sky. ``ALERT_POLL=off`` in the environment switches the poll off.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, Iterable, Mapping, Optional

import httpx
import structlog

logger = structlog.get_logger(__name__)

SOURCE_URL = "https://siren.pp.ua/api/v3/alerts"
INTERVAL_S = 60
TIMEOUT_S = 20
USER_AGENT = "SYNDICATE-alerts/1 (one request a minute)"


def air_levels(regions: Iterable[Any]) -> Dict[str, str]:
    """Region id -> "R" (red level) or "Y" (any other active air-raid alert); others dropped."""
    levels: Dict[str, str] = {}
    for region in regions or []:
        if not isinstance(region, Mapping):
            continue
        for alert in region.get("activeAlerts") or []:
            if not isinstance(alert, Mapping) or alert.get("type") != "AIR":
                continue
            region_id = str(alert.get("regionId") or region.get("regionId"))
            red = any(isinstance(level, Mapping) and str(level.get("alertLevel")).lower() == "red"
                      for level in alert.get("activeAlertLevels") or [])
            levels[region_id] = "R" if red or levels.get(region_id) == "R" else "Y"
    return levels


#: Fallback with the same upstream data on another host (checked 14.11.2026: same update time to the
#: second as siren.pp.ua). Regions are keyed by name, so they are mapped onto Ukraine Alarm ids.
FALLBACK_URL = "https://vadimklimenko.com/map/statuses.json"


def _id_for(name: str, parent: Optional[str]) -> Optional[str]:
    from src.alert_watch import NAMES, UP

    return next((region for region, title in NAMES.items() if title == name and UP.get(region) == parent), None)


def fallback_levels(data: Any) -> Dict[str, str]:
    """Region id -> "R"/"Y" from the fallback's nested oblast -> district names; unknown names dropped."""
    levels: Dict[str, str] = {}

    def walk(places: Any, parent: Optional[str]) -> None:
        for name, place in (places or {}).items() if isinstance(places, Mapping) else []:
            if not isinstance(place, Mapping):
                continue
            region = _id_for(str(name), parent)
            if region and place.get("enabled"):
                levels[region] = "R" if str(place.get("alert_level")).lower() == "red" else "Y"
            if region:
                walk(place.get("districts"), region)
                walk(place.get("communities"), region)

    walk(data.get("states") if isinstance(data, Mapping) else None, None)
    return levels


async def _get_json(url: str, transport: Any) -> Any:
    async with httpx.AsyncClient(timeout=TIMEOUT_S, transport=transport,
                                 headers={"User-Agent": USER_AGENT}) as client:
        response = await client.get(url)
    response.raise_for_status()
    return response.json()


async def read_picture(transport: Any = None) -> Optional[Dict[str, str]]:
    """The air-raid picture from siren.pp.ua, or from the fallback when siren fails; None if both fail."""
    try:
        regions = await _get_json(SOURCE_URL, transport)
        if isinstance(regions, list):
            return air_levels(regions)
        logger.warning("alert_poll_unexpected_shape", source="siren")
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("alert_poll_failed", source="siren", error_type=type(exc).__name__)
    try:
        data = await _get_json(FALLBACK_URL, transport)
        if isinstance(data, Mapping) and isinstance(data.get("states"), Mapping):
            logger.info("alert_poll_fallback_used")
            return fallback_levels(data)
        logger.warning("alert_poll_unexpected_shape", source="fallback")
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("alert_poll_failed", source="fallback", error_type=type(exc).__name__)
    return None


async def poll_once(watch: Any, transport: Any = None) -> bool:
    """One read; True when a picture was delivered to the watch."""
    picture = await read_picture(transport)
    if picture is None:
        return False
    watch.accept_poll()
    watch.handle_relay({"regions": picture})
    return True


def enabled() -> bool:
    return os.getenv("ALERT_POLL", "on").strip().lower() not in ("off", "0", "false", "no")


async def loop(watch: Any) -> None:
    logger.info("alert_poll_started", source=SOURCE_URL, interval_s=INTERVAL_S)
    while True:
        try:
            await poll_once(watch)
        except Exception as exc:  # noqa: BLE001 - one bad round must not end the poll
            logger.warning("alert_poll_round_failed", error_type=type(exc).__name__)
        await asyncio.sleep(INTERVAL_S)
