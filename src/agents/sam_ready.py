"""Sam readiness. Empty grants stay empty. Does not activate trading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.agents.sam_access import (
    load_sam_manifest,
    sam_auto_fx_crypto_armed,
    sam_auto_invest_allowed,
    sam_can_place_auto,
    sam_telegram_bot_allowed,
)

_REPO = Path(__file__).resolve().parents[2]


def sam_readiness() -> dict[str, Any]:
    manifest = load_sam_manifest()
    grants_empty = (
        list(manifest.get("capabilities") or []) == []
        and list(manifest.get("resource_scopes") or []) == []
        and list(manifest.get("services_enabled") or []) == []
    )
    live = manifest.get("live_modes") or {}
    return {
        "agent": "sam",
        "activation": manifest.get("activation"),
        "role_status": manifest.get("role_status"),
        "grants_empty": grants_empty,
        "auto_fx_crypto": sam_auto_fx_crypto_armed(manifest),
        "auto_invest": sam_auto_invest_allowed(manifest),
        "can_place_auto": sam_can_place_auto(manifest),
        "telegram_bot": sam_telegram_bot_allowed(manifest),
        "voice": live.get("voice") is True,
        "broker_demo": live.get("broker_demo") is True,
        "broker_live": live.get("broker_live") is True,
        "broker": (manifest.get("execution") or {}).get("broker"),
        "n8n_control_plane": (manifest.get("n8n") or {}).get("control_plane") is True,
        "eva_cannot_assign": True,
        "knowledge_loaded": (manifest.get("knowledge_bases") or {}).get("quant", {}).get("status") == "loaded",
        "prompt_file_exists": (_REPO / str(manifest.get("prompt_file") or "")).is_file(),
        "live_runtime": False,
        "deployable_as_prepared_profile": grants_empty
        and manifest.get("activation") == "prepared_not_enabled"
        and live.get("auto_invest") is not True,
    }
