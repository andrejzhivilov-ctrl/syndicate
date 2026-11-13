"""Док — список продуктів для Єви і нутрієнтний критерій (власник: Док).

Док має вихід в інтернет і базу рецептів/знань: він складає список потрібних продуктів і
кількості. Єва отримує список і, якщо зможе, формує кошик (або Андрій сам).
Чистий Python: нічого не замовляє, нікуди не пише, мережі не викликає.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional

# Нутрієнтний критерій належить Доку. Значення — ПРОЄКТНІ, до затвердження Доком/Андрієм.
NUTRITION_OWNER = "doc"
NUTRITION_LIMITS_PER_100G: Dict[str, Decimal] = {
    "sugar_g": Decimal("5"),
    "fat_g": Decimal("5"),
    "carbs_g": Decimal("20"),
}
NUTRITION_WEIGHTS: Dict[str, Decimal] = {
    "sugar_g": Decimal("1.5"),
    "fat_g": Decimal("1.0"),
    "carbs_g": Decimal("0.5"),
}
FOOD_CATEGORIES = frozenset({"vegetables", "fruits", "dairy", "meat", "fish", "eggs",
                             "grains", "bakery", "pantry", "drinks", "other"})


def nutrition_score(nutrition: Optional[Dict[str, Any]]) -> Optional[Decimal]:
    """Менше = краще. None, якщо бракує будь-якого з трьох показників."""
    if not nutrition:
        return None
    total = Decimal("0")
    for key, weight in NUTRITION_WEIGHTS.items():
        if nutrition.get(key) is None:
            return None
        total += Decimal(str(nutrition[key])) * weight
    return total.quantize(Decimal("0.01"))


def within_limits(nutrition: Optional[Dict[str, Any]]) -> Optional[bool]:
    """True/False за порогами; None — даних немає (нічого не вигадуємо)."""
    if not nutrition or any(nutrition.get(k) is None for k in NUTRITION_LIMITS_PER_100G):
        return None
    return all(Decimal(str(nutrition[k])) <= lim for k, lim in NUTRITION_LIMITS_PER_100G.items())


def build_shopping_list(items: Iterable[Dict[str, Any]], meal_plan_ref: Optional[str] = None) -> Dict[str, Any]:
    """Список для Єви. Кожен рядок: назва, кількість, одиниця, категорія, перевірка складу."""
    rows: List[Dict[str, Any]] = []
    for it in items:
        name = str(it.get("name", "")).strip()
        if not name:
            return {"type": "shopping_list", "from": "doc", "to": "eva", "status": "rejected",
                    "reason": "empty_name"}
        try:
            qty = Decimal(str(it.get("qty", 1)))
        except Exception:  # noqa: BLE001
            return {"type": "shopping_list", "from": "doc", "to": "eva", "status": "rejected",
                    "reason": "bad_qty"}
        if qty <= 0:
            return {"type": "shopping_list", "from": "doc", "to": "eva", "status": "rejected",
                    "reason": "bad_qty"}
        category = it.get("category", "other")
        if category not in FOOD_CATEGORIES:
            return {"type": "shopping_list", "from": "doc", "to": "eva", "status": "rejected",
                    "reason": "unknown_category", "item": name}
        rows.append({"name": name, "qty": str(qty), "unit": it.get("unit", "шт"),
                     "category": category,
                     "nutrition_check": within_limits(it.get("nutrition")),
                     "score": None if nutrition_score(it.get("nutrition")) is None
                     else str(nutrition_score(it.get("nutrition")))})
    if not rows:
        return {"type": "shopping_list", "from": "doc", "to": "eva", "status": "rejected",
                "reason": "empty_list"}
    return {"type": "shopping_list", "from": "doc", "to": "eva", "status": "ready_for_eva",
            "meal_plan_ref": meal_plan_ref, "items": rows,
            "nutrition_owner": NUTRITION_OWNER,
            "order_allowed": False}
