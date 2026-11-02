"""Air-raid watch: Ukraine Alarm level -> a phrase from the operator's bank -> Alice's Telegram bot.

Runs without any model call. A notification that Telegram did not accept stays queued
for the next tick, and a source that stays silent is reported once, because a quiet bot
must not read as a quiet sky.
"""
from __future__ import annotations

import asyncio
from typing import Any, List, Optional

import structlog

from src.alert_phrases import AlertTracker
from src.integrations.public_data import alerts_region, alerts_token, region_alert_level

logger = structlog.get_logger(__name__)

POLL_INTERVAL_S = 60
ALERT_BOT = "alice"
#: Consecutive failed readings before the operator is told the watch is blind.
BLIND_AFTER = 5
BLIND_NOTICE = "⚠️ Не бачу стану тривог: Ukraine Alarm не відповідає ({reason}). Орієнтуйся на сирену й інші джерела."
SIGHT_NOTICE = "✅ Стан тривог знову бачу."


class AlertWatch:
    def __init__(self, vault: Any, gateway: Any, *, tracker: Optional[AlertTracker] = None, transport: Any = None) -> None:
        self._vault = vault
        self._gateway = gateway
        self._tracker = tracker or AlertTracker()
        self._transport = transport
        self._failures = 0
        self._pending: List[str] = []

    async def _read(self) -> Optional[str]:
        reading = await region_alert_level(
            await alerts_token(self._vault), await alerts_region(self._vault), transport=self._transport
        )
        if reading["status"] == "ok":
            if self._failures >= BLIND_AFTER:
                self._pending.append(SIGHT_NOTICE)
            self._failures = 0
            return reading["level"]
        self._failures += 1
        if self._failures == BLIND_AFTER:
            self._pending.append(BLIND_NOTICE.format(reason=reading["reason"]))
        logger.warning("alert_watch_blind", reason=reading["reason"], failures=self._failures)
        return None

    async def _flush(self) -> None:
        owner = await self._gateway.owner_user_id() if self._pending else None
        while owner and self._pending and await self._gateway.send(ALERT_BOT, owner, self._pending[0]):
            self._pending.pop(0)

    async def tick(self) -> None:
        notification = self._tracker.update(await self._read())
        if notification:
            self._pending.append(notification)
        await self._flush()

    async def loop(self) -> None:
        while True:
            try:
                await self.tick()
            except Exception as exc:  # noqa: BLE001 - one bad tick must not end the watch
                logger.warning("alert_watch_tick_failed", error_type=type(exc).__name__)
            await asyncio.sleep(POLL_INTERVAL_S)
