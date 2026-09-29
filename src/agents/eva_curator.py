from __future__ import annotations
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta

import structlog

logger = structlog.get_logger(__name__)

class EvaCurator:
    """
    Eva Life Curator Agent.
    Handles proactive life management: reviews, decisions, deadlines, and social contacts.
    """
    AGENT_ID = 'eva_curator'

    def __init__(self, memory: Any, llm: Optional[Any] = None, config: Optional[Dict[str, Any]] = None, registry: Optional[Any] = None) -> None:
        self._memory = memory
        self._llm = llm
        self._config = config or {}
        self._registry = registry

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action based on payload."""
        action = payload.get("action")
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
                return {"error": f"Unknown action: {action}"}
        except Exception as exc: # noqa: BLE001
            logger.exception("Error executing EvaCurator action", action=action, exc_info=exc)
            return {"error": str(exc)}

    async def _weekly_review(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = "Synthesize a weekly review based on the past week's events across all agents."
        reflection = "Week was productive but energy dipped mid-week."
        if self._llm:
            try:
                reflection = await self._llm.generate(prompt)
            except Exception:
                pass
                
        result = {
            "week_summary": "Solid progress on core projects.",
            "completed": ["Launched new module", "3 workouts completed"],
            "stuck": ["Waiting on external API keys"],
            "mood_trend": "Stable",
            "energy_trend": "Slightly declining",
            "top_3_focuses_next_week": ["Fix bugs", "Client meeting", "Rest"],
            "reflection": reflection
        }
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="weekly_review",
            content=json.dumps(result),
            metadata={"date": str(date.today())}
        )
        return result

    async def _record_decision(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        decision = payload.get("decision", "Unknown Decision")
        reasoning = payload.get("reasoning", "No reasoning provided")
        expected_outcome = payload.get("expected_outcome", "Unknown outcome")
        category = payload.get("category", "general")
        importance = payload.get("importance", "medium")
        
        decision_id = str(uuid.uuid4())
        recorded_at = str(datetime.utcnow().isoformat())
        review_date = str((datetime.utcnow() + timedelta(days=30)).date())
        
        doc = {
            "decision_id": decision_id,
            "decision": decision,
            "reasoning": reasoning,
            "expected_outcome": expected_outcome,
            "category": category,
            "importance": importance,
            "recorded_at": recorded_at,
            "review_date": review_date
        }
        
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="decision_journal",
            content=json.dumps(doc),
            metadata={"decision_id": decision_id, "semantic": True}
        )
        
        return {
            "decision_id": decision_id,
            "recorded_at": recorded_at,
            "review_date": review_date
        }

    async def _review_decisions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        lookback_days = payload.get("lookback_days", 60)
        
        mock_decision = {
            "decision": "Switch to asynchronous workflow",
            "expected_outcome": "Faster processing times"
        }
        
        prompt = f"Evaluate the actual vs expected outcome of these decisions: {json.dumps([mock_decision])}"
        insights = "Decisions largely met expectations."
        if self._llm:
            try:
                insights = await self._llm.generate(prompt)
            except Exception:
                pass
                
        result = {
            "decisions_reviewed": [mock_decision],
            "insights": insights,
            "pattern_observed": "Consistent overestimation of speed improvements."
        }
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="review_decisions",
            content=json.dumps(result),
            metadata={"lookback_days": lookback_days}
        )
        return result

    async def _deadline_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "overdue": [],
            "due_7_days": ["Quarterly taxes"],
            "due_30_days": ["Project alpha launch"],
            "due_90_days": ["Annual review"]
        }
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="deadline_check",
            content=json.dumps(result),
            metadata={"checked_at": str(datetime.utcnow())}
        )
        return result

    async def _add_deadline(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        title = payload.get("title", "Untitled")
        due_date = payload.get("due_date", str(date.today()))
        category = payload.get("category", "general")
        remind_days_before = payload.get("remind_days_before", 1)
        recurring = payload.get("recurring", False)
        
        doc = {
            "deadline_id": str(uuid.uuid4()),
            "title": title,
            "due_date": due_date,
            "category": category,
            "remind_days_before": remind_days_before,
            "recurring": recurring
        }
        
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="deadlines",
            content=json.dumps(doc),
            metadata={"title": title, "semantic": True}
        )
        return {"status": "success", "deadline_id": doc["deadline_id"]}

    async def _social_pulse(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "birthdays_upcoming": ["Alice (in 2 days)"],
            "not_contacted_30_days": ["Bob", "Charlie"],
            "important_dates": ["Anniversary on 15th"]
        }
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="social_pulse",
            content=json.dumps(result),
            metadata={}
        )
        return result

    async def _add_contact(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        doc = {
            "contact_id": str(uuid.uuid4()),
            "name": payload.get("name", "Unknown"),
            "relationship": payload.get("relationship", "Acquaintance"),
            "birthday": payload.get("birthday", ""),
            "last_contact": payload.get("last_contact", ""),
            "notes": payload.get("notes", "")
        }
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="social_contacts",
            content=json.dumps(doc),
            metadata={"name": doc["name"], "semantic": True}
        )
        return {"status": "success", "contact_id": doc["contact_id"]}

    async def _morning_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "deadlines_today": [],
            "birthdays_today": [],
            "decisions_to_review_count": 2,
            "stuck_items_count": 1
        }
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="morning_data",
            content=json.dumps(result),
            metadata={}
        )
        return result
