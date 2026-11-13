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
from typing import Any, Dict, Iterable, Mapping

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


async def poll_once(watch: Any, transport: Any = None) -> bool:
    """One read; True when a picture was delivered to the watch."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_S, transport=transport,
                                     headers={"User-Agent": USER_AGENT}) as client:
            response = await client.get(SOURCE_URL)
        response.raise_for_status()
        regions = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("alert_poll_failed", error_type=type(exc).__name__)
        return False
    if not isinstance(regions, list):
        logger.warning("alert_poll_unexpected_shape")
        return False
    watch.accept_poll()
    watch.handle_relay({"regions": air_levels(regions)})
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
