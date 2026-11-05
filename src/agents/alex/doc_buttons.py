"""Док — інтерактивні кнопки Telegram-бота (inline keyboard). Лише розмітка й розбір callback.

Бот приватний: лише Андрій (єдиний chat_id). Єва отримує короткий звіт без кнопок.
Callback_data ≤ 64 байти (обмеження Telegram).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# (текст, callback, хто може натиснути)
MENUS: Dict[str, List[List[Tuple[str, str, str]]]] = {
    "main": [
        [("🟢 Готовність ЦНС", "rec:ready", "andrii"), ("😴 Сон і HRV", "rec:sleep", "andrii")],
        [("🏋️ Тренування", "trn:today", "andrii"), ("🍳 Рецепт / КБЖУ", "nut:recipe", "andrii")],
        [("💊 Добавки на сьогодні", "sup:today", "andrii"), ("🧪 Завантажити аналіз", "lab:upload", "andrii")],
        [("🔬 Дослідження", "res:new", "andrii"), ("🗄 Стан архіву", "arc:status", "andrii")],
        [("📊 Повний звіт", "rep:full", "andrii"), ("📝 Звіт для Єви", "rep:eva", "andrii")],
    ],
    "knowledge": [   # підтвердження знань, які Док хоче зберегти (самонавчання)
        [("✅ Зберегти в базу", "kn:accept", "andrii"), ("❌ Відхилити", "kn:reject", "andrii")],
        [("🔎 Показати джерело", "kn:source", "andrii"), ("⏭ Пізніше", "kn:later", "andrii")],
    ],
    "supplements": [  # розклад прийому: відмітка виконаного
        [("✔️ Прийнято", "sup:taken", "andrii"), ("⏰ Нагадати пізніше", "sup:snooze", "andrii")],
    ],
}

ACTIONS = {
    "rec:ready": ("readiness", "today"),
    "rec:sleep": ("sleep", "today"),
    "trn:today": ("training", "today"),
    "nut:recipe": ("recipe", "ask_link"),
    "sup:today": ("supplements", "today"),
    "sup:taken": ("supplements", "mark_taken"),
    "sup:snooze": ("supplements", "snooze"),
    "lab:upload": ("lab", "ask_file"),
    "res:new": ("research", "ask_topic"),
    "arc:status": ("archive", "status"),
    "rep:full": ("report", "full"),
    "rep:eva": ("report", "eva_brief"),
    "kn:accept": ("knowledge", "accept"),
    "kn:reject": ("knowledge", "reject"),
    "kn:source": ("knowledge", "source"),
    "kn:later": ("knowledge", "later"),
    "menu:main": ("menu", "main"),
}


def build_keyboard(menu: str, sender: str) -> dict:
    rows = []
    for row in MENUS[menu]:
        buttons = [{"text": t, "callback_data": cb} for t, cb, who in row if sender in who.split(",")]
        if buttons:
            rows.append(buttons)
    return {"inline_keyboard": rows}


def handle_callback(data: str, sender: str) -> Optional[dict]:
    """Розбір натискання. None — невідома кнопка або не Андрій."""
    if sender != "andrii" or data not in ACTIONS:
        return None
    action, arg = ACTIONS[data]
    return {"action": action, "arg": arg, "callback": data}
