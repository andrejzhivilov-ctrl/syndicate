"""
Base connector for all third-party integrations.

Design principles (Zero-Trust / Least-Privilege):
- Every secret is retrieved through HashiCorp Vault (src.vault_client.VaultClient).
  Vault path convention: ``secret/data/syndicate/<SERVICE_NAME>``.
- A local environment-variable fallback exists ONLY for local development and is
  logged loudly as a warning. It must never be relied on in production.
- Outbound HTTP has: configurable timeout, exponential-backoff retry on 429/5xx,
  and a per-connector asyncio token-bucket rate limiter.
"""

from __future__ import annotations

import abc
import asyncio
import os
import time
from typing import Any, Dict, Optional

import structlog

from src.vault_paths import secret_path

try:
    import httpx
    _HTTPX_AVAILABLE = True
except ImportError:  # pragma: no cover
    _HTTPX_AVAILABLE = False

try:
    from tenacity import (
        retry,
        retry_if_exception_type,
        stop_after_attempt,
        wait_exponential,
    )
    _TENACITY_AVAILABLE = True
except ImportError:  # pragma: no cover
    _TENACITY_AVAILABLE = False

logger = structlog.get_logger(__name__)


class ConnectorError(RuntimeError):
    """Raised when a connector operation fails unrecoverably."""


class _TokenBucket:
    """Minimal asyncio token-bucket rate limiter."""

    def __init__(self, rate_per_sec: float, capacity: Optional[int] = None) -> None:
        self._rate = max(rate_per_sec, 0.001)
        self._capacity = capacity if capacity is not None else max(int(rate_per_sec), 1)
        self._tokens = float(self._capacity)
        self._updated = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._updated
            self._updated = now
            self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
            if self._tokens < 1.0:
                wait_for = (1.0 - self._tokens) / self._rate
                await asyncio.sleep(wait_for)
                self._tokens = 0.0
            else:
                self._tokens -= 1.0


class BaseConnector(abc.ABC):
    """Abstract base for all external-service connectors."""

    SERVICE_NAME: str = "base"

    def __init__(self, vault_client: Any = None, config: Optional[Dict[str, Any]] = None) -> None:
        self._vault = vault_client
        self._config = config or {}
        self._timeout = float(self._config.get("timeout", 30.0))
        self._rate_limiter = _TokenBucket(
            rate_per_sec=float(self._config.get("rate_per_sec", 5.0)),
            capacity=self._config.get("rate_capacity"),
        )
        self._secret_cache: Dict[str, str] = {}

    # ------------------------------------------------------------------ secrets
    async def _get_secret(self, key: str) -> str:
        """Fetch a secret for this service from Vault, with env fallback (dev only)."""
        if key in self._secret_cache:
            return self._secret_cache[key]

        value: Optional[str] = None
        if self._vault is not None:
            try:
                path = secret_path(self.SERVICE_NAME)
                secrets = await self._read_vault(path)
                if secrets and key in secrets:
                    value = str(secrets[key])
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "vault_secret_read_failed",
                    service=self.SERVICE_NAME,
                    key=key,
                    error=str(exc),
                )

        if value is None:
            # Try the namespaced variable first (TELEGRAM_BOT_TOKEN) and then
            # the bare one (BOT_TOKEN). The old code only checked the bare
            # name, so the documented variables in .env.example were ignored.
            for env_key in (f"{self.SERVICE_NAME.upper()}_{key.upper()}", key.upper()):
                candidate = os.environ.get(env_key)
                if candidate:
                    value = candidate
                    logger.warning(
                        "using_env_fallback_secret",
                        service=self.SERVICE_NAME,
                        env_key=env_key,
                        hint="Production must serve this secret via Vault, not env.",
                    )
                    break

        if value is None:
            raise ConnectorError(
                f"Secret '{key}' for service '{self.SERVICE_NAME}' not found in Vault or env."
            )

        self._secret_cache[key] = value
        return value

    async def _read_vault(self, path: str) -> Optional[Dict[str, Any]]:
        """Read a KV-v2 secret from Vault, supporting sync or async VaultClient."""
        reader = getattr(self._vault, "read_secret", None) or getattr(self._vault, "get_secret", None)
        if reader is None:
            return None
        result = reader(path)
        if asyncio.iscoroutine(result):
            result = await result
        # Normalise KV-v2 envelope {"data": {"data": {...}}}
        if isinstance(result, dict):
            if "data" in result and isinstance(result["data"], dict) and "data" in result["data"]:
                return result["data"]["data"]
            if "data" in result and isinstance(result["data"], dict):
                return result["data"]
            return result
        return None

    # -------------------------------------------------------------------- http
    async def _request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        files: Optional[Any] = None,
        expect_bytes: bool = False,
    ) -> Any:
        """Rate-limited, retrying HTTP request. Returns parsed JSON or raw bytes."""
        if not _HTTPX_AVAILABLE:
            raise ConnectorError("httpx is required for connector HTTP calls but is not installed.")

        await self._rate_limiter.acquire()

        async def _do() -> Any:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.request(
                    method, url, headers=headers, params=params,
                    json=json, data=data, files=files,
                )
                if resp.status_code in (429,) or resp.status_code >= 500:
                    resp.raise_for_status()
                if resp.status_code >= 400:
                    raise ConnectorError(
                        f"{self.SERVICE_NAME} {method} {url} -> {resp.status_code}: {resp.text[:500]}"
                    )
                return resp.content if expect_bytes else resp.json()

        if _TENACITY_AVAILABLE and _HTTPX_AVAILABLE:
            retryer = retry(
                reraise=True,
                stop=stop_after_attempt(int(self._config.get("max_retries", 4))),
                wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
                retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TransportError)),
            )
            return await retryer(_do)()
        return await _do()

    # ------------------------------------------------------------------ health
    @abc.abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Return a dict like {'service': name, 'healthy': bool, 'detail': ...}."""
        raise NotImplementedError
