"""
Proactive scheduler — the Syndicate writes first.

* 07:30 Morning briefing (Eva composes Doc/Fin/Kira/Curator morning data)
* 21:00 Evening reflection (Doc recovery + Kira 5-minute sparring prompt)

The scheduler is intentionally tiny: n8n owns the real cron (see
``n8n_templates``); this module defines the schedule contract, evaluates cron
expressions deterministically (so it is testable) and exposes the tasks the
n8n webhooks call.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class ScheduledJob:
    name: str
    cron: str          # "m h dom mon dow" — numbers, lists (1,2), ranges (1-5), steps (*/5), *
    task: str          # method name on the orchestrator
    description: str = ""


DEFAULT_JOBS: List[ScheduledJob] = [
    ScheduledJob("morning_briefing", "30 7 * * *", "proactive_daily_briefing", "Ранковий бриф Єви"),
    ScheduledJob("evening_reflection", "0 21 * * *", "proactive_evening_reflection", "Вечірній рефлекс Дока та Кіри"),
    ScheduledJob("weekly_review", "0 20 * * 0", "weekly_life_review", "Недільний Life Review"),
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
        stamp = when.strftime("%Y-%m-%d %H:%M")
        out = []
        for job in self.jobs:
            if cron_matches(job.cron, when) and self._last_run.get(job.name) != stamp:
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
