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
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import redis.asyncio as aioredis
import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

logger = structlog.get_logger(__name__)

EMBEDDING_DIM = 1536  # text-embedding-3-small


def _ensure_uuid(val: Optional[str]) -> str:
    """Ensure value is a valid UUID string; convert arbitrary strings deterministically via UUID5."""
    if not val:
        return str(uuid.uuid4())
    try:
        return str(uuid.UUID(str(val)))
    except (ValueError, TypeError, AttributeError):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(val)))


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
    """Unified memory interface for EVA agents."""

    def __init__(self, postgres_dsn: str, redis_url: str) -> None:
        self._postgres_dsn = postgres_dsn
        self._redis_url = redis_url
        self._engine = None
        self._session_factory = None
        self._redis: Optional[aioredis.Redis] = None
        self._ready = False

    @property
    def is_ready(self) -> bool:
        return self._ready

    async def initialize(self) -> None:
        """Initialize database and Redis connections."""
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

        self._redis = await aioredis.from_url(
            self._redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await self._redis.ping()

        self._ready = True
        logger.info("Memory manager initialized")

    async def close(self) -> None:
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

        vector_str = str(embedding) if embedding else None

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

        return episode_id

    async def get_recent_episodes(
        self,
        session_id: str,
        agent_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Retrieve recent episodes from cache or database."""
        norm_session_id = _ensure_uuid(session_id)
        if self._redis is not None:
            cache_key = f"episodes:{norm_session_id}:{agent_id}"
            cached = await self._redis.lrange(cache_key, 0, limit - 1)
            if cached:
                return [json.loads(ep) for ep in cached]

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
                  AND (:agent_id IS NULL OR agent_id = :agent_id)
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
                  AND (:agent_id IS NULL OR agent_id = :agent_id)
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
