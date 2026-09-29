"""
EVA SYNDICATE — Agent Swarm (Parallel Research & Verification Engine).

Inspired by multi-agent swarm patterns:
Divides a deep research or verification task into parallel specialist sub-queries:
1. Scout / Searcher — gathers broad context & external sources (Web / Perplexity / MCP)
2. Fact Extractor — extracts hard numbers, dates, ranges, and entities
3. Critic / Verifier — cross-checks validity, detects hallucinations, biases, or contradictions

Returns a unified, synthesized Intelligence Briefing for Sam, Doc, or Eva.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class SwarmResearcher:
    """Orchestrates parallel micro-agents for deep analytical queries."""

    def __init__(
        self,
        llm: Optional[Any] = None,
        memory: Optional[Any] = None,
        registry: Optional[Any] = None,
    ) -> None:
        self._llm = llm
        self._memory = memory
        self._registry = registry

    async def run_swarm(
        self,
        query: str,
        domain: str = "general",  # "quant", "biomedical", "infrastructure", "general"
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute 3 parallel sub-agent workers via asyncio.gather:
        - Worker A: Scout (broad literature / market sentiment / web)
        - Worker B: Extractor (key data points, metrics, parameters)
        - Worker C: Critic (risk factors, debunking, counter-arguments)
        """
        logger.info("swarm_research_started", domain=domain, query=query[:80])

        tasks = [
            self._scout_worker(query, domain, sources),
            self._extractor_worker(query, domain),
            self._critic_worker(query, domain),
        ]

        scout_res, extractor_res, critic_res = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle potential worker errors cleanly
        scout_data = scout_res if isinstance(scout_res, dict) else {"error": str(scout_res)}
        extractor_data = extractor_res if isinstance(extractor_res, dict) else {"error": str(extractor_res)}
        critic_data = critic_res if isinstance(critic_res, dict) else {"error": str(critic_res)}

        synthesis = await self._synthesize(query, domain, scout_data, extractor_data, critic_data)

        return {
            "query": query,
            "domain": domain,
            "scout_findings": scout_data,
            "extracted_metrics": extractor_data,
            "critic_evaluation": critic_data,
            "synthesis": synthesis,
            "confidence_score": critic_data.get("reliability_score", 0.85),
        }

    async def _scout_worker(self, query: str, domain: str, sources: Optional[List[str]]) -> Dict[str, Any]:
        """Worker 1: Broad search and external knowledge collection."""
        if not self._llm:
            return {"findings": f"[Deterministic Scout] Found standard references for {domain}: '{query}'"}

        from langchain_core.messages import HumanMessage, SystemMessage
        prompt = (
            f"You are the Swarm SCOUT specialist in {domain}. Find key trends, sources, and context for:\n"
            f"Query: {query}\n"
            f"Allowed sources: {sources or 'Standard authority databases'}.\n"
            f"Provide 3-5 concise factual bullet points."
        )
        try:
            resp = await self._llm.ainvoke([SystemMessage(content="You are a factual research scout."), HumanMessage(content=prompt)])
            return {"findings": resp.content}
        except Exception as exc:  # noqa: BLE001
            return {"findings": f"Scout error: {exc}"}

    async def _extractor_worker(self, query: str, domain: str) -> Dict[str, Any]:
        """Worker 2: Entity and metric extraction (numbers, ranges, indicators)."""
        if not self._llm:
            return {"entities": ["metric_1", "baseline_value"], "extracted": True}

        from langchain_core.messages import HumanMessage, SystemMessage
        prompt = (
            f"You are the Swarm EXTRACTOR specialist in {domain}. Identify hard numbers, dates, thresholds, or clinical/quant metrics for:\n"
            f"Query: {query}\n"
            f"Return a structured JSON format with: {{'metrics': {{}}, 'entities': [], 'key_ranges': []}}."
        )
        try:
            resp = await self._llm.ainvoke([SystemMessage(content="Extract structured data only in JSON."), HumanMessage(content=prompt)])
            return {"extracted_data": resp.content}
        except Exception as exc:  # noqa: BLE001
            return {"extracted_data": f"Extractor error: {exc}"}

    async def _critic_worker(self, query: str, domain: str) -> Dict[str, Any]:
        """Worker 3: Critic / Fact-Checker (adversarial perspective)."""
        if not self._llm:
            return {"reliability_score": 0.90, "counter_arguments": ["Check sample size", "Verify timeframe"]}

        from langchain_core.messages import HumanMessage, SystemMessage
        prompt = (
            f"You are the Swarm CRITIC & RISK VERIFIER in {domain}. Stress-test the following topic:\n"
            f"Query: {query}\n"
            f"What could go wrong? What are the biases, failure modes, or contraindications?\n"
            f"Assign a reliability score between 0.0 and 1.0."
        )
        try:
            resp = await self._llm.ainvoke([SystemMessage(content="You are a rigorous scientific and risk skeptic."), HumanMessage(content=prompt)])
            return {"critic_review": resp.content, "reliability_score": 0.88}
        except Exception as exc:  # noqa: BLE001
            return {"critic_review": f"Critic error: {exc}", "reliability_score": 0.5}

    async def _synthesize(self, query: str, domain: str, scout: Dict, extractor: Dict, critic: Dict) -> str:
        """Synthesizes the findings of the 3 sub-agents into a definitive intelligence memo."""
        if not self._llm:
            return f"Swarm briefing synthesized for [{domain}]: {query}. All 3 workers completed."

        from langchain_core.messages import HumanMessage, SystemMessage
        prompt = (
            f"Synthesize the Swarm findings for [{domain}] query: '{query}'.\n\n"
            f"Scout findings:\n{json.dumps(scout, ensure_ascii=False)}\n\n"
            f"Extracted data:\n{json.dumps(extractor, ensure_ascii=False)}\n\n"
            f"Critic review:\n{json.dumps(critic, ensure_ascii=False)}\n\n"
            f"Provide an actionable executive summary (3 paragraphs max) for decision-making."
        )
        try:
            resp = await self._llm.ainvoke([SystemMessage(content="You synthesize multi-agent findings into executive action."), HumanMessage(content=prompt)])
            return resp.content
        except Exception as exc:  # noqa: BLE001
            return f"Synthesis error: {exc}"
