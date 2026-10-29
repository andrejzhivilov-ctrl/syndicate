"""Directors' working files in Garage (internal S3), one bucket and key per director.

Why a separate store: agents keep drafts, exports and report attachments here
instead of in chat memory or the vector store, so working files do not bloat
the context they pay tokens for.

Access model (enforced twice: by the Garage key grants made in
``tools/garage_setup.py`` and again here, so a code bug cannot widen it):

* ``agent-<id>`` — the director's own bucket: read and write with its own key;
* ``syndicate-shared`` — read for every director, write only for Eva;
* no delete in this client (deleting needs Andrii's approval); ``tmp/`` expires
  by itself after ``TMP_DAYS`` days, so scratch files do not pile up.

Limit, stated honestly: Garage authorises S3 DeleteObject with plain write
permission, so whoever holds a director's raw key could delete that director's
files. Only the runtime reads the keys today. Real protection against deletion
needs a backup of ``/data/garage`` — not set up yet (docs/HANDOFF.md).

The key lives in Vault at ``agents/<id>/storage``. Without it every call returns
an honest ``unavailable``; nothing pretends a file was saved.
"""
from __future__ import annotations

import asyncio
import re
from typing import Any, Callable, Dict, Optional

import structlog

from src.vault_paths import DIRECTOR_IDS, STORAGE, agent_secret_path

logger = structlog.get_logger(__name__)

ENDPOINT = "http://garage:3900"
REGION = "garage"
SHARED_BUCKET = "syndicate-shared"
SHARED_WRITERS = frozenset({"eva"})
QUOTA_AGENT_BYTES = 5 * 1024 ** 3
QUOTA_SHARED_BYTES = 20 * 1024 ** 3
MAX_OBJECT_BYTES = 100 * 1024 ** 2
TMP_PREFIX = "tmp/"
TMP_DAYS = 7
LIST_LIMIT = 100

_BAD_KEY = re.compile(r"(^/)|(\.\.)|(//)|[\\\x00-\x1f\x7f]")


def bucket_for(agent_id: str) -> str:
    return f"agent-{agent_id}"


def _unavailable(reason: str, **extra: Any) -> Dict[str, Any]:
    return {"status": "unavailable", "reason": reason, **extra}


def _valid_key(key: str) -> bool:
    return isinstance(key, str) and 0 < len(key) <= 512 and not _BAD_KEY.search(key)


def _boto_client(creds: Dict[str, Any]) -> Any:
    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=creds.get("endpoint") or ENDPOINT,
        region_name=REGION,
        aws_access_key_id=creds["access_key_id"],
        aws_secret_access_key=creds["secret_access_key"],
        config=Config(s3={"addressing_style": "path"}, retries={"max_attempts": 2},
                      connect_timeout=5, read_timeout=30),
    )


class AgentStorage:
    """One director's view of the store. Every method raises nothing."""

    def __init__(self, agent_id: str, vault: Any, *, client_factory: Callable[[Dict[str, Any]], Any] = _boto_client):
        self.agent_id = agent_id
        self._vault = vault
        self._factory = client_factory
        self._client: Any = None

    async def _s3(self) -> Optional[Any]:
        if self._client is None:
            if self.agent_id not in DIRECTOR_IDS:
                return None
            try:
                creds = await self._vault.get_secret(agent_secret_path(self.agent_id, STORAGE)) or {}
            except Exception as exc:  # noqa: BLE001 - treated as "not configured"
                logger.warning("agent_storage_vault_error", agent=self.agent_id, error_type=type(exc).__name__)
                return None
            if not creds.get("access_key_id") or not creds.get("secret_access_key"):
                return None
            self._client = self._factory(creds)
        return self._client

    def _failed(self, op: str, exc: Exception) -> Dict[str, Any]:
        response = getattr(exc, "response", None)
        code = response.get("Error", {}).get("Code") if isinstance(response, dict) else None
        logger.warning("agent_storage_error", agent=self.agent_id, op=op, code=code, error_type=type(exc).__name__)
        return _unavailable("storage_error", code=code or type(exc).__name__)

    async def _call(self, op: str, **kwargs: Any) -> Dict[str, Any]:
        try:  # building the client (endpoint/config from Vault) is inside the boundary too
            client = await self._s3()
            if client is None:
                return _unavailable("storage_not_configured", agent=self.agent_id)
            return {"status": "ok", "response": await asyncio.to_thread(getattr(client, op), **kwargs)}
        except Exception as exc:  # noqa: BLE001 - storage outage must not crash a director
            return self._failed(op, exc)

    def _bucket(self, shared: bool) -> str:
        return SHARED_BUCKET if shared else bucket_for(self.agent_id)

    async def put(self, key: str, data: bytes, content_type: str = "application/octet-stream",
                  shared: bool = False) -> Dict[str, Any]:
        if not _valid_key(key):
            return {"status": "error", "error": "invalid_key"}
        if shared and self.agent_id not in SHARED_WRITERS:
            return {"status": "denied", "error": "shared_is_read_only", "writers": sorted(SHARED_WRITERS)}
        if not isinstance(data, (bytes, bytearray)) or len(data) > MAX_OBJECT_BYTES:
            return {"status": "error", "error": "too_large_or_not_bytes", "max_bytes": MAX_OBJECT_BYTES}
        result = await self._call("put_object", Bucket=self._bucket(shared), Key=key, Body=bytes(data),
                                  ContentType=content_type)
        if result["status"] != "ok":
            return result
        return {"status": "ok", "bucket": self._bucket(shared), "key": key, "bytes": len(data)}

    async def get(self, key: str, shared: bool = False) -> Dict[str, Any]:
        if not _valid_key(key):
            return {"status": "error", "error": "invalid_key"}
        result = await self._call("get_object", Bucket=self._bucket(shared), Key=key)
        if result["status"] != "ok":
            return result
        body = result["response"]["Body"]
        try:
            data = await asyncio.to_thread(body.read, MAX_OBJECT_BYTES + 1)
        except Exception as exc:  # noqa: BLE001 - a broken stream is an outage, not a crash
            return self._failed("get_object.read", exc)
        finally:
            close = getattr(body, "close", None)
            if callable(close):
                close()
        if len(data) > MAX_OBJECT_BYTES:
            return {"status": "error", "error": "too_large", "max_bytes": MAX_OBJECT_BYTES}
        return {"status": "ok", "key": key, "data": data,
                "content_type": result["response"].get("ContentType")}

    async def list(self, prefix: str = "", shared: bool = False, limit: int = LIST_LIMIT) -> Dict[str, Any]:
        if prefix and not _valid_key(prefix):
            return {"status": "error", "error": "invalid_prefix"}
        result = await self._call("list_objects_v2", Bucket=self._bucket(shared), Prefix=prefix,
                                  MaxKeys=max(1, min(limit, LIST_LIMIT)))
        if result["status"] != "ok":
            return result
        items = [{"key": o["Key"], "bytes": o.get("Size", 0),
                  "modified": o["LastModified"].isoformat() if o.get("LastModified") else None}
                 for o in result["response"].get("Contents", [])]
        return {"status": "ok", "bucket": self._bucket(shared), "items": items,
                "truncated": bool(result["response"].get("IsTruncated"))}


def _size(n: int) -> str:
    for unit in ("Б", "КБ", "МБ"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} ГБ"


async def files_reply(agent_id: str, arg: str, storage: AgentStorage) -> Dict[str, Any]:
    """/files [prefix] and /files shared [prefix] — a listing, no model call."""
    shared = arg.split()[:1] == ["shared"]
    prefix = arg.split(maxsplit=1)[1] if shared and len(arg.split()) > 1 else ("" if shared else arg.strip())
    listing = await storage.list(prefix, shared=shared, limit=30)
    base = {"agent": agent_id, "mode": "files"}
    if listing["status"] == "unavailable":
        return {**base, **listing, "response": "Сховище файлів ще не підключене для цього агента."}
    if listing["status"] != "ok":
        return {**base, **listing, "response": "Не вдалося прочитати сховище."}
    where = "спільній теці" if shared else "моєму сховищі"
    if not listing["items"]:
        return {**base, "status": "completed", "response": f"У {where} поки немає файлів" + (f" з «{prefix}»." if prefix else ".")}
    lines = [f"Файли в {where}:"] + [f"• {i['key']} — {_size(i['bytes'])}" for i in listing["items"]]
    if listing["truncated"]:
        lines.append("… показано перші 30.")
    return {**base, "status": "completed", "response": "\n".join(lines)}
