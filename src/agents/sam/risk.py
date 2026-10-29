"""Deterministic risk module: the model gives a direction and strength, code sizes the trade.

Operator decision 29.10 (from the Sam dossier): a language model never sets an
absolute order size. It returns a normalised signal in [-1, +1] with reasons;
this module turns it into units from equity, volatility (ATR) and hard limits:

* risk per trade at most ``MAX_RISK_PER_TRADE`` of equity, scaled by |strength|;
* stop distance = ``ATR_MULTIPLE`` x ATR, so volatile markets get smaller size;
* notional per asset at most 5% (single stocks) or 10% (everything else) of equity;
* no new risk once the day's drawdown reaches ``MAX_DAILY_DRAWDOWN``.

The result is still only a proposal for Andrii's approval.
"""
from __future__ import annotations

import math
from decimal import ROUND_DOWN, Decimal
from typing import Any, Dict, Mapping

MAX_RISK_PER_TRADE = 0.01
MAX_DAILY_DRAWDOWN = 0.02
ATR_MULTIPLE = 2.0
ASSET_CAP = {"equity": 0.05}
DEFAULT_ASSET_CAP = 0.10
#: Fields a model must never set: sizing is this module's job.
FORBIDDEN_MODEL_FIELDS = frozenset({"quantity", "qty", "units", "lots", "size", "notional", "position_size",
                                    "contracts", "leverage"})


def _num(value: Any, name: str, low: float = 0.0, high: float = math.inf, *, strict_low: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"invalid_{name}")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"invalid_{name}") from None
    if not math.isfinite(result) or result > high or result < low or (strict_low and result == low):
        raise ValueError(f"invalid_{name}")
    return result


def model_signal(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate what a model may say: direction via sign of strength, plus reasons."""
    if FORBIDDEN_MODEL_FIELDS & set(payload):
        raise ValueError("model_cannot_size_orders")
    strength = _num(payload.get("strength"), "strength", -1.0, 1.0)
    rationale = payload.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError("rationale_required")
    return {"strength": strength, "direction": "long" if strength > 0 else "short" if strength < 0 else "flat",
            "rationale": rationale.strip()[:2000]}


def daily_guard(equity_start: float, equity_now: float, limit: float = MAX_DAILY_DRAWDOWN) -> Dict[str, Any]:
    start = _num(equity_start, "equity_start", 0.0, strict_low=True)
    now = _num(equity_now, "equity_now", 0.0)
    drawdown = max(0.0, (start - now) / start)
    return {"drawdown": drawdown, "limit": limit, "blocked": drawdown >= limit}


def position_size(signal: Mapping[str, Any], *, equity: float, equity_start_of_day: float, price: float,
                  atr: float, asset_class: str = "other", contract_multiplier: float = 1.0,
                  lot_step: float = 1.0) -> Dict[str, Any]:
    """Units for one proposal, or a blocked result with the reason. Raises on bad inputs."""
    sig = model_signal(signal)
    equity = _num(equity, "equity", 0.0, strict_low=True)
    price = _num(price, "price", 0.0, strict_low=True)
    atr = _num(atr, "atr", 0.0, strict_low=True)
    multiplier = _num(contract_multiplier, "contract_multiplier", 0.0, strict_low=True)
    step = _num(lot_step, "lot_step", 0.0, strict_low=True)
    guard = daily_guard(equity_start_of_day, equity)
    base = {"direction": sig["direction"], "strength": sig["strength"], "rationale": sig["rationale"],
            "daily_drawdown": guard["drawdown"], "requires_hitl": True, "auto_execute": False}
    if guard["blocked"]:
        return {**base, "status": "blocked", "reason": "daily_drawdown_limit", "units": 0}
    if sig["direction"] == "flat":
        return {**base, "status": "blocked", "reason": "no_direction", "units": 0}
    risk_budget = equity * MAX_RISK_PER_TRADE * abs(sig["strength"])
    stop_distance = ATR_MULTIPLE * atr
    by_risk = risk_budget / (stop_distance * multiplier)
    cap = ASSET_CAP.get(asset_class, DEFAULT_ASSET_CAP)
    by_cap = equity * cap / (price * multiplier)
    raw = min(by_risk, by_cap)
    units = float((Decimal(str(raw)) / Decimal(str(step))).to_integral_value(rounding=ROUND_DOWN) * Decimal(str(step)))
    if units <= 0:
        return {**base, "status": "blocked", "reason": "below_minimum_lot", "units": 0}
    stop = price - stop_distance if sig["direction"] == "long" else price + stop_distance
    return {**base, "status": "ok", "units": units, "entry": price, "stop": stop,
            "risk_amount": units * stop_distance * multiplier, "notional": units * price * multiplier,
            "asset_cap": cap, "limited_by": "asset_cap" if by_cap < by_risk else "risk"}
