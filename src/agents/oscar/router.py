"""Task-specific model selection, bounded context and PII-safe invocation."""
from __future__ import annotations

import json
from typing import Any

from src.pii import PIIRedactor

ROUTES = {
    "draft": "grok", "reply": "grok", "newsletter": "grok", "thumbnail": "grok",
    "research": "gemini", "pain_map": "gemini", "channel_analysis": "gemini",
    "classify": "haiku", "tags": "haiku", "queue_review": "haiku",
}


class TriLLMRouter:
    def __init__(self, providers: dict[str, Any] | None = None) -> None:
        self.providers = dict(providers or {})

    async def invoke(self, task: str, system: str, content: Any) -> dict:
        if task not in ROUTES:
            raise ValueError("unknown_llm_task")
        provider = ROUTES[task]
        client = self.providers.get(provider)
        if client is None:
            return {"status": "unavailable", "value": None, "provider": provider,
                    "warning": "provider_not_configured"}
        raw = json.dumps(content, ensure_ascii=False, allow_nan=False)
        # Actual model context limits depend on configured model; do not assume 2M.
        if len(raw) > 200000:
            return {"status": "error", "error": "context_budget_exceeded", "provider": provider}
        redactor = PIIRedactor()
        safe_system, _ = redactor.redact(system)
        safe_content, _ = redactor.redact(raw)
        try:
            result = await client.ainvoke([("system", safe_system), ("human", safe_content)])
            value = result.content
            if not isinstance(value, str) or not value.strip():
                raise ValueError("empty_provider_output")
        except Exception:
            return {"status": "unavailable", "value": None, "provider": provider,
                    "warning": "provider_request_failed"}
        return {"status": "ok", "value": value, "provider": provider,
                "model_generated": True, "requires_editorial_review": True}
