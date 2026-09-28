"""Fin Agent — Financial analysis, data aggregation, reporting."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import structlog
from src.memory import MemoryManager

logger = structlog.get_logger(__name__)


class FinAgent:
    """Financial analysis specialist agent."""
    AGENT_ID = "fin"

    def __init__(self, memory: MemoryManager, llm: Optional[Any] = None) -> None:
        self._memory = memory
        self._llm = llm

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "analyze")
        data = payload.get("data", {})

        if action == "analyze":
            return await self._analyze(data)
        elif action == "report":
            return await self._generate_report(data)
        else:
            return {"error": f"Unknown action: {action}", "agent": self.AGENT_ID}

    async def _analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not self._llm:
            return {
                "analysis": "Stub analysis — LLM not configured",
                "metrics": {},
                "agent": self.AGENT_ID,
            }
        from langchain_core.messages import HumanMessage
        response = await self._llm.ainvoke([
            HumanMessage(content=f"Analyze the following financial data and provide key metrics:\n{data}")
        ])
        return {"analysis": response.content, "agent": self.AGENT_ID}

    async def _generate_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"report": "Financial report generation not yet implemented", "agent": self.AGENT_ID}
