"""
EVA Orchestrator — LangGraph-based multi-agent coordination system.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, TypedDict

import structlog
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.lessons import LessonsStore
from src.confidence import ConfidenceBudget, EscalationLevel
from src.pii import PIIRedactor

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
        # Eva Curator
        "weekly_review": "eva_curator",
        "record_decision": "eva_curator",
        "deadline_check": "eva_curator",
        "social_pulse": "eva_curator",
        # Doc full
        "morning_readiness": "doc",
        "training_protocol": "doc",
        "nutrition_plan": "doc",
        "biomarker_trend": "doc",
        "screening_calendar": "doc",
        "emergency_card": "doc",
        "compliance_check": "doc",
        "nervous_system": "doc",
        "swarm_research_doc": "doc",
        # Sam & Architect additions
        "swarm_research_sam": "sam",
        "portfolio_risk": "sam",
        "generate_ui_scaffold": "architect",
        "gitops_sync": "architect",
        "drift_detect": "architect",
        "verify_code": "architect",
        "self_healing_generate": "architect",
    }

    def __init__(
        self,
        memory_manager: MemoryManager,
        sentinel: SentinelAgent,
        llm_config: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[Any] = None,
        voice_manager: Optional[Any] = None,
        lessons_store: Optional[LessonsStore] = None,
        confidence_budget: Optional[ConfidenceBudget] = None,
        pii_redactor: Optional[PIIRedactor] = None,
    ) -> None:
        self._memory = memory_manager
        self._sentinel = sentinel
        self._llm_config = llm_config
        # Agent-level config (risk params, chat ids, thresholds) and the shared
        # connector registry (Telegram / Google / MCP) for agents that need them.
        self._config = dict(config or {})
        self._registry = registry
        # Provider-agnostic voice subsystem (TTS/STT with fallback chains).
        # Exposed to agents (e.g. Eva voice briefings) via self._voice.
        self._voice = voice_manager
        self._lessons = lessons_store
        self._confidence = confidence_budget
        self._pii = pii_redactor
        self._llm = None
        self._llm_fast = None
        self._llm_reasoning = None
        self._graph = None

    async def initialize(self) -> None:
        """Initialize tiered LLMs (Claude 3.5 Sonnet + OpenAI fast tier + Reasoning tier for Architect) and build the agent graph."""
        anthropic_key = self._llm_config.get("anthropic_api_key", "")
        openai_key = self._llm_config.get("openai_api_key", "")
        reasoning_model = self._llm_config.get("reasoning_model", "o3-mini")

        if anthropic_key and anthropic_key != "PLACEHOLDER_UPDATE_ME":
            try:
                from langchain_anthropic import ChatAnthropic
                self._llm = ChatAnthropic(
                    api_key=anthropic_key,
                    model="claude-3-5-sonnet-20241022",
                    temperature=0,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to initialize ChatAnthropic", error=str(exc))

        if openai_key and openai_key != "PLACEHOLDER_UPDATE_ME":
            fast_llm = ChatOpenAI(
                api_key=openai_key,
                model="gpt-4o-mini",
                temperature=0,
            )
            self._llm_fast = fast_llm
            try:
                self._llm_reasoning = ChatOpenAI(
                    api_key=openai_key,
                    model=reasoning_model,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to initialize reasoning LLM, falling back to primary LLM", error=str(exc))
            if self._llm is None:
                self._llm = ChatOpenAI(
                    api_key=openai_key,
                    model="gpt-4o",
                    temperature=0,
                )

        if self._llm_reasoning is None and self._llm is not None:
            self._llm_reasoning = self._llm

        if self._llm is None:
            logger.warning("LLM API keys not configured — running in deterministic/stub mode")

        if LANGGRAPH_AVAILABLE:
            self._graph = self._build_graph()

        logger.info(
            "Orchestrator initialized",
            llm_ready=self._llm is not None,
            fast_llm_ready=self._llm_fast is not None,
            reasoning_llm_ready=self._llm_reasoning is not None,
        )

    def _build_graph(self) -> Any:
        """Build the LangGraph state machine."""
        builder = StateGraph(AgentState)

        # Nodes
        builder.add_node("router", self._route_task)
        builder.add_node("lessons_check", self._lessons_check)
        builder.add_node("eva_direct", self._eva_direct_handler)
        builder.add_node("doc_agent", self._doc_agent_handler)
        builder.add_node("fin_agent", self._fin_agent_handler)
        builder.add_node("sam_agent", self._sam_agent_handler)
        builder.add_node("architect_agent", self._architect_agent_handler)
        builder.add_node("sentinel_check", self._sentinel_check_handler)
        builder.add_node("eva_curator", self._eva_curator_handler)
        builder.add_node("confidence_gate", self._confidence_gate)
        builder.add_node("outbound_veto", self._outbound_veto)
        builder.add_node("hitl_gate", self._hitl_gate)
        builder.add_node("finalize", self._finalize)

        # Entry point
        builder.set_entry_point("router")

        # Router to lessons_check
        builder.add_edge("router", "lessons_check")

        # Conditional routing from lessons_check
        builder.add_conditional_edges(
            "lessons_check",
            self._select_agent,
            {
                "eva": "eva_direct",
                "doc": "doc_agent",
                "fin": "fin_agent",
                "sam": "sam_agent",
                "architect": "architect_agent",
                "sentinel": "sentinel_check",
                "eva_curator": "eva_curator",
            },
        )

        # All agents go through confidence gate
        for agent_node in [
            "eva_direct", "doc_agent", "fin_agent",
            "sam_agent", "architect_agent", "sentinel_check", "eva_curator",
        ]:
            builder.add_edge(agent_node, "confidence_gate")

        builder.add_edge("confidence_gate", "outbound_veto")
        builder.add_edge("outbound_veto", "hitl_gate")
        
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

    async def _lessons_check(self, state: AgentState) -> AgentState:
        if self._lessons:
            lessons = await self._lessons.check_before_action(
                agent_id=state.get('current_agent', 'eva'),
                action_embedding=None,  # embedding computed if available
            )
            if lessons:
                state['payload']['prior_lessons'] = lessons
        return state

    async def _confidence_gate(self, state: AgentState) -> AgentState:
        if self._confidence and state.get('result'):
            confidence = state['result'].get('confidence', 0.90)
            action_risk = state['result'].get('action_risk', 'low')
            escalation = self._confidence.evaluate(
                agent_id=state.get('current_agent', 'eva'),
                confidence=confidence,
                action_type=state.get('task_type', 'unknown'),
                action_risk=action_risk,
            )
            if escalation.level == EscalationLevel.REFUSE:
                state['result']['refused'] = True
                state['result']['refuse_reason'] = escalation.reason
            elif escalation.level == EscalationLevel.ASK:
                state['requires_hitl'] = True
                state['hitl_reason'] = f'Confidence gate: {escalation.reason}'
        return state

    async def _outbound_veto(self, state: AgentState) -> AgentState:
        if state.get('result', {}).get('outbound_actions'):
            blocked = []
            for action in state['result']['outbound_actions']:
                veto = await self._sentinel.veto_outbound_action(state.get('current_agent', 'eva'), action)
                if not veto.allowed:
                    blocked.append({**action, 'veto_reason': veto.reason})
            if blocked:
                state['result']['blocked_actions'] = blocked
        return state

    async def _eva_curator_handler(self, state: AgentState) -> AgentState:
        from src.agents.eva_curator import EvaCurator
        agent = EvaCurator(memory=self._memory, llm=self._llm, config=self._config)
        result = await agent.execute(state['payload'])
        state['result'] = result
        state['status'] = 'completed'
        return state

    async def _eva_direct_handler(self, state: AgentState) -> AgentState:
        """EVA handles simple orchestration tasks directly."""
        if not self._llm:
            state["result"] = {"response": "LLM not configured. Stub response.", "agent": "eva"}
            state["status"] = "completed"
            return state
            
        if self._pii:
            payload_text, _ = self._pii.redact(str(state['payload']))
        else:
            payload_text = str(state['payload'])

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=payload_text),
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
            "portfolio_risk": "portfolio_risk",
            "swarm_research_sam": "swarm_research",
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
        """Delegate to the Architect (CTO / n8n engineer) using dedicated Reasoning LLM tier."""
        from src.agents.architect import ArchitectAgent

        agent = ArchitectAgent(
            memory=self._memory,
            llm=self._llm_reasoning or self._llm,
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
            "generate_ui_scaffold": "generate_ui_scaffold",
            "gitops_sync": "gitops_sync",
            "drift_detect": "drift_detect",
            "verify_code": "verify_code",
            "self_healing_generate": "self_healing_generate",
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

    async def proactive_daily_briefing(self) -> Dict:
        """Called by n8n cron at 07:00. Gathers data from all agents."""
        results = {}
        for agent_id, port in [('eva', 8001), ('fin', 8004), ('sam', 8006), ('doc', 8005), ('marshal', 8002)]:
            try:
                r = await self.execute('morning_data_' + agent_id, {'action': 'morning_data'})
                results[agent_id] = r.get('result', {})
            except Exception:
                results[agent_id] = {'error': 'unavailable'}
        # Compose briefing via Eva
        briefing = await self.execute('compose_briefing', {'agent_data': results})
        # Voice briefing if voice manager available
        if self._voice and briefing.get('result', {}).get('response'):
            await self._voice.speak(briefing['result']['response'])
        return briefing
