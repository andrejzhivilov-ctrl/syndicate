"""
Doc Agent — Health, Training, Nutrition, and Medical Intelligence Specialist.
v4.1 Verified:
- Zero fabricated emergency medical data (strict safety rule: never invent blood type/allergies).
- Uses `await self._llm.ainvoke([HumanMessage(content=...)])` instead of synchronous `.generate()`.
- Matches `MemoryManager.save_episode(session_id=..., agent_id=..., role=..., content=..., metadata=...)`.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List, Optional

import structlog
from langchain_core.messages import HumanMessage

logger = structlog.get_logger(__name__)


class DocAgent:
    """
    Health, training, and nutrition agent (Doc).
    Handles physiological data, readiness, protocols, nutrition, and medical records.
    """

    AGENT_ID = "doc"

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
        """Helper to invoke async ChatModel cleanly via ainvoke()."""
        if not self._llm:
            return fallback
        try:
            resp = await self._llm.ainvoke([HumanMessage(content=prompt)])
            return str(getattr(resp, "content", resp))
        except Exception as exc:  # noqa: BLE001
            logger.warning("doc_llm_ainvoke_failed", error=str(exc))
            return fallback

    async def _save(self, payload: Dict[str, Any], category: str, data: Dict[str, Any], extra_meta: Optional[Dict[str, Any]] = None) -> None:
        """Helper to persist episode with matching signature."""
        if not self._memory:
            return
        meta = {"category": category}
        if extra_meta:
            meta.update(extra_meta)
        await self._memory.save_episode(
            session_id=payload.get("session_id", "doc-default-session"),
            agent_id=self.AGENT_ID,
            role="assistant",
            content=json.dumps(data, ensure_ascii=False),
            metadata=meta,
        )

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action based on payload."""
        action = payload.get("action", "summarize")
        try:
            if action == "summarize":
                return await self._summarize(payload)
            elif action == "extract":
                return await self._extract(payload)
            elif action == "morning_readiness":
                return await self._morning_readiness(payload)
            elif action == "training_protocol":
                return await self._training_protocol(payload)
            elif action == "nutrition_plan":
                return await self._nutrition_plan(payload)
            elif action == "biomarker_trend":
                return await self._biomarker_trend(payload)
            elif action == "screening_calendar":
                return await self._screening_calendar(payload)
            elif action == "emergency_card":
                return await self._emergency_card(payload)
            elif action == "pre_visit_dossier":
                return await self._pre_visit_dossier(payload)
            elif action == "compliance_check":
                return await self._compliance_check(payload)
            elif action == "nervous_system":
                return await self._nervous_system(payload)
            elif action == "morning_data":
                return await self._morning_data(payload)
            elif action in ("swarm_research", "deep_medical_research"):
                return await self._swarm_research(payload)
            else:
                logger.warning("Unknown action in DocAgent", action=action)
                return {"error": f"Unknown action: {action}", "agent": self.AGENT_ID}
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error executing DocAgent action", action=action, exc_info=exc)
            return {"error": str(exc), "agent": self.AGENT_ID}

    async def _summarize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("content") or payload.get("text", "")
        if not text:
            return {"error": "No content provided", "agent": self.AGENT_ID}
        summary = await self._llm_ask(
            f"Summarize the following medical/document content concisely:\n\n{text[:4000]}",
            fallback=f"Summary of {len(text)} chars.",
        )
        res = {"summary": summary, "agent": self.AGENT_ID}
        await self._save(payload, "summarize", res, {"length": len(text)})
        return res

    async def _extract(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("content") or payload.get("text", "")
        fields = payload.get("fields", [])
        extracted_str = await self._llm_ask(
            f"Extract the following fields as JSON: {fields}\n\nDocument:\n{text[:4000]}",
            fallback=json.dumps({f: None for f in fields}),
        )
        res = {"extracted": extracted_str, "agent": self.AGENT_ID}
        await self._save(payload, "extract", res, {"fields": fields})
        return res

    async def _morning_readiness(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        hrv_ms = float(payload.get("hrv_ms", 50.0))
        sleep_hours = float(payload.get("sleep_hours", 7.5))
        sleep_quality = float(payload.get("sleep_quality", 80.0))
        resting_hr = float(payload.get("resting_hr", 65.0))
        steps_yesterday = int(payload.get("steps_yesterday", 8000))
        stress_score = float(payload.get("stress_score", 30.0))

        hrv_score = min(100.0, max(0.0, (hrv_ms / 50.0) * 75.0))
        if 7.0 <= sleep_hours <= 9.0:
            sleep_score = 100.0
        elif sleep_hours < 7.0:
            sleep_score = max(0.0, (sleep_hours / 7.0) * 100.0)
        else:
            sleep_score = max(0.0, 100.0 - (sleep_hours - 9.0) * 15.0)

        sq_score = min(100.0, max(0.0, sleep_quality))
        rhr_score = min(100.0, max(0.0, 100.0 - (resting_hr - 55.0) * 2.5))
        steps_score = min(100.0, max(0.0, (steps_yesterday / 8000.0) * 85.0))
        s_score = min(100.0, max(0.0, 100.0 - stress_score))

        composite = (
            hrv_score * 0.30
            + sleep_score * 0.25
            + sq_score * 0.15
            + rhr_score * 0.15
            + steps_score * 0.10
            + s_score * 0.05
        )
        score = round(composite, 1)

        warnings: List[str] = []
        if hrv_ms < 35:
            warnings.append("Low HRV detected: sympathetic nervous system dominance")
        if sleep_hours < 6.0:
            warnings.append("Significant sleep debt (< 6h)")
        if resting_hr > 75:
            warnings.append("Elevated resting heart rate")

        if score < 45:
            zone = "red"
            intensity = "rest"
            deload = True
        elif score < 70:
            zone = "yellow"
            intensity = "light" if score < 55 else "moderate"
            deload = False
        else:
            zone = "green"
            intensity = "intense"
            deload = False

        result = {
            "agent": self.AGENT_ID,
            "score": score,
            "zone": zone,
            "recommended_intensity": intensity,
            "warnings": warnings,
            "deload_suggested": deload,
        }
        await self._save(payload, "morning_readiness", result, {"score": score, "zone": zone})
        return result

    async def _training_protocol(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        readiness_score = float(payload.get("readiness_score", 75.0))
        training_type = payload.get("training_type", "strength")
        goal = payload.get("goal", "hypertrophy")
        equipment = payload.get("equipment_available", ["barbell", "dumbbells", "pullup_bar"])

        if readiness_score < 45:
            intensity = "low (deload / recovery)"
            duration = 25
        elif readiness_score < 70:
            intensity = "moderate"
            duration = 45
        else:
            intensity = "high"
            duration = 60

        notes = await self._llm_ask(
            f"Create a concise training note for a {training_type} session ({goal}), readiness {readiness_score}/100, equipment: {equipment}.",
            fallback=f"Structured {training_type} protocol calibrated for readiness {readiness_score}.",
        )

        result = {
            "agent": self.AGENT_ID,
            "workout": {
                "warmup": "10 min dynamic mobility + joint activation",
                "main_block": [
                    "Compound Primary Lift: 4x6-8 @ RPE 7.5",
                    "Secondary Accessory: 3x10-12",
                    "Core & Postural Stability: 3 sets",
                ],
                "cooldown": "5 min parasympathetic nasal breathing",
            },
            "duration_min": duration,
            "intensity": intensity,
            "notes": notes,
        }
        await self._save(payload, "training_protocol", result, {"readiness": readiness_score})
        return result

    async def _nutrition_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        goal = payload.get("goal", "maintenance")
        weight_kg = float(payload.get("weight_kg", 80.0))
        height_cm = float(payload.get("height_cm", 180.0))
        age = int(payload.get("age", 35))
        sex = payload.get("sex", "male")
        activity_level = payload.get("activity_level", "moderate")

        # Real Mifflin-St Jeor formula
        bmr = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age) + (5.0 if sex == "male" else -161.0)
        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }
        tdee = bmr * multipliers.get(activity_level, 1.55)

        if goal == "cut":
            calories = tdee - 400
        elif goal == "bulk":
            calories = tdee + 300
        else:
            calories = tdee

        protein_g = weight_kg * 2.0
        fat_g = weight_kg * 1.0
        carbs_g = max(50.0, (calories - (protein_g * 4.0) - (fat_g * 9.0)) / 4.0)
        water_ml = weight_kg * 35.0

        plan = {
            "agent": self.AGENT_ID,
            "calories": round(calories),
            "protein_g": round(protein_g),
            "fat_g": round(fat_g),
            "carbs_g": round(carbs_g),
            "water_ml": round(water_ml),
        }
        await self._save(payload, "nutrition_plan", plan, {"weight": weight_kg, "goal": goal})
        return plan

    async def _biomarker_trend(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        biomarkers = payload.get("biomarkers", [])
        narrative = await self._llm_ask(
            f"Analyze these biomarker values and trends, projecting any out-of-range trajectories:\n{json.dumps(biomarkers, ensure_ascii=False)}",
            fallback="Biomarker trend evaluation completed.",
        )

        result = {
            "agent": self.AGENT_ID,
            "biomarkers_count": len(biomarkers),
            "narrative": narrative,
            "next_tests_recommended": ["CBC", "Ferritin", "Vitamin D (25-OH)", "HbA1c", "Lipid Panel"],
        }
        await self._save(payload, "biomarker_trend", result)
        return result

    async def _screening_calendar(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        age = int(payload.get("age", 35))
        last_checkups = payload.get("last_checkups", {})

        annual = ["blood_pressure", "dental", "vision", "comprehensive_blood_panel"]
        overdue = [t for t in annual if t not in last_checkups]
        upcoming = [t for t in annual if t in last_checkups]

        if age >= 45 and "colonoscopy" not in last_checkups:
            overdue.append("colonoscopy")

        result = {
            "agent": self.AGENT_ID,
            "upcoming": upcoming,
            "overdue": overdue,
            "schedule_12_months": ["Annual Blood Panel (Q1)", "Dental Checkup (Q2)", "Cardio/ECG Check (Q3)"],
        }
        await self._save(payload, "screening_calendar", result, {"age": age})
        return result

    async def _emergency_card(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return verified emergency medical card.
        SAFETY RULE: Never return fabricated medical data (no fake blood types, allergies, or phone numbers).
        """
        supplied_profile = payload.get("medical_profile")
        if isinstance(supplied_profile, dict) and supplied_profile.get("blood_type"):
            card = {
                "agent": self.AGENT_ID,
                "status": "verified",
                "blood_type": supplied_profile.get("blood_type"),
                "allergies": supplied_profile.get("allergies", []),
                "conditions": supplied_profile.get("conditions", []),
                "medications": supplied_profile.get("medications", []),
                "emergency_contacts": supplied_profile.get("emergency_contacts", []),
                "last_updated": str(date.today()),
            }
            await self._save(payload, "emergency_card", card)
            return card

        # Check if a verified card was previously saved in episodic memory
        if self._memory:
            recent = await self._memory.get_recent_episodes(
                session_id=payload.get("session_id", "doc-default-session"),
                agent_id=self.AGENT_ID,
                limit=20,
            )
            for ep in recent:
                meta = ep.get("metadata") or {}
                if meta.get("category") == "emergency_card":
                    try:
                        parsed = json.loads(ep.get("content", "{}"))
                        if parsed.get("status") == "verified":
                            return parsed
                    except Exception:
                        pass

        # Explicitly unconfigured — zero fake values
        return {
            "agent": self.AGENT_ID,
            "status": "not_configured",
            "blood_type": None,
            "allergies": [],
            "conditions": [],
            "medications": [],
            "emergency_contacts": [],
            "warning": "Emergency medical profile has not been configured yet. Provide verified 'medical_profile' in payload to initialize.",
        }

    async def _pre_visit_dossier(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        visit_type = payload.get("visit_type", "general")
        symptoms = payload.get("symptoms", [])
        summary = await self._llm_ask(
            f"Compose a clinical pre-visit dossier for a {visit_type} appointment. Reported symptoms: {symptoms}.",
            fallback=f"Structured pre-visit summary for {visit_type} consultation.",
        )
        result = {
            "agent": self.AGENT_ID,
            "visit_type": visit_type,
            "summary": summary,
            "symptoms": symptoms,
            "questions_for_doctor": [
                "What differential diagnoses should we rule out first?",
                "Are any additional blood panels or imaging studies indicated?",
            ],
        }
        await self._save(payload, "pre_visit_dossier", result)
        return result

    async def _compliance_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        items = payload.get("protocol_items", [])
        evaluated = []
        for item in items:
            name = item.get("name", "item")
            freq = item.get("prescribed_frequency", "daily")
            actual = item.get("actual_completed", True)
            evaluated.append({
                "name": name,
                "prescribed": freq,
                "completed": bool(actual),
                "status": "adherent" if actual else "missed",
            })
        rate = round((sum(1 for x in evaluated if x["completed"]) / max(1, len(evaluated))) * 100.0, 1)
        result = {
            "agent": self.AGENT_ID,
            "compliance_rate_pct": rate,
            "items": evaluated,
        }
        await self._save(payload, "compliance_check", result)
        return result

    async def _nervous_system(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        hrv_ms = float(payload.get("hrv_ms", 45.0))
        stress_score = float(payload.get("stress_score", 60.0))
        technique = "Physiological Sigh (double inhale + long exhale)" if stress_score >= 60 else "Box Breathing (4-4-4-4)"
        result = {
            "agent": self.AGENT_ID,
            "breathing_exercise": technique,
            "duration_min": 5,
            "sleep_hygiene_tips": [
                "Zero blue light 60 min prior to sleep",
                "Room temperature 18-19°C",
                "Magnesium glycinate 400mg before bed",
            ],
            "grounding_exercise": "5-4-3-2-1 sensory grounding protocol",
        }
        await self._save(payload, "nervous_system", result, {"hrv": hrv_ms, "stress": stress_score})
        return result

    async def _morning_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        readiness = await self._morning_readiness(payload)
        result = {
            "agent": self.AGENT_ID,
            "readiness_score": readiness["score"],
            "zone": readiness["zone"],
            "recommended_intensity": readiness["recommended_intensity"],
            "water_target_ml": self._config.get("water_target_ml", 2500),
            "warnings": readiness["warnings"],
        }
        await self._save(payload, "morning_data", result)
        return result

    async def _swarm_research(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Deep medical / pharmacology research via Swarm (Scout, Extractor, Critic)."""
        from src.swarm import SwarmResearcher

        query = payload.get("query", "General biomedical health query")
        sources = payload.get("sources", ["PubMed", "Examine.com", "UpToDate", "OpenFoodFacts"])

        swarm = SwarmResearcher(llm=self._llm, memory=self._memory, registry=self._registry)
        briefing = await swarm.run_swarm(query=query, domain="biomedical", sources=sources)

        return {
            "agent": self.AGENT_ID,
            "action": "swarm_research",
            "medical_briefing": briefing,
        }
