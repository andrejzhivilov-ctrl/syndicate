"""Єва — кошики продуктів (Сільпо, АТБ, Varus, Ашан ...). Чистий Python, без мережі.

Що тут є:
- реєстр мереж і чесний статус доступу (за замовчуванням не підключено);
- критерій здоров'я (мало цукру, мало жиру, помірно вуглеводів) — лише коли є дані;
- пошук дешевших альтернатив у іншій мережі з нутрієнтами не гірше за початковий товар;
- пропозиція кошика, що чекає підтвердження Андрія. Замовлення тут неможливе.

Самі мережі опитуються браузерним воркером у n8n (окремий дозвіл при розгортанні). Тут
лише логіка над уже отриманими даними.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional

# ---------------------------------------------------------------- мережі
# status: not_connected — жодних звернень. Підключення — окремий дозвіл при розгортанні.
RETAILERS: Dict[str, Dict[str, str]] = {
    "silpo": {
        "label": "Сільпо", "status": "not_connected", "mode": "browser_worker_n8n",
        "cart": "можливий через обліковий запис користувача",
        "risk": "внутрішній API не публічний; умови користування і облікові дані перевірити до підключення",
    },
    "atb": {
        "label": "АТБ", "status": "not_connected", "mode": "browser_worker_n8n",
        "cart": "можливий через обліковий запис користувача (zakaz.atbmarket.com)",
        "risk": "сайт був на технічних роботах під час перевірки; підключення — після стабілізації",
    },
    "varus": {
        "label": "Varus", "status": "not_connected", "mode": "browser_worker_n8n",
        "cart": "відкритий API дає лише акції і магазини, кошика немає",
        "risk": "для кошика — лише браузерний воркер",
    },
    "auchan": {
        "label": "Ашан", "status": "not_connected", "mode": "browser_worker_n8n",
        "cart": "не перевірено",
        "risk": "не перевірено",
    },
}

# ---------------------------------------------------------------- нутрієнти
# Проєктні пороги на 100 г. ПОТРЕБУЮТЬ ПІДТВЕРДЖЕННЯ АНДРІЄМ (він сказав «мало», а не цифри).
NUTRITION_LIMITS_PER_100G: Dict[str, Decimal] = {
    "sugar_g": Decimal("5"),
    "fat_g": Decimal("5"),
    "carbs_g": Decimal("20"),
}
# Вага у сумарному балі: цукор важить найбільше, бо це головна вимога.
NUTRITION_WEIGHTS: Dict[str, Decimal] = {
    "sugar_g": Decimal("1.5"),
    "fat_g": Decimal("1.0"),
    "carbs_g": Decimal("0.5"),
}


def nutrition_score(nutrition: Optional[Dict[str, Any]]) -> Optional[Decimal]:
    """Менше = краще. None, якщо бракує будь-якого з трьох показників (нічого не вигадуємо)."""
    if not nutrition:
        return None
    total = Decimal("0")
    for key, weight in NUTRITION_WEIGHTS.items():
        if nutrition.get(key) is None:
            return None
        total += Decimal(str(nutrition[key])) * weight
    return total.quantize(Decimal("0.01"))


def within_limits(nutrition: Optional[Dict[str, Any]]) -> Optional[bool]:
    """True/False за порогами; None — даних немає."""
    if not nutrition or any(nutrition.get(k) is None for k in NUTRITION_LIMITS_PER_100G):
        return None
    return all(Decimal(str(nutrition[k])) <= lim for k, lim in NUTRITION_LIMITS_PER_100G.items())


def cheaper_alternatives(item: Dict[str, Any], candidates: Iterable[Dict[str, Any]],
                         max_items: int = 3) -> List[Dict[str, Any]]:
    """Дешевші альтернативи в іншій мережі, які не гірші за товар по нутрієнтах.

    item/candidate: {"name", "category", "price", "retailer", "nutrition": {...}}.
    Товари без повних нутрієнтів не пропонуються як «не гірші» — позначаємо окремо.
    """
    base_price = Decimal(str(item["price"]))
    base_score = nutrition_score(item.get("nutrition"))
    out = []
    for c in candidates:
        if c.get("category") != item.get("category") or c.get("retailer") == item.get("retailer"):
            continue
        price = Decimal(str(c["price"]))
        if price >= base_price:
            continue
        score = nutrition_score(c.get("nutrition"))
        if score is None or base_score is None:
            out.append({"name": c["name"], "retailer": c["retailer"], "price": str(price),
                        "saving": str(base_price - price), "nutrition_check": "unknown",
                        "advisory_only": True})
            continue
        if score > base_score:
            continue  # гірший склад — не пропонуємо
        out.append({"name": c["name"], "retailer": c["retailer"], "price": str(price),
                    "saving": str(base_price - price), "score": str(score),
                    "nutrition_check": "not_worse", "advisory_only": True})
    known = [o for o in out if o["nutrition_check"] == "not_worse"]
    unknown = [o for o in out if o["nutrition_check"] == "unknown"]
    known.sort(key=lambda o: (Decimal(o["score"]), Decimal(o["price"])))
    unknown.sort(key=lambda o: Decimal(o["price"]))
    return (known + unknown)[:max_items]


def build_basket_proposal(retailer: str, items: List[Dict[str, Any]],
                          requested_by: str = "eva") -> Dict[str, Any]:
    """Пропозиція кошика для підтвердження Андрієм. Замовлення не створює."""
    if retailer not in RETAILERS:
        return {"type": "basket_proposal", "status": "rejected", "reason": "unknown_retailer"}
    if not items:
        return {"type": "basket_proposal", "status": "rejected", "reason": "empty_basket"}
    total = Decimal("0")
    rows = []
    for it in items:
        qty = int(it.get("qty", 1))
        if qty <= 0:
            return {"type": "basket_proposal", "status": "rejected", "reason": "bad_qty"}
        price = Decimal(str(it["price"]))
        total += price * qty
        score = nutrition_score(it.get("nutrition"))
        rows.append({"name": it["name"], "qty": qty, "price": str(price),
                     "nutrition_check": within_limits(it.get("nutrition")),
                     "score": None if score is None else str(score)})
    return {
        "type": "basket_proposal",
        "from": "eva", "to": "andrii", "requested_by": requested_by,
        "retailer": retailer, "retailer_status": RETAILERS[retailer]["status"],
        "items": rows, "total": str(total.quantize(Decimal("0.01"))),
        "status": "awaiting_andrii_confirmation",
        "evidence": None,            # сюди — скрін або посилання після браузерного воркера
        "order_allowed": False,      # замовлення робить Андрій сам
    }


def attach_evidence(proposal: Dict[str, Any], screenshot_path: Optional[str] = None,
                    cart_url: Optional[str] = None) -> Dict[str, Any]:
    """Додає скрін або посилання на кошик. Жодних змін статусу замовлення."""
    if proposal.get("type") != "basket_proposal" or proposal.get("status") == "rejected":
        return proposal
    if not screenshot_path and not cart_url:
        return proposal
    return {**proposal, "evidence": {"screenshot": screenshot_path, "cart_url": cart_url}}
