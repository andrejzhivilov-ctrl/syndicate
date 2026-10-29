"""Hash-chained, append-only audit trail of Sam's signals, decisions and outcomes.

Pattern from virattt/ai-hedge-fund: each entry stores the hash of the previous
one, so editing or deleting any past record breaks every later hash and
``verify`` shows exactly where. In Postgres the table also refuses UPDATE,
DELETE and TRUNCATE by trigger (``config/postgres/migration_v6_sam_ledger.sql``).

The hash covers ``body``: the exact canonical JSON text stored as-is in a TEXT
column. ``payload`` (JSONB) is only a queryable copy. Hashing the JSONB would
break on values Postgres normalises (``-0.0`` becomes ``0``, big numbers change
notation), and an intact chain would look tampered.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional

import structlog

logger = structlog.get_logger(__name__)

GENESIS = "0" * 64
_LOCK_KEY = 0x5A3_1ED6  # one advisory lock serialises appends across processes


def canonical_body(created_at: str, signal_id: Optional[str], event: str, payload: Mapping[str, Any]) -> str:
    return json.dumps({"at": created_at, "signal": signal_id, "event": event, "payload": payload},
                      sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def entry_hash(prev_hash: str, body: str) -> str:
    return hashlib.sha256(f"{prev_hash}\n{body}".encode("utf-8")).hexdigest()


def verify(rows: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Recompute the chain oldest first; report the first broken sequence number."""
    prev, count = GENESIS, 0
    for row in rows:
        if row["prev_hash"] != prev or row["entry_hash"] != entry_hash(prev, row["body"]):
            return {"status": "ok", "intact": False, "length": count, "broken_at": row.get("seq", count + 1)}
        prev, count = row["entry_hash"], count + 1
    return {"status": "ok", "intact": True, "length": count, "broken_at": None, "head": prev}


class HashLedger:
    """Postgres when a pool is given, otherwise process memory (tests, degraded mode)."""

    def __init__(self, pool: Optional[Any] = None) -> None:
        self._pool = pool
        self._rows: List[Dict[str, Any]] = []

    async def append(self, event: str, signal_id: Optional[str], payload: Mapping[str, Any]) -> Dict[str, Any]:
        created = datetime.now(timezone.utc).isoformat()
        body = canonical_body(created, signal_id, event, json.loads(json.dumps(dict(payload), default=str)))
        if self._pool is None:
            prev = self._rows[-1]["entry_hash"] if self._rows else GENESIS
            row = {"seq": len(self._rows) + 1, "signal_id": signal_id, "event": event, "body": body,
                   "prev_hash": prev, "entry_hash": entry_hash(prev, body)}
            self._rows.append(row)
            return {"status": "ok", "backend": "memory", "entry_hash": row["entry_hash"]}
        try:
            async with self._pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute("SELECT pg_advisory_xact_lock($1)", _LOCK_KEY)
                    prev = await conn.fetchval(
                        "SELECT entry_hash FROM agents.sam_journal_ledger ORDER BY seq DESC LIMIT 1") or GENESIS
                    digest = entry_hash(prev, body)
                    await conn.execute(
                        "INSERT INTO agents.sam_journal_ledger "
                        "(created_at, signal_id, event, payload, body, prev_hash, entry_hash) "
                        # body is bound as its own TEXT parameter: reusing one parameter for the
                        # JSONB copy would make Postgres type it JSONB and store normalised text.
                        "VALUES ($1::timestamptz, $2, $3, ($4::text::jsonb)->'payload', $5::text, $6, $7)",
                        datetime.fromisoformat(created), signal_id, event, body, body, prev, digest)
            return {"status": "ok", "backend": "postgres", "entry_hash": digest}
        except Exception as exc:  # noqa: BLE001 - the journal goes on; the gap is logged loudly
            logger.warning("sam_ledger_append_failed", ledger_event=event, error_type=type(exc).__name__)
            return {"status": "unavailable", "reason": "ledger_write_failed"}

    async def rows(self) -> List[Dict[str, Any]]:
        if self._pool is None:
            return list(self._rows)
        async with self._pool.acquire() as conn:
            records = await conn.fetch(
                "SELECT seq, signal_id, event, body, prev_hash, entry_hash "
                "FROM agents.sam_journal_ledger ORDER BY seq")
        return [dict(r) for r in records]

    async def verify(self) -> Dict[str, Any]:
        try:
            return verify(await self.rows())
        except Exception as exc:  # noqa: BLE001
            logger.warning("sam_ledger_verify_failed", error_type=type(exc).__name__)
            return {"status": "unavailable", "reason": "ledger_read_failed"}
