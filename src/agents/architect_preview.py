"""Local n8n JSON → mermaid + explanations. Never calls n8n API."""

from __future__ import annotations

import re
from typing import Any, Mapping

from src.agents.architect.flowlint import lint_workflow

_SECRET = re.compile(
    r"(sk-ant-[A-Za-z0-9_-]+|sk-(?:proj-|live-)?[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]+|xox[baprs]-[A-Za-z0-9-]+|AIza[A-Za-z0-9_-]+|Bearer\s+\S+)",
    re.I,
)


def _safe(text: object) -> str:
    return _SECRET.sub("[REDACTED]", str(text))


def _node_id(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", name).strip("_") or "node"
    if cleaned[0].isdigit():
        cleaned = f"n_{cleaned}"
    return cleaned


def workflow_to_mermaid(workflow: Mapping[str, Any]) -> str:
    nodes = workflow.get("nodes") if isinstance(workflow.get("nodes"), list) else []
    connections = workflow.get("connections") if isinstance(workflow.get("connections"), dict) else {}
    lines = ["flowchart TD"]
    for node in nodes:
        if not isinstance(node, dict):
            continue
        name = _safe(node.get("name") or "node")
        ntype = _safe(str(node.get("type") or "").rsplit(".", 1)[-1])
        lines.append(f"    {_node_id(name)}[\"{name}<br/>{ntype}\"]")
    for src, payload in connections.items():
        if not isinstance(payload, dict):
            continue
        for branch in payload.get("main") or []:
            if not isinstance(branch, list):
                continue
            for edge in branch:
                if isinstance(edge, dict) and edge.get("node"):
                    lines.append(f"    {_node_id(_safe(src))} --> {_node_id(_safe(edge['node']))}")
    if len(lines) == 1:
        lines.append("    empty[\"немає вузлів\"]")
    return "\n".join(lines)


def explain_nodes(workflow: Mapping[str, Any]) -> list[dict[str, str]]:
    rows = []
    for node in workflow.get("nodes") or []:
        if not isinstance(node, dict):
            continue
        rows.append(
            {
                "name": _safe(node.get("name") or ""),
                "type": _safe(node.get("type") or ""),
                "role": "trigger" if "trigger" in str(node.get("type") or "").lower() or "webhook" in str(node.get("type") or "").lower() else "step",
            }
        )
    return rows


def build_preview(workflow: Mapping[str, Any]) -> dict[str, Any]:
    """Visual project for Andrii. Does not activate n8n."""
    data = dict(workflow)
    data["active"] = False
    lint = lint_workflow(data)
    return {
        "agent": "architect",
        "status": "preview",
        "active": False,
        "calls_n8n_api": False,
        "mermaid": workflow_to_mermaid(data),
        "explanations": explain_nodes(data),
        "lint_ok": bool(lint.passed),
        "lint_errors": len(lint.errors()),
        "grants_capability": False,
    }


def deliver_after_confirm(workflow: Mapping[str, Any], *, approved: bool) -> dict[str, Any]:
    """Andrii confirmed the picture. Live mount is inactive-only; activate is not granted."""
    from src.agents.architect_n8n import mount_inactive_workflow

    if approved is not True:
        return {"status": "cancelled", "activates_n8n": False, "grants_capability": False}
    preview = build_preview(workflow)
    if not preview["lint_ok"]:
        return {
            "status": "lint_failed",
            "activates_n8n": False,
            "calls_n8n_api": False,
            "lint_errors": preview["lint_errors"],
        }
    return mount_inactive_workflow(workflow, approved=True)
