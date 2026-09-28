"""
EVA SYNDICATE — Runtime configuration assembler.

Reads environment variables (dev fallbacks; production secrets come from Vault)
and produces the nested ``config`` dict consumed by:

  * :func:`src.integrations.build_default_registry`  (Telegram / Google / MCP)
  * :func:`src.voice.build_voice_manager`            (TTS / STT fallback chains)
  * :class:`src.orchestrator.EvaOrchestrator`        (agent-level params)

Design notes
------------
* This module NEVER raises on missing keys — every value is optional. Connectors
  and voice providers degrade gracefully and resolve real secrets from Vault at
  call time; the env values here are only DEV fallbacks / feature toggles.
* Provider priority names in ``.env`` use friendly aliases (``xai``, ``whisper``,
  ``groq``). The voice registry uses canonical keys (``xai_grok``,
  ``whisper_local``, ``groq_whisper``). :func:`_normalize_voice_priority` maps
  between them so a chain configured in ``.env`` actually resolves.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

# Friendly ``.env`` alias -> canonical provider registry key.
_TTS_ALIASES = {
    "xai": "xai_grok",
    "grok": "xai_grok",
    "eleven": "elevenlabs",
    "elevenlabs": "elevenlabs",
    "openai": "openai",
}
_STT_ALIASES = {
    "whisper": "whisper_local",
    "whisper_local": "whisper_local",
    "local": "whisper_local",
    "groq": "groq_whisper",
    "groq_whisper": "groq_whisper",
}


def _split_csv(val: Optional[str]) -> List[str]:
    if not val:
        return []
    return [x.strip() for x in val.split(",") if x.strip()]


def _normalize_voice_priority(raw: Optional[str], aliases: Dict[str, str], default: List[str]) -> List[str]:
    names = _split_csv(raw)
    if not names:
        return default
    out: List[str] = []
    for name in names:
        canonical = aliases.get(name.lower(), name)
        if canonical not in out:
            out.append(canonical)
    return out


def _env(name: str) -> Optional[str]:
    val = os.getenv(name)
    return val if val else None


def build_runtime_config(env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Assemble the runtime config dict from environment variables.

    Parameters
    ----------
    env:
        Optional mapping to read from instead of :data:`os.environ` (used in
        tests). Defaults to the live process environment.
    """
    if env is not None:
        # Temporarily read from the supplied mapping without mutating os.environ.
        get = lambda k: (env.get(k) or None)  # noqa: E731
    else:
        get = _env

    # ── Connectors: only enable a connector when it has enough config to work ──
    enabled: List[str] = []
    google_cfg: Dict[str, Any] = {}
    if get("GOOGLE_SERVICE_ACCOUNT_JSON") or get("GOOGLE_SERVICE_ACCOUNT_FILE") or get("GOOGLE_OAUTH_CLIENT_ID"):
        enabled.append("google_workspace")
        google_cfg = {
            "service_account_json": get("GOOGLE_SERVICE_ACCOUNT_JSON"),
            "service_account_file": get("GOOGLE_SERVICE_ACCOUNT_FILE"),
            "subject": get("GOOGLE_WORKSPACE_SUBJECT"),
            "oauth_client_id": get("GOOGLE_OAUTH_CLIENT_ID"),
            "oauth_client_secret": get("GOOGLE_OAUTH_CLIENT_SECRET"),
            "oauth_refresh_token": get("GOOGLE_OAUTH_REFRESH_TOKEN"),
        }

    telegram_cfg: Dict[str, Any] = {}
    if get("TELEGRAM_BOT_TOKEN") or get("SAM_TELEGRAM_BOT_TOKEN"):
        enabled.append("telegram")
        telegram_cfg = {
            "bot_token": get("TELEGRAM_BOT_TOKEN"),
            "sam_bot_token": get("SAM_TELEGRAM_BOT_TOKEN"),
            "chat_id": get("TELEGRAM_CHAT_ID"),
        }

    mcp_cfg: Dict[str, Any] = {}
    if get("MCP_SERVERS"):
        enabled.append("mcp")
        mcp_cfg = {"signing_key": get("MCP_SIGNING_KEY")}

    # ── Voice: normalize friendly aliases to canonical registry keys ──────────
    tts_priority = _normalize_voice_priority(
        get("TTS_PRIORITY"), _TTS_ALIASES, ["elevenlabs", "xai_grok", "openai"]
    )
    stt_priority = _normalize_voice_priority(
        get("STT_PRIORITY"), _STT_ALIASES, ["whisper_local", "groq_whisper"]
    )

    config: Dict[str, Any] = {
        # ---- integrations registry ----
        "enabled": enabled,
        "google_workspace": google_cfg,
        "telegram": telegram_cfg,
        "mcp": mcp_cfg,
        "mcp_servers": get("MCP_SERVERS") or {},
        # ---- voice manager ----
        "tts_priority": tts_priority,
        "stt_priority": stt_priority,
        "elevenlabs": {
            "voice_id": get("ELEVENLABS_VOICE_ID"),
            "model_id": get("ELEVENLABS_MODEL_ID") or "eleven_multilingual_v2",
        },
        "xai_grok": {"voice": get("XAI_VOICE") or "default"},
        "openai": {
            "model": get("OPENAI_TTS_MODEL") or "tts-1",
            "voice": get("OPENAI_TTS_VOICE") or "alloy",
        },
        "whisper_local": {"url": get("WHISPER_URL") or "http://whisper:9000"},
        "groq_whisper": {},
        # ---- agent-level params (Sam risk engine, thresholds) ----
        "sam": {
            "telegram_chat_id": get("SAM_TELEGRAM_CHAT_ID"),
            "confluence_threshold": _to_float(get("SAM_CONFLUENCE_THRESHOLD"), 95.0),
            "risk_per_trade": _to_float(get("SAM_RISK_PER_TRADE"), 0.01),
            "daily_stop_out": _to_float(get("SAM_DAILY_STOP_OUT"), 0.03),
        },
    }
    return config


def _to_float(val: Optional[str], default: float) -> float:
    try:
        return float(val) if val not in (None, "") else default
    except (TypeError, ValueError):
        return default
