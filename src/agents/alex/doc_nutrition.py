"""Док — розрахунок енергії й КБЖУ (Mifflin-St Jeor). Детерміновано, без LLM.

Якщо немає даних профілю (вага, зріст, вік, стать, активність) — повертає `not_configured`.
Ніяких «типових» значень не підставляємо: це правило безпеки Дока.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, Optional

ACTIVITY_FACTORS: Dict[str, Decimal] = {
    "sedentary": Decimal("1.2"),
    "light": Decimal("1.375"),
    "moderate": Decimal("1.55"),
    "active": Decimal("1.725"),
    "very_active": Decimal("1.9"),
}
PROTEIN_G_PER_KG = Decimal("2.0")
FAT_G_PER_KG = Decimal("1.0")
WATER_ML_PER_KG = Decimal("35")
KCAL_PER_G = {"protein": Decimal("4"), "fat": Decimal("9"), "carb": Decimal("4")}
REQUIRED_FIELDS = ("weight_kg", "height_cm", "age", "sex", "activity")


def _missing(profile: Dict[str, Any]) -> list:
    return [f for f in REQUIRED_FIELDS if profile.get(f) in (None, "")]


def bmr_mifflin_st_jeor(weight_kg: Decimal, height_cm: Decimal, age: int, sex: str) -> Decimal:
    base = Decimal("10") * weight_kg + Decimal("6.25") * height_cm - Decimal("5") * Decimal(age)
    if sex == "male":
        return (base + Decimal("5")).quantize(Decimal("1"))
    if sex == "female":
        return (base - Decimal("161")).quantize(Decimal("1"))
    raise ValueError("sex must be 'male' or 'female'")


def energy_and_macros(profile: Dict[str, Any]) -> Dict[str, Any]:
    """BMR, TDEE, КБЖУ та вода за профілем. Без даних — `not_configured` з переліком полів."""
    missing = _missing(profile)
    if missing:
        return {"agent": "doc", "status": "not_configured", "missing": missing,
                "message": "Потрібні дані профілю. Вигадувати не буду."}
    if profile["activity"] not in ACTIVITY_FACTORS:
        return {"agent": "doc", "status": "rejected", "reason": "unknown_activity"}
    try:
        weight = Decimal(str(profile["weight_kg"]))
        height = Decimal(str(profile["height_cm"]))
        age = int(profile["age"])
        bmr = bmr_mifflin_st_jeor(weight, height, age, profile["sex"])
    except (ValueError, ArithmeticError) as exc:
        return {"agent": "doc", "status": "rejected", "reason": f"bad_input:{exc}"}
    tdee = (bmr * ACTIVITY_FACTORS[profile["activity"]]).quantize(Decimal("1"))
    protein = (PROTEIN_G_PER_KG * weight).quantize(Decimal("1"))
    fat = (FAT_G_PER_KG * weight).quantize(Decimal("1"))
    carb_kcal = tdee - protein * KCAL_PER_G["protein"] - fat * KCAL_PER_G["fat"]
    carbs = max(Decimal("0"), (carb_kcal / KCAL_PER_G["carb"])).quantize(Decimal("1"))
    return {
        "agent": "doc", "status": "ok", "bmr_kcal": str(bmr), "tdee_kcal": str(tdee),
        "protein_g": str(protein), "fat_g": str(fat), "carb_g": str(carbs),
        "water_ml": str((WATER_ML_PER_KG * weight).quantize(Decimal("1"))),
        "note": "Оцінка для планування, не діагноз. Формула: Mifflin-St Jeor × коефіцієнт активності.",
    }


def readiness_zone(score: Optional[float]) -> str:
    """Зони готовності за досьє: зелена 70–100, жовта 45–69, червона <45. None → без оцінки."""
    if score is None:
        return "not_configured"
    if score >= 70:
        return "green"
    if score >= 45:
        return "yellow"
    return "red"
