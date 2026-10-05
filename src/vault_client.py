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

    def _auth_headers(self) -> Dict[str, str]:
        """Vault request headers. Raises instead of sending an empty token."""
        if not self._token:
            raise RuntimeError("vault_not_authenticated: call authenticate() first")
        return {"X-Vault-Token": self._token}

    async def __aenter__(self) -> "VaultClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def authenticate(self) -> None:
        """Authenticate via AppRole and store token."""
        response = await self._http.post(
            f"{self._vault_addr}/v1/auth/approle/login",
            json={"role_id": self._role_id, "secret_id": self._secret_id},
        )
        response.raise_for_status()
        data = response.json()

        auth = data.get("auth") or {}
        token = auth.get("client_token")
        if not token:
            # A 200 without a token means a misconfigured AppRole; fail loudly
            # instead of caching ``None`` and silently skipping every later auth.
            raise RuntimeError("vault_login_response_missing_client_token")
        self._token = token
        lease_duration = int(auth.get("lease_duration") or 0)
        self._token_expires_at = time.time() + max(lease_duration, 0)

        logger.info("Vault authenticated", lease_duration_seconds=lease_duration)

    async def get_secret(self, path: str) -> Dict[str, Any]:
        """Retrieve a KV v2 secret from Vault."""
        if not self.is_authenticated:
            await self.authenticate()

        response = await self._http.get(
            f"{self._vault_addr}/v1/{path}",
            headers=self._auth_headers(),
        )
        response.raise_for_status()
        payload = response.json()
        try:
            return payload["data"]["data"]
        except (KeyError, TypeError):
            # KV v1 (and empty KV v2 secrets) have a different envelope; report
            # it instead of raising a bare KeyError deep in the caller.
            raise RuntimeError(
                f"vault_unexpected_secret_envelope: {path} "
                f"(keys: {sorted(payload) if isinstance(payload, dict) else type(payload).__name__})"
            ) from None

    async def start_token_renewal(self) -> None:
        """Background task: renew the token at 75% of its TTL.

        Runs forever until cancelled. A Vault outage must not kill the loop
        (the old code let ``authenticate()`` raise straight out of it, so the
        renewal task died silently and every later ``get_secret`` 403'd).
        """
        while True:
            time_until_expiry = self._token_expires_at - time.time()
            # Renew at 75% of TTL, but never sleep less than a minute.
            sleep_duration = max(time_until_expiry * 0.75, 60)
            try:
                await asyncio.sleep(sleep_duration)
            except asyncio.CancelledError:
                logger.info("vault_token_renewal_cancelled")
                raise

            try:
                await self._renew_token()
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.error("Token renewal failed, re-authenticating", error=str(exc))
                try:
                    await self.authenticate()
                except asyncio.CancelledError:
                    raise
                except Exception as auth_exc:  # noqa: BLE001
                    logger.error(
                        "Vault re-authentication failed, retrying",
                        error=str(auth_exc),
                        retry_in_seconds=sleep_duration,
                    )

    def ensure_token_renewal(self) -> asyncio.Task:
        """Start the renewal loop once and keep a handle so it can be cancelled."""
        if self._renewal_task is None or self._renewal_task.done():
            self._renewal_task = asyncio.create_task(self.start_token_renewal())
        return self._renewal_task

    async def _renew_token(self) -> None:
        """Renew the current token."""
        response = await self._http.post(
            f"{self._vault_addr}/v1/auth/token/renew-self",
            headers=self._auth_headers(),
        )
        response.raise_for_status()
        data = response.json()
        lease_duration = data["auth"]["lease_duration"]
        self._token_expires_at = time.time() + lease_duration
        logger.info("Vault token renewed", lease_duration_seconds=lease_duration)

    async def revoke_token(self) -> None:
        """Revoke the current token on shutdown."""
        if not self._token:
            return
        try:
            await self._http.post(
                f"{self._vault_addr}/v1/auth/token/revoke-self",
                headers=self._auth_headers(),
            )
            logger.info("Vault token revoked")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Token revocation failed", error=str(exc))
        finally:
            # Drop the token even when revocation fails — otherwise the client
            # keeps presenting a token that Vault may already have expired.
            self._token = None
            self._token_expires_at = 0

    async def aclose(self) -> None:
        """Close the HTTP client and stop the renewal loop."""
        task = self._renewal_task
        self._renewal_task = None
        if task is not None and not task.done():
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        await self._http.aclose()
