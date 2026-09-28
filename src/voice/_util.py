"""Shared helpers for voice providers (Vault secret retrieval)."""

from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


async def read_vault_secret(vault_client: Any, service: str, key: str) -> Optional[str]:
    """Read ``key`` from Vault path secret/data/eva-syndicate/<service>, env fallback (dev)."""
    value: Optional[str] = None
    if vault_client is not None:
        reader = getattr(vault_client, "read_secret", None) or getattr(vault_client, "get_secret", None)
        if reader is not None:
            try:
                path = f"secret/data/eva-syndicate/{service}"
                result = reader(path)
                if asyncio.iscoroutine(result):
                    result = await result
                data = _unwrap(result)
                if data and key in data:
                    value = str(data[key])
            except Exception as exc:  # noqa: BLE001
                logger.warning("voice_vault_read_failed", service=service, key=key, error=str(exc))

    if value is None:
        env_key = key.upper()
        value = os.environ.get(env_key)
        if value is not None:
            logger.warning("voice_env_fallback_secret", service=service, env_key=env_key)
    return value


def _unwrap(result: Any) -> Optional[Dict[str, Any]]:
    if isinstance(result, dict):
        if "data" in result and isinstance(result["data"], dict) and "data" in result["data"]:
            return result["data"]["data"]
        if "data" in result and isinstance(result["data"], dict):
            return result["data"]
        return result
    return None
