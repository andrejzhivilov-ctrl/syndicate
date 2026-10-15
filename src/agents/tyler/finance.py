"""Decimal unit economics including payment fees, tax and landed costs."""
from decimal import Decimal, InvalidOperation, ROUND_CEILING

CENT = Decimal("0.01")
MIN_MARGIN = Decimal("0.35")
PREMIUM_BLANKS = frozenset({"bella_canvas_3001", "comfort_colors_1717", "stanley_stella", "orka_coatings"})


def money(value, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"invalid_{name}")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"invalid_{name}") from exc
    if not result.is_finite() or result < 0 or result > Decimal("1000000"):
        raise ValueError(f"invalid_{name}")
    if result != result.quantize(CENT):
        raise ValueError("money_requires_minor_units")
    return result


def calculate_margin(payload: dict) -> dict:
    price = money(payload["price"], "price")
    if price <= 0:
        raise ValueError("price_must_be_positive")
    currency = payload["currency"]
    if currency != "USD":
        raise ValueError("stripe_fee_schedule_requires_usd")
    costs = {key: money(payload[key], key) for key in ("blank", "print", "shipping", "tax")}
    # Round fees upward so a fractional cent cannot accidentally clear the gate.
    fee = (price * Decimal("0.029") + Decimal("0.30")).quantize(CENT, rounding=ROUND_CEILING)
    total = sum(costs.values()) + fee
    profit = price - total
    margin = profit / price
    minimum_price = ((sum(costs.values()) + Decimal("0.30")) /
                     (1 - MIN_MARGIN - Decimal("0.029"))).quantize(CENT, rounding=ROUND_CEILING)
    # Recheck rounded fees at the suggested price.
    while (minimum_price - sum(costs.values()) -
           (minimum_price * Decimal("0.029") + Decimal("0.30")).quantize(CENT, rounding=ROUND_CEILING)) / minimum_price < MIN_MARGIN:
        minimum_price += CENT
    return {"status": "ok" if margin >= MIN_MARGIN else "blocked", "currency": currency,
            "price": str(price), "costs": {key: str(value) for key, value in costs.items()},
            "payment_fee": str(fee), "net_profit": str(profit), "net_margin": str(margin),
            "minimum_price": str(minimum_price), "minimum_margin": str(MIN_MARGIN),
            "eligible": margin >= MIN_MARGIN, "source_mode": "supplied_costs",
            "warning": "Quote depends on supplied costs and USD Stripe schedule; revalidate before fulfillment"}
