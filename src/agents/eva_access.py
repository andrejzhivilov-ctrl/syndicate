"""Host-owned Eva access helpers. These are not grants and do not enable Hermes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from src.agent_platform.contracts import AgentProfile, RuntimeKind

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EVA_PROFILE_PATH = _REPO_ROOT / "config" / "agents" / "eva.profile.json"
EVA_MEMORY_NAMESPACE = "agents/eva"


def load_eva_manifest() -> dict[str, Any]:
    """Load the Eva profile manifest; missing/invalid files fail closed."""
    try:
        payload = json.loads(_EVA_PROFILE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("eva_manifest_unavailable") from exc
    if not isinstance(payload, dict):
        raise ValueError("eva_manifest_unavailable")
    return payload


def eva_agent_profile(manifest: Mapping[str, Any] | None = None) -> AgentProfile:
    """Build the control-plane profile from the manifest without inventing grants."""
    data = dict(manifest or load_eva_manifest())
    return AgentProfile(
        agent_id=str(data.get("agent_id", "")),
        hermes_profile=str(data.get("hermes_profile", "")),
        memory_namespace=str(data.get("memory_namespace", "")),
        capabilities=frozenset(data.get("capabilities") or ()),
        resource_scopes=frozenset(data.get("resource_scopes") or ()),
        runtime=RuntimeKind(str(data.get("runtime", "hermes"))),
    )


def eva_memory_namespace_allowed(target_agent: str) -> bool:
    """Own-namespace only. Any other agent id is deny."""
    return target_agent == "eva"


def telegram_inbound_allowed(
    *,
    enabled: bool,
    allowlist: object,
    chat_id: str | None,
) -> bool:
    """Empty or missing allowlist is deny. Unknown bot/chat ids are never invented."""
    if enabled is not True:
        return False
    if not isinstance(allowlist, (list, tuple)) or not allowlist:
        return False
    if not isinstance(chat_id, str) or not chat_id.strip():
        return False
    allowed = [item for item in allowlist if isinstance(item, str) and item.strip()]
    return chat_id in allowed


def eva_telegram_inbound_allowed(chat_id: str | None, manifest: Mapping[str, Any] | None = None) -> bool:
    data = dict(manifest or load_eva_manifest())
    channel = data.get("inbound_channels", {}).get("telegram", {}) if isinstance(data.get("inbound_channels"), dict) else {}
    if not isinstance(channel, dict):
        return False
    return telegram_inbound_allowed(
        enabled=channel.get("enabled") is True,
        allowlist=channel.get("chat_allowlist"),
        chat_id=chat_id,
    )


def extract_telegram_chat_id(payload: Mapping[str, Any] | None) -> str | None:
    """Read a chat id if present; never derive identity from IP, timezone, or metadata."""
    if not isinstance(payload, Mapping):
        return None
    message = payload.get("message")
    if isinstance(message, Mapping):
        chat = message.get("chat")
        if isinstance(chat, Mapping) and chat.get("id") is not None:
            return str(chat.get("id"))
    if payload.get("chat_id") is not None:
        return str(payload.get("chat_id"))
    return None
