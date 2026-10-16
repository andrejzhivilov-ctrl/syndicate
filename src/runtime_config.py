"""
SYNDICATE — Runtime configuration assembler v4.0.

Reads environment variables (dev fallbacks; production secrets come from Vault)
and produces the nested ``config`` dict consumed by:

  * :func:`src.integrations.build_default_registry`  (Telegram / Google / MCP)
  * :func:`src.voice.build_voice_manager`            (TTS / STT fallback chains)
  * :class:`src.orchestrator.EvaOrchestrator`        (agent-level params)
  * :class:`src.confidence.ConfidenceBudget`         (escalation thresholds)
  * :class:`src.lessons.LessonsStore`                (anti-fragility memory)
  * :class:`src.pii.PIIRedactor`                     (PII masking config)

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

from src.embeddings import EMBEDDING_DIM

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


def _to_float(val: Optional[str], default: float) -> float:
    try:
        return float(val) if val not in (None, "") else default
    except (TypeError, ValueError):
        return default


def _to_bool(val: Optional[str], default: bool = False) -> bool:
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")


def build_runtime_config(env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Assemble the runtime config dict from environment variables.

    Parameters
    ----------
    env:
        Optional mapping to read from instead of :data:`os.environ` (used in
        tests). Defaults to the live process environment.
    """
    if env is not None:
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
        # ── integrations registry ──
        "enabled": enabled,
        "google_workspace": google_cfg,
        "telegram": telegram_cfg,
        "mcp": mcp_cfg,
        "mcp_servers": get("MCP_SERVERS") or {},
        # ── voice manager ──
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
        # ── agent-level params (Sam risk engine, thresholds) ──
        "sam": {
            "telegram_chat_id": get("SAM_TELEGRAM_CHAT_ID"),
            "confluence_threshold": _to_float(get("SAM_CONFLUENCE_THRESHOLD"), 95.0),
            "risk_per_trade": _to_float(get("SAM_RISK_PER_TRADE"), 0.01),
            "daily_stop_out": _to_float(get("SAM_DAILY_STOP_OUT"), 0.03),
        },

        # ═══════════════════════════════════════════════════════════════
        # v4.0 NEW: Confidence Budget — per-agent escalation thresholds
        # ═══════════════════════════════════════════════════════════════
        "confidence": {
            # Default thresholds (overridden per-agent below)
            "default_act_threshold": _to_float(get("CONFIDENCE_DEFAULT_ACT"), 0.80),
            "default_ask_threshold": _to_float(get("CONFIDENCE_DEFAULT_ASK"), 0.45),
            # Per-agent overrides
            "agents": {
                "sam": {
                    # Sam NEVER auto-executes. Every signal goes to HITL.
                    "act_threshold": _to_float(get("SAM_ACT_THRESHOLD"), 1.0),
                    "ask_threshold": _to_float(get("SAM_ASK_THRESHOLD"), 0.0),
                },
                "doc": {
                    "act_threshold": _to_float(get("DOC_ACT_THRESHOLD"), 0.85),
                    "ask_threshold": _to_float(get("DOC_ASK_THRESHOLD"), 0.50),
                },
                "fin": {
                    "act_threshold": _to_float(get("FIN_ACT_THRESHOLD"), 0.85),
                    "ask_threshold": _to_float(get("FIN_ASK_THRESHOLD"), 0.50),
                },
                "architect": {
                    "act_threshold": _to_float(get("ARCHITECT_ACT_THRESHOLD"), 0.75),
                    "ask_threshold": _to_float(get("ARCHITECT_ASK_THRESHOLD"), 0.40),
                },
                "sentinel": {
                    "act_threshold": _to_float(get("SENTINEL_ACT_THRESHOLD"), 0.90),
                    "ask_threshold": _to_float(get("SENTINEL_ASK_THRESHOLD"), 0.60),
                },
                "eva": {
                    "act_threshold": _to_float(get("EVA_ACT_THRESHOLD"), 0.80),
                    "ask_threshold": _to_float(get("EVA_ASK_THRESHOLD"), 0.45),
                },
            },
        },

        # ═══════════════════════════════════════════════════════════════
        # v4.0 NEW: Lessons Layer — anti-fragility config
        # ═══════════════════════════════════════════════════════════════
        "lessons": {
            "enabled": _to_bool(get("LESSONS_ENABLED"), default=True),
            "min_similarity": _to_float(get("LESSONS_MIN_SIMILARITY"), 0.72),
            "max_results": int(get("LESSONS_MAX_RESULTS") or "5"),
            "cleanup_expired_hours": int(get("LESSONS_CLEANUP_HOURS") or "24"),
        },

        # ═══════════════════════════════════════════════════════════════
        # v4.0 NEW: Semantic Response Cache — token savings
        # ═══════════════════════════════════════════════════════════════
        "response_cache": {
            "enabled": _to_bool(get("RESPONSE_CACHE_ENABLED"), default=True),
            "similarity_threshold": _to_float(get("CACHE_SIMILARITY_THRESHOLD"), 0.95),
            "dynamic_ttl_hours": int(get("CACHE_DYNAMIC_TTL_HOURS") or "24"),
            "static_ttl_hours": int(get("CACHE_STATIC_TTL_HOURS") or "168"),  # 7 days
        },

        # ═══════════════════════════════════════════════════════════════
        # v4.0 NEW: PII Redaction — data masking before LLM
        # ═══════════════════════════════════════════════════════════════
        "pii": {
            "enabled": _to_bool(get("PII_REDACTION_ENABLED"), default=True),
            "redact_in_logs": _to_bool(get("PII_REDACT_LOGS"), default=True),
        },

        # ═══════════════════════════════════════════════════════════════
        # v4.0 NEW: Eva Curator — proactive life management
        # ═══════════════════════════════════════════════════════════════
        "eva_curator": {
            "weekly_review_day": get("EVA_WEEKLY_REVIEW_DAY") or "sunday",
            "weekly_review_hour": int(get("EVA_WEEKLY_REVIEW_HOUR") or "20"),
            "deadline_alert_days": int(get("EVA_DEADLINE_ALERT_DAYS") or "7"),
            "decision_review_lookback_days": int(get("EVA_DECISION_REVIEW_DAYS") or "60"),
        },

        # ═══════════════════════════════════════════════════════════════
        # v4.0 NEW: Doc Health — readiness & health config
        # ═══════════════════════════════════════════════════════════════
        "doc": {
            "readiness_red_threshold": _to_float(get("DOC_READINESS_RED"), 40.0),
            "readiness_yellow_threshold": _to_float(get("DOC_READINESS_YELLOW"), 65.0),
            "deload_trigger_days": int(get("DOC_DELOAD_TRIGGER_DAYS") or "3"),
            "water_target_ml": int(get("DOC_WATER_TARGET_ML") or "2500"),
        },

        # ═══════════════════════════════════════════════════════════════
        # Semantic memory: self-hosted embeddings (BGE-M3, 1024 dims)
        # An empty EMBEDDINGS_URL disables vector search deliberately — episodic
        # memory keeps working, so this is a mode, not a misconfiguration.
        # ═══════════════════════════════════════════════════════════════
        "embeddings": {
            "url": (get("EMBEDDINGS_URL") or "").strip(),
            "model": (get("EMBEDDINGS_MODEL") or "bge-m3").strip(),
            "dimensions": int(get("EMBEDDINGS_DIM") or str(EMBEDDING_DIM)),
            "timeout": _to_float(get("EMBEDDINGS_TIMEOUT"), 30.0),
            "enabled": bool((get("EMBEDDINGS_URL") or "").strip()),
        },

        # ═══════════════════════════════════════════════════════════════
        # v4.0 NEW: Tiered LLM routing
        # ═══════════════════════════════════════════════════════════════
        "llm_routing": {
            "cheap_model": get("LLM_CHEAP_MODEL") or "gemini-2.0-flash",
            "expensive_model": get("LLM_EXPENSIVE_MODEL") or "claude-sonnet-4-20250514",
            # Tasks routed to cheap model (formatting, simple routing, health checks)
            "cheap_tasks": _split_csv(get("LLM_CHEAP_TASKS")) or [
                "summarize", "health", "status", "morning_data",
                "compliance_check", "deadline_check", "social_pulse",
            ],
            # Tasks routed to expensive model (analysis, trading, code review)
            "expensive_tasks": _split_csv(get("LLM_EXPENSIVE_TASKS")) or [
                "evaluate_setup", "trade_decision", "review_code",
                "biomarker_trend", "weekly_review",
            ],
        },
    }
    for agent_id in ("oscar", "tyler", "jack", "alice"):
        prefix = agent_id.upper()
        config[agent_id] = {
            "enabled": _to_bool(get(f"{prefix}_WORKER_ENABLED")),
            "worker_url": get(f"{prefix}_WORKER_URL"),
            "allowed_actions": _split_csv(get(f"{prefix}_COORDINATOR_ACTIONS")) or ["capabilities"],
        }
    return config
