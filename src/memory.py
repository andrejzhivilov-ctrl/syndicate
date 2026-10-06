"""
Memory Manager: semantic (pgvector) + episodic (PostgreSQL) + cache (Redis).
v4.1 Verified:
- Uses CAST(:embedding AS vector) instead of ::vector to avoid SQLAlchemy parameter syntax conflicts.
- Deterministic UUID5 normalization for session_id so arbitrary string session IDs never fail UUID column constraints.
- Handles JSONB auto-deserialization in asyncpg (dict vs str).
- Flexible save_episode signature supporting both positional and keyword calls (session_id, role, category).
"""

from __future__ import annotations

import json
import math
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import asyncpg
import redis.asyncio as aioredis
import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.embeddings import EMBEDDING_DIM, EmbeddingUnavailable  # noqa: F401  (re-exported)
from src.pii import PIIRedactor

logger = structlog.get_logger(__name__)
_AUDIT_REDACTOR = PIIRedactor()

_AUDIT_LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")
_AUDIT_HASH_RE = re.compile(r"^[a-fA-F0-9]{64}$")
_AUDIT_OUTCOMES = {"pending", "success", "failure", "overridden", "blocked", "refused"}
_AUDIT_ESCALATIONS = {"act", "ask", "refuse"}
_AUDIT_RISK_LEVELS = {"low", "medium", "high", "critical", "unknown"}


def _audit_label(value: Any, *, limit: int, default: str = "unknown") -> str:
    """Keep only bounded identifier labels, never partially retain free-form input."""
    label = str(value or "").strip()
    if not label or not _AUDIT_LABEL_RE.fullmatch(label):
        return default
    redacted, _events = _AUDIT_REDACTOR.redact(label)
    if redacted != label:
        return default
    return label[:limit]


def _audit_labels(values: Any, *, limit: int = 32) -> List[str]:
    """Keep only bounded identifier labels for JSONB audit columns."""
    if not isinstance(values, (list, tuple, set)):
        return []
    safe = []
    for item in list(values)[:limit]:
        if isinstance(item, str) and len(item) <= 128:
            label = _audit_label(item, limit=128, default="")
            if label:
                safe.append(label)
    return safe


def _audit_count(value: Any) -> Optional[int]:
    try:
        return max(0, min(10000, int(value)))
    except (TypeError, ValueError, OverflowError):
        return None


def _audit_score(value: Any) -> Optional[float]:
    try:
        score = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return round(min(1.0, max(0.0, score)), 3) if math.isfinite(score) else None


def _audit_details(details: Any) -> Dict[str, Any]:
    """Allow only low-risk correlation/status fields in the durable audit row."""
    if not isinstance(details, dict):
        return {}
    safe: Dict[str, Any] = {}
    for key in ("task_id", "result_status", "skill_capture_status"):
        if details.get(key) is not None:
            safe[key] = _audit_label(details[key], limit=128)
    for key in ("requires_hitl", "hitl_override", "allowed"):
        if isinstance(details.get(key), bool):
            safe[key] = details[key]
    for key in ("prior_lessons_count", "blocked_actions_count"):
        if key in details and (count := _audit_count(details[key])) is not None:
            safe[key] = count
    if "risk_score" in details and (score := _audit_score(details["risk_score"])) is not None:
        safe["risk_score"] = score
    return safe

"""Module-level alias kept for callers that imported it from here."""



def _ensure_uuid(val: Optional[str]) -> str:
    """Ensure value is a valid UUID string; convert arbitrary strings deterministically via UUID5."""
    if not val:
        return str(uuid.uuid4())
    try:
        return str(uuid.UUID(str(val)))
    except (ValueError, TypeError, AttributeError):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(val)))


def _redact_dsn(text: str) -> str:
    """Strip credentials from any ``scheme://user:password@host`` inside a message.

    Connection errors are logged, and a Redis/PostgreSQL URL can embed the
    password (``redis://:secret@host:6379/0``). Logging it verbatim would leak a
    secret into the log stream that ``deploy/`` ships off-box.
    """
    return re.sub(r"(?i)(\w+://)[^/@\s]*@", r"\1***@", str(text))


def _ensure_dict(val: Any) -> Dict[str, Any]:
    """Safely normalize JSONB column value (which asyncpg may return as dict or str)."""
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return {"raw": val}
    return {}


class MemoryManager:
    """Unified memory interface for EVA agents.

    Owns two connection pools to the same PostgreSQL database:

    * ``_engine`` / ``_session_factory`` — SQLAlchemy+asyncpg, used by the
      vector/JSONB code paths (episodes, semantic search, lessons).
    * ``pool`` — a raw ``asyncpg`` pool, used by the v4 components that speak
      libpq SQL with ``$1`` placeholders and probe ``memory.pool`` /
      ``memory._pool`` / ``memory.db_pool`` (Sam's ``TradeJournal`` and the
      per-device ``DeviceTokenStore``). Before this pool existed both silently
      fell back to volatile in-memory storage, so ``agents.sam_trade_journal``
      and ``auth.device_tokens`` stayed empty in production and every restart
      lost the data.
    """

    def __init__(
        self,
        postgres_dsn: str,
        redis_url: str = "",
        embedder: Optional[Any] = None,
    ) -> None:
        self._postgres_dsn = postgres_dsn
        self._redis_url = redis_url or ""
        self._engine = None
        self._session_factory = None
        self._redis: Optional[aioredis.Redis] = None
        self._ready = False
        # Vector producer for semantic search. ``None`` is a supported mode: the
        # memory still works, only semantic search reports "disabled".
        self._embedder = embedder
        # Counted so a degraded deployment is visible instead of merely slow.
        self.embedding_failures = 0
        # Raw asyncpg pool for the ``$1``-style SQL components (see class docstring).
        self.pool: Optional[asyncpg.Pool] = None

    @property
    def embeddings_enabled(self) -> bool:
        return self._embedder is not None

    async def _embed(self, text: str, *, what: str) -> Optional[List[float]]:
        """Produce a vector, or ``None`` when the provider cannot.

        A missing vector is never a reason to lose the episode or the lesson: the
        text is the valuable part, and semantic search simply will not find that
        one row. Reporting is left to the caller — the counter makes the
        degradation observable.
        """
        if self._embedder is None or not str(text).strip():
            return None
        try:
            return await self._embedder.embed_one(str(text))
        except EmbeddingUnavailable as exc:
            self.embedding_failures += 1
            logger.warning("embedding_unavailable", what=what, error=str(exc))
            return None

    async def embedding_status(self) -> Dict[str, Any]:
        """Honest status of the vector layer for health output."""
        if self._embedder is None:
            return {
                "status": "disabled",
                "value": None,
                "warning": "no embedding provider configured — semantic search is off",
                "failures": self.embedding_failures,
            }
        probe = await self._embedder.health()
        return {**probe, "failures": self.embedding_failures}


    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def cache_enabled(self) -> bool:
        """Whether the Redis cache layer is currently in use.

        False is a normal, supported state: every read is then served by
        PostgreSQL. Callers may expose it so an operator can see that the cache
        degraded instead of wondering why reads are slower.
        """
        return self._redis is not None

    def _libpq_dsn(self) -> str:
        """Strip SQLAlchemy driver suffixes — ``asyncpg`` only understands libpq DSNs."""
        return self._postgres_dsn.replace("postgresql+asyncpg://", "postgresql://").replace(
            "postgres+asyncpg://", "postgresql://"
        )

    async def initialize(self) -> None:
        """Initialize database and Redis connections.

        Redis is optional: without ``redis_url`` the cache layer is disabled and
        every read goes to PostgreSQL (slower but always correct). This keeps the
        agent usable when only the database is provisioned.
        """
        self._engine = create_async_engine(
            self._postgres_dsn,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )

        async with self._engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

        # A failure here must not be silent: without the pool the journal and
        # device tokens degrade to memory-only storage.
        try:
            self.pool = await asyncpg.create_pool(self._libpq_dsn(), min_size=1, max_size=5)
        except Exception as exc:  # noqa: BLE001
            self.pool = None
            logger.warning(
                "asyncpg_pool_unavailable",
                error=str(exc),
                impact="trade journal and device tokens fall back to memory-only storage",
            )

        if self._redis_url:
            self._redis = await self._connect_redis(self._redis_url)
        else:
            self._redis = None
            logger.warning("redis_cache_disabled", reason="no redis_url configured")

        self._ready = True
        logger.info("Memory manager initialized")

    async def _connect_redis(self, redis_url: str) -> Optional[aioredis.Redis]:
        """Connect to Redis, degrading to "no cache" instead of failing startup.

        Redis is declared optional (see :meth:`initialize`), yet the bare
        ``ping()`` used to raise straight out of ``initialize()``. A password
        mismatch — the ``requirepass`` placeholder that ``deploy/scripts`` ships —
        therefore aborted the whole application startup through ``lifespan``,
        even though every read can be served by PostgreSQL. A cache outage must
        cost latency, never availability.
        """
        client: Optional[aioredis.Redis] = None
        try:
            client = await aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
            await client.ping()
            logger.info("redis_cache_enabled")
            return client
        except Exception as exc:  # noqa: BLE001
            if client is not None:
                try:
                    await client.aclose()
                except Exception:  # noqa: BLE001
                    pass
            logger.warning(
                "redis_cache_disabled",
                error=_redact_dsn(str(exc)),
                impact="every read falls back to PostgreSQL (slower, always correct)",
            )
            return None

    async def _disable_redis(self, reason: str, error: Exception) -> None:
        """Circuit-breaker: drop a cache that failed mid-flight.

        The cache is a latency optimisation, so a failure in it must never
        propagate into an agent call. Disabling it once keeps a broken Redis from
        adding a timeout to every subsequent read.
        """
        self._redis = None
        logger.warning(
            "redis_cache_disabled_midflight",
            reason=reason,
            error=_redact_dsn(str(error)),
            impact="reads fall back to PostgreSQL for the rest of this process",
        )

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None
        if self._engine:
            await self._engine.dispose()
        if self._redis:
            await self._redis.aclose()
        self._ready = False

    # ─── Episodic Memory ─────────────────────────────────────────────────────

    async def save_episode(
        self,
        session_id: Optional[str] = None,
        agent_id: str = "eva",
        role: str = "assistant",
        content: str = "",
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
    ) -> str:
        """Save a conversation turn or agent event.
        Supports optional category keyword (merged into metadata) and auto-normalizes session_id to UUID.
        """
        episode_id = str(uuid.uuid4())
        norm_session_id = _ensure_uuid(session_id or f"default-{agent_id}")
        valid_role = role if role in ("user", "assistant", "system", "tool") else "assistant"

        meta = dict(metadata or {})
        if category:
            meta["category"] = category

        if embedding is None:
            # This is the write half of vector memory: until now nothing ever
            # passed an embedding, so ``content_vector`` stayed NULL for every row
            # and semantic search had nothing to search.
            embedding = await self._embed(content, what=f"episode:{agent_id}")

        vector_str = str(list(embedding)) if embedding else None

        if self._session_factory is not None:
            async with self._session_factory() as session:
                if vector_str is not None:
                    await session.execute(
                        text("""
                            INSERT INTO memory.episodes
                            (id, session_id, agent_id, role, content, content_vector, metadata)
                            VALUES (CAST(:id AS uuid), CAST(:session_id AS uuid), :agent_id, :role, :content, CAST(:vector AS vector), CAST(:metadata AS jsonb))
                        """),
                        {
                            "id": episode_id,
                            "session_id": norm_session_id,
                            "agent_id": agent_id,
                            "role": valid_role,
                            "content": str(content),
                            "vector": vector_str,
                            "metadata": json.dumps(meta),
                        },
                    )
                else:
                    await session.execute(
                        text("""
                            INSERT INTO memory.episodes
                            (id, session_id, agent_id, role, content, content_vector, metadata)
                            VALUES (CAST(:id AS uuid), CAST(:session_id AS uuid), :agent_id, :role, :content, NULL, CAST(:metadata AS jsonb))
                        """),
                        {
                            "id": episode_id,
                            "session_id": norm_session_id,
                            "agent_id": agent_id,
                            "role": valid_role,
                            "content": str(content),
                            "metadata": json.dumps(meta),
                        },
                    )
                await session.commit()

        if self._redis is not None:
            try:
                cache_key = f"episodes:{norm_session_id}:{agent_id}"
                await self._redis.lpush(cache_key, json.dumps({
                    "id": episode_id,
                    "role": valid_role,
                    "content": str(content),
                    "metadata": meta,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }))
                await self._redis.ltrim(cache_key, 0, 49)
                await self._redis.expire(cache_key, 3600)
            except Exception as exc:  # noqa: BLE001
                # The episode is already committed to PostgreSQL; a cache write
                # failure must not surface as a failed memory write.
                await self._disable_redis("write_failed", exc)

        return episode_id

    async def get_recent_episodes(
        self,
        session_id: str,
        agent_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Retrieve recent episodes from cache or database."""
        norm_session_id = _ensure_uuid(session_id or f"default-{agent_id}")
        if self._redis is not None:
            try:
                cache_key = f"episodes:{norm_session_id}:{agent_id}"
                cached = await self._redis.lrange(cache_key, 0, limit - 1)
                if cached:
                    return [json.loads(ep) for ep in cached]
            except Exception as exc:  # noqa: BLE001
                # Fall through to PostgreSQL — the cache is optional.
                await self._disable_redis("read_failed", exc)

        if self._session_factory is None:
            return []

        async with self._session_factory() as session:
            result = await session.execute(
                text("""
                    SELECT id, role, content, metadata, created_at
                    FROM memory.episodes
                    WHERE session_id = CAST(:session_id AS uuid) AND agent_id = :agent_id
                    ORDER BY created_at DESC
                    LIMIT :limit
                """),
                {"session_id": norm_session_id, "agent_id": agent_id, "limit": limit},
            )
            rows = result.fetchall()
            return [
                {
                    "id": str(r.id),
                    "role": r.role,
                    "content": r.content,
                    "metadata": _ensure_dict(r.metadata),
                    "created_at": str(r.created_at),
                }
                for r in rows
            ]

    # ─── Semantic Search ──────────────────────────────────────────────────────

    async def semantic_search(
        self,
        query_embedding: List[float],
        agent_id: Optional[str] = None,
        limit: int = 5,
        min_similarity: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Find semantically similar episodes using HNSW index and CAST(:embedding AS vector)."""
        if not query_embedding or not isinstance(query_embedding, (list, tuple)):
            return []
        if self._session_factory is None:
            return []

        async with self._session_factory() as session:
            query = """
                SELECT id, agent_id, role, content, metadata, created_at,
                       1 - (content_vector <=> CAST(:embedding AS vector)) AS similarity
                FROM memory.episodes
                WHERE content_vector IS NOT NULL
                  -- CAST(:agent_id AS text) is required: bare "(:agent_id IS NULL)"
                  -- makes asyncpg raise AmbiguousParameterError ("could not
                  -- determine data type of parameter $2") whenever a caller
                  -- passes agent_id=..., i.e. semantic search was broken
                  -- against a real database.
                  AND (CAST(:agent_id AS text) IS NULL OR agent_id = :agent_id)
                  AND 1 - (content_vector <=> CAST(:embedding AS vector)) >= :min_similarity
                ORDER BY content_vector <=> CAST(:embedding AS vector)
                LIMIT :limit
            """
            result = await session.execute(
                text(query),
                {
                    "embedding": str(list(query_embedding)),
                    "agent_id": agent_id,
                    "min_similarity": float(min_similarity),
                    "limit": int(limit),
                },
            )
            rows = result.fetchall()
            return [
                {
                    "id": str(r.id),
                    "agent_id": r.agent_id,
                    "role": r.role,
                    "content": r.content,
                    "metadata": _ensure_dict(r.metadata),
                    "similarity": float(r.similarity),
                    "created_at": str(r.created_at),
                }
                for r in rows
            ]

    # ─── Prompt-ready recall (the read half of the memory loop) ─────────────

    ROLE_LABELS = {"user": "Оператор", "assistant": "Агент", "system": "Система", "tool": "Інструмент"}
    # Worst-case length of the "older episodes did not fit" note, reserved inside
    # ``max_chars`` so the finished block never exceeds the budget.
    TRUNCATION_NOTE_RESERVE = 160

    # The recall block is assembled in small pieces on purpose: one method per
    # decision (what to embed, what to merge, what fits the budget, how to render)
    # keeps each of them readable and testable in isolation.
    CONTEXT_HEADER = "Твоя пам'ять — витяг з останніх епізодів цієї сесії (не повний діалог):"

    async def build_memory_context(
        self,
        agent_id: str,
        session_id: Optional[str] = None,
        query_embedding: Optional[List[float]] = None,
        query_text: Optional[str] = None,
        limit: int = 20,
        max_chars: int = 4000,
        per_episode_chars: int = 400,
    ) -> Dict[str, Any]:
        """Compose a bounded, prompt-ready recap of what an agent remembers.

        This is the **read** half of the memory loop. Agents called
        ``save_episode`` and read nothing back, so every conversation started
        from zero and the stored episodes were a pure token/storage cost with no
        benefit.

        Two honesty rules from ``AGENTS.md`` are enforced here:

        * "could not read" → ``status="unavailable"`` with a ``warning``; the
          caller must not pretend it remembered anything.
        * "read it, there was nothing" → ``status="ok"`` with empty ``text``;
          that is a real result, not a failure.

        Token economy is the point: the block never exceeds ``max_chars``
        (≈4 characters per token for Ukrainian), each episode is clipped to
        ``per_episode_chars``, and ``dropped`` reports exactly how many older
        episodes did not fit the budget. The agent recalls the recent past
        instead of re-reading the dialogue.
        """
        # Reported separately from the overall status: episodic recall can succeed
        # while the vector half is off, and the caller deserves to know which.
        semantic_status: Dict[str, Any] = {
            "status": "disabled" if self._embedder is None else "not_requested",
            "warning": None,
        }
        empty = self._empty_context(agent_id, semantic_status)

        query_embedding, semantic_status = await self._resolve_query_embedding(
            query_embedding, query_text, agent_id, semantic_status
        )

        try:
            episodes = await self.get_recent_episodes(
                session_id=session_id or f"default-{agent_id}",
                agent_id=agent_id,
                limit=max(0, int(limit)),
            )
            semantic = await self._semantic_matches(query_embedding, agent_id)
        except Exception as exc:  # noqa: BLE001
            # Redis already degrades internally; this guard covers a database
            # that is down. An agent must still answer without its memory.
            logger.warning("memory_context_unavailable", agent_id=agent_id, error=str(exc))
            return {**empty, "status": "unavailable", "warning": f"memory read failed: {exc}"}

        if query_embedding and semantic_status["status"] == "not_requested":
            semantic_status = {"status": "ok", "warning": None}

        if not episodes and not semantic:
            # Checked, found nothing. Not a failure — do not inject anything.
            return empty

        candidates = self._merge_candidates(episodes, semantic)
        kept, dropped = self._fill_budget(candidates, max_chars, per_episode_chars)
        if not kept:
            return {**empty, "episodes_available": len(candidates), "dropped": dropped}

        return {
            "status": "ok",
            "value": None,
            "agent_id": agent_id,
            "text": self._render_context(kept, dropped),
            "episodes_used": len(kept),
            "episodes_available": len(candidates),
            "dropped": dropped,
            "truncated": bool(dropped),
            "warning": None,
            "semantic": semantic_status,
        }

    def _empty_context(self, agent_id: str, semantic_status: Dict[str, Any]) -> Dict[str, Any]:
        """A context that remembers nothing — used for both "empty" and "failed"."""
        return {
            "status": "ok",
            "value": None,
            "agent_id": agent_id,
            "text": "",
            "episodes_used": 0,
            "episodes_available": 0,
            "dropped": 0,
            "truncated": False,
            "warning": None,
            "semantic": semantic_status,
        }

    async def _resolve_query_embedding(
        self,
        query_embedding: Optional[List[float]],
        query_text: Optional[str],
        agent_id: str,
        semantic_status: Dict[str, Any],
    ) -> tuple:
        """Embed the current question, or report why that was not possible."""
        if query_embedding is not None or not query_text or self._embedder is None:
            return query_embedding, semantic_status
        try:
            return await self._embedder.embed_one(str(query_text)), {"status": "ok", "warning": None}
        except EmbeddingUnavailable as exc:
            self.embedding_failures += 1
            logger.warning("memory_query_embedding_failed", agent_id=agent_id, error=str(exc))
            return None, {
                "status": "unavailable",
                "warning": f"query could not be embedded: {exc}",
            }

    async def _semantic_matches(
        self, query_embedding: Optional[List[float]], agent_id: str
    ) -> List[Dict[str, Any]]:
        """Vector matches for the current query; empty when there is no vector."""
        if not query_embedding:
            return []
        return await self.semantic_search(
            query_embedding=query_embedding, agent_id=agent_id, limit=5
        )

    @staticmethod
    def _merge_candidates(
        episodes: List[Dict[str, Any]], semantic: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Recent episodes first, then semantic matches that are not already there.

        Order matters: it is the order the budget is filled in, so the freshest
        memory is the last thing to be dropped.
        """
        seen = {str(episode.get("id")) for episode in episodes}
        return list(episodes) + [
            episode for episode in semantic if str(episode.get("id")) not in seen
        ]

    def _fill_budget(
        self, candidates: List[Dict[str, Any]], max_chars: int, per_episode_chars: int
    ) -> tuple:
        """Greedily keep episodes until the character budget is spent.

        ``max_chars`` is a hard limit, so the header and the truncation note are
        reserved up front instead of being appended afterwards and pushing the
        block over budget.
        """
        budget = max(
            0, int(max_chars) - len(self.CONTEXT_HEADER) - 1 - self.TRUNCATION_NOTE_RESERVE
        )
        per_episode = max(0, int(per_episode_chars))
        kept: List[str] = []
        used = 0
        for episode in candidates:
            line = self._format_episode(episode, per_episode)
            if not line:
                continue
            if used + len(line) + 1 > budget:
                break
            kept.append(line)
            used += len(line) + 1
        return kept, len(candidates) - len(kept)

    def _render_context(self, kept: List[str], dropped: int) -> str:
        """Oldest-first rendering, with an honest note about what did not fit."""
        lines = list(reversed(kept))
        footer = ""
        if dropped:
            footer = (
                f"\n(Ще {dropped} старіших епізодів не вмістилися в бюджет пам'яті — "
                f"за потреби попроси деталі.)"
            )
        return f"{self.CONTEXT_HEADER}\n" + "\n".join(lines) + footer

    def _format_episode(self, episode: Dict[str, Any], max_chars: int) -> str:
        """One prompt line per episode: ``[MM-DD HH:MM] Роль: текст``."""
        content = str(episode.get("content") or "").strip()
        if not content:
            return ""
        content = " ".join(content.split())  # collapse newlines, keep one line each
        if max_chars and len(content) > max_chars:
            content = content[: max_chars - 1].rstrip() + "…"
        # "2026-10-06 10:20:00+00:00" → "10-06 10:20" (the year is noise inside a
        # recent-episode recap and costs tokens).
        stamp = str(episode.get("created_at") or "")[:16].replace("T", " ")
        stamp = stamp[5:] if stamp else "—"
        role = self.ROLE_LABELS.get(str(episode.get("role")), str(episode.get("role") or "?"))
        return f"[{stamp}] {role}: {content}"

    # ─── Durable audit writes (append-only tables) ─────────────────────────

    async def _write_audit_sql(
        self, *, event: str, statement: str, params: Dict[str, Any]
    ) -> bool:
        """Best-effort append; an audit outage must not change the task result."""
        if self._session_factory is None:
            logger.warning("durable_audit_unavailable", audit_kind=event, reason="database_not_initialized")
            return False
        try:
            async with self._session_factory() as session:
                await session.execute(text(statement), params)
                await session.commit()
            return True
        except Exception as exc:  # noqa: BLE001 - audit failure must never fail agent work
            # Do not log SQL params, action payloads, or exception text that may
            # contain user-controlled values. The exception type is sufficient
            # to diagnose a broken persistence path without copying PII.
            logger.warning("durable_audit_write_failed", audit_kind=event, error_type=type(exc).__name__)
            return False

    async def write_audit_decision(
        self,
        *,
        agent_id: str,
        action: str,
        task_type: Optional[str] = None,
        confidence: Optional[float] = None,
        escalation: Optional[str] = None,
        facts_used: Any = None,
        lessons_checked: Any = None,
        model_used: Optional[str] = None,
        input_hash: Optional[str] = None,
        outcome: str = "pending",
        hitl_override: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Append a privacy-minimized decision row to ``audit.decisions``."""
        safe_confidence = None
        if confidence is not None:
            try:
                value = float(confidence)
                if math.isfinite(value):
                    safe_confidence = round(min(1.0, max(0.0, value)), 3)
            except (TypeError, ValueError, OverflowError):
                pass
        safe_escalation = (
            escalation
            if isinstance(escalation, str) and escalation in _AUDIT_ESCALATIONS
            else None
        )
        safe_outcome = (
            outcome
            if isinstance(outcome, str) and outcome in _AUDIT_OUTCOMES
            else "failure"
        )
        safe_hash = str(input_hash) if input_hash and _AUDIT_HASH_RE.fullmatch(str(input_hash)) else None

        statement = """
            INSERT INTO audit.decisions
                (agent_id, action, task_type, confidence, escalation, facts_used,
                 lessons_checked, model_used, input_hash, outcome, hitl_override, details)
            VALUES
                (:agent_id, :action, :task_type, :confidence, :escalation,
                 CAST(:facts_used AS jsonb), CAST(:lessons_checked AS jsonb),
                 :model_used, :input_hash, :outcome, :hitl_override, CAST(:details AS jsonb))
        """
        params = {
            "agent_id": _audit_label(agent_id, limit=64),
            "action": _audit_label(action, limit=128),
            "task_type": _audit_label(task_type, limit=128) if task_type else None,
            "confidence": safe_confidence,
            "escalation": safe_escalation,
            "facts_used": json.dumps(_audit_labels(facts_used), ensure_ascii=False),
            "lessons_checked": json.dumps(_audit_labels(lessons_checked), ensure_ascii=False),
            "model_used": _audit_label(model_used, limit=64) if model_used else None,
            "input_hash": safe_hash,
            "outcome": safe_outcome,
            "hitl_override": hitl_override is True,
            "details": json.dumps(_audit_details(details), ensure_ascii=False, sort_keys=True),
        }
        return await self._write_audit_sql(event="decision", statement=statement, params=params)

    async def write_outbound_veto(
        self,
        *,
        agent_id: str,
        action_type: str,
        policy_rule: str,
        allowed: bool,
        reason: Optional[str] = None,
        risk_level: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Append a privacy-minimized outbound decision to ``audit.outbound_vetoes``."""
        # Persist only the fixed reason vocabulary used by the orchestrator;
        # ignore arbitrary/free-form strings, even if a redactor could mask known PII.
        safe_reasons = {"outbound_allowed", "outbound_blocked", "approval_required"}
        safe_reason = reason if isinstance(reason, str) and reason in safe_reasons else None
        safe_risk = (
            risk_level
            if isinstance(risk_level, str) and risk_level in _AUDIT_RISK_LEVELS
            else "unknown"
        )
        statement = """
            INSERT INTO audit.outbound_vetoes
                (agent_id, action_type, policy_rule, allowed, reason, risk_level, details)
            VALUES
                (:agent_id, :action_type, :policy_rule, :allowed, :reason, :risk_level,
                 CAST(:details AS jsonb))
        """
        params = {
            "agent_id": _audit_label(agent_id, limit=64),
            "action_type": _audit_label(action_type, limit=128),
            "policy_rule": _audit_label(policy_rule, limit=32),
            "allowed": allowed is True,
            "reason": safe_reason,
            "risk_level": safe_risk,
            "details": json.dumps(_audit_details(details), ensure_ascii=False, sort_keys=True),
        }
        return await self._write_audit_sql(event="outbound_veto", statement=statement, params=params)

    # ─── Agent Checkpoints (LangGraph) ──────────────────────────────────────

    async def save_checkpoint(
        self,
        thread_id: str,
        checkpoint_id: str,
        agent_id: str,
        state_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Save LangGraph agent state checkpoint."""
        if self._session_factory is None:
            return
        async with self._session_factory() as session:
            await session.execute(
                text("""
                    INSERT INTO agents.checkpoints
                    (thread_id, checkpoint_id, agent_id, state_data, metadata)
                    VALUES (:thread_id, :checkpoint_id, :agent_id, CAST(:state_data AS jsonb), CAST(:metadata AS jsonb))
                    ON CONFLICT (thread_id, checkpoint_id) DO UPDATE
                    SET state_data = EXCLUDED.state_data,
                        metadata = EXCLUDED.metadata
                """),
                {
                    "thread_id": str(thread_id),
                    "checkpoint_id": str(checkpoint_id),
                    "agent_id": agent_id,
                    "state_data": json.dumps(state_data),
                    "metadata": json.dumps(metadata or {}),
                },
            )
            await session.commit()

    async def load_checkpoint(
        self,
        thread_id: str,
        checkpoint_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Load the latest or specific checkpoint (handles both dict and str JSONB)."""
        if self._session_factory is None:
            return None
        async with self._session_factory() as session:
            if checkpoint_id:
                q = text("""
                    SELECT state_data FROM agents.checkpoints
                    WHERE thread_id = :thread_id AND checkpoint_id = :checkpoint_id
                """)
                params = {"thread_id": str(thread_id), "checkpoint_id": str(checkpoint_id)}
            else:
                q = text("""
                    SELECT state_data FROM agents.checkpoints
                    WHERE thread_id = :thread_id
                    ORDER BY created_at DESC LIMIT 1
                """)
                params = {"thread_id": str(thread_id)}

            result = await session.execute(q, params)
            row = result.fetchone()
            if row:
                return _ensure_dict(row.state_data)
            return None

    # ─── Semantic Response Cache (Token Savings) ───────────────────────────

    async def check_response_cache(
        self,
        query_embedding: List[float],
        agent_id: Optional[str] = None,
        similarity_threshold: float = 0.95,
    ) -> Optional[Dict[str, Any]]:
        """Check if a semantically similar query was already answered."""
        if not query_embedding or not isinstance(query_embedding, (list, tuple)):
            return None
        if self._session_factory is None:
            return None

        async with self._session_factory() as session:
            query = """
                SELECT id, response_text, tokens_saved, hit_count,
                       1 - (query_vector <=> CAST(:embedding AS vector)) AS similarity
                FROM memory.response_cache
                WHERE query_vector IS NOT NULL
                  -- Same asyncpg inference trap as in semantic_search():
                  -- a bare "(:agent_id IS NULL)" raises AmbiguousParameterError.
                  AND (CAST(:agent_id AS text) IS NULL OR agent_id = :agent_id)
                  AND (expires_at IS NULL OR expires_at > NOW())
                  AND 1 - (query_vector <=> CAST(:embedding AS vector)) >= :threshold
                ORDER BY query_vector <=> CAST(:embedding AS vector)
                LIMIT 1
            """
            result = await session.execute(
                text(query),
                {
                    "embedding": str(list(query_embedding)),
                    "agent_id": agent_id,
                    "threshold": float(similarity_threshold),
                },
            )
            row = result.fetchone()
            if row:
                await session.execute(
                    text("UPDATE memory.response_cache SET hit_count = hit_count + 1 WHERE id = :id"),
                    {"id": row.id},
                )
                await session.commit()
                return {
                    "cache_hit": True,
                    "response": row.response_text,
                    "similarity": float(row.similarity),
                    "tokens_saved": row.tokens_saved,
                }
            return None

    async def cache_response(
        self,
        query_text: str,
        query_embedding: List[float],
        response_text: str,
        agent_id: str,
        model_used: Optional[str] = None,
        tokens_saved: int = 0,
        ttl_hours: int = 24,
    ) -> None:
        """Cache an LLM response with pgvector embedding and TTL using make_interval."""
        if not query_embedding or not isinstance(query_embedding, (list, tuple)):
            return
        if self._session_factory is None:
            return

        async with self._session_factory() as session:
            await session.execute(
                text("""
                    INSERT INTO memory.response_cache
                    (agent_id, query_text, query_vector, response_text, model_used, tokens_saved, ttl_hours, expires_at)
                    VALUES (
                        :agent_id,
                        :query_text,
                        CAST(:vector AS vector),
                        :response_text,
                        :model_used,
                        :tokens_saved,
                        :ttl_hours,
                        NOW() + make_interval(hours => :ttl_hours)
                    )
                """),
                {
                    "agent_id": str(agent_id),
                    "query_text": str(query_text),
                    "vector": str(list(query_embedding)),
                    "response_text": str(response_text),
                    "model_used": model_used,
                    "tokens_saved": int(tokens_saved),
                    "ttl_hours": int(ttl_hours),
                },
            )
            await session.commit()
