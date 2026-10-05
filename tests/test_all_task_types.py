"""
EVA SYNDICATE — Task-routing smoke suite.

Exercises **every** task type in ``EvaOrchestrator.TASK_ROUTING`` with a mocked
LLM and a mocked database session. The point is not to assert on the answers,
but to prove that each route:

  * does not raise,
  * returns a JSON-serialisable result (a raw ``bytes`` payload used to blow up
    the FastAPI layer with a 500),
  * reports ``status == "completed"``.

Add an entry to ``PAYLOADS`` (or ``PRESEED``) whenever a new task type appears
in ``TASK_ROUTING`` — ``test_every_task_type_is_covered`` enforces that.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "deploy" / "runtime"))


# ─────────────────────────────────────────────────────────────────────────────
# Test doubles
# ─────────────────────────────────────────────────────────────────────────────
class MockResult:
    def __init__(self, rows=None, scalar_val=None):
        self._rows = rows or []
        self._scalar = scalar_val

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def scalar(self):
        return self._scalar

    def scalar_one(self):
        return self._scalar or "00000000-0000-0000-0000-000000000001"


class MockAsyncSession:
    def __init__(self, log: List[str]) -> None:
        self.log = log

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def execute(self, stmt, params=None):
        self.log.append(str(stmt))
        return MockResult(rows=[], scalar_val=0)

    async def commit(self):
        return None


class _Resp:
    def __init__(self, content: str) -> None:
        self.content = content


class MockLLM:
    """Deterministic stand-in for ChatAnthropic / ChatOpenAI."""

    async def ainvoke(self, messages):
        if isinstance(messages, str):
            text = messages
        else:
            text = "\n".join(getattr(m, "content", str(m)) for m in messages)
        if "Answer with exactly one of:" in text:
            m = re.search(r"Answer with exactly one of:\s*([^,\n]+)", text)
            if m:
                return _Resp(f"{m.group(1).strip()}. Consensus.")
        return _Resp(json.dumps({
            "summary": "ok", "status": "ok", "confidence": 0.95,
            "response": "probe response", "recommendation": "A",
            "findings": ["x"], "claims": [], "verified_facts": [],
            "synthesis": "s", "analysis": "a", "curriculum": "c",
            "socratic_response": "s", "quiz": "q", "narrative": "n",
            "vibecoding_brief": "b", "historical_synthesis": "h",
            "review": "r", "summary_text": "st",
        }))


# ─────────────────────────────────────────────────────────────────────────────
# Payloads
# ─────────────────────────────────────────────────────────────────────────────
#: Task types whose payload needs a value produced by an earlier task.
PRESEED = ("review_change_request", "apply_change_request")

#: Task types that legitimately answer with ``status == "error"`` because the
#: sandbox has no vector backend / no network egress. Everything else must
#: complete cleanly.
EXPECTED_ERROR_RESULTS = frozenset({"vault_reindex"})


def _payloads(tmp_path: Path) -> Dict[str, Dict[str, Any]]:
    art = tmp_path / "probe_art.png"
    return {
        "sensory_split_audio": {"audio_bytes": b"\x00" * 10, "filename": "a.ogg"},
        "sensory_extract_doc": {"file_bytes": b"hello world", "filename": "d.txt"},
        "sensory_chunk_text": {"text": "hello world this is a longer chunk of text for embedding"},
        "sensory_route_telegram": {"update_id": 1, "message": {"chat": {"id": 1}, "text": "hi"}},
        "record_error": {"source": "probe", "error_message": "boom", "payload": {"a": 1}},
        "get_recent_errors": {"limit": 5},
        "generate_n8n_template": {"template": "sensory_switch"},
        "proactive_morning": {},
        "proactive_evening": {},
        "render_short_video": {"action": "render_short_video", "topic": "x"},
        "create_viral_short": {"action": "create_viral_short", "topic": "x"},
        "direct_short_script": {"action": "direct_short_script", "topic": "x"},
        "source_broll_batch": {"action": "source_broll_batch", "scenes": []},
        "generate_karaoke_captions": {"action": "generate_karaoke_captions", "text": "hello world"},
        "publish_content_campaign": {"action": "publish_content_campaign", "video_path": ""},
        "generate_viral_thread": {"action": "generate_viral_thread", "topic": "x"},
        "generate_pod_mockup": {
            "action": "generate_pod_mockup",
            "artwork_path": str(art),
            "preset": "tshirt_front",
        },
        "scout_affiliate_offers": {"action": "scout_affiliate_offers"},
        "analyze_pod_trends": {"action": "analyze_pod_trends"},
        "aggregate_growth_metrics": {"action": "aggregate_growth_metrics", "revenue": 100.0, "costs": 10.0},
        "setup_antidetect_profile": {
            "action": "setup_antidetect_profile", "account_name": "a", "platform": "threads",
        },
        "humanize_text": {"text": "Delve into the cutting edge landscape of things."},
        "enhance_video_prompt": {"idea": "cyberpunk server room", "options": {"camera_move": "dolly_in"}},
        "build_release_pack": {
            "title": "T", "copy_text": "Delve into it.", "video_idea": "v", "evidence_context": "e",
        },
        "floor3_query": {}, "floor4_query": {}, "floor5_query": {}, "floor6_query": {},
        "quant_signal": {"symbol": "BTC/USDT", "entry": 100.0, "stop_loss": 90.0, "take_profit": 130.0},
        "evaluate_setup": {"symbol": "BTC/USDT", "entry": 100.0, "stop_loss": 90.0},
        "trade_decision": {"callback_data": "approve_abc123"},
        "portfolio_review": {},
        "portfolio_risk": {"symbol": "BTCUSDT", "open_positions": []},
        "swarm_research_sam": {"query": "macro"},
        "morning_data_sam": {"action": "morning_data"},
        "socratic_dialogue": {"topic": "t", "statement": "s"},
        "lesson_plan": {"goal": "g"},
        "mentor_code_review": {"code": "def f(): pass"},
        "language_practice": {},
        "history_synthesis": {"query": "Rome"},
        "vibecoding_session": {"concept": "c"},
        "micro_quiz": {"topic": "asyncio"},
        "academy_overview": {"action": "academy_overview"},
        "morning_data_kira": {"action": "morning_data"},
        "kira_socratic_next": {
            "session_id": "s1", "user_message": "help", "problem_statement": "p", "solution": "s",
        },
        "kira_socratic_solve": {"session_id": "s1", "problem_statement": "p", "solution": "s"},
        "analyze_document": {"text": "doc text"},
        "summarize": {"content": "some content"},
        "morning_readiness": {
            "hrv_ms": 65, "sleep_hours": 7.5, "sleep_quality": 85,
            "resting_hr": 60, "steps_yesterday": 9000, "stress_score": 30,
        },
        "training_protocol": {"readiness_score": 80},
        "nutrition_plan": {"weight_kg": 80, "height_cm": 180, "age": 30, "sex": "male"},
        "biomarker_trend": {"biomarkers": [{"name": "ferritin", "value": 100}]},
        "screening_calendar": {"age": 40, "last_checkups": {}},
        "emergency_card": {},
        "compliance_check": {"protocol_items": [{"name": "x", "actual_completed": True}]},
        "nervous_system": {"hrv_ms": 40, "stress_score": 70, "sleep_quality": 50},
        "swarm_research_doc": {"query": "q"},
        "morning_data_doc": {"hrv_ms": 65},
        "chat": {"message": "hello"},
        "webhook_telegram": {"message": "hello"},
        "weekly_review": {"action": "weekly_review"},
        "record_decision": {"decision": "d", "reasoning": "r", "expected_outcome": "o"},
        "deadline_check": {"deadlines": [{"title": "t", "due_date": "2030-01-01"}]},
        "social_pulse": {"contacts": []},
        "morning_data_eva": {"action": "morning_data"},
        "office_lookup": {"query": "sumifs"},
        "generate_macro": {"macro_type": "clean_and_trim"},
        "create_excel_report": {"title": "T", "output_path": str(tmp_path / "probe.xlsx")},
        "create_word_document": {"title": "T", "output_path": str(tmp_path / "probe.docx")},
        "financial_analysis": {"data": {"a": 1}},
        "fin_runway": {"cash_balance": 1000.0, "monthly_burn": 100.0},
        "fin_budget_check": {"amount": 100.0},
        "fin_tax_radar": {},
        "fin_sync_bank": {"accounts": [{"balance": 10.0, "currency": "UAH"}]},
        "morning_data_fin": {},
        "fin_report": {"period": "monthly"},
        "marshal_execute": {"action": "security_audit"},
        "morning_data_marshal": {},
        "security_audit": {},
        "security_status": {},
        "incident_report": {"limit": 5},
        "emergency_lockdown": {"reason": "probe"},
        "design_workflow": {"name": "W", "trigger": "webhook"},
        "lint_workflow": {"workflow": {"nodes": [], "connections": {}}},
        "golden_template": {"name": "list"},
        "generate_adr": {"title": "T"},
        "review_code": {"code": "def f(): pass"},
        "generate_ui_scaffold": {"framework": "nextjs"},
        "gitops_sync": {"workflow_name": "w", "workflow_json": {}, "adr": {}},
        "drift_detect": {"live_workflows": []},
        "verify_code": {"code": "def f():\n    return 1\n"},
        "self_healing_generate": {"specification": "do a thing", "max_retries": 2},
        "morning_data_architect": {},
        "security_check": {"task_type": "chat", "payload": {"message": "hi"}},
        "sentinel_command_safety": {"command": "git status"},
        "sentinel_lethal_trifecta": {
            "reads_private_data": True,
            "processes_untrusted_input": True,
            "initiates_external_communication": True,
        },
        "sentinel_slopsquatting": {"package_name": "requsts"},
        "sentinel_scan_secrets": {"output": "key sk-ant-abcdefghijklmnopqrstuvwx"},
        "council_deliberate": {"question": "q", "options": ["A", "B"]},
        "orc_verify": {"claim": "c", "evidence": "e"},
        "submit_change_request": {
            "title": "T", "description": "d",
            "target_path": "wiki/probe.md", "proposed_content": "# P",
        },
        "review_change_request": {"cr_id": None, "decision": "approve"},
        "apply_change_request": {"cr_id": None},
        "parse_memory_command": {"text": "Запиши думку: probe"},
        "vault_write_ground_truth": {"path": "wiki/probe1.md", "content": "# P1"},
        "vault_read_ground_truth": {"path": "wiki/probe1.md"},
        "vault_reindex": {},
        "floors_overview": {},
    }


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def routed_task_types() -> List[str]:
    from src.orchestrator import EvaOrchestrator

    return sorted(EvaOrchestrator.TASK_ROUTING)


@pytest.fixture(scope="module")
def harness(tmp_path_factory):
    """One orchestrator for the whole module — initialisation is expensive."""
    from src.agents.sentinel import SentinelAgent
    from src.confidence import ConfidenceBudget
    from src.error_collector import ErrorCollector
    from src.lessons import LessonsStore
    from src.memory import MemoryManager
    from src.orchestrator import EvaOrchestrator
    from src.pii import PIIRedactor

    tmp = tmp_path_factory.mktemp("task_types")
    log: List[str] = []

    mem = MemoryManager(
        postgres_dsn="postgresql+asyncpg://localhost/test",
        redis_url="redis://localhost:6379/0",
    )
    mem._session_factory = lambda: MockAsyncSession(log)

    llm = MockLLM()
    orch = EvaOrchestrator(
        memory_manager=mem,
        sentinel=SentinelAgent(),
        llm_config={},
        config={"vault_root": str(tmp / "vault")},
        lessons_store=LessonsStore(session_factory=lambda: MockAsyncSession(log)),
        confidence_budget=ConfidenceBudget(),
        pii_redactor=PIIRedactor(),
        error_collector=ErrorCollector(),
    )
    orch._llm = llm
    orch._llm_fast = llm
    orch._llm_reasoning = llm

    asyncio.run(orch.initialize())

    class Harness:
        orchestrator = orch
        payloads = _payloads(tmp)
        cr_id: Optional[str] = None

    return Harness()


def _build_payload(harness, task_type: str) -> Dict[str, Any]:
    payload = dict(harness.payloads.get(task_type, {}))
    if task_type in PRESEED:
        # A fresh CR per call: ``apply`` moves it to "applied", so a shared id
        # would make ``review`` fail with ``not_pending`` depending on order.
        seed = asyncio.run(harness.orchestrator.execute("submit_change_request", {
            "title": f"Seed for {task_type}",
            "description": "seed CR",
            "target_path": "wiki/seed.md",
            "proposed_content": "# Seed\n",
        }))
        payload["cr_id"] = (seed.get("result") or {}).get("cr_id")
    return payload


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────
def test_every_task_type_is_covered(routed_task_types):
    declared = set(_payloads(Path("/tmp")))
    missing = [t for t in routed_task_types if t not in declared]
    assert not missing, f"no probe payload for task type(s): {missing}"


@pytest.mark.parametrize("task_type", sorted(_payloads(Path("/tmp"))))
def test_task_type_routes_cleanly(harness, task_type: str):
    orch = harness.orchestrator
    payload = _build_payload(harness, task_type)

    result = asyncio.run(orch.execute(task_type, payload))

    assert isinstance(result, dict), f"{task_type}: orchestrator returned {type(result)}"
    assert result.get("status") == "completed", f"{task_type}: {result}"

    # A non-serialisable value here used to surface as an HTTP 500.
    json.dumps(result, default=str)

    body = result.get("result")
    if isinstance(body, dict):
        err = body.get("error")
        if err and task_type not in EXPECTED_ERROR_RESULTS:
            pytest.fail(f"{task_type} answered with an error: {err}")
        if task_type in EXPECTED_ERROR_RESULTS:
            assert body.get("status") == "error", f"{task_type}: expected a clean error, got {body}"


def test_split_audio_result_contains_no_raw_bytes(harness):
    result = asyncio.run(harness.orchestrator.execute(
        "sensory_split_audio", {"audio_bytes": b"\x00" * 10, "filename": "a.ogg"}
    ))
    body = result.get("result") or {}
    for chunk in body.get("chunks", []):
        assert not any(isinstance(v, (bytes, bytearray)) for v in chunk.values())


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
