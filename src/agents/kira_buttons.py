"""Кіра — інтерактивні кнопки Telegram (inline keyboard). Лише розмітка і розбір callback.

Бот приватний: натиснути може лише власник (allowlist). Порожній allowlist = відмова всім.
Callback_data ≤ 64 байти (обмеження Telegram). Мережі тут немає: бот-раннер окремий і
ще не запущений (немає токена).

Формат callback:
  kira:disc:<дисципліна>          → квіз із цієї дисципліни
  kira:act:<socratic|plan|quiz|status|spark>
  kira:ans:<question_id>:<A-D>    → відповідь на питання
  kira:prop:<proposal_id>:<ok|no> → схвалити / відхилити пропозицію (лише власник)
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

OWNER = "andrii"
CALLBACK_MAX_BYTES = 64

MENUS: Dict[str, List[List[Tuple[str, str]]]] = {
    "main": [
        [("🇬🇧 ENG", "kira:disc:english"), ("💻 DEV", "kira:disc:programming")],
        [("🧠 AI", "kira:disc:ai_engineering"), ("⚡ VIBE", "kira:disc:vibecoding")],
        [("🏛️ HIST", "kira:disc:history")],
        [("🥊 Спаринг", "kira:act:socratic"), ("📚 План", "kira:act:plan")],
        [("⚡ Тест", "kira:act:quiz"), ("📈 Прогрес", "kira:act:status")],
        [("🌅 Іскра дня", "kira:act:spark")],
    ],
}

ACTIONS: Dict[str, str] = {
    "socratic": "socratic_dialogue",
    "plan": "lesson_plan",
    "quiz": "micro_quiz",
    "status": "learning_status",
    "spark": "morning_data",
}

DISCIPLINE_KEYS = ("english", "programming", "ai_engineering", "vibecoding", "history")


def build_main_menu() -> List[List[Dict[str, str]]]:
    return [[{"text": t, "callback_data": c} for t, c in row] for row in MENUS["main"]]


def build_answer_keyboard(question_id: str) -> Optional[List[List[Dict[str, str]]]]:
    """Кнопки A–D для питання. None, якщо callback не поміщається в 64 байти."""
    rows = []
    for letter in ("A", "B", "C", "D"):
        data = f"kira:ans:{question_id}:{letter}"
        if len(data.encode("utf-8")) > CALLBACK_MAX_BYTES:
            return None
        rows.append({"text": letter, "callback_data": data})
    return [rows[:2], rows[2:]]


def build_proposal_keyboard(proposal_id: str) -> List[List[Dict[str, str]]]:
    return [[
        {"text": "✅ Схвалити", "callback_data": f"kira:prop:{proposal_id}:ok"},
        {"text": "❌ Відхилити", "callback_data": f"kira:prop:{proposal_id}:no"},
    ]]


def parse_callback(data: str, sender_id: str, owner_ids: Iterable[str]) -> Dict[str, Any]:
    """Розбір натиснутої кнопки. Повертає {"ok": bool, ...}; помилка — з причиною.

    Не виконує дій: повертає, яку дію (action) викликати в KiraAgent.execute.
    """
    allowed = {str(x) for x in owner_ids if str(x)}
    if not allowed or str(sender_id) not in allowed:
        return {"ok": False, "reason": "not_owner"}
    if not isinstance(data, str) or len(data.encode("utf-8")) > CALLBACK_MAX_BYTES:
        return {"ok": False, "reason": "bad_callback"}

    parts = data.split(":")
    if len(parts) < 3 or parts[0] != "kira":
        return {"ok": False, "reason": "bad_callback"}
    kind = parts[1]

    if kind == "disc" and len(parts) == 3 and parts[2] in DISCIPLINE_KEYS:
        return {"ok": True, "action": "micro_quiz", "discipline": parts[2]}
    if kind == "act" and len(parts) == 3 and parts[2] in ACTIONS:
        return {"ok": True, "action": ACTIONS[parts[2]]}
    if kind == "ans" and len(parts) == 4 and parts[3] in ("A", "B", "C", "D") and parts[2]:
        return {"ok": True, "action": "micro_quiz_answer", "question_id": parts[2], "choice": parts[3]}
    if kind == "prop" and len(parts) == 4 and parts[2] and parts[3] in ("ok", "no"):
        return {
            "ok": True,
            "action": "decide_proposal",
            "proposal_id": parts[2],
            "decision": "approve" if parts[3] == "ok" else "reject",
            "actor": OWNER,
        }
    return {"ok": False, "reason": "unknown_callback"}
