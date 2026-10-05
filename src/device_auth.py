"""Per-device access tokens for EVA SYNDICATE clients (PC / mobile).

Why this exists
---------------
The runtime has a single shared secret (``EVA_API_KEY``) presented as
``X-API-Key``. That is fine for server-to-server calls and for the operator's
own automation, but it must **never** be shipped inside a mobile or desktop
app: anything compiled into an APK/IPA/binary can be extracted, and a leaked
master key is unrevocable without redeploying every client.

A device token instead:

  * is issued **per device** and is shown to the client exactly once
    (only its SHA-256 hash is stored);
  * is **short-lived** and rotatable (``/auth/device/refresh``);
  * can be **revoked individually** without touching other devices
    or the master key;
  * carries **scopes**, so a phone that only needs to answer HITL prompts
    does not get to apply change requests.

The master key stays valid for everything — this module only *adds* a second,
safer credential type, so existing automation keeps working unchanged.

Storage: PostgreSQL (``auth.device_tokens``) when a pool is available,
otherwise an in-memory store, so the service never fails to start without a
database. Same degraded-mode contract as ``src.agents.sam.journal``.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)

DEFAULT_TTL_SECONDS = 30 * 24 * 3600        # 30 days
MIN_TTL_SECONDS = 60
MAX_TTL_SECONDS = 365 * 24 * 3600
MAX_TOKENS_PER_DEVICE = 10

# Scopes a client can be limited to. An empty list grants NO scope beyond
# general authentication — a token must list a scope explicitly to use it.
# master key can do; a non-empty list restricts the token to those prefixes.
SCOPE_EXECUTE = "execute"
SCOPE_READ = "read"
SCOPE_HITL = "hitl"
KNOWN_SCOPES = (SCOPE_EXECUTE, SCOPE_READ, SCOPE_HITL)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(moment: datetime) -> str:
    return moment.isoformat()


@dataclass
class DeviceToken:
    token_id: str
    device_id: str
    secret_hash: str
    label: str = ""
    scopes: List[str] = field(default_factory=list)
    issued_at: str = field(default_factory=lambda: _iso(_utcnow()))
    expires_at: str = field(default_factory=lambda: _iso(_utcnow() + timedelta(seconds=DEFAULT_TTL_SECONDS)))
    revoked_at: Optional[str] = None
    last_seen_at: Optional[str] = None

    @property
    def expired(self) -> bool:
        try:
            return datetime.fromisoformat(self.expires_at) <= _utcnow()
        except (ValueError, TypeError):
            # An unparsable expiry must never read as "valid".
            return True

    @property
    def revoked(self) -> bool:
        return self.revoked_at is not None

    @property
    def usable(self) -> bool:
        return not self.revoked and not self.expired

    def public_dict(self) -> Dict[str, Any]:
        """Never includes the secret or its hash."""
        return {
            "token_id": self.token_id,
            "device_id": self.device_id,
            "label": self.label,
            "scopes": list(self.scopes),
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "revoked_at": self.revoked_at,
            "last_seen_at": self.last_seen_at,
            "status": "revoked" if self.revoked else ("expired" if self.expired else "active"),
        }


class DeviceTokenStore:
    """Issue, verify, rotate and revoke per-device tokens."""

    def __init__(
        self,
        memory: Optional[Any] = None,
        default_ttl_seconds: int = DEFAULT_TTL_SECONDS,
        max_tokens_per_device: int = MAX_TOKENS_PER_DEVICE,
    ) -> None:
        self._memory = memory
        self._default_ttl = int(default_ttl_seconds)
        self._max_per_device = int(max_tokens_per_device)
        self._mem_tokens: Dict[str, DeviceToken] = {}

    # ------------------------------------------------------------------ pool
    def _pool(self) -> Optional[Any]:
        for attr in ("pool", "_pool", "db_pool"):
            pool = getattr(self._memory, attr, None)
            if pool is not None:
                return pool
        return None

    # ---------------------------------------------------------- token format
    @staticmethod
    def _hash_secret(secret: str) -> str:
        return hashlib.sha256(secret.encode("utf-8")).hexdigest()

    @staticmethod
    def _split(token: str) -> tuple:
        """``<token_id>.<secret>`` -> ``(token_id, secret)``."""
        token_id, dot, secret = (token or "").partition(".")
        if not dot or not token_id or not secret:
            return None, None
        return token_id, secret

    @staticmethod
    def _clamp_ttl(ttl: Optional[int], default: int) -> int:
        try:
            value = int(ttl) if ttl is not None else int(default)
        except (TypeError, ValueError):
            value = int(default)
        return max(MIN_TTL_SECONDS, min(MAX_TTL_SECONDS, value))

    # --------------------------------------------------------------- issuing
    async def enroll(
        self,
        device_id: str,
        label: str = "",
        scopes: Optional[List[str]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Issue a new token. The plaintext is returned **once** — store the hash only."""
        device_id = (device_id or "").strip()
        if not device_id:
            raise ValueError("device_id is required")
        unknown = [s for s in (scopes or []) if s not in KNOWN_SCOPES]
        if unknown:
            raise ValueError(f"unknown scopes: {unknown} (known: {list(KNOWN_SCOPES)})")

        ttl = self._clamp_ttl(ttl_seconds, self._default_ttl)
        token_id = secrets.token_hex(8)
        secret = secrets.token_urlsafe(32)
        record = DeviceToken(
            token_id=token_id,
            device_id=device_id,
            secret_hash=self._hash_secret(secret),
            label=label or "",
            scopes=list(scopes or []),
            expires_at=_iso(_utcnow() + timedelta(seconds=ttl)),
        )

        pool = self._pool()
        if pool is None:
            self._mem_tokens[token_id] = record
            self._enforce_limit(device_id)
            logger.info("device_token_issued", token_id=token_id, device_id=device_id, backend="memory")
        else:  # pragma: no cover - needs live DB
            try:
                async with pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO auth.device_tokens
                            (token_id, secret_hash, device_id, label, scopes, expires_at)
                        VALUES ($1,$2,$3,$4,$5,$6)
                        """,
                        token_id, record.secret_hash, device_id, record.label,
                        json.dumps(record.scopes), datetime.fromisoformat(record.expires_at),
                    )
                logger.info("device_token_issued", token_id=token_id, device_id=device_id, backend="postgres")
            except Exception as exc:  # noqa: BLE001
                logger.error("device_token_write_failed", error=str(exc))
                raise RuntimeError(f"device token issuance failed: {exc}") from exc

        return {
            "token": f"{token_id}.{secret}",   # shown once, never stored
            **record.public_dict(),
            "expires_in_seconds": ttl,
            "warning": "Store this token now — only its hash is kept and it cannot be shown again.",
        }

    def _enforce_limit(self, device_id: str) -> None:
        """Keep only the newest N active tokens per device (in-memory backend)."""
        active = [
            (t.issued_at, t.token_id)
            for t in self._mem_tokens.values()
            if t.device_id == device_id and not t.revoked
        ]
        if len(active) <= self._max_per_device:
            return
        active.sort()
        for _issued, token_id in active[: len(active) - self._max_per_device]:
            self._mem_tokens.pop(token_id, None)
            logger.warning("device_token_evicted", token_id=token_id, device_id=device_id)

    # --------------------------------------------------------------- loading
    async def _load(self, token_id: str) -> Optional[DeviceToken]:
        pool = self._pool()
        if pool is None:
            return self._mem_tokens.get(token_id)
        try:  # pragma: no cover - needs live DB
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT token_id, device_id, secret_hash, label, scopes,
                           issued_at, expires_at, revoked_at, last_seen_at
                    FROM auth.device_tokens
                    WHERE token_id = $1
                    """,
                    token_id,
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("device_token_read_failed", error=str(exc))
            return None
        if row is None:
            return None
        scopes = row["scopes"]
        if isinstance(scopes, str):
            try:
                scopes = json.loads(scopes)
            except json.JSONDecodeError:
                scopes = []
        return DeviceToken(
            token_id=row["token_id"],
            device_id=row["device_id"],
            secret_hash=row["secret_hash"],
            label=row["label"] or "",
            scopes=list(scopes or []),
            issued_at=_iso(row["issued_at"]),
            expires_at=_iso(row["expires_at"]),
            revoked_at=_iso(row["revoked_at"]) if row["revoked_at"] else None,
            last_seen_at=_iso(row["last_seen_at"]) if row["last_seen_at"] else None,
        )

    async def _touch(self, token_id: str) -> None:
        now = _utcnow()
        pool = self._pool()
        if pool is None:
            record = self._mem_tokens.get(token_id)
            if record is not None:
                record.last_seen_at = _iso(now)
            return
        try:  # pragma: no cover - needs live DB
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE auth.device_tokens SET last_seen_at=$2 WHERE token_id=$1",
                    token_id, now,
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("device_token_touch_failed", error=str(exc))

    # -------------------------------------------------------------- verifying
    async def verify(self, token: Optional[str], required_scope: Optional[str] = None) -> Optional[DeviceToken]:
        """Return the record if the token is valid, else ``None``.

        Never raises — an unusable token is simply not a credential.
        """
        token_id, secret = self._split(token)
        if not token_id:
            return None
        record = await self._load(token_id)
        if record is None or not record.usable:
            return None
        if not hmac.compare_digest(record.secret_hash, self._hash_secret(secret)):
            logger.warning("device_token_secret_mismatch", token_id=token_id)
            return None
        # Least privilege: a scope must be *explicitly* granted. An empty scope
        # list does NOT inherit everything — otherwise a token minted with no
        # scopes could approve financial changes. The master key is the only
        # credential that implicitly grants all scopes.
        if required_scope and required_scope not in record.scopes:
            logger.warning(
                "device_token_scope_denied",
                token_id=token_id, required=required_scope, granted=record.scopes,
            )
            return None
        await self._touch(token_id)
        return record

    # --------------------------------------------------------------- rotating
    async def refresh(self, token: Optional[str], ttl_seconds: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Rotate: revoke the presented token and issue a fresh one for the same device."""
        record = await self.verify(token)
        if record is None:
            return None
        await self.revoke(record.token_id)
        return await self.enroll(
            device_id=record.device_id,
            label=record.label,
            scopes=record.scopes,
            ttl_seconds=ttl_seconds if ttl_seconds is not None else self._default_ttl,
        )

    # --------------------------------------------------------------- revoking
    async def revoke(self, token_id: str) -> bool:
        pool = self._pool()
        if pool is None:
            record = self._mem_tokens.get(token_id)
            if record is None:
                return False
            record.revoked_at = _iso(_utcnow())
            logger.info("device_token_revoked", token_id=token_id, backend="memory")
            return True
        try:  # pragma: no cover - needs live DB
            async with pool.acquire() as conn:
                result = await conn.execute(
                    "UPDATE auth.device_tokens SET revoked_at=NOW() WHERE token_id=$1 AND revoked_at IS NULL",
                    token_id,
                )
            revoked = bool(result and "1" in str(result).split()[-1:])
            logger.info("device_token_revoked", token_id=token_id, backend="postgres")
            return revoked
        except Exception as exc:  # noqa: BLE001
            logger.warning("device_token_revoke_failed", error=str(exc))
            return False

    async def list_devices(self) -> List[Dict[str, Any]]:
        pool = self._pool()
        if pool is None:
            records = list(self._mem_tokens.values())
        else:  # pragma: no cover - needs live DB
            try:
                async with pool.acquire() as conn:
                    rows = await conn.fetch(
                        """
                        SELECT token_id, device_id, label, scopes, issued_at,
                               expires_at, revoked_at, last_seen_at
                        FROM auth.device_tokens
                        ORDER BY issued_at DESC
                        LIMIT 200
                        """
                    )
            except Exception as exc:  # noqa: BLE001
                logger.warning("device_token_list_failed", error=str(exc))
                return []
            records = []
            for row in rows:
                scopes = row["scopes"]
                if isinstance(scopes, str):
                    try:
                        scopes = json.loads(scopes)
                    except json.JSONDecodeError:
                        scopes = []
                records.append(DeviceToken(
                    token_id=row["token_id"], device_id=row["device_id"],
                    secret_hash="", label=row["label"] or "", scopes=list(scopes or []),
                    issued_at=_iso(row["issued_at"]), expires_at=_iso(row["expires_at"]),
                    revoked_at=_iso(row["revoked_at"]) if row["revoked_at"] else None,
                    last_seen_at=_iso(row["last_seen_at"]) if row["last_seen_at"] else None,
                ))
        return [r.public_dict() for r in records]

    async def purge_expired(self, older_than_seconds: int = 7 * 24 * 3600) -> int:
        """Drop long-dead records. Returns how many were removed."""
        cutoff = _utcnow() - timedelta(seconds=older_than_seconds)
        pool = self._pool()
        if pool is None:
            dead = [
                tid for tid, r in self._mem_tokens.items()
                if not r.usable and datetime.fromisoformat(r.expires_at) < cutoff
            ]
            for tid in dead:
                self._mem_tokens.pop(tid, None)
            return len(dead)
        try:  # pragma: no cover - needs live DB
            async with pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM auth.device_tokens WHERE expires_at < $1", cutoff,
                )
            return int(str(result).split()[-1]) if result else 0
        except Exception as exc:  # noqa: BLE001
            logger.warning("device_token_purge_failed", error=str(exc))
            return 0


def token_age_seconds(record: DeviceToken) -> float:
    try:
        return max(0.0, time.time() - datetime.fromisoformat(record.issued_at).timestamp())
    except (ValueError, TypeError):
        return 0.0
