"""HITL vs auto path: investments never auto; empty grants cannot place."""

from __future__ import annotations

from src.agents.sam_access import sam_auto_invest_allowed, sam_can_place_auto
from src.agents.sam_broker import submit_lot
from src.agents.sam_policy import classify_venue, decide_execution, layers_complete
from src.agents.sam_ready import sam_readiness
from src.agents.sam_report import build_eva_payload


def _full_layers(score: float) -> dict:
    names = ("smc", "macro", "cot", "derivatives", "news_shield")
    return {
        "confluence_score": score,
        "layers": {name: {"score": 99.0, "missing": False, "veto": False} for name in names},
    }


def test_classify_venue() -> None:
    assert classify_venue("EURUSD") == "forex"
    assert classify_venue("XAUUSD") == "forex"
    assert classify_venue("BTC/USDT") == "crypto"
    assert classify_venue("VOO") == "investment"
    assert classify_venue("AAPL", "ibkr") == "investment"


def test_incomplete_layers_cannot_auto() -> None:
    confluence = {"confluence_score": 99.0, "layers": {"smc": {"score": None, "missing": True}}}
    assert layers_complete(confluence) is False
    plan = decide_execution(symbol="EURUSD", confluence=confluence)
    assert plan["path"] == "no_trade"
    assert plan["auto_execute"] is False


def test_invest_always_hitl_even_at_99() -> None:
    plan = decide_execution(symbol="VOO", confluence=_full_layers(99.5))
    assert plan["path"] == "invest_discuss"
    assert plan["auto_execute"] is False
    assert sam_auto_invest_allowed({"live_modes": {"auto_invest": True}}) is False


def test_fx_99_without_grant_stays_hitl() -> None:
    armed = {
        "capabilities": [],
        "live_modes": {"auto_fx_crypto": True, "auto_invest": False},
    }
    assert sam_can_place_auto(armed) is False
    plan = decide_execution(symbol="EURUSD", confluence=_full_layers(99.2), manifest=armed)
    assert plan["path"] == "auto_eligible_no_grant"
    assert plan["requires_hitl"] is True
    assert plan["auto_execute"] is False


def test_submit_lot_is_unavailable_without_broker() -> None:
    result = submit_lot(
        symbol="EURUSD",
        account_mode="demo",
        approved=True,
        confluence=_full_layers(99.2),
    )
    assert result["status"] == "broker_unavailable"
    assert result["calls_broker"] is False
    assert result["filled"] is False


def test_eva_payload_and_readiness() -> None:
    payload = build_eva_payload({"pnl_24h_usd": 1.0, "pnl_24h_percent": 1.0})
    assert payload["eva_cannot_assign"] is True
    snap = sam_readiness()
    assert snap["grants_empty"] is True
    assert snap["auto_fx_crypto"] is False
    assert snap["auto_invest"] is False
    assert snap["can_place_auto"] is False
    assert snap["telegram_bot"] is False
    assert snap["deployable_as_prepared_profile"] is True
