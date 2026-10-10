"""Host-owned Sam access helpers. These are not grants."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from src.agent_platform.contracts import AgentProfile, RuntimeKind

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PROFILE_PATH = _REPO_ROOT / "config" / "agents" / "sam.profile.json"


def load_sam_manifest() -> dict[str, Any]:
    try:
        payload = json.loads(_PROFILE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("sam_manifest_unavailable") from exc
    if not isinstance(payload, dict):
        raise ValueError("sam_manifest_unavailable")
    return payload


def sam_agent_profile(manifest: Mapping[str, Any] | None = None) -> AgentProfile:
    data = dict(manifest or load_sam_manifest())
    return AgentProfile(
        agent_id=str(data.get("agent_id", "")),
        hermes_profile=str(data.get("hermes_profile", "")),
        memory_namespace=str(data.get("memory_namespace", "")),
        capabilities=frozenset(data.get("capabilities") or ()),
        resource_scopes=frozenset(data.get("resource_scopes") or ()),
        runtime=RuntimeKind(str(data.get("runtime", "hermes"))),
    )


def sam_accepts_task(source: str) -> bool:
    return source == "andrii"


def _live(manifest: Mapping[str, Any]) -> dict[str, Any]:
    block = manifest.get("live_modes")
    return dict(block) if isinstance(block, dict) else {}


def sam_auto_invest_allowed(manifest: Mapping[str, Any] | None = None) -> bool:
    """Investments never auto — even if the JSON flag is flipped by mistake."""
    del manifest
    return False


def sam_auto_fx_crypto_armed(manifest: Mapping[str, Any] | None = None) -> bool:
    data = dict(manifest or load_sam_manifest())
    live = _live(data)
    return live.get("auto_fx_crypto") is True and live.get("auto_invest") is not True


def sam_can_place_auto(manifest: Mapping[str, Any] | None = None) -> bool:
    data = dict(manifest or load_sam_manifest())
    caps = data.get("capabilities") or []
    return sam_auto_fx_crypto_armed(data) and "trade.execute" in caps


def sam_telegram_bot_allowed(manifest: Mapping[str, Any] | None = None) -> bool:
    data = dict(manifest or load_sam_manifest())
    live = _live(data)
    inbound = data.get("inbound_channels") if isinstance(data.get("inbound_channels"), dict) else {}
    tg = inbound.get("telegram") if isinstance(inbound.get("telegram"), dict) else {}
    return live.get("telegram_bot") is True and tg.get("enabled") is True
