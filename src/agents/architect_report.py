"""Architect → Eva report is payload only. Architect does not call Eva."""

from __future__ import annotations

from typing import Any, Mapping


def build_eva_report(snapshot: Mapping[str, Any] | None = None) -> dict[str, Any]:
    data = dict(snapshot or {})
    waiting = data.get("waiting_hitl")
    drafts = data.get("drafts_inactive")
    lines = [
        f"чернетки inactive: {drafts if drafts is not None else 'невідомо'}",
        f"очікує HITL Андрія: {waiting if waiting is not None else 'невідомо'}",
        "live n8n: не ввімкнено",
        "без секретів і без вигаданого health хоста",
    ]
    return {
        "agent": "architect",
        "status": "brief",
        "for_eva_payload": True,
        "eva_must_not_fetch": True,
        "eva_cannot_assign": True,
        "summary": "; ".join(lines),
    }
