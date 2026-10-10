"""Host-owned Marshal access helpers. These are not grants."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from src.agent_platform.contracts import AgentProfile, RuntimeKind

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PROFILE_PATH = _REPO_ROOT / "config" / "agents" / "marshal.profile.json"


def load_marshal_manifest() -> dict[str, Any]:
    try:
        payload = json.loads(_PROFILE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("marshal_manifest_unavailable") from exc
    if not isinstance(payload, dict):
        raise ValueError("marshal_manifest_unavailable")
    return payload


def marshal_agent_profile(manifest: Mapping[str, Any] | None = None) -> AgentProfile:
    data = dict(manifest or load_marshal_manifest())
    return AgentProfile(
        agent_id=str(data.get("agent_id", "")),
        hermes_profile=str(data.get("hermes_profile", "")),
        memory_namespace=str(data.get("memory_namespace", "")),
        capabilities=frozenset(data.get("capabilities") or ()),
        resource_scopes=frozenset(data.get("resource_scopes") or ()),
        runtime=RuntimeKind(str(data.get("runtime", "hermes"))),
    )


def marshal_memory_namespace_allowed(target_agent: str) -> bool:
    return target_agent == "marshal"


def marshal_host_control_allowed(manifest: Mapping[str, Any] | None = None) -> bool:
    data = dict(manifest or load_marshal_manifest())
    live = data.get("live_modes") if isinstance(data.get("live_modes"), dict) else {}
    return live.get("host_control") is True and live.get("emergency_lockdown") is True


def marshal_telegram_inbound_allowed(chat_id: str | None, manifest: Mapping[str, Any] | None = None) -> bool:
    data = dict(manifest or load_marshal_manifest())
    channels = data.get("inbound_channels") if isinstance(data.get("inbound_channels"), dict) else {}
    telegram = channels.get("telegram") if isinstance(channels.get("telegram"), dict) else {}
    if telegram.get("enabled") is not True:
        return False
    allowlist = telegram.get("chat_allowlist")
    if not isinstance(allowlist, (list, tuple)) or not allowlist:
        return False
    if not isinstance(chat_id, str) or not chat_id.strip():
        return False
    return chat_id in [item for item in allowlist if isinstance(item, str)]
