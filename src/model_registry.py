"""Single place for LLM model IDs.

Model names go stale quickly (providers retire them). Defaults below are only a
fallback; set ``LLM_MODEL_<KEY>`` in the environment/Vault config to override
without a code change, and run ``python -m tools.check_models`` at deploy time to
verify every configured ID against the provider's own model list.
"""
from __future__ import annotations

import os

DEFAULTS = {
    "GEMINI_PRO": "gemini-2.5-pro",
    # Direct Gemini key (27.10): 2.5-pro/2.5-flash answer 404 "no longer available
    # to new users"; 3.5-flash and 2.5-flash-lite answer. Prefer OpenRouter for Google.
    "GEMINI_FAST": "gemini-3.5-flash",
    "OPENROUTER_FAST": "google/gemini-4-hydrogen",
    "OPENROUTER_DIRECTOR": "anthropic/claude-sonnet-5.5",
    "OPENAI_PRIMARY": "gpt-4o",
    # Owner's Telegram voice notes (src/voice_reply.py); listed by our key on 28.10.
    "OPENAI_TRANSCRIBE": "gpt-4o-mini-transcribe",
    "ANTHROPIC_PRIMARY": "claude-sonnet-5-5",
    "ANTHROPIC_DIRECTOR": "claude-haiku-5-5",
    "GROK_DIRECTOR": "grok-2",
    "COUNCIL_GOOGLE": "gemini-3.5-flash",
    "LLM_CHEAP": "gemini-2.5-flash-lite",
    "LLM_EXPENSIVE": "claude-sonnet-5-5",
    "OPENROUTER_REASONING": "deepseek/deepseek-v4-pro",
    # Per-agent tier routing (src/llm_router.py). OR_* are OpenRouter IDs and are
    # verified against OpenRouter's public model list by tools/check_models.py.
    "OR_CLAUDE_HAIKU": "anthropic/claude-haiku-5.5",
    "OR_CLAUDE_SONNET": "anthropic/claude-sonnet-5.5",
    "OR_CLAUDE_OPUS": "anthropic/claude-opus-5.5",
    "OR_DEEPSEEK_PRO": "deepseek/deepseek-v4-pro",
    "OR_GEMINI_ARGON": "google/gemini-4-argon",
    # 16.11.2026: Gemini 4 Hydrogen (out 12.11) replaces 3.8 Flash. $1.50/$7.50 per 1M tokens,
    # takes images, video and audio. Light work stays on Haiku 5.5 ($0.10/$0.50).
    "OR_GEMINI_HYDROGEN": "google/gemini-4-hydrogen",
    "OR_GPT_LUNA": "openai/gpt-6-luna",
    "OR_GPT_SOL": "openai/gpt-6.1-sol",
    "OR_GROK": "x-ai/grok-4.7",
    # Gateway web search (src/hermes_tools.py): $1/M tokens + $0.005 a search on 06.11.2026.
    "OR_SONAR": "perplexity/sonar",
    "OR_SONAR_PRO": "perplexity/sonar-pro",
    "OR_SONAR_DEEP_RESEARCH": "perplexity/sonar-deep-research",
    "GEMINI_FLASH_LATEST": "gemini-3.5-flash",
    # 19.11.2026: Gemini watches a YouTube link itself (src/video_digest.py), so the server block on yt-dlp does not matter.
    "GEMINI_VIDEO": "gemini-4-hydrogen",
}


def model_for(key: str) -> str:
    """Return the configured model ID for ``key`` (env ``LLM_MODEL_<KEY>`` wins)."""
    if key not in DEFAULTS:
        raise KeyError(f"unknown model key: {key}")
    override = os.environ.get(f"LLM_MODEL_{key}", "").strip()
    return override or DEFAULTS[key]
