"""
SYNDIKAT Chief Operating Officer (COO) — Marshal Agent.
Commands Floor 2 Operations: Content Factory v2.0, Growth Hacking,
Affiliate Scouting, POD Studios, and Account Compliance.
Directs the autonomous media production line with zero human bottlenecks.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import structlog

from src.departments.coordinator import Floor2Coordinator

logger = structlog.get_logger(__name__)


class MarshalAgent:
    """Operational commander of Floor 2 business units and Content Factory."""

    AGENT_ID = "marshal"

    def __init__(self, memory=None, llm=None, config: Optional[Dict[str, Any]] = None):
        self._memory = memory
        self._llm = llm
        self._config = config or {}
        self.floor2 = Floor2Coordinator(config=self._config)

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch operational action to Floor 2 business units."""
        action = payload.get("action", "")
        logger.info("marshal_action_dispatched", action=action)

        # Delegate directly to Floor 2 Coordinator
        result = await self.floor2.execute(payload)

        # Record operational episode in shared memory if available
        if self._memory and hasattr(self._memory, "save_episode"):
            try:
                await self._memory.save_episode(
                    agent_id=self.AGENT_ID,
                    action=action,
                    summary=f"Marshal executed {action}",
                    data=result
                )
            except Exception as e:
                logger.warning("marshal_memory_save_failed", error=str(e))

        return result
