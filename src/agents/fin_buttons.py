"""Fin — інтерактивні кнопки (Telegram inline keyboard). Лише побудова розмітки й розбір callback.

Жодного мережевого виклику. Розмітка віддається наверх; відправку зробить бот після
окремого дозволу (fin.telegram.bot). Текст мовою користувача, без голосового виходу.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from src.agents.fin_ledger import route_allowed

# callback_data обмежена 64 байтами Telegram — тримаємо короткі коди.
MENUS: Dict[str, List[List[Tuple[str, str, str]]]] = {
    # (текст кнопки, callback, хто може натиснути)
    "main": [
        [("📊 ЗВІТ — повний фінансовий", "rep:full", "andrii")],
        [("📅 Стандартний звіт", "rep:standard", "andrii,eva"),
         ("🗓 Плани платежів", "plan:all", "andrii,eva")],
        [("🛒 Перевірити кошик", "funds:basket", "eva"),
         ("💰 Кошти і джерела", "funds:sources", "andrii,eva")],
        [("✅ Записати витрату", "exp:new", "andrii,eva")],
    ],
    "report": [
        [("📊 Повний", "rep:full", "andrii"), ("📅 День", "rep:day", "andrii,eva")],
        [("📅 Тиждень", "rep:week", "andrii,eva"), ("📅 Місяць", "rep:month", "andrii,eva")],
        [("⬅️ Назад", "menu:main", "andrii,eva")],
    ],
    "export": [
        [("PDF", "exp:pdf", "andrii"), ("DOCX", "exp:docx", "andrii")],
        [("XLSX", "exp:xlsx", "andrii"), ("PPTX", "exp:pptx", "andrii")],
        [("Obsidian (.md)", "exp:obsidian", "andrii")],
    ],
}

ACTIONS = {
    "rep:full": ("report", "full"),
    "rep:standard": ("report", "standard"),
    "rep:day": ("report", "day"),
    "rep:week": ("report", "week"),
    "rep:month": ("report", "month"),
    "plan:all": ("plan", "all"),
    "funds:basket": ("funds_check", "basket"),
    "funds:sources": ("sources", "all"),
    "exp:new": ("expense_note", "new"),
    "exp:pdf": ("export", "pdf"),
    "exp:docx": ("export", "docx"),
    "exp:xlsx": ("export", "xlsx"),
    "exp:pptx": ("export", "pptx"),
    "exp:obsidian": ("export", "obsidian"),
    "menu:main": ("menu", "main"),
}


def build_keyboard(menu: str, sender: str) -> dict:
    """Розмітка для Telegram sendMessage(reply_markup=...). Показує лише кнопки, доступні sender."""
    rows = []
    for row in MENUS[menu]:
        buttons = [{"text": text, "callback_data": cb}
                   for text, cb, who in row if sender in who.split(",")]
        if buttons:
            rows.append(buttons)
    return {"inline_keyboard": rows}


def handle_callback(data: str, sender: str) -> Optional[dict]:
    """Розбір натискання. None — невідома кнопка або немає доступу."""
    if data not in ACTIONS:
        return None
    msg_type_map = {"report": "report_request", "plan": "report_request",
                    "funds_check": "funds_check", "sources": "basket_status",
                    "expense_note": "expense_note", "export": "report_request",
                    "menu": "report_request"}
    action, arg = ACTIONS[data]
    if not route_allowed(sender, msg_type_map[action]):
        return None
    # Повний звіт — лише Андрій.
    if data == "rep:full" and sender != "andrii":
        return None
    return {"action": action, "arg": arg, "callback": data}
