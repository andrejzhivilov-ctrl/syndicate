"""Readiness snapshot. Empty grants stay empty; this does not activate Marshal."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.agents.marshal_access import load_marshal_manifest, marshal_host_control_allowed, marshal_telegram_inbound_allowed
from src.agents.marshal_observe import telegram_send_allowed
from src.agents.marshal_skill_scan import resolve_skillspector_binary

_REPO = Path(__file__).resolve().parents[2]


def marshal_readiness() -> dict[str, Any]:
    manifest = load_marshal_manifest()
    binary = resolve_skillspector_binary(manifest)
    grants_empty = (
        list(manifest.get("capabilities") or []) == []
        and list(manifest.get("resource_scopes") or []) == []
        and list(manifest.get("services_enabled") or []) == []
        and list(manifest.get("skills") or []) == []
    )
    return {
        "agent": "marshal",
        "activation": manifest.get("activation"),
        "role_status": manifest.get("role_status"),
        "model_status": manifest.get("model_status"),
        "grants_empty": grants_empty,
        "host_control": marshal_host_control_allowed(manifest),
        "telegram_inbound": marshal_telegram_inbound_allowed("1", manifest),
        "telegram_send": telegram_send_allowed(manifest),
        "skill_scan_binary": binary,
        "skill_scan_installed": binary is not None,
        "skill_scan_llm_pass": manifest.get("skill_scan", {}).get("llm_pass") is True,
        "n8n_control_plane": manifest.get("n8n", {}).get("control_plane") is True,
        "drive_configured": bool(manifest.get("workspace", {}).get("drive", {}).get("folder_id")),
        "knowledge_loaded": manifest.get("knowledge_bases", {}).get("security", {}).get("status") == "loaded",
        "prompt_file_exists": (_REPO / str(manifest.get("prompt_file") or "")).is_file(),
        "deployable_as_prepared_profile": grants_empty and manifest.get("activation") == "prepared_not_enabled",
        "live_runtime": False,
    }
