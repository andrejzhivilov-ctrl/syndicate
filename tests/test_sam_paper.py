"""Sam's paper ledger and strategy tournament (Andrii, 19.11.2026)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from src import agent_jobs, agent_schedule, hermes_tools, sam_paper, sam_strategies

T0 = datetime(2026, 11, 19, 10, 0, tzinfo=timezone.utc)


def _empty():
    return {"open": [], "closed": [], "bets": [], "settled": []}


def test_a_trade_is_sized_by_risk_capped_by_leverage_and_closed_by_its_stop_first():
    ledger = _empty()
    made = sam_paper.open_trade(ledger, account="crypto", strategy="levels_15m", source="binance", symbol="BTC/USDT",
                                side="long", entry=100.0, stop=98.0, target=105.0, risk=0.01, now=T0)
    trade = made["trade"]
    assert trade["risk_money"] <= 1.0 and trade["size"] * trade["entry"] <= 100 * 10 + 1e-9  # 1% of $100, x10 cap
    both = [{"time": T0 + timedelta(minutes=1), "high": 106.0, "low": 97.0}]  # stop and target in one candle
    closed = sam_paper.mark(ledger, "binance", "BTC/USDT", both, T0 + timedelta(minutes=2))
    assert closed[0]["exit_reason"] == "stop" and closed[0]["r"] < -0.9 and ledger["open"] == []
    wrong = sam_paper.open_trade(ledger, account="crypto", strategy="x", source="binance", symbol="BTC/USDT",
                                 side="long", entry=100.0, stop=101.0, target=103.0, risk=0.01)
    assert wrong["error"] == "stop_and_target_on_wrong_sides"


def test_loss_limits_freeze_an_account_and_new_projects_have_their_own_small_basket():
    ledger = _empty()
    ledger["closed"].append({"account": "trading", "strategy": "x", "pnl": -3.5, "r": -1, "closed_at": T0.isoformat()})
    assert sam_paper.frozen(ledger, "trading", T0) == "day"
    refused = sam_paper.open_trade(ledger, account="trading", strategy="x", source="yahoo", symbol="EURUSD=X",
                                   side="long", entry=1.1, stop=1.09, target=1.125, risk=0.01, now=T0)
    assert refused["reason"] == "loss_limit_day"
    first = sam_paper.open_trade(ledger, account="crypto", strategy="new_project", source="binance", symbol="NEW/USDT",
                                 side="long", entry=1.0, stop=0.5, target=2.25, risk=0.01, leverage=1, now=T0)
    assert first["status"] == "ok"
    for _ in range(10):
        last = sam_paper.open_trade(ledger, account="crypto", strategy="new_project", source="binance",
                                    symbol="NEW2/USDT", side="long", entry=1.0, stop=0.5, target=2.25, risk=0.01,
                                    leverage=1, now=T0)
    assert last["reason"] == "new_project_basket_full"


def test_bets_need_positive_expectation_use_a_quarter_kelly_capped_at_two_percent_and_keep_clv():
    ledger = _empty()
    assert sam_paper.place_bet(ledger, strategy="elo", sport="football", event="A-B", market="1x2", selection="A",
                               odds=1.8, probability=0.5, now=T0)["reason"] == "no_positive_expectation"
    bet = sam_paper.place_bet(ledger, strategy="elo", sport="football", event="A-B", market="1x2", selection="A",
                              odds=2.5, probability=0.6, now=T0)["bet"]
    assert bet["stake"] == 20.0  # quarter Kelly is 8.3%, capped at 2% of 1000
    settled = sam_paper.settle_bet(ledger, bet["id"], True, closing_odds=2.2)["bet"]
    assert settled["pnl"] == 30.0 and settled["clv"] > 0
    stats = sam_paper.stats(ledger)
    assert stats["accounts"]["bets"]["balance"] == 1030.0 and stats["strategies"]["elo"]["avg_clv"] > 0


def _rows(prices):
    start = int((T0 - timedelta(days=3)).timestamp() * 1000)
    return [[start + i * 900_000, p, p * 1.002, p * 0.998, p, 1.0] for i, p in enumerate(prices)]


def test_the_tournament_runs_every_strategy_and_never_duplicates_an_open_trade(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    prices = list(np.linspace(100, 100, 250)) + [100, 104, 108]  # a break above yesterday's high

    def fetch(source, symbol, timeframe, limit):
        if source != "binance" or symbol != "BTC/USDT":
            raise TimeoutError("not in this test")  # a dead source never stops the others
        return _rows(prices)

    ledger = _empty()
    opened = sam_strategies.run(ledger, fetch, ["levels_15m", "breakout_1h"], now=T0)
    assert opened and all(t["symbol"] == "BTC/USDT" for t in opened)
    assert all(abs(t["target"] - t["entry"]) >= 2.5 * abs(t["entry"] - t["stop"]) - 1e-9 for t in opened)
    assert sam_strategies.run(ledger, fetch, ["levels_15m", "breakout_1h"], now=T0) == []  # one per strategy and symbol


def test_sam_has_paper_tools_and_a_schedule_that_is_quiet_at_night():
    assert {"paper_trade", "paper_bet"} <= set(hermes_tools.granted("sam"))
    jobs = agent_schedule.JOBS
    assert jobs["sam_paper_mark"].cron == "* * * * *" and jobs["sam_tournament"].cron == "*/5 * * * *"
    assert jobs["sam_morning"].cron == "0 8 * * *" and jobs["sam_london"].cron == "45 9 * * 1-5"
    assert agent_jobs.QUIET in jobs["sam_reflection"].text and agent_jobs.QUIET in jobs["sam_bets"].text
    assert "сесії" in jobs["sam_morning"].text and "ризики" in jobs["sam_morning"].text
    assert agent_jobs.AGENT_KINDS["sam"] == frozenset({"report"})


def test_the_paper_tool_answers_status_and_refuses_unknown_actions(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    status = sam_paper.trade_tool({"action": "status"})
    assert status["accounts"]["trading"]["balance"] == 100.0 and status["accounts"]["invest"]["currency"] == "UAH"
    assert sam_paper.trade_tool({"action": "buy"})["error"] == "unknown_action"
    made = sam_paper.trade_tool({"action": "open", "account": "trading", "strategy": "news", "source": "yahoo",
                                 "symbol": "GC=F", "side": "short", "entry": 2000, "stop": 2010, "target": 1975})
    assert made["status"] == "ok" and sam_paper.trade_tool({"action": "status"})["open_trades"] == 1


def test_a_stop_inside_the_fees_is_widened_by_the_engine_and_the_money_at_risk_stays_the_same():
    """20.11.2026: one-minute scalps with a stop inside the costs lost 2-3.4R a stop. Andrii: widen, never refuse;
    crypto pays futures fees (maker in, maker at target, taker plus slippage at the stop)."""
    ledger = _empty()
    # Sam's own trade with such a stop gets the closest honest stop back instead of a silent loss.
    tight = sam_paper.open_trade(ledger, account="crypto", strategy="combo", source="binance", symbol="BTC/USDT",
                                 side="long", entry=100.0, stop=99.9, target=100.25, risk=0.005, now=T0)
    assert tight["reason"] == "costs_eat_the_edge" and 99.55 < tight["min_stop"] < 99.65 and ledger["open"] == []
    # The tournament moves the stop out to the floor and opens the trade.
    signal = sam_strategies.with_cost_floor(sam_strategies.Signal("long", 100.0, 99.9, "EMA"), "crypto", "scalp_5m")
    assert signal.stop == pytest.approx(tight["min_stop"]) and "комісії" in signal.reason
    made = sam_paper.open_trade(ledger, account="crypto", strategy="scalp_5m", source="binance", symbol="BTC/USDT",
                                side="long", entry=signal.entry, stop=signal.stop, target=signal.target(), risk=0.005, now=T0)
    trade = made["trade"]
    assert made["status"] == "ok" and trade["risk_money"] == pytest.approx(0.5, rel=1e-6)  # 0.5% of $100 either way
    stopped = sam_paper.mark(ledger, "binance", "BTC/USDT", [{"time": T0 + timedelta(minutes=5), "high": 100.1,
                                                              "low": 99.0}], T0 + timedelta(minutes=6))[0]
    assert -1.25 < stopped["r"] < -1.0  # the fees cost at most 0.2R now, not 1-2R
    hit = sam_paper.open_trade(_empty(), account="crypto", strategy="scalp_5m", source="binance", symbol="ETH/USDT",
                               side="long", entry=100.0, stop=signal.stop, target=signal.target(), risk=0.005, now=T0)
    won = sam_paper.mark({"open": [hit["trade"]], "closed": []}, "binance", "ETH/USDT",
                         [{"time": T0 + timedelta(minutes=5), "high": 102.0, "low": 99.95}], T0 + timedelta(minutes=6))[0]
    assert won["exit_reason"] == "target" and won["r"] > 2.3  # a hit target is a real win after fees
    # The new-projects basket buys the coin on spot: 0.1% a side, so its floor is wider.
    assert sam_paper.min_stop_distance("crypto", 100.0, "new_project") > 2 * sam_paper.min_stop_distance("crypto", 100.0)
