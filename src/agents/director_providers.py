"""Bounded read/LLM adapters with per-director Vault secrets and fixed origins.

No scraping, purchases, publishing or betting endpoints are exposed. Adapters
are injected by the operator at startup, never selected through request input.
"""
from __future__ import annotations

import re
from types import SimpleNamespace

import httpx

from src.agents.director_base import text
from src.vault_paths import agent_secret_path, secret_path

LLM_ENDPOINTS = {
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "grok": "https://api.x.ai/v1/chat/completions",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    "haiku": "https://api.anthropic.com/v1/messages",
}
BOOKMAKERS = {"parimatch", "vbet", "pinnacle", "betfair_ex_uk", "betfair_ex_eu"}


from src.model_registry import model_for  # noqa: E402


class VaultLLM:
    def __init__(self, provider: str, secret: dict, *, transport=None) -> None:
        if provider not in LLM_ENDPOINTS:
            raise ValueError(f"unknown_provider: {provider}")
        self.provider = provider
        self.key = text(secret["api_key"], "api_key", 1000)
        default_model = model_for({
            "openrouter": "OPENROUTER_DIRECTOR", "gemini": "GEMINI_FLASH_LATEST", "grok": "GROK_DIRECTOR",
        }.get(provider, "ANTHROPIC_DIRECTOR"))
        self.model = text(secret.get("model") or default_model, "model", 200)
        self.transport = transport

    async def ainvoke(self, messages: list) -> SimpleNamespace:
        system, human = messages[0][1], messages[1][1]
        if self.provider == "haiku":
            headers = {"x-api-key": self.key, "anthropic-version": "2023-06-01"}
            body = {
                "model": self.model,
                "max_tokens": 4096,
                "system": system,
                "messages": [{"role": "user", "content": human}]
            }
        elif self.provider == "openrouter":
            headers = {
                "Authorization": f"Bearer {self.key}",
                "HTTP-Referer": "https://syndicateholding.com",
                "X-Title": "SYNDICATE Holding",
            }
            body = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": human}]
            }
        else:
            headers = {"Authorization": f"Bearer {self.key}"}
            body = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": human}]
            }
        async with httpx.AsyncClient(timeout=60, transport=self.transport, follow_redirects=False) as client:
            response = await client.post(LLM_ENDPOINTS[self.provider], headers=headers, json=body)
            response.raise_for_status()
            result = response.json()
        if self.provider == "haiku":
            content = "\n".join(block["text"] for block in result["content"] if block["type"] == "text")
        else:
            content = result["choices"][0]["message"]["content"]
        return SimpleNamespace(content=content)


class YouTubeComments:
    def __init__(self, secret: dict, *, transport=None) -> None:
        self.key = text(secret["api_key"], "api_key", 1000)
        self.transport = transport

    async def fetch(self, video_id: str) -> dict:
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            raise ValueError("invalid_video_id")
        try:
            async with httpx.AsyncClient(timeout=20, transport=self.transport, follow_redirects=False) as client:
                response = await client.get(
                    "https://www.googleapis.com/youtube/v3/commentThreads",
                    params={
                        "key": self.key,
                        "part": "snippet",
                        "videoId": video_id,
                        "maxResults": 100,
                        "textFormat": "plainText",
                        "order": "relevance"
                    }
                )
                response.raise_for_status()
                result = response.json()
            comments = [{
                "id": row["id"],
                "channel": "youtube",
                "text": row["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            } for row in result.get("items", [])]
        except Exception:
            return {"status": "unavailable", "value": None, "warning": "youtube_comments_request_failed"}
        return {
            "status": "ok",
            "comments": comments,
            "next_page_available": bool(result.get("nextPageToken")),
            "coverage": "up_to_100_top_level_comments_not_all_replies"
        }


class OddsScout:
    def __init__(self, secret: dict, *, transport=None) -> None:
        self.key = text(secret["api_key"], "api_key", 1000)
        self.transport = transport

    async def fetch(self, payload: dict) -> dict:
        sport = text(payload["sport_key"], "sport_key", 100)
        if not re.fullmatch(r"[a-z0-9_]+", sport):
            raise ValueError("invalid_sport_key")
        market = payload.get("market", "h2h")
        if market not in {"h2h", "spreads", "totals"}:
            raise ValueError("unsupported_market")
        try:
            async with httpx.AsyncClient(timeout=20, transport=self.transport, follow_redirects=False) as client:
                response = await client.get(
                    f"https://api.the-odds-api.com/v4/sports/{sport}/odds",
                    params={
                        "apiKey": self.key,
                        "regions": "eu,uk",
                        "markets": market,
                        "oddsFormat": "decimal",
                        "dateFormat": "iso"
                    }
                )
                response.raise_for_status()
                events = response.json()
            if not isinstance(events, list) or len(events) > 1000:
                raise ValueError("invalid_provider_response")
            found = {book["key"] for event in events for book in event.get("bookmakers", [])}
            selected = [{**event, "bookmakers": [b for b in event.get("bookmakers", []) if b["key"] in BOOKMAKERS]}
                        for event in events]
        except Exception:
            return {"status": "unavailable", "value": None, "warning": "odds_request_failed"}
        return {
            "status": "ok",
            "events": selected,
            "source": "the_odds_api",
            "coverage": {key: ("available" if key in found else "unavailable") for key in sorted(BOOKMAKERS)},
            "warning": "Bookmaker and live coverage depend on provider plan; availability is not guaranteed"
        }


#: Extra names a provider's key may have in the holding-wide api-keys pool.
_POOL_KEY_ALIASES = {
    "gemini": ("google_api_key", "google"),
    "haiku": ("anthropic_api_key", "anthropic"),
    "grok": ("xai_api_key", "xai"),
}


async def build_provider(vault, agent_id: str, provider: str):
    """Resolve director's credentials or holding-wide provider pool.

    Supports openrouter, gemini, grok, haiku for all directors.
    """
    secret = None
    # 1. Try agent-specific secret path
    try:
        secret = await vault.get_secret(agent_secret_path(agent_id, provider))
    except Exception:
        secret = None

    # 2. If not found or empty, resolve from holding-wide api-keys pool
    if not secret or not secret.get("api_key"):
        try:
            pool = await vault.get_secret(secret_path("api-keys"))
            lookup_keys = [f"{provider}_api_key", provider, *_POOL_KEY_ALIASES.get(provider, ())]
            for lk in lookup_keys:
                if pool.get(lk):
                    secret = {"api_key": pool[lk], "provider": provider}
                    break
        except Exception:
            pass

    if not secret:
        raise ValueError(f"provider_credential_not_found: {provider} for agent {agent_id}")

    if provider in LLM_ENDPOINTS:
        return VaultLLM(provider, secret)
    if provider == "youtube":
        return YouTubeComments(secret)
    return OddsScout(secret)
