"""Deploy-time check: are the configured model IDs still served by the providers?

Usage: GEMINI_API_KEY=… ANTHROPIC_API_KEY=… OPENAI_API_KEY=… python -m tools.check_models
Exit code 1 if any configured model is missing from a provider whose key is set.
Keys are read from the environment only and never printed.
"""
from __future__ import annotations

import os
import sys

import httpx

from src.model_registry import DEFAULTS, model_for

PROVIDERS = {
    "gemini": ("GEMINI_API_KEY", lambda k: ("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", {"x-goog-api-key": k}),
               lambda j: {m["name"].split("/", 1)[-1] for m in j.get("models", [])}, ("GEMINI_PRO", "GEMINI_FAST", "GEMINI_FLASH_LATEST", "COUNCIL_GOOGLE", "LLM_CHEAP")),
    "anthropic": ("ANTHROPIC_API_KEY", lambda k: ("https://api.anthropic.com/v1/models?limit=1000", {"x-api-key": k, "anthropic-version": "2023-06-01"}),
                  lambda j: {m["id"] for m in j.get("data", [])}, ("ANTHROPIC_PRIMARY", "ANTHROPIC_DIRECTOR", "LLM_EXPENSIVE")),
    "openai": ("OPENAI_API_KEY", lambda k: ("https://api.openai.com/v1/models", {"Authorization": f"Bearer {k}"}),
               lambda j: {m["id"] for m in j.get("data", [])}, ("OPENAI_PRIMARY",)),
    # OpenRouter publishes its model list without auth, so every OR_* / OPENROUTER_*
    # ID is verified on every run, key or not.
    "openrouter": (None, lambda k: ("https://openrouter.ai/api/v1/models", {}),
                   lambda j: {m["id"] for m in j.get("data", [])},
                   tuple(k for k in DEFAULTS if k.startswith(("OR_", "OPENROUTER_")))),
}


def main() -> int:
    failed = False
    for name, (env, req, parse, keys) in PROVIDERS.items():
        key = "public" if env is None else os.environ.get(env, "").strip()
        if not key:
            print(f"SKIP  {name}: {env} not set")
            continue
        url, headers = req(key)
        try:
            r = httpx.get(url, headers=headers, timeout=20)
            r.raise_for_status()
            available = parse(r.json())
        except Exception as exc:  # noqa: BLE001 - never echo the key/URL
            print(f"ERROR {name}: could not list models ({type(exc).__name__})")
            failed = True
            continue
        for k in keys:
            model = model_for(k)
            ok = model in available
            failed |= not ok
            print(f"{'OK   ' if ok else 'MISSING'} {name}: {k}={model}")
    print("Unchecked keys (xAI direct has no key-less list here):", ", ".join(k for k in DEFAULTS if k.startswith("GROK")))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
