"""Live n8n mount after Andrii HITL. n8n is not a control plane or grant source."""

from __future__ import annotations

import json
import os
from typing import Any, Mapping
from urllib.parse import urlparse

import httpx

from src.agent_platform.contracts import AccessRequest, ActionClass, DecisionStatus
from src.agent_platform.policy import AgentPolicy
from src.agents.architect.flowlint import lint_workflow
from src.agents.architect_access import architect_agent_profile, architect_n8n_live_allowed
from src.agents.architect_preview import build_preview

_API_KEY_ENV = "N8N_API_KEY"
_BASE_URL_ENV = "N8N_BASE_URL"


def n8n_credentials_from_env(env: Mapping[str, str] | None = None) -> tuple[str | None, str | None]:
    source = env if env is not None else os.environ
    base = str(source.get(_BASE_URL_ENV) or "").strip().rstrip("/")
    key = str(source.get(_API_KEY_ENV) or "").strip()
    if not base or not key:
        return None, None
    parsed = urlparse(base)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None, None
    return base, key


def _policy_allows_mount(*, approved: bool) -> dict[str, Any] | None:
    if approved is not True:
        return {"status": "cancelled", "activates_n8n": False, "error": "hitl_not_approved"}
    if not architect_n8n_live_allowed():
        return {"status": "denied", "error": "n8n_live_not_granted", "activates_n8n": False}
    decision = AgentPolicy().evaluate(
        architect_agent_profile(),
        AccessRequest(
            agent_id="architect",
            capability="n8n.workflow.mount",
            action_class=ActionClass.PRODUCTION_DEPLOYMENT,
            resource_scope="n8n/live",
        ),
    )
    if decision.status is DecisionStatus.DENIED:
        return {"status": "denied", "error": decision.code.value, "activates_n8n": False}
    return None


def mount_inactive_workflow(
    workflow: Mapping[str, Any],
    *,
    approved: bool,
    env: Mapping[str, str] | None = None,
    transport: httpx.BaseTransport | None = None,
) -> dict[str, Any]:
    """Create the workflow on live n8n as active=false. Never activates it."""
    blocked = _policy_allows_mount(approved=approved)
    if blocked is not None:
        return {"agent": "architect", **blocked, "calls_n8n_api": False, "grants_capability": False}

    data = dict(workflow)
    data["active"] = False
    lint = lint_workflow(data)
    if not lint.passed:
        return {
            "agent": "architect",
            "status": "lint_failed",
            "activates_n8n": False,
            "calls_n8n_api": False,
            "lint_errors": len(lint.errors()),
        }

    base, key = n8n_credentials_from_env(env)
    if not base or not key:
        return {
            "agent": "architect",
            "status": "mount_unavailable",
            "error": "n8n_env_missing",
            "activates_n8n": False,
            "calls_n8n_api": False,
            "note": f"Set {_BASE_URL_ENV} and {_API_KEY_ENV} on the host. Not in the profile.",
        }

    headers = {"X-N8N-API-KEY": key, "Content-Type": "application/json"}
    try:
        with httpx.Client(transport=transport, timeout=30.0) as client:
            response = client.post(f"{base}/api/v1/workflows", headers=headers, json=data)
    except httpx.HTTPError as exc:
        return {
            "agent": "architect",
            "status": "mount_failed",
            "error": type(exc).__name__,
            "activates_n8n": False,
            "calls_n8n_api": True,
        }

    if response.status_code >= 400:
        return {
            "agent": "architect",
            "status": "mount_failed",
            "error": f"http_{response.status_code}",
            "activates_n8n": False,
            "calls_n8n_api": True,
        }

    body: Any
    try:
        body = response.json()
    except json.JSONDecodeError:
        body = {}
    workflow_id = None
    if isinstance(body, dict):
        workflow_id = body.get("id")
        nested = body.get("data")
        if workflow_id is None and isinstance(nested, dict):
            workflow_id = nested.get("id")
    preview = build_preview(data)
    return {
        "agent": "architect",
        "status": "mounted_inactive",
        "n8n_workflow_id": workflow_id,
        "active": False,
        "activates_n8n": False,
        "calls_n8n_api": True,
        "lint_ok": True,
        "mermaid": preview["mermaid"],
        "explanations": preview["explanations"],
        "grants_capability": False,
        "note": "Змонтовано inactive. Activate — окремий HITL, capability n8n.workflow.activate не видана.",
    }
