"""Sam's strategy catalog, its rule language and the backtest gate (Andrii, 20.11.2026)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

from src import agent_schedule, hermes_tools, sam_backtest, sam_catalog, sam_rules

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _frame(closes, spread=0.002, step=3600):
    index = pd.to_datetime([T0 + timedelta(seconds=i * step) for i in range(len(closes))], utc=True)
    c = pd.Series(closes, index=index, dtype=float)
    return pd.DataFrame({"open": c.shift(1).fillna(c.iloc[0]), "high": c * (1 + spread), "low": c * (1 - spread),
                         "close": c, "volume": 1.0}, index=index)


def _rows(frame):
    return [[int(i.timestamp() * 1000), r.open, r.high, r.low, r.close, r.volume] for i, r in frame.iterrows()]


def test_the_rule_language_runs_only_what_it_lists():
    for bad in ("__import__('os').system('id')", "close.real", "open(1)", "[close]", "close if 1 else 2",
                "ema(close)", "ema(close, 0)", "lambda: 1", "'text' > 1", "secret > 1"):
        assert sam_rules.check(bad), bad
    frame = _frame(list(np.linspace(100, 90, 60)) + list(np.linspace(90, 120, 60)))
    crossed = sam_rules.evaluate("cross_up(ema(close, 5), ema(close, 20))", frame)
    assert crossed.dtype == bool and 1 <= int(crossed.sum()) <= 3
    combo = sam_rules.evaluate("rsi(close, 14) > 50 and close > highest(high, 10) or not close > 0", frame)
    assert combo.dtype == bool and combo.iloc[-1]
    stop = sam_rules.evaluate("close - 1.5 * atr(14)", frame)
    assert stop.iloc[-1] < frame["close"].iloc[-1]


def test_every_strategy_in_the_repository_is_valid_and_obeys_andriis_rules():
    seeds = sam_catalog.seeds()
    assert {"levels_15m", "breakout_1h", "trend_ema_1h", "mean_reversion_15m", "scalp_1m", "scalp_5m", "ema_20_55_rsi_4h"} <= set(seeds)
    for sid, spec in seeds.items():
        assert spec["id"] == sid and sam_catalog.validate(spec) == [], sid
        assert spec["risk"] <= 0.01 and spec["rr"] >= 2.5


def test_the_backtest_enters_on_the_next_open_and_counts_the_stop_first():
    spec = {"id": "t", "timeframe": "1h", "risk": 0.01, "rr": 2.5, "min_bars": 0, "markets": ["crypto"],
            "long": "close > 0", "stop_long": "close - 1"}
    frame = _frame([100.0] * 5)
    frame.iloc[2, frame.columns.get_loc("open")] = 100.5
    frame.iloc[2, frame.columns.get_loc("high")] = 110.0  # target and stop both inside bar 2
    frame.iloc[2, frame.columns.get_loc("low")] = 90.0
    first = sam_backtest.simulate(spec, frame, "trading")[0]  # 3 bps: the timing, not the cost gate, is tested
    assert first["entry_bar"] == 1 and first["entry"] == frame["open"].iloc[1]  # bar 0's signal, bar 1's open
    second = sam_backtest.simulate(spec, frame.iloc[1:], "trading")[0]
    assert second["entry"] == 100.5 and second["why"] == "stop" and second["r"] < -1  # worse case and costs


def _trend(n=1500):
    rng = np.random.default_rng(7)
    return _frame(list(100 * np.exp(np.cumsum(0.004 + rng.normal(0, 0.01, n)))))


def test_a_new_idea_is_tested_at_once_and_only_a_passing_one_reaches_paper(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", str(tmp_path / "vault"))
    (tmp_path / "vault").mkdir()
    history = _trend()

    def fetch(source, symbol, timeframe, bars):
        if symbol != "BTC/USDT":
            raise TimeoutError("one source only")
        return _rows(history)

    spec = {"id": "sam_trend_follow", "title": "Тренд", "hypothesis": "тренд триває", "timeframe": "1h", "style": "mid",
            "markets": ["crypto"], "risk": 0.01, "long": "close > ema(close, 50) and cross_up(close, highest(high, 20))",
            "stop_long": "close - 2 * atr(14)"}
    made = sam_catalog.tool({"action": "propose", "spec": spec}, fetch)
    assert made["status"] == "ok" and made["now"] in ("paper", "rejected")
    assert "crypto:binance:ETH/USDT" in made["missing"]  # a dead source is named, never guessed
    if made["now"] == "rejected":
        assert made["reasons"]
    # Always short against a rising market: no fee floor can save it (20.11.2026: stops are widened, not refused).
    noise = {**spec, "id": "sam_noise", "parent": "sam_trend_follow", "long": None, "stop_long": None,
             "short": "close > 0", "stop_short": "close * 1.001"}
    worse = sam_catalog.tool({"action": "propose", "spec": noise}, fetch)
    assert worse["now"] == "rejected" and any("очікування" in r for r in worse["reasons"])
    assert sam_catalog.tool({"action": "propose", "spec": spec}, fetch)["problems"]  # an id is never reused
    card = (tmp_path / "vault" / "Сем" / "Стратегії" / "sam_noise.md").read_text(encoding="utf-8")
    assert "[[sam_trend_follow]]" in card and "rejected" in card
    index = (tmp_path / "vault" / "Сем" / "Стратегії" / "Каталог.md").read_text(encoding="utf-8")
    assert "[[levels_15m]]" in index and "[[sam_noise]]" in index


def test_sam_cannot_name_a_real_money_candidate_and_unknown_actions_are_errors(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    assert sam_catalog.set_status("trend_ema_1h", "candidate", "гарно", "sam")["reason"] == "needs_andrii"
    assert sam_catalog.tool({"action": "delete", "id": "trend_ema_1h"}, None)["available_actions"] == \
        ["archive", "backtest", "get", "list", "propose"]
    assert sam_catalog.tool({"action": "archive", "id": "trend_ema_1h"}, None)["error"] == "why_is_required"
    assert sam_catalog.tool({"action": "archive", "id": "trend_ema_1h", "why": "не працює"}, None)["now"] == "archived"
    listed = sam_catalog.tool({"action": "list"}, None)["strategies"]
    assert {r["id"]: r["status"] for r in listed}["trend_ema_1h"] == "archived"  # archived, still listed
    assert "trend_ema_1h" not in sam_catalog.active()


def test_a_broken_rule_never_stops_the_tournament_and_sam_has_the_tool(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    assert hermes_tools.STRATEGY in hermes_tools.granted("sam")
    assert agent_schedule.JOBS["sam_backtest_ideas"].cron == "30 5 * * *"
    assert agent_schedule.JOBS["sam_rebacktest"].cron == "0 6 1 * *"
    # 20.11.2026: the 1m scalp stays on paper with the fee floor; the 5m variant waits as an idea for its test
    assert "scalp_1m" in sam_catalog.active("1m") and "scalp_5m" not in sam_catalog.active()
    with pytest.raises(sam_rules.RuleError):
        sam_rules.evaluate("nonsense(close)", _trend(50))
