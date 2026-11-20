"""Target first or stop first: Sam's replays of a planned trade (Andrii, 20.11.2026)."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from src import hermes_tools, sam_montecarlo as mc

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _frame(drift: float, n: int = 1500, vol: float = 0.004, seed: int = 3) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    steps = rng.normal(0, vol, n)
    close = 100 * np.exp(np.cumsum(drift + steps - steps.mean()))  # no accidental drift in the "flat" market
    index = pd.to_datetime([T0 + timedelta(hours=i) for i in range(n)], utc=True)
    c = pd.Series(close, index=index)
    return pd.DataFrame({"open": c.shift(1).fillna(c.iloc[0]), "high": c * 1.002, "low": c * 0.998, "close": c,
                         "volume": 1.0}, index=index)


def test_a_symmetric_plan_on_a_random_walk_is_a_coin_flip_and_the_drift_shows():
    flat = mc.odds(_frame(0.0), "long", 100.0, 98.0, 102.0, horizon=200, replays=4000)
    assert flat["status"] == "ok" and abs(flat["p_target_first"] - flat["p_stop_first"]) < 0.08
    assert flat["p_target_first"] + flat["p_stop_first"] + flat["p_neither"] == 1.0 or \
        abs(flat["p_target_first"] + flat["p_stop_first"] + flat["p_neither"] - 1) < 0.002
    up = mc.odds(_frame(0.001), "long", 100.0, 98.0, 102.0, horizon=200, replays=4000)
    down = mc.odds(_frame(0.001), "short", 100.0, 102.0, 98.0, horizon=200, replays=4000)
    assert up["p_target_first"] > 0.6 and down["p_stop_first"] > 0.6 and up["expected_r"] > 0 > down["expected_r"]
    assert mc.odds(_frame(0.0), "long", 100.0, 98.0, 102.0, replays=500, seed=5) == \
        mc.odds(_frame(0.0), "long", 100.0, 98.0, 102.0, replays=500, seed=5)  # the same seed, the same answer


def test_a_bar_touching_both_counts_as_the_stop_and_bad_plans_are_refused():
    frame = _frame(0.0, vol=0.0)
    frame["high"], frame["low"] = frame["close"] * 1.05, frame["close"] * 0.95  # every bar spans stop and target
    both = mc.odds(frame, "long", 100.0, 98.0, 102.0, horizon=5, replays=500)
    assert both["p_stop_first"] == 1.0 and both["expected_r"] == -1.0
    assert mc.odds(frame, "long", 100.0, 101.0, 102.0)["error"] == "stop_and_target_on_wrong_sides"
    assert mc.odds(frame.iloc[:50], "long", 100.0, 98.0, 102.0)["reason"] == "not_enough_history"


def test_the_tool_names_its_source_and_sam_has_it():
    frame = _frame(0.0)

    def fetch(source, symbol, timeframe, bars):
        return [[int(i.timestamp() * 1000), r.open, r.high, r.low, r.close, r.volume] for i, r in frame.iterrows()]

    out = asyncio.run(mc.tool({"source": "binance", "symbol": "BTC/USDT", "side": "long", "entry": 100, "stop": 98,
                               "target": 105, "replays": 500}, fetch))
    assert out["status"] == "ok" and out["symbol"] == "BTC/USDT" and out["history"].startswith("2026-01-01")

    def dead(*_a):
        raise TimeoutError("down")

    assert asyncio.run(mc.tool({"source": "binance", "symbol": "BTC/USDT", "side": "long", "entry": 1, "stop": 0.9,
                                "target": 1.3}, dead))["status"] == "unavailable"
    assert hermes_tools.TRADE_ODDS in hermes_tools.granted("sam")
