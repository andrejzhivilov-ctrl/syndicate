"""Doc Agent — Document analysis, summarization, information extraction."""

from __future__ import annotations
from typing import Any, Dict, Optional
import structlog
from src.memory import MemoryManager

logger = structlog.get_logger(__name__)


class DocAgent:
    """Document processing specialist agent."""
    AGENT_ID = "doc"

    def __init__(self, memory: MemoryManager, llm: Optional[Any] = None) -> None:
        self._memory = memory
        self._llm = llm

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "summarize")
        content = payload.get("content", "")

        if not content:
            return {"error": "No content provided", "agent": self.AGENT_ID}

        if action == "summarize":
            return await self._summarize(content)
        elif action == "extract":
            return await self._extract(content, payload.get("fields", []))
        else:
            return {"error": f"Unknown action: {action}", "agent": self.AGENT_ID}

    async def _summarize(self, content: str) -> Dict[str, Any]:
        if not self._llm:
            return {"summary": f"[Stub] Content received ({len(content)} chars)", "agent": self.AGENT_ID}

        from langchain_core.messages import HumanMessage
        response = await self._llm.ainvoke([
            HumanMessage(content=f"Summarize the following document concisely:\n\n{content[:4000]}")
        ])
        return {"summary": response.content, "agent": self.AGENT_ID}

    async def _extract(self, content: str, fields: list) -> Dict[str, Any]:
        if not self._llm or not fields:
            return {"extracted": {f: None for f in fields}, "agent": self.AGENT_ID}

        from langchain_core.messages import HumanMessage
        prompt = f"Extract the following fields from the document: {fields}\n\nDocument:\n{content[:4000]}\n\nRespond with JSON only."
        response = await self._llm.ainvoke([HumanMessage(content=prompt)])
        return {"extracted": response.content, "agent": self.AGENT_ID}
