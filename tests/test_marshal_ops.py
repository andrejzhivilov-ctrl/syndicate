"""Observe, HITL, brief, readiness — still no grants."""

from __future__ import annotations

from src.agents.marshal_brief import build_daily_brief
from src.agents.marshal_hitl import build_alert_card, build_skill_proposal
from src.agents.marshal_observe import classify_event, record_event, telegram_send_allowed
from src.agents.marshal_ready import marshal_readiness


def test_andrii_web_lookup_is_observe_not_hitl() -> None:
    event = {"actor": "eva", "action": "web_search", "andrii_requested": True, "dest_class": "web"}
    stored = record_event(event)
    assert classify_event(event) == "observe"
    assert stored["alert"] is False
    assert stored["block"] is False
    assert stored["url"] is None
    assert stored["body"] is None
    assert build_alert_card(event) is None


def test_critical_leak_builds_red_card_without_telegram() -> None:
    event = {"actor": "sam", "action": "secret_exfil"}
    card = build_alert_card(event)
    assert card is not None
    assert card["status"] == "RED"
    assert card["sends_telegram"] is False
    assert card["grants_capability"] is False
    assert card["timeout_default"] == "deny"


def test_skill_proposal_without_scan_cannot_look_clean() -> None:
    card = build_skill_proposal(
        "/tmp/missing-skill",
        reason="demo",
        scan_result={"status": "scan_unavailable", "recommendation": "unknown", "error": "skillspector_not_installed"},
    )
    assert "allow" not in card["buttons"]
    assert card["installs_skill"] is False
    assert card["approve_means_grant"] is False


def test_brief_is_payload_only() -> None:
    events = [
        record_event({"actor": "eva", "action": "web_search", "andrii_requested": True}),
        record_event({"actor": "fin", "action": "leak"}),
    ]
    brief = build_daily_brief(events)
    assert brief["for_eva_payload"] is True
    assert brief["eva_must_not_fetch"] is True
    assert brief["red_count"] == 1
    assert brief["observe_count"] == 1


def test_readiness_keeps_grants_empty_and_channels_denied() -> None:
    snap = marshal_readiness()
    assert snap["grants_empty"] is True
    assert snap["host_control"] is False
    assert snap["telegram_inbound"] is False
    assert snap["telegram_send"] is False
    assert snap["skill_scan_llm_pass"] is False
    assert snap["n8n_control_plane"] is False
    assert snap["drive_configured"] is False
    assert snap["live_runtime"] is False
    assert snap["deployable_as_prepared_profile"] is True
    assert telegram_send_allowed() is False
