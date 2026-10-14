"""Prepared Antigravity contract, not a live runtime or Telegram bot.

No providers, credentials, filesystem writes or network calls are implemented.
Request payloads cannot activate the agent or grant permissions.
"""

from __future__ import annotations

from typing import Any


# Telegram command names are a future interface contract, not registered handlers.
ACTION_CAPABILITIES = {
    "app": "antigravity.app.build",
    "img": "antigravity.image.generate",
    "video": "antigravity.video.render",
    "research": "antigravity.research.read",
    "github": "antigravity.github.pr",
    "billing_status": "antigravity.billing.read",
    "history": "antigravity.history.read",
}


class AntigravityAgent:
    """Offline readiness surface. Deliberately not wired into the orchestrator."""

    AGENT_ID = "antigravity"

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload.get("action", "status")
        base = {"agent": self.AGENT_ID, "value": None}
        if not isinstance(action, str):
            return {**base, "status": "rejected", "reason": "action_must_be_string"}
        if action == "status":
            return {
                **base,
                "status": "prepared_not_enabled",
                "live_runtime": False,
                "providers_connected": False,
                "history_ingested": False,
                "available_actions": ["status"],
                "planned_actions": sorted(ACTION_CAPABILITIES),
            }
        if action not in ACTION_CAPABILITIES:
            return {**base, "status": "rejected", "reason": "unknown_action"}
        # Even forged grants/activation in a payload cannot authorize anything.
        # Actual dispatch must be added via the host-owned platform policy + HITL.
        return {
            **base,
            "status": "denied",
            "action": action,
            "reason": "prepared_not_enabled",
            "required_capability": ACTION_CAPABILITIES[action],
            "provider_status": "not_implemented",
        }
