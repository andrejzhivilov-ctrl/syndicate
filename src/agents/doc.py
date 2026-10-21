"""
Doc Agent — Clinical Health, Biomarkers, and Medical Intelligence Specialist.
v5.0 Verified (Domain Separation):
- Doc is strictly a medical agent (biomarkers, screening calendar, pre-visit dossiers, clinical HRV, emergency medical card).
- Training protocols, workouts, sports nutrition (Mifflin-St Jeor), recipes, and shopping lists are delegated to TrainerAgent ('trainer').
- Zero fabricated emergency medical data (strict safety rule: never invent blood type/allergies).
- Uses `await self._llm.ainvoke([HumanMessage(content=...)])` instead of synchronous `.generate()`.
- Matches `MemoryManager.save_episode(session_id=..., agent_id=..., role=..., content=..., metadata=...)`.
"""

from __future__ import annotations

import json
from contextvars import ContextVar
from datetime import date
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

logger = structlog.get_logger(__name__)


def _opt_float(payload: Dict[str, Any], key: str) -> Optional[float]:
    """Read a metric, keeping absence as ``None``.

    Substituting a plausible default (HRV 50 ms, weight 80 kg, …) turned
    "never measured" into a confident score with a colour zone, which then
    propagated into the morning briefing. Absence must stay visible, so a
    missing or non-numeric value is returned as ``None`` for the caller to
    report as ``unavailable``.
    """
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


class DocAgent:
    """
    Medical intelligence and clinical health agent (Doc).
    Handles physiological data, clinical readiness, biomarkers, preventive screening,
    pre-visit dossiers, and emergency medical records.
    Training, workout plans, and sports nutrition are delegated to TrainerAgent ('trainer').
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
        self._memory_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
            f"doc_memory_context_{id(self)}", default=None
        )
        # Dispatch table (was a 13-branch if/elif chain that grew a new branch
        # every time an action was added, and whose final ``else`` silently
        # returned a string instead of a result dict).
        self._ACTION_MAP: Dict[str, Any] = {
            "summarize": self._summarize,
            "extract": self._extract,
            "morning_readiness": self._morning_readiness,
            "training_protocol": self._training_protocol,
            "nutrition_plan": self._nutrition_plan,
            "shopping_list": self._shopping_list,
            "biomarker_trend": self._biomarker_trend,
            "screening_calendar": self._screening_calendar,
            "emergency_card": self._emergency_card,
            "pre_visit_dossier": self._pre_visit_dossier,
            "compliance_check": self._compliance_check,
            "nervous_system": self._nervous_system,
            "morning_data": self._morning_data,
            "swarm_research": self._swarm_research,
            "deep_medical_research": self._swarm_research,
        }

    async def _shopping_list(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Delegated to TrainerAgent: Doc is strictly medical."""
        from src.agents.trainer import TrainerAgent

        trainer = TrainerAgent(memory=self._memory, llm=self._llm, config=self._config, registry=self._registry)
        res = await trainer.execute({**payload, "action": "shopping_list"})
        res["delegated_by"] = self.AGENT_ID
        return res

    async def _llm_ask(self, prompt: str, fallback: str) -> str:
        """Invoke the LLM with bounded memory, treating prior health data as historical."""
        if not self._llm:
            return fallback
        prompt = append_memory_context(
            prompt,
            self._memory_context.get() or {},
            instruction=(
                "Remembered medical measurements, medications, or symptoms are historical "
                "only. Do not present them as current; use current payload measurements "
                "for present-tense recommendations."
            ),
        )
        try:
            resp = await self._llm.ainvoke([HumanMessage(content=prompt)])
            return str(getattr(resp, "content", resp))
        except Exception as exc:  # noqa: BLE001
            logger.warning("doc_llm_ainvoke_failed", error=str(exc))
            return fallback

    async def _save(self, payload: Dict[str, Any], category: str, data: Dict[str, Any], extra_meta: Optional[Dict[str, Any]] = None) -> None:
        """Persist a compact episode with PII redaction and non-blocking failure."""
        meta = {"category": category}
        if extra_meta:
            meta.update(extra_meta)
        await save_agent_episode(
            self._memory,
            agent_id=self.AGENT_ID,
            session_id=memory_session_id(payload, "doc-default-session"),
            action=category,
            role="assistant",
            content=json.dumps(data, ensure_ascii=False, default=str)[:8000],
            metadata=meta,
        )

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action based on payload."""
        action = payload.get("action", "summarize")
        try:
            handler = self._ACTION_MAP.get(action)
            if handler is None:
                logger.warning("Unknown action in DocAgent", action=action)
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}",
                    "agent": self.AGENT_ID,
                    "available_actions": sorted(self._ACTION_MAP),
                }
            session_id = memory_session_id(payload, "doc-default-session")
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

    def _unavailable(self, category: str, warning: str) -> Dict[str, Any]:
        """Structured absence (AGENTS.md §1) for a measurement never read."""
        return {
            "agent": self.AGENT_ID,
            "category": category,
            "status": "unavailable",
            "value": None,
            "warning": warning,
        }

    # Readiness is a weighted composite. Weights are renormalised over the
    # metrics actually supplied, so a partial morning is scored on what was
    # measured and nothing else.
    _READINESS_FIELDS: Dict[str, str] = {
        "hrv": "hrv_ms",
        "sleep_duration": "sleep_hours",
        "sleep_quality": "sleep_quality",
        "resting_hr": "resting_hr",
        "steps": "steps_yesterday",
        "stress": "stress_score",
    }
    _READINESS_WEIGHTS: Dict[str, float] = {
        "hrv": 0.30,
        "sleep_duration": 0.25,
        "sleep_quality": 0.15,
        "resting_hr": 0.15,
        "steps": 0.10,
        "stress": 0.05,
    }

    @staticmethod
    def _score_hrv(value: float) -> float:
        return min(100.0, max(0.0, (value / 50.0) * 75.0))

    @staticmethod
    def _score_sleep_duration(hours: float) -> float:
        if 7.0 <= hours <= 9.0:
            return 100.0
        if hours < 7.0:
            return max(0.0, (hours / 7.0) * 100.0)
        return max(0.0, 100.0 - (hours - 9.0) * 15.0)

    @staticmethod
    def _score_sleep_quality(value: float) -> float:
        return min(100.0, max(0.0, value))

    @staticmethod
    def _score_resting_hr(value: float) -> float:
        return min(100.0, max(0.0, 100.0 - (value - 55.0) * 2.5))

    @staticmethod
    def _score_steps(value: float) -> float:
        return min(100.0, max(0.0, (value / 8000.0) * 85.0))

    @staticmethod
    def _score_stress(value: float) -> float:
        return min(100.0, max(0.0, 100.0 - value))

    def _readiness_metrics(self, payload: Dict[str, Any]) -> "tuple[Dict[str, Any], Dict[str, float], List[str]]":
        """Read each metric; a missing one is reported, never substituted."""
        readings: Dict[str, Any] = {
            "hrv": _opt_float(payload, "hrv_ms"),
            "sleep_duration": _opt_float(payload, "sleep_hours"),
            "sleep_quality": _opt_float(payload, "sleep_quality"),
            "resting_hr": _opt_float(payload, "resting_hr"),
            "steps": _opt_int(payload, "steps_yesterday"),
            "stress": _opt_float(payload, "stress_score"),
        }
        scorers = {
            "hrv": self._score_hrv,
            "sleep_duration": self._score_sleep_duration,
            "sleep_quality": self._score_sleep_quality,
            "resting_hr": self._score_resting_hr,
            "steps": self._score_steps,
            "stress": self._score_stress,
        }
        component = {
            name: scorers[name](value) for name, value in readings.items() if value is not None
        }
        missing = sorted(
            self._READINESS_FIELDS[name] for name, value in readings.items() if value is None
        )
        return readings, component, missing

    @staticmethod
    def _readiness_warnings(
        readings: Dict[str, Any], missing: List[str]
    ) -> List[str]:
        warnings: List[str] = []
        if missing:
            warnings.append(f"Partial data — missing: {', '.join(missing)}")
        if readings["hrv"] is not None and readings["hrv"] < 35:
            warnings.append("Low HRV detected: sympathetic nervous system dominance")
        if readings["sleep_duration"] is not None and readings["sleep_duration"] < 6.0:
            warnings.append("Significant sleep debt (< 6h)")
        if readings["resting_hr"] is not None and readings["resting_hr"] > 75:
            warnings.append("Elevated resting heart rate")
        return warnings

    @staticmethod
    def _readiness_zone(score: float) -> "tuple[str, str, bool]":
        if score < 45:
            return "red", "rest", True
        if score < 70:
            return "yellow", "light" if score < 55 else "moderate", False
        return "green", "intense", False

    async def _morning_readiness(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Every metric is optional at the boundary and absent stays None: a
        # fabricated hrv_ms/sleep pair used to produce a score and a "green"
        # zone out of data nobody supplied.
        readings, component, missing = self._readiness_metrics(payload)

        # The two core drivers: without either of them there is no readiness
        # worth reporting, so report absence instead of a number.
        if readings["hrv"] is None and readings["sleep_duration"] is None:
            result = {
                **self._unavailable(
                    "morning_readiness",
                    "no HRV and no sleep data supplied — readiness not computed "
                    f"(missing: {', '.join(missing)})",
                ),
                "score": None,
                "zone": None,
                "recommended_intensity": None,
                "deload_suggested": None,
                "warnings": [],
                "missing_inputs": missing,
                "partial": True,
            }
            await self._save(payload, "morning_readiness", result)
            return result

        active = {name: self._READINESS_WEIGHTS[name] for name in component}
        total_weight = sum(active.values())
        score = round(
            sum(component[name] * weight for name, weight in active.items()) / total_weight, 1
        )
        zone, intensity, deload = self._readiness_zone(score)

        result = {
            "agent": self.AGENT_ID,
            "status": "ok",
            "score": score,
            "zone": zone,
            "recommended_intensity": intensity,
            "warnings": self._readiness_warnings(readings, missing),
            "deload_suggested": deload,
            "missing_inputs": missing,
            "partial": bool(missing),
            "inputs_used": sorted(component),
        }
        await self._save(payload, "morning_readiness", result, {"score": score, "zone": zone})
        return result

    async def _training_protocol(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Delegated to TrainerAgent: Doc is strictly medical."""
        from src.agents.trainer import TrainerAgent

        trainer = TrainerAgent(memory=self._memory, llm=self._llm, config=self._config, registry=self._registry)
        res = await trainer.execute({**payload, "action": "training_protocol"})
        res["delegated_by"] = self.AGENT_ID
        return res

    async def _nutrition_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Delegated to TrainerAgent: Doc is strictly medical."""
        from src.agents.trainer import TrainerAgent

        trainer = TrainerAgent(memory=self._memory, llm=self._llm, config=self._config, registry=self._registry)
        res = await trainer.execute({**payload, "action": "nutrition_plan"})
        res["delegated_by"] = self.AGENT_ID
        return res

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
        # Age drives the colonoscopy recommendation (≥45). Assuming 35 hid a
        # screening that an older operator should be offered.
        age = _opt_int(payload, "age")
        last_checkups = payload.get("last_checkups", {})

        annual = ["blood_pressure", "dental", "vision", "comprehensive_blood_panel"]
        today = date.today()
        # NOTE: the previous implementation had these two lists swapped — items
        # that were never done were reported as "overdue" under that name while
        # completed ones were called "upcoming". A screening that has no entry in
        # ``last_checkups`` is simply *due*; only a screening whose recorded date
        # has passed its interval is genuinely overdue.
        completed = [t for t in annual if t in last_checkups]
        due = [t for t in annual if t not in last_checkups]

        overdue: List[str] = []
        for name, last_done in last_checkups.items():
            try:
                last_dt = date.fromisoformat(str(last_done))
            except (TypeError, ValueError):
                continue
            if (today - last_dt).days > 365:
                overdue.append(name)

        warnings: List[str] = []
        if age is None:
            warnings.append("age not supplied — age-dependent screening (colonoscopy ≥45) not evaluated")
        elif age >= 45 and "colonoscopy" not in last_checkups:
            due.append("colonoscopy")

        result = {
            "agent": self.AGENT_ID,
            "status": "ok",
            "age": age,
            "completed": completed,
            "due": due,
            "overdue": overdue,
            "warnings": warnings,
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
        # Previously hrv_ms defaulted to 45 and stress_score to 60, so an empty
        # payload "measured" a stressed operator and prescribed the sigh.
        hrv_ms = _opt_float(payload, "hrv_ms")
        stress_score = _opt_float(payload, "stress_score")

        warnings: List[str] = []
        if stress_score is not None:
            technique = (
                "Physiological Sigh (double inhale + long exhale)"
                if stress_score >= 60
                else "Box Breathing (4-4-4-4)"
            )
            personalised = True
        elif hrv_ms is not None:
            # Low HRV indicates sympathetic dominance — the sigh downshifts faster.
            technique = (
                "Physiological Sigh (double inhale + long exhale)"
                if hrv_ms < 35
                else "Box Breathing (4-4-4-4)"
            )
            personalised = True
        else:
            technique = "Box Breathing (4-4-4-4)"
            personalised = False
            warnings.append(
                "no hrv_ms / stress_score supplied — generic protocol, not personalised "
                "(no metrics were measured)"
            )

        result = {
            "agent": self.AGENT_ID,
            "status": "ok",
            "breathing_exercise": technique,
            "personalised": personalised,
            "inputs": {"hrv_ms": hrv_ms, "stress_score": stress_score},
            "duration_min": 5,
            "sleep_hygiene_tips": [
                "Zero blue light 60 min prior to sleep",
                "Room temperature 18-19°C",
                "Magnesium glycinate 400mg before bed",
            ],
            "grounding_exercise": "5-4-3-2-1 sensory grounding protocol",
            "warnings": warnings,
        }
        await self._save(payload, "nervous_system", result, {"hrv": hrv_ms, "stress": stress_score})
        return result

    async def _morning_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        readiness = await self._morning_readiness(payload)
        result = {
            "agent": self.AGENT_ID,
            "status": readiness["status"],
            "readiness_score": readiness["score"],
            "zone": readiness["zone"],
            "recommended_intensity": readiness["recommended_intensity"],
            "water_target_ml": self._config.get("water_target_ml", 2500),
            "warnings": readiness["warnings"],
            "missing_inputs": readiness.get("missing_inputs", []),
            "partial": readiness.get("partial", False),
        }
        if readiness["status"] != "ok":
            result["warning"] = readiness["warning"]
        await self._save(payload, "morning_data", result)
        return result

    async def _swarm_research(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Deep medical / pharmacology research via Swarm (Scout, Extractor, Critic)."""
        from src.swarm import SwarmResearcher

        query = payload.get("query", "General biomedical health query")
        sources = payload.get("sources", ["PubMed", "Examine.com", "UpToDate", "OpenFoodFacts"])

        swarm = SwarmResearcher(llm=self._llm, memory=self._memory, registry=self._registry)
        briefing = await swarm.run_swarm(query=query, domain="biomedical", sources=sources)
        result = {
            "agent": self.AGENT_ID,
            "action": "swarm_research",
            "medical_briefing": briefing,
        }
        await self._save(payload, "swarm_research", {
            "query": str(query)[:500],
            "medical_briefing": briefing,
        })
        return result
