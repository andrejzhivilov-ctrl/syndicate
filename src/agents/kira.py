"""
Kira Agent — Academic Mentor, Live Psychotherapist, English Pronunciation Coach & SYNDICATE Academy Director.
Floor 8: Enlightenment, Academy, Psychological Resilience & Mentorship.

Strict Domain Isolation:
Dedicated solely to education, cognitive elevation, live psychotherapy, and skill mastery for Andriy.
Дисципліни, банк питань і ранкові елементи — у каталозі (``kira_catalog_seed.json``),
доповнення схвалює Андрій (``kira_learning``). Нові дисципліни додаються даними, не кодом.

Правила чесності (AGENTS.md, розділ 1):
- Без LLM дії, що потребують генерації тексту, повертають ``unavailable`` без вигаданого змісту.
- Квізи — лише з банку з ключем відповіді. Відповіді, які LLM генерує без перевірки, не дають
  оцінки знань.
- Метрики (accuracy) з'являються лише від реальних відповідей і лише після мінімальної кількості.
- Акустична оцінка вимови (``english_pronunciation_assessment``) та LiveKit-сесії (``live_therapy_session``)
  працюють детерміновано через локальний стек ``LiveKit + Silero VAD v5 + Kokoro-82M + PronunciationCoach``
  за $0.00 токенів.
"""

from __future__ import annotations

import json
import os
from contextvars import ContextVar
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import structlog
from langchain_core.messages import HumanMessage

from src.agent_memory import (
    append_memory_context,
    memory_session_id,
    memory_status,
    recall_agent_memory,
    save_agent_episode,
)
from src.agents.kira_catalog import MORNING_KINDS, load_seed
from src.agents.kira_learning import KiraLearningStore
from src.voice.livekit_realtime import LiveKitRealtimeBridge
from src.voice.pronunciation_coach import PronunciationCoach

logger = structlog.get_logger(__name__)

#: Статуси, після яких результат має сенс зберігати в пам'ять (не «порожні» відповіді).
SAVEABLE_STATUSES = ("ok", "partial", "completed")

# Сумісність: попередній імпорт DISCIPLINES з цього модуля працює і зараз.
DISCIPLINES: Dict[str, Any] = load_seed()["disciplines"]


class KiraAgent:
    """
    Academic Mentor, Live Psychotherapist, English Pronunciation Coach & Director of Floor 8.
    Cultivates deep mastery, guides Socratic dialogue, conducts zero-token live voice therapy,
    and evaluates phoneme-level English pronunciation.
    """

    AGENT_ID = "kira"
    FLOOR = 8

    def __init__(
        self,
        memory: Optional[Any] = None,
        llm: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[Any] = None,
        learning: Optional[KiraLearningStore] = None,
        livekit_bridge: Optional[LiveKitRealtimeBridge] = None,
        pronunciation_coach: Optional[PronunciationCoach] = None,
    ) -> None:
        self._memory = memory
        self._llm = llm
        self._config = config or {}
        self._registry = registry
        if learning is None:
            data_dir = os.getenv("KIRA_DATA_DIR")
            learning = KiraLearningStore(Path(data_dir) / "kira_learning.json" if data_dir else None)
        self._learning = learning
        self._livekit = livekit_bridge or LiveKitRealtimeBridge()
        self._pronunciation_coach = pronunciation_coach or PronunciationCoach()
        self._memory_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
            f"kira_memory_context_{id(self)}", default=None
        )

    # ------------------------------------------------------------ допоміжні
    def _catalog(self) -> Dict[str, Any]:
        return self._learning.catalog()

    def _unavailable(self, action: str, reason: str, **extra: Any) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "status": "unavailable",
            "agent": self.AGENT_ID,
            "action": action,
            "reason": reason,
            "floor": self.FLOOR,
        }
        out.update(extra)
        return out

    async def _llm_ask(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """Повертає (текст, None) або (None, причина). Фолбек-тексту немає."""
        if not self._llm:
            return None, "llm_not_configured"
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
            return str(getattr(resp, "content", resp)), None
        except Exception as exc:  # noqa: BLE001
            logger.warning("kira_llm_ainvoke_failed", error_type=type(exc).__name__)
            return None, "llm_error"

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

    # ------------------------------------------------------------ диспетчер
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch academic, psychotherapy, or pronunciation coaching action."""
        action = payload.get("action", "socratic_dialogue")
        logger.info("kira_action_dispatched", action=action)

        dispatch_table = {
            "socratic_dialogue": self.socratic_dialogue,
            "lesson_plan": self.lesson_plan,
            "code_review": self.code_review_mentor,
            "language_practice": self.language_practice,
            "english_pronunciation_assessment": self.english_pronunciation_assessment,
            "live_therapy_session": self.live_therapy_session,
            "history_synthesis": self.history_synthesis,
            "vibecoding_session": self.vibecoding_session,
            "micro_quiz": self.micro_quiz,
            "micro_quiz_answer": self.micro_quiz_answer,
            "learning_status": self.learning_status,
            "propose_learning": self.propose_learning,
            "decide_proposal": self.decide_proposal,
            "disciplines_overview": self.disciplines_overview,
            "academy_overview": self.disciplines_overview,
            "morning_data": self.morning_data,
        }

        handler = dispatch_table.get(action)
        if handler is None:
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
                if result.get("status") in SAVEABLE_STATUSES:
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

    # ------------------------------------------------------------ каталог
    async def disciplines_overview(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Return structured catalogue of all active Academy disciplines."""
        catalog = self._catalog()
        return {
            "status": "ok",
            "agent": self.AGENT_ID,
            "floor": self.FLOOR,
            "title": "SYNDICATE Academy — Поверх 8",
            "disciplines": catalog["disciplines"],
            "quiz_items": len(catalog["quiz_bank"]),
            "active_students": ["Андрій (Founder & Sovereign)"],
            "philosophy": "Сувора спеціалізація. Сократівський метод. Миттєве застосування знань у практиці.",
            "live_capabilities": [
                "LiveKit + Silero VAD v5 + Kokoro-82M Psychotherapy Mode ($0 tokens)",
                "Wav2Vec2-GOP Acoustic English Pronunciation Coach (IPA phoneme scoring)",
            ],
        }

    # ------------------------------------------------------------ Live Psychotherapy & English Pronunciation
    async def live_therapy_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start or process a full-duplex LiveKit + Silero VAD v5 + Kokoro-82M Psychotherapy session.
        100% local voice processing ($0.00 voice tokens, zero third-party audio leakage).
        """
        session_id = str(payload.get("session_id", "kira-therapy-live"))
        mode = str(payload.get("mode", "psychotherapy"))
        user_reflection = payload.get("user_reflection")

        room_info = self._livekit.start_session(
            session_id=session_id,
            agent_id=self.AGENT_ID,
            mode=mode,
            privacy_local_only=True,
        )

        # Optional LLM therapeutic reflection if LLM is configured and user shared thoughts
        therapeutic_reply: Optional[str] = None
        if isinstance(user_reflection, str) and user_reflection.strip() and self._llm:
            prompt = (
                "Ви — Кіра, емпатичний психотерапевт (CBT та екзистенційний підхід) і ментор Андрія. "
                f"Андрій поділився станом під час Live-сесії: \"{user_reflection}\". "
                "Дайте теплу, спокійну, глибоку підтримку українською мовою та поставте одне м'яке рефлексивне запитання."
            )
            therapeutic_reply, _ = await self._llm_ask(prompt)

        return {
            "status": "ok",
            "agent": self.AGENT_ID,
            "floor": self.FLOOR,
            "live_room": room_info,
            "therapeutic_reply": therapeutic_reply,
            "voice_profile": "0.70*af_heart + 0.30*af_nicole (speed=0.90x empathetic cadence)",
            "voice_token_cost_usd": 0.0,
        }

    async def english_pronunciation_assessment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Acoustic phoneme & IPA pronunciation assessment for Andrii's spoken English.
        Detects phonetic errors (/θ/, /ð/, /w/ vs /v/, vowel length) that standard Whisper STT auto-corrects.
        """
        target_phrase = payload.get("target_phrase") or payload.get("user_input")
        if not isinstance(target_phrase, str) or not target_phrase.strip():
            return self._unavailable("english_pronunciation_assessment", "target_phrase_required")

        acoustic_phonemes = payload.get("acoustic_phonemes_detected")
        substitutions = payload.get("simulated_substitutions")

        report = self._pronunciation_coach.evaluate_utterance(
            target_phrase=target_phrase,
            acoustic_phonemes_detected=acoustic_phonemes,
            simulated_substitutions=substitutions if isinstance(substitutions, dict) else None,
        )

        return {
            "status": "ok",
            "agent": self.AGENT_ID,
            "floor": self.FLOOR,
            "assessment": report.to_dict(),
        }

    # ------------------------------------------------------------ LLM-дії (без LLM — unavailable)
    async def socratic_dialogue(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Socratic Sparring: Challenges assumptions, deconstructs mental models,
        and pushes Andriy toward first-principles thinking.
        """
        topic = payload.get("topic", "Architectural tradeoffs in autonomous agent swarms")
        statement = payload.get("statement", "We should use microservices for all agent communication.")
        discipline = payload.get("discipline", "programming")
        disciplines = self._catalog()["disciplines"]

        prompt = f"""Ви — Кіра, інтелектуальний наставник та академічний ментор 8-го поверху синдикату SYNDICATE.
Ваш студент — Андрій (засновник синдикату). Ви спілкуєтесь на рівних, із глибокою повагою, інтелектуальною гостротою та сократівською іронією.

Дисципліна: {disciplines.get(discipline, {}).get('title', discipline)}
Тема розмови: {topic}
Твердження студента: "{statement}"

Завдання:
1. Застосуйте сократівський діалог. Не давайте готову банальну відповідь.
2. Знайдіть приховані припущення та слабкі місця у твердженні.
3. Поставте 2-3 точні, гострі контр-питання, які змусять мислити від перших принципів (First Principles).
4. Наведіть одну сильну аналогію (з інженерії, історії управління або когнітивних наук).
5. Формат: чіткий, захоплюючий, вишуканий стиль українською мовою."""

        text, reason = await self._llm_ask(prompt)
        if text is None:
            return self._unavailable("socratic_dialogue", reason or "llm_not_configured", discipline=discipline, topic=topic)
        return {
            "status": "ok",
            "discipline": discipline,
            "topic": topic,
            "socratic_response": text,
            "floor": self.FLOOR,
        }

    async def lesson_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a curriculum. Без LLM — лише каркас із тем каталогу (без змісту, status=partial).
        """
        discipline = payload.get("discipline", "ai_engineering")
        goal = payload.get("goal", "Побудова агентної пам'яті на базі pgvector та GraphRAG")
        depth = payload.get("depth", "advanced")
        disciplines = self._catalog()["disciplines"]
        if discipline not in disciplines:
            return self._unavailable("lesson_plan", "unknown_discipline", discipline=discipline)

        prompt = f"""Ви — Кіра, ментор SYNDICATE Academy. Складіть інтенсивний навчальний план для Андрія.
Дисципліна: {disciplines[discipline]['title']}
Ціль: {goal}
Рівень: {depth}

Складіть структурований план у форматі:
1. 🎯 Головна мета та кінцевий артефакт (що конкретно Андрій напише/зрозуміє).
2. 📚 Модуль 1: Фундаментальні концепції (теорія від перших принципів).
3. ⚙️ Модуль 2: Архітектура та Hands-on практика (код, інструменти).
4. 🥊 Модуль 3: Стрес-тест та Hardcore завдання.
5. 💡 Менторська порада від Кіри (на що звернути критичну увагу)."""

        text, reason = await self._llm_ask(prompt)
        topics = disciplines[discipline]["topics"]
        skeleton = {
            "module_1_fundamentals": topics[:2],
            "module_2_practice": topics[2:3],
            "module_3_stress_test": topics[3:4],
        }
        if text is None:
            return {
                "status": "partial",
                "agent": self.AGENT_ID,
                "discipline": discipline,
                "goal": goal,
                "skeleton": skeleton,
                "curriculum": None,
                "reason": reason or "llm_not_configured",
                "warning": "Лише каркас із каталогу теми; зміст плану не згенеровано (LLM недоступний).",
                "floor": self.FLOOR,
            }
        return {
            "status": "ok",
            "agent": self.AGENT_ID,
            "discipline": discipline,
            "goal": goal,
            "curriculum": text,
            "skeleton": skeleton,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "floor": self.FLOOR,
        }

    async def code_review_mentor(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Educational code review focused on architectural beauty, elegance, and vibecoding flow."""
        code_snippet = payload.get("code")
        language = payload.get("language", "python")
        if not isinstance(code_snippet, str) or not code_snippet.strip():
            return self._unavailable("code_review", "code_required", language=language)

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

        text, reason = await self._llm_ask(prompt)
        if text is None:
            return self._unavailable("code_review", reason or "llm_not_configured", language=language)
        return {"status": "ok", "language": language, "review": text, "floor": self.FLOOR}

    async def language_practice(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """English Immersion Drill for executive leadership, investor pitches, and tech negotiation."""
        scenario = payload.get("scenario", "Pitching SYNDICATE autonomous multi-agent platform to Andreessen Horowitz (a16z)")
        user_input = payload.get("user_input")
        if not isinstance(user_input, str) or not user_input.strip():
            return self._unavailable("language_practice", "user_input_required", scenario=scenario)

        prompt = f"""You are Kira, executive English mentor for Andriy, founder of SYNDICATE.
Scenario: {scenario}
Andriy's phrase/pitch: "{user_input}"

Provide:
1. 🌟 Native Executive Polish (Rewrite the phrase to sound like a tier-1 Silicon Valley founder — confident, precise, charismatic).
2. 🔍 Nuance Breakdown (Why the change works: word choice, cadence, subtext).
3. 💬 Follow-up Challenge Question (In character as the investor/partner asking a hard question in English for Andriy to answer next)."""

        text, reason = await self._llm_ask(prompt)
        if text is None:
            return self._unavailable("language_practice", reason or "llm_not_configured", scenario=scenario)
        return {"status": "ok", "scenario": scenario, "feedback": text, "floor": self.FLOOR}

    async def history_synthesis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Strategic synthesis of historical lessons, mental models, and geopolitical precedents."""
        query = payload.get("query")
        if not isinstance(query, str) or not query.strip():
            return self._unavailable("history_synthesis", "query_required")

        prompt = f"""Ви — Кіра, ментор з історії та стратегічного мислення 8-го поверху.
Запит Андрія: "{query}"

Проведіть глибокий історичний синтез:
1. 🏛️ Історичний прецедент (наприклад: реформи Діоклетіана, Венеційська республіка, стратегія Бісмарка або доктрина візантійського балансу).
2. 🧠 Фундаментальна модель управління та балансу інституцій (First Principles).
3. ⚡ Прямий висновок для архітектури SYNDICATE сьогодні."""

        text, reason = await self._llm_ask(prompt)
        if text is None:
            return self._unavailable("history_synthesis", reason or "llm_not_configured")
        return {"status": "ok", "query": query, "historical_synthesis": text, "floor": self.FLOOR}

    async def vibecoding_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mentorship on rapid vibecoding: orchestrating AI models, crafting specs, shipping artifacts."""
        task_concept = payload.get("concept")
        if not isinstance(task_concept, str) or not task_concept.strip():
            return self._unavailable("vibecoding_session", "concept_required")

        prompt = f"""Ви — Кіра. Допоможіть Андрію у вайбкодинг-сесії для швидкого прототипування.
Концепт задачі: "{task_concept}"

Складіть компактний, надточний Вайбкодинг-Бриф для згодовування в Cursor/Claude/Copilot:
1. 🎯 One-shot System Prompt для кодогенератора.
2. 🧱 Мінімальна схема файлів (Zero-bloat architecture).
3. ⚡ Трик для швидкого тестування без ручного написання моків."""

        text, reason = await self._llm_ask(prompt)
        if text is None:
            return self._unavailable("vibecoding_session", reason or "llm_not_configured", concept=task_concept)
        return {"status": "ok", "concept": task_concept, "vibecoding_brief": text, "floor": self.FLOOR}

    # ------------------------------------------------------------ квіз з банку (без LLM)
    async def micro_quiz(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Питання з перевіреного банку. Ключ відповіді не повертається, відповідь іде окремою дією."""
        discipline = payload.get("discipline", "programming")
        topic = payload.get("topic")
        catalog = self._catalog()
        if discipline not in catalog["disciplines"]:
            return self._unavailable("micro_quiz", "unknown_discipline", discipline=discipline)
        item = self._learning.next_quiz_item(discipline, topic)
        if item is None:
            return self._unavailable(
                "micro_quiz", "no_quiz_items_for_discipline", discipline=discipline, topic=topic
            )
        return {
            "status": "ok",
            "discipline": discipline,
            "question": {
                "id": item["id"],
                "topic": item["topic"],
                "question": item["question"],
                "options": item["options"],
            },
            "recording": "saved" if self._learning.available else "not_recorded_no_store",
            "weak_topics": self._learning.weak_topics(),
            "floor": self.FLOOR,
        }

    async def micro_quiz_answer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        question_id = payload.get("question_id")
        choice = payload.get("choice")
        if not isinstance(question_id, str) or not isinstance(choice, str):
            return {"status": "rejected", "reason": "question_id_and_choice_required", "floor": self.FLOOR}
        result = self._learning.record_answer(question_id, choice)
        result["floor"] = self.FLOOR
        return result

    async def learning_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Реальні результати: статистика тільки з перевірених відповідей."""
        return {
            "status": "ok",
            "floor": self.FLOOR,
            "store": "configured" if self._learning.available else "not_configured",
            "topic_stats": self._learning.topic_stats(),
            "weak_topics": self._learning.weak_topics(),
            "pending_proposals": self._learning.pending(),
        }

    # ------------------------------------------------------------ пропозиції (схвалює тільки Андрій)
    async def propose_learning(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = self._learning.propose(
            str(payload.get("kind", "")),
            payload.get("payload") if isinstance(payload.get("payload"), dict) else {},
            str(payload.get("reason", "")),
        )
        result["floor"] = self.FLOOR
        return result

    async def decide_proposal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = self._learning.decide(
            str(payload.get("proposal_id", "")),
            str(payload.get("decision", "")),
            str(payload.get("actor", "")),
        )
        result["floor"] = self.FLOOR
        return result

    # ------------------------------------------------------------ ранкова іскра (07:00)
    async def morning_data(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compact educational spark for Eva's 07:00 daily executive briefing.
        Ротація перевіреного каталогу за датою: однаковий день — однаковий елемент.
        """
        payload = payload or {}
        raw_date = payload.get("date")
        try:
            day = date.fromisoformat(raw_date) if isinstance(raw_date, str) else date.today()
        except ValueError:
            return {"status": "rejected", "reason": "date_must_be_ISO_YYYY-MM-DD", "floor": self.FLOOR}

        items = self._catalog()["morning_items"]
        spark: Dict[str, Any] = {}
        sources: Dict[str, str] = {}
        for kind in MORNING_KINDS:
            pool = items[kind]
            chosen = pool[day.toordinal() % len(pool)]
            spark[kind] = chosen["text"]
            sources[kind] = chosen["source"]
        return {
            "status": "ok",
            "agent": self.AGENT_ID,
            "floor": self.FLOOR,
            "date": day.isoformat(),
            "word_of_the_day_en": spark["word_of_the_day"],
            "coding_spark": spark["coding_spark"],
            "history_model": spark["history_model"],
            "sources": sources,
            "academy_status": (
                f"дисциплін: {len(self._catalog()['disciplines'])}, "
                f"питань у банку: {len(self._catalog()['quiz_bank'])}, "
                f"пропозицій на схваленні: {len(self._learning.pending())}"
            ),
        }
