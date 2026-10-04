"""
Kira's Socratic Tutor — teaches thinking, does not hand out answers.

Hint ladder (per student+topic):
  1  clarifying question      — "what exactly do you expect, what have you tried?"
  2  conceptual nudge         — name the principle/area to look at
  3  scaffold                 — structure of the solution with the key step left blank
  4  reveal                   — full answer, only after real attempts (or an explicit
                                confirmed request), followed by a teach-back task

Requests like "just give me the code" never skip the ladder silently: the tutor
acknowledges them, explains why, and moves one rung up instead.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

ANSWER_REQUEST = re.compile(
    r"(дай|напиши|скажи|покажи|просто)\s+(мені\s+)?(готов\w+\s+)?(відповідь|ответ|код|рішення|решение)|"
    r"give me the (answer|code|solution)|just (tell|show|write)|без\s+пояснен|не\s+хочу\s+думати",
    re.I,
)
MIN_ATTEMPTS_FOR_REVEAL = 3


@dataclass
class TutorSession:
    student: str
    topic: str
    attempts: int = 0
    level: int = 1
    history: list = field(default_factory=list)
    revealed: bool = False


class SocraticTutor:
    def __init__(self) -> None:
        self._sessions: Dict[Tuple[str, str], TutorSession] = {}

    def _session(self, student: str, topic: str) -> TutorSession:
        return self._sessions.setdefault((student, topic), TutorSession(student, topic))

    def reset(self, student: str, topic: str) -> None:
        self._sessions.pop((student, topic), None)

    @staticmethod
    def wants_answer(message: str) -> bool:
        return bool(ANSWER_REQUEST.search(message or ""))

    @staticmethod
    def _is_real_attempt(message: str) -> bool:
        words = re.findall(r"\w+", message or "", re.UNICODE)
        return len(words) >= 6 or "```" in (message or "")

    def next_turn(
        self,
        student: str,
        topic: str,
        message: str,
        discipline: str = "programming",
        concept: str = "",
        scaffold: str = "",
        answer: str = "",
        confirm_reveal: bool = False,
    ) -> Dict[str, Any]:
        s = self._session(student, topic)
        asked_for_answer = self.wants_answer(message)
        if self._is_real_attempt(message) and not asked_for_answer:
            s.attempts += 1
        s.history.append(message)

        # Level selection: attempts and persistence move the ladder, shortcuts do not skip it.
        target = 1 + min(s.attempts, 2) + (1 if asked_for_answer and s.attempts >= 1 else 0)
        s.level = max(s.level, min(target, 3))

        can_reveal = s.attempts >= MIN_ATTEMPTS_FOR_REVEAL or (asked_for_answer and confirm_reveal and s.attempts >= 1)
        if can_reveal and (asked_for_answer or s.attempts >= MIN_ATTEMPTS_FOR_REVEAL + 1):
            s.level, s.revealed = 4, True

        if s.level == 1:
            text = (
                f"Перш ніж ми рушимо далі по темі «{topic}»: що саме ти очікуєш отримати і що вже пробував? "
                "Опиши, будь ласка, свою гіпотезу 2–3 реченнями — навіть якщо вона неповна."
            )
            mode = "clarify"
        elif s.level == 2:
            area = f" Подивись у бік: {concept}." if concept else ""
            text = (
                "Ти вже близько до суті, але прихована помилка ховається в припущенні, яке ти не озвучив."
                f"{area} Яке твердження ти приймаєш як очевидне — і що буде, якщо воно хибне?"
            )
            mode = "nudge"
        elif s.level == 3:
            frame = scaffold or "1) Визнач вхід і вихід. 2) Назви інваріант. 3) ____ (ключовий крок — за тобою). 4) Перевір граничний випадок."
            text = f"Дам каркас, але ключовий крок залишаю тобі:\n{frame}\nЗапиши, що має бути на місці пропуску, і чому."
            mode = "scaffold"
        else:
            if not answer:
                text = "Ти докладав зусиль, тож я готова розкрити рішення — але конкретного ключа відповіді для цієї теми немає. Сформулюймо його разом."
            else:
                text = (
                    f"Ти пройшов {s.attempts} спроб(и), тому ось повне пояснення:\n{answer}\n\n"
                    "Тепер зворотне навчання: поясни це своїми словами так, ніби вчиш колегу, і назви одну ситуацію, де підхід ламається."
                )
            mode = "reveal"

        note = ""
        if asked_for_answer and mode != "reveal":
            note = "Я не відмовляюсь допомагати — я не віддам готове, бо тоді знання не залишиться з тобою. Піднімаємось на крок вище."

        return {
            "tutor": "kira", "discipline": discipline, "topic": topic, "mode": mode, "level": s.level,
            "attempts": s.attempts, "answer_revealed": mode == "reveal" and bool(answer),
            "answer_request_detected": asked_for_answer, "message": text, "note": note,
        }

    def next_hint(
        self,
        session_id: str,
        user_message: str = "",
        problem_statement: str = "",
        solution: str = "",
        student: str = "student",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Convenience method for next ladder turn."""
        turn = self.next_turn(
            student=student,
            topic=problem_statement or session_id,
            message=user_message,
            concept=kwargs.get("concept", ""),
            scaffold=kwargs.get("scaffold", ""),
            answer=solution,
        )
        return {
            "status": "ok",
            "session_id": session_id,
            "stage": turn["mode"],
            "stage_index": turn["level"],
            "hint": turn["message"],
            "level": turn["level"],
            "answer_revealed": turn["answer_revealed"],
            "turn": turn,
        }

    def solve(
        self,
        session_id: str,
        problem_statement: str = "",
        solution: str = "",
        student: str = "student",
    ) -> Dict[str, Any]:
        """Fast-forward to solve stage."""
        s = self._session(student, problem_statement or session_id)
        s.attempts = MIN_ATTEMPTS_FOR_REVEAL + 1
        s.level = 4
        s.revealed = True
        turn = self.next_turn(
            student=student,
            topic=problem_statement or session_id,
            message="Show me the full solution now please.",
            answer=solution,
            confirm_reveal=True,
        )
        return {
            "status": "solved",
            "solution": solution,
            "message": turn["message"],
            "stage": "reveal",
            "level": 4,
        }
