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
    "GEMINI_FAST": "gemini-2.5-flash",
    "OPENROUTER_FAST": "google/gemini-2.5-flash",
    "OPENROUTER_DIRECTOR": "anthropic/claude-3.5-sonnet",
    "OPENAI_PRIMARY": "gpt-4o",
    "ANTHROPIC_DIRECTOR": "claude-3-5-haiku-20241022",
    "GROK_DIRECTOR": "grok-2",
    "COUNCIL_GOOGLE": "gemini-2.0-flash",
    "LLM_CHEAP": "gemini-2.0-flash",
    "LLM_EXPENSIVE": "claude-sonnet-4-20250514",
}


def model_for(key: str) -> str:
    """Return the configured model ID for ``key`` (env ``LLM_MODEL_<KEY>`` wins)."""
    if key not in DEFAULTS:
        raise KeyError(f"unknown model key: {key}")
    override = os.environ.get(f"LLM_MODEL_{key}", "").strip()
    return override or DEFAULTS[key]
