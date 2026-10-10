"""Док — нагадування про добавки і показання цифрами. Детерміновано.

Слоти: щодня о 13:10 і о 19:10 (Europe/Kyiv). Розклад і сам список добавок — ваші, задаються в
конфігурації. Без списку добавок нагадування не вигадуються.
Пороги зон і цифри затверджуються окремо (досьє: «показання цифрами, пороги затвердимо»).
"""

from __future__ import annotations

from datetime import datetime, time
from typing import Any, Dict, Iterable, List, Optional, Set
from zoneinfo import ZoneInfo

KYIV = ZoneInfo("Europe/Kyiv")
DAILY_SLOTS = (time(13, 10), time(19, 10))
SLOT_LABELS = {time(13, 10): "13:10", time(19, 10): "19:10"}


def due_slots(now: datetime, sent_today: Iterable[str], slots=DAILY_SLOTS) -> List[str]:
    """Слоти, які вже настали сьогодні і ще не відправлені. `now` — з tzinfo або наївний (Kyiv)."""
    local = now.astimezone(KYIV) if now.tzinfo else now.replace(tzinfo=KYIV)
    done = set(sent_today)
    out = []
    for slot in slots:
        label = SLOT_LABELS[slot]
        if local.time() >= slot and label not in done:
            out.append(label)
    return out


def reminder_text(supplements: List[Dict[str, Any]], slot_label: str) -> Dict[str, Any]:
    """Текст нагадування. Порожній список — нічого не надсилається й не вигадується."""
    items = [s for s in supplements if slot_label in s.get("slots", [])]
    if not supplements:
        return {"status": "not_configured", "message": "Список добавок не задано."}
    if not items:
        return {"status": "nothing_scheduled", "slot": slot_label}
    lines = [f"💊 Добавки о {slot_label}:"]
    for s in items:
        note = s.get("timing", "")
        lines.append(f"• {s['name']} — {s.get('dose', '?')}{(', ' + note) if note else ''}")
    return {"status": "ok", "slot": slot_label, "text": "\n".join(lines),
            "buttons": ["sup:taken", "sup:snooze"]}


def format_metric(name: str, value: Optional[float], unit: str, zone: Optional[str] = None,
                  show_numbers: bool = True) -> str:
    """Показання цифрами (за замовчуванням). Зона — лише як доповнення, без заміни числа."""
    if value is None:
        return f"{name}: немає даних"
    if not show_numbers:
        return f"{name}: {zone or 'немає зони'}"
    base = f"{name}: {value:g} {unit}"
    return f"{base} ({zone})" if zone else base


def validate_supplement(s: Dict[str, Any], allowed_slots: Set[str]) -> Optional[str]:
    if not s.get("name") or not s.get("dose"):
        return "missing_name_or_dose"
    if any(slot not in allowed_slots for slot in s.get("slots", [])):
        return "unknown_slot"
    if s.get("interaction_check") != "done":
        return "interaction_check_pending"
    return None
