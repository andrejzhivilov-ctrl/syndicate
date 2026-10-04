"""
Eva Agent — Chief Executive Officer (CEO) & Supreme Coordinator of EVA SYNDICATE.
Floor 10 Command Specialist.

Coordinates executive strategy, delegating tasks to:
- Fin (CFO - Floor 10)
- Marshal (CSO / Supreme Security Commander - Floor 10)
- Architect (CTO - Floor 10)
- Sam (CIO/Quant - Floor 7)
- Kira (Academy Head - Floor 8)
- Doc (Health Officer - Floor 9)
Integrates EvaCurator for life review, decision loop, deadlines, and social pulse.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
import structlog
from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.eva_curator import EvaCurator
from src.floors import active_floors, reserved_floors

logger = structlog.get_logger(__name__)

EVA_SYSTEM_PROMPT = """Ти — Єва (Eva), верховний координатор та CEO екосистеми EVA SYNDICATE.
Твоя мета — забезпечувати максимальну продуктивність, безпеку та стратегічну ясність оператора.
Ти координуєш 10 поверхів Синдикату:
- Поверх 1: Сервер та n8n (Сенсорний шлюз, черга помилок DLQ, крон)
- Поверх 2: Фабрика контенту (Контент-завод, Humanizer, Google Veo 3 / Kling AI, POD мерч)
- Поверхи 3–6: Reserved Floors (Конституційний системний резерв)
- Поверх 7: Сем (Квант, Confluence Engine, ліквідність, строгий HITL ризик-гейт)
- Поверх 8: Кіра (SYNDICATE Academy, Сократівський тьютор 4 етапів)
- Поверх 9: Док (Health & Energy, готовність HRV, Mifflin-St Jeor TDEE, відновлення)
- Поверх 10: Командування (Єва CEO, Фін CFO, Маршал CSO - Безпека, Архітектор CTO, Sentinel Protocol, LLM Рада, Орк Верифікатор, Markdown Vault).

Спілкуйся ділово, впевнено, структуровано та українською мовою.
"""


class EvaAgent:
    """
    Chief Executive Officer (CEO) and Supreme Coordinator agent for EVA SYNDICATE.
    """
    AGENT_ID = "eva"

    def __init__(
        self,
        memory: Any,
        llm: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[Any] = None,
        curator: Optional[EvaCurator] = None,
    ) -> None:
        self._memory = memory
        self._llm = llm
        self._config = dict(config or {})
        self._registry = registry
        self._curator = curator or EvaCurator(memory=memory, llm=llm, config=config, registry=registry)

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch executive action."""
        action = payload.get("action", "chat")
        logger.info("eva_action_dispatched", action=action)

        try:
            if action in ("chat", "conversation", "message"):
                return await self._chat(payload)
            elif action in ("compose_briefing", "morning_briefing"):
                return await self._compose_briefing(payload)
            elif action in ("compose_reflection", "evening_reflection"):
                return await self._compose_reflection(payload)
            elif action == "delegate":
                return await self._delegate_intent(payload)
            elif action == "system_status":
                return await self._system_status()
            elif action in (
                "weekly_review",
                "record_decision",
                "review_decisions",
                "deadline_check",
                "add_deadline",
                "social_pulse",
                "add_contact",
                "morning_data",
            ):
                # Delegate life curation actions to EvaCurator
                return await self._curator.execute(payload)
            else:
                # Default conversation handling for unknown actions
                return await self._chat(payload)
        except Exception as exc:  # noqa: BLE001
            logger.exception("EvaAgent execution error", action=action, exc_info=exc)
            return {"error": str(exc), "agent": self.AGENT_ID, "action": action}

    async def _chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle executive conversation with user."""
        user_message = payload.get("message") or payload.get("text") or str(payload)

        if not self._llm:
            return {
                "agent": self.AGENT_ID,
                "response": "Єва на зв'язку. Всі системи Синдикату активні та готові до виконання завдань.",
                "status": "ok",
                "mode": "deterministic",
            }

        messages = [
            SystemMessage(content=EVA_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]
        resp = await self._llm.ainvoke(messages)
        content = getattr(resp, "content", str(resp))

        # Save episode to memory if available
        if self._memory and hasattr(self._memory, "save_episode"):
            try:
                await self._memory.save_episode(
                    session_id=payload.get("session_id", "eva_executive_chat"),
                    agent_id=self.AGENT_ID,
                    role="assistant",
                    content=content,
                    metadata={"action": "chat"},
                )
            except Exception as e:
                logger.warning("eva_memory_save_failed", error=str(e))

        return {
            "agent": self.AGENT_ID,
            "response": content,
            "status": "completed",
        }

    async def _compose_briefing(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize reports from Doc, Fin, Marshal, Kira, Sam, Architect
        into a morning briefing (07:30).
        """
        agent_data = payload.get("agent_data", {})
        doc_data = agent_data.get("doc", {})
        fin_data = agent_data.get("fin", {})
        marshal_data = agent_data.get("marshal", {})
        kira_data = agent_data.get("kira", {})

        # Deterministic summary base
        readiness = doc_data.get("readiness_score", 85)
        zone = doc_data.get("zone", "green")
        runway = fin_data.get("runway_months", 12.0)

        prompt = (
            f"Сформуй ранковий бриф (07:30) для оператора Синдикату на основі зібраних даних:\n"
            f"- Здоров'я (Док): готовність {readiness}/100 (зона {zone})\n"
            f"- Фінанси (Фін): грошовий ранвей {runway} міс.\n"
            f"- Операції (Маршал): статус фабрики контенту: {marshal_data.get('status', 'активно')}\n"
            f"- Академія (Кіра): навчальний фокус: {kira_data.get('focus', 'системна інженерія')}\n\n"
            f"Формат: чітко, структуровано, по-діловому, до 150 слів. Додай коротке мотиваційне напуття."
        )

        if self._llm:
            try:
                resp = await self._llm.ainvoke([SystemMessage(content=EVA_SYSTEM_PROMPT), HumanMessage(content=prompt)])
                summary_text = getattr(resp, "content", str(resp))
            except Exception as exc:  # noqa: BLE001
                logger.warning("eva_briefing_llm_failed", error=str(exc))
                summary_text = (
                    f"Доброго ранку, операторе! Готовність організму: {readiness}/100 ({zone}). "
                    f"Фінансовий резерв: {runway} міс. Всі 10 поверхів Синдикату у штатному режимі."
                )
        else:
            summary_text = (
                f"Доброго ранку, операторе! Готовність організму: {readiness}/100 ({zone}). "
                f"Фінансовий резерв: {runway} міс. Всі 10 поверхів Синдикату у штатному режимі."
            )

        return {
            "agent": self.AGENT_ID,
            "response": summary_text,
            "briefing": summary_text,
            "agent_data": agent_data,
            "readiness_score": readiness,
            "runway_months": runway,
            "status": "completed",
        }

    async def _compose_reflection(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize evening reflection (21:00) with Doc energy review and Kira quiz.
        """
        evening_data = payload.get("evening_data", {})
        doc_data = evening_data.get("doc", {})
        kira_data = evening_data.get("kira", {})

        prompt = (
            f"Сформуй підсумкову вечірню рефлексію (21:00) для оператора:\n"
            f"- Відновлення та вегетативна система (Док): {doc_data}\n"
            f"- Мікро-квіз дня (Кіра): {kira_data.get('quiz', 'тест пройдено')}\n\n"
            f"Склади коротке, заспокійливе резюме дня, порадивши перехід до фази відпочинку."
        )

        if self._llm:
            try:
                resp = await self._llm.ainvoke([SystemMessage(content=EVA_SYSTEM_PROMPT), HumanMessage(content=prompt)])
                reflection_text = getattr(resp, "content", str(resp))
            except Exception as exc:  # noqa: BLE001
                logger.warning("eva_reflection_llm_failed", error=str(exc))
                reflection_text = "Вечірня рефлексія: день успішно завершено. Рекомендовано знизити екранний час та перейти до сну."
        else:
            reflection_text = "Вечірня рефлексія: день успішно завершено. Рекомендовано знизити екранний час та перейти до сну."

        return {
            "agent": self.AGENT_ID,
            "response": reflection_text,
            "reflection": reflection_text,
            "evening_data": evening_data,
            "status": "completed",
        }

    async def _delegate_intent(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse user request intent and recommend/route to target agent.
        """
        query = (payload.get("query") or payload.get("message") or "").lower()
        target = "eva"
        reason = "Загальна координація"

        if any(w in query for w in ["гроші", "бюджет", "витрати", "банк", "податки", "ранвей", "fin"]):
            target = "fin"
            reason = "Фінансові операції та бюджетний контроль (Фін CFO)"
        elif any(w in query for w in ["безпека", "захист", "атака", "злам", "інцидент", "маршал", "sentinel", "security"]):
            target = "marshal"
            reason = "Аудит безпеки, відбиття загроз та нагляд Sentinel Protocol (Маршал CSO)"
        elif any(w in query for w in ["контент", "відео", "тікток", "мерч", "pod", "реліз"]):
            target = "floor2"
            reason = "Операції Фабрики контенту (Поверх 2)"
        elif any(w in query for w in ["код", "архітектура", "репозиторій", "помилка", "компілятор", "архітектор"]):
            target = "architect"
            reason = "Технічний аналіз коду та архітектури (Архітектор CTO)"
        elif any(w in query for w in ["здоров'я", "пульс", "сон", "харчування", "стрес", "тренування", "док"]):
            target = "doc"
            reason = "Медичний контроль та оптимізація енергії (Док Health Officer)"
        elif any(w in query for w in ["навчання", "курс", "знання", "підказка", "урок", "кіра"]):
            target = "kira"
            reason = "Сократівське навчання в SYNDICATE Academy (Кіра)"
        elif any(w in query for w in ["трейдинг", "біржа", "крипта", "btc", "сигнал", "сем"]):
            target = "sam"
            reason = "Кількісний аналіз капіталу (Сем Quant CIO)"

        return {
            "agent": self.AGENT_ID,
            "target_agent": target,
            "reason": reason,
            "query": query,
            "status": "routed",
        }

    async def _system_status(self) -> Dict[str, Any]:
        """Provide holistic status of all 10 floors of EVA SYNDICATE."""
        return {
            "agent": self.AGENT_ID,
            "ecosystem": "EVA SYNDICATE",
            "version": "4.2.0-PROD",
            "active_floors": active_floors(),
            "reserved_floors": reserved_floors(),
            "status": "operational",
            "governance": "Constitutional SSOT in Git",
            "security": "Zero-Trust Sentinel with Outbound Veto active",
        }
