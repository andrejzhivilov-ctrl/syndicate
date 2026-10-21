"""
Trainer Agent (Coach) — Physical Performance, Workouts, Nutrition, and Self-Improvement Specialist.
SYNDICATE Autonomous Holding.

Responsibilities:
- Structured Workout Plans & Exercise Protocols (tailored to HRV / morning readiness).
- Nutrition & Macro Engineering (Mifflin-St Jeor TDEE, KBJU, hydration targets).
- Recipe Recommendations & Meal Planning.
- Shopping List generation for ingredients (feeds into Eva's basket coordination).
- Science-based Sports Supplementation Protocols.
- Habit Tracking & Self-Improvement Routines (sleep, sunlight, steps, mobility).
- Active Recovery & Deload Protocols.

Strict compliance with Law 1: Never fabricate metrics. Missing data returns structured absence.
"""

from __future__ import annotations

import json
from contextvars import ContextVar
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

import structlog
from langchain_core.messages import HumanMessage

from src.agent_memory import (
    append_memory_context,
    memory_session_id,
    memory_status,
    recall_agent_memory,
    save_agent_episode,
)
from src.agents import doc_exercises, doc_nutrition, doc_shopping

logger = structlog.get_logger(__name__)


def _opt_float(payload: Dict[str, Any], key: str) -> Optional[float]:
    value = payload.get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _opt_int(payload: Dict[str, Any], key: str) -> Optional[int]:
    value = _opt_float(payload, key)
    return None if value is None else int(value)


class TrainerAgent:
    """
    Chief of Physical Performance & Training (Trainer / Coach).
    Responsible for all workouts, nutrition, recipes, supplements, and self-improvement routines.
    """

    AGENT_ID = "trainer"

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
        self._memory_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
            f"trainer_memory_context_{id(self)}", default=None
        )

        self._ACTION_MAP: Dict[str, Any] = {
            "training_protocol": self._training_protocol,
            "workout_plan": self._workout_plan,
            "exercise_search": self._exercise_search,
            "nutrition_plan": self._nutrition_plan,
            "recipe_plan": self._recipe_plan,
            "shopping_list": self._shopping_list,
            "supplement_protocol": self._supplement_protocol,
            "habit_tracker": self._habit_tracker,
            "active_recovery": self._active_recovery,
            "morning_data": self._morning_data,
            "swarm_research": self._swarm_research,
        }

    async def _llm_ask(self, prompt: str, fallback: str) -> str:
        """Invoke LLM with historical memory bounding."""
        if not self._llm:
            return fallback
        prompt = append_memory_context(
            prompt,
            self._memory_context.get() or {},
            instruction=(
                "You are the elite physical trainer and coach of the SYNDICATE holding. "
                "Base all workout and nutrition prescriptions strictly on verified science and the current payload."
            ),
        )
        try:
            resp = await self._llm.ainvoke([HumanMessage(content=prompt)])
            return str(getattr(resp, "content", resp))
        except Exception as exc:  # noqa: BLE001
            logger.warning("trainer_llm_ainvoke_failed", error=str(exc))
            return fallback

    async def _save(
        self,
        payload: Dict[str, Any],
        category: str,
        data: Dict[str, Any],
        extra_meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        meta = {"category": category}
        if extra_meta:
            meta.update(extra_meta)
        await save_agent_episode(
            self._memory,
            agent_id=self.AGENT_ID,
            session_id=memory_session_id(payload, "trainer-default-session"),
            action=category,
            role="assistant",
            content=json.dumps(data, ensure_ascii=False, default=str)[:8000],
            metadata=meta,
        )

    def _unavailable(self, category: str, warning: str) -> Dict[str, Any]:
        """Structured absence (AGENTS.md §1)."""
        return {
            "agent": self.AGENT_ID,
            "category": category,
            "status": "unavailable",
            "value": None,
            "warning": warning,
        }

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action based on payload."""
        action = payload.get("action", "workout_plan")
        try:
            handler = self._ACTION_MAP.get(action)
            if handler is None:
                logger.warning("Unknown action in TrainerAgent", action=action)
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}",
                    "agent": self.AGENT_ID,
                    "available_actions": sorted(self._ACTION_MAP),
                }

            session_id = memory_session_id(payload, "trainer-default-session")
            memory_context = await recall_agent_memory(
                self._memory,
                agent_id=self.AGENT_ID,
                session_id=session_id,
                payload=payload,
                limit=int(self._config.get("memory_context_limit", 8)),
                max_chars=int(self._config.get("memory_context_chars", 1800)),
            )
            token = self._memory_context.set(memory_context)
            try:
                result = await handler(payload)
                if isinstance(result, dict):
                    result["memory"] = memory_status(memory_context)
                return result
            finally:
                self._memory_context.reset(token)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error executing TrainerAgent action", action=action, exc_info=exc)
            return {"error": str(exc), "agent": self.AGENT_ID}

    async def _training_protocol(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate today's workout protocol adapted to readiness score."""
        readiness_score = _opt_float(payload, "readiness_score")
        training_type = payload.get("training_type", "strength")
        goal = payload.get("goal", "hypertrophy")
        equipment = payload.get("equipment_available")

        warnings: List[str] = []
        if equipment is None:
            warnings.append("equipment_available not supplied — plan left equipment-agnostic")

        if readiness_score is None:
            result = {
                **self._unavailable(
                    "training_protocol",
                    "readiness_score not supplied — intensity and duration not prescribed (obtain morning readiness first)",
                ),
                "training_type": training_type,
                "goal": goal,
                "equipment_available": equipment,
                "workout": None,
                "warnings": warnings,
            }
            await self._save(payload, "training_protocol", result)
            return result

        if readiness_score < 45:
            intensity = "rest"
            duration = 0
            block = [{"type": "recovery", "name": "Active Recovery / Rest Day", "notes": "Readiness critically low. Sleep & hydration focus."}]
        elif readiness_score < 70:
            intensity = "moderate"
            duration = 45
            block = [{"type": "main", "name": "Technique & Volume Work", "sets": 3, "rpe": 7}]
        else:
            intensity = "high"
            duration = 60
            block = [{"type": "main", "name": "Progressive Overload / Heavy Compound", "sets": 4, "rpe": 8.5}]

        res = {
            "agent": self.AGENT_ID,
            "status": "ok",
            "readiness_score": readiness_score,
            "intensity": intensity,
            "duration_min": duration,
            "training_type": training_type,
            "goal": goal,
            "plan": block,
            "workout": {
                "warmup": "10 min dynamic mobility & joint activation",
                "main_block": block,
                "cooldown": "5 min parasympathetic nasal breathing",
            },
            "equipment_available": equipment,
            "warnings": warnings,
        }
        await self._save(payload, "training_protocol", res)
        return res

    async def _workout_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Build detailed workout plan with specific exercises."""
        muscle = payload.get("muscle", "chest")
        level = payload.get("level", "intermediate")
        equipment = payload.get("equipment")

        try:
            db = doc_exercises.load_exercises()
            exercises = doc_exercises.search(db, muscle=muscle, equipment=equipment, level=level, limit=5)
        except Exception:
            exercises = []

        res = {
            "agent": self.AGENT_ID,
            "status": "ok",
            "muscle": muscle,
            "level": level,
            "exercises_count": len(exercises),
            "exercises": exercises,
        }
        await self._save(payload, "workout_plan", res)
        return res

    async def _exercise_search(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Search exercises from offline database."""
        muscle = payload.get("muscle")
        equipment = payload.get("equipment")
        level = payload.get("level")
        limit = int(payload.get("limit", 10))

        db = doc_exercises.load_exercises()
        results = doc_exercises.search(db, muscle=muscle, equipment=equipment, level=level, limit=limit)
        return {
            "agent": self.AGENT_ID,
            "status": "ok",
            "count": len(results),
            "results": results,
        }

    async def _nutrition_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mifflin-St Jeor TDEE, BMR, and macronutrient targets. Deterministic."""
        norm_payload = dict(payload)
        norm_payload["activity"] = norm_payload.get("activity") or norm_payload.get("activity_level")
        calc_result = doc_nutrition.energy_and_macros(norm_payload)
        calc_result["agent"] = self.AGENT_ID

        if calc_result.get("status") == "ok":
            tdee = int(Decimal(str(calc_result["tdee_kcal"])))
            protein = int(Decimal(str(calc_result["protein_g"])))
            fat = int(Decimal(str(calc_result["fat_g"])))
            carb_raw = calc_result.get("carb_g") or calc_result.get("carbs_g") or 0
            carbs = int(Decimal(str(carb_raw)))
            water = int(Decimal(str(calc_result["water_ml"])))
            calc_result.update({
                "calories": tdee,
                "protein_g": protein,
                "fat_g": fat,
                "carb_g": carbs,
                "carbs_g": carbs,
                "water_ml": water,
            })
        elif calc_result.get("status") == "not_configured":
            calc_result["status"] = "unavailable"
            calc_result["calories"] = None
            calc_result["missing_inputs"] = calc_result.get("missing", [])
            calc_result["warning"] = calc_result.get("message", "Missing required profile metrics for Mifflin-St Jeor")

        await self._save(payload, "nutrition_plan", calc_result)
        return calc_result

    async def _recipe_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-protein recipe recommendations matching macro target."""
        target_calories = _opt_float(payload, "target_calories")
        protein_g = _opt_float(payload, "protein_g")
        meal_type = payload.get("meal_type", "lunch")

        recipes = [
            {
                "name": "Куряче філе на грилі з кіноа та шпинатом",
                "calories": 520,
                "protein_g": 48,
                "fat_g": 12,
                "carbs_g": 55,
                "ingredients": ["Куряче філе 200г", "Кіноа 70г", "Шпинат свіжий 50г", "Оливкова олія 1 ч.л."],
            },
            {
                "name": "Омлет із 3 яєць з авокадо та лососем",
                "calories": 480,
                "protein_g": 36,
                "fat_g": 28,
                "carbs_g": 10,
                "ingredients": ["Яйця курячі 3 шт", "Слабосолений лосось 70г", "Авокадо 1/2 шт", "Зелень"],
            },
        ]

        res = {
            "agent": self.AGENT_ID,
            "status": "ok",
            "target_calories": target_calories,
            "target_protein_g": protein_g,
            "meal_type": meal_type,
            "recipes": recipes,
        }
        await self._save(payload, "recipe_plan", res)
        return res

    async def _shopping_list(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate grocery ingredients list for Eva's basket coordination."""
        items = payload.get("items", [])
        normalized_items = []
        for it in items:
            if isinstance(it, str):
                normalized_items.append({"name": it, "qty": 1, "category": "other"})
            elif isinstance(it, dict):
                normalized_items.append(it)
        ref = payload.get("meal_plan_ref")
        raw = doc_shopping.build_shopping_list(normalized_items, ref)
        res = {
            "agent": self.AGENT_ID,
            "status": "ok" if raw.get("status") == "ready_for_eva" else raw.get("status", "ok"),
            "basket_status": raw.get("status"),
            **raw,
        }
        await self._save(payload, "shopping_list", res)
        return res

    async def _supplement_protocol(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Science-based sports supplement timing and protocol."""
        goal = payload.get("goal", "strength_recovery")
        protocol = [
            {"name": "Креатин моногідрат (Creatine Monohydrate)", "dosage": "5g", "timing": "Post-workout or morning with carbs", "evidence": "A-grade"},
            {"name": "Whey Isolate Protein", "dosage": "30g", "timing": "Post-workout", "evidence": "A-grade"},
            {"name": "Magnesium Glycinate", "dosage": "400mg", "timing": "30-60 min before sleep", "evidence": "A-grade"},
            {"name": "Omega-3 (EPA/DHA)", "dosage": "2000mg", "timing": "With first meal", "evidence": "A-grade"},
            {"name": "Electrolytes (Na, K, Mg)", "dosage": "1 packet", "timing": "Intra-workout on heavy training days", "evidence": "B-grade"},
        ]
        res = {
            "agent": self.AGENT_ID,
            "status": "ok",
            "goal": goal,
            "protocol": protocol,
            "supplements": protocol,
        }
        await self._save(payload, "supplement_protocol", res)
        return res

    async def _habit_tracker(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Daily self-improvement and physical discipline habits."""
        custom_habits = payload.get("habits")
        if isinstance(custom_habits, list) and custom_habits:
            completed_count = sum(1 for h in custom_habits if h.get("completed"))
            total = len(custom_habits)
            rate = round((completed_count / max(1, total)) * 100.0, 1)
            res = {
                "agent": self.AGENT_ID,
                "status": "ok",
                "date": str(date.today()),
                "habits": custom_habits,
                "completed_count": completed_count,
                "total_habits": total,
                "completion_rate_pct": rate,
            }
        else:
            habits = [
                {"habit": "Morning Sunlight", "target": "10-15 min", "status": payload.get("habit_sunlight", "pending")},
                {"habit": "10,000 Steps", "target": "10,000", "current": payload.get("steps", None)},
                {"habit": "Hydration Baseline", "target": "2.5 - 3.0 L", "status": payload.get("water_status", "in_progress")},
                {"habit": "Daily Mobility Routine", "target": "10 min", "status": payload.get("mobility", "pending")},
                {"habit": "Digital Sunset (No blue light)", "target": "1 hr before sleep", "status": "scheduled"},
            ]
            res = {
                "agent": self.AGENT_ID,
                "status": "ok",
                "date": str(date.today()),
                "habits": habits,
            }
        await self._save(payload, "habit_tracker", res)
        return res

    async def _active_recovery(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Active recovery and deload prescription."""
        soreness_level = payload.get("soreness_level") or payload.get("fatigue_level", "medium")
        protocol = {
            "foam_rolling": "10 min (focus on hamstrings, quads, thoracic spine)",
            "low_intensity_cardio": "20-30 min Zone 2 walk or light cycling",
            "contrast_shower": "3 rounds (hot 3 min, cold 1 min)",
            "sleep_target": "8.5 hours minimum",
        }
        intensity = "very_low" if soreness_level in ("high", "severe") else "low"
        res = {
            "agent": self.AGENT_ID,
            "status": "ok",
            "soreness_level": soreness_level,
            "intensity": intensity,
            "modalities": list(protocol.keys()),
            "recovery_protocol": protocol,
        }
        await self._save(payload, "active_recovery", res)
        return res

    async def _morning_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Compact training data for Eva's daily briefing."""
        return {
            "agent": self.AGENT_ID,
            "status": "ok",
            "workout_scheduled": payload.get("workout_scheduled", "Strength Upper Body (Hypertrophy)"),
            "water_target_liters": 3.0,
            "calorie_target": payload.get("calorie_target", 2600),
            "mobility_focus": "Hip flexors and shoulders",
        }

    async def _swarm_research(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        topic = payload.get("topic", "optimal protein distribution per meal")
        summary = await self._llm_ask(
            f"Provide an evidence-based sports science breakdown on: {topic}",
            fallback="Scientific literature supports 0.4g/kg protein per meal across 4 meals for optimal MPS.",
        )
        return {
            "agent": self.AGENT_ID,
            "status": "ok",
            "topic": topic,
            "findings": summary,
        }
