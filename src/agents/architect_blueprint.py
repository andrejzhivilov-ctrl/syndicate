"""Blueprint 3-in-1 package for Andrii HITL. Does not activate n8n or send Telegram."""

from __future__ import annotations

from typing import Any, Mapping

from src.agents.architect_access import architect_accepts_task, architect_n8n_live_allowed


def build_blueprint(
    *,
    title: str,
    goal: str,
    source: str,
    mermaid: str = "",
) -> dict[str, Any]:
    if not architect_accepts_task(source):
        return {
            "status": "denied",
            "error": "eva_or_other_cannot_assign_architect",
            "source": source,
            "activates_n8n": False,
        }
    return {
        "status": "BLUEPRINT",
        "title": title,
        "goal": goal,
        "source": "andrii",
        "passport": {
            "goal": goal,
            "active": False,
            "core_nodes_only": True,
            "secrets_in_json": False,
        },
        "schema": mermaid or "(немає схеми)",
        "buttons": ["approve_design", "rework", "cancel"],
        "timeout_default": "cancel",
        "sends_telegram": False,
        "activates_n8n": False,
        "grants_capability": False,
        "n8n_live": architect_n8n_live_allowed(),
    }


def apply_blueprint_decision(blueprint: Mapping[str, Any], decision: str) -> dict[str, Any]:
    """Approve design ≠ activate workflow."""
    if blueprint.get("status") != "BLUEPRINT":
        return {"status": "denied", "error": "not_a_blueprint"}
    if decision != "approve_design":
        return {
            "status": "cancelled" if decision == "cancel" else "rework",
            "activates_n8n": False,
            "grants_capability": False,
        }
    return {
        "status": "design_approved_inactive",
        "activates_n8n": False,
        "active": False,
        "grants_capability": False,
        "note": "Потрібен окремий HITL на live n8n, якого немає в grants.",
    }
