"""Architect readiness. Empty grants stay empty."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.agents.architect_access import (
    architect_gitops_push_allowed,
    architect_n8n_live_allowed,
    load_architect_manifest,
)

_REPO = Path(__file__).resolve().parents[2]


def architect_readiness() -> dict[str, Any]:
    manifest = load_architect_manifest()
    grants_empty = (
        list(manifest.get("capabilities") or []) == []
        and list(manifest.get("resource_scopes") or []) == []
        and list(manifest.get("services_enabled") or []) == []
    )
    return {
        "agent": "architect",
        "activation": manifest.get("activation"),
        "role_status": manifest.get("role_status"),
        "grants_empty": grants_empty,
        "n8n_live": architect_n8n_live_allowed(manifest),
        "gitops_push": architect_gitops_push_allowed(manifest),
        "telegram_bot": (manifest.get("live_modes") or {}).get("telegram_bot") is True,
        "prompt_file_exists": (_REPO / str(manifest.get("prompt_file") or "")).is_file(),
        "eva_cannot_assign": True,
        "knowledge_loaded": (manifest.get("knowledge_bases") or {}).get("architecture", {}).get("status") == "loaded",
        "drive_configured": bool((manifest.get("workspace") or {}).get("drive", {}).get("folder_id")),
        "live_runtime": False,
        "deployable_as_prepared_profile": grants_empty
        and manifest.get("activation") == "prepared_not_enabled",
    }
