from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy import text

logger = structlog.get_logger(__name__)

class LessonsStore:
    """
    Syndicate-wide Lessons Layer. A shared pgvector-backed store where
    ANY agent records failures/lessons and queries before acting.
    """
    def __init__(self, session_factory: Any, redis: Optional[Any] = None) -> None:
        self._session_factory = session_factory
        self._redis = redis

    async def record_lesson(
        self,
        agent_id: str,
        kind: str,
        summary: str,
        context: Dict[str, Any],
        category: str,
        severity: str,
        embedding: List[float],
        do_not_compress: bool = False
    ) -> None:
        """Record a lesson into the shared store and optionally cache recent ones."""
        query = text("""
            INSERT INTO memory.lessons (
                agent_id, kind, summary, context, category,
                severity, embedding, do_not_compress, times_matched, created_at
            ) VALUES (
                :agent_id, :kind, :summary, :context, :category,
                :severity, :embedding, :do_not_compress, 0, NOW()
            ) RETURNING id;
        """)
        
        try:
            async with self._session_factory() as session:
                result = await session.execute(
                    query,
                    {
                        "agent_id": agent_id,
                        "kind": kind,
                        "summary": summary,
                        "context": json.dumps(context),
                        "category": category,
                        "severity": severity,
                        "embedding": str(embedding),
                        "do_not_compress": do_not_compress,
                    }
                )
                lesson_id = result.scalar_one()
                await session.commit()
                
                if self._redis:
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
        except Exception as exc: # noqa: BLE001
            logger.exception("failed_to_record_lesson", agent_id=agent_id, exc_info=exc)
            raise

    async def check_before_action(
        self,
        agent_id: str,
        action_embedding: List[float],
        limit: int = 5,
        min_similarity: float = 0.72
    ) -> List[Dict[str, Any]]:
        """
        Query lessons using pgvector cosine similarity search before an action.
        Searches across ALL agents, weighted by severity.
        """
        query = text("""
            SELECT id, agent_id, kind, summary, context, category, severity, times_matched, created_at,
                   1 - (embedding <=> :action_embedding::vector) as similarity
            FROM memory.lessons
            WHERE (1 - (embedding <=> :action_embedding::vector)) >= :min_similarity
            ORDER BY similarity DESC
            LIMIT :limit;
        """)
        
        try:
            async with self._session_factory() as session:
                result = await session.execute(
                    query,
                    {
                        "action_embedding": str(action_embedding),
                        "min_similarity": min_similarity,
                        "limit": limit
                    }
                )
                rows = result.fetchall()
                
                lessons = []
                for row in rows:
                    lessons.append({
                        "id": row.id,
                        "agent_id": row.agent_id,
                        "kind": row.kind,
                        "summary": row.summary,
                        "context": row.context if isinstance(row.context, dict) else json.loads(row.context),
                        "category": row.category,
                        "severity": row.severity,
                        "times_matched": row.times_matched,
                        "created_at": row.created_at,
                        "similarity": row.similarity
                    })
                
                logger.info("checked_before_action", agent_id=agent_id, matches=len(lessons))
                return lessons
        except Exception as exc: # noqa: BLE001
            logger.exception("failed_check_before_action", agent_id=agent_id, exc_info=exc)
            return []

    async def increment_match(self, lesson_id: int) -> None:
        """Increment the match count for a retrieved lesson."""
        query = text("""
            UPDATE memory.lessons
            SET times_matched = times_matched + 1
            WHERE id = :lesson_id;
        """)
        try:
            async with self._session_factory() as session:
                await session.execute(query, {"lesson_id": lesson_id})
                await session.commit()
            logger.info("incremented_lesson_match", lesson_id=lesson_id)
        except Exception as exc: # noqa: BLE001
            logger.exception("failed_to_increment_match", lesson_id=lesson_id, exc_info=exc)

    async def get_agent_lessons(self, agent_id: str, kind: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent lessons for a specific agent."""
        where_clause = "agent_id = :agent_id"
        params: Dict[str, Any] = {"agent_id": agent_id, "limit": limit}
        
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
                
                lessons = []
                for row in rows:
                    lessons.append({
                        "id": row.id,
                        "agent_id": row.agent_id,
                        "kind": row.kind,
                        "summary": row.summary,
                        "context": row.context if isinstance(row.context, dict) else json.loads(row.context),
                        "category": row.category,
                        "severity": row.severity,
                        "times_matched": row.times_matched,
                        "created_at": row.created_at
                    })
                
                return lessons
        except Exception as exc: # noqa: BLE001
            logger.exception("failed_get_agent_lessons", agent_id=agent_id, exc_info=exc)
            return []

    async def cleanup_expired(self) -> None:
        """Clean up expired lessons from the store."""
        query = text("""
            DELETE FROM memory.lessons
            WHERE expires_at < NOW();
        """)
        try:
            async with self._session_factory() as session:
                result = await session.execute(query)
                deleted_count = result.rowcount
                await session.commit()
            logger.info("cleaned_up_expired_lessons", deleted_count=deleted_count)
        except Exception as exc: # noqa: BLE001
            logger.exception("failed_to_cleanup_expired_lessons", exc_info=exc)
