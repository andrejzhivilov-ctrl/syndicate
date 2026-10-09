"""
Kira Agent — Academic Mentor, Intellectual Sparring Partner & SYNDICATE Academy Director.
Floor 8: Enlightenment, Academy & Mentorship.

Strict Domain Isolation:
Dedicated solely to education, cognitive elevation, and skill mastery for Andriy.
Zero cross-domain distractions. Kira focuses exclusively on 5 core disciplines:
1. 🇬🇧 English Mastery (Business, Tech, Pitching, Idioms)
2. 💻 Programming & System Architecture (Python, Go, Distributed Systems, Clean Code)
3. 🧠 AI Engineering & Agents (LLMs, RAG, Swarms, LangGraph, Embeddings)
4. ⚡ Vibecoding & Rapid Prototyping (Prompt-to-Code, Cursor/Claude workflows, MVP shipping)
5. 🏛️ World History, Strategy & Mental Models (Geopolitics, Roman Empire, Machiavelli, Sun Tzu)
"""

from __future__ import annotations

import json
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

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


DISCIPLINES = {
    "english": {
        "title": "Англійська мова (English Mastery)",
        "icon": "🇬🇧",
        "focus": "Business English, Tech Discussions, Silicon Valley Pitching, Nuance & Precision",
        "topics": ["Investor Negotiations", "Technical Architecture Defense", "Idioms & Executive Presence", "Accent & Pronunciation Nuance"],
    },
    "programming": {
        "title": "Програмування (Software Engineering)",
        "icon": "💻",
        "focus": "System Architecture, High-Load, Python/Async, Rust/Go, Design Patterns & Clean Code",
        "topics": ["Distributed Systems", "Concurrency & AsyncIO", "Microservices & Event-Driven Architecture", "Data Structures & Algorithmic Optimization"],
    },
    "ai_engineering": {
        "title": "Нейромережі (AI Engineering & Agents)",
        "icon": "🧠",
        "focus": "Autonomous Agent Swarms, LangGraph, Advanced RAG, Fine-Tuning, Reasoning Models",
        "topics": ["Multi-Agent Orchestration", "Vector Databases & Semantic Routing", "Prompt Engineering & Guardrails", "Local Model Deployment (Ollama/vLLM)"],
    },
    "vibecoding": {
        "title": "Вайбкодинг (Rapid AI Prototyping)",
        "icon": "⚡",
        "focus": "Prompt-Driven Development, Cursor & Claude Workflows, Zero-Friction MVP Shipping",
        "topics": ["Spec-Driven Generation", "Agentic Debugging Loops", "Full-Stack MVP in 60 Minutes", "AI Copilot Synergy"],
    },
    "history": {
        "title": "Історія (Strategy & Mental Models)",
        "icon": "🏛️",
        "focus": "Geopolitics, Civilizational Cycles, Military Strategy, Lessons of Empire & Power",
        "topics": ["Roman Republic & Imperial Decay", "Sun Tzu & The Art of War", "Cold War Intelligence Doctrines", "Monetary Crises & Industrial Revolutions"],
    },
}


class KiraAgent:
    """
    Academic Mentor & Director of Floor 8 (SYNDICATE Academy).
    Cultivates deep mastery, guides Socratic dialogue, and generates personalized curricula.
    """

    AGENT_ID = "kira"
    FLOOR = 8

    def __init__(
        self,
        memory: Optional[Any] = None,
        llm: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[Any] = None,
    ) -> None:
        self._memory = memory
        self._llm = llm
        self._config = config or {}
        self._registry = registry
        self._memory_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
            f"kira_memory_context_{id(self)}", default=None
        )

    async def _llm_ask(self, prompt: str, fallback: str) -> str:
        """Invoke the LLM with bounded, untrusted historical context."""
        if not self._llm:
            return fallback
        prompt = append_memory_context(
            prompt,
            self._memory_context.get() or {},
            instruction=(
                "Use prior learning preferences and completed topics as historical "
                "context; do not assume past quiz answers prove current mastery."
            ),
        )
        try:
            resp = await self._llm.ainvoke([HumanMessage(content=prompt)])
            return str(getattr(resp, "content", resp))
        except Exception as exc:  # noqa: BLE001
            logger.warning("kira_llm_ainvoke_failed", error=str(exc))
            return fallback

    async def _save(self, payload: Dict[str, Any], category: str, data: Dict[str, Any]) -> None:
        """Save a redacted educational episode without blocking the lesson."""
        await save_agent_episode(
            self._memory,
            agent_id=self.AGENT_ID,
            session_id=memory_session_id(payload, "kira-academy-session"),
            action=category,
            role="mentor",
            content=json.dumps(data, ensure_ascii=False, default=str)[:8000],
            metadata={
                "category": category,
                "floor": self.FLOOR,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch academic or mentorship action."""
        action = payload.get("action", "socratic_dialogue")
        logger.info("kira_action_dispatched", action=action)

        dispatch_table = {
            "socratic_dialogue": self.socratic_dialogue,
            "lesson_plan": self.lesson_plan,
            "code_review": self.code_review_mentor,
            "language_practice": self.language_practice,
            "history_synthesis": self.history_synthesis,
            "vibecoding_session": self.vibecoding_session,
            "micro_quiz": self.micro_quiz,
            "disciplines_overview": self.disciplines_overview,
            "academy_overview": self.disciplines_overview,
            "morning_data": self.morning_data,
        }

        handler = dispatch_table.get(action)
        if handler is None:
            # Previously an unknown action silently fell through to
            # ``socratic_dialogue``, so a typo produced a plausible-looking but
            # unrelated answer instead of an error.
            logger.warning("kira_unknown_action", action=action)
            return {
                "status": "error",
                "agent": self.AGENT_ID,
                "error": f"Unknown action: {action}",
                "available_actions": sorted(dispatch_table),
            }

        session_id = memory_session_id(payload, "kira-academy-session")
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
            await self._save(payload, f"academy_{action}", result)
            if action == "socratic_dialogue" and result.get("socratic_response"):
                result["skill_candidate"] = {
                    "name": "Socratic dialogue for deliberate learning",
                    "when_to_use": "When helping a learner examine a claim or difficult concept.",
                    "procedure": (
                        "Clarify the learner's claim and topic; surface hidden assumptions; "
                        "ask two or three focused questions; offer one useful analogy; "
                        "finish by inviting the learner to test or refine their reasoning."
                    ),
                }
            return result
        finally:
            self._memory_context.reset(token)

    async def disciplines_overview(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Return structured catalogue of all active Academy disciplines."""
        return {
            "status": "ok",
            "agent": self.AGENT_ID,
            "floor": self.FLOOR,
            "title": "SYNDICATE Academy — Поверх 8",
            "disciplines": DISCIPLINES,
            "active_students": ["Андрій (Founder & Sovereign)"],
            "philosophy": "Сувора спеціалізація. Сократівський метод. Миттєве застосування знань у практиці.",
        }

    async def socratic_dialogue(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Socratic Sparring: Challenges assumptions, deconstructs mental models,
        and pushes Andriy toward first-principles thinking.
        """
        topic = payload.get("topic", "Architectural tradeoffs in autonomous agent swarms")
        statement = payload.get("statement", "We should use microservices for all agent communication.")
        discipline = payload.get("discipline", "programming")

        prompt = f"""Ви — Кіра, інтелектуальний наставник та академічний ментор 8-го поверху синдикату SYNDICATE.
Ваш студент — Андрій (засновник синдикату). Ви спілкуєтесь на рівних, із глибокою повагою, інтелектуальною гостротою та сократівською іронією.

Дисципліна: {DISCIPLINES.get(discipline, {}).get('title', discipline)}
Тема розмови: {topic}
Твердження студента: "{statement}"

Завдання:
1. Застосуйте сократівський діалог. Не давайте готову банальну відповідь.
2. Знайдіть приховані припущення та слабкі місця у твердженні.
3. Поставте 2-3 точні, гострі контр-питання, які змусять мислити від перших принципів (First Principles).
4. Наведіть одну сильну аналогію (з інженерії, військової історії або когнітивних наук).
5. Формат: чіткий, захоплюючий, вишуканий стиль українською мовою."""

        fallback = (
            f"«Андрію, твоє твердження щодо '{topic}' звучить переконливо, але давай розберемо його фундамент. "
            f"Якщо ми приймемо це як аксіому, що станеться з системою при десятикратному навантаженні? "
            f"Яке приховане припущення ти тут робиш щодо затримки мережі та узгодженості даних?»"
        )

        response = await self._llm_ask(prompt, fallback)
        return {
            "discipline": discipline,
            "topic": topic,
            "socratic_response": response,
            "confidence": 0.95,
            "floor": self.FLOOR,
        }

    async def lesson_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a high-density, tailored curriculum for Andriy.
        """
        discipline = payload.get("discipline", "ai_engineering")
        goal = payload.get("goal", "Побудова агентної пам'яті на базі pgvector та GraphRAG")
        depth = payload.get("depth", "advanced")

        prompt = f"""Ви — Кіра, ментор SYNDICATE Academy. Складіть інтенсивний навчальний план для Андрія.
Дисципліна: {discipline}
Ціль: {goal}
Рівень: {depth}

Складіть структурований план у форматі:
1. 🎯 Головна мета та кінцевий артефакт (що конкретно Андрій напише/зрозуміє).
2. 📚 Модуль 1: Фундаментальні концепції (теорія від перших принципів).
3. ⚙️ Модуль 2: Архітектура та Hands-on практика (код, інструменти).
4. 🥊 Модуль 3: Стрес-тест та Hardcore завдання.
5. 💡 Менторська порада від Кіри (на що звернути критичну увагу)."""

        fallback = (
            f"План для цілі '{goal}' підготовлено:\n"
            "1. Фундамент векторних індексів HNSW та косинусної близькості.\n"
            "2. Практика: розгортання LangGraph StateGraph з рекурентним завантаженням уроків.\n"
            "3. Hardcore: симуляція збоїв та виявлення галюцинацій через Sentinel."
        )

        response = await self._llm_ask(prompt, fallback)
        return {
            "discipline": discipline,
            "goal": goal,
            "curriculum": response,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "floor": self.FLOOR,
        }

    async def code_review_mentor(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Educational code review focused on architectural beauty, elegance, and vibecoding flow.
        """
        code_snippet = payload.get("code", "def fetch_data(): pass")
        language = payload.get("language", "python")

        prompt = f"""Ви — Кіра. Проведіть навчальний менторський код-рев'ю для Андрія.
Мова: {language}
Код:
```{language}
{code_snippet}
```

Проаналізуйте:
1. Архітектурну елегантність та простоту.
2. Продуктивність (асинхронність, пам'ять, масштабованість).
3. Вайбкодинг-потенціал: як оптимізувати промпт або структуру для швидкої ітерації з AI.
4. Покращений рефакторинг коду.
Будьте конструктивною, точковою та вимогливою."""

        fallback = "Код перевірено. Рекомендується додати асинхронний контекстний менеджер та типізацію Pydantic."
        response = await self._llm_ask(prompt, fallback)
        return {
            "language": language,
            "review": response,
            "status": "reviewed",
            "floor": self.FLOOR,
        }

    async def language_practice(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        English Immersion Drill for executive leadership, investor pitches, and tech negotiation.
        """
        scenario = payload.get("scenario", "Pitching SYNDICATE autonomous multi-agent platform to Andreessen Horowitz (a16z)")
        user_input = payload.get("user_input", "We build an autonomous agent holding that replaces human operations.")

        prompt = f"""You are Kira, executive English mentor for Andriy, founder of SYNDICATE.
Scenario: {scenario}
Andriy's phrase/pitch: "{user_input}"

Provide:
1. 🌟 Native Executive Polish (Rewrite the phrase to sound like a tier-1 Silicon Valley founder — confident, precise, charismatic).
2. 🔍 Nuance Breakdown (Why the change works: word choice, cadence, subtext).
3. 💬 Follow-up Challenge Question (In character as the investor/partner asking a hard question in English for Andriy to answer next)."""

        fallback = (
            "Native Polish: 'SYNDICATE is an autonomous multi-agent holding company engineered to eliminate operational friction and scale sovereign enterprise execution.'\n"
            "Challenge: 'How do you guarantee state consistency across your multi-agent layer during high-frequency volatility?'"
        )

        response = await self._llm_ask(prompt, fallback)
        return {
            "scenario": scenario,
            "feedback": response,
            "floor": self.FLOOR,
        }

    async def history_synthesis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strategic synthesis of historical lessons, mental models, and geopolitical precedents.
        """
        query = payload.get("query", "Як зберегти суверенітет та контроль у децентралізованій системі?")

        prompt = f"""Ви — Кіра, ментор з історії та стратегічного мислення 8-го поверху.
Запит Андрія: "{query}"

Проведіть глибокий історичний синтез:
1. 🏛️ Історичний прецедент (наприклад: реформи Діоклетіана, Венеційська республіка, стратегія Бісмарка або доктрина візантійського балансу).
2. 🧠 Фундаментальна модель влади та контролю (First Principles).
3. ⚡ Прямий висновок для архітектури SYNDICATE сьогодні."""

        fallback = (
            "Прецедент: Реформи Діоклетіана (Тетрархія). Розподіл операційного тягаря за збереження єдиного ідеологічного центру. "
            "Висновок для SYNDICATE: Ізоляція поверхів (Док, Сем, Кіра) захищає від єдиної точки відмови."
        )

        response = await self._llm_ask(prompt, fallback)
        return {
            "query": query,
            "historical_synthesis": response,
            "floor": self.FLOOR,
        }

    async def vibecoding_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mentorship on rapid vibecoding: orchestrating AI models, crafting specs,
        and turning ideas into production artifacts in single-digit minutes.
        """
        task_concept = payload.get("concept", "Telegram bot that parses financial PDFs and calls Fin agent")

        prompt = f"""Ви — Кіра. Допоможіть Андрію у вайбкодинг-сесії для швидкого прототипування.
Концепт задачі: "{task_concept}"

Складіть компактний, надточний Вайбкодинг-Бриф для згодовування в Cursor/Claude/Copilot:
1. 🎯 One-shot System Prompt для кодогенератора.
2. 🧱 Мінімальна схема файлів (Zero-bloat architecture).
3. ⚡ Трик для швидкого тестування без ручного написання моків."""

        fallback = "Вайбкодинг-бриф готовий: швидка специфікація на базі FastAPI та aiogram з прямим викликом src.agents.fin."
        response = await self._llm_ask(prompt, fallback)
        return {
            "concept": task_concept,
            "vibecoding_brief": response,
            "floor": self.FLOOR,
        }

    async def micro_quiz(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a 3-question rapid retention quiz on a chosen discipline."""
        discipline = payload.get("discipline", "programming")
        topic = payload.get("topic", "Python Concurrency")

        prompt = f"""Складіть експрес-тест із 3 запитань від Кіри для перевірки знань Андрія.
Дисципліна: {discipline}, Тема: {topic}.
Кожне запитання повинно бути практичним (не шкільна теорія, а реальний кейс), з 4 варіантами (A, B, C, D) та зазначенням правильної відповіді з коротким поясненням."""

        fallback = "1. Що відбудеться при виклику asyncio.gather() без обробки винятків? A) Падіння B) Повернення винятку..."
        response = await self._llm_ask(prompt, fallback)
        return {
            "discipline": discipline,
            "topic": topic,
            "quiz": response,
            "floor": self.FLOOR,
        }

    async def morning_data(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compact educational spark for Eva's 07:00 daily executive briefing.
        Provides a cognitive boost to start Andriy's day.
        """
        return {
            "agent": self.AGENT_ID,
            "floor": self.FLOOR,
            "word_of_the_day_en": "Antifragile (noun/adj) — Things that gain from disorder and volatility.",
            "coding_spark": "Tip: Use asyncio.TaskGroup (Python 3.11+) instead of gather for structured concurrency.",
            "history_model": "Carthage vs. Rome: Logistics and institutional endurance always overcome tactical genius.",
            "academy_status": "Поверх 8 функціонує в штатному режимі. Готова до сесії.",
        }
