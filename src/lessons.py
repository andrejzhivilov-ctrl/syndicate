"""
Syndicate-wide Lessons Layer (src/lessons.py).
v4.1 Verified:
- Matches `memory.lessons` column `lesson_vector`
- Uses `CAST(:embedding AS vector)` instead of `::vector`
- Gracefully falls back to non-vector query when `action_embedding` is None
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy import text

from src.embeddings import EmbeddingUnavailable

logger = structlog.get_logger(__name__)


class LessonsStore:
    """
    Syndicate-wide Lessons Layer. A shared pgvector-backed store where
    ANY agent records failures/lessons and queries before acting.
    """

    def __init__(
        self,
        session_factory: Any,
        redis: Optional[Any] = None,
        embedder: Optional[Any] = None,
    ) -> None:
        self._session_factory = session_factory
        self._redis = redis
        # Vector producer. Without it ``lesson_vector`` stays NULL and
        # ``check_before_action`` keeps using its non-vector fallback — a
        # supported mode, just a weaker one.
        self._embedder = embedder

    async def _embed(self, text: str, *, what: str) -> Optional[List[float]]:
        """Vector for ``text``, or ``None`` — a lesson is never lost for it."""
        if self._embedder is None or not str(text).strip():
            return None
        try:
            return await self._embedder.embed_one(str(text))
        except EmbeddingUnavailable as exc:
            logger.warning("lesson_embedding_unavailable", what=what, error=str(exc))
            return None

    async def record_lesson(
        self,
        agent_id: str,
        kind: str,
        summary: str,
        context: Optional[Any] = None,
        category: Optional[str] = None,
        severity: str = "medium",
        embedding: Optional[List[float]] = None,
        do_not_compress: bool = False,
    ) -> Optional[str]:
        """Record a lesson into the shared store and optionally cache recent ones."""
        if self._session_factory is None:
            return None

        ctx_str = json.dumps(context, ensure_ascii=False) if isinstance(context, (dict, list)) else str(context or "")

        if embedding is None:
            # Kind + summary is what a future action is matched against, so that
            # is exactly what gets embedded.
            embedding = await self._embed(f"{kind}: {summary}", what=f"lesson:{agent_id}")

        vec_str = str(list(embedding)) if embedding else None

        try:
            async with self._session_factory() as session:
                if vec_str is not None:
                    query = text("""
                        INSERT INTO memory.lessons (
                            agent_id, kind, summary, context, category,
                            severity, lesson_vector, do_not_compress, times_matched, created_at
                        ) VALUES (
                            :agent_id, :kind, :summary, :context, :category,
                            :severity, CAST(:embedding AS vector), :do_not_compress, 0, NOW()
                        ) RETURNING id;
                    """)
                    params = {
                        "agent_id": agent_id,
                        "kind": kind,
                        "summary": summary,
                        "context": ctx_str,
                        "category": category,
                        "severity": severity,
                        "embedding": vec_str,
                        "do_not_compress": bool(do_not_compress),
                    }
                else:
                    query = text("""
                        INSERT INTO memory.lessons (
                            agent_id, kind, summary, context, category,
                            severity, lesson_vector, do_not_compress, times_matched, created_at
                        ) VALUES (
                            :agent_id, :kind, :summary, :context, :category,
                            :severity, NULL, :do_not_compress, 0, NOW()
                        ) RETURNING id;
                    """)
                    params = {
                        "agent_id": agent_id,
                        "kind": kind,
                        "summary": summary,
                        "context": ctx_str,
                        "category": category,
                        "severity": severity,
                        "do_not_compress": bool(do_not_compress),
                    }

                result = await session.execute(query, params)
                lesson_id = str(result.scalar_one())
                await session.commit()

                if self._redis is not None:
                    cache_key = f"lessons:{agent_id}:recent"
                    lesson_data = {
                        "id": lesson_id,
                        "agent_id": agent_id,
                        "kind": kind,
                        "summary": summary,
                        "category": category,
                        "severity": severity,
                    }
                    await self._redis.lpush(cache_key, json.dumps(lesson_data))
                    await self._redis.ltrim(cache_key, 0, 19)

            logger.info("recorded_lesson", agent_id=agent_id, lesson_id=lesson_id, kind=kind)
            return lesson_id
        except Exception as exc:  # noqa: BLE001
            logger.exception("failed_to_record_lesson", agent_id=agent_id, exc_info=exc)
            return None

    async def check_before_action(
        self,
        agent_id: str,
        action_embedding: Optional[List[float]] = None,
        limit: int = 5,
        min_similarity: float = 0.72,
        action_text: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query lessons using pgvector cosine similarity search before an action.
        If action_embedding is None, falls back to retrieving recent lessons for the agent/critical severity.

        Pass ``action_text`` (what the agent is about to do) to have it embedded
        here — until now every caller passed ``None``, so the vector branch was
        dead code and only the weaker non-vector fallback ever ran.
        """
        if self._session_factory is None:
            return []

        if action_embedding is None and action_text:
            action_embedding = await self._embed(
                str(action_text), what=f"action_check:{agent_id}"
            )

        try:
            async with self._session_factory() as session:
                if action_embedding and isinstance(action_embedding, (list, tuple)):
                    query = text("""
                        SELECT id, agent_id, kind, summary, context, category, severity, times_matched, created_at,
                               1 - (lesson_vector <=> CAST(:action_embedding AS vector)) AS similarity
                        FROM memory.lessons
                        WHERE lesson_vector IS NOT NULL
                          AND (expires_at IS NULL OR expires_at > NOW())
                          AND (1 - (lesson_vector <=> CAST(:action_embedding AS vector))) >= :min_similarity
                        ORDER BY lesson_vector <=> CAST(:action_embedding AS vector)
                        LIMIT :limit;
                    """)
                    result = await session.execute(
                        query,
                        {
                            "action_embedding": str(list(action_embedding)),
                            "min_similarity": float(min_similarity),
                            "limit": int(limit),
                        },
                    )
                else:
                    # Non-vector fallback: retrieve agent's own lessons + critical syndicate lessons
                    query = text("""
                        SELECT id, agent_id, kind, summary, context, category, severity, times_matched, created_at,
                               1.0 AS similarity
                        FROM memory.lessons
                        WHERE (expires_at IS NULL OR expires_at > NOW())
                          AND (agent_id = :agent_id OR severity IN ('high', 'critical'))
                        ORDER BY created_at DESC
                        LIMIT :limit;
                    """)
                    result = await session.execute(
                        query,
                        {"agent_id": agent_id, "limit": int(limit)},
                    )

                rows = result.fetchall()
                lessons = []
                for row in rows:
                    lessons.append({
                        "id": str(row.id),
                        "agent_id": row.agent_id,
                        "kind": row.kind,
                        "summary": row.summary,
                        "context": row.context,
                        "category": row.category,
                        "severity": row.severity,
                        "times_matched": row.times_matched,
                        "created_at": str(row.created_at),
                        "similarity": float(row.similarity),
                    })

                logger.info("checked_before_action", agent_id=agent_id, matches=len(lessons))
                return lessons
        except Exception as exc:  # noqa: BLE001
            logger.exception("failed_check_before_action", agent_id=agent_id, exc_info=exc)
            return []

    async def increment_match(self, lesson_id: str) -> None:
        """Increment the match count for a retrieved lesson."""
        if self._session_factory is None:
            return
        query = text("""
            UPDATE memory.lessons
            SET times_matched = times_matched + 1
            WHERE id = CAST(:lesson_id AS uuid);
        """)
        try:
            async with self._session_factory() as session:
                await session.execute(query, {"lesson_id": str(lesson_id)})
                await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.exception("failed_to_increment_match", lesson_id=lesson_id, exc_info=exc)

    async def get_agent_lessons(
        self, agent_id: str, kind: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Retrieve recent lessons for a specific agent."""
        if self._session_factory is None:
            return []
        where_clause = "agent_id = :agent_id"
        params: Dict[str, Any] = {"agent_id": agent_id, "limit": int(limit)}

        if kind:
            where_clause += " AND kind = :kind"
            params["kind"] = kind

        query = text(f"""
            SELECT id, agent_id, kind, summary, context, category, severity, times_matched, created_at
            FROM memory.lessons
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit;
        """)

        try:
            async with self._session_factory() as session:
                result = await session.execute(query, params)
                rows = result.fetchall()
                return [
                    {
                        "id": str(row.id),
                        "agent_id": row.agent_id,
                        "kind": row.kind,
                        "summary": row.summary,
                        "context": row.context,
                        "category": row.category,
                        "severity": row.severity,
                        "times_matched": row.times_matched,
                        "created_at": str(row.created_at),
                    }
                    for row in rows
                ]
        except Exception as exc:  # noqa: BLE001
            logger.exception("failed_get_agent_lessons", agent_id=agent_id, exc_info=exc)
            return []

    async def cleanup_expired(self) -> None:
        """Clean up expired lessons from the store."""
        if self._session_factory is None:
            return
        query = text("""
            DELETE FROM memory.lessons
            WHERE expires_at IS NOT NULL AND expires_at < NOW();
        """)
        try:
            async with self._session_factory() as session:
                await session.execute(query)
                await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.exception("failed_to_cleanup_expired_lessons", exc_info=exc)
