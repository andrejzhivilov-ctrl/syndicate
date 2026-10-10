"""K.O.D.E.K.S. — інтерактивні кнопки Telegram-бота. Лише розмітка й розбір callback.

Бот приватний: лише Андрій. Зміна (редагування або видалення) мічених файлів і будь-який вихід в інтернет —
лише після натискання «Дозволити» від Андрія. Єва отримує звіт (усі дії агентів, включно з автоматичними).

Callback містить прив'язку до конкретного запиту: токен зміни (`chg:yes:<token>`), ID запису
(`del:pick:<id>`), номер запиту на завантаження (`net:yes:<req>`), розширення формату (`fmt:yes:<ext>`).
Без прив'язки кнопка «Так» не знала б, на яку зміну вона відповідає, тому голі `chg:yes` відхиляються.
Ліміт Telegram — 64 байти на callback_data.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

# Параметр callback: токен (8 hex), ID запису (12 hex), номер запиту (8 hex) або розширення (a-z0-9).
PARAM_RE = re.compile(r"^[a-z0-9]{1,32}$")
CALLBACK_MAX_BYTES = 64

# (текст кнопки, callback_data-шаблон, хто може натиснути). Шаблон може містити {token}, {req}, {id}, {ext}.
MENUS: Dict[str, List[List[Tuple[str, str, str]]]] = {
    "main": [
        [("📥 Завантажити файл", "up:file", "andrii"), ("🔒 Завантажити з міткою", "up:protected", "andrii")],
        [("🔗 Посилання (з дозволом)", "up:link", "andrii"), ("🏷 Позначити міткою", "lbl:start", "andrii")],
        [("🔓 Зняти мітку", "lbl:offstart", "andrii"), ("🗂 Структура архіву", "tree:show", "andrii")],
        [("✏️ Перезаписати", "edit:start", "andrii"), ("🗑 Видалити", "del:start", "andrii")],
        [("🧭 Розподіл по базах", "route:show", "andrii"), ("🧩 Вивчити новий формат", "fmt:learn", "andrii")],
        [("🎙 Транскрибація", "tr:start", "andrii"), ("🌐 Переклад", "tl:start", "andrii")],
        [("📊 Звіт для Єви", "rep:eva", "andrii"), ("📋 Повний звіт", "rep:full", "andrii")],
    ],
    "confirm_delete": [
        [("✅ Так, видалити (кошик на 30 днів)", "chg:yes:{token}", "andrii"),
         ("❌ Скасувати", "chg:no:{token}", "andrii")],
    ],
    "approve_download": [
        [("✅ Дозволити завантаження", "net:yes:{req}", "andrii"), ("❌ Ні", "net:no:{req}", "andrii")],
    ],
    "approve_change": [
        [("✅ Дозволити зміну", "chg:yes:{token}", "andrii"), ("❌ Заборонити", "chg:no:{token}", "andrii")],
    ],
    "confirm_label_removal": [
        [("✅ Зняти мітку", "lbl:offyes:{id}", "andrii"), ("❌ Залишити", "lbl:offno", "andrii")],
    ],
    "approve_format": [
        [("✅ Вивчити формат", "fmt:yes:{ext}", "andrii"), ("❌ Не треба", "fmt:no:{ext}", "andrii")],
    ],
    "back": [
        [("⬅️ Меню", "menu:main", "andrii")],
    ],
}

# Статичні callback без параметрів.
ACTIONS: Dict[str, Tuple[str, str]] = {
    "up:file": ("upload", "await_file"),
    "up:protected": ("upload", "await_file_protected"),
    "up:link": ("download", "ask_url"),
    "lbl:start": ("label", "pick_unlabeled"),
    "lbl:offstart": ("label", "pick_labeled"),
    "lbl:offno": ("label", "cancel"),
    "tree:show": ("archive", "tree"),
    "edit:start": ("edit", "pick_item"),
    "del:start": ("delete", "pick_item"),
    "route:show": ("route", "show"),
    "tr:start": ("transcribe", "await_media"),
    "tl:start": ("translate", "await_text"),
    "fmt:learn": ("format", "ask_ext"),
    "rep:eva": ("report", "eva"),
    "rep:full": ("report", "full"),
    "menu:main": ("menu", "main"),
}

# Callback з рівно одним параметром: "<голова>:<param>" → (action, arg).
PARAM_ACTIONS: Dict[str, Tuple[str, str]] = {
    "chg:yes": ("change", "confirm"),
    "chg:no": ("change", "reject"),
    "net:yes": ("download", "approve"),
    "net:no": ("download", "reject"),
    "fmt:yes": ("format", "approve"),
    "fmt:no": ("format", "reject"),
    "del:pick": ("delete", "request"),
    "edit:pick": ("edit", "await_file"),
    "lbl:on": ("label", "label"),
    "lbl:off": ("label", "ask_unlabel"),
    "lbl:offyes": ("label", "unlabel"),
}


def build_keyboard(menu: str, sender: str, **params: str) -> dict:
    """Розмітка для Telegram sendMessage(reply_markup=...). Показує лише кнопки, доступні sender.

    Параметри шаблону (token, req, id, ext) передаються іменованими аргументами.
    Якщо параметра немає — помилка, а не кнопка з порожнім ID.
    """
    rows = []
    for row in MENUS[menu]:
        buttons = []
        for text, template, who in row:
            if sender not in who.split(","):
                continue
            cb = template.format(**params)
            if len(cb.encode("utf-8")) > CALLBACK_MAX_BYTES:
                raise ValueError(f"callback_data задовга: {cb!r}")
            buttons.append({"text": text, "callback_data": cb})
        if buttons:
            rows.append(buttons)
    return {"inline_keyboard": rows}


def item_keyboard(head: str, items: Sequence[Tuple[str, str]], back: bool = True) -> dict:
    """Кнопки вибору запису: items = [(rec_id, підпис)]. head — наприклад 'del:pick'."""
    rows: List[List[Dict[str, str]]] = []
    for rec_id, label in items:
        cb = f"{head}:{rec_id}"
        if not PARAM_RE.match(rec_id) or len(cb.encode("utf-8")) > CALLBACK_MAX_BYTES:
            raise ValueError(f"некоректний ID для callback: {rec_id!r}")
        rows.append([{"text": label[:60], "callback_data": cb}])
    if back:
        rows.append([{"text": "⬅️ Меню", "callback_data": "menu:main"}])
    return {"inline_keyboard": rows}


def parse_callback(data: str) -> Optional[Dict[str, Any]]:
    """Розбір callback_data. None — невідома кнопка або підроблений параметр."""
    if not isinstance(data, str) or len(data.encode("utf-8")) > CALLBACK_MAX_BYTES:
        return None
    if data in ACTIONS:
        action, arg = ACTIONS[data]
        return {"action": action, "arg": arg, "callback": data, "param": None}
    head, sep, param = data.rpartition(":")
    if not sep or head not in PARAM_ACTIONS or not PARAM_RE.match(param):
        return None
    action, arg = PARAM_ACTIONS[head]
    return {"action": action, "arg": arg, "callback": data, "param": param}


def handle_callback(data: str, sender: str) -> Optional[dict]:
    """Лише Андрій. Інші відправники й невідомі callback — None (нічого не виконується)."""
    if sender != "andrii":
        return None
    return parse_callback(data)
