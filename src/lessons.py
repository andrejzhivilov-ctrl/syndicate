"""
Syndicate-wide Lessons Layer (src/lessons.py).
v4.1 Verified:
- Matches `memory.lessons` column `lesson_vector`
- Uses `CAST(:embedding AS vector)` instead of `::vector`
- Gracefully falls back to non-vector query when `action_embedding` is None
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy import text

from src.embeddings import EmbeddingUnavailable

logger = structlog.get_logger(__name__)

#: Upper bound for embedding the action text before an agent answers.
ACTION_EMBED_TIMEOUT_S = 1.0
OPERATOR_CATEGORY = "operator_correction"
#: Corrections put in front of the model on every turn, so their number stays bounded.
MAX_OPERATOR_LESSONS = 10


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

    async def add_operator_lesson(self, agent_id: str, summary: str) -> Optional[str]:
        """A correction from Andrii. Applied by name, so it needs no vector and no embedding delay."""
        return await self.record_lesson(
            agent_id=agent_id, kind="lesson", summary=summary, category=OPERATOR_CATEGORY,
            embedding=[], do_not_compress=True,
        )

    async def operator_lessons(self, agent_id: str) -> Optional[List[Dict[str, str]]]:
        """Andrii's live corrections for one agent, newest first; ``None`` when unreadable."""
        if self._session_factory is None:
            return None
        query = text("""
            SELECT id, summary FROM memory.lessons
            WHERE agent_id = :agent_id AND category = :category
              AND (expires_at IS NULL OR expires_at > NOW())
            ORDER BY created_at DESC
            LIMIT :limit;
        """)
        params = {"agent_id": agent_id, "category": OPERATOR_CATEGORY, "limit": MAX_OPERATOR_LESSONS}
        try:
            async with self._session_factory() as session:
                rows = (await session.execute(query, params)).fetchall()
        except Exception as exc:  # noqa: BLE001 - a reply must not fail for its lessons
            logger.warning("operator_lessons_unavailable", agent_id=agent_id, error_type=type(exc).__name__)
            return None
        return [{"id": str(row.id), "summary": row.summary} for row in rows]

    async def retire_operator_lesson(self, agent_id: str, lesson_id: str) -> bool:
        """Expire a correction; the row stays, so nothing is finally deleted."""
        query = text("""
            UPDATE memory.lessons SET expires_at = NOW()
            WHERE id = CAST(:lesson_id AS uuid) AND agent_id = :agent_id AND category = :category;
        """)
        params = {"lesson_id": lesson_id, "agent_id": agent_id, "category": OPERATOR_CATEGORY}
        try:
            async with self._session_factory() as session:
                changed = (await session.execute(query, params)).rowcount
                await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning("operator_lesson_not_retired", agent_id=agent_id, error_type=type(exc).__name__)
            return False
        return bool(changed)

    async def _has_vectors(self) -> bool:
        """Whether any live lesson can match by vector; without one, embedding is wasted time."""
        query = text("""
            SELECT EXISTS (
                SELECT 1 FROM memory.lessons
                WHERE lesson_vector IS NOT NULL
                  AND (expires_at IS NULL OR expires_at > NOW())
            );
        """)
        try:
            async with self._session_factory() as session:
                result = await session.execute(query)
                return bool(result.scalar())
        except Exception as exc:  # noqa: BLE001 - the check below reports a database failure itself
            logger.warning("lessons_vector_probe_failed", error_type=type(exc).__name__)
            return False

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

        if action_embedding is None and action_text and await self._has_vectors():
            # A slow embedding service must not hold the agent's answer: past this
            # bound the check runs without vectors, as it does on embedding failure.
            try:
                action_embedding = await asyncio.wait_for(
                    self._embed(str(action_text), what=f"action_check:{agent_id}"), ACTION_EMBED_TIMEOUT_S
                )
            except asyncio.TimeoutError:
                logger.warning("action_check_embedding_timeout", agent_id=agent_id)
                action_embedding = None

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
