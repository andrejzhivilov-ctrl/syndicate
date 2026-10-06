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

from typing import Any, Dict, Optional
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
    DEFAULT_SESSION_ID = "eva_executive_chat"
    # Recall budget: 20 episodes / ~4000 characters ≈ 1000 tokens, which is the
    # token-economy answer to "remember everything without re-reading dialogue".
    MEMORY_CONTEXT_LIMIT = 20
    MEMORY_CONTEXT_CHARS = 4000

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
        """Handle executive conversation with user.

        Recalls recent episodes **before** answering. Eva used to write every
        turn with ``save_episode`` and never read anything back, so each
        conversation started from zero while the stored episodes cost tokens and
        storage for nothing. See ``MemoryManager.build_memory_context``.
        """
        user_message = payload.get("message") or payload.get("text") or str(payload)
        session_id = payload.get("session_id") or self.DEFAULT_SESSION_ID

        if not self._llm:
            return {
                "agent": self.AGENT_ID,
                "response": "Єва на зв'язку. Всі системи Синдикату активні та готові до виконання завдань.",
                "status": "ok",
                "mode": "deterministic",
            }

        memory = await self._recall(payload, session_id, query_text=user_message)
        system_prompt = EVA_SYSTEM_PROMPT
        if memory["text"]:
            system_prompt = f"{EVA_SYSTEM_PROMPT}\n\n{memory['text']}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]
        resp = await self._llm.ainvoke(messages)
        content = getattr(resp, "content", str(resp))

        await self._remember(session_id, "user", user_message, {"action": "chat"})
        await self._remember(session_id, "assistant", content, {"action": "chat"})

        return {
            "agent": self.AGENT_ID,
            "response": content,
            "status": "completed",
            "memory": {
                "status": memory["status"],
                "episodes_used": memory["episodes_used"],
                "episodes_available": memory["episodes_available"],
                "truncated": memory["truncated"],
                "warning": memory["warning"],
                # Whether the vector half contributed, and why not if it did not.
                "semantic": memory.get("semantic"),
            },
        }

    async def _recall(
        self, payload: Dict[str, Any], session_id: str, query_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Read this session's recent episodes. Never raises, never invents data.

        Returns the ``build_memory_context`` contract; a missing or broken
        backend yields ``status="unavailable"`` so the caller can pass the truth
        on instead of claiming it remembered something.
        """
        unavailable: Dict[str, Any] = {
            "status": "unavailable",
            "text": "",
            "episodes_used": 0,
            "episodes_available": 0,
            "truncated": False,
            "warning": None,
            "semantic": {"status": "unavailable", "warning": None},
        }
        if not self._memory or not hasattr(self._memory, "build_memory_context"):
            return {**unavailable, "warning": "memory backend does not expose build_memory_context"}

        try:
            block = await self._memory.build_memory_context(
                agent_id=self.AGENT_ID,
                session_id=session_id,
                # The current question drives semantic recall, so episodes that
                # fell out of the recent slice can still be found.
                query_embedding=payload.get("query_embedding"),
                query_text=query_text,
                limit=int(self._config.get("memory_context_limit", self.MEMORY_CONTEXT_LIMIT)),
                max_chars=int(self._config.get("memory_context_chars", self.MEMORY_CONTEXT_CHARS)),
            )
        except Exception as exc:  # noqa: BLE001
            # An agent must answer even when its memory is unreachable — but it
            # must say so rather than silently answer without context.
            logger.warning("eva_memory_recall_failed", error=str(exc))
            return {**unavailable, "warning": f"memory read failed: {exc}"}

        return {**unavailable, **dict(block or {})}

    async def _remember(self, session_id: str, role: str, content: str, metadata: Dict[str, Any]) -> None:
        """Persist one turn of the conversation; a memory failure is not fatal."""
        if not self._memory or not hasattr(self._memory, "save_episode"):
            return
        try:
            await self._memory.save_episode(
                session_id=session_id,
                agent_id=self.AGENT_ID,
                role=role,
                content=content,
                metadata=dict(metadata),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("eva_memory_save_failed", role=role, error=str(exc))

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

        # Deterministic summary base. No defaults: absent metrics used to become
        # "readiness 85/100, zone green, runway 12 months" in a briefing the
        # operator reads as measured fact (AGENTS.md §1 — never fabricate).
        readiness = doc_data.get("readiness_score")
        zone = doc_data.get("zone")
        runway = fin_data.get("runway_months")
        marshal_status = marshal_data.get("status")
        kira_focus = kira_data.get("focus")

        missing = [
            name
            for name, value in (
                ("doc.readiness_score", readiness),
                ("fin.runway_months", runway),
                ("marshal.status", marshal_status),
                ("kira.focus", kira_focus),
            )
            if value is None
        ]
        warnings = (
            ["missing inputs: " + ", ".join(missing) + " — reported as unavailable, not estimated"]
            if missing
            else []
        )

        health_line = (
            f"готовність {readiness}/100 (зона {zone if zone is not None else 'невідома'})"
            if readiness is not None
            else "дані про готовність відсутні"
        )
        finance_line = f"грошовий ранвей {runway} міс." if runway is not None else "дані про ранвей відсутні"
        ops_line = f"статус фабрики контенту: {marshal_status}" if marshal_status else "статус операцій невідомий"
        academy_line = f"навчальний фокус: {kira_focus}" if kira_focus else "навчальний фокус не задано"

        prompt = (
            f"Сформуй ранковий бриф (07:30) для оператора Синдикату на основі зібраних даних:\n"
            f"- Здоров'я (Док): {health_line}\n"
            f"- Фінанси (Фін): {finance_line}\n"
            f"- Операції (Маршал): {ops_line}\n"
            f"- Академія (Кіра): {academy_line}\n\n"
            f"Якщо показник відсутній — так і напиши («дані відсутні»), не вигадуй чисел.\n"
            f"Формат: чітко, структуровано, по-діловому, до 150 слів. Додай коротке мотиваційне напуття."
        )

        fallback_text = (
            "Доброго ранку, операторе! "
            f"Здоров'я: {health_line}. Фінанси: {finance_line}. "
            f"Операції: {ops_line}. Академія: {academy_line}."
        )

        if self._llm:
            try:
                resp = await self._llm.ainvoke([SystemMessage(content=EVA_SYSTEM_PROMPT), HumanMessage(content=prompt)])
                summary_text = getattr(resp, "content", str(resp))
            except Exception as exc:  # noqa: BLE001
                logger.warning("eva_briefing_llm_failed", error=str(exc))
                summary_text = fallback_text
        else:
            summary_text = fallback_text

        return {
            "agent": self.AGENT_ID,
            # Every source missing means the briefing itself has nothing to
            # report, so its status is unavailable rather than a cheerful "ok".
            "status": "unavailable" if len(missing) == 4 else "completed",
            "response": summary_text,
            "briefing": summary_text,
            "agent_data": agent_data,
            "readiness_score": readiness,
            "runway_months": runway,
            "missing_inputs": missing,
            "warnings": warnings,
        }

    async def _compose_reflection(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize evening reflection (21:00) with Doc energy review and Kira quiz.
        """
        evening_data = payload.get("evening_data", {})
        doc_data = evening_data.get("doc", {})
        kira_data = evening_data.get("kira", {})

        # A canned "the day went well" belongs to nobody's data. If neither Doc
        # nor Kira reported anything, say so instead of inventing a good day.
        missing = [name for name, value in (("doc", doc_data), ("kira", kira_data)) if not value]
        warnings = (
            ["missing inputs: " + ", ".join(missing) + " — reflection reports absence, not a verdict"]
            if missing
            else []
        )

        prompt = (
            f"Сформуй підсумкову вечірню рефлексію (21:00) для оператора:\n"
            f"- Відновлення та вегетативна система (Док): {doc_data if doc_data else 'дані відсутні'}\n"
            f"- Мікро-квіз дня (Кіра): {kira_data.get('quiz', 'тест пройдено') if kira_data else 'дані відсутні'}\n\n"
            f"Якщо даних немає — прямо скажи, що їх немає, і не оцінюй день.\n"
            f"Склади коротке, заспокійливе резюме дня, порадивши перехід до фази відпочинку."
        )

        if missing:
            fallback_text = (
                "Вечірня рефлексія: даних про відновлення та навчання за сьогодні немає "
                f"(немає: {', '.join(missing)}). Рекомендовано знизити екранний час і перейти до сну."
            )
        else:
            fallback_text = (
                "Вечірня рефлексія: день завершено за наявними даними. "
                "Рекомендовано знизити екранний час та перейти до сну."
            )

        if self._llm:
            try:
                resp = await self._llm.ainvoke([SystemMessage(content=EVA_SYSTEM_PROMPT), HumanMessage(content=prompt)])
                reflection_text = getattr(resp, "content", str(resp))
            except Exception as exc:  # noqa: BLE001
                logger.warning("eva_reflection_llm_failed", error=str(exc))
                reflection_text = fallback_text
        else:
            reflection_text = fallback_text

        return {
            "agent": self.AGENT_ID,
            "status": "unavailable" if len(missing) == 2 else "completed",
            "response": reflection_text,
            "reflection": reflection_text,
            "evening_data": evening_data,
            "missing_inputs": missing,
            "warnings": warnings,
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
