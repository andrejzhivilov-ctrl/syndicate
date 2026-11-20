"""Target first, stop first or neither: 10 000 replays of a planned trade (Andrii, 20.11.2026).

The idea comes from the "Time Machine" skill in Jakeschincariol/day-trader-skill (MIT): before a trade
is sized, replay the rest of the move many times from the instrument's own recent bars and count how
often the target comes first. That skill is written for US stocks inside one New York session and its
script is not in our vendor copy; this is our own version for 24-hour crypto and FX bars.

How a replay is built: every recent bar becomes three ratios to the bar before it (high, low, close over
the previous close). A replay strings together random *blocks* of consecutive bars (so calm and wild
stretches stay together), starting at the entry price, for ``horizon`` bars. A bar that touches both the
stop and the target counts as the stop (the worse case, as on paper). The result is a simulation from
the instrument's own past, not a forecast: it says whether the plan is a coin flip, not where price goes.
"""
from __future__ import annotations

import math
from typing import Any, Dict, Mapping, Optional

import numpy as np
import pandas as pd

MAX_REPLAYS = 20_000
MAX_HORIZON = 500
BLOCK = 6
MIN_POOL = 200


def ratios(frame: pd.DataFrame) -> np.ndarray:
    """(bars, 3): high, low, close of each bar over the previous close."""
    prev = frame["close"].shift(1)
    out = pd.concat([frame["high"] / prev, frame["low"] / prev, frame["close"] / prev], axis=1).dropna()
    out = out[(out > 0).all(axis=1) & np.isfinite(out).all(axis=1)]
    return out.to_numpy(float)


def replay(pool: np.ndarray, entry: float, horizon: int, replays: int, seed: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    blocks = math.ceil(horizon / BLOCK)
    starts = rng.integers(0, len(pool) - BLOCK, size=(replays, blocks))
    index = (starts[:, :, None] + np.arange(BLOCK)[None, None, :]).reshape(replays, -1)[:, :horizon]
    steps = pool[index]  # (replays, horizon, 3)
    closes = entry * np.cumprod(steps[:, :, 2], axis=1)
    prev = np.concatenate([np.full((replays, 1), entry), closes[:, :-1]], axis=1)
    return {"high": prev * steps[:, :, 0], "low": prev * steps[:, :, 1], "close": closes}


def _first(hit: np.ndarray) -> np.ndarray:
    """Index of the first True per row, or the row length when there is none."""
    return np.where(hit.any(axis=1), hit.argmax(axis=1), hit.shape[1])


def odds(frame: pd.DataFrame, side: str, entry: float, stop: float, target: float, horizon: int = 24,
         replays: int = 10_000, seed: int = 19) -> Dict[str, Any]:
    if side not in ("long", "short"):
        return {"status": "error", "error": "side_must_be_long_or_short"}
    sign = 1 if side == "long" else -1
    if not all(isinstance(x, (int, float)) and math.isfinite(x) and x > 0 for x in (entry, stop, target)) \
            or not (sign * (entry - stop) > 0 and sign * (target - entry) > 0):
        return {"status": "error", "error": "stop_and_target_on_wrong_sides"}
    horizon = max(1, min(int(horizon), MAX_HORIZON))
    replays = max(100, min(int(replays), MAX_REPLAYS))
    pool = ratios(frame)
    if len(pool) < MIN_POOL:
        return {"status": "unavailable", "reason": "not_enough_history", "bars": len(pool), "needed": MIN_POOL}
    paths = replay(pool, entry, horizon, replays, seed)
    if side == "long":
        stop_hit, target_hit = paths["low"] <= stop, paths["high"] >= target
    else:
        stop_hit, target_hit = paths["high"] >= stop, paths["low"] <= target
    first_stop, first_target = _first(stop_hit), _first(target_hit)
    stopped = first_stop <= first_target
    stopped &= first_stop < horizon
    won = (first_target < first_stop) & (first_target < horizon)
    neither = ~(stopped | won)
    risk = abs(entry - stop)
    rr = abs(target - entry) / risk
    open_r = sign * (paths["close"][:, -1] - entry) / risk
    r = np.where(won, rr, np.where(stopped, -1.0, open_r))
    final = paths["close"][:, -1]
    p_target, p_stop = float(won.mean()), float(stopped.mean())
    return {"status": "ok", "replays": replays, "horizon_bars": horizon, "seed": seed, "pool_bars": len(pool),
            "p_target_first": round(p_target, 3), "p_stop_first": round(p_stop, 3),
            "p_neither": round(float(neither.mean()), 3), "reward_risk": round(rr, 2),
            "expected_r": round(float(r.mean()), 3), "breakeven_win_rate": round(1 / (1 + rr), 3),
            "close_percentiles": {str(q): round(float(np.percentile(final, q)), 6) for q in (5, 25, 50, 75, 95)},
            "verdict": _verdict(p_target, p_stop, float(r.mean())),
            "note": "Симуляція з власних барів інструмента, а не прогноз. Перевір і правило на історії (strategy backtest)."}


def _verdict(p_target: float, p_stop: float, expected_r: float) -> str:
    if expected_r <= 0:
        return "без переваги: очікування в R не більше нуля"
    if abs(p_target - p_stop) < 0.05:
        return "майже монетка: перевага лише від співвідношення ціль/стоп"
    return "є перевага в симуляції" if expected_r >= 0.2 else "слабка перевага"


async def tool(args: Mapping[str, Any], fetch: Optional[Any] = None) -> Dict[str, Any]:
    """trade_odds: source, symbol, timeframe, side, entry, stop, target, horizon, replays."""
    import asyncio

    from src import market_data, sam_strategies

    fetch = fetch or market_data.history
    source, symbol = str(args.get("source", "")).lower(), str(args.get("symbol", ""))
    timeframe = str(args.get("timeframe") or "1h").lower()
    if source not in market_data.SOURCES or timeframe not in market_data.TIMEFRAMES:
        return {"status": "error", "error": "unknown_source_or_timeframe", "available_sources": list(market_data.SOURCES),
                "available_timeframes": sorted(market_data.TIMEFRAMES)}
    try:
        frame = sam_strategies.frame_of(await asyncio.to_thread(fetch, source, symbol, timeframe, 1_500))
    except Exception as exc:  # noqa: BLE001 - a dead source is reported, never guessed
        return {"status": "unavailable", "reason": f"{source}_{type(exc).__name__}"}
    try:
        numbers = {k: float(args[k]) for k in ("entry", "stop", "target")}
    except (KeyError, TypeError, ValueError):
        return {"status": "error", "error": "entry_stop_target_must_be_numbers"}
    result = await asyncio.to_thread(odds, frame, str(args.get("side", "")), numbers["entry"], numbers["stop"],
                                     numbers["target"], int(args.get("horizon") or 24), int(args.get("replays") or 10_000))
    return {**result, "source": source, "symbol": symbol, "timeframe": timeframe,
            "history": f"{str(frame.index[0])[:16]} .. {str(frame.index[-1])[:16]}" if len(frame) else None}
