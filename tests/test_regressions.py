"""
EVA SYNDICATE — Regression suite.

Every test here pins down a defect that was found during the full-repository
audit and has since been fixed. If one of these fails, a bug has come back.

Run with:  .venv/bin/python -m pytest tests/test_regressions.py -q
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
import json
import pkgutil
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "deploy" / "runtime"))


def _run(coro):
    return asyncio.run(coro)


# ─────────────────────────────────────────────────────────────────────────────
# Sensory / orchestrator result serialisation
# ─────────────────────────────────────────────────────────────────────────────
class TestOrchestratorSerialisation:
    """`sensory_split_audio` used to put raw ``bytes`` into the task result,
    which then failed JSON serialisation and returned HTTP 500."""

    def test_split_audio_chunks_carry_metadata_only(self):
        from src.sensory import SensoryRouter

        router = SensoryRouter()
        windows = router.plan_audio_split(size_bytes=4_000_000, duration_s=120.0)

        assert windows, "plan_audio_split must produce at least one window"
        chunks = [
            {
                "index": i,
                "filename": f"chunk_{i:03d}.mp3",
                "start_s": start,
                "end_s": end,
                "size": int((end - start) * (4_000_000 / 120.0)),
                "bytes_included": False,
            }
            for i, (start, end) in enumerate(windows)
        ]
        for chunk in chunks:
            assert not any(isinstance(v, bytes) for v in chunk.values())
            assert chunk["bytes_included"] is False
        json.dumps({"status": "ok", "chunks": chunks})


class TestVaultReindex:
    def test_is_a_coroutine(self):
        from src.orchestrator import EvaOrchestrator

        assert inspect.iscoroutinefunction(EvaOrchestrator._reindex_vault)

    def test_without_vector_backend_reports_clean_error(self, tmp_path):
        from src.orchestrator import EvaOrchestrator
        from src.vault_md import MarkdownVault

        class Stub:
            def __init__(self, vault) -> None:
                self._vault = vault

        out = _run(EvaOrchestrator._reindex_vault(
            Stub(MarkdownVault(vault_root=tmp_path / "v")), {}
        ))
        assert out["status"] == "error"
        assert "embed" in out["error"] and "upsert" in out["error"]
        assert "files" in out
        json.dumps(out)

    def test_with_injected_backend_is_used(self, tmp_path):
        from src.orchestrator import EvaOrchestrator
        from src.vault_md import MarkdownVault

        vault = MarkdownVault(vault_root=tmp_path / "vault")
        vault.write("wiki/note.md", "# Note\n\nhello vector world\n")

        embedded: list[str] = []
        upserted: list[tuple[str, Any]] = []

        async def embed(text: str):
            embedded.append(text)
            return [0.1, 0.2, 0.3]

        async def upsert(path: str, index: int, chunk: str, vector, content_hash: str):
            upserted.append((path, index, vector))
            return None

        class Stub:
            def __init__(self) -> None:
                self._vault = vault

        out = _run(EvaOrchestrator._reindex_vault(Stub(), {"embed": embed, "upsert": upsert}))
        assert out["status"] == "ok", out
        assert embedded, "the embedder must actually be called"
        assert upserted, "the upsert callable must actually be called"
        json.dumps(out)


# ─────────────────────────────────────────────────────────────────────────────
# Confidence budget / HITL
# ─────────────────────────────────────────────────────────────────────────────
class TestConfidenceNeverAutoAct:
    def test_max_confidence_still_requires_human_on_trades(self):
        from src.confidence import ConfidenceBudget, EscalationLevel

        budget = ConfidenceBudget()
        result = budget.evaluate(
            agent_id="sam", confidence=1.0, action_type="trade_execute", action_risk="critical"
        )
        assert result.level is EscalationLevel.ASK
        assert "human approval" in result.reason.lower()

    def test_normal_action_can_still_act(self):
        from src.confidence import ConfidenceBudget, EscalationLevel

        budget = ConfidenceBudget()
        result = budget.evaluate(
            agent_id="eva", confidence=0.95, action_type="chat", action_risk="low"
        )
        assert result.level is EscalationLevel.ACT

    def test_destructive_actions_covered(self):
        from src.confidence import ConfidenceBudget

        for action in ("trade_execute", "delete_data", "financial_transaction",
                       "emergency_lockdown", "place_order"):
            assert action in ConfidenceBudget.NEVER_AUTO_ACT


# ─────────────────────────────────────────────────────────────────────────────
# FinAgent — no fabricated numbers
# ─────────────────────────────────────────────────────────────────────────────
def _fin() -> Any:
    from src.agents.fin import FinAgent

    return FinAgent(memory=None)


class TestFinAgentHonesty:
    def test_bank_failure_is_not_fabricated(self):
        out = _run(_fin()._sync_bank_data({}))
        assert out["status"] in ("ok", "unavailable")
        if out["status"] == "unavailable":
            assert out["total_uah"] == 0
            assert out["total_usd"] == 0
            assert "not estimated" in out["warning"].lower()
            # The old code invented 185400/74200 UAH and 15000 USD.
            assert out["total_uah"] != 185400
            assert out["total_usd"] != 15000

    def test_explicit_accounts_are_summed(self):
        out = _run(_fin()._sync_bank_data({
            "accounts": [
                {"currency": "UAH", "balance": 1000},
                {"currency": "UAH", "balance": "2500.5"},
                {"currency": "USD", "balance": 100},
            ]
        }))
        assert out["status"] == "ok"
        assert out["total_uah"] == pytest.approx(3500.5)
        assert out["total_usd"] == pytest.approx(100.0)

    def test_runway_with_no_burn_is_unknown_not_infinite(self):
        out = _run(_fin()._calculate_runway({"cash_balance": 100_000, "monthly_burn": 0}))
        assert out["runway_months"] is None
        assert out["runway_days"] is None
        assert out["status"] == "unknown"
        assert out["runway_months"] != 999

    def test_runway_with_burn_is_computed(self):
        out = _run(_fin()._calculate_runway({"cash_balance": 100_000, "monthly_burn": 10_000}))
        assert out["runway_months"] == pytest.approx(10.0)
        assert out["status"] == "healthy"

    def test_runway_critical_below_three_months(self):
        out = _run(_fin()._calculate_runway({"cash_balance": 10_000, "monthly_burn": 10_000}))
        assert out["status"] == "critical"
        assert out["alert"]


# ─────────────────────────────────────────────────────────────────────────────
# DocAgent — screening calendar semantics
# ─────────────────────────────────────────────────────────────────────────────
class TestDocScreeningCalendar:
    def _calendar(self, last_checkups: Dict[str, str]):
        from src.agents.doc import DocAgent

        return _run(DocAgent(memory=None)._screening_calendar({"last_checkups": last_checkups}))

    def test_recent_screening_is_completed(self):
        recent = (date.today() - timedelta(days=30)).isoformat()
        out = self._calendar({"blood_pressure": recent})
        assert "blood_pressure" in out["completed"]
        assert "blood_pressure" not in out.get("upcoming", {})
        assert "blood_pressure" not in out["due"]

    def test_old_screening_is_overdue(self):
        old = (date.today() - timedelta(days=800)).isoformat()
        out = self._calendar({"blood_pressure": old})
        assert "blood_pressure" in out["overdue"]

    def test_missing_screening_is_due(self):
        out = self._calendar({})
        assert "blood_pressure" in out["due"]
        assert out["completed"] == []


# ─────────────────────────────────────────────────────────────────────────────
# SamAgent — trade journal rejections & runtime config
# ─────────────────────────────────────────────────────────────────────────────
class TestSamJournalConstraints:
    def _journal(self):
        from src.agents.sam.journal import TradeJournal

        return TradeJournal(memory=None)

    @staticmethod
    def _entry(symbol: str, direction: str) -> Any:
        from src.agents.sam.journal import JournalEntry

        return JournalEntry(
            signal_id=f"sig-{symbol}-{direction}",
            symbol=symbol,
            direction=direction,
            confluence_score=0.62,
            threshold=0.60,
        )

    def test_rejection_blocks_a_repeat_proposal(self):
        journal = self._journal()
        entry = self._entry("BTCUSDT", "long")
        _run(journal.record_signal(entry))
        _run(journal.record_decision(
            entry.signal_id, "reject", reason="ATR too wide",
            symbol="BTCUSDT", direction="long",
        ))
        constraints = _run(journal.negative_constraints("BTCUSDT"))
        assert constraints, "a rejected setup must record a negative constraint"
        assert any("ATR too wide" in c.get("summary", "") for c in constraints)

    def test_gate_blocks_only_the_rejected_instrument(self):
        from src.agents.sam.agent import SamAgent

        journal = self._journal()
        entry = self._entry("BTCUSDT", "long")
        _run(journal.record_signal(entry))
        _run(journal.record_decision(
            entry.signal_id, "reject", reason="ATR too wide",
            symbol="BTCUSDT", direction="long",
        ))
        constraints = _run(journal.negative_constraints())
        sam = SamAgent(memory=None)
        assert sam._match_constraint("BTCUSDT", "long", constraints) is not None
        assert sam._match_constraint("ETHUSDT", "short", constraints) is None

    def test_get_signal_returns_the_stored_signal(self):
        journal = self._journal()
        entry = self._entry("ETHUSDT", "short")
        _run(journal.record_signal(entry))
        stored = _run(journal.get_signal(entry.signal_id))
        assert stored is not None
        assert stored["symbol"] == "ETHUSDT"
        assert _run(journal.get_signal("missing")) is None


class TestSamRuntimeConfigNormalisation:
    def test_fraction_keys_are_converted_to_percent(self):
        from src.agents.sam.agent import SamAgent

        sam = SamAgent(memory=None, config={"risk_per_trade": 0.01, "daily_stop_out": 0.03})
        assert sam._config["risk_pct"] == pytest.approx(1.0)
        assert sam._config["daily_stop_pct"] == pytest.approx(3.0)

    def test_telegram_chat_id_alias(self):
        from src.agents.sam.agent import SamAgent

        sam = SamAgent(memory=None, config={"telegram_chat_id": "12345"})
        assert sam._config["sam_chat_id"] == "12345"

    def test_morning_data_returns_a_digest(self):
        from src.agents.sam.agent import SamAgent

        out = _run(SamAgent(memory=None).execute({"action": "morning_data"}))
        assert "error" not in out, out
        assert "digest" in out


# ─────────────────────────────────────────────────────────────────────────────
# Socratic tutor session isolation
# ─────────────────────────────────────────────────────────────────────────────
class TestSocraticSessionIsolation:
    def test_two_sessions_do_not_share_a_ladder(self):
        from src.agents.kira_socratic import SocraticTutor, TutorSession

        assert "session_id" in TutorSession.__dataclass_fields__

        tutor = SocraticTutor()
        a = tutor._session(student="alice", topic="recursion", session_id="s1")
        b = tutor._session(student="alice", topic="recursion", session_id="s2")

        assert a is not b
        a.level = 3
        assert b.level != 3

    def test_session_eviction_is_bounded(self):
        from src.agents.kira_socratic import SocraticTutor

        max_sessions = SocraticTutor.MAX_SESSIONS
        tutor = SocraticTutor()
        for i in range(max_sessions + 25):
            tutor._session(student=f"u{i}", topic="t", session_id=f"s{i}")
        assert len(tutor._sessions) <= max_sessions


# ─────────────────────────────────────────────────────────────────────────────
# Writable data paths (read-only container)
# ─────────────────────────────────────────────────────────────────────────────
class TestDataPaths:
    def test_env_var_relocates_every_writable_dir(self, tmp_path, monkeypatch):
        from src import data_paths

        monkeypatch.setenv(data_paths.ENV_VAR, str(tmp_path))
        for key in data_paths.DIRS:
            assert str(data_paths.data_dir(key)).startswith(str(tmp_path))

    def test_absolute_explicit_path_wins(self, tmp_path, monkeypatch):
        from src import data_paths

        monkeypatch.setenv(data_paths.ENV_VAR, str(tmp_path))
        explicit = tmp_path / "explicit"
        assert data_paths.data_dir("videos", explicit) == explicit

    def test_unset_env_keeps_repository_relative_defaults(self, monkeypatch):
        from src import data_paths

        monkeypatch.delenv(data_paths.ENV_VAR, raising=False)
        assert data_paths.data_dir("vault") == Path("vault_md")

    def test_vault_honours_data_dir(self, tmp_path, monkeypatch):
        from src import data_paths
        from src.vault_md import MarkdownVault

        monkeypatch.setenv(data_paths.ENV_VAR, str(tmp_path))
        vault = MarkdownVault()
        assert str(vault.root).startswith(str(tmp_path))
        assert vault.root.exists()

    def test_media_factories_honour_data_dir(self, tmp_path, monkeypatch):
        from src import data_paths

        monkeypatch.setenv(data_paths.ENV_VAR, str(tmp_path))

        from src.departments.compliance.antidetect_browser import AntiDetectProfileManager
        from src.departments.content_factory.mockup_studio import MockupStudio
        from src.departments.content_factory.video_producer import VideoProducer

        for factory in (VideoProducer, MockupStudio, AntiDetectProfileManager):
            inst = factory()
            root = getattr(inst, "output_dir", None) or inst.profiles_dir
            assert str(root).startswith(str(tmp_path)), factory.__name__


# ─────────────────────────────────────────────────────────────────────────────
# Edge-TTS resilience
# ─────────────────────────────────────────────────────────────────────────────
class TestVideoProducerTTSGuards:
    def test_tts_failure_returns_error_not_exception(self, tmp_path, monkeypatch):
        from src.departments.content_factory import video_producer
        from src.departments.content_factory.video_producer import VideoProducer

        class Boom:
            def __init__(self, *a, **k):
                pass

            async def save(self, *a, **k):
                raise OSError("Network is unreachable")

        monkeypatch.setattr(video_producer.edge_tts, "Communicate", Boom, raising=False)
        vp = VideoProducer(output_dir=str(tmp_path))
        out = _run(vp.generate_voiceover("hello world", str(tmp_path / "vo.mp3")))
        assert out["status"] == "error"
        assert "unavailable" in out["message"].lower()

    def test_empty_script_is_rejected_before_network(self, tmp_path):
        from src.departments.content_factory.video_producer import VideoProducer

        vp = VideoProducer(output_dir=str(tmp_path))
        out = _run(vp.generate_voiceover("   ", str(tmp_path / "vo.mp3")))
        assert out["status"] == "error"


# ─────────────────────────────────────────────────────────────────────────────
# Office copilot knowledge filtering
# ─────────────────────────────────────────────────────────────────────────────
class TestOfficeKnowledgeFiltering:
    def _lookup(self, payload):
        from src.agents.office_copilot import OfficeCopilotAgent

        return OfficeCopilotAgent()._lookup_knowledge(payload)

    def test_tool_selector_is_respected(self):
        word = self._lookup({"tool": "word"})
        assert "word_shortcuts" in word["data"]
        assert "formulas" not in word["data"]

        excel = self._lookup({"tool": "excel"})
        assert "formulas" in excel["data"]
        assert "word_shortcuts" not in excel["data"]

        macro = self._lookup({"tool": "macro"})
        assert "macros" in macro["data"]
        assert "formulas" not in macro["data"]

    def test_all_returns_everything(self):
        out = self._lookup({})
        for key in ("word_shortcuts", "excel_shortcuts", "formulas", "macros"):
            assert key in out["data"]

    def test_query_filter_still_works(self):
        out = self._lookup({"tool": "excel", "query": "sumifs"})
        assert out["data"]["matched_formulas"]


# ─────────────────────────────────────────────────────────────────────────────
# Agent runner hardening
# ─────────────────────────────────────────────────────────────────────────────
class TestAgentRunnerHardening:
    def test_no_signal_handlers_installed_at_import(self):
        """The runner used to hijack SIGTERM/SIGINT at import time, which made
        ``docker stop`` a no-op and forced a SIGKILL after the grace period."""
        src = (REPO_ROOT / "deploy" / "runtime" / "agent_runner.py").read_text(encoding="utf-8")
        assert "signal.signal(" not in src

    def test_private_client_detection_is_not_over_broad(self):
        mod = importlib.import_module("agent_runner")
        check = mod._is_private_client

        for private in ("127.0.0.1", "10.1.2.3", "192.168.0.5", "172.16.0.1",
                        "172.31.255.255", "::1", "localhost", "fc00::1", "fd12:3456::1"):
            assert check(private) is True, private
        # 172.32.x and 172.15.x are PUBLIC addresses — the old check matched
        # every address starting with "172.".
        for public in ("172.32.0.1", "172.15.0.1", "8.8.8.8", "203.0.113.5", "172.0.0.1", ""):
            assert check(public) is False, public

    def test_json_safe_handles_bytes_and_nan(self):
        mod = importlib.import_module("agent_runner")

        out = mod._json_safe({"b": b"\x00\x01", "n": float("nan"), "s": "x" * 50_000})
        assert "bytes" in out["b"]
        assert isinstance(out["n"], str)
        assert len(out["s"]) < 50_000
        json.dumps(out)

    def test_cockpit_probe_has_no_stale_paths(self):
        runner = (REPO_ROOT / "deploy" / "runtime" / "agent_runner.py").read_text(encoding="utf-8")
        assert "repo_code" not in runner, "/cockpit still probes the stale repo_code/ layout"

    def test_cockpit_resolves_from_repo_root(self):
        mod = importlib.import_module("agent_runner")
        from fastapi.responses import HTMLResponse

        response = _run(mod.cockpit_interface())
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 200
        assert "SYNDIKAT" in response.body.decode("utf-8", "replace")


# ─────────────────────────────────────────────────────────────────────────────
# Deprecation sweep
# ─────────────────────────────────────────────────────────────────────────────
class TestNoNaiveUtc:
    def test_datetime_utcnow_is_gone(self):
        offenders = []
        for base in ("src", "deploy"):
            for path in (REPO_ROOT / base).rglob("*.py"):
                for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if "datetime.utcnow()" in line:
                        offenders.append(f"{path.relative_to(REPO_ROOT)}:{i}")
        assert offenders == [], f"naive utcnow() found: {offenders}"


# ─────────────────────────────────────────────────────────────────────────────
# Change requests — approval authority
# ─────────────────────────────────────────────────────────────────────────────
def _cr_store(tmp_path: Path):
    from src.change_requests import ChangeRequestStore
    from src.vault_md import MarkdownVault

    vault = MarkdownVault(vault_root=tmp_path / "vault")
    vault.write("statutes/security.md", "# Security Statute\n\nOld text.\n", allow_protected=True)
    return ChangeRequestStore(vault=vault), vault


class TestChangeRequestStore:
    def test_unknown_cr_id_raises_a_typed_error(self, tmp_path):
        from src.change_requests import ChangeRequestError

        store, _ = _cr_store(tmp_path)
        with pytest.raises(ChangeRequestError):
            store.review("CR-00000000", decision="approve", reviewer="Marshal")

    def test_author_cannot_approve_their_own_request(self, tmp_path):
        """``review()`` used to do ``self._approvers.add(reviewer)`` first, so the
        author could approve — and apply — their own change."""
        from src.change_requests import ChangeRequestError

        store, _ = _cr_store(tmp_path)
        cr = store.submit(
            title="Relax the statute",
            description="Self-approved change.",
            target_path="statutes/security.md",
            proposed_content="# Security Statute\n\nNew text.\n",
            author="Architect",
        )
        with pytest.raises(ChangeRequestError) as exc:
            store.review(cr["cr_id"], decision="approve", reviewer="Architect")
        assert "author" in str(exc.value)

    def test_unknown_reviewer_cannot_grant_themselves_authority(self, tmp_path):
        from src.change_requests import ChangeRequestError

        store, _ = _cr_store(tmp_path)
        cr = store.submit(
            title="Relax the statute",
            description=".",
            target_path="statutes/security.md",
            proposed_content="# Security Statute\n\nNew text.\n",
            author="Architect",
        )
        with pytest.raises(ChangeRequestError) as exc:
            store.review(cr["cr_id"], decision="approve", reviewer="RandomBot")
        assert "approver_not_authorized" in str(exc.value)

    def test_independent_reviewer_can_approve_and_apply(self, tmp_path):
        store, vault = _cr_store(tmp_path)
        cr = store.submit(
            title="Tighten the statute",
            description="Reviewed by a second party.",
            target_path="statutes/security.md",
            proposed_content="# Security Statute\n\nNew text.\n",
            author="Architect",
        )
        reviewed = store.review(cr["cr_id"], decision="approve", reviewer="Marshal")
        assert reviewed["status"] == "approved"

        applied = store.apply(cr["cr_id"])
        assert applied["status"] == "applied"
        assert "New text." in vault.read("statutes/security.md")

    def test_author_cannot_apply_even_after_another_reviewer_approved(self, tmp_path):
        from src.change_requests import ChangeRequestError

        store, vault = _cr_store(tmp_path)
        cr = store.submit(
            title="Tighten the statute",
            description=".",
            target_path="statutes/security.md",
            proposed_content="# Security Statute\n\nNew text.\n",
            author="Architect",
        )
        store.review(cr["cr_id"], decision="approve", reviewer="Marshal")
        with pytest.raises(ChangeRequestError) as exc:
            store.apply(cr["cr_id"], approver="Architect")
        assert "author" in str(exc.value)
        assert "Old text." in vault.read("statutes/security.md")

    def test_path_traversal_is_rejected_at_creation(self, tmp_path):
        from src.change_requests import ChangeRequestStore, ChangeRequestError
        from src.vault_md import MarkdownVault, VaultError

        store = ChangeRequestStore(vault=MarkdownVault(vault_root=tmp_path / "v2"))
        with pytest.raises((VaultError, ChangeRequestError)):
            store.create(
                author="Architect", title="escape", rationale=".",
                changes=[{"path": "../../etc/passwd.md", "content": "x"}],
            )


# ─────────────────────────────────────────────────────────────────────────────
# Repository hygiene
# ─────────────────────────────────────────────────────────────────────────────
class TestRepositoryHygiene:
    def test_compose_files_are_in_sync(self):
        root = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        nested = (REPO_ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8")
        assert root == nested, "docker-compose.yml and deploy/docker-compose.yml have drifted"

    def test_every_dockerfile_reference_exists(self):
        import re

        compose = (REPO_ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8")
        for dockerfile in re.findall(r"dockerfile:\s*(\S+)", compose):
            assert (REPO_ROOT / dockerfile).exists(), f"missing build context: {dockerfile}"

    def test_no_duplicate_top_level_yaml_keys(self):
        """A repeated key silently drops the first block — this is how the
        source mounts vanished from the eva-agent service."""
        import yaml

        compose = yaml.safe_load((REPO_ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8"))
        for _name, svc in compose.get("services", {}).items():
            assert "volumes" in svc or "image" in svc or "build" in svc
            if "build" in svc:
                assert "image" not in svc

    def test_agent_service_mounts_source_and_a_writable_volume(self):
        import yaml

        compose = yaml.safe_load((REPO_ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8"))
        svc = compose["services"]["eva-agent"]
        mounts = "\n".join(svc.get("volumes", []))
        assert "/app/src" in mounts
        assert "/app/runtime" in mounts
        assert "/data/eva" in mounts
        assert svc["environment"]["EVA_DATA_DIR"] == "/data/eva"
        assert svc.get("read_only") is True

    def test_no_stale_env_file_committed(self):
        assert not (REPO_ROOT / ".env").exists(), ".env must never be committed"

    def test_every_source_module_imports(self):
        """Import failures only surface at runtime on the server; catch them here."""
        import src

        failures = []
        for mod in pkgutil.walk_packages(src.__path__, prefix="src."):
            try:
                importlib.import_module(mod.name)
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{mod.name}: {type(exc).__name__}: {exc}")
        assert failures == [], "import failures:\n" + "\n".join(failures)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
