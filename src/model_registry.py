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
    "OPENROUTER_FAST": "google/gemini-3.8-flash",
    "OPENROUTER_DIRECTOR": "anthropic/claude-sonnet-5.5",
    "OPENAI_PRIMARY": "gpt-4o",
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
    "OR_DEEPSEEK_FLASH": "deepseek/deepseek-v4.1-flash",
    "OR_DEEPSEEK_PRO": "deepseek/deepseek-v4-pro",
    "OR_QWEN_MAX": "qwen/qwen3.8-max-0902",
    "OR_GEMINI_ARGON": "google/gemini-4-argon",
    "OR_GEMINI_FLASH": "google/gemini-3.8-flash",
    "OR_GPT_LUNA": "openai/gpt-6-luna",
    "OR_GPT_SOL": "openai/gpt-6.1-sol",
    "OR_GROK": "x-ai/grok-4.7",
    "OR_SONAR_PRO": "perplexity/sonar-pro",
    "OR_SONAR_DEEP_RESEARCH": "perplexity/sonar-deep-research",
    "GEMINI_FLASH_LATEST": "gemini-3.5-flash",
}


def model_for(key: str) -> str:
    """Return the configured model ID for ``key`` (env ``LLM_MODEL_<KEY>`` wins)."""
    if key not in DEFAULTS:
        raise KeyError(f"unknown model key: {key}")
    override = os.environ.get(f"LLM_MODEL_{key}", "").strip()
    return override or DEFAULTS[key]
