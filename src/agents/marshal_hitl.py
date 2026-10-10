"""HITL card builder. Does not send Telegram and does not grant rights."""

from __future__ import annotations

from typing import Any, Mapping

from src.agents.marshal_observe import classify_event
from src.agents.marshal_skill_scan import scan_skill_proposal


def build_alert_card(event: Mapping[str, Any]) -> dict[str, Any] | None:
    """Andrii-requested web lookup produces no card. Only red is HITL."""
    level = classify_event(event)
    if level != "red":
        return None
    return {
        "status": "RED",
        "hitl_required": True,
        "agent": str(event.get("actor") or "unknown"),
        "action": str(event.get("action") or "unknown"),
        "risk": str(event.get("action") or "unknown"),
        "buttons": ["allow", "deny", "review"],
        "timeout_default": "deny",
        "sends_telegram": False,
        "grants_capability": False,
        "details": "без секретів і без payload",
    }


def build_skill_proposal(
    path: str,
    *,
    reason: str,
    scan_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    scan = dict(scan_result) if scan_result is not None else scan_skill_proposal(path)
    approve_blocked = scan.get("status") != "scanned" or scan.get("recommendation") == "do_not_install"
    return {
        "status": "SKILL_PROPOSAL",
        "hitl_required": True,
        "path": path,
        "reason": reason,
        "scan": {
            "status": scan.get("status"),
            "risk_score": scan.get("risk_score"),
            "recommendation": scan.get("recommendation"),
            "error": scan.get("error"),
        },
        "buttons": ["deny", "review"] if approve_blocked else ["allow", "deny", "review"],
        "approve_means_grant": False,
        "installs_skill": False,
        "sends_telegram": False,
        "note": "Погодити ≠ рядок у capabilities. Немає скану або do_not_install — не ставити.",
    }
