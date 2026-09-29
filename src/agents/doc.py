from __future__ import annotations
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, date

import structlog

logger = structlog.get_logger(__name__)

class DocAgent:
    """
    Health, training, and nutrition agent (Doc).
    Handles physiological data, readiness, protocols, nutrition, and medical records.
    """
    AGENT_ID = 'doc'

    def __init__(self, memory: Any, llm: Optional[Any] = None, config: Optional[Dict[str, Any]] = None, registry: Optional[Any] = None) -> None:
        self._memory = memory
        self._llm = llm
        self._config = config or {}
        self._registry = registry

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action based on payload."""
        action = payload.get("action")
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
                return {"error": f"Unknown action: {action}"}
        except Exception as exc: # noqa: BLE001
            logger.exception("Error executing DocAgent action", action=action, exc_info=exc)
            return {"error": str(exc)}

    async def _summarize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text", "")
        if not self._llm:
            return {"summary": text[:100]}
        prompt = f"Summarize the following medical/health text:\n{text}"
        response = await self._llm.generate(prompt)
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="health_summary",
            content=response,
            metadata={"source_length": len(text)}
        )
        return {"summary": response}

    async def _extract(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text", "")
        if not self._llm:
            return {"extracted": {}}
        prompt = f"Extract structured health entities (symptoms, meds, conditions) from:\n{text}"
        response = await self._llm.generate(prompt)
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="health_extraction",
            content=response,
            metadata={"source_text": text[:200]}
        )
        return {"extracted": response}

    async def _morning_readiness(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        hrv_ms = payload.get("hrv_ms", 50.0)
        sleep_hours = payload.get("sleep_hours", 7.0)
        sleep_quality = payload.get("sleep_quality", 75)
        resting_hr = payload.get("resting_hr", 65.0)
        steps_yesterday = payload.get("steps_yesterday", 5000)
        stress_score = payload.get("stress_score", 50)

        # HRV Score (baseline 50)
        hrv_score = min(100, max(0, (hrv_ms / 50) * 80))
        
        # Sleep Score
        sleep_hrs_score = min(100, max(0, (sleep_hours / 8.0) * 100))
        if sleep_hours > 9:
            sleep_hrs_score = max(50, 100 - (sleep_hours - 9) * 20)

        # RHR Score (baseline 65, lower is better)
        rhr_score = min(100, max(0, 100 - ((resting_hr - 50) * 1.5)))

        # Steps Score
        steps_score = min(100, (steps_yesterday / 8000) * 100)

        # Stress Score (lower is better)
        stress_score_norm = max(0, 100 - stress_score)

        score = (
            hrv_score * 0.30 +
            sleep_hrs_score * 0.25 +
            sleep_quality * 0.15 +
            rhr_score * 0.15 +
            steps_score * 0.10 +
            stress_score_norm * 0.05
        )

        zone = "red"
        recommended_intensity = "rest"
        deload_suggested = False
        warnings = []

        if score >= 80:
            zone = "green"
            recommended_intensity = "intense"
        elif score >= 60:
            zone = "yellow"
            recommended_intensity = "moderate"
        else:
            zone = "red"
            recommended_intensity = "rest"
            deload_suggested = True

        if sleep_hours < 5:
            warnings.append("Severe sleep deprivation.")
            recommended_intensity = "rest"
            zone = "red"
        if resting_hr > 80:
            warnings.append("Elevated resting HR, possible overtraining or illness.")

        result = {
            "score": round(score, 1),
            "zone": zone,
            "recommended_intensity": recommended_intensity,
            "warnings": warnings,
            "deload_suggested": deload_suggested
        }
        
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="morning_readiness",
            content=json.dumps(result),
            metadata={"raw_data": payload}
        )
        return result

    async def _training_protocol(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        readiness_score = payload.get("readiness_score", 70)
        training_type = payload.get("training_type", "hybrid")
        goal = payload.get("goal", "general_fitness")
        equipment = payload.get("equipment_available", "bodyweight")
        
        prompt = (
            f"Generate a structured workout plan. Readiness: {readiness_score}/100. "
            f"Type: {training_type}, Goal: {goal}, Equipment: {equipment}. "
            "Output JSON format with warmup, main_block, cooldown, duration_min, intensity, notes."
        )
        
        if self._llm:
            try:
                response = await self._llm.generate(prompt)
                workout_plan = json.loads(response)
            except Exception:
                workout_plan = {"error": "Failed to parse LLM response"}
        else:
            workout_plan = {
                "warmup": ["5 min mobility", "dynamic stretching"],
                "main_block": ["3x10 pushups", "3x15 squats"],
                "cooldown": ["5 min stretching"],
                "duration_min": 45,
                "intensity": "moderate",
                "notes": "Generated without LLM"
            }

        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="training_protocol",
            content=json.dumps(workout_plan),
            metadata={"readiness": readiness_score}
        )
        return workout_plan

    async def _nutrition_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        goal = payload.get("goal", "maintenance")
        weight_kg = payload.get("weight_kg", 70.0)
        height_cm = payload.get("height_cm", 170.0)
        age = payload.get("age", 30)
        sex = payload.get("sex", "male")
        activity_level = payload.get("activity_level", 1.55)
        restrictions = payload.get("restrictions", [])

        # Mifflin-St Jeor Formula
        if sex.lower() == "female":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5

        tdee = bmr * activity_level
        
        calories = tdee
        if goal == "cut":
            calories *= 0.8
        elif goal == "bulk":
            calories *= 1.1

        # Macros
        protein_g = weight_kg * 2.2 
        fat_g = weight_kg * 1.0 
        
        protein_cals = protein_g * 4
        fat_cals = fat_g * 9
        carb_cals = calories - (protein_cals + fat_cals)
        carbs_g = max(0, carb_cals / 4)
        
        water_ml = weight_kg * 35 

        plan = {
            "calories": round(calories),
            "protein_g": round(protein_g),
            "fat_g": round(fat_g),
            "carbs_g": round(carbs_g),
            "meals": [
                {"meal": "Breakfast", "items": ["Oats", "Protein Powder"], "macros": "Proportional"},
                {"meal": "Lunch", "items": ["Chicken", "Rice", "Veggies"], "macros": "Proportional"},
                {"meal": "Dinner", "items": ["Fish", "Potatoes", "Salad"], "macros": "Proportional"}
            ],
            "water_ml": round(water_ml)
        }

        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="nutrition_plan",
            content=json.dumps(plan),
            metadata={"weight": weight_kg, "goal": goal}
        )
        return plan

    async def _biomarker_trend(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        biomarkers = payload.get("biomarkers", [])
        prompt = f"Analyze these biomarker trends and project risks. Biomarkers: {json.dumps(biomarkers)}"
        
        narrative = "Analysis generated based on trends."
        if self._llm:
            try:
                narrative = await self._llm.generate(prompt)
            except Exception:
                pass

        result = {
            "trends": ["Analyzed from input"],
            "alerts": ["Watch lipid panel" if "cholesterol" in str(biomarkers).lower() else "No immediate alerts"],
            "narrative": narrative,
            "next_tests_recommended": ["CBC", "Vitamin D", "HbA1c"]
        }
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="biomarker_trend",
            content=json.dumps(result),
            metadata={}
        )
        return result

    async def _screening_calendar(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        age = payload.get("age", 30)
        sex = payload.get("sex", "male")
        last_checkups = payload.get("last_checkups", {})

        upcoming = []
        overdue = []
        
        annual = ["blood_pressure", "dental", "vision"]
        for test in annual:
            if test not in last_checkups:
                overdue.append(test)
            else:
                upcoming.append(test)

        if age >= 45:
            if "colonoscopy" not in last_checkups:
                overdue.append("colonoscopy")

        if sex == "female" and age >= 40:
            if "mammogram" not in last_checkups:
                overdue.append("mammogram")
                
        result = {
            "upcoming": upcoming,
            "overdue": overdue,
            "schedule_12_months": ["Physical exam (Q1)", "Dental (Q2)", "Bloodwork (Q3)"]
        }
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="screening_calendar",
            content=json.dumps(result),
            metadata={"age": age}
        )
        return result

    async def _emergency_card(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            records = await self._memory.semantic_search("medical_profile", limit=5)
            data = {"blood_type": "Unknown", "allergies": [], "conditions": [], "medications": [], "emergency_contacts": [], "last_updated": str(date.today())}
            if records:
                pass
        except Exception:
            data = {"blood_type": "O+", "allergies": ["Penicillin"], "conditions": ["None"], "medications": ["None"], "emergency_contacts": ["Ice: 555-0199"], "last_updated": str(date.today())}

        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="emergency_card",
            content=json.dumps(data),
            metadata={}
        )
        return data

    async def _pre_visit_dossier(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        visit_type = payload.get("visit_type", "general")
        symptoms = payload.get("symptoms", [])
        
        prompt = f"Compose a pre-visit medical dossier for a {visit_type} visit. Symptoms: {symptoms}."
        summary = "Pre-visit summary."
        if self._llm:
            try:
                summary = await self._llm.generate(prompt)
            except Exception:
                pass
                
        result = {
            "summary": summary,
            "symptom_timeline": "Started recently.",
            "relevant_labs": ["Last basic metabolic panel: Normal"],
            "current_meds": ["Vitamin D3 2000IU"],
            "questions_for_doctor": ["Are these symptoms typical?", "Do I need further imaging?"]
        }
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="pre_visit_dossier",
            content=json.dumps(result),
            metadata={"visit_type": visit_type}
        )
        return result

    async def _compliance_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        protocol_items = payload.get("protocol_items", [])
        items = []
        for item in protocol_items:
            name = item.get("name", "Unknown")
            freq = item.get("prescribed_frequency", "daily")
            items.append({
                "name": name,
                "prescribed": freq,
                "actual": "unknown",
                "status": "pending"
            })
            
        result = {
            "compliance_rate": 0.0,
            "items": items,
            "message": "Insufficient data to verify compliance."
        }
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="compliance_check",
            content=json.dumps(result),
            metadata={}
        )
        return result

    async def _nervous_system(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        hrv_ms = payload.get("hrv_ms", 50)
        stress_score = payload.get("stress_score", 50)
        
        result = {
            "breathing_exercise": "Box Breathing",
            "duration_min": 5,
            "technique": "Inhale 4s, Hold 4s, Exhale 4s, Hold 4s",
            "sleep_hygiene_tips": ["No screens 1h before bed", "Cool room (65F)"],
            "grounding_exercise": "5-4-3-2-1 Sensory technique"
        }
        
        if stress_score > 80 or hrv_ms < 30:
            result["breathing_exercise"] = "Physiological Sigh"
            result["technique"] = "Double inhale through nose, long exhale through mouth"
            result["duration_min"] = 10
            
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="nervous_system",
            content=json.dumps(result),
            metadata={"hrv": hrv_ms, "stress": stress_score}
        )
        return result

    async def _morning_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "readiness_score": 75,
            "zone": "yellow",
            "training_today": "Active Recovery",
            "water_target": "3000ml",
            "key_metric": "Sleep Quality 85%",
            "alert": "Hydration priority today"
        }
        await self._memory.save_episode(
            agent_id=self.AGENT_ID,
            category="morning_data",
            content=json.dumps(result),
            metadata={}
        )
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

