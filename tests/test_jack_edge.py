"""Jack's edge validation (29.10): de-vig methods, palpable errors, CLV, calibration,
bounded qualitative adjustments, one market shape, no martingale."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import pytest

from src.agents.jack import JackAgent
from src.agents.jack.markets import normalize
from src.agents.jack.quant import evaluate, fair_probabilities
from src.agents.jack.tracker import _calibration, _clv


@pytest.fixture(autouse=True)
def isolated_store(monkeypatch, tmp_path):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))


def run(agent, action, **payload):
    return asyncio.run(agent.execute({"action": action, **payload}))


def signal(**updates):
    return {"probability": 0.6, "decimal_odds": 2, "bankroll": 1000,
            "observed_at": datetime.now(timezone.utc).isoformat(), "model_source": "test-fixture",
            "event_id": "event-1", "market": "winner", "selection": "home", **updates}


SHARP = [1.55, 4.2, 6.5]  # favourite / draw / longshot, ~4.4% margin


@pytest.mark.parametrize("method", ["proportional", "power", "shin"])
def test_every_method_returns_a_proper_distribution(method):
    probs = fair_probabilities(SHARP, method)
    assert sum(probs) == pytest.approx(1) and all(0 < p < 1 for p in probs)


def test_shin_and_power_take_more_margin_from_the_longshot():
    prop, power, shin = (fair_probabilities(SHARP, m) for m in ("proportional", "power", "shin"))
    assert shin[2] < prop[2] and power[2] < prop[2]
    assert shin[0] > prop[0] and power[0] > prop[0]


def test_unknown_method_and_bad_markets_are_rejected():
    with pytest.raises(ValueError):
        fair_probabilities(SHARP, "magic")
    with pytest.raises(ValueError):
        fair_probabilities([2.0])


def test_palpable_error_is_blocked_for_a_manual_check():
    result = evaluate(signal(probability=0.65))
    assert result["eligible"] is False and result["requires_manual_check"] is True
    assert evaluate(signal())["eligible"] is True  # EV exactly 20% is still the boundary, not an error


def test_qualitative_adjustments_are_bounded_sourced_and_returned():
    adj = [{"factor": "key striker out", "delta": -0.03, "source": "club statement 29.10"}]
    result = evaluate(signal(probability=0.58, adjustments=adj))
    assert result["probability"] == pytest.approx(0.55) and result["adjustments"][0]["source"]
    with pytest.raises(ValueError):
        evaluate(signal(adjustments=[{"factor": "vibes", "delta": 0.2, "source": "llm"}]))
    with pytest.raises(ValueError):
        evaluate(signal(adjustments=[{"factor": f"f{i}", "delta": 0.02, "source": "s"} for i in range(3)]))
    with pytest.raises(ValueError):
        evaluate(signal(adjustments=[{"factor": "no source", "delta": 0.01}]))


@pytest.mark.parametrize("field", ["stake", "stake_override", "progression", "martingale", "multiplier"])
def test_caller_can_never_size_or_escalate_a_stake(field):
    with pytest.raises(ValueError, match="manual_stake_or_progression_forbidden"):
        evaluate(signal(**{field: 1}))


def test_clv_is_recorded_at_settlement_and_reported():
    agent = JackAgent()
    record = run(agent, "record_paper", **signal())["record"]
    settled = run(agent, "settle_paper", record_id=record["id"], outcome="loss", closing_odds=1.8,
                  closing_source="pinnacle_fair")
    assert settled["record"]["clv"] == pytest.approx(2 / 1.8 - 1)
    report = run(agent, "report")
    assert report["clv"]["count"] == 1 and report["clv"]["positive_share"] == 1
    assert report["calibration"]["brier"] == pytest.approx(0.36)
    assert report["stake_rule"] == "quarter_kelly_capped_per_event_no_progression"


def test_empty_metrics_are_none_not_zero():
    assert _clv([]) == {"count": 0, "average": None, "positive_share": None}
    assert _calibration([])["brier"] is None and _calibration([])["log_loss"] is None


def test_markets_from_any_source_get_one_shape():
    market = normalize({"event_id": "e1", "sport": "Football", "bookmaker": "Pinnacle", "market": "TOTAL",
                        "line": 2.25, "selections": {"Over": 1.95, "under": 1.9},
                        "observed_at": "2026-10-29T10:00:00+02:00"})
    assert market["market"] == "total" and market["line"] == 2.25
    assert market["selections"] == [{"name": "over", "odds": 1.95}, {"name": "under", "odds": 1.9}]
    assert market["observed_at"] == "2026-10-29T08:00:00+00:00"
    bad = {"event_id": "e1", "sport": "f", "bookmaker": "b", "observed_at": "2026-10-29T10:00:00+00:00"}
    for broken in ({"market": "total", "line": 2.3, "selections": {"over": 2, "under": 2}},
                   {"market": "1x2", "selections": {"home": 2, "away": 2}},
                   {"market": "corners_exact", "selections": {}},
                   {"market": "moneyline", "line": 1, "selections": {"home": 2, "away": 2}}):
        with pytest.raises(ValueError):
            normalize({**bad, **broken})


def test_agent_exposes_normalize_and_shin_benchmark_by_default():
    agent = JackAgent()
    assert "normalize" in run(agent, "capabilities")["available_actions"]
    bench = run(agent, "benchmark", odds=SHARP)
    assert bench["method"] == "shin_vig_removal"
