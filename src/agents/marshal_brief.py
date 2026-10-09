"""Daily Marshal brief for Eva payload. Eva does not call Marshal."""

from __future__ import annotations

from typing import Any, Iterable, Mapping


def build_daily_brief(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = list(events)
    red = [item for item in rows if item.get("level") == "red"]
    yellow = [item for item in rows if item.get("level") == "yellow"]
    lookups = [item for item in rows if item.get("level") == "observe"]
    lines = [
        f"червоні: {len(red)}",
        f"жовті (лише бриф): {len(yellow)}",
        f"інтернет за командою Андрія (observe): {len(lookups)}",
        "без секретів, без URL, без payload",
    ]
    return {
        "agent": "marshal",
        "status": "brief",
        "for_eva_payload": True,
        "eva_must_not_fetch": True,
        "red_count": len(red),
        "yellow_count": len(yellow),
        "observe_count": len(lookups),
        "summary": "; ".join(lines),
        "open_hitl": len(red),
    }
