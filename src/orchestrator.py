"""
EVA Orchestrator — LangGraph-based multi-agent coordination system.
SYNDICATE ROUND TABLE & NEURAL CORE:
- Central Neural Core: Eva Orchestrator, Shared Memory (pgvector), Vault Keyring, Confidence Gate, Outbound Veto
- Directorial Round Table (Radial Peer-to-Peer Network):
  * Command & Strategy: Eva (Chief of Staff), LLM Council, OrcVerifier, ChangeRequests
  * Systems & Engineering: Architect (CTO), Alice (SDK Integration), Antigravity Bridge
  * Security & Compliance: Marshal (CSO), Sentinel Zero-Trust Protocol
  * Capital & Governance: Fin (CFO), Monobank sync, Runway, Basket fund approvals
  * Quant & Markets: Sam (Director of Trading & Confluence Engine)
  * Clinical Medicine: Doc (Chief Medical Officer, biomarkers, clinical screenings)
  * Physical Performance & Lifestyle: Trainer (Workouts, Mifflin-St Jeor TDEE, meal plans, habits)
  * Academy & Synthesis: Kira (Dean of Academy, Socratic Tutor, Micro-quizzes)
  * Media & Creative Operations: Oscar (Creative Director, viral video, release packs)
  * Operations & Commerce: Tyler (Director of Operations, supplier check, price comparisons)
  * Quant Probabilities: Jack (Kelly criterion, anti-tilt, probabilistic modeling)
  * Knowledge & Archive: Kodex (Archivist, Obsidian, NotebookLM)
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

import structlog

from src.llm_router import TieredLLM
from src.vault_paths import secret_path
from src.model_registry import model_for
from langchain_openai import ChatOpenAI

from src.lessons import LessonsStore
from src.confidence import ConfidenceBudget, EscalationLevel
from src.pii import PIIRedactor
from src.memory import MemoryManager
from src.agents.sentinel import SentinelAgent
from src.floors import FLOORS, active_floors, reserved_floors
from src.sensory import SensoryRouter
from src.error_collector import ErrorCollector
from src.vault_md import MarkdownVault, VaultError
from src.council import LLMCouncil
from src.verifier import OrcVerifier
from src.change_requests import ChangeRequestError, ChangeRequestStore
from src.hitl_queue import HitlQueue
from src.skill_store import SkillStore
from src.tool_contracts import ToolRegistry
from src.memory_commands import parse_command, execute_command
from src.agents.kira_socratic import SocraticTutor
from src.departments.content_factory.humanizer import Humanizer
from src.departments.content_factory.video_prompt_enhancer import VideoPromptEnhancer
from src.departments.content_factory.release_pack import ReleasePackBuilder
from src.proactive import ProactiveScheduler

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

logger = structlog.get_logger(__name__)

#: Per-call wait for a routed model before failing over (seconds).
ROUTED_TIMEOUT_S = 60
#: Deep-research models run many searches per call.
DEEP_RESEARCH_TIMEOUT_S = 600

# Task types that only a verified human operator may trigger. They are refused
# on the generic /execute surface and re-checked inside the CR handler.
OPERATOR_ONLY_TASK_TYPES = frozenset({"review_change_request", "apply_change_request"})
# The reviewer identity recorded for operator decisions. It is a constant, not
# a payload field: a caller must not be able to pick who "approved" a change.
OPERATOR_IDENTITY = "operator"


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
    # True only when the HTTP layer authenticated an operator (HITL scope or
    # master key) for this exact call. Never derived from the payload.
    operator_verified: bool


SYSTEM_PROMPT = (Path(__file__).with_name("agents") / "eva_runtime_prompt.md").read_text(encoding="utf-8")


class EvaOrchestrator:
    """Central orchestrator coordinating all 10 floors of SYNDICATE."""

    TASK_ROUTING = {
        "oscar_task": "oscar",
        "tyler_task": "tyler",
        "jack_task": "jack",
        "scout_task": "scout",
        "dex_task": "dex",
        "ray_task": "ray",
        "atlas_task": "atlas",
        "sonar_task": "sonar",
        "deep_research": "sonar",
        "verify_sources": "sonar",
        "compare_entities": "sonar",
        "crawl_markdown": "sonar",
        "alice_engineer": "alice",
        "alice_code_review": "alice",
        "alice_status": "alice",
        # ─── Floor 1: Server & n8n ──────────────────────────────────────────
        "sensory_split_audio": "sensory",
        "sensory_extract_doc": "sensory",
        "sensory_chunk_text": "sensory",
        "sensory_route_telegram": "sensory",
        "record_error": "error_collector",
        "get_recent_errors": "error_collector",
        "generate_n8n_template": "n8n_templates",
        "proactive_morning": "proactive",
        "proactive_evening": "proactive",

        # ─── Floor 2: Content Factory & Operations ──────────────────────────
        "render_short_video": "floor2",
        "create_viral_short": "floor2",
        "direct_short_script": "floor2",
        "source_broll_batch": "floor2",
        "generate_karaoke_captions": "floor2",
        "publish_content_campaign": "floor2",
        "generate_viral_thread": "floor2",
        "generate_pod_mockup": "floor2",
        "scout_affiliate_offers": "floor2",
        "analyze_pod_trends": "floor2",
        "aggregate_growth_metrics": "floor2",
        "setup_antidetect_profile": "floor2",
        "humanize_text": "floor2_enhancer",
        "enhance_video_prompt": "floor2_enhancer",
        "build_release_pack": "floor2_enhancer",

        # ─── Floors 3-6: Reserved ───────────────────────────────────────────
        "floor3_query": "reserved_floor",
        "floor4_query": "reserved_floor",
        "floor5_query": "reserved_floor",
        "floor6_query": "reserved_floor",

        # ─── Floor 7: Quant & Capital (Sam) ─────────────────────────────────
        "quant_signal": "sam",
        "evaluate_setup": "sam",
        "trade_decision": "sam",
        "portfolio_review": "sam",
        "portfolio_risk": "sam",
        "swarm_research_sam": "sam",
        "morning_data_sam": "sam",

        # ─── Floor 8: SYNDICATE Academy (Kira) ──────────────────────────────
        "socratic_dialogue": "kira",
        "lesson_plan": "kira",
        "mentor_code_review": "kira",
        "language_practice": "kira",
        "history_synthesis": "kira",
        "vibecoding_session": "kira",
        "micro_quiz": "kira",
        "academy_overview": "kira",
        "morning_data_kira": "kira",
        "micro_quiz_answer": "kira",
        "learning_status": "kira",
        "propose_learning": "kira",
        "decide_proposal": "kira",
        "kira_socratic_next": "kira_socratic",
        "kira_socratic_solve": "kira_socratic",

        # ─── Floor 9: Health & Energy (Doc & Trainer) ─────────────────────────────────
        # Doc (Strictly Clinical Health & Medical Intelligence)
        "analyze_document": "doc",
        "summarize": "doc",
        "morning_readiness": "doc",
        "biomarker_trend": "doc",
        "screening_calendar": "doc",
        "emergency_card": "doc",
        "compliance_check": "doc",
        "nervous_system": "doc",
        "swarm_research_doc": "doc",
        "morning_data_doc": "doc",

        # Trainer (Physical Performance, Workouts, Sports Nutrition, Self-Improvement)
        "training_protocol": "trainer",
        "workout_plan": "trainer",
        "exercise_search": "trainer",
        "nutrition_plan": "trainer",
        "recipe_plan": "trainer",
        "shopping_list": "trainer",
        "supplement_protocol": "trainer",
        "habit_tracker": "trainer",
        "active_recovery": "trainer",
        "swarm_research_trainer": "trainer",
        "morning_data_trainer": "trainer",

        # ─── Floor 10: Command Floor (Eva, Fin, Marshal, Architect, Services) ─
        # Eva & Curators
        "chat": "eva",
        "webhook_telegram": "eva",
        "webhook_telegram_eva": "eva",
        "webhook_telegram_alice": "alice",
        "webhook_telegram_sonar": "sonar",
        "webhook_telegram_architect": "architect",
        "webhook_telegram_kodex": "kodex",
        "webhook_telegram_marshal": "marshal",
        "webhook_telegram_fin": "fin",
        "webhook_telegram_sam": "sam",
        "webhook_telegram_jack": "jack",
        "webhook_telegram_scout": "scout",
        "webhook_telegram_oscar": "oscar",
        "webhook_telegram_tyler": "tyler",
        "webhook_telegram_ray": "ray",
        "webhook_telegram_dex": "dex",
        "webhook_telegram_doc": "doc",
        "webhook_telegram_trainer": "trainer",
        "webhook_telegram_kira": "kira",
        "webhook_telegram_atlas": "atlas",
        "weekly_review": "eva_curator",
        "record_decision": "eva_curator",
        "deadline_check": "eva_curator",
        "social_pulse": "eva_curator",
        "morning_data_eva": "eva_curator",
        # Office Copilot
        "office_lookup": "eva_office",
        "generate_macro": "eva_office",
        "create_excel_report": "eva_office",
        "create_word_document": "eva_office",
        # Fin (CFO)
        "financial_analysis": "fin",
        "fin_runway": "fin",
        "fin_budget_check": "fin",
        "fin_tax_radar": "fin",
        "fin_sync_bank": "fin",
        "morning_data_fin": "fin",
        "fin_report": "fin",
        "eva_basket_ready": "fin",   # автоматичний виклик Єви (funds_check)
        "fin_funds_check": "fin",    # прямий запит Андрія
        # Marshal (CSO - Chief Security Officer commanding Sentinel Protocol)
        "marshal_execute": "marshal",
        "morning_data_marshal": "marshal",
        "security_audit": "marshal",
        "security_status": "marshal",
        "incident_report": "marshal",
        "emergency_lockdown": "marshal",
        # Architect (CTO)
        "design_workflow": "architect",
        "lint_workflow": "architect",
        "golden_template": "architect",
        "generate_adr": "architect",
        "review_code": "architect",
        "generate_ui_scaffold": "architect",
        "gitops_sync": "architect",
        "drift_detect": "architect",
        "verify_code": "architect",
        "self_healing_generate": "architect",
        "morning_data_architect": "architect",
        # Floor 10 Security & Governance Services
        "security_check": "sentinel",
        "sentinel_command_safety": "sentinel",
        "sentinel_lethal_trifecta": "sentinel",
        "sentinel_slopsquatting": "sentinel",
        "sentinel_scan_secrets": "sentinel",
        "council_deliberate": "council",
        "orc_verify": "orc_verifier",
        "submit_change_request": "change_requests",
        "review_change_request": "change_requests",
        "apply_change_request": "change_requests",
        "parse_memory_command": "memory_command",
        "vault_write_ground_truth": "vault",
        "vault_read_ground_truth": "vault",
        "vault_reindex": "vault",
        "floors_overview": "floor_registry",
        # Kodex (Chief Archivist — NotebookLM & Obsidian Second Brain)
        "kodex_ingest_notebook": "kodex",
        "kodex_export_obsidian": "kodex",
        "kodex_dispatch_task": "kodex",
        "kodex_triage_tasks": "kodex",
        "kodex_storage_stats": "kodex",
        # Antigravity (External 24/7 VM Super-Agent Contractor Gateway)
        "antigravity_contractor_dispatch": "antigravity_gateway",
        "antigravity_contractor_compact": "antigravity_gateway",
        "antigravity_contractor_status": "antigravity_gateway",
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
        markdown_vault: Optional[MarkdownVault] = None,
        error_collector: Optional[ErrorCollector] = None,
        tool_registry: Optional[ToolRegistry] = None,
        council: Optional[LLMCouncil] = None,
        orc_verifier: Optional[OrcVerifier] = None,
        socratic_tutor: Optional[SocraticTutor] = None,
        sensory_router: Optional[SensoryRouter] = None,
        change_requests: Optional[ChangeRequestStore] = None,
        humanizer: Optional[Humanizer] = None,
        video_prompt_enhancer: Optional[VideoPromptEnhancer] = None,
        release_pack_builder: Optional[ReleasePackBuilder] = None,
        director_clients: Optional[Dict[str, Any]] = None,
        vault_client: Optional[Any] = None,
        hitl_queue: Optional[HitlQueue] = None,
    ) -> None:
        self._hitl_queue = hitl_queue or HitlQueue()
        self._memory = memory_manager
        self._sentinel = sentinel
        self._llm_config = dict(llm_config or {})
        self._config = dict(config or {})
        self._director_clients = dict(director_clients or {})
        self._vault_client = vault_client
        self._registry = registry
        self._voice = voice_manager
        self._lessons = lessons_store
        self._confidence = confidence_budget
        self._pii = pii_redactor

        # ─── 10-Floor Integrated Subsystems ─────────────────────────────────
        # ``None`` lets MarkdownVault fall back to EVA_DATA_DIR-aware resolution;
        # hardcoding "vault_md" here made the read-only container fail to boot.
        vault_root = self._config.get("vault_root")
        self._vault = markdown_vault or MarkdownVault(vault_root=vault_root)
        self._skill_store = SkillStore(vault=self._vault)
        self._error_collector = error_collector or ErrorCollector(lessons_store=self._lessons)
        self._tool_registry = tool_registry or ToolRegistry()
        self._sensory = sensory_router or SensoryRouter()
        self._socratic_tutor = socratic_tutor or SocraticTutor()
        self._humanizer = humanizer or Humanizer()
        self._video_enhancer = video_prompt_enhancer or VideoPromptEnhancer()
        self._change_requests = change_requests or ChangeRequestStore(vault=self._vault)
        self._proactive_scheduler = ProactiveScheduler()

        self._llm = None
        self._llm_fast = None
        self._llm_reasoning = None
        self._graph = None

        # These will be initialized or wired with LLM in initialize()
        self._council = council
        self._orc_verifier = orc_verifier
        self._release_pack = release_pack_builder

    def _init_llms(self) -> None:
        """Tiered LLM setup supporting OpenRouter, Gemini, Anthropic, and OpenAI."""
        anthropic_key = self._llm_config.get("anthropic_api_key") or self._llm_config.get("anthropic", "")
        openai_key = self._llm_config.get("openai_api_key") or self._llm_config.get("openai", "")
        openrouter_key = self._llm_config.get("openrouter_api_key") or self._llm_config.get("openrouter", "")
        gemini_key = (
            self._llm_config.get("gemini_api_key")
            or self._llm_config.get("gemini", "")
            or self._llm_config.get("google_api_key", "")
            or self._llm_config.get("google", "")
        )
        reasoning_model = self._llm_config.get("reasoning_model", "o3-mini")
        self._provider_keys = {
            name: key for name, key in (
                ("anthropic", anthropic_key), ("openrouter", openrouter_key), ("gemini", gemini_key),
            ) if key and key != "PLACEHOLDER_UPDATE_ME"
        }

        # 1. Primary LLM: Anthropic -> OpenRouter (Claude) -> Gemini Pro -> OpenAI (gpt-4o).
        # Model IDs come from the registry: hard-coded IDs here went stale and
        # every primary call failed while startup still logged success.
        if anthropic_key and anthropic_key != "PLACEHOLDER_UPDATE_ME":
            try:
                from langchain_anthropic import ChatAnthropic
                # No temperature: current Claude models reject it with HTTP 400
                # ("`temperature` is deprecated for this model").
                self._llm = ChatAnthropic(
                    api_key=anthropic_key,
                    model=model_for("ANTHROPIC_PRIMARY"),
                    timeout=ROUTED_TIMEOUT_S,
                    max_retries=1,
                )
                logger.info("Initialized primary LLM via Direct Anthropic", model=model_for("ANTHROPIC_PRIMARY"))
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to initialize ChatAnthropic", error=str(exc))

        if self._llm is None and openrouter_key and openrouter_key != "PLACEHOLDER_UPDATE_ME":
            try:
                openrouter_model = self._llm_config.get("openrouter_model") or model_for("OPENROUTER_DIRECTOR")
                self._llm = ChatOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=openrouter_key,
                    model=openrouter_model,
                    temperature=0,
                    default_headers={
                        "HTTP-Referer": "https://syndicateholding.com",
                        "X-Title": "SYNDICATE Holding",
                    },
                )
                logger.info("Initialized primary LLM via OpenRouter", model=openrouter_model)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to initialize OpenRouter primary LLM", error=str(exc))

        if self._llm is None and gemini_key and gemini_key != "PLACEHOLDER_UPDATE_ME":
            try:
                self._llm = ChatOpenAI(
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                    api_key=gemini_key,
                    model=model_for("GEMINI_PRO"),
                    temperature=0,
                )
                logger.info("Initialized primary LLM via Gemini Pro")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to initialize Gemini Pro primary LLM", error=str(exc))

        if self._llm is None and openai_key and openai_key != "PLACEHOLDER_UPDATE_ME":
            try:
                self._llm = ChatOpenAI(
                    api_key=openai_key,
                    model=model_for("OPENAI_PRIMARY"),
                    temperature=0,
                )
                logger.info("Initialized primary LLM via OpenAI")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to initialize OpenAI primary LLM", error=str(exc))

        # 2. Fast LLM: Gemini Flash -> OpenRouter Gemini Flash -> OpenAI gpt-4o-mini
        if gemini_key and gemini_key != "PLACEHOLDER_UPDATE_ME":
            try:
                self._llm_fast = ChatOpenAI(
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                    api_key=gemini_key,
                    model=model_for("GEMINI_FAST"),
                    temperature=0,
                )
                logger.info("Initialized fast LLM via Gemini Flash")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to initialize Gemini Flash fast LLM", error=str(exc))

        if self._llm_fast is None and openrouter_key and openrouter_key != "PLACEHOLDER_UPDATE_ME":
            try:
                self._llm_fast = ChatOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=openrouter_key,
                    model=model_for("OPENROUTER_FAST"),
                    temperature=0,
                    default_headers={
                        "HTTP-Referer": "https://syndicateholding.com",
                        "X-Title": "SYNDICATE Holding",
                    },
                )
                logger.info("Initialized fast LLM via OpenRouter Gemini Flash")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to initialize OpenRouter fast LLM", error=str(exc))

        if self._llm_fast is None and openai_key and openai_key != "PLACEHOLDER_UPDATE_ME":
            try:
                self._llm_fast = ChatOpenAI(
                    api_key=openai_key,
                    model="gpt-4o-mini",
                    temperature=0,
                )
                logger.info("Initialized fast LLM via OpenAI")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to initialize OpenAI fast LLM", error=str(exc))

        # 3. Reasoning LLM: OpenRouter (deepseek-r1 or o3-mini) -> OpenAI o3-mini -> Fallback to primary LLM
        if openrouter_key and openrouter_key != "PLACEHOLDER_UPDATE_ME":
            try:
                openrouter_reasoning = self._llm_config.get("reasoning_model") or model_for("OPENROUTER_REASONING")
                self._llm_reasoning = ChatOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=openrouter_key,
                    model=openrouter_reasoning,
                    default_headers={
                        "HTTP-Referer": "https://syndicateholding.com",
                        "X-Title": "SYNDICATE Holding",
                    },
                )
                logger.info("Initialized reasoning LLM via OpenRouter", model=openrouter_reasoning)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to initialize OpenRouter reasoning LLM", error=str(exc))

        if self._llm_reasoning is None and openai_key and openai_key != "PLACEHOLDER_UPDATE_ME":
            try:
                self._llm_reasoning = ChatOpenAI(
                    api_key=openai_key,
                    model=reasoning_model,
                )
                logger.info("Initialized reasoning LLM via OpenAI")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to initialize OpenAI reasoning LLM", error=str(exc))

    def _routed_client(self, transport: str, model_id: str) -> Any:
        """Chat model for one router candidate; None when its transport has no key."""
        key = getattr(self, "_provider_keys", {}).get(transport)
        if not key:
            return None
        # Bounded waits: without a timeout a hung provider (seen live with direct
        # Gemini) blocked the agent instead of failing over to the next candidate.
        timeout = DEEP_RESEARCH_TIMEOUT_S if "deep-research" in model_id else ROUTED_TIMEOUT_S
        if transport == "anthropic":
            from langchain_anthropic import ChatAnthropic
            # Current Claude models reject `temperature` (HTTP 400).
            return ChatAnthropic(api_key=key, model=model_id, timeout=timeout, max_retries=1)
        if transport == "gemini":
            return ChatOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                              api_key=key, model=model_id, temperature=0, timeout=timeout, max_retries=1)
        if transport == "openrouter":
            return ChatOpenAI(base_url="https://openrouter.ai/api/v1", api_key=key, model=model_id, temperature=0,
                              timeout=timeout, max_retries=1,
                              default_headers={"HTTP-Referer": "https://syndicateholding.com",
                                               "X-Title": "SYNDICATE Holding"})
        raise ValueError(f"unknown_llm_transport: {transport}")

    def _llm_for(self, agent_id: str, default: Any = None) -> Any:
        """The agent's tiered model (base/heavy by task complexity).

        ``default`` (primary LLM when omitted) is what the agent used before
        routing existed; it stays the last resort.
        """
        fallback = default if default is not None else self._llm
        if not getattr(self, "_provider_keys", None):
            return fallback
        routed = getattr(self, "_routed_llms", None)
        if routed is None:
            routed = self._routed_llms = {}
        if agent_id not in routed:
            routed[agent_id] = TieredLLM(agent_id, self._routed_client, fallback=fallback)
        return routed[agent_id]

    def _init_verification_stack(self) -> None:
        """Council / Orc / release-pack are created once and reused."""
        if self._council is None:
            self._council = LLMCouncil(llm=self._llm, default_threshold=0.66)
        if self._orc_verifier is None:
            self._orc_verifier = OrcVerifier(llm=self._llm)
        if self._release_pack is None:
            self._release_pack = ReleasePackBuilder(
                humanizer=self._humanizer,
                video_enhancer=self._video_enhancer,
                verifier=self._orc_verifier,
                cr_store=self._change_requests,
            )

    async def initialize(self) -> None:
        """Initialize tiered LLMs and compile the agent graph."""
        self._init_llms()

        if self._llm_reasoning is None and self._llm is not None:
            self._llm_reasoning = self._llm

        self._init_verification_stack()

        if LANGGRAPH_AVAILABLE:
            self._graph = self._build_graph()

        logger.info(
            "Orchestrator initialized across 10 floors",
            llm_ready=self._llm is not None,
            fast_llm_ready=self._llm_fast is not None,
            reasoning_llm_ready=self._llm_reasoning is not None,
        )

    def _build_graph(self) -> Any:
        """Build the LangGraph state machine covering all 10 syndicate floors."""
        builder = StateGraph(AgentState)

        # Base and routing nodes
        builder.add_node("oscar_agent", self._director_handler)
        builder.add_node("tyler_agent", self._director_handler)
        builder.add_node("jack_agent", self._director_handler)
        builder.add_node("alice_agent", self._director_handler)
        builder.add_node("scout_agent", self._director_handler)
        builder.add_node("dex_agent", self._director_handler)
        builder.add_node("ray_agent", self._director_handler)
        builder.add_node("atlas_agent", self._director_handler)
        builder.add_node("sonar_agent", self._director_handler)
        builder.add_node("router", self._route_task)
        builder.add_node("lessons_check", self._lessons_check)

        # Floor 1: Server & n8n
        builder.add_node("sensory", self._sensory_handler)
        builder.add_node("error_collector", self._error_collector_handler)
        builder.add_node("n8n_templates", self._n8n_templates_handler)
        builder.add_node("proactive", self._proactive_handler)

        # Floor 2: Content Factory
        builder.add_node("floor2", self._floor2_handler)
        builder.add_node("floor2_enhancer", self._floor2_enhancer_handler)

        # Floors 3-6: Reserved
        builder.add_node("reserved_floor", self._reserved_floor_handler)

        # Floor 7: Quant & Capital (Sam)
        builder.add_node("sam_agent", self._sam_agent_handler)

        # Floor 8: SYNDICATE Academy (Kira)
        builder.add_node("kira_agent", self._kira_agent_handler)
        builder.add_node("kira_socratic", self._kira_socratic_handler)

        # Floor 9: Health & Energy (Doc)
        builder.add_node("doc_agent", self._doc_agent_handler)
        builder.add_node("trainer_agent", self._trainer_agent_handler)

        # Floor 10: Command Floor
        builder.add_node("eva_direct", self._eva_direct_handler)
        builder.add_node("eva_curator", self._eva_curator_handler)
        builder.add_node("eva_office", self._eva_office_handler)
        builder.add_node("fin_agent", self._fin_agent_handler)
        builder.add_node("marshal_agent", self._marshal_agent_handler)
        builder.add_node("architect_agent", self._architect_agent_handler)
        builder.add_node("sentinel_check", self._sentinel_check_handler)
        builder.add_node("council", self._council_handler)
        builder.add_node("orc_verifier", self._orc_verifier_handler)
        builder.add_node("change_requests", self._change_requests_handler)
        builder.add_node("memory_command", self._memory_command_handler)
        builder.add_node("vault", self._vault_handler)
        builder.add_node("floor_registry", self._floor_registry_handler)
        builder.add_node("kodex_agent", self._kodex_agent_handler)
        builder.add_node("antigravity_gateway", self._antigravity_gateway_handler)

        # Governance & output gates
        builder.add_node("confidence_gate", self._confidence_gate)
        builder.add_node("outbound_veto", self._outbound_veto)
        builder.add_node("hitl_gate", self._hitl_gate)
        builder.add_node("finalize", self._finalize)

        # Entry point
        builder.set_entry_point("router")
        builder.add_edge("router", "lessons_check")

        # Conditional dispatch from lessons_check to target agent/service
        agent_node_map = {
            "oscar": "oscar_agent",
            "tyler": "tyler_agent",
            "jack": "jack_agent",
            "alice": "alice_agent",
            "scout": "scout_agent",
            "dex": "dex_agent",
            "ray": "ray_agent",
            "atlas": "atlas_agent",
            "sonar": "sonar_agent",
            "sensory": "sensory",
            "error_collector": "error_collector",
            "n8n_templates": "n8n_templates",
            "proactive": "proactive",
            "floor2": "floor2",
            "floor2_enhancer": "floor2_enhancer",
            "reserved_floor": "reserved_floor",
            "sam": "sam_agent",
            "kira": "kira_agent",
            "kira_socratic": "kira_socratic",
            "doc": "doc_agent",
            "trainer": "trainer_agent",
            "eva": "eva_direct",
            "eva_curator": "eva_curator",
            "eva_office": "eva_office",
            "fin": "fin_agent",
            "marshal": "marshal_agent",
            "architect": "architect_agent",
            "sentinel": "sentinel_check",
            "council": "council",
            "orc_verifier": "orc_verifier",
            "change_requests": "change_requests",
            "memory_command": "memory_command",
            "vault": "vault",
            "floor_registry": "floor_registry",
            "kodex": "kodex_agent",
            "antigravity_gateway": "antigravity_gateway",
        }

        builder.add_conditional_edges(
            "lessons_check",
            self._select_agent,
            agent_node_map,
        )

        # All worker nodes proceed to confidence gate
        for node_id in set(agent_node_map.values()):
            builder.add_edge(node_id, "confidence_gate")

        builder.add_edge("confidence_gate", "outbound_veto")
        builder.add_edge("outbound_veto", "hitl_gate")

        builder.add_conditional_edges(
            "hitl_gate",
            lambda s: "finalize" if not s.get("requires_hitl") else "hitl_gate",
            {"finalize": "finalize", "hitl_gate": "hitl_gate"},
        )

        builder.add_edge("finalize", END)
        return builder.compile()

    async def _route_task(self, state: AgentState) -> AgentState:
        """Analyze task and set routing destination."""
        task_type = state.get("task_type", "chat")
        state["status"] = "running"
        state["current_agent"] = self.TASK_ROUTING.get(task_type, "eva")
        logger.info("routing_task", task_type=task_type, target=state["current_agent"])
        return state

    def _select_agent(self, state: AgentState) -> str:
        return state.get("current_agent", "eva")

    async def _lessons_check(self, state: AgentState) -> AgentState:
        payload = state.get("payload") or {}
        # Never accept the reusable-procedure channel from caller input; populate
        # it exclusively from the local, repeated-success SkillStore below.
        payload.pop("prior_skills", None)
        state["payload"] = payload
        # The action text is what a past lesson or verified skill has to match;
        # without it the vector branch was unreachable and skill lookup had no
        # useful filter.
        user_text = (
            payload.get("query")
            or payload.get("message")
            or payload.get("text")
            or payload.get("topic")
            or payload.get("goal")
            or payload.get("action")
            or ""
        )
        task_text = str(state.get("task_type", "")).replace("_", " ").strip()
        lookup_text = " ".join(part for part in (task_text, str(user_text).strip()) if part)[:1200]
        agent_id = state.get("current_agent", "eva")
        if self._lessons:
            lessons = await self._lessons.check_before_action(
                agent_id=agent_id,
                action_embedding=None,
                action_text=lookup_text or None,
            )
            if lessons:
                payload["prior_lessons"] = lessons

        # Only the educational agent consumes learned procedures today.
        # Health, finance, trading, and security decisions stay isolated until
        # their own skill-specific review policy exists.
        if str(agent_id) == "kira":
            try:
                skills = self._skill_store.find_relevant(
                    agent_id=str(agent_id),
                    query=lookup_text,
                    limit=3,
                )
                if skills:
                    payload["prior_skills"] = skills
            except Exception as exc:  # noqa: BLE001 - learning must not block task execution
                logger.warning("skill_lookup_failed", agent_id=agent_id, error=str(exc))
        return state

    async def _confidence_gate(self, state: AgentState) -> AgentState:
        if self._confidence and state.get("result"):
            result = state["result"]
            action_risk = result.get("action_risk", "low")
            confidence = result.get("confidence")
            if confidence is None:
                # An agent that does not report confidence must not be trusted
                # by default for anything that can act on the outside world.
                # Read-only, low-risk results keep the historical 0.90.
                acts_outside = bool(result.get("outbound_actions")) or action_risk != "low"
                confidence = 0.0 if acts_outside else 0.90
            escalation = self._confidence.evaluate(
                agent_id=state.get("current_agent", "eva"),
                confidence=confidence,
                action_type=state.get("task_type", "unknown"),
                action_risk=action_risk,
            )
            if escalation.level == EscalationLevel.REFUSE:
                result["refused"] = True
                result["refuse_reason"] = escalation.reason
            elif escalation.level == EscalationLevel.ASK:
                state["requires_hitl"] = True
                state["hitl_reason"] = f"Confidence gate: {escalation.reason}"
        return state

    async def _persist_outbound_audit(self, state: AgentState, action: Dict[str, Any], veto: Any) -> None:
        writer = getattr(self._memory, "write_outbound_veto", None)
        if not callable(writer):
            return
        score = getattr(veto, "risk_score", None)
        try:
            score_value = float(score) if score is not None else 0.0
        except (TypeError, ValueError, OverflowError):
            score_value = 0.0
        requires_hitl = bool(getattr(veto, "requires_hitl", False))
        policy_rule = "hitl_required" if requires_hitl else "blocked" if not veto.allowed else "allowed"
        risk_level = (
            "critical" if score_value >= 0.9
            else "high" if score_value >= 0.7
            else "medium" if score_value >= 0.4
            else "low"
        )
        try:
            await writer(
                agent_id=str(state.get("current_agent", "eva")),
                action_type=str(action.get("type", action.get("action", "unknown"))),
                policy_rule=policy_rule,
                allowed=bool(veto.allowed),
                reason=(
                    "approval_required" if requires_hitl
                    else "outbound_blocked" if not veto.allowed
                    else "outbound_allowed"
                ),
                risk_level=risk_level,
                details={
                    "task_id": state.get("task_id"),
                    "requires_hitl": requires_hitl,
                    "risk_score": score_value,
                },
            )
        except Exception as exc:  # noqa: BLE001 - audit outage must not change veto behavior
            logger.warning("outbound_audit_write_failed", error_type=type(exc).__name__)

    async def _outbound_veto(self, state: AgentState) -> AgentState:
        if state.get("result", {}).get("outbound_actions"):
            blocked = []
            for action in state["result"]["outbound_actions"]:
                veto = await self._sentinel.veto_outbound_action(state.get("current_agent", "eva"), action)
                await self._persist_outbound_audit(state, action, veto)
                if getattr(veto, "requires_hitl", False):
                    state["requires_hitl"] = True
                    state["hitl_reason"] = "An outbound action requires operator approval"
                if not veto.allowed:
                    blocked.append({**action, "veto_reason": veto.reason})
            if blocked:
                state["result"]["blocked_actions"] = blocked
        return state

    # ─── Floor 1 Handlers ───────────────────────────────────────────────────

    async def _sensory_handler(self, state: AgentState) -> AgentState:
        task_type = state["task_type"]
        payload = state["payload"]
        if task_type == "sensory_split_audio":
            chunks = self._sensory.split_audio_for_whisper(
                payload.get("audio_bytes", b""),
                filename=payload.get("filename", "audio.ogg"),
            )
            # Raw audio bytes are NOT JSON serializable: returning them here made
            # every /execute response blow up with "Object of type bytes is not
            # JSON serializable". Emit metadata only; callers that really need
            # the bytes can ask for them explicitly (they are in-process anyway).
            state["result"] = {
                "status": "ok",
                "chunks_count": len(chunks),
                "chunks": [
                    {
                        "index": c["index"],
                        "filename": c["filename"],
                        "size": c["size"],
                        "bytes_included": False,
                    }
                    for c in chunks
                ],
            }
        elif task_type == "sensory_extract_doc":
            text, meta = self._sensory.extract_document(
                payload.get("file_bytes", b""),
                payload.get("filename", "doc.txt"),
            )
            state["result"] = {"status": "ok", "text": text, "metadata": meta}
        elif task_type == "sensory_chunk_text":
            chunks = self._sensory.chunk_for_embedding(payload.get("text", ""))
            state["result"] = {"status": "ok", "chunks_count": len(chunks), "chunks": chunks}
        elif task_type == "sensory_route_telegram":
            routed = self._sensory.route_telegram_payload(payload)
            state["result"] = {"status": "ok", "routed": routed}
        else:
            state["result"] = {"status": "error", "error": f"Unknown sensory task: {task_type}"}
        state["status"] = "completed"
        return state

    async def _error_collector_handler(self, state: AgentState) -> AgentState:
        task_type = state["task_type"]
        payload = state["payload"]
        if task_type == "record_error":
            res = await self._error_collector.record_error(
                source=payload.get("source", "system"),
                error_message=payload.get("error_message", "unknown error"),
                payload=payload.get("payload", {}),
                stack_trace=payload.get("stack_trace"),
                severity=payload.get("severity", "error"),
            )
            state["result"] = res
        elif task_type == "get_recent_errors":
            res = self._error_collector.get_recent_errors(limit=payload.get("limit", 20))
            state["result"] = {"status": "ok", "errors": res}
        else:
            state["result"] = {"status": "error", "error": f"Unknown error_collector task: {task_type}"}
        state["status"] = "completed"
        return state

    async def _n8n_templates_handler(self, state: AgentState) -> AgentState:
        from src.n8n_templates import (
            build_sensory_switch_workflow,
            build_error_handler_workflow,
            build_cron_briefing_workflow,
            build_evening_reflection_workflow,
        )
        template_name = state["payload"].get("template", "sensory_switch")
        if template_name == "sensory_switch":
            wf = build_sensory_switch_workflow()
        elif template_name == "error_handler":
            wf = build_error_handler_workflow()
        elif template_name == "cron_briefing":
            wf = build_cron_briefing_workflow()
        elif template_name == "evening_reflection":
            wf = build_evening_reflection_workflow()
        else:
            wf = build_sensory_switch_workflow()
        state["result"] = {"status": "ok", "template": template_name, "workflow": wf}
        state["status"] = "completed"
        return state

    async def _proactive_handler(self, state: AgentState) -> AgentState:
        task_type = state["task_type"]
        if task_type == "proactive_morning":
            res = await self.proactive_daily_briefing()
            state["result"] = res
        elif task_type == "proactive_evening":
            res = await self.proactive_evening_reflection()
            state["result"] = res
        else:
            state["result"] = {"status": "error", "error": f"Unknown proactive task: {task_type}"}
        state["status"] = "completed"
        return state

    # ─── Floor 2 Handlers ───────────────────────────────────────────────────

    async def _floor2_handler(self, state: AgentState) -> AgentState:
        from src.departments.coordinator import Floor2Coordinator
        coord = Floor2Coordinator(config=self._config, vault_client=self._vault_client)
        payload = dict(state["payload"])
        if "action" not in payload:
            payload["action"] = state["task_type"]
        result = await coord.execute(payload)
        state["result"] = result
        state["status"] = "completed"
        return state

    async def _floor2_enhancer_handler(self, state: AgentState) -> AgentState:
        task_type = state["task_type"]
        payload = state["payload"]
        if task_type == "humanize_text":
            text = payload.get("text", "")
            res = self._humanizer.humanize(text)
            state["result"] = res
        elif task_type == "enhance_video_prompt":
            idea = payload.get("idea", "")
            res = self._video_enhancer.enhance(idea, **payload.get("options", {}))
            state["result"] = res
        elif task_type == "build_release_pack":
            res = await self._release_pack.build(payload)
            state["result"] = res
        else:
            state["result"] = {"status": "error", "error": f"Unknown floor2 enhancer task: {task_type}"}
        state["status"] = "completed"
        return state

    # ─── Floors 3-6 Handlers ────────────────────────────────────────────────

    async def _reserved_floor_handler(self, state: AgentState) -> AgentState:
        task_type = state.get("task_type", "")
        state["result"] = {
            "status": "reserved",
            "message": f"Floors 3-6 are explicitly reserved for Syndicate expansion (requested: {task_type}).",
            "active_floors": active_floors(),
            "reserved_floors": reserved_floors(),
        }
        state["status"] = "completed"
        return state

    async def _director_handler(self, state: AgentState) -> AgentState:
        from src.agents.oscar import OscarAgent
        from src.agents.tyler import TylerAgent
        from src.agents.jack import JackAgent
        from src.agents.alice import AliceAgent
        from src.agents.scout import ScoutAgent
        from src.agents.dex import DexAgent
        from src.agents.ray import RayAgent
        from src.agents.atlas import AtlasAgent
        from src.agents.sonar import SonarAgent

        agent_id = state["current_agent"]
        classes = {"oscar": OscarAgent, "tyler": TylerAgent, "jack": JackAgent, "alice": AliceAgent, "scout": ScoutAgent, "dex": DexAgent, "ray": RayAgent, "atlas": AtlasAgent, "sonar": SonarAgent}
        config = self._config.get(agent_id, {})
        payload = dict(state.get("payload") or {})
        default_actions = {
            "alice_engineer": "engineer",
            "alice_code_review": "review",
            "alice_status": "capabilities",
        }
        payload.setdefault("action", default_actions.get(state.get("task_type", ""), "capabilities"))
        if config.get("enabled") is not True:
            state["result"] = {"agent": agent_id, "status": "unavailable", "value": None,
                               "warning": "agent_prepared_not_enabled"}
        elif payload.get("action") not in config.get("allowed_actions", ["capabilities"]):
            state["result"] = {"agent": agent_id, "status": "denied", "reason": "action_not_granted"}
        else:
            agent = self._director_clients.get(agent_id)
            if agent is None:
                agent = AliceAgent() if agent_id == "alice" else classes[agent_id](memory=self._memory, config=config)
            state["result"] = await agent.execute(payload)
        state["status"] = "completed"
        return state

    # ─── Floor 7 Handlers (Sam) ─────────────────────────────────────────────

    async def _sam_agent_handler(self, state: AgentState) -> AgentState:
        from src.agents.sam import SamAgent
        agent = SamAgent(
            memory=self._memory,
            llm=self._llm_for("sam"),
            config=self._config.get("sam", self._config),
            registry=self._registry,
        )
        payload = dict(state["payload"])
        action_map = {
            "quant_signal": "evaluate_setup",
            "evaluate_setup": "evaluate_setup",
            "trade_decision": "decision",
            "portfolio_review": "reflect",
            "portfolio_risk": "portfolio_risk",
            "swarm_research_sam": "swarm_research",
            "morning_data_sam": "morning_data",
        }
        payload.setdefault("action", action_map.get(state["task_type"], "evaluate_setup"))
        result = await agent.execute(payload)
        state["result"] = result
        if result.get("tradeable") and result.get("requires_hitl"):
            state["requires_hitl"] = True
            state["hitl_reason"] = "Sam quant signal requires human approval (strict capital protection)"
        state["status"] = "completed"
        return state

    # ─── Floor 8 Handlers (Kira) ────────────────────────────────────────────

    async def _kira_agent_handler(self, state: AgentState) -> AgentState:
        from src.agents.kira import KiraAgent
        agent = KiraAgent(memory=self._memory, llm=self._llm_for("kira"), config=self._config.get("kira", self._config))
        payload = dict(state["payload"])
        # ``mentor_code_review`` used to fall through to Kira's default handler
        # (socratic_dialogue), silently answering a code-review request with a
        # dialogue. Map routed task types onto Kira's real action names.
        action_map = {
            "mentor_code_review": "code_review",
            "morning_data_kira": "morning_data",
            # A free-text Telegram message to Kira is a conversation turn: the
            # user's own words are the statement to challenge. (Without this the
            # agent argued with a hard-coded demo statement.)
            "webhook_telegram_kira": "socratic_dialogue",
        }
        if state["task_type"] == "webhook_telegram_kira":
            incoming = str(payload.get("text") or "").strip()
            payload.setdefault("statement", incoming)
            payload.setdefault("topic", incoming[:120])
        payload.setdefault("action", action_map.get(state["task_type"], state["task_type"]))
        result = await agent.execute(payload)
        state["result"] = result
        state["status"] = "completed"
        return state

    async def _kira_socratic_handler(self, state: AgentState) -> AgentState:
        task_type = state["task_type"]
        payload = state["payload"]
        if task_type == "kira_socratic_next":
            res = self._socratic_tutor.next_hint(
                session_id=payload.get("session_id", "socratic_session"),
                user_message=payload.get("user_message", ""),
                problem_statement=payload.get("problem_statement", ""),
                solution=payload.get("solution", ""),
            )
            state["result"] = res
        elif task_type == "kira_socratic_solve":
            res = self._socratic_tutor.solve(
                session_id=payload.get("session_id", "socratic_session"),
                problem_statement=payload.get("problem_statement", ""),
                solution=payload.get("solution", ""),
            )
            state["result"] = res
        else:
            state["result"] = {"status": "error", "error": f"Unknown kira socratic task: {task_type}"}
        state["status"] = "completed"
        return state

    # ─── Floor 9 Handlers (Doc) ─────────────────────────────────────────────

    async def _doc_agent_handler(self, state: AgentState) -> AgentState:
        from src.agents.doc import DocAgent
        agent = DocAgent(memory=self._memory, llm=self._llm_for("doc"), config=self._config.get("doc", self._config))
        payload = dict(state["payload"])
        # Task types routed here do not always match DocAgent's action names
        # (e.g. ``morning_data_doc``), so translate them explicitly.
        action_map = {
            "analyze_document": "summarize",
            "morning_data_doc": "morning_data",
            "swarm_research_doc": "swarm_research",
        }
        if state["task_type"] == "webhook_telegram_doc":
            # Doc works on documents and structured metrics, not free chat, and
            # health data must never be guessed from a chat line.
            state["result"] = {
                "agent": "doc",
                "status": "unavailable",
                "value": None,
                "reason": "free_text_not_supported: send a document or use a command",
            }
            state["status"] = "completed"
            return state
        payload.setdefault("action", action_map.get(state["task_type"], state["task_type"]))
        result = await agent.execute(payload)
        state["result"] = result
        state["status"] = "completed"
        return state

    async def _trainer_agent_handler(self, state: AgentState) -> AgentState:
        from src.agents.trainer import TrainerAgent

        agent = TrainerAgent(
            memory=self._memory,
            llm=self._llm_for("trainer"),
            config=self._config.get("trainer", self._config),
            registry=self._registry,
        )
        payload = dict(state["payload"])
        action_map = {
            "morning_data_trainer": "morning_data",
            "swarm_research_trainer": "swarm_research",
            "webhook_telegram_trainer": "capabilities",
        }
        payload.setdefault("action", action_map.get(state["task_type"], state["task_type"]))
        result = await agent.execute(payload)
        state["result"] = result
        state["status"] = "completed"
        return state

    # ─── Floor 10 Handlers (Command Floor) ──────────────────────────────────

    async def _telegram_owner_id(self) -> Optional[str]:
        """Owner's Telegram user id from Vault; None (deny) when unavailable."""
        client = getattr(self, "_vault_client", None)
        if client is None:
            return None
        try:
            secret = await client.get_secret(secret_path("telegram"))
        except Exception as exc:  # noqa: BLE001 - no owner means deny, not a crash
            logger.warning("telegram_owner_lookup_failed", error_type=type(exc).__name__)
            return None
        value = (secret or {}).get("owner_user_id")
        return str(value) if value else None

    async def _eva_direct_handler(self, state: AgentState) -> AgentState:
        from src.agents.eva import EvaAgent
        from src.agents.eva_access import eva_telegram_inbound_allowed, extract_telegram_chat_id

        payload = dict(state["payload"])
        if state.get("task_type") in {"webhook_telegram", "webhook_telegram_eva"} and not eva_telegram_inbound_allowed(
            extract_telegram_chat_id(payload), owner_user_id=await self._telegram_owner_id()
        ):
            state["result"] = {
                "agent": "eva",
                "status": "denied",
                "error": "telegram_inbound_denied",
            }
            state["status"] = "completed"
            return state
        agent = EvaAgent(memory=self._memory, llm=self._llm_for("eva"), config=self._config, vault=self._vault)
        if "action" not in payload:
            payload["action"] = state["task_type"] if state["task_type"] in ("chat", "compose_briefing", "compose_reflection", "delegate", "system_status") else "chat"
        result = await agent.execute(payload)
        state["result"] = result
        state["status"] = "completed"
        return state

    async def _eva_curator_handler(self, state: AgentState) -> AgentState:
        from src.agents.eva_curator import EvaCurator
        agent = EvaCurator(memory=self._memory, llm=self._llm_for("eva"), config=self._config, vault=self._vault)
        payload = dict(state["payload"])
        if "action" not in payload:
            payload["action"] = state["task_type"]
        result = await agent.execute(payload)
        state["result"] = result
        state["status"] = "completed"
        return state

    async def _eva_office_handler(self, state: AgentState) -> AgentState:
        from src.agents.office_copilot import OfficeCopilotAgent
        agent = OfficeCopilotAgent(memory=self._memory, llm=self._llm_for("office_copilot"), config=self._config)
        payload = dict(state["payload"])
        if "action" not in payload:
            payload["action"] = state["task_type"]
        result = await agent.execute(payload)
        state["result"] = result
        state["status"] = "completed"
        return state

    async def _fin_agent_handler(self, state: AgentState) -> AgentState:
        from src.agents.fin import FinAgent
        agent = FinAgent(memory=self._memory, llm=self._llm_for("fin"), config=self._config.get("fin", self._config), registry=self._registry)
        payload = dict(state["payload"])
        action_map = {
            "financial_analysis": "analyze",
            "fin_runway": "runway",
            "fin_budget_check": "budget_check",
            "fin_tax_radar": "tax_radar",
            "fin_sync_bank": "sync_bank_data",
            "morning_data_fin": "morning_data",
            "fin_report": "report",
            "eva_basket_ready": "funds_check",
            "fin_funds_check": "funds_check",
        }
        # Відправник визначає, кому відповідає Фін: автоматичний виклик — від Єви.
        payload.setdefault("from", "eva" if state["task_type"] == "eva_basket_ready" else "andrii")
        payload.setdefault("action", action_map.get(state["task_type"], "analyze"))
        result = await agent.execute(payload)
        state["result"] = result
        state["status"] = "completed"
        return state

    async def _marshal_agent_handler(self, state: AgentState) -> AgentState:
        from src.agents.marshal import MarshalAgent
        from src.agents.marshal_access import marshal_host_control_allowed

        payload = dict(state["payload"])
        action_map = {
            "marshal_execute": payload.get("action", "security_audit"),
            "morning_data_marshal": "morning_data",
            "security_audit": "security_audit",
            "security_status": "security_audit",
            "incident_report": "incident_report",
            "emergency_lockdown": "emergency_lockdown",
            "compliance_check": "compliance_check",
        }
        payload["action"] = action_map.get(state["task_type"], payload.get("action", "security_audit"))
        if payload["action"] == "emergency_lockdown" and not marshal_host_control_allowed():
            state["result"] = {
                "agent": "marshal",
                "status": "denied",
                "error": "host_control_not_granted",
            }
            state["status"] = "completed"
            return state
        agent = MarshalAgent(
            memory=self._memory,
            llm=self._llm_for("marshal"),
            config=self._config.get("marshal", self._config),
            sentinel=self._sentinel,
        )
        result = await agent.execute(payload)
        state["result"] = result
        state["status"] = "completed"
        return state

    async def _architect_agent_handler(self, state: AgentState) -> AgentState:
        from src.agents.architect import ArchitectAgent
        agent = ArchitectAgent(
            memory=self._memory,
            llm=self._llm_for("architect", default=self._llm_reasoning),
            config=self._config.get("architect", self._config),
            registry=self._registry,
            change_request_store=self._change_requests,
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
            "morning_data_architect": "capabilities",
        }
        payload.setdefault("action", action_map.get(state["task_type"], "capabilities"))
        result = await agent.execute(payload)
        state["result"] = result
        if result.get("requires_hitl"):
            state["requires_hitl"] = True
            state["hitl_reason"] = result.get("hitl_reason") or "Architect workflow proposal requires operator approval"
        state["status"] = "completed"
        return state

    async def _sentinel_check_handler(self, state: AgentState) -> AgentState:
        task_type = state["task_type"]
        payload = state["payload"]
        if task_type == "sentinel_command_safety":
            res = self._sentinel.check_command_safety(payload.get("command", ""))
            state["result"] = res
        elif task_type == "sentinel_lethal_trifecta":
            res = self._sentinel.check_lethal_trifecta(payload)
            state["result"] = res
        elif task_type == "sentinel_slopsquatting":
            res = self._sentinel.assess_dependency_install(payload.get("package_name", ""))
            state["result"] = res
        elif task_type == "sentinel_scan_secrets":
            res = self._sentinel.scan_output_for_secrets(payload.get("output", ""))
            state["result"] = res
        else:
            validation = await self._sentinel.validate_task(payload)
            state["result"] = {
                "allowed": validation.allowed,
                "reason": validation.reason,
                "risk_score": validation.risk_score,
            }
        state["status"] = "completed"
        return state

    async def _council_handler(self, state: AgentState) -> AgentState:
        res = await self._council.deliberate(
            question=state["payload"].get("question", ""),
            options=state["payload"].get("options", []),
            context=state["payload"].get("context") or "",
        )
        res_dict = res.to_dict() if hasattr(res, "to_dict") else res
        state["result"] = res_dict
        if not res_dict.get("quorum") or res_dict.get("consensus_score", 0) < 0.60:
            state["requires_hitl"] = True
            state["hitl_reason"] = f"LLM Council low consensus / dissenting opinion: {res_dict.get('chosen')}"
        state["status"] = "completed"
        return state

    async def _orc_verifier_handler(self, state: AgentState) -> AgentState:
        res = await self._orc_verifier.verify_claim(
            claim=state["payload"].get("claim", ""),
            evidence=state["payload"].get("evidence", ""),
            context=state["payload"].get("context"),
        )
        state["result"] = res
        state["status"] = "completed"
        return state

    async def _change_requests_handler(self, state: AgentState) -> AgentState:
        task_type = state["task_type"]
        payload = state["payload"]
        try:
            if task_type == "submit_change_request":
                state["result"] = self._change_requests.submit(
                    title=payload.get("title", "Untitled CR"),
                    description=payload.get("description", ""),
                    target_path=payload.get("target_path", "statutes/statute.md"),
                    proposed_content=payload.get("proposed_content", ""),
                    # Default to an unprivileged ``agent`` identity: if the CR
                    # defaulted to ``operator`` — the same identity ``review``
                    # and ``apply`` default to — every default round-trip was
                    # refused as self-approval once the guard was enforced.
                    author=payload.get("author", "agent"),
                )
            elif task_type in OPERATOR_ONLY_TASK_TYPES:
                # Approval is a human act. Only the authenticated /cr/review and
                # /cr/apply endpoints set ``operator_verified``; a caller cannot
                # supply it (nor a ``reviewer`` name) through the payload.
                if not state.get("operator_verified"):
                    logger.warning("operator_only_task_refused", task_type=task_type)
                    state["result"] = {
                        "status": "error",
                        "error": "operator_verification_required",
                    }
                elif task_type == "review_change_request":
                    state["result"] = self._change_requests.review(
                        cr_id=payload.get("cr_id", ""),
                        decision=payload.get("decision", "approve"),
                        reviewer=OPERATOR_IDENTITY,
                        comment=payload.get("comment", ""),
                    )
                else:
                    state["result"] = self._change_requests.apply(cr_id=payload.get("cr_id", ""))
            else:
                state["result"] = {"status": "error", "error": f"Unknown CR task: {task_type}"}
        except ChangeRequestError as exc:
            # A missing / already-decided CR is an expected condition, not a crash:
            # surface it as a normal error result so HTTP callers get 200 + error.
            logger.warning("change_request_rejected", reason=str(exc))
            state["result"] = {"status": "error", "error": str(exc)}
        except VaultError as exc:
            logger.warning("change_request_vault_error", reason=str(exc))
            state["result"] = {"status": "error", "error": str(exc)}
        state["status"] = "completed"
        return state

    async def _memory_command_handler(self, state: AgentState) -> AgentState:
        text = state["payload"].get("text", "")
        cmd = parse_command(text if isinstance(text, str) else "")
        if cmd is None:
            state["result"] = {"status": "not_a_memory_command"}
        else:
            try:
                state["result"] = execute_command(
                    cmd,
                    self._vault,
                    operator_confirmed_forget=state["payload"].get("confirmed") is True,
                )
            except VaultError:
                logger.warning("memory_command_failed", command=cmd.kind)
                state["result"] = {"status": "error", "error": "memory_command_failed"}
        state["status"] = "completed"
        return state

    async def _vault_handler(self, state: AgentState) -> AgentState:
        task_type = state["task_type"]
        payload = state["payload"]
        if task_type == "vault_write_ground_truth":
            rel_path = payload.get("path", "wiki/general.md")
            content = payload.get("content", "")
            if not isinstance(rel_path, str) or not isinstance(content, str):
                state["result"] = {"status": "error", "error": "string_path_and_content_required"}
                state["status"] = "completed"
                return state
            try:
                parts = Path(rel_path).parts
                if parts and (
                    parts[0] in {"raw", "archive"}
                    or (len(parts) >= 3 and parts[0] == "agents" and parts[2] == "memory.md")
                ):
                    state["result"] = {
                        "status": "refused",
                        "error": "managed_memory_path_requires_policy_command",
                    }
                    state["status"] = "completed"
                    return state
                self._vault.write(rel_path, content)
            except VaultError:
                state["result"] = {"status": "error", "error": "vault_write_rejected"}
                state["status"] = "completed"
                return state
            state["result"] = {"status": "ok", "path": rel_path}
        elif task_type == "vault_read_ground_truth":
            rel_path = payload.get("path", "wiki/general.md")
            exists = self._vault.exists(rel_path)
            content = self._vault.read(rel_path) if exists else None
            state["result"] = {"status": "ok" if exists else "not_found", "path": rel_path, "content": content}
        elif task_type == "vault_reindex":
            state["result"] = await self._reindex_vault(payload)
        else:
            state["result"] = {"status": "error", "error": f"Unknown vault task: {task_type}"}
        state["status"] = "completed"
        return state

    async def _reindex_vault(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Rebuild the pgvector index from the Markdown ground truth.

        ``MarkdownVault.reindex`` needs an ``embed`` and an ``upsert`` callable.
        The previous implementation called it with no arguments (and never
        awaited the coroutine), so ``vault_reindex`` always blew up with a
        ``TypeError``. Without an embedder wired we now refuse cleanly instead.
        """
        embed = payload.get("embed")
        upsert = payload.get("upsert")
        if embed is None or upsert is None:
            return {
                "status": "error",
                "error": (
                    "vault_reindex requires an 'embed' and an 'upsert' callable "
                    "(vector index is a rebuildable copy of the Markdown source)"
                ),
                "files": self._vault.list_files(),
            }
        stats = await self._vault.reindex(embed=embed, upsert=upsert)
        return {"status": "ok", **stats}

    async def _floor_registry_handler(self, state: AgentState) -> AgentState:
        state["result"] = {
            "status": "ok",
            "floors": FLOORS,
            "active_floors": active_floors(),
            "reserved_floors": reserved_floors(),
        }
        state["status"] = "completed"
        return state

    async def _kodex_agent_handler(self, state: AgentState) -> AgentState:
        from src.agents.kodex import KodexAgent
        from src.integrations.notebooklm_obsidian_bridge import NotebookLMObsidianBridge

        vault_root = Path(getattr(self._vault, "root", None) or getattr(self._vault, "_root", None) or "scratch")
        bridge = NotebookLMObsidianBridge(vault_path=vault_root / "second_brain")
        agent = KodexAgent(
            memory=self._memory,
            config=self._config.get("kodex", self._config),
            bridge=bridge,
        )
        payload = dict(state.get("payload") or {})
        action_map = {
            "kodex_ingest_notebook": "process_with_notebooklm",
            "kodex_export_obsidian": "sync_to_obsidian",
            "kodex_dispatch_task": "dispatch_task",
            "kodex_triage_tasks": "triage_task_web",
            "kodex_storage_stats": "storage_stats",
        }
        payload.setdefault("action", action_map.get(state.get("task_type", ""), "storage_stats"))
        if "content" not in payload and "summary" in payload:
            payload["content"] = payload["summary"]
        state["result"] = await agent.execute(payload)
        state["status"] = "completed"
        return state

    async def _antigravity_gateway_handler(self, state: AgentState) -> AgentState:
        from src.integrations.antigravity_contractor_gateway import AntigravityContractorGateway

        vault_root = Path(getattr(self._vault, "root", None) or getattr(self._vault, "_root", None) or "scratch")
        gw = AntigravityContractorGateway(
            channels_dir=vault_root / "antigravity_contractor",
        )
        task_type = state.get("task_type", "")
        payload = dict(state.get("payload") or {})
        if task_type == "antigravity_contractor_dispatch":
            state["result"] = gw.agent_submits_task(
                agent_id=str(payload.get("requester_agent", payload.get("agent_id", "architect"))),
                task_title=str(payload.get("objective", payload.get("title", "Analyze architecture"))),
                task_prompt=str(payload.get("context_summary", payload.get("prompt", "Execute R&D task"))),
                attachments=list(payload.get("target_files") or []),
            )
        elif task_type == "antigravity_contractor_compact":
            channel = gw.get_channel(str(payload.get("agent_id", "architect")))
            state["result"] = channel.compact_thread()
        else:
            state["result"] = gw.get_status()
        state["status"] = "completed"
        return state

    async def _hitl_gate(self, state: AgentState) -> AgentState:
        """Park the task for a human instead of letting its actions through.

        Outbound actions are removed from the result and stored in the HITL
        queue; they come back only via an approved ``HitlQueue.release``.
        If the queue itself fails we fail closed: the actions are dropped and
        the result says so, rather than being released unreviewed.
        """
        if not state.get("requires_hitl"):
            return state
        reason = str(state.get("hitl_reason") or "approval_required")
        logger.warning("hitl_required", reason=reason, task_type=state.get("task_type"))
        result = state.get("result")
        if not isinstance(result, dict):
            result = {"value": result} if result is not None else {}
        held = list(result.pop("outbound_actions", None) or [])
        if result.get("approval_cr_id") and not held:
            # The agent already parked this as a change request, which has its
            # own approval inbox (/cr/pending). Do not create a second item.
            result["hitl_item_id"] = None
            result["hitl_via"] = "change_request"
        else:
            try:
                result["hitl_item_id"] = self._hitl_queue.enqueue(
                    agent_id=str(state.get("current_agent", "eva")),
                    task_type=str(state.get("task_type", "unknown")),
                    task_id=str(state.get("task_id", "")),
                    reason=reason,
                    held_actions=held,
                )
            except Exception as exc:  # noqa: BLE001 - fail closed, never release unreviewed
                logger.error("hitl_enqueue_failed", error_type=type(exc).__name__)
                result["hitl_item_id"] = None
                result["hitl_queue_error"] = "enqueue_failed_actions_dropped"
        result["required_hitl"] = True
        result["hitl_reason"] = reason
        result["held_actions_count"] = len(held)
        state["result"] = result
        # The task itself finished (it produced a proposal); what is held is the
        # *effect*. The flag is cleared so the graph proceeds to finalize — the
        # old hitl_gate -> hitl_gate loop edge would otherwise spin forever.
        state["requires_hitl"] = False
        return state

    @staticmethod
    def _task_audit_outcome(state: AgentState, result: Dict[str, Any]) -> str:
        result_status = str(result.get("status", "")).lower()
        if result.get("refused") or result_status == "refused":
            return "refused"
        if (
            result.get("blocked")
            or result.get("allowed") is False
            or result.get("blocked_actions")
            or result_status.startswith("blocked")
        ):
            return "blocked"
        if (
            state.get("status") != "completed"
            or result.get("error")
            or result_status in {"error", "failed", "unavailable"}
        ):
            return "failure"
        if state.get("requires_hitl") or result.get("requires_hitl") or result.get("required_hitl"):
            return "pending"
        return "success"

    async def _persist_task_audit(self, state: AgentState, result: Any) -> None:
        writer = getattr(self._memory, "write_audit_decision", None)
        if not callable(writer):
            return
        result_data = result if isinstance(result, dict) else {}
        outcome = self._task_audit_outcome(state, result_data)
        requires_hitl = bool(
            state.get("requires_hitl")
            or result_data.get("requires_hitl")
            or result_data.get("required_hitl")
        )
        capture = result_data.get("skill_capture")
        capture_status = capture.get("status") if isinstance(capture, dict) else None
        payload = state.get("payload")
        if not isinstance(payload, dict):
            payload = {}
        prior_lessons = payload.get("prior_lessons")
        details = {
            "task_id": state.get("task_id"),
            "result_status": result_data.get("status", state.get("status")),
            "requires_hitl": requires_hitl,
            "allowed": result_data.get("allowed"),
            "risk_score": result_data.get("risk_score"),
            "prior_lessons_count": len(prior_lessons) if isinstance(prior_lessons, list) else 0,
            "blocked_actions_count": len(result_data.get("blocked_actions") or []),
            "skill_capture_status": capture_status,
        }
        try:
            await writer(
                agent_id=str(state.get("current_agent", "eva")),
                action=str(state.get("task_type", "unknown")),
                task_type=str(state.get("task_type", "unknown")),
                confidence=result_data.get("confidence"),
                escalation="refuse" if outcome in {"refused", "blocked"} else "ask" if requires_hitl else "act",
                facts_used=[],
                lessons_checked=[],
                outcome=outcome,
                hitl_override=False,
                details=details,
            )
        except Exception as exc:  # noqa: BLE001 - audit outage must not change task result
            logger.warning("decision_audit_write_failed", error_type=type(exc).__name__)

    async def _finalize(self, state: AgentState) -> AgentState:
        result = state.get("result")
        if hasattr(result, "to_dict"):
            result = result.to_dict()
        elif hasattr(result, "__dict__") and not isinstance(result, (dict, list, str, int, float, bool, type(None))):
            result = getattr(result, "__dict__", str(result))

        if isinstance(result, dict) and "skill_candidate" in result:
            candidate = result.pop("skill_candidate")
            result_status = str(result.get("status", "")).lower()
            succeeded = (
                state.get("status") == "completed"
                and not result.get("error")
                and not result.get("refused")
                and not result.get("blocked")
                and not result.get("blocked_actions")
                and not result.get("requires_hitl")
                and result.get("verified") is not False
                and result_status not in {"error", "failed", "unavailable"}
                and not result_status.startswith("blocked")
            )
            try:
                capture = self._skill_store.record_success(
                    agent_id=str(state.get("current_agent", "eva")),
                    task_type=str(state.get("task_type", "unknown")),
                    task_id=str(state.get("task_id", "unknown")),
                    candidate=candidate,
                    success=succeeded,
                )
            except Exception as exc:  # noqa: BLE001 - skill storage must never fail a task
                logger.warning("skill_capture_failed", error=str(exc))
                capture = {"status": "error", "reason": str(exc)}
            result["skill_capture"] = capture
            state["result"] = result

        await self._persist_task_audit(state, result)
        # Chat, memory queries, and Telegram payloads may contain private text.
        # Do not persist their input/output in LangGraph checkpoints.
        if state.get("task_type") not in {"chat", "webhook_telegram", "parse_memory_command"}:
            await self._memory.save_checkpoint(
                thread_id=state["session_id"],
                checkpoint_id=state["task_id"],
                agent_id=state.get("current_agent", "eva"),
                state_data={"status": state["status"], "task_type": state.get("task_type")},
            )
        return state

    # ─── Execution Routine ──────────────────────────────────────────────────

    async def execute(
        self,
        task_type: str,
        payload: Dict[str, Any],
        session_id: Optional[str] = None,
        *,
        operator_verified: bool = False,
    ) -> Dict[str, Any]:
        """Execute a task through the orchestration graph across any of the 10 floors.

        ``operator_verified`` must only be passed by code that has itself
        authenticated a human operator (see ``/cr/review`` and ``/cr/apply``).
        """
        task_id = str(uuid.uuid4())
        provided_session_id = (
            session_id.strip()
            if isinstance(session_id, str) and session_id.strip()
            else None
        )
        session_id = provided_session_id or str(uuid.uuid4())
        task_payload = dict(payload or {})
        if provided_session_id:
            # The explicit conversation ID is authoritative so domain agents
            # pair recall with writes on the same thread even if the payload
            # contains a stale or conflicting session_id.
            task_payload["session_id"] = provided_session_id

        initial_state: AgentState = {
            "session_id": session_id,
            "task_id": task_id,
            "task_type": task_type,
            "payload": task_payload,
            "messages": [],
            "current_agent": None,
            "result": None,
            "requires_hitl": False,
            "hitl_reason": None,
            "error": None,
            "status": "pending",
            "operator_verified": bool(operator_verified),
        }

        if self._graph:
            final_state = await self._graph.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": session_id}},
            )
        else:
            final_state = await self._fallback_execute(initial_state)

        return {
            "task_id": task_id,
            "status": final_state["status"],
            "result": final_state.get("result"),
        }

    async def _fallback_execute(self, state: AgentState) -> AgentState:
        """Deterministic fallback dispatcher when LangGraph compile is bypassed."""
        state = await self._route_task(state)
        state = await self._lessons_check(state)

        target = state.get("current_agent", "eva")
        dispatch_table = {
            "oscar": self._director_handler,
            "tyler": self._director_handler,
            "jack": self._director_handler,
            "alice": self._director_handler,
            "scout": self._director_handler,
            "dex": self._director_handler,
            "ray": self._director_handler,
            "atlas": self._director_handler,
            "sonar": self._director_handler,
            "sensory": self._sensory_handler,
            "error_collector": self._error_collector_handler,
            "n8n_templates": self._n8n_templates_handler,
            "proactive": self._proactive_handler,
            "floor2": self._floor2_handler,
            "floor2_enhancer": self._floor2_enhancer_handler,
            "reserved_floor": self._reserved_floor_handler,
            "sam": self._sam_agent_handler,
            "kira": self._kira_agent_handler,
            "kira_socratic": self._kira_socratic_handler,
            "doc": self._doc_agent_handler,
            "trainer": self._trainer_agent_handler,
            "eva": self._eva_direct_handler,
            "eva_curator": self._eva_curator_handler,
            "eva_office": self._eva_office_handler,
            "fin": self._fin_agent_handler,
            "marshal": self._marshal_agent_handler,
            "architect": self._architect_agent_handler,
            "sentinel": self._sentinel_check_handler,
            "council": self._council_handler,
            "orc_verifier": self._orc_verifier_handler,
            "change_requests": self._change_requests_handler,
            "memory_command": self._memory_command_handler,
            "vault": self._vault_handler,
            "floor_registry": self._floor_registry_handler,
            "kodex": self._kodex_agent_handler,
            "antigravity_gateway": self._antigravity_gateway_handler,
        }

        handler = dispatch_table.get(target, self._eva_direct_handler)
        state = await handler(state)
        state = await self._confidence_gate(state)
        state = await self._outbound_veto(state)
        state = await self._hitl_gate(state)
        state = await self._finalize(state)
        return state

    async def handle_webhook(self, source: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhooks from external systems."""
        chat = await self._telegram_chat(source, payload)
        if chat is not None:
            return chat
        task_type = f"webhook_{source}"
        result = await self.execute(task_type=task_type, payload=payload)
        return result

    async def _telegram_chat(self, source: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Free text to a director's bot is a conversation (Eva keeps her own path).

        Returns None when the message is not chat (commands, Eva) so the regular
        task routing handles it.
        """
        from src.agent_chat import PERSONAS, ChatHistory, chat_reply, chat_text

        agent_id = source[len("telegram_"):] if source.startswith("telegram_") else None
        text = chat_text(payload or {})
        if agent_id in (None, "eva") or agent_id not in PERSONAS or text is None:
            return None
        from src.agents.eva_access import extract_telegram_chat_id

        owner = await self._telegram_owner_id()
        if not owner or extract_telegram_chat_id(payload) != owner:
            result: Dict[str, Any] = {"agent": agent_id, "status": "denied", "error": "telegram_inbound_denied"}
        else:
            if getattr(self, "_chat_history", None) is None:
                # Read the Redis handle on every call: MemoryManager drops it on failure.
                self._chat_history = ChatHistory(lambda: getattr(getattr(self, "_memory", None), "_redis", None))
            result = await chat_reply(agent_id, text, self._llm_for(agent_id), self._chat_history, owner)
        return {"task_id": str(uuid.uuid4()), "status": "completed", "result": result}

    # ─── Proactive Lifecycles ────────────────────────────────────────────────

    async def proactive_daily_briefing(self, agent_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compose only from reports already supplied; never dispatch agent tasks."""
        if not isinstance(agent_data, dict):
            return {
                "status": "unavailable",
                "reason": "no_precollected_reports",
                "agent_tasks_dispatched": False,
                "voice_started": False,
            }
        result = await self.execute("chat", {"action": "compose_briefing", "agent_data": agent_data})
        return {"briefing": result.get("result", {}), "agent_data": agent_data, "agent_tasks_dispatched": False}

    async def proactive_evening_reflection(self, evening_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compose only from reports already supplied; do not invoke Doc or Kira."""
        if not isinstance(evening_data, dict):
            return {
                "status": "unavailable",
                "reason": "no_precollected_reports",
                "agent_tasks_dispatched": False,
            }
        result = await self.execute("chat", {"action": "compose_reflection", "evening_data": evening_data})
        return {"reflection": result.get("result", {}), "evening_data": evening_data, "agent_tasks_dispatched": False}

    async def proactive_nightly_analysis(self) -> Dict[str, Any]:
        """Dormant 03:00 contract; no source provider is configured or invoked."""
        return {
            "status": "unavailable",
            "reason": "nightly_source_provider_not_configured",
            "agent_tasks_dispatched": False,
            "external_actions": False,
        }

    async def weekly_life_review(self) -> Dict[str, Any]:
        """Called by n8n cron on Sunday at 20:00."""
        return await self.execute("weekly_review", {"action": "weekly_review"})

    def get_floors_registry(self) -> Dict[str, Any]:
        """Direct access to the 10-floor layout."""
        return {
            "floors": FLOORS,
            "active": active_floors(),
            "reserved": reserved_floors(),
        }


    async def quick_perplexity_search(self, query: str) -> dict:
        """Fast Perplexity lookup directly in Eva for immediate 2-3s answers."""
        from src.agents.sonar import SonarAgent
        agent = SonarAgent(memory=self._memory, config=self._config.get("sonar", {}))
        return await agent.quick_search({"query": query})
