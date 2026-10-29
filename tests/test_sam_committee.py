"""Sam (29.10): bull/bear committee, deterministic risk module, futures, macro sources, hash ledger."""
from __future__ import annotations

import asyncio
from datetime import date

import httpx
import pytest

from src.agents.sam.committee import arbitrate
from src.agents.sam.futures import back_adjust, curve_structure, roll_due
from src.agents.sam.journal import JournalEntry, TradeJournal
from src.agents.sam.ledger import GENESIS, HashLedger, verify
from src.agents.sam.risk import daily_guard, model_signal, position_size
from src.integrations.macro_data import cot_positioning, edgar_filings, eia_latest, fred_latest


def ev(claim, source="FRED DFII10 2026-10-28", weight=1.0):
    return {"claim": claim, "source": source, "weight": weight}


# ── committee ────────────────────────────────────────────────────────────────
def test_committee_needs_both_sides_and_sourced_evidence():
    assert arbitrate({"evidence": [ev("x")]}, None)["status"] == "incomplete"
    loud = arbitrate({"thesis": "up", "evidence": [{"claim": "trust me"}] * 5}, {"thesis": "down", "evidence": []})
    assert loud["status"] == "incomplete" and loud["unsourced_dropped"]["bull"] == 5


def test_committee_scores_the_better_sourced_case():
    result = arbitrate({"thesis": "gold up", "evidence": [ev("real yields falling"), ev("CB buying", "WGC Q3")] * 3},
                       {"thesis": "gold down", "evidence": [ev("DXY up", "FRED DTWEXBGS")]})
    assert result["status"] == "ok" and 0 < result["strength"] <= 1 and result["requires_hitl"] is True
    assert 0 <= result["confidence"] <= 100
    balanced = arbitrate({"evidence": [ev("a")]}, {"evidence": [ev("b")]})
    assert balanced["strength"] == 0 and balanced["actionable"] is False


# ── risk module ─────────────────────────────────────────────────────────────
@pytest.mark.parametrize("field", ["quantity", "lots", "size", "notional", "leverage"])
def test_model_can_never_size_an_order(field):
    with pytest.raises(ValueError, match="model_cannot_size_orders"):
        model_signal({"strength": 0.5, "rationale": "x", field: 10})


def test_size_comes_from_atr_risk_and_asset_cap():
    sig = {"strength": 0.5, "rationale": "committee 72/100"}
    result = position_size(sig, equity=10_000, equity_start_of_day=10_000, price=100, atr=2)
    # risk budget 10_000 * 1% * 0.5 = 50; stop 2 * ATR = 4 → 12.5 → 12 units; cap 10% = 10 units → 10
    assert result["units"] == 10 and result["limited_by"] == "asset_cap"
    assert result["stop"] == 96 and result["requires_hitl"] is True and result["auto_execute"] is False
    wide = position_size(sig, equity=10_000, equity_start_of_day=10_000, price=100, atr=20)
    assert wide["units"] == 1 and wide["limited_by"] == "risk"  # volatile market → smaller size
    stock = position_size({"strength": 1, "rationale": "x"}, equity=10_000, equity_start_of_day=10_000,
                          price=100, atr=0.5, asset_class="equity")
    assert stock["notional"] <= 500


def test_daily_drawdown_stops_new_risk_and_flat_signal_does_nothing():
    assert daily_guard(10_000, 9_800)["blocked"] is True and daily_guard(10_000, 9_900)["blocked"] is False
    blocked = position_size({"strength": 0.9, "rationale": "x"}, equity=9_790, equity_start_of_day=10_000,
                            price=100, atr=1)
    assert blocked["status"] == "blocked" and blocked["reason"] == "daily_drawdown_limit" and blocked["units"] == 0
    flat = position_size({"strength": 0, "rationale": "x"}, equity=10_000, equity_start_of_day=10_000, price=1, atr=1)
    assert flat["reason"] == "no_direction"


# ── futures ─────────────────────────────────────────────────────────────────
def test_contango_costs_a_long_and_backwardation_pays():
    contango = curve_structure(70.0, 71.4, 30)
    assert contango["structure"] == "contango" and contango["roll_yield_annual_long"] < 0
    assert curve_structure(70.0, 69.0, 30)["roll_yield_annual_long"] > 0


def test_roll_window_and_back_adjusted_series_have_no_fake_gap():
    assert roll_due(date(2026, 11, 3), date(2026, 10, 29))["roll_due"] is True
    assert roll_due(date(2026, 12, 20), date(2026, 10, 29))["roll_due"] is False
    series = back_adjust([{"prices": [100, 102], "roll_from": 102, "roll_to": 104}, {"prices": [104, 105]}])
    assert series[1] == pytest.approx(104) and series[2] == 104  # no jump at the roll
    assert series[0] == pytest.approx(100 * 104 / 102)


# ── macro sources ───────────────────────────────────────────────────────────
def _transport(response):
    return httpx.MockTransport(lambda request: response)


def test_cot_net_positions_and_missing_fields():
    rows = [{"market_and_exchange_names": "GOLD - COMMODITY EXCHANGE INC.", "report_date_as_yyyy_mm_dd":
             "2026-10-20T00:00:00.000", "open_interest_all": "402279", "noncomm_positions_long_all": "237142",
             "noncomm_positions_short_all": "37277", "comm_positions_long_all": "59531"}]
    data = asyncio.run(cot_positioning("088691", transport=_transport(httpx.Response(200, json=rows))))
    assert data["noncommercial_net"] == 199865 and data["commercial_net"] is None
    assert data["report_date"] == "2026-10-20"
    assert asyncio.run(cot_positioning("08;DROP"))["reason"] == "invalid_market_code"


def test_keyed_sources_are_unavailable_without_keys_and_keep_gaps_as_none():
    assert asyncio.run(fred_latest("DFII10", None))["reason"] == "key_not_configured"
    assert asyncio.run(eia_latest("petroleum/stoc/wstk", "WCESTUS1", None))["reason"] == "key_not_configured"
    assert asyncio.run(edgar_filings(320193, None))["reason"] == "user_agent_not_configured"
    gap = httpx.Response(200, json={"observations": [{"date": "2026-10-28", "value": "."}]})
    assert asyncio.run(fred_latest("DFII10", "k", transport=_transport(gap)))["value"] is None


def test_edgar_keeps_only_material_filings():
    recent = {"form": ["4", "10-Q", "144", "8-K"], "filingDate": ["d1", "d2", "d3", "d4"],
              "accessionNumber": ["a1", "a2", "a3", "a4"]}
    resp = httpx.Response(200, json={"name": "Apple Inc.", "filings": {"recent": recent}})
    data = asyncio.run(edgar_filings(320193, "SYNDICATE ops@example.org", transport=_transport(resp)))
    assert [f["form"] for f in data["filings"]] == ["10-Q", "8-K"]
    skewed = httpx.Response(200, json={"filings": {"recent": {"form": ["10-K"], "filingDate": [],
                                                              "accessionNumber": ["a"]}}})
    assert asyncio.run(edgar_filings(1, "x ops@example.org", transport=_transport(skewed)))["reason"] == \
        "inconsistent_filings"


# ── hash ledger ─────────────────────────────────────────────────────────────
def test_journal_writes_a_chain_that_detects_tampering():
    journal = TradeJournal(memory=None)
    entry = JournalEntry(signal_id="S1", symbol="XAUUSD", direction="long", confluence_score=96, threshold=95)
    asyncio.run(journal.record_signal(entry))
    asyncio.run(journal.record_decision("S1", "approve"))
    asyncio.run(journal.record_outcome("S1", "win", 2.0))
    ledger = journal.ledger()
    rows = asyncio.run(ledger.rows())
    assert [r["event"] for r in rows] == ["signal", "decision", "outcome"] and rows[0]["prev_hash"] == GENESIS
    assert asyncio.run(ledger.verify())["intact"] is True
    rows[1]["payload"]["decision"] = "reject"  # rewrite history
    broken = verify(rows)
    assert broken["intact"] is False and broken["broken_at"] == 2


def test_ledger_write_failure_is_reported_not_raised():
    class BrokenPool:
        def acquire(self):
            raise ConnectionError("db down")

    assert asyncio.run(HashLedger(BrokenPool()).append("signal", "S", {}))["status"] == "unavailable"
