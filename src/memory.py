"""
Memory Manager: semantic (pgvector) + episodic (PostgreSQL) + cache (Redis).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import redis.asyncio as aioredis
import structlog
from pgvector.asyncpg import register_vector
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

logger = structlog.get_logger(__name__)

EMBEDDING_DIM = 1536  # text-embedding-3-small


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
        """Initialize database connections."""
        # PostgreSQL
        self._engine = create_async_engine(
            self._postgres_dsn,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )

        # Register pgvector type with asyncpg
        async with self._engine.begin() as conn:
            await conn.execute(text("SELECT 1"))  # Test connection

        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

        # Redis
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
        session_id: str,
        agent_id: str,
        role: str,
        content: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save a conversation turn or agent event."""
        episode_id = str(uuid.uuid4())
        async with self._session_factory() as session:
            await session.execute(
                text("""
                    INSERT INTO memory.episodes
                    (id, session_id, agent_id, role, content, content_vector, metadata)
                    VALUES (:id, :session_id, :agent_id, :role, :content, :vector, :metadata)
                """),
                {
                    "id": episode_id,
                    "session_id": session_id,
                    "agent_id": agent_id,
                    "role": role,
                    "content": content,
                    "vector": str(embedding) if embedding else None,
                    "metadata": json.dumps(metadata or {}),
                },
            )
            await session.commit()

        # Cache last N episodes in Redis for fast retrieval
        cache_key = f"episodes:{session_id}:{agent_id}"
        await self._redis.lpush(cache_key, json.dumps({
            "id": episode_id,
            "role": role,
            "content": content,
            "created_at": datetime.utcnow().isoformat(),
        }))
        await self._redis.ltrim(cache_key, 0, 49)  # Keep last 50
        await self._redis.expire(cache_key, 3600)  # 1 hour TTL

        return episode_id

    async def get_recent_episodes(
        self,
        session_id: str,
        agent_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Retrieve recent episodes from cache or database."""
        cache_key = f"episodes:{session_id}:{agent_id}"
        cached = await self._redis.lrange(cache_key, 0, limit - 1)

        if cached:
            return [json.loads(ep) for ep in cached]

        # Fallback to database
        async with self._session_factory() as session:
            result = await session.execute(
                text("""
                    SELECT id, role, content, metadata, created_at
                    FROM memory.episodes
                    WHERE session_id = :session_id AND agent_id = :agent_id
                    ORDER BY created_at DESC
                    LIMIT :limit
                """),
                {"session_id": session_id, "agent_id": agent_id, "limit": limit},
            )
            rows = result.fetchall()
            return [
                {"id": str(r.id), "role": r.role, "content": r.content,
                 "metadata": r.metadata, "created_at": str(r.created_at)}
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
        """Find semantically similar episodes using HNSW index."""
        async with self._session_factory() as session:
            query = """
                SELECT id, agent_id, role, content, metadata, created_at,
                       1 - (content_vector <=> :embedding::vector) AS similarity
                FROM memory.episodes
                WHERE content_vector IS NOT NULL
                  AND (:agent_id IS NULL OR agent_id = :agent_id)
                  AND 1 - (content_vector <=> :embedding::vector) >= :min_similarity
                ORDER BY content_vector <=> :embedding::vector
                LIMIT :limit
            """
            result = await session.execute(
                text(query),
                {
                    "embedding": str(query_embedding),
                    "agent_id": agent_id,
                    "min_similarity": min_similarity,
                    "limit": limit,
                },
            )
            rows = result.fetchall()
            return [
                {
                    "id": str(r.id),
                    "agent_id": r.agent_id,
                    "role": r.role,
                    "content": r.content,
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
        async with self._session_factory() as session:
            await session.execute(
                text("""
                    INSERT INTO agents.checkpoints
                    (thread_id, checkpoint_id, agent_id, state_data, metadata)
                    VALUES (:thread_id, :checkpoint_id, :agent_id, :state_data, :metadata)
                    ON CONFLICT (thread_id, checkpoint_id) DO UPDATE
                    SET state_data = EXCLUDED.state_data,
                        metadata = EXCLUDED.metadata
                """),
                {
                    "thread_id": thread_id,
                    "checkpoint_id": checkpoint_id,
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
        """Load the latest or specific checkpoint."""
        async with self._session_factory() as session:
            if checkpoint_id:
                q = text("""
                    SELECT state_data FROM agents.checkpoints
                    WHERE thread_id = :thread_id AND checkpoint_id = :checkpoint_id
                """)
                params = {"thread_id": thread_id, "checkpoint_id": checkpoint_id}
            else:
                q = text("""
                    SELECT state_data FROM agents.checkpoints
                    WHERE thread_id = :thread_id
                    ORDER BY created_at DESC LIMIT 1
                """)
                params = {"thread_id": thread_id}

            result = await session.execute(q, params)
            row = result.fetchone()
            if row:
                return json.loads(row.state_data)
            return None

    # ─── Semantic Response Cache (Token Savings) ───────────────────────────

    async def check_response_cache(
        self,
        query_embedding: List[float],
        agent_id: Optional[str] = None,
        similarity_threshold: float = 0.95,
    ) -> Optional[Dict[str, Any]]:
        """Check if a semantically similar query was already answered."""
        async with self._session_factory() as session:
            query = """
                SELECT id, response_text, tokens_saved, hit_count,
                       1 - (query_vector <=> :embedding::vector) AS similarity
                FROM memory.response_cache
                WHERE query_vector IS NOT NULL
                  AND (:agent_id IS NULL OR agent_id = :agent_id)
                  AND (expires_at IS NULL OR expires_at > NOW())
                  AND 1 - (query_vector <=> :embedding::vector) >= :threshold
                ORDER BY query_vector <=> :embedding::vector
                LIMIT 1
            """
            result = await session.execute(
                text(query),
                {
                    "embedding": str(query_embedding),
                    "agent_id": agent_id,
                    "threshold": similarity_threshold,
                },
            )
            row = result.fetchone()
            if row:
                # Increment hit count asynchronously
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
        """Cache an LLM response with pgvector embedding and TTL."""
        async with self._session_factory() as session:
            await session.execute(
                text("""
                    INSERT INTO memory.response_cache
                    (agent_id, query_text, query_vector, response_text, model_used, tokens_saved, ttl_hours, expires_at)
                    VALUES (:agent_id, :query_text, :vector, :response_text, :model_used, :tokens_saved, :ttl_hours,
                            NOW() + INTERVAL '1 hour' * :ttl_hours)
                """),
                {
                    "agent_id": agent_id,
                    "query_text": query_text,
                    "vector": str(query_embedding),
                    "response_text": response_text,
                    "model_used": model_used,
                    "tokens_saved": tokens_saved,
                    "ttl_hours": ttl_hours,
                },
            )
            await session.commit()

