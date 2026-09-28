"""
EVA Orchestrator — LangGraph-based multi-agent coordination system.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, TypedDict

import structlog
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.base import BaseCheckpointSaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

from src.memory import MemoryManager
from src.agents.sentinel import SentinelAgent

logger = structlog.get_logger(__name__)


class AgentState(TypedDict):
    """Shared state for the EVA orchestration graph."""
    session_id: str
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    messages: List[Any]
    current_agent: Optional[str]
    result: Optional[Dict[str, Any]]
    requires_hitl: bool
    hitl_reason: Optional[str]
    error: Optional[str]
    status: str  # pending | running | awaiting_hitl | completed | failed


SYSTEM_PROMPT = """You are EVA, the central orchestrator of the EVA SYNDICATE autonomous system.
Your role is to:
1. Analyze incoming tasks and determine the appropriate specialist agent.
2. Coordinate multi-step workflows across agents.
3. Ensure all actions comply with security policies (validated by Sentinel).
4. Maintain context and continuity via the memory system.

Specialist agents available:
- Sentinel: Security validation, permission checks, threat assessment
- Doc: Document analysis, summarization, information extraction
- Fin: Financial analysis, data aggregation, reporting
- Sam: Quant trading & asset management (confluence engine, strict HITL, capital protection)
- Architect: Infrastructure/CTO, n8n workflow engineering, FlowLint QA, GitOps/ADR, code review

Always respond with structured JSON indicating routing decisions."""


class EvaOrchestrator:
    """Central orchestrator coordinating all EVA SYNDICATE agents."""

    TASK_ROUTING = {
        "analyze_document": "doc",
        "summarize": "doc",
        "financial_analysis": "fin",
        "security_check": "sentinel",
        "chat": "eva",
        "webhook_telegram": "eva",
        # Sam — quant trading & asset management
        "quant_signal": "sam",
        "evaluate_setup": "sam",
        "trade_decision": "sam",
        "portfolio_review": "sam",
        # Architect — infrastructure, n8n engineering, GitOps
        "design_workflow": "architect",
        "lint_workflow": "architect",
        "golden_template": "architect",
        "generate_adr": "architect",
        "review_code": "architect",
    }

    def __init__(
        self,
        memory_manager: MemoryManager,
        sentinel: SentinelAgent,
        llm_config: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[Any] = None,
    ) -> None:
        self._memory = memory_manager
        self._sentinel = sentinel
        self._llm_config = llm_config
        # Agent-level config (risk params, chat ids, thresholds) and the shared
        # connector registry (Telegram / Google / MCP) for agents that need them.
        self._config = dict(config or {})
        self._registry = registry
        self._llm = None
        self._graph = None

    async def initialize(self) -> None:
        """Initialize LLM and build the agent graph."""
        openai_key = self._llm_config.get("openai_api_key", "")
        if openai_key and openai_key != "PLACEHOLDER_UPDATE_ME":
            self._llm = ChatOpenAI(
                api_key=openai_key,
                model="gpt-4-turbo-preview",
                temperature=0,
            )
        else:
            logger.warning("LLM API key not configured — running in stub mode")

        if LANGGRAPH_AVAILABLE:
            self._graph = self._build_graph()

        logger.info("Orchestrator initialized", llm_ready=self._llm is not None)

    def _build_graph(self) -> Any:
        """Build the LangGraph state machine."""
        builder = StateGraph(AgentState)

        # Nodes
        builder.add_node("router", self._route_task)
        builder.add_node("eva_direct", self._eva_direct_handler)
        builder.add_node("doc_agent", self._doc_agent_handler)
        builder.add_node("fin_agent", self._fin_agent_handler)
        builder.add_node("sam_agent", self._sam_agent_handler)
        builder.add_node("architect_agent", self._architect_agent_handler)
        builder.add_node("sentinel_check", self._sentinel_check_handler)
        builder.add_node("hitl_gate", self._hitl_gate)
        builder.add_node("finalize", self._finalize)

        # Entry point
        builder.set_entry_point("router")

        # Conditional routing from router
        builder.add_conditional_edges(
            "router",
            self._select_agent,
            {
                "eva": "eva_direct",
                "doc": "doc_agent",
                "fin": "fin_agent",
                "sam": "sam_agent",
                "architect": "architect_agent",
                "sentinel": "sentinel_check",
            },
        )

        # All agents go through HITL gate before finalization
        for agent_node in [
            "eva_direct", "doc_agent", "fin_agent",
            "sam_agent", "architect_agent", "sentinel_check",
        ]:
            builder.add_edge(agent_node, "hitl_gate")

        builder.add_conditional_edges(
            "hitl_gate",
            lambda s: "finalize" if not s["requires_hitl"] else "hitl_gate",
            {"finalize": "finalize", "hitl_gate": "hitl_gate"},
        )

        builder.add_edge("finalize", END)

        return builder.compile()

    async def _route_task(self, state: AgentState) -> AgentState:
        """Analyze task and prepare routing."""
        logger.info("Routing task", task_type=state["task_type"])
        state["status"] = "running"
        state["current_agent"] = self.TASK_ROUTING.get(state["task_type"], "eva")
        return state

    def _select_agent(self, state: AgentState) -> str:
        return state.get("current_agent", "eva")

    async def _eva_direct_handler(self, state: AgentState) -> AgentState:
        """EVA handles simple orchestration tasks directly."""
        if not self._llm:
            state["result"] = {"response": "LLM not configured. Stub response.", "agent": "eva"}
            state["status"] = "completed"
            return state

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=str(state["payload"])),
        ]
        response = await self._llm.ainvoke(messages)
        state["result"] = {"response": response.content, "agent": "eva"}
        state["status"] = "completed"

        # Persist to episodic memory
        await self._memory.save_episode(
            session_id=state["session_id"],
            agent_id="eva",
            role="assistant",
            content=response.content,
        )
        return state

    async def _doc_agent_handler(self, state: AgentState) -> AgentState:
        """Delegate to Doc agent."""
        from src.agents.doc import DocAgent
        agent = DocAgent(memory=self._memory, llm=self._llm)
        result = await agent.execute(state["payload"])
        state["result"] = result
        state["status"] = "completed"
        return state

    async def _fin_agent_handler(self, state: AgentState) -> AgentState:
        """Delegate to Fin agent."""
        from src.agents.fin import FinAgent
        agent = FinAgent(memory=self._memory, llm=self._llm)
        result = await agent.execute(state["payload"])
        state["result"] = result
        state["status"] = "completed"
        return state

    async def _sam_agent_handler(self, state: AgentState) -> AgentState:
        """Delegate to Sam (quant CIO). Maps task_type → agent action."""
        from src.agents.sam import SamAgent

        agent = SamAgent(
            memory=self._memory,
            llm=self._llm,
            config=self._config.get("sam", self._config),
            registry=self._registry,
        )
        payload = dict(state["payload"])
        # Infer the Sam action from the routed task_type when not explicit.
        action_map = {
            "quant_signal": "evaluate_setup",
            "evaluate_setup": "evaluate_setup",
            "trade_decision": "decision",
            "portfolio_review": "reflect",
        }
        payload.setdefault("action", action_map.get(state["task_type"], "evaluate_setup"))
        result = await agent.execute(payload)
        state["result"] = result
        # A tradeable Sam signal is surfaced for human approval via Telegram; the
        # graph does not auto-execute — the real decision arrives as a separate
        # trade_decision task from the callback.
        if result.get("tradeable") and result.get("requires_hitl"):
            state["hitl_reason"] = "Sam quant signal requires human approval"
        state["status"] = "completed"
        return state

    async def _architect_agent_handler(self, state: AgentState) -> AgentState:
        """Delegate to the Architect (CTO / n8n engineer)."""
        from src.agents.architect import ArchitectAgent

        agent = ArchitectAgent(
            memory=self._memory,
            llm=self._llm,
            config=self._config.get("architect", self._config),
            registry=self._registry,
        )
        payload = dict(state["payload"])
        action_map = {
            "design_workflow": "design_workflow",
            "lint_workflow": "lint_workflow",
            "golden_template": "golden_template",
            "generate_adr": "adr",
            "review_code": "review_code",
        }
        payload.setdefault("action", action_map.get(state["task_type"], "capabilities"))
        result = await agent.execute(payload)
        state["result"] = result
        state["status"] = "completed"
        return state

    async def _sentinel_check_handler(self, state: AgentState) -> AgentState:
        """Run a full Sentinel security check."""
        validation = await self._sentinel.validate_task(state["payload"])
        state["result"] = {
            "allowed": validation.allowed,
            "reason": validation.reason,
            "risk_score": validation.risk_score,
        }
        state["status"] = "completed"
        return state

    async def _hitl_gate(self, state: AgentState) -> AgentState:
        """Human-in-the-loop checkpoint. Auto-approve for now; extend for real HITL."""
        if state.get("requires_hitl"):
            logger.warning("HITL required", reason=state.get("hitl_reason"))
            # In production: pause execution, notify operator, wait for approval
            # For now: auto-approve low-risk tasks
            state["requires_hitl"] = False
        return state

    async def _finalize(self, state: AgentState) -> AgentState:
        """Save checkpoint and finalize task."""
        await self._memory.save_checkpoint(
            thread_id=state["session_id"],
            checkpoint_id=state["task_id"],
            agent_id=state.get("current_agent", "eva"),
            state_data={"result": state.get("result"), "status": state["status"]},
        )
        return state

    async def execute(
        self,
        task_type: str,
        payload: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a task through the orchestration graph."""
        task_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())

        initial_state: AgentState = {
            "session_id": session_id,
            "task_id": task_id,
            "task_type": task_type,
            "payload": payload,
            "messages": [],
            "current_agent": None,
            "result": None,
            "requires_hitl": False,
            "hitl_reason": None,
            "error": None,
            "status": "pending",
        }

        if self._graph:
            final_state = await self._graph.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": session_id}},
            )
        else:
            # Fallback without LangGraph
            final_state = await self._fallback_execute(initial_state)

        return {
            "task_id": task_id,
            "status": final_state["status"],
            "result": final_state.get("result"),
        }

    async def _fallback_execute(self, state: AgentState) -> AgentState:
        """Minimal fallback when LangGraph is unavailable."""
        state["result"] = {"response": "Processed via fallback (LangGraph unavailable)"}
        state["status"] = "completed"
        return state

    async def handle_webhook(self, source: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhooks from external systems."""
        task_type = f"webhook_{source}"
        result = await self.execute(task_type=task_type, payload=payload)
        return result
