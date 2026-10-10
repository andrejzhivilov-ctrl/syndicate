"""Architect ops: Andrii-only tasks, Eva reports payload-only, n8n inactive-only."""

from __future__ import annotations

from src.agents.architect import n8n_builder
from src.agents.architect_access import architect_accepts_task, architect_n8n_live_allowed
from src.agents.architect_preview import build_preview, deliver_after_confirm
from src.agents.architect_blueprint import apply_blueprint_decision, build_blueprint
from src.agents.architect_ready import architect_readiness
from src.agents.architect_report import build_eva_report


def test_eva_cannot_assign_architect() -> None:
    assert architect_accepts_task("andrii") is True
    assert architect_accepts_task("eva") is False
    denied = build_blueprint(title="x", goal="y", source="eva")
    assert denied["status"] == "denied"
    assert denied["activates_n8n"] is False


def test_blueprint_approve_does_not_activate_n8n() -> None:
    draft = build_blueprint(title="mail", goal="draft ingest", source="andrii")
    assert draft["status"] == "BLUEPRINT"
    assert draft["sends_telegram"] is False
    assert draft["activates_n8n"] is False
    decided = apply_blueprint_decision(draft, "approve_design")
    assert decided["activates_n8n"] is False
    assert decided["active"] is False
    assert decided["grants_capability"] is False
    # Live mount is granted; approve_design still must not activate.
    assert architect_n8n_live_allowed() is True


def test_eva_report_is_payload_only() -> None:
    report = build_eva_report({"drafts_inactive": 2, "waiting_hitl": 1})
    assert report["for_eva_payload"] is True
    assert report["eva_cannot_assign"] is True
    assert report["eva_must_not_fetch"] is True


def test_preview_and_confirm_do_not_call_n8n() -> None:
    workflow = n8n_builder.build_workflow(name="preview-draft", trigger="manual")
    preview = build_preview(workflow)
    assert preview["active"] is False
    assert preview["calls_n8n_api"] is False
    assert "flowchart" in preview["mermaid"]
    assert preview["explanations"]
    delivered = deliver_after_confirm(workflow, approved=True)
    assert delivered["activates_n8n"] is False
    assert delivered["status"] in {"mounted_inactive", "mount_unavailable"}
    cancelled = deliver_after_confirm(workflow, approved=False)
    assert cancelled["status"] == "cancelled"


def test_architect_readiness_empty_grants() -> None:
    snap = architect_readiness()
    assert snap["grants_empty"] is False
    assert snap["n8n_live"] is True
    assert snap["gitops_push"] is False
    assert snap["telegram_bot"] is False
    assert snap["eva_cannot_assign"] is True
    assert snap["n8n_mount_granted"] is True
    assert snap["n8n_activate_granted"] is False
    assert snap["knowledge_loaded"] is False
    assert snap["drive_configured"] is False
    assert snap["deployable_as_prepared_profile"] is True
