"""K.O.D.E.K.S. — інтерактивні кнопки Telegram-бота. Лише розмітка й розбір callback.

Бот приватний: лише Андрій. Видалення і будь-який вихід в інтернет — тільки після натискання
«Підтвердити» від Андрія. Єва отримує звіт (без кнопок).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

MENUS: Dict[str, List[List[Tuple[str, str, str]]]] = {
    "main": [
        [("📥 Завантажити файл", "up:file", "andrii"), ("🔗 Посилання (з дозволом)", "up:link", "andrii")],
        [("🗂 Структура архіву", "tree:show", "andrii"), ("✏️ Перезаписати", "edit:start", "andrii")],
        [("🗑 Видалити", "del:start", "andrii"), ("🧭 Розподіл по базах", "route:show", "andrii")],
        [("🎙 Транскрибація", "tr:start", "andrii"), ("🌐 Переклад", "tl:start", "andrii")],
        [("🧩 Вивчити новий формат", "fmt:learn", "andrii"), ("📊 Звіт для Єви", "rep:eva", "andrii")],
        [("📋 Повний звіт", "rep:full", "andrii")],
    ],
    "confirm_delete": [
        [("✅ Так, видалити (кошик на 30 днів)", "del:yes", "andrii"), ("❌ Скасувати", "del:no", "andrii")],
    ],
    "approve_download": [
        [("✅ Дозволити завантаження", "net:yes", "andrii"), ("❌ Ні", "net:no", "andrii")],
    ],
    "approve_format": [
        [("✅ Вивчити формат", "fmt:yes", "andrii"), ("❌ Не треба", "fmt:no", "andrii")],
    ],
}

ACTIONS = {
    "up:file": ("upload", "await_file"),
    "up:link": ("download", "ask_url"),
    "tree:show": ("archive", "tree"),
    "edit:start": ("edit", "pick_item"),
    "del:start": ("delete", "pick_item"),
    "del:yes": ("delete", "confirm"),
    "del:no": ("delete", "cancel"),
    "route:show": ("route", "show"),
    "tr:start": ("transcribe", "await_media"),
    "tl:start": ("translate", "await_text"),
    "fmt:learn": ("format", "ask_ext"),
    "fmt:yes": ("format", "approve"),
    "fmt:no": ("format", "reject"),
    "net:yes": ("download", "approve"),
    "net:no": ("download", "reject"),
    "rep:eva": ("report", "eva"),
    "rep:full": ("report", "full"),
}


def build_keyboard(menu: str, sender: str) -> dict:
    rows = []
    for row in MENUS[menu]:
        buttons = [{"text": t, "callback_data": cb} for t, cb, who in row if sender in who.split(",")]
        if buttons:
            rows.append(buttons)
    return {"inline_keyboard": rows}


def handle_callback(data: str, sender: str) -> Optional[dict]:
    if sender != "andrii" or data not in ACTIONS:
        return None
    action, arg = ACTIONS[data]
    return {"action": action, "arg": arg, "callback": data}
