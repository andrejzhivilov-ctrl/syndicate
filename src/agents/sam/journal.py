"""Sam's self-learning trade journal & reflection store.

Backs the ``self_learning_journal`` skill (spec §6, skill #7) and the
``TRADING_JOURNAL_REFLECTIONS`` archive sector (spec §2).  Persists every
proposed signal, the human's HITL decision, the eventual outcome, and derived
*lessons* / *negative constraints* used to block repetition of losing patterns.

Storage backend is PostgreSQL via the shared :class:`~src.memory.MemoryManager`
connection pool when available (tables ``agents.sam_trade_journal`` and
``agents.sam_reflections`` created in ``config/postgres/init.sql``).  When no
pool is supplied (unit tests / degraded mode) it transparently falls back to an
in-memory store so the agent never crashes.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class JournalEntry:
    signal_id: str
    symbol: str
    direction: str
    confluence_score: float
    threshold: float
    layers: Dict[str, Any] = field(default_factory=dict)
    venue: Optional[str] = None
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_pct: Optional[float] = None
    position_size: Optional[float] = None
    status: str = "proposed"
    created_at: datetime = field(default_factory=_utcnow)

    def to_dict(self) -> Dict[str, Any]:
        d = dict(self.__dict__)
        d["created_at"] = self.created_at.isoformat()
        return d


class TradeJournal:
    """Persistence layer for Sam's signals, decisions, outcomes and lessons."""

    def __init__(self, memory: Optional[Any] = None) -> None:
        # ``memory`` is expected to expose an asyncpg pool at ``memory.pool`` or
        # a ``memory._pool``; we probe defensively to stay compatible.
        self._memory = memory
        self._mem_entries: Dict[str, Dict[str, Any]] = {}
        self._mem_reflections: List[Dict[str, Any]] = []

    def _pool(self) -> Optional[Any]:
        for attr in ("pool", "_pool", "db_pool"):
            pool = getattr(self._memory, attr, None)
            if pool is not None:
                return pool
        return None

    # ------------------------------------------------------------------ #
    # Recording signals & decisions.
    # ------------------------------------------------------------------ #
    async def record_signal(self, entry: JournalEntry) -> None:
        pool = self._pool()
        if pool is None:
            self._mem_entries[entry.signal_id] = entry.to_dict()
            logger.info("journal_signal_recorded", signal_id=entry.signal_id, backend="memory")
            return
        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO agents.sam_trade_journal
                        (signal_id, symbol, venue, direction, confluence_score,
                         threshold, layers, entry_price, stop_loss, take_profit,
                         risk_pct, position_size, status)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
                    ON CONFLICT (signal_id) DO NOTHING
                    """,
                    entry.signal_id, entry.symbol, entry.venue, entry.direction,
                    entry.confluence_score, entry.threshold, json.dumps(entry.layers),
                    entry.entry_price, entry.stop_loss, entry.take_profit,
                    entry.risk_pct, entry.position_size, entry.status,
                )
            logger.info("journal_signal_recorded", signal_id=entry.signal_id, backend="postgres")
        except Exception as exc:  # noqa: BLE001
            logger.warning("journal_db_write_failed", error=str(exc))
            self._mem_entries[entry.signal_id] = entry.to_dict()

    async def record_decision(
        self,
        signal_id: str,
        decision: str,
        by: str = "andrii",
        reason: str = "",
        *,
        symbol: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> None:
        """Persist a HITL approve/reject and, on reject, a negative constraint.

        ``symbol``/``direction`` are embedded into the constraint summary because
        :meth:`SamAgent._match_constraint` matches on that text. Without them a
        rejected signal never blocked a repeat proposal for the same instrument,
        which made the whole negative-constraint gate a no-op.
        """
        status = "approved" if decision == "approve" else "rejected"
        pool = self._pool()
        if pool is None:
            e = self._mem_entries.get(signal_id)
            if e:
                e["status"] = status
                e["hitl_decision"] = decision
                e["hitl_by"] = by
        else:
            try:
                async with pool.acquire() as conn:
                    await conn.execute(
                        """
                        UPDATE agents.sam_trade_journal
                        SET status=$2, hitl_decision=$3, hitl_by=$4, decided_at=NOW()
                        WHERE signal_id=$1
                        """,
                        signal_id, status, decision, by,
                    )
            except Exception as exc:  # noqa: BLE001
                logger.warning("journal_decision_write_failed", error=str(exc))

        if decision == "reject":
            where = f"{symbol or '?'}:{direction or '?'}"
            base = reason or "Signal rejected by human — pattern flagged for review"
            await self.add_reflection(
                signal_id=signal_id,
                kind="negative_constraint",
                summary=f"{where} — {base}",
                detail={"symbol": symbol, "direction": direction},
            )

    async def get_signal(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """Return a recorded signal (or ``None``) so callers can enrich decisions."""
        pool = self._pool()
        if pool is None:
            return self._mem_entries.get(signal_id)
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT signal_id, symbol, direction, status
                    FROM agents.sam_trade_journal
                    WHERE signal_id = $1
                    """,
                    signal_id,
                )
            return dict(row) if row else None
        except Exception as exc:  # noqa: BLE001
            logger.warning("journal_signal_read_failed", error=str(exc))
            return None

    async def record_outcome(
        self, signal_id: str, outcome: str, realized_r: Optional[float] = None
    ) -> None:
        pool = self._pool()
        if pool is None:
            e = self._mem_entries.get(signal_id)
            if e:
                e["outcome"] = outcome
                e["realized_r"] = realized_r
                e["status"] = "closed"
            return
        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE agents.sam_trade_journal
                    SET outcome=$2, realized_r=$3, status='closed', closed_at=NOW()
                    WHERE signal_id=$1
                    """,
                    signal_id, outcome, realized_r,
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("journal_outcome_write_failed", error=str(exc))

    # ------------------------------------------------------------------ #
    # Reflections / lessons (RAG negative constraints).
    # ------------------------------------------------------------------ #
    async def add_reflection(
        self,
        *,
        summary: str,
        kind: str = "lesson",
        signal_id: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None,
        weight: float = 1.0,
    ) -> None:
        row = {
            "signal_id": signal_id,
            "kind": kind,
            "summary": summary,
            "detail": detail or {},
            "weight": weight,
            "created_at": _utcnow().isoformat(),
        }
        pool = self._pool()
        if pool is None:
            self._mem_reflections.append(row)
            logger.info("reflection_added", kind=kind, backend="memory")
            return
        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO agents.sam_reflections
                        (signal_id, kind, summary, detail, weight)
                    VALUES ($1,$2,$3,$4,$5)
                    """,
                    signal_id, kind, summary, json.dumps(detail or {}), weight,
                )
            logger.info("reflection_added", kind=kind, backend="postgres")
        except Exception as exc:  # noqa: BLE001
            logger.warning("reflection_write_failed", error=str(exc))
            self._mem_reflections.append(row)

    def _filter_constraints(
        self,
        rows: List[Dict[str, Any]],
        symbol: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Apply the symbol filter + limit consistently for both backends.

        ``symbol`` used to be accepted and then silently ignored, so a
        constraint learned on BTCUSDT gated ETHUSDT too (and the caller in
        :meth:`SamAgent.evaluate_setup` believed it was symbol-scoped).
        """
        items = [r for r in rows if r.get("kind") == "negative_constraint"]
        if symbol:
            wanted = symbol.upper()
            items = [r for r in items if self._constraint_symbol(r) == wanted]
        return items[-limit:]

    def _constraint_symbol(self, row: Dict[str, Any]) -> str:
        """Resolve a reflection's instrument: detail -> journal entry -> SQL join."""
        for candidate in (
            (row.get("detail") or {}).get("symbol"),
            row.get("symbol"),
        ):
            if candidate:
                return str(candidate).upper()
        entry = self._mem_entries.get(row.get("signal_id")) or {}
        return str(entry.get("symbol") or "").upper()

    async def negative_constraints(self, symbol: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Return active negative constraints to gate new proposals.

        When ``symbol`` is given only the constraints recorded for that symbol
        are returned; pass ``None`` for the global set.
        """
        pool = self._pool()
        if pool is None:
            return self._filter_constraints(self._mem_reflections, symbol, limit)
        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT r.signal_id, r.kind, r.summary, r.detail, r.weight,
                           r.created_at, j.symbol AS symbol
                    FROM agents.sam_reflections r
                    LEFT JOIN agents.sam_trade_journal j ON j.signal_id = r.signal_id
                    WHERE r.kind = 'negative_constraint'
                      AND ($2::text IS NULL OR j.symbol = $2)
                    ORDER BY r.created_at DESC
                    LIMIT $1
                    """,
                    limit,
                    symbol.upper() if symbol else None,
                )
            return [dict(r) for r in rows]
        except Exception as exc:  # noqa: BLE001
            logger.warning("negative_constraints_read_failed", error=str(exc))
            return []

    # ------------------------------------------------------------------ #
    # Performance calibration (feeds threshold self-tuning).
    # ------------------------------------------------------------------ #
    async def performance_stats(self, lookback: int = 200) -> Dict[str, Any]:
        """Summarise recent realised outcomes for calibration / reporting.

        This reports *realised* statistics from the journal — it never
        fabricates or projects a win-rate.  With no closed trades it returns
        zeros and ``sample=0`` so callers must not over-interpret it.
        """
        entries: List[Dict[str, Any]] = []
        pool = self._pool()
        if pool is None:
            entries = [e for e in self._mem_entries.values() if e.get("outcome")]
        else:
            try:
                async with pool.acquire() as conn:
                    rows = await conn.fetch(
                        """
                        SELECT outcome, realized_r, confluence_score
                        FROM agents.sam_trade_journal
                        WHERE outcome IS NOT NULL
                        ORDER BY closed_at DESC NULLS LAST
                        LIMIT $1
                        """,
                        lookback,
                    )
                entries = [dict(r) for r in rows]
            except Exception as exc:  # noqa: BLE001
                logger.warning("performance_stats_read_failed", error=str(exc))
                entries = []

        sample = len(entries)
        wins = sum(1 for e in entries if e.get("outcome") == "win")
        rs = [float(e["realized_r"]) for e in entries if e.get("realized_r") is not None]
        return {
            "sample": sample,
            "wins": wins,
            "losses": sum(1 for e in entries if e.get("outcome") == "loss"),
            "realized_win_rate": round(wins / sample, 4) if sample else 0.0,
            "avg_realized_r": round(sum(rs) / len(rs), 3) if rs else 0.0,
            "note": "Realised stats only; not a forward-looking probability.",
        }
