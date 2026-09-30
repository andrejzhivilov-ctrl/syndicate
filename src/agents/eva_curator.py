"""
Eva Life Curator — Proactive Life Management, Decision Loop, Deadlines & Social Graph.
v4.1 Verified:
- Uses `await self._llm.ainvoke([HumanMessage(...)])` instead of `.generate()`.
- Matches `MemoryManager.save_episode(session_id=..., agent_id=..., role=..., content=..., metadata=...)`.
- No string passed into `semantic_search` (uses SQL/episodic retrieval safely).
"""

from __future__ import annotations

import json
import uuid
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import structlog
from langchain_core.messages import HumanMessage

logger = structlog.get_logger(__name__)


class EvaCurator:
    """
    Eva Life Curator — proactive life management capabilities.
    Handles weekly reviews, decision loop tracking, deadlines, and social graph.
    """

    AGENT_ID = "eva_curator"

    def __init__(
        self,
        memory: Any,
        llm: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[Any] = None,
    ) -> None:
        self._memory = memory
        self._llm = llm
        self._config = config or {}
        self._registry = registry

    async def _llm_ask(self, prompt: str, fallback: str) -> str:
        if not self._llm:
            return fallback
        try:
            resp = await self._llm.ainvoke([HumanMessage(content=prompt)])
            return str(getattr(resp, "content", resp))
        except Exception as exc:  # noqa: BLE001
            logger.warning("curator_llm_ainvoke_failed", error=str(exc))
            return fallback

    async def _save(self, payload: Dict[str, Any], category: str, data: Dict[str, Any], extra_meta: Optional[Dict[str, Any]] = None) -> None:
        if not self._memory:
            return
        meta = {"category": category}
        if extra_meta:
            meta.update(extra_meta)
        await self._memory.save_episode(
            session_id=payload.get("session_id", "eva-curator-session"),
            agent_id=self.AGENT_ID,
            role="assistant",
            content=json.dumps(data, ensure_ascii=False),
            metadata=meta,
        )

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute curator action based on payload."""
        action = payload.get("action", "weekly_review")
        try:
            if action == "weekly_review":
                return await self._weekly_review(payload)
            elif action == "record_decision":
                return await self._record_decision(payload)
            elif action == "review_decisions":
                return await self._review_decisions(payload)
            elif action == "deadline_check":
                return await self._deadline_check(payload)
            elif action == "add_deadline":
                return await self._add_deadline(payload)
            elif action == "social_pulse":
                return await self._social_pulse(payload)
            elif action == "add_contact":
                return await self._add_contact(payload)
            elif action == "morning_data":
                return await self._morning_data(payload)
            else:
                logger.warning("Unknown action in EvaCurator", action=action)
                return {"error": f"Unknown action: {action}", "agent": self.AGENT_ID}
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error executing EvaCurator action", action=action, exc_info=exc)
            return {"error": str(exc), "agent": self.AGENT_ID}

    async def _weekly_review(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        recent_episodes = []
        if self._memory:
            recent_episodes = await self._memory.get_recent_episodes(
                session_id=payload.get("session_id", "eva-curator-session"),
                agent_id="eva",
                limit=30,
            )

        reflection = await self._llm_ask(
            f"Synthesize a weekly life review and top 3 priorities based on recent events: {json.dumps(recent_episodes[:10], ensure_ascii=False)}",
            fallback="Consistent weekly execution. Focus on strategic priorities and recovery balance.",
        )

        result = {
            "agent": self.AGENT_ID,
            "week_summary": "Productive week across Syndicate domains.",
            "episodes_analyzed": len(recent_episodes),
            "top_3_focuses_next_week": payload.get("focuses", [
                "1. Execute key strategic milestones",
                "2. Maintain physiological readiness & sleep discipline",
                "3. Review pending financial & infrastructure items",
            ]),
            "reflection": reflection,
        }
        await self._save(payload, "weekly_review", result)
        return result

    async def _record_decision(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        decision_id = str(uuid.uuid4())
        decision = payload.get("decision", "")
        reasoning = payload.get("reasoning", "")
        expected_outcome = payload.get("expected_outcome", "")
        category = payload.get("category", "general")
        importance = payload.get("importance", "medium")

        now_date = date.today()
        review_date = now_date + timedelta(days=int(payload.get("review_in_days", 60)))

        record = {
            "agent": self.AGENT_ID,
            "decision_id": decision_id,
            "decision": decision,
            "reasoning": reasoning,
            "expected_outcome": expected_outcome,
            "category": category,
            "importance": importance,
            "recorded_at": str(now_date),
            "review_date": str(review_date),
        }
        await self._save(payload, "decision_journal", record, {"decision_id": decision_id})
        return record

    async def _review_decisions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        lookback_days = int(payload.get("lookback_days", 60))
        past_decisions = payload.get("decisions", [])

        insights = await self._llm_ask(
            f"Review past decisions from {lookback_days} days ago and compare expected vs actual outcomes: {json.dumps(past_decisions, ensure_ascii=False)}",
            fallback="Decision loop review: assumptions were largely sound; continue tracking long-term outcomes.",
        )

        result = {
            "agent": self.AGENT_ID,
            "lookback_days": lookback_days,
            "decisions_reviewed": past_decisions,
            "insights": insights,
        }
        await self._save(payload, "review_decisions", result)
        return result

    async def _deadline_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        deadlines = payload.get("deadlines", [])
        today = date.today()
        overdue: List[Dict[str, Any]] = []
        due_7_days: List[Dict[str, Any]] = []
        due_30_days: List[Dict[str, Any]] = []

        for d in deadlines:
            try:
                due_dt = date.fromisoformat(d.get("due_date", str(today)))
                delta = (due_dt - today).days
                item = {**d, "days_left": delta}
                if delta < 0:
                    overdue.append(item)
                elif delta <= 7:
                    due_7_days.append(item)
                elif delta <= 30:
                    due_30_days.append(item)
            except Exception:
                continue

        result = {
            "agent": self.AGENT_ID,
            "overdue": overdue,
            "due_7_days": due_7_days,
            "due_30_days": due_30_days,
        }
        await self._save(payload, "deadline_check", result)
        return result

    async def _add_deadline(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            "agent": self.AGENT_ID,
            "id": str(uuid.uuid4()),
            "title": payload.get("title", "Untitled Deadline"),
            "due_date": payload.get("due_date", str(date.today() + timedelta(days=30))),
            "category": payload.get("category", "documents"),
            "remind_days_before": int(payload.get("remind_days_before", 7)),
            "recurring": payload.get("recurring", "none"),
            "status": "active",
        }
        await self._save(payload, "deadlines", record)
        return record

    async def _social_pulse(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        contacts = payload.get("contacts", [])
        result = {
            "agent": self.AGENT_ID,
            "contacts_checked": len(contacts),
            "birthdays_upcoming": [c for c in contacts if c.get("birthday_soon")],
            "not_contacted_30_days": [c for c in contacts if c.get("days_since_contact", 0) >= 30],
        }
        await self._save(payload, "social_pulse", result)
        return result

    async def _add_contact(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            "agent": self.AGENT_ID,
            "id": str(uuid.uuid4()),
            "name": payload.get("name", ""),
            "relationship": payload.get("relationship", ""),
            "birthday": payload.get("birthday"),
            "last_contact": payload.get("last_contact", str(date.today())),
            "notes": payload.get("notes", ""),
        }
        await self._save(payload, "social_contacts", record)
        return record

    async def _morning_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        dl = await self._deadline_check(payload)
        result = {
            "agent": self.AGENT_ID,
            "overdue_deadlines": len(dl["overdue"]),
            "due_7_days_count": len(dl["due_7_days"]),
        }
        await self._save(payload, "morning_data", result)
        return result
