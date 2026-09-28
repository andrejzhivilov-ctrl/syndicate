"""
Vault client with AppRole authentication and automatic token renewal.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, Optional

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger(__name__)


class VaultClient:
    """Async HashiCorp Vault client with AppRole auth and lease management."""

    def __init__(self, vault_addr: str, role_id: str, secret_id: str) -> None:
        self._vault_addr = vault_addr.rstrip("/")
        self._role_id = role_id
        self._secret_id = secret_id
        self._token: Optional[str] = None
        self._token_expires_at: float = 0
        self._renewal_task: Optional[asyncio.Task] = None
        self._http = httpx.AsyncClient(timeout=10.0)

    @property
    def is_authenticated(self) -> bool:
        return self._token is not None and time.time() < self._token_expires_at

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def authenticate(self) -> None:
        """Authenticate via AppRole and store token."""
        response = await self._http.post(
            f"{self._vault_addr}/v1/auth/approle/login",
            json={"role_id": self._role_id, "secret_id": self._secret_id},
        )
        response.raise_for_status()
        data = response.json()

        self._token = data["auth"]["client_token"]
        lease_duration = data["auth"]["lease_duration"]
        self._token_expires_at = time.time() + lease_duration

        logger.info("Vault authenticated", lease_duration_seconds=lease_duration)

    async def get_secret(self, path: str) -> Dict[str, Any]:
        """Retrieve a KV v2 secret from Vault."""
        if not self.is_authenticated:
            await self.authenticate()

        response = await self._http.get(
            f"{self._vault_addr}/v1/{path}",
            headers={"X-Vault-Token": self._token},
        )
        response.raise_for_status()
        return response.json()["data"]["data"]

    async def start_token_renewal(self) -> None:
        """Background task: renew token before expiry."""
        while True:
            time_until_expiry = self._token_expires_at - time.time()
            # Renew at 75% of TTL
            sleep_duration = max(time_until_expiry * 0.75, 60)
            await asyncio.sleep(sleep_duration)

            try:
                await self._renew_token()
            except Exception as exc:
                logger.error("Token renewal failed, re-authenticating", error=str(exc))
                await self.authenticate()

    async def _renew_token(self) -> None:
        """Renew the current token."""
        response = await self._http.post(
            f"{self._vault_addr}/v1/auth/token/renew-self",
            headers={"X-Vault-Token": self._token},
        )
        response.raise_for_status()
        data = response.json()
        lease_duration = data["auth"]["lease_duration"]
        self._token_expires_at = time.time() + lease_duration
        logger.info("Vault token renewed", lease_duration_seconds=lease_duration)

    async def revoke_token(self) -> None:
        """Revoke the current token on shutdown."""
        if self._token:
            try:
                await self._http.post(
                    f"{self._vault_addr}/v1/auth/token/revoke-self",
                    headers={"X-Vault-Token": self._token},
                )
                self._token = None
                logger.info("Vault token revoked")
            except Exception as exc:
                logger.warning("Token revocation failed", error=str(exc))

    async def aclose(self) -> None:
        await self._http.aclose()
