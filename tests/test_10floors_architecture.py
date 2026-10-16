"""
SYNDICATE — 10-Floor Comprehensive Sandbox Verification Suite
Tests all 10 floors of the Syndicate architecture:
- Floor 1: Server & n8n (SensoryRouter, ErrorCollector, n8n templates, ProactiveScheduler)
- Floor 2: Content Factory (Floor2Coordinator, Humanizer, VideoPromptEnhancer, ReleasePackBuilder)
- Floors 3-6: Reserved Floors (Single Source of Truth verification, graceful routing)
- Floor 7: Quant & Capital (SamAgent, ConfluenceEngine, strict HITL)
- Floor 8: SYNDICATE Academy (KiraAgent, SocraticTutor 4-stage hint ladder)
- Floor 9: Health & Energy (DocAgent, morning readiness index, Mifflin-St Jeor, emergency card)
- Floor 10: Command Floor (Eva, Fin, Marshal, Architect, Sentinel Zero-Trust, Council, OrcVerifier, ChangeRequests, Vault, MemoryCommands)
- Integration: FastAPI agent runner, HMAC webhooks, Cockpit UI, Specialized endpoints.
"""

from __future__ import annotations

import ast
import asyncio
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Isolate every artefact the suite writes. Previously the tests wrote straight
# into the tracked ``scratch/`` directory, so each run left the repository dirty
# and successive runs were not idempotent (thoughts.md grew one line per run).
import atexit
import shutil
import tempfile

SANDBOX_DIR = Path(tempfile.mkdtemp(prefix="eva_10floors_"))
atexit.register(lambda: shutil.rmtree(SANDBOX_DIR, ignore_errors=True))
os.environ["EVA_DATA_DIR"] = str(SANDBOX_DIR / "data")

# Locate repo root cleanly
_this_file = Path(__file__).resolve()
if (_this_file.parent / "src").exists():
    REPO_PATH = _this_file.parent
elif (_this_file.parent.parent / "src").exists():
    REPO_PATH = _this_file.parent.parent
elif (_this_file.parent.parent / "repo_code" / "src").exists():
    REPO_PATH = _this_file.parent.parent / "repo_code"
else:
    REPO_PATH = Path("repo_code").resolve()

sys.path.insert(0, str(REPO_PATH))
sys.path.insert(0, str(REPO_PATH / "deploy" / "runtime"))

# Directories that must never be scanned/imported by the suite (virtualenvs,
# vendored dependencies, caches). Scanning them produced >10k third-party files
# and crashed the suite on unrelated upstream syntax errors.
_SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", "site-packages",
    "dist", "build", ".eggs",
}


def discover_python_files(root: Path) -> List[Path]:
    """Return every first-party ``*.py`` file under ``root``."""
    found: List[Path] = []
    for path in root.rglob("*.py"):
        if any(part in _SKIP_DIRS for part in path.relative_to(root).parts[:-1]):
            continue
        found.append(path)
    return sorted(found)


# ─── Mock Fixtures for Sandbox Isolation ─────────────────────────────────────

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
    def __init__(self, query_log: List[Dict[str, Any]]):
        self.query_log = query_log

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def execute(self, stmt, params=None):
        sql_str = str(stmt)
        if "::vector" in sql_str and ":embedding::vector" in sql_str:
            raise RuntimeError(f"SQL Syntax Bug Detected: :embedding::vector in {sql_str}")
        if "INTERVAL ':ttl_hours" in sql_str:
            raise RuntimeError(f"SQL Syntax Bug Detected: quoted :ttl_hours in {sql_str}")
        self.query_log.append({"sql": sql_str, "params": params or {}})
        return MockResult(rows=[], scalar_val=0)

    async def commit(self):
        pass


class MockLLMResponse:
    def __init__(self, content: str):
        self.content = content


class MockReasoningLLM:
    """Mock LLM supporting Council, Verifier, and Agent operations deterministically."""
    def __init__(self):
        self.call_count = 0

    async def ainvoke(self, messages):
        self.call_count += 1
        if isinstance(messages, str):
            prompt_text = messages
        elif isinstance(messages, list):
            prompt_text = "\n".join(getattr(m, "content", str(m)) for m in messages)
        else:
            prompt_text = getattr(messages, "content", str(messages))

        # Check for Council options prompt
        if "Answer with exactly one of:" in prompt_text:
            import re
            m = re.search(r"Answer with exactly one of:\s*([^,\n]+)", prompt_text)
            if m:
                first_opt = m.group(1).strip()
                return MockLLMResponse(f"{first_opt}. Optimal consensus decision.")

        # Self-healing code generation
        if "Compiler-in-the-Loop" in prompt_text or "Write production-ready async Python code" in prompt_text:
            if "PREVIOUS ATTEMPT FAILED" not in prompt_text:
                return MockLLMResponse(
                    "```python\n"
                    "async def broken_agent_step(memory, llm):\n"
                    "    res = await llm.generate(['hello'])\n"
                    "    await memory.save_episode(session_id='123', agent_id='doc', role='assistant', content='hi', category='bad_arg')\n"
                    "    return res\n"
                    "```"
                )
            else:
                return MockLLMResponse(
                    "```python\n"
                    "async def healed_agent_step(memory, llm):\n"
                    "    res = await llm.ainvoke(['hello'])\n"
                    "    await memory.save_episode(session_id='123', agent_id='doc', role='assistant', content=res.content, metadata={'category': 'fixed'})\n"
                    "    return res.content\n"
                    "```"
                )

        # Orc verifier response
        if "OrcVerifier" in prompt_text or "adversarial factual verification" in prompt_text:
            return MockLLMResponse(json.dumps({
                "verdict": "verified",
                "factual_score": 0.95,
                "confidence": 0.92,
                "hallucinations": [],
                "unsupported_claims": [],
                "reasoning": "Claim is fully supported by evidence provided."
            }))

        # LLM Council deliberation response
        if "deliberate" in prompt_text.lower() or "council" in prompt_text.lower():
            return MockLLMResponse(json.dumps({
                "recommendation": "Deploy new cluster configuration",
                "confidence": 0.94,
                "rationale": "High consensus among nodes and minimal systemic risk."
            }))

        # Default structured JSON
        return MockLLMResponse(json.dumps({
            "summary": "Sandbox 10-floor verified response",
            "status": "ok",
            "confidence": 0.95,
            "response": "SYNDICATE 10-floor operational readiness verified.",
            "recommendation": "Option A",
            "findings": ["Subsystem normal", "Telemetry optimal"],
            "claims": [{"claim": "Test claim", "confidence": 0.95}],
            "verified_facts": ["Fact 1 verified"],
            "synthesis": "High confidence synthesis across 10 floors.",
        }))


# ─── Main Sandbox Suite ──────────────────────────────────────────────────────

async def run_10floors_sandbox_suite():
    print("=" * 76)
    print("🚀 SYNDICATE — 10-FLOOR SANDBOX ARCHITECTURE VERIFICATION SUITE")
    print("=" * 76)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: AST & Compilation Integrity across ALL Python files
    # ─────────────────────────────────────────────────────────────────────────
    py_files = discover_python_files(REPO_PATH)
    assert py_files, f"No first-party Python files discovered under {REPO_PATH}"
    print(f"\n[1/10] Checking AST syntax & compilation of all {len(py_files)} Python files...")
    for f in py_files:
        rel = f.relative_to(REPO_PATH)
        source = f.read_text(encoding="utf-8")
        ast.parse(source, filename=str(rel))
    print(f"  ✅ All {len(py_files)} Python files parsed cleanly with 0 SyntaxErrors.")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: Floor 1 — Server & n8n Verification
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[2/10] Testing Floor 1: Server & n8n (SensoryRouter, ErrorCollector, n8n templates, ProactiveScheduler)...")
    from src.sensory import SensoryRouter
    from src.error_collector import ErrorCollector
    from src.n8n_templates import (
        build_sensory_switch_workflow,
        build_error_handler_workflow,
        build_cron_briefing_workflow,
        build_evening_reflection_workflow,
    )
    from src.proactive import ProactiveScheduler, cron_matches

    # 2a. Sensory Router: Whisper audio splitting (<25MB chunks)
    router = SensoryRouter(max_audio_chunk_bytes=1000)
    fake_audio = b"\x00" * 3500
    chunks = router.split_audio_for_whisper(fake_audio, filename="voice.ogg")
    assert len(chunks) == 4, f"Expected 4 chunks, got {len(chunks)}"
    assert all(c["size"] <= 1000 for c in chunks)

    # 2b. Sensory Router: Document extraction & Chunking
    txt_bytes = b"Hello SYNDICATE. This is a ground truth document test.\n\nParagraph two with key facts."
    extracted_text, meta = router.extract_document(txt_bytes, filename="test.txt")
    assert "SYNDICATE" in extracted_text and meta["type"] == "txt"

    text_chunks = router.chunk_for_embedding(extracted_text, chunk_size=30, overlap=5)
    assert len(text_chunks) >= 2

    # 2c. Sensory Router: Telegram 4096-char splitter
    long_msg = "A" * 9000
    split_msgs = router.split_telegram_message(long_msg)
    assert len(split_msgs) == 3
    assert all(len(m) <= 4096 for m in split_msgs)

    # 2d. Error Collector (DLQ with SHA-256 fingerprinting & PII redaction)
    err_collector = ErrorCollector()
    res1 = await err_collector.record_error(
        source="n8n_workflow_checkout",
        error_message="Payment failed for user user@example.com with phone +380501234567",
        payload={"order_id": 999, "customer_email": "user@example.com"},
        severity="error",
    )
    assert res1["status"] == "recorded"
    assert "user@example.com" not in res1["fingerprint_summary"]  # PII redacted!

    # Test deduplication of identical error
    res2 = await err_collector.record_error(
        source="n8n_workflow_checkout",
        error_message="Payment failed for user user@example.com with phone +380501234567",
        payload={"order_id": 999, "customer_email": "user@example.com"},
        severity="error",
    )
    assert res2["status"] == "deduplicated"
    assert res2["occurrences"] == 2

    recent_errors = err_collector.get_recent_errors(limit=5)
    assert len(recent_errors) == 1 and recent_errors[0]["occurrences"] == 2

    # 2e. n8n Templates (FlowLint verified workflows)
    wf_sensory = build_sensory_switch_workflow()
    wf_error = build_error_handler_workflow()
    wf_briefing = build_cron_briefing_workflow()
    wf_evening = build_evening_reflection_workflow()

    assert "nodes" in wf_sensory and "connections" in wf_sensory
    assert any("telegramTrigger" in n["type"] or "webhook" in n["type"] for n in wf_sensory["nodes"])
    assert any("30 7 * * *" in str(n.get("parameters", {})) for n in wf_briefing["nodes"])
    assert any("0 21 * * *" in str(n.get("parameters", {})) for n in wf_evening["nodes"])

    # The error-handler template must actually route failures to the DLQ endpoint.
    assert "nodes" in wf_error and "connections" in wf_error
    assert any("errorTrigger" in n["type"] for n in wf_error["nodes"])
    assert "/webhook/error" in json.dumps(wf_error)

    # 2f. The prepared, dormant Eva-only 03:00 Kyiv cron contract is the sole default job.
    scheduler = ProactiveScheduler()
    assert {j.name for j in scheduler.jobs} == {"nightly_analysis"}
    t_0300 = datetime(2026, 10, 4, 3, 0)
    t_0730 = datetime(2026, 10, 4, 7, 30)
    assert cron_matches("0 3 * * *", t_0300)
    assert cron_matches("30 7 * * *", t_0730)
    assert [job.name for job in scheduler.due(t_0300)] == ["nightly_analysis"]
    assert scheduler.due(t_0730) == []
    print("  ✅ Floor 1 (Sensory Router, Dead Letter Queue, n8n FlowLint Workflows, Proactive Cron) verified!")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: Floor 2 — Operations & Content Factory
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[3/10] Testing Floor 2: Content Factory (Humanizer, VideoPromptEnhancer, ReleasePackBuilder, POD, Growth)...")
    from src.departments.content_factory.humanizer import Humanizer
    from src.departments.content_factory.video_prompt_enhancer import VideoPromptEnhancer
    from src.departments.content_factory.release_pack import ReleasePackBuilder
    from src.departments.coordinator import Floor2Coordinator

    # 3a. Humanizer: AI-cliché detection & scrubbing
    humanizer = Humanizer()
    robotic_text = (
        "In today's fast-paced digital landscape, it is a testament to innovation that we delve into "
        "cutting-edge paradigms. Furthermore, this is a game-changer."
    )
    h_res = humanizer.humanize(robotic_text)
    assert h_res["original_robotic_score"] >= 30
    assert len(h_res["clichés_detected"]) >= 3
    assert "game-changer" in [c["cliché"] for c in h_res["clichés_detected"]]
    assert h_res["scrubbed_score"] < h_res["original_robotic_score"]

    # 3b. VideoPromptEnhancer: Google Veo 3 / Kling AI cinematic prompt
    video_enhancer = VideoPromptEnhancer()
    v_res = video_enhancer.enhance(
        idea="A futuristic command center in Kyiv with holographic spheres",
        camera_move="dolly_in",
        lighting="cyberpunk_neon",
        lens="anamorphic_35mm",
    )
    assert "dolly in" in v_res["prompt"].lower() or "dolly" in v_res["prompt"].lower()
    assert "cyberpunk neon" in v_res["prompt"].lower() or "neon" in v_res["prompt"].lower()
    assert "watermark" in v_res["negative_prompt"].lower()

    # 3c. ReleasePackBuilder: combines humanizer + video enhancer + Orc verifier
    mock_llm = MockReasoningLLM()
    from src.verifier import OrcVerifier
    from src.change_requests import ChangeRequestStore
    from src.vault_md import MarkdownVault

    test_vault = MarkdownVault(vault_root=str(SANDBOX_DIR / "test_vault"))
    cr_store = ChangeRequestStore(vault=test_vault)
    orc = OrcVerifier(llm=mock_llm)

    pack_builder = ReleasePackBuilder(
        humanizer=humanizer,
        video_enhancer=video_enhancer,
        verifier=orc,
        cr_store=cr_store,
    )
    pack_res = await pack_builder.build({
        "title": "Autonomous Syndicate Launch Briefing",
        "copy_text": "Delve into the game-changer revolution in AI agent systems.",
        "video_idea": "Cyberpunk server racks pulsing with blue light",
        "evidence_context": "SYNDICATE release specifications v4.1.",
        "submit_cr": True,
    })
    assert pack_res["status"] == "ok"
    assert "humanized_copy" in pack_res
    assert "video_prompt" in pack_res
    assert pack_res["verification"]["verdict"] in ("verified", "factual")
    assert pack_res["change_request"]["cr_id"].startswith("CR-")

    # 3d. Floor2Coordinator POD & growth operations
    coord = Floor2Coordinator()
    pod_res = await coord.execute({
        "action": "generate_pod_mockup",
        "artwork_path": str(SANDBOX_DIR / "sandbox_art.png"),
        "preset": "tshirt_front",
    })
    assert pod_res["status"] == "ok"

    # Sentinel IP Trademark Veto check
    veto_pod = await coord.execute({
        "action": "generate_pod_mockup",
        "artwork_path": "media/art/disney_mickey_hoodie.png",
        "preset": "hoodie_chest",
    })
    assert veto_pod["status"] == "veto_blocked"
    print("  ✅ Floor 2 (Humanizer, Video Prompt Enhancer, Release Pack Builder, POD Mockup, Trademark Veto) verified!")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: Floors 3-6 — Reserved Floors
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[4/10] Testing Floors 3-6: Reserved Floors (Single Source of Truth & Graceful Routing)...")
    from src.floors import FLOORS, reserved_floors, floor_of

    assert reserved_floors() == [3, 4, 5, 6]
    assert all(FLOORS[f]["status"] == "reserved" for f in [3, 4, 5, 6])
    assert all(len(FLOORS[f]["agents"]) == 0 for f in [3, 4, 5, 6])
    assert floor_of("doc") == 9
    assert floor_of("kira") == 8
    assert floor_of("sam") == 7
    print("  ✅ Floors 3-6 (Explicitly Reserved Single Source of Truth Registry) verified!")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 5: Floor 7 — Quant & Capital (Sam)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[5/10] Testing Floor 7: Quant & Capital (SamAgent, ConfluenceEngine, strict HITL)...")
    from src.agents.sam import SamAgent

    mock_query_log = []
    from src.memory import MemoryManager
    mem = MemoryManager(postgres_dsn="postgresql+asyncpg://localhost/test", redis_url="redis://localhost:6379/0")
    mem._session_factory = lambda: MockAsyncSession(mock_query_log)

    sam = SamAgent(memory=mem, llm=mock_llm, config={"max_drawdown_pct": 5.0, "risk_per_trade_pct": 1.0})
    sam_eval = await sam.execute({
        "action": "evaluate_setup",
        "asset": "BTC/USDT",
        "signals": [
            {"source": "trend_ema", "direction": "long", "score": 85},
            {"source": "orderflow_cvd", "direction": "long", "score": 80},
            {"source": "liquidity_sweep", "direction": "long", "score": 90},
        ],
    })
    assert "confluence" in sam_eval and sam_eval.get("requires_hitl") is True
    assert sam_eval.get("auto_execute") is False
    print("  ✅ Floor 7 (Sam Quant Confluence, Capital Risk Gate, strict HITL Enforcement) verified!")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 6: Floor 8 — SYNDICATE Academy (Kira)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[6/10] Testing Floor 8: SYNDICATE Academy (KiraAgent, SocraticTutor 4-stage hint ladder)...")
    from src.agents.kira import KiraAgent
    from src.agents.kira_socratic import SocraticTutor

    kira = KiraAgent(memory=mem, llm=mock_llm)
    academy_info = await kira.execute({"action": "academy_overview"})
    assert academy_info["status"] == "ok"
    assert "disciplines" in academy_info and len(academy_info["disciplines"]) >= 4

    # Socratic Tutor: 4-stage hint ladder
    tutor = SocraticTutor()
    session_id = "test_socratic_session_01"
    prob = "Implement an async queue worker with error backoff in Python."
    sol = "Use asyncio.Queue, async for, and exponential backoff with asyncio.sleep."

    # Stage 1: Clarify (no attempt yet)
    h1 = tutor.next_hint(session_id, user_message="Help", problem_statement=prob, solution=sol)
    assert h1["stage"] == "clarify" and h1["stage_index"] == 1
    assert "exponential backoff" not in h1["hint"]  # Does not reveal solution!

    # Stage 2: Nudge (attempt 1)
    h2 = tutor.next_hint(session_id, user_message="My first attempt at writing the queue loop", problem_statement=prob, solution=sol)
    assert h2["stage"] == "nudge" and h2["stage_index"] == 2

    # Stage 3: Scaffold (attempt 2)
    h3 = tutor.next_hint(session_id, user_message="My second attempt adding sleep retry backoff", problem_statement=prob, solution=sol)
    assert h3["stage"] == "scaffold" and h3["stage_index"] == 3

    # Attempt 3: real attempt
    _ = tutor.next_hint(session_id, user_message="My third attempt with try catch exception block", problem_statement=prob, solution=sol)

    # Stage 4: Reveal (after 3 real attempts, asking for answer)
    h4 = tutor.next_hint(session_id, user_message="I have tried 3 times, give me the solution now", problem_statement=prob, solution=sol)
    assert h4["stage"] == "reveal" and h4["stage_index"] == 4
    assert "exponential backoff" in h4["hint"]

    # Solve finishes the ladder
    solve_res = tutor.solve(session_id, problem_statement=prob, solution=sol)
    assert solve_res["status"] == "solved"
    print("  ✅ Floor 8 (Kira Academy, Socratic Tutor 4-Stage Hint Ladder, Shortcut Prevention) verified!")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 7: Floor 9 — Health & Energy (Doc)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[7/10] Testing Floor 9: Health & Energy (DocAgent, morning readiness, Mifflin-St Jeor TDEE, emergency card)...")
    from src.agents.doc import DocAgent

    doc = DocAgent(memory=mem, llm=mock_llm)

    # 7a. Deterministic morning readiness score
    readiness = await doc.execute({
        "action": "morning_readiness",
        "hrv_ms": 72,
        "sleep_hours": 8.0,
        "sleep_quality": 90,
        "resting_hr": 58,
        "steps_yesterday": 11000,
        "stress_score": 25,
    })
    assert readiness["score"] >= 80
    assert readiness["zone"] == "green"
    assert readiness["recommended_intensity"] in ("intense", "moderate")

    # 7b. Real Mifflin-St Jeor TDEE calculation
    nutrition = await doc.execute({
        "action": "nutrition_plan",
        "weight_kg": 80,
        "height_cm": 182,
        "age": 30,
        "sex": "male",
        "goal": "maintenance",
        "activity_level": "moderate",
    })
    assert 2000 < nutrition["calories"] < 3200
    assert nutrition["protein_g"] > 120
    assert nutrition["water_ml"] >= 2000

    # 7c. Emergency Medical Card
    med_card = await doc.execute({"action": "emergency_card"})
    assert "blood_type" in med_card or "emergency_contacts" in med_card

    # 7d. Nervous system stress recovery protocol (veteran context)
    nervous = await doc.execute({
        "action": "nervous_system",
        "hrv_ms": 40,
        "stress_score": 75,
        "sleep_quality": 50,
    })
    assert "breathing_exercise" in nervous and "grounding_exercise" in nervous
    print("  ✅ Floor 9 (Doc Morning Readiness, Mifflin-St Jeor Nutrition, Emergency Card, Stress Recovery) verified!")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 8: Floor 10 — Command Floor & Security Services
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[8/10] Testing Floor 10: Command Floor (Sentinel Zero-Trust, Council, OrcVerifier, ChangeRequests, Vault, Memory)...")
    from src.agents.sentinel import SentinelAgent
    from src.council import LLMCouncil
    from src.change_requests import ChangeRequestStore
    from src.vault_md import MarkdownVault
    from src.memory_commands import parse_command, execute_command
    from src.agents.eva_curator import EvaCurator
    from src.agents.fin import FinAgent
    from src.agents.marshal import MarshalAgent

    # 8a. Sentinel Zero-Trust Protections
    sentinel = SentinelAgent()

    # Lethal Trifecta check: reading private data + untrusted external content + external communication
    trifecta_blocked = sentinel.check_lethal_trifecta({
        "reads_private_data": True,
        "processes_untrusted_input": True,
        "initiates_external_communication": True,
    })
    assert not trifecta_blocked["allowed"]
    assert "lethal trifecta" in trifecta_blocked["reason"].lower()

    # Destructive command safety check
    cmd_unsafe = sentinel.check_command_safety("rm -rf / --no-preserve-root")
    assert not cmd_unsafe["allowed"]
    cmd_safe = sentinel.check_command_safety("git status")
    assert cmd_safe["allowed"]

    # Slopsquatting check on suspicious packages
    slop_check = sentinel.assess_dependency_install("requsts")  # typo of requests
    assert slop_check["risk"] in ("medium", "high") or slop_check["is_slopsquatting"]

    # Secret leakage scan in output
    secret_scan = sentinel.scan_output_for_secrets("Here is the key: ghp_1234567890abcdef1234567890abcdef1234")
    assert secret_scan["has_secrets"]
    assert "[REDACTED_GH_TOKEN]" in secret_scan["redacted_output"]

    # 8b. LLM Council deliberation with Jaccard consensus
    council = LLMCouncil(llm=mock_llm, default_threshold=0.60)
    council_res = await council.deliberate(
        question="Should we migrate the pgvector cluster to AWS Aurora or dedicated bare-metal?",
        options=["Aurora Serverless v2", "Bare-metal dedicated with NVMe"],
    )
    assert council_res["quorum"] is True
    assert "chosen" in council_res

    # 8c. Orc Verifier (adversarial factual validation)
    orc_res = await orc.verify_claim(
        claim="SYNDICATE floor layout contains exactly 10 floors with floors 3-6 reserved.",
        evidence="floors.py specifies FLOORS dictionary with keys 1 to 10. Keys 3, 4, 5, 6 have status reserved.",
    )
    assert orc_res["verdict"] in ("verified", "factual")

    # 8d. ChangeRequestStore (Company-as-Code governance)
    vault_dir = SANDBOX_DIR / "test_statute_vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    statute_vault = MarkdownVault(vault_root=str(vault_dir))
    cr_store = ChangeRequestStore(vault=statute_vault)

    # Submit change request for protected statute
    cr = cr_store.submit(
        title="Update Syndicate Security Statute",
        description="Enforce Sentinel Zero-Trust outbound action block.",
        target_path="statutes/security.md",
        proposed_content="# Security Statute\n\nAll external actions require Sentinel approval.",
        author="Architect",
    )
    assert cr["status"] == "submitted" and cr["cr_id"].startswith("CR-")

    # Review & approve CR
    reviewed = cr_store.review(cr["cr_id"], decision="approve", reviewer="Marshal", comment="Approved for ops.")
    assert reviewed["status"] == "approved"

    # Apply CR to Ground Truth vault
    applied = cr_store.apply(cr["cr_id"])
    assert applied["status"] == "applied"
    assert statute_vault.exists("statutes/security.md")
    assert "Security Statute" in statute_vault.read("statutes/security.md")

    # 8e. Natural language Memory Commands parser & routing
    cmd_doc = parse_command("Запам'ятай мій пульс у спокої 58 уд/хв та вага 80 кг")
    assert cmd_doc.kind == "remember" and cmd_doc.target_agent == "doc"

    cmd_fin = parse_command("Онови про мене: бюджет на рекламу 500 USD")
    assert cmd_fin.kind == "update" and cmd_fin.target_agent == "fin"

    cmd_thought = parse_command("Запиши думку: розширити поверх 8 курсом по агентам")
    assert cmd_thought.kind == "thought" and cmd_thought.target_agent == "eva"

    thought_res = execute_command(cmd_thought, statute_vault)
    assert thought_res["status"] == "thought_saved"
    assert statute_vault.exists("raw/thoughts.md")

    # 8f. Fin Agent (CFO) and Marshal Agent (COO)
    fin = FinAgent(memory=mem, llm=mock_llm)
    fin_runway = await fin.execute({"action": "runway", "cash_balance": 50000.0, "monthly_burn": 5000.0})
    assert fin_runway["runway_months"] == 10.0

    # 8f. Fin Agent (CFO) and Marshal Agent (CSO - Chief Security Officer commanding Sentinel)
    marshal = MarshalAgent(memory=mem, llm=mock_llm, sentinel=sentinel)
    marshal_audit = await marshal.execute({"action": "security_audit"})
    assert marshal_audit["role"] == "Chief Security Officer (CSO)"
    assert "Sentinel Protocol" in marshal_audit["protocol_status"]

    # Marshal enforces Sentinel Protocol on dangerous task
    marshal_check = await marshal.execute({"action": "validate_task", "task": {"task_type": "admin_override"}})
    assert not marshal_check["allowed"] and marshal_check["commander"] == "Marshal"

    # 8g. Eva Curator Life Review
    curator = EvaCurator(memory=mem, llm=mock_llm)
    dec_res = await curator.execute({
        "action": "record_decision",
        "decision": "Reserve floors 3-6 for future expansion",
        "reasoning": "Keep layout clean while specializations mature",
        "expected_outcome": "Zero namespace collision",
        "category": "architecture",
        "importance": "high",
    })
    assert dec_res["decision_id"] is not None
    print("  ✅ Floor 10 (Sentinel Trifecta/Slopsquatting, Council, OrcVerifier, ChangeRequests, Vault, Memory, Fin, Marshal, Curator) verified!")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 9: EvaOrchestrator LangGraph 10-Floor Coordination
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[9/10] Testing EvaOrchestrator 10-Floor Execution Graph & Proactive Briefings...")
    from src.orchestrator import EvaOrchestrator
    from src.confidence import ConfidenceBudget
    from src.pii import PIIRedactor
    from src.lessons import LessonsStore

    lessons = LessonsStore(session_factory=lambda: MockAsyncSession(mock_query_log))
    budget = ConfidenceBudget()
    pii = PIIRedactor()

    orchestrator = EvaOrchestrator(
        memory_manager=mem,
        sentinel=sentinel,
        llm_config={"openai_api_key": "test-key"},
        config={"vault_root": str(SANDBOX_DIR / "test_orch_vault")},
        lessons_store=lessons,
        confidence_budget=budget,
        pii_redactor=pii,
        markdown_vault=statute_vault,
        error_collector=err_collector,
        council=council,
        orc_verifier=orc,
        socratic_tutor=tutor,
        humanizer=humanizer,
        video_prompt_enhancer=video_enhancer,
        release_pack_builder=pack_builder,
    )
    orchestrator._llm = mock_llm
    orchestrator._llm_reasoning = mock_llm
    await orchestrator.initialize()

    # 9a. Test routing across various floors
    # Floor 1 sensory
    res_sensory = await orchestrator.execute("sensory_chunk_text", {"text": "Chunk test for Floor 1."})
    assert res_sensory["status"] == "completed" and res_sensory["result"]["status"] == "ok"

    # Floor 2 humanizer
    res_humanize = await orchestrator.execute("humanize_text", {"text": "Delve into the cutting-edge landscape."})
    assert res_humanize["status"] == "completed" and "scrubbed_text" in res_humanize["result"]

    # Floors 3-6 reserved query
    res_f4 = await orchestrator.execute("floor4_query", {})
    assert res_f4["status"] == "completed" and res_f4["result"]["status"] == "reserved"

    # Floor 7 Sam trade decision (strict HITL check)
    res_sam = await orchestrator.execute("trade_decision", {"action": "decision", "symbol": "BTC/USDT", "approved": False})
    assert res_sam["status"] == "completed"

    # Floor 8 Kira Socratic hint
    res_kira = await orchestrator.execute("kira_socratic_next", {
        "session_id": "orch_socratic",
        "user_message": "Need hint",
        "problem_statement": "Queue worker",
        "solution": "Use asyncio.Queue",
    })
    assert res_kira["status"] == "completed" and res_kira["result"]["stage"] == "clarify"

    # Floor 9 Doc readiness
    res_doc = await orchestrator.execute("morning_readiness", {
        "hrv_ms": 65, "sleep_hours": 7.5, "sleep_quality": 85, "resting_hr": 60, "steps_yesterday": 9000, "stress_score": 30
    })
    assert res_doc["status"] == "completed" and res_doc["result"]["zone"] == "green"

    # Floor 10 Council deliberation
    res_council = await orchestrator.execute("council_deliberate", {
        "question": "Release pack approval", "options": ["Approve", "Iterate"]
    })
    assert res_council["status"] == "completed" and res_council["result"]["quorum"] is True

    # 9b. Scheduled tasks do not dispatch other agents without precollected reports.
    morning_briefing = await orchestrator.proactive_daily_briefing()
    assert morning_briefing["status"] == "unavailable"
    assert morning_briefing["agent_tasks_dispatched"] is False

    evening_reflection = await orchestrator.proactive_evening_reflection()
    assert evening_reflection["status"] == "unavailable"
    assert evening_reflection["agent_tasks_dispatched"] is False
    print("  ✅ EvaOrchestrator (on-demand reports; no automatic agent dispatch) verified!")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 10: FastAPI Runtime & Specialized Endpoints Suite
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[10/10] Testing FastAPI Endpoints (Auth, HMAC, Cockpit, Specialized 10-Floor Routes)...")
    from fastapi.testclient import TestClient
    from agent_runner import app, app_state

    # Wire mocked app_state
    app_state.ready = True
    app_state.api_key = "sandbox-secret-api-key-2026"
    app_state.webhook_secret = "sandbox-webhook-hmac-secret"
    app_state.memory_manager = mem
    app_state.orchestrator = orchestrator
    app_state.sentinel = sentinel
    app_state.lessons_store = lessons
    app_state.confidence_budget = budget
    app_state.pii_redactor = pii

    client = TestClient(app)

    # 10a. Health probe (public)
    r_health = client.get("/health")
    assert r_health.status_code == 200 and r_health.json()["status"] == "healthy"

    # 10b. Cockpit UI requires a credential; the operator's master key works.
    assert client.get("/cockpit").status_code == 401
    r_cockpit = client.get("/cockpit", headers={"X-API-Key": "sandbox-secret-api-key-2026"})
    assert r_cockpit.status_code == 200
    assert "SYNDIKAT" in r_cockpit.text or "SYNDICATE" in r_cockpit.text
    print("  ✓ /cockpit read authentication verified (401 without key -> 200 with X-API-Key)")

    # 10c. Authentication check on /status
    r_unauth = client.get("/status")
    assert r_unauth.status_code == 401
    r_auth = client.get("/status", headers={"X-API-Key": "sandbox-secret-api-key-2026"})
    assert r_auth.status_code == 200 and r_auth.json()["ready"] is True
    print("  ✓ /status authentication verified (401 without key -> 200 with X-API-Key)")

    # 10d. Webhook HMAC verification on /webhook/telegram
    body_bytes = json.dumps({"task_type": "chat", "payload": {"message": "Signed message"}}).encode()
    valid_sig = hmac.new(b"sandbox-webhook-hmac-secret", body_bytes, hashlib.sha256).hexdigest()

    r_bad_hmac = client.post("/webhook/telegram", content=body_bytes, headers={"X-Webhook-Signature": "invalid_sig"})
    assert r_bad_hmac.status_code == 401
    r_good_hmac = client.post("/webhook/telegram", content=body_bytes, headers={"X-Webhook-Signature": valid_sig})
    assert r_good_hmac.status_code == 200 and r_good_hmac.json()["ok"] is True
    print("  ✓ /webhook/telegram HMAC authentication verified (401 on bad HMAC -> 200 on valid)")

    # 10e. Specialized 10-floor endpoints; registry is read-scope protected.
    # /floors
    assert client.get("/floors").status_code == 401
    r_floors = client.get("/floors", headers={"X-API-Key": "sandbox-secret-api-key-2026"})
    assert r_floors.status_code == 200
    floors_data = r_floors.json()
    assert len(floors_data["active"]) == 6 and len(floors_data["reserved"]) == 4

    # /sensory/chunk
    r_sensory = client.post(
        "/sensory/chunk",
        json={"text": "Sensory chunk test through FastAPI endpoint."},
        headers={"X-API-Key": "sandbox-secret-api-key-2026"},
    )
    assert r_sensory.status_code == 200 and r_sensory.json()["status"] == "completed"

    # /webhook/error (Dead letter queue)
    r_err_wh = client.post("/webhook/error", json={"source": "n8n_test", "error_message": "Test webhook error"})
    assert r_err_wh.status_code == 200 and r_err_wh.json()["ok"] is True

    # /proactive/morning
    r_morning = client.post("/proactive/morning", headers={"X-API-Key": "sandbox-secret-api-key-2026"})
    assert r_morning.status_code == 200 and r_morning.json()["ok"] is True

    # /proactive/evening
    r_evening = client.post("/proactive/evening", headers={"X-API-Key": "sandbox-secret-api-key-2026"})
    assert r_evening.status_code == 200 and r_evening.json()["ok"] is True

    # /council
    r_council = client.post(
        "/council",
        json={"question": "Deliberate endpoint test", "options": ["A", "B"]},
        headers={"X-API-Key": "sandbox-secret-api-key-2026"},
    )
    assert r_council.status_code == 200 and r_council.json()["status"] == "completed"

    # /cr/submit
    r_cr = client.post(
        "/cr/submit",
        json={"title": "Endpoint CR Test", "target_path": "statutes/test.md", "proposed_content": "# Test"},
        headers={"X-API-Key": "sandbox-secret-api-key-2026"},
    )
    assert r_cr.status_code == 200 and r_cr.json()["result"]["cr_id"].startswith("CR-")
    print("  ✅ FastAPI 10-Floor Specialized Endpoints (/floors, /sensory, /error, /proactive, /council, /cr) verified!")

    print("\n" + "=" * 76)
    print("🏆 ALL 10 SUITES FOR ALL 10 FLOORS PASSED WITH ZERO ERRORS!")
    print("=" * 76)


if __name__ == "__main__":
    asyncio.run(run_10floors_sandbox_suite())
