"""One backtester for every strategy in Sam's catalog (Andrii, 20.11.2026).

The rule is the same expression the live tournament uses (src/sam_rules.py), run over history with the
costs of the paper account. Honest by construction:

- A signal on a closed bar enters at the *next* bar's open, never at a price already gone.
- If the stop and the target are both inside one bar, the stop counts (the worse case, as on paper).
- Costs are charged on entry and exit; the position is sized by the risk per trade and capped by leverage.
- The last 30% of the bars are out of sample: the gate looks only at them, the first 70% are reported
  for comparison. Buy-and-hold over the same bars is always beside the result.

The gate to paper is written here, not chosen by the model: enough out-of-sample trades, positive
expectancy after costs, profit factor above the bar, drawdown inside Andrii's total loss limit.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping, Optional

import numpy as np
import pandas as pd

from src import sam_paper, sam_rules

OUT_OF_SAMPLE = 0.30
GATE = {"min_trades": 20, "min_expectancy_r": 0.05, "min_profit_factor": 1.10,
        "max_drawdown_pct": sam_paper.LOSS_LIMITS["total"] * 100}


def signals(spec: Mapping[str, Any], frame: pd.DataFrame) -> Dict[str, Optional[pd.Series]]:
    """Entry flags and stop prices on every bar; a side the spec leaves out stays None."""
    out: Dict[str, Optional[pd.Series]] = {}
    for side in ("long", "short"):
        rule = spec.get(side)
        out[side] = sam_rules.evaluate(rule, frame).astype(bool) if rule else None
        out[f"stop_{side}"] = sam_rules.evaluate(spec[f"stop_{side}"], frame) if rule else None
    warm = int(spec.get("min_bars") or 0)
    for side in ("long", "short"):
        if out[side] is not None and warm:
            out[side].iloc[:warm] = False
    return out


def _exit(side: str, highs: np.ndarray, lows: np.ndarray, start: int, stop: float, target: float):
    for j in range(start, len(highs)):
        hit_stop = lows[j] <= stop if side == "long" else highs[j] >= stop
        hit_target = highs[j] >= target if side == "long" else lows[j] <= target
        if hit_stop:
            return j, stop, "stop"
        if hit_target:
            return j, target, "target"
    return None


def simulate(spec: Mapping[str, Any], frame: pd.DataFrame, account: str) -> List[Dict[str, Any]]:
    """Every trade the rule would have made on these bars, one position at a time."""
    marks = signals(spec, frame)
    opens, highs, lows = (frame[c].to_numpy(float) for c in ("open", "high", "low"))
    closes = frame["close"].to_numpy(float)
    cost = sam_paper.ACCOUNTS[account]["cost_bps"] / 10_000
    lev = sam_paper.ACCOUNTS[account]["max_leverage"]
    risk_frac, rr = float(spec["risk"]), float(spec.get("rr") or 2.5)
    trades: List[Dict[str, Any]] = []
    i, n = 0, len(frame)
    while i < n - 1:
        side = "long" if marks["long"] is not None and marks["long"].iat[i] else \
            "short" if marks["short"] is not None and marks["short"].iat[i] else None
        if side is None:
            i += 1
            continue
        entry, stop = opens[i + 1], float(marks[f"stop_{side}"].iat[i])
        sign = 1 if side == "long" else -1
        distance = (entry - stop) * sign
        if not (math.isfinite(entry) and math.isfinite(stop) and entry > 0 and distance > 0):
            i += 1  # a gap through the stop or a missing value: no honest entry
            continue
        target = entry + sign * rr * distance
        if sam_paper.cost_in_r(account, entry, stop, target) > sam_paper.MAX_COST_R:
            i += 1  # paper refuses a trade whose costs eat the edge; the history must not count it either
            continue
        found = _exit(side, highs, lows, i + 1, stop, target)
        j, price, why = found if found else (n - 1, closes[-1], "end_of_data")
        fraction = min(risk_frac / distance, lev / entry)  # units per unit of equity
        move = (price - entry) * sign
        pnl = fraction * move - fraction * (entry + price) * cost
        trades.append({"entry_bar": i + 1, "exit_bar": j, "side": side, "entry": entry, "exit": price,
                       "why": why, "r": move / distance - (entry + price) * cost / distance, "pnl_frac": pnl})
        i = j + 1
    return trades


def metrics(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not trades:
        return {"trades": 0, "win_rate": None, "profit_factor": None, "expectancy_r": None,
                "return_pct": 0.0, "max_drawdown_pct": 0.0}
    rs = [t["r"] for t in trades]
    gains, losses = sum(r for r in rs if r > 0), -sum(r for r in rs if r < 0)
    equity, peak, worst = 1.0, 1.0, 0.0
    for t in trades:
        equity *= 1 + t["pnl_frac"]
        peak = max(peak, equity)
        worst = max(worst, 1 - equity / peak)
    return {"trades": len(rs), "win_rate": round(sum(r > 0 for r in rs) / len(rs), 3),
            "profit_factor": round(gains / losses, 3) if losses else None,
            "expectancy_r": round(float(np.mean(rs)), 3),
            "return_pct": round((equity - 1) * 100, 2), "max_drawdown_pct": round(worst * 100, 2)}


def _buy_hold(frame: pd.DataFrame) -> Optional[float]:
    first, last = float(frame["close"].iloc[0]), float(frame["close"].iloc[-1])
    return round((last / first - 1) * 100, 2) if first > 0 else None


def run_one(spec: Mapping[str, Any], frame: pd.DataFrame, account: str) -> Dict[str, Any]:
    """In-sample and out-of-sample results for one instrument, with buy-and-hold beside each."""
    split = int(len(frame) * (1 - OUT_OF_SAMPLE))
    trades = simulate(spec, frame, account)
    inside = [t for t in trades if t["entry_bar"] < split]
    outside = [t for t in trades if t["entry_bar"] >= split]
    return {"bars": len(frame), "from": str(frame.index[0])[:16], "to": str(frame.index[-1])[:16],
            "in_sample": {**metrics(inside), "buy_hold_pct": _buy_hold(frame.iloc[:split])},
            "out_of_sample": {**metrics(outside), "buy_hold_pct": _buy_hold(frame.iloc[split:])},
            "_trades_out": outside}


def verdict(per_symbol: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    """The gate over all instruments together; reasons name every failed condition."""
    pooled = [t for r in per_symbol.values() for t in r.get("_trades_out", [])]
    total = metrics(pooled) if pooled else metrics([])
    worst_dd = max((r["out_of_sample"]["max_drawdown_pct"] for r in per_symbol.values()), default=0.0)
    reasons = []
    if total["trades"] < GATE["min_trades"]:
        reasons.append(f"мало угод поза вибіркою: {total['trades']} < {GATE['min_trades']}")
    if total["expectancy_r"] is None or total["expectancy_r"] < GATE["min_expectancy_r"]:
        reasons.append(f"очікування {total['expectancy_r']}R < {GATE['min_expectancy_r']}R")
    if total["trades"] and (total["profit_factor"] is not None and total["profit_factor"] < GATE["min_profit_factor"]):
        reasons.append(f"profit factor {total['profit_factor']} < {GATE['min_profit_factor']}")
    if worst_dd > GATE["max_drawdown_pct"]:
        reasons.append(f"просадка {worst_dd}% > {GATE['max_drawdown_pct']}%")
    return {"passed": not reasons, "reasons": reasons,
            "out_of_sample_total": {k: total[k] for k in ("trades", "win_rate", "profit_factor", "expectancy_r")},
            "worst_drawdown_pct": worst_dd, "gate": GATE}


def report(spec: Mapping[str, Any], frames: Mapping[str, Any]) -> Dict[str, Any]:
    """frames: "account:source:symbol" -> DataFrame or None (a source that failed is named, not skipped silently)."""
    results, missing = {}, []
    for key, frame in frames.items():
        if frame is None or len(frame) < int(spec.get("min_bars") or 0) + 50:
            missing.append(key)
            continue
        results[key] = run_one(spec, frame, key.split(":", 1)[0])
    if not results:
        return {"status": "unavailable", "reason": "no_history", "missing": missing}
    decided = verdict(results)
    for row in results.values():
        row.pop("_trades_out", None)
    return {"status": "ok", "timeframe": spec["timeframe"], "per_symbol": results, "missing": missing, **decided}
