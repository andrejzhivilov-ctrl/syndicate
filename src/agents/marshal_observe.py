"""Layer A: metadata-only observe. Not a grant and not a Telegram sender."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from src.agents.marshal_access import load_marshal_manifest

CRITICAL_ACTIONS = frozenset(
    {
        "leak",
        "secret_exfil",
        "skill_install",
        "mcp_connect",
        "grant_expand",
        "production_deploy",
        "financial_execute",
        "delete",
        "exfil",
    }
)

WEB_LOOKUP_ACTIONS = frozenset({"web_lookup", "web_search", "web_fetch"})


def _andrii_requested(event: Mapping[str, Any]) -> bool:
    return event.get("andrii_requested") is True


def classify_event(event: Mapping[str, Any]) -> str:
    """yellow stays in the brief; red is critical HITL; lookup is observe-only."""
    action = str(event.get("action") or "")
    if action in CRITICAL_ACTIONS:
        return "red"
    if action in WEB_LOOKUP_ACTIONS and _andrii_requested(event):
        return "observe"
    if action in WEB_LOOKUP_ACTIONS:
        return "observe"
    return "yellow"


def record_event(event: Mapping[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    """Keep metadata only. Drop bodies, URLs with query, secrets."""
    stamp = now or datetime.now(timezone.utc)
    level = classify_event(event)
    return {
        "agent": "marshal",
        "ts": stamp.isoformat(),
        "actor": str(event.get("actor") or "unknown"),
        "action": str(event.get("action") or "unknown"),
        "dest_class": str(event.get("dest_class") or "unknown"),
        "andrii_requested": _andrii_requested(event),
        "level": level,
        "alert": level == "red",
        "block": False,
        "body": None,
        "url": None,
    }


def telegram_send_allowed(manifest: Mapping[str, Any] | None = None) -> bool:
    """Outbound Telegram is a service grant. Empty services_enabled is deny."""
    data = dict(manifest or load_marshal_manifest())
    live = data.get("live_modes") if isinstance(data.get("live_modes"), dict) else {}
    services = data.get("services_enabled") or []
    return live.get("telegram_bot") is True and "telegram" in services
