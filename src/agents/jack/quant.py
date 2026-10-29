"""+EV threshold and fractional Kelly capped per event, including open exposure.

Edge validation (operator decision 29.10):

* the margin is removed by the proportional, power or Shin method; Shin is the
  default for a sharp benchmark because books load more margin on longshots;
* an EV above ``PALPABLE_EV`` is not "great value" but a suspected palpable
  error or stale line: blocked and sent for a manual check;
* a language model may only *weigh qualitative factors* (injuries, rotation,
  motivation): each adjustment is bounded, sourced and returned in the result,
  never a free-form "who wins" prediction;
* the stake is always quarter Kelly capped per event; a caller cannot supply a
  stake or a progression, so a martingale is impossible by construction.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN

from src.agents.director_base import number, text, utc_now

EV_THRESHOLD = Decimal("0.045")
PALPABLE_EV = Decimal("0.20")
KELLY_MULTIPLIER = 0.25
MAX_ADJUSTMENT = 0.03          # one qualitative factor moves the probability by at most 3 points
MAX_TOTAL_ADJUSTMENT = 0.05    # all factors together: at most 5 points
MAX_ADJUSTMENTS = 5
DEVIG_METHODS = ("proportional", "power", "shin")
#: Fields that would let a caller size or escalate a stake (martingale, "догон").
FORBIDDEN_STAKE_FIELDS = frozenset({"stake", "stake_override", "progression", "martingale", "multiplier"})


def _adjust(probability: float, adjustments: object) -> tuple[float, list[dict]]:
    """Apply sourced deltas in Decimal, so 0.55 + 0.02 + 0.03 is exactly 0.60 (no EV boundary drift)."""
    if adjustments in (None, []):
        return probability, []
    if not isinstance(adjustments, list) or len(adjustments) > MAX_ADJUSTMENTS:
        raise ValueError("invalid_adjustments")
    applied = []
    for item in adjustments:
        if not isinstance(item, dict):
            raise ValueError("invalid_adjustments")
        delta = number(item.get("delta"), "adjustment_delta", -MAX_ADJUSTMENT, MAX_ADJUSTMENT)
        applied.append({"factor": text(item.get("factor"), "adjustment_factor", 200), "delta": delta,
                        "source": text(item.get("source"), "adjustment_source", 500)})
    total = sum((Decimal(str(a["delta"])) for a in applied), Decimal("0"))
    if abs(total) > Decimal(str(MAX_TOTAL_ADJUSTMENT)):
        raise ValueError("adjustments_exceed_total_bound")
    adjusted = Decimal(str(probability)) + total
    return float(min(Decimal("0.999"), max(Decimal("0.001"), adjusted))), applied


def evaluate(payload: dict, *, risk_cap: float = 0.01) -> dict:
    forbidden = FORBIDDEN_STAKE_FIELDS & set(payload)
    if forbidden:
        raise ValueError("manual_stake_or_progression_forbidden")
    probability = number(payload["probability"], "probability", 0, 1)
    probability, adjustments = _adjust(probability, payload.get("adjustments"))
    odds = number(payload["decimal_odds"], "decimal_odds", 1.000001, 10000)
    bankroll = number(payload["bankroll"], "bankroll", 0.01, 1e12)
    cap = number(risk_cap, "risk_cap", 0.000001, 0.025)
    observed = datetime.fromisoformat(payload["observed_at"])
    if observed.tzinfo is None:
        raise ValueError("odds_time_must_be_aware")
    age = (utc_now() - observed.astimezone(timezone.utc)).total_seconds()
    if age < -5 or age > 600:
        return {"status": "blocked", "reason": "stale_or_future_odds", "eligible": False}
    model_source = text(payload["model_source"], "model_source", 1000)
    exact_ev = Decimal(str(probability)) * Decimal(str(odds)) - 1
    ev = float(exact_ev)
    if exact_ev > PALPABLE_EV:
        return {"status": "blocked", "eligible": False, "reason": "suspected_palpable_error_or_stale_line",
                "ev": ev, "decimal_odds": odds, "probability": probability, "adjustments": adjustments,
                "requires_manual_check": True, "real_bet_placed": False}
    full_kelly = max(0, ev / (odds - 1))
    fraction = min(cap, KELLY_MULTIPLIER * full_kelly)
    eligible = exact_ev >= EV_THRESHOLD and fraction > 0
    return {"status": "ok" if eligible else "blocked", "eligible": eligible,
            "probability": probability, "decimal_odds": odds, "ev": ev, "adjustments": adjustments,
            "kelly_multiplier": KELLY_MULTIPLIER, "stake_fraction": fraction if eligible else 0,
            "stake": float((Decimal(str(bankroll)) * Decimal(str(fraction))).quantize(Decimal("0.01"), rounding=ROUND_DOWN)) if eligible else 0,
            "bankroll": bankroll, "event_risk_cap": cap, "model_source": model_source,
            "observed_at": observed.astimezone(timezone.utc).isoformat(),
            "requires_hitl": eligible, "real_bet_placed": False,
            "warning": "Conditional on supplied model probability; no calibrated accuracy claimed"}


def _implied(odds: list) -> list[float]:
    if not isinstance(odds, list) or not 2 <= len(odds) <= 100:
        raise ValueError("invalid_market")
    return [1 / number(o, "odds", 1.000001, 10000) for o in odds]


def _bisect(f, lo: float, hi: float) -> float:
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _power(inverse: list[float]) -> list[float]:
    # Find k with sum(pi ** k) == 1; k > 1 when the book has a margin.
    k = _bisect(lambda k: sum(p ** k for p in inverse) - 1, 0.01, 50.0)
    return [p ** k for p in inverse]


def _shin(inverse: list[float]) -> list[float]:
    total = sum(inverse)

    def probs(z: float) -> list[float]:
        return [(math.sqrt(z * z + 4 * (1 - z) * p * p / total) - z) / (2 * (1 - z)) for p in inverse]

    z = _bisect(lambda z: sum(probs(z)) - 1, 0.0, 0.999)
    return probs(z)


def fair_probabilities(odds: list, method: str = "proportional") -> list[float]:
    """Margin-free probabilities of one market's selections."""
    if method not in DEVIG_METHODS:
        raise ValueError("unknown_devig_method")
    inverse = _implied(odds)
    total = sum(inverse)
    if method == "proportional" or total <= 1:  # no margin to remove beyond normalising
        return [p / total for p in inverse]
    raw = _power(inverse) if method == "power" else _shin(inverse)
    norm = sum(raw)
    return [p / norm for p in raw]
