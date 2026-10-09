"""Dormant schedule contract for a prepared Eva-only text review.

No job in this module dispatches tasks to other agents or performs external
actions. The nightly source provider and production/n8n activation remain unconfigured.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional
from zoneinfo import ZoneInfo

import structlog

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class ScheduledJob:
    name: str
    cron: str          # "m h dom mon dow" — numbers, lists (1,2), ranges (1-5), steps (*/5), *
    task: str          # method name on the orchestrator
    description: str = ""
    timezone: str = "Europe/Kyiv"


DEFAULT_JOBS: List[ScheduledJob] = [
    ScheduledJob(
        "nightly_analysis",
        "0 3 * * *",
        "proactive_nightly_analysis",
        "Євин текстовий аналіз без запуску інших агентів",
        "Europe/Kyiv",
    ),
]


def _field_matches(spec: str, value: int, lo: int, hi: int) -> bool:
    for part in spec.split(","):
        step = 1
        if "/" in part:
            part, step_s = part.split("/", 1)
            step = max(1, int(step_s))
        if part in ("*", ""):
            rng = range(lo, hi + 1)
        elif "-" in part:
            a, b = part.split("-", 1)
            rng = range(int(a), int(b) + 1)
        else:
            rng = range(int(part), int(part) + 1) if step == 1 else range(int(part), hi + 1)
        if value in rng and (value - rng.start) % step == 0:
            return True
    return False


def cron_matches(cron: str, when: datetime) -> bool:
    minute, hour, dom, mon, dow = cron.split()
    py_dow = (when.weekday() + 1) % 7      # cron: 0 = Sunday
    return (
        _field_matches(minute, when.minute, 0, 59)
        and _field_matches(hour, when.hour, 0, 23)
        and _field_matches(dom, when.day, 1, 31)
        and _field_matches(mon, when.month, 1, 12)
        and _field_matches(dow, py_dow, 0, 6)
    )


class ProactiveScheduler:
    def __init__(self, jobs: Optional[List[ScheduledJob]] = None) -> None:
        self.jobs = list(jobs or DEFAULT_JOBS)
        self._last_run: Dict[str, str] = {}

    def due(self, when: datetime) -> List[ScheduledJob]:
        out = []
        for job in self.jobs:
            zone = ZoneInfo(job.timezone)
            local_when = when.replace(tzinfo=zone) if when.tzinfo is None else when.astimezone(zone)
            stamp = local_when.strftime("%Y-%m-%d %H:%M")
            if cron_matches(job.cron, local_when) and self._last_run.get(job.name) != stamp:
                out.append(job)
        return out

    async def run_due(self, when: datetime, orchestrator: Any) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        for job in self.due(when):
            self._last_run[job.name] = when.strftime("%Y-%m-%d %H:%M")
            fn: Optional[Callable[[], Awaitable[Any]]] = getattr(orchestrator, job.task, None)
            if fn is None:
                results[job.name] = {"error": f"missing_task:{job.task}"}
                continue
            try:
                results[job.name] = await fn()
            except Exception as exc:  # noqa: BLE001
                logger.error("scheduled_job_failed", job=job.name, error=str(exc))
                results[job.name] = {"error": str(exc)}
        return results
