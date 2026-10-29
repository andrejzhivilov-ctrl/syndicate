"""Futures specifics for metals and energy: curve shape, roll window, back-adjusted series.

Gold, silver, crude and gas trade through expiring contracts. A naive price
series glues contracts together and shows a fake gap on every roll; a naive
signal ignores that holding a contango curve costs money every month.
"""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Mapping

ROLL_DAYS_BEFORE_EXPIRY = 5


def curve_structure(front: float, next_: float, days_between: int) -> Dict[str, object]:
    """Contango (next > front) or backwardation, with the annualised roll yield of holding long."""
    if front <= 0 or next_ <= 0 or days_between <= 0:
        raise ValueError("invalid_curve_inputs")
    spread = next_ / front - 1
    shape = "contango" if spread > 0 else "backwardation" if spread < 0 else "flat"
    # A long position rolls from front into next: contango costs, backwardation pays.
    roll_yield_annual = -spread * 365 / days_between
    return {"structure": shape, "spread": spread, "roll_yield_annual_long": roll_yield_annual}


def roll_due(expiry: date, today: date, roll_days: int = ROLL_DAYS_BEFORE_EXPIRY) -> Dict[str, object]:
    days_left = (expiry - today).days
    if days_left < 0:
        return {"roll_due": True, "days_left": days_left, "reason": "contract_expired"}
    return {"roll_due": days_left <= roll_days, "days_left": days_left,
            "reason": "inside_roll_window" if days_left <= roll_days else "hold"}


def back_adjust(segments: List[Mapping[str, object]]) -> List[float]:
    """Ratio back-adjusted continuous series from contract segments.

    ``segments`` are oldest first: ``{"prices": [...], "roll_from": old_close, "roll_to": new_open}``
    on every segment but the last. Older prices are scaled by new/old at each roll,
    so the joined series has no artificial gap and percentage moves stay true.
    """
    if not segments:
        return []
    out: List[float] = []
    factor = 1.0
    for seg in reversed(segments):
        if seg.get("roll_from") is not None:  # this segment rolled into the next one: scale it to the new level
            old, new = float(seg["roll_from"]), float(seg["roll_to"])  # type: ignore[arg-type]
            if old <= 0 or new <= 0:
                raise ValueError("invalid_roll_prices")
            factor *= new / old
        prices = [float(p) for p in seg["prices"]]  # type: ignore[union-attr]
        out[:0] = [p * factor for p in prices]
    return out
