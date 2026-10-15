"""+EV threshold and fractional Kelly capped per event, including open exposure."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN

from src.agents.director_base import number, text, utc_now


def evaluate(payload: dict, *, risk_cap: float = 0.01) -> dict:
    probability = number(payload["probability"], "probability", 0, 1)
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
    full_kelly = max(0, ev / (odds - 1))
    fraction = min(cap, 0.25 * full_kelly)
    eligible = exact_ev >= Decimal("0.045") and fraction > 0
    return {"status": "ok" if eligible else "blocked", "eligible": eligible,
            "probability": probability, "decimal_odds": odds, "ev": ev,
            "kelly_multiplier": 0.25, "stake_fraction": fraction if eligible else 0,
            "stake": float((Decimal(str(bankroll)) * Decimal(str(fraction))).quantize(Decimal("0.01"), rounding=ROUND_DOWN)) if eligible else 0,
            "bankroll": bankroll, "event_risk_cap": cap, "model_source": model_source,
            "observed_at": observed.astimezone(timezone.utc).isoformat(),
            "requires_hitl": eligible, "real_bet_placed": False,
            "warning": "Conditional on supplied model probability; no calibrated accuracy claimed"}


def fair_probabilities(odds: list) -> list[float]:
    if not isinstance(odds, list) or not 2 <= len(odds) <= 100:
        raise ValueError("invalid_market")
    inverse = [1 / number(o, "odds", 1.000001, 10000) for o in odds]
    total = sum(inverse)
    return [p / total for p in inverse]
