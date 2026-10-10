"""Fin — детерміновані правила (чистий Python, без мережі, без банків, без LLM).

Нічого тут не виконує платежів. Функції лише рахують і повертають рекомендацію.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Optional

GREEN_MONTHS = Decimal("6")
YELLOW_MONTHS = Decimal("3")
TOKEN_DAILY_LIMIT_USD = Decimal("5.00")
TOKEN_WARN_RATIO = Decimal("0.80")
TOKEN_SPIKE_USD_15M = Decimal("0.50")
FX_DAILY_MOVE_PCT = Decimal("1.5")
SAFETY_FUND = "safety"


def runway_months(liquid: Decimal, burn_3m: Iterable[Decimal]) -> Optional[Decimal]:
    """Runway = чистий ліквідний капітал / середній місячний burn за 3 міс."""
    values = [Decimal(str(v)) for v in burn_3m]
    if len(values) != 3:
        return None
    avg = sum(values, Decimal("0")) / Decimal("3")
    if avg <= 0:
        return None
    return (Decimal(str(liquid)) / avg).quantize(Decimal("0.1"))


def runway_zone(months: Optional[Decimal]) -> str:
    """Зони: green >6, yellow 3–6, red <3. Без даних — 'undefined' (не вигадуємо)."""
    if months is None:
        return "undefined"
    if months > GREEN_MONTHS:
        return "green"
    if months >= YELLOW_MONTHS:
        return "yellow"
    return "red"


def reconcile_receipt(items: Iterable[Decimal], fiscal_total: Decimal,
                      bank_amount: Optional[Decimal] = None) -> dict:
    """Самозвірка: сума позицій = ПІДСУМОК; якщо є виписка — ще й з банком.

    Будь-яка ненульова різниця (хоча б 1 копійка) → 'unreconciled'.
    """
    total = sum((Decimal(str(i)) for i in items), Decimal("0"))
    fiscal = Decimal(str(fiscal_total))
    diff_items = (total - fiscal).copy_abs()
    if diff_items != 0:
        return {"status": "unreconciled", "reason": "items_vs_fiscal_total", "diff": str(diff_items)}
    if bank_amount is None:
        return {"status": "bank_pending", "reason": "no_bank_statement_yet"}
    diff_bank = (fiscal - Decimal(str(bank_amount))).copy_abs()
    if diff_bank != 0:
        return {"status": "unreconciled", "reason": "receipt_vs_bank", "diff": str(diff_bank)}
    return {"status": "reconciled", "reason": "ok"}


def basket_audit(total: Decimal, category_left: Optional[Decimal]) -> dict:
    """Аудит кошика — ЛИШЕ рекомендація. Ніяких списань, ніяких замовлень."""
    if category_left is None:
        return {"decision": "hold", "reason": "no_category_budget_data", "advisory_only": True}
    t = Decimal(str(total))
    left = Decimal(str(category_left))
    if t <= left:
        return {"decision": "within_budget", "reason": "fits_category_limit", "advisory_only": True}
    return {"decision": "over_budget", "reason": "exceeds_category_limit",
            "shortfall": str(t - left), "advisory_only": True}


def allocate_purchase(amount: Decimal, category: str, fund_left: dict,
                      purpose: str, next_period_ok: bool = True) -> dict:
    """Рекомендація виділення коштів під покупку (потік Єва → Фін). Без платежів.

    fund_left, напр. {"consumables": 800, "rest": 300, "goals": 0, "safety": 9000}.
    Фонд Безпеки недоторканний — ніколи не джерело покупки.
    """
    amt = Decimal(str(amount))
    funds = {k: Decimal(str(v)) for k, v in fund_left.items()}
    order = ["consumables"] if category == "food" else ["rest", "goals"]
    for fund in order:
        if funds.get(fund, Decimal("0")) >= amt:
            return {"status": "funds_allocated", "allowed_amount": str(amt), "source_fund": fund,
                    "purpose": purpose, "advisory_only": True}
    if next_period_ok:
        return {"status": "next_period", "reason": "not_planned_this_period",
                "purpose": purpose, "advisory_only": True}
    blocked = funds.get(SAFETY_FUND, Decimal("0")) >= amt
    return {"status": "reserve_blocked" if blocked else "over_budget",
            "purpose": purpose, "advisory_only": True}


def token_guard(spent_usd_day: Decimal, spent_usd_15m: Decimal = Decimal("0")) -> dict:
    """Ліміт токенів $5/добу. 80% — попередження; >$0.50 за 15 хв — сигнал Маршалу."""
    ratio = Decimal(str(spent_usd_day)) / TOKEN_DAILY_LIMIT_USD
    spike = Decimal(str(spent_usd_15m))
    if spike > TOKEN_SPIKE_USD_15M:
        level = "circuit_signal"
    elif ratio >= Decimal("1"):
        level = "over"
    elif ratio >= TOKEN_WARN_RATIO:
        level = "warn"
    else:
        level = "ok"
    return {
        "level": level,
        "ratio": str(ratio.quantize(Decimal("0.01"))),
        "switch_to_cheap_models": level in {"warn", "over", "circuit_signal"},
        "notify_marshal": level == "circuit_signal",
    }


def fx_move_alert(prev_rate: Decimal, new_rate: Decimal) -> dict:
    """Добовий стрибок курсу >1.5% — рекомендація, не торгова дія."""
    prev = Decimal(str(prev_rate))
    new = Decimal(str(new_rate))
    if prev <= 0:
        return {"alert": False, "reason": "invalid_prev_rate"}
    pct = ((new - prev) / prev * Decimal("100")).copy_abs()
    return {"alert": pct > FX_DAILY_MOVE_PCT, "move_pct": str(pct.quantize(Decimal("0.01")))}
