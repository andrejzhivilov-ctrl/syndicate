"""Operator-configured HTTP bridge from LangGraph to one isolated tool worker."""
from __future__ import annotations

from urllib.parse import urlsplit

import httpx

from src.vault_paths import agent_secret_path
from src.vault_client import is_placeholder_secret


class DirectorWorkerClient:
    def __init__(self, agent_id: str, url: str, vault, *, transport=None) -> None:
        if agent_id not in {"oscar", "tyler", "jack", "alice"}:
            raise ValueError("unknown_agent")
        parts = urlsplit(url)
        if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
            raise ValueError("invalid_worker_url")
        if parts.path not in {"", "/"} or parts.query or parts.fragment:
            raise ValueError("worker_url_requires_origin")
        self.agent_id, self.url, self.vault = agent_id, url.rstrip("/"), vault
        self.transport = transport

    async def execute(self, payload: dict) -> dict:
        try:
            secret = await self.vault.get_secret(agent_secret_path(self.agent_id, "auth"))
            key = secret.get("api_key")
            if not isinstance(key, str) or is_placeholder_secret(key):
                raise ValueError("worker_key_unavailable")
            async with httpx.AsyncClient(timeout=120, follow_redirects=False, transport=self.transport) as client:
                response = await client.post(f"{self.url}/execute", headers={"X-API-Key": key},
                                             json={"payload": payload})
                response.raise_for_status()
                result = response.json()
            if not isinstance(result, dict) or result.get("agent") != self.agent_id or "status" not in result:
                raise ValueError("worker_response_mismatch")
            return result
        except Exception:
            return {"agent": self.agent_id, "status": "unavailable", "value": None,
                    "warning": "director_worker_request_failed"}


def build_director_clients(config: dict, vault) -> dict[str, DirectorWorkerClient]:
    return {agent_id: DirectorWorkerClient(agent_id, config[agent_id]["worker_url"], vault)
            for agent_id in ("oscar", "tyler", "jack", "alice")
            if config.get(agent_id, {}).get("enabled") is True and config[agent_id].get("worker_url")}
