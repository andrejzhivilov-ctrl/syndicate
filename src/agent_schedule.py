"""The fixed schedule inside syndicate-agent: it replaces n8n (stage 6 of 7).

The jobs live here, in the repository, with tests; an agent cannot add or move one. Every job
is off until Andrii names it in ``SYNDICATE_SCHEDULE`` (comma-separated, in ``.env``), as the
n8n workflows were off until he activated them. Each run is one call, never a loop:

- the same job never runs twice at once (a still-running job is skipped and logged);
- a run is cut off after ``JOB_TIMEOUT_S``;
- a result other than ``ok`` is written to the journal and sent once to Andrii through the
  alarm bot, with the reason; nothing is retried before the next scheduled time.

Times are Kyiv time. The jobs run ``agent_jobs.handle``, the code the n8n workflows used to call,
so a reminder costs no model call and the weekly review stays one Hermes turn.
"""
from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from zoneinfo import ZoneInfo

import structlog

from src import learning_feeds, agent_jobs
from src.alert_watch import ALERT_BOT
from src.data_paths import ensure_dir
from src.proactive import cron_matches

logger = structlog.get_logger(__name__)

ENV_VAR = "SYNDICATE_SCHEDULE"
TIMEZONE = ZoneInfo("Europe/Kyiv")
JOB_TIMEOUT_S = 300


@dataclass(frozen=True)
class Job:
    name: str
    cron: str  # "m h dom mon dow", Kyiv time
    agent: str
    kind: str
    description: str
    text: str = ""


#: Alex still runs under the id ``trainer`` until stage 7.
JOBS: Dict[str, Job] = {job.name: job for job in (
    Job("alex_morning_plan", "0 8 * * *", "trainer", "morning_brief",
        "Алекс: план дня з Obsidian"),
    Job("alex_checkin", "30 21 * * *", "trainer", "checkin", "Алекс: контроль дня",
        "Як пройшов день: тренування, їжа, вода, сон? Коротко напиши, Тренер врахує."),
    Job("alex_measurements", "30 7 * * 1", "trainer", "reminder", "Алекс: тижневі заміри",
        "Понеділок — тижневі заміри: вага натщесерце після туалету, талія, груди, стегна, фото в тих "
        "самих умовах. Надішли Тренеру, він внесе в щоденник."),
    Job("alex_learning", "0 4 * * 1", "trainer", "learning",
        "Алекс: нове з підключених джерел за тиждень"),
    Job("alex_reflection", "0 5 * * 1", "trainer", "reflection",
        "Алекс: тижнева саморефлексія (один виклик Hermes)"),
)}


def enabled_from_env(raw: Optional[str] = None) -> Tuple[List[str], List[str]]:
    """Job names Andrii switched on, and the names that match no job."""
    value = os.getenv(ENV_VAR, "") if raw is None else raw
    names = [part.strip() for part in value.split(",") if part.strip()]
    return [n for n in names if n in JOBS], [n for n in names if n not in JOBS]


async def run_job(job: Job, gateway: Any) -> Dict[str, Any]:
    """One run of one job; the result is honest about what did not happen."""
    if job.kind != "learning":
        return await agent_jobs.handle(job.agent, {"kind": job.kind, "text": job.text}, gateway)
    items, failed = await learning_feeds.collect(job.agent)
    feeds = learning_feeds.feeds_for(job.agent)
    if not feeds or len(failed) == len(feeds):
        return {"status": "unavailable", "kept": 0, "feeds_failed": len(failed),
                "reason": "no_feeds_configured" if not feeds else "feeds_unreachable"}
    result = await agent_jobs.handle(job.agent, {"kind": "learning", "items": items}, gateway)
    return {**result, "feeds_failed": len(failed)}


def _journal(job: Job, result: Dict[str, Any], started: datetime) -> None:
    path = ensure_dir("schedule") / f"{job.name}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"at": started.isoformat(timespec="seconds"), **result}
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")


def _reason(result: Dict[str, Any]) -> str:
    return str(result.get("reason") or result.get("error") or result.get("status") or "unknown")


class AgentSchedule:
    def __init__(self, gateway: Any, enabled: Iterable[str]) -> None:
        self.gateway = gateway
        self.jobs = [JOBS[name] for name in dict.fromkeys(enabled) if name in JOBS]
        self._last: Dict[str, str] = {}
        self._running: Dict[str, asyncio.Task] = {}
        self._tasks: Set[asyncio.Task] = set()

    def due(self, now: datetime) -> List[Job]:
        local = now.astimezone(TIMEZONE)
        stamp = local.strftime("%Y-%m-%d %H:%M")
        out = []
        for job in self.jobs:
            if cron_matches(job.cron, local) and self._last.get(job.name) != stamp:
                self._last[job.name] = stamp
                out.append(job)
        return out

    def start_due(self, now: datetime) -> List[str]:
        started = []
        for job in self.due(now):
            running = self._running.get(job.name)
            if running is not None and not running.done():
                logger.warning("scheduled_job_overlap_skipped", job=job.name)
                continue
            task = asyncio.create_task(self.run(job, now))
            self._running[job.name] = task
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
            started.append(job.name)
        return started

    async def run(self, job: Job, started: Optional[datetime] = None) -> Dict[str, Any]:
        moment = started or datetime.now(timezone.utc)
        try:
            result = await asyncio.wait_for(run_job(job, self.gateway), JOB_TIMEOUT_S)
        except asyncio.TimeoutError:
            result = {"status": "error", "error": "timeout"}
        except Exception as exc:  # noqa: BLE001 - one failed job never stops the schedule
            result = {"status": "error", "error": type(exc).__name__}
        logger.info("scheduled_job_done", job=job.name, status=result.get("status"), reason=result.get("reason"))
        try:
            _journal(job, result, moment)
        except OSError as exc:
            logger.warning("schedule_journal_failed", job=job.name, error=type(exc).__name__)
        if result.get("status") != "ok":
            await self._report(job, result)
        return result

    async def _report(self, job: Job, result: Dict[str, Any]) -> bool:
        text = (f"Розклад: «{job.description}» ({job.name}) не виконано: {_reason(result)}. "
                "Повтору не буде, наступна спроба за розкладом.")
        try:
            owner = await self.gateway.owner_user_id() if self.gateway else None
            return bool(owner) and bool(await self.gateway.send(ALERT_BOT, owner, text))
        except Exception as exc:  # noqa: BLE001 - the report is best effort, the journal has it
            logger.warning("schedule_report_failed", job=job.name, error=type(exc).__name__)
            return False

    async def loop(self) -> None:
        logger.info("schedule_started", jobs=[job.name for job in self.jobs])
        while True:
            now = datetime.now(timezone.utc)
            try:
                self.start_due(now)
            except Exception as exc:  # noqa: BLE001 - keep the clock alive
                logger.error("schedule_tick_failed", error=type(exc).__name__)
            await asyncio.sleep(60.5 - datetime.now(timezone.utc).second)
