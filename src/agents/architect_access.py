"""Host-owned Architect access helpers. These are not grants."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from src.agent_platform.contracts import ActivationStatus, AgentProfile, RuntimeKind

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PROFILE_PATH = _REPO_ROOT / "config" / "agents" / "architect.profile.json"


def load_architect_manifest() -> dict[str, Any]:
    try:
        payload = json.loads(_PROFILE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("architect_manifest_unavailable") from exc
    if not isinstance(payload, dict):
        raise ValueError("architect_manifest_unavailable")
    return payload


def architect_agent_profile(manifest: Mapping[str, Any] | None = None) -> AgentProfile:
    data = dict(manifest or load_architect_manifest())
    return AgentProfile(
        agent_id=str(data.get("agent_id", "")),
        runtime_profile=str(data.get("runtime_profile", "")),
        memory_namespace=str(data.get("memory_namespace", "")),
        capabilities=frozenset(data.get("capabilities") or ()),
        resource_scopes=frozenset(data.get("resource_scopes") or ()),
        runtime=RuntimeKind(str(data.get("runtime", "hermes"))),
        activation_status=ActivationStatus(str(data.get("activation", "prepared_not_enabled"))),
    )


def architect_accepts_task(source: str) -> bool:
    """Only Andrii may assign work. Eva is not a task source."""
    return source == "andrii"


def architect_n8n_live_allowed(manifest: Mapping[str, Any] | None = None) -> bool:
    data = dict(manifest or load_architect_manifest())
    n8n = data.get("n8n") if isinstance(data.get("n8n"), dict) else {}
    caps = data.get("capabilities") or []
    services = data.get("services_enabled") or []
    return (
        data.get("activation") == "enabled"
        and "n8n" in services
        and n8n.get("status") == "configured"
        and n8n.get("live_api") is True
        and n8n.get("activation") == "live_mount_after_hitl"
        and n8n.get("control_plane") is not True
        and n8n.get("permission_source") is not True
        and "n8n.workflow.mount" in caps
        and "n8n.workflow.activate" not in caps
    )


def architect_gitops_push_allowed(manifest: Mapping[str, Any] | None = None) -> bool:
    data = dict(manifest or load_architect_manifest())
    live = data.get("live_modes") if isinstance(data.get("live_modes"), dict) else {}
    return data.get("activation") == "enabled" and live.get("gitops_push") is True
