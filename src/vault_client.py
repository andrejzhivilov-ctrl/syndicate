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

from src.vault_paths import read_path_candidates

logger = structlog.get_logger(__name__)

#: Strings that mean "nobody filled this in yet". ``vault_init.sh`` used to
#: write ``CHANGE_ME_BEFORE_PRODUCTION`` / ``PLACEHOLDER_UPDATE_ME`` into Vault,
#: and half the callers then had to remember to filter them (eight ad-hoc
#: checks existed, and one of them was always missing). A placeholder read as a
#: real secret is worse than a missing one: the failure surfaces far from the
#: cause, sometimes as an authenticated request with a nonsense token.
PLACEHOLDER_MARKERS = (
    "CHANGE_ME",
    "PLACEHOLDER",
    "REPLACE_ME",
    "UPDATE_ME",
    "FIXME",
    "TODO",
)


def is_placeholder_secret(value: Any) -> bool:
    """True when ``value`` is a fill-me-in marker rather than a real secret.

    >>> is_placeholder_secret("CHANGE_ME_BEFORE_PRODUCTION")
    True
    >>> is_placeholder_secret("sk-live-…")
    False
    """
    if value is None:
        return True
    text = str(value).strip()
    if not text:
        return True
    upper = text.upper()
    return any(marker in upper for marker in PLACEHOLDER_MARKERS)


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
        #: ``(path, key)`` pairs Vault holds only as fill-me-in markers. Read by
        #: /health so an operator can see *which* secret was never filled in.
        self.placeholder_keys: list[tuple[str, str]] = []

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
        """Retrieve a KV v2 secret from Vault.

        Keys whose value is a fill-me-in marker (or empty) are dropped and
        reported, so a half-configured Vault behaves exactly like a missing
        secret: callers fall back to env or report ``unavailable``. The flagged
        keys are recorded in :attr:`placeholder_keys` for diagnostics — the
        values themselves are never logged.
        """
        if not self.is_authenticated:
            await self.authenticate()

        candidates = read_path_candidates(path)
        selected_path = candidates[0]
        response = None
        for index, candidate in enumerate(candidates):
            response = await self._http.get(
                f"{self._vault_addr}/v1/{candidate}",
                headers=self._auth_headers(),
            )
            if response.status_code == 404 and index < len(candidates) - 1:
                logger.info(
                    "vault_canonical_path_missing_trying_legacy",
                    requested_path=path,
                    fallback_path=candidates[index + 1],
                )
                continue
            response.raise_for_status()
            selected_path = candidate
            break
        assert response is not None  # read_path_candidates always returns at least one path
        payload = response.json()
        try:
            data = payload["data"]["data"]
        except (KeyError, TypeError):
            # KV v1 (and empty KV v2 secrets) have a different envelope; report
            # it instead of raising a bare KeyError deep in the caller.
            raise RuntimeError(
                f"vault_unexpected_secret_envelope: {selected_path} "
                f"(keys: {sorted(payload) if isinstance(payload, dict) else type(payload).__name__})"
            ) from None

        if not isinstance(data, dict):
            raise RuntimeError(f"vault_unexpected_secret_envelope: {selected_path} (data is {type(data).__name__})")

        usable: Dict[str, Any] = {}
        for key, value in data.items():
            if is_placeholder_secret(value):
                self.placeholder_keys.append((selected_path, key))
                logger.warning("vault_placeholder_secret_ignored", path=selected_path, key=key)
                continue
            usable[key] = value
        return usable

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
