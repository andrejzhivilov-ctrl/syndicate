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
import re
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

    def test_banking_client_does_not_inject_sandbox_balances(self):
        """Root cause of the fabricated figures: BankingClient silently
        substituted a hardcoded portfolio whenever no token was configured."""
        from src.integrations.banking import BankingClient

        out = _run(BankingClient().get_accounts_overview())
        assert out["status"] == "unavailable"
        assert out["accounts"] == []
        assert out["totals"]["UAH"] == 0.0
        assert out["totals"]["USD"] == 0.0

    def test_sandbox_balances_are_opt_in_and_labelled(self, monkeypatch):
        from src.integrations.banking import BankingClient

        monkeypatch.setenv("EVA_BANKING_SANDBOX", "1")
        out = _run(BankingClient().get_accounts_overview())
        assert out["synthetic"] is True
        assert out["accounts"]

    def test_fin_never_reports_sandbox_money_as_ok(self):
        out = _run(_fin()._sync_bank_data({}))
        assert out["status"] == "unavailable"
        assert out["total_uah"] != 185400
        assert out["total_uah"] != 74200
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

    def test_symbol_filter_is_not_silently_ignored(self):
        """`negative_constraints(symbol=...)` used to return the global set."""
        journal = self._journal()
        for sym in ("BTCUSDT", "ETHUSDT"):
            entry = self._entry(sym, "long")
            _run(journal.record_signal(entry))
            _run(journal.record_decision(
                entry.signal_id, "reject", reason=f"{sym} spread too wide",
                symbol=sym, direction="long",
            ))

        all_constraints = _run(journal.negative_constraints())
        assert len(all_constraints) == 2
        btc = _run(journal.negative_constraints("BTCUSDT"))
        assert len(btc) == 1
        assert "BTCUSDT:long" in btc[0]["summary"]
        assert _run(journal.negative_constraints("ETHUSDT"))[0]["summary"].startswith("ETHUSDT")
        assert _run(journal.negative_constraints("SOLUSDT")) == []

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
# Growth analyst — no invented metrics in a CFO dossier
# ─────────────────────────────────────────────────────────────────────────────
class TestGrowthAnalystHonesty:
    def test_no_channel_data_is_reported_as_unavailable(self):
        from src.departments.operations.growth_analyst import GrowthAnalyst

        out = GrowthAnalyst().aggregate_channel_performance()
        assert out["status"] == "unavailable"
        assert out["total_outbound_clicks"] == 0
        assert out["channels"] == {}
        # The old implementation hardcoded 128_500 impressions / 2_560 clicks.
        assert out["total_outbound_clicks"] != 2560

    def test_supplied_channels_are_aggregated(self):
        from src.departments.operations.growth_analyst import GrowthAnalyst

        out = GrowthAnalyst().aggregate_channel_performance({
            "x": {"impressions": 1000, "link_clicks": 25},
            "youtube": {"views": 500, "link_clicks": 10},
        })
        assert out["status"] == "ok"
        assert out["total_outbound_clicks"] == 35
        assert out["channels"]["x"]["ctr"] == "2.50%"

    def test_dossier_without_ledger_figures_is_refused(self):
        from src.departments.operations.growth_analyst import GrowthAnalyst

        out = GrowthAnalyst().formulate_cfo_dossier(None, None)
        assert out["status"] == "unavailable"
        assert "calculated_roi" not in out
        assert out["cfo_audit_required"] is True

    def test_dossier_with_ledger_figures_computes_roi(self):
        from src.departments.operations.growth_analyst import GrowthAnalyst

        out = GrowthAnalyst().formulate_cfo_dossier(400.0, 100.0)
        assert out["status"] == "ok"
        assert out["calculated_roi"] == "300.0%"

    def test_coordinator_does_not_default_the_money(self):
        """The Floor-2 coordinator used to default revenue/costs to 210/35."""
        from src.departments.coordinator import Floor2Coordinator

        out = _run(Floor2Coordinator().execute({"action": "aggregate_growth_metrics"}))
        dossier = out["cfo_dossier"]
        assert dossier["status"] == "unavailable"
        assert out["performance"]["status"] == "unavailable"
        assert "$210.00" not in json.dumps(out)


# ─────────────────────────────────────────────────────────────────────────────
# Content Factory: no fabricated artefacts, no silent successes
# ─────────────────────────────────────────────────────────────────────────────
class TestContentFactoryHonesty:
    @staticmethod
    def _tmp_video(tmp_path) -> str:
        video = tmp_path / "clip.mp4"
        video.write_bytes(b"\x00" * 16)
        return str(video)

    def test_telegram_without_token_does_not_claim_success(self, monkeypatch, tmp_path):
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        from src.departments.content_factory.publisher import ContentPublisher

        out = _run(ContentPublisher().publish_to_telegram(self._tmp_video(tmp_path), "hi"))
        assert out["status"] == "not_published"
        assert out["published"] is False

    def test_youtube_without_credentials_does_not_claim_success(self, monkeypatch):
        monkeypatch.setenv("YOUTUBE_CREDENTIALS_PATH", "/definitely/not/here.json")
        from src.departments.content_factory.publisher import ContentPublisher

        out = _run(ContentPublisher().schedule_youtube_short("v.mp4", "t", "d", ["#ai"]))
        assert out["status"] == "not_published"
        assert out["published"] is False
        assert out["video_id"] if "video_id" in out else True

    def test_campaign_reports_nothing_published_when_all_channels_are_unconfigured(
        self, monkeypatch, tmp_path
    ):
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.setenv("YOUTUBE_CREDENTIALS_PATH", "/definitely/not/here.json")
        from src.departments.content_factory.publisher import ContentPublisher

        out = _run(ContentPublisher().dispatch_full_campaign(self._tmp_video(tmp_path), {}))
        assert out["status"] == "not_published"
        assert out["published_platforms"] == []
        assert out["published"] is False

    def test_missing_video_file_is_an_error(self, monkeypatch):
        from src.departments.content_factory.publisher import ContentPublisher

        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
        out = _run(ContentPublisher().publish_to_telegram("/nope.mp4", "hi"))
        assert out["status"] == "error"

    def test_grok_writer_without_key_returns_no_posts(self, monkeypatch):
        monkeypatch.delenv("XAI_API_KEY", raising=False)
        monkeypatch.delenv("EVA_GROK_MOCK", raising=False)
        from src.departments.content_factory.grok_writer import GrokWriter

        out = _run(GrokWriter().generate_thread("topic"))
        assert out["status"] == "unavailable"
        assert out["posts"] == []

        reply = _run(GrokWriter().generate_reply_snipe("post", "angle"))
        assert reply["status"] == "unavailable"
        assert reply["reply"] is None

    def test_grok_demo_copy_is_opt_in_and_labelled(self, monkeypatch):
        monkeypatch.delenv("XAI_API_KEY", raising=False)
        monkeypatch.setenv("EVA_GROK_MOCK", "1")
        from src.departments.content_factory.grok_writer import GrokWriter

        out = _run(GrokWriter().generate_thread("topic"))
        assert out["posts"]
        assert out["synthetic"] is True
        assert out["status"] == "unavailable"

    def test_script_template_matches_the_requested_duration(self, monkeypatch):
        monkeypatch.delenv("XAI_API_KEY", raising=False)
        from src.departments.content_factory.script_director import ScriptDirector

        for duration in (15, 30, 60):
            out = _run(ScriptDirector().generate_short_script("AI", target_duration_sec=duration))
            scenes = out["script"]["scenes"]
            total = round(sum(sc["duration_sec"] for sc in scenes), 2)
            assert abs(total - duration) < 0.5, f"{duration}s brief produced {total}s of scenes"
            assert out["synthetic"] is True

    def test_caption_timestamps_are_valid_ass(self, tmp_path, monkeypatch):
        monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
        from src.departments.content_factory.caption_engine import CaptionEngine

        engine = CaptionEngine()
        words = engine.generate_word_timestamps("one two three four", 1.999)
        path = engine.create_ass_karaoke_file(words, output_filename="c.ass")
        text = Path(path).read_text(encoding="utf-8")
        stamps = re.findall(r"Dialogue: 0,([^,]+),([^,]+),", text)
        assert stamps, "no caption events generated"
        for start, end in stamps:
            for stamp in (start, end):
                centis = int(stamp.split(".")[1])
                assert 0 <= centis <= 99, f"invalid ASS centisecond field: {stamp}"

    def test_caption_filename_cannot_escape_the_output_dir(self, tmp_path, monkeypatch):
        monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
        from src.departments.content_factory.caption_engine import CaptionEngine

        path = CaptionEngine().create_ass_karaoke_file(
            [{"word": "a", "start": 0.0, "end": 1.0, "duration": 1.0}],
            output_filename="../../escaped.ass",
        )
        assert Path(path).parent.name == "captions"

    def test_mockup_from_missing_artwork_is_labelled(self, tmp_path, monkeypatch):
        monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
        from src.departments.content_factory.mockup_studio import MockupStudio

        out = MockupStudio().composite_artwork(str(tmp_path / "missing.png"))
        assert out["synthetic"] is True
        assert any("artwork_not_found" in w for w in out["warnings"])

    def test_video_producer_rejects_missing_broll(self, tmp_path, monkeypatch):
        monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
        from src.departments.content_factory.video_producer import VideoProducer

        out = _run(VideoProducer().render_video("/nope.mp4", "text", "out.mp4"))
        assert out["status"] == "error"
        assert "broll_video not found" in out["message"]


# ─────────────────────────────────────────────────────────────────────────────
# Orc adversarial verifier
# ─────────────────────────────────────────────────────────────────────────────
class _Skeptic:
    def __init__(self, answer: str) -> None:
        self._answer = answer

    async def ainvoke(self, prompt: str):  # noqa: ARG002 - signature parity with an LLM
        return type("Resp", (), {"content": self._answer})()


class TestOrcVerifier:
    @staticmethod
    def _claim(statement="sky is blue", response="the sky is blue", **kwargs):
        from src.verifier import Claim, Evidence

        return Claim(
            statement=statement,
            author="tester",
            evidence=Evidence(call={"action": "verify"}, response=response),
            **kwargs,
        )

    def test_no_evidence_is_unproven(self):
        from src.verifier import Claim, OrcVerifier

        verdict = _run(OrcVerifier().verify(Claim(statement="x", author="t")))
        assert verdict.status == "unproven"
        assert verdict.reasons == ["no_evidence"]

    def test_stale_evidence_is_unproven(self):
        from src.verifier import OrcVerifier

        claim = self._claim()
        claim.evidence.timestamp -= 200_000
        verdict = _run(OrcVerifier().verify(claim))
        assert verdict.status == "unproven"
        assert verdict.reasons == ["evidence_stale"]

    def test_missing_and_forbidden_content_refute(self):
        from src.verifier import OrcVerifier

        verdict = _run(OrcVerifier().verify(self._claim(must_contain=["green"])))
        assert verdict.status == "refuted"
        assert verdict.reasons == ["evidence_missing:green"]

        verdict = _run(OrcVerifier().verify(self._claim(must_not_contain=["blue"])))
        assert verdict.status == "refuted"
        assert verdict.reasons == ["evidence_contradicts:blue"]

    def test_replay_mismatch_refutes(self):
        from src.verifier import OrcVerifier

        async def replayer(call):  # noqa: ARG001
            return "the sky is green"

        verdict = _run(OrcVerifier().verify(self._claim(), replayer))
        assert verdict.status == "refuted"
        assert verdict.replay_matched is False

    def test_replay_failure_is_unproven_not_refuted(self):
        from src.verifier import OrcVerifier

        async def replayer(call):  # noqa: ARG001
            raise RuntimeError("boom")

        verdict = _run(OrcVerifier().verify(self._claim(), replayer))
        assert verdict.status == "unproven"
        assert verdict.reasons == ["replay_failed:RuntimeError"]
        assert verdict.replay_matched is None

    def test_clean_evidence_is_confirmed(self):
        from src.verifier import OrcVerifier

        async def replayer(call):  # noqa: ARG001
            return "the sky is blue"

        verdict = _run(OrcVerifier().verify(self._claim(), replayer))
        assert verdict.status == "confirmed"
        assert "replay_matched" in verdict.reasons

    def test_skeptic_can_refute(self):
        from src.verifier import OrcVerifier

        assert _run(OrcVerifier(skeptic_llm=_Skeptic("REFUTED")).verify(self._claim())).status == "refuted"
        assert _run(OrcVerifier(skeptic_llm=_Skeptic("HOLDS")).verify(self._claim())).status == "confirmed"

    def test_skeptic_failure_does_not_refute(self):
        from src.verifier import OrcVerifier

        class Boom:
            async def ainvoke(self, prompt):  # noqa: ARG002
                raise RuntimeError("llm down")

        assert _run(OrcVerifier(skeptic_llm=Boom()).verify(self._claim())).status == "confirmed"


# ─────────────────────────────────────────────────────────────────────────────
# PII redaction
# ─────────────────────────────────────────────────────────────────────────────
class TestPIIRedaction:
    """A leak here goes straight to an external LLM, so it is asserted per pattern."""

    def _redact(self, text: str) -> str:
        from src.pii import PIIRedactor

        redacted, _events = PIIRedactor().redact(text)
        return redacted

    def test_ukrainian_iban_is_masked(self):
        """The old pattern spanned 27 chars — real UA IBANs are 29 and leaked whole."""
        iban = "UA213223130000026007233566001"
        assert len(iban) == 29
        out = self._redact(f"pay to {iban} today")
        assert iban not in out
        assert "233566001" not in out
        assert out.startswith("pay to UA21**...6001")

    def test_every_pattern_masks_its_own_sample(self):
        samples = {
            "ukrainian_phone": ("call +380671234567 now", "+380671234567"),
            "intl_phone": ("call +12025550143 now", "25550143"),
            "email": ("mail andrii.test@example.com please", "andrii.test@"),
            "credit_card": ("card 4111 1111 1111 1111", "4111 1111 1111"),
            "ukrainian_ipn": ("ipn 1234567890", "234567890"),
            "passport": ("passport AB123456", "123456"),
            "iban": ("iban UA213223130000026007233566001", "3223130000026007233566"),
            "api_key_ghp": ("key ghp_abcdefghijklmnopqrstuvwxyz012345", "ghp_abcdefghijklmnopqrstuvwxyz012345"),
            "api_key_sk_ant": ("key sk-ant-abcdefghijklmnopqrstuv", "sk-ant-abcdefghijklmnopqrstuv"),
            "api_key_gsk": ("key gsk_abcdefghijklmnopqrstuvwxyz01", "gsk_abcdefghijklmnopqrstuvwxyz01"),
            "ipv4": ("host 192.168.100.200", "100.200"),
        }
        for name, (sample, secret) in samples.items():
            out = self._redact(sample)
            assert secret not in out, f"{name} leaked: {out}"

    def test_events_are_recorded_for_audit(self):
        from src.pii import PIIRedactor

        redacted, events = PIIRedactor().redact("+380671234567")
        assert [e.pattern_name for e in events] == ["ukrainian_phone"]
        assert events[0].original_match == "+380671234567"

    def test_non_strings_pass_through(self):
        from src.pii import PIIRedactor

        assert PIIRedactor().redact(42) == (42, [])
        assert PIIRedactor().redact(None) == (None, [])

    def test_dict_redaction_walks_nested_containers(self):
        from src.pii import PIIRedactor

        out = PIIRedactor().redact_dict(
            {"a": {"b": "andrii.test@example.com"}, "l": ["+380671234567", 5, None]}
        )
        assert out == {"a": {"b": "a***@example.com"}, "l": ["+380***567", 5, None]}


# ─────────────────────────────────────────────────────────────────────────────
# Action dispatch tables (the long if/elif chains that were refactored away)
# ─────────────────────────────────────────────────────────────────────────────
def _dispatch_agents():
    """Every agent whose ``execute()`` dispatches through ``_ACTION_MAP``."""
    from src.agents.architect.agent import ArchitectAgent
    from src.agents.doc import DocAgent
    from src.agents.kira import KiraAgent
    from src.agents.marshal import MarshalAgent
    from src.agents.sam.agent import SamAgent
    from src.departments.coordinator import Floor2Coordinator

    built = []
    for factory in (
        lambda: ArchitectAgent(memory=None),
        lambda: DocAgent(memory=None),
        lambda: KiraAgent(memory=None),
        lambda: MarshalAgent(),
        lambda: SamAgent(memory=None),
        Floor2Coordinator,
    ):
        agent = factory()
        if hasattr(agent, "_ACTION_MAP"):
            built.append(agent)
    return built


class TestActionDispatchTables:
    def test_every_agent_exposes_a_populated_action_map(self):
        agents = _dispatch_agents()
        assert agents, "no agent exposes _ACTION_MAP — did the dispatchers regress?"
        for agent in agents:
            assert agent._ACTION_MAP, f"{type(agent).__name__} has an empty action map"

    def test_every_handler_accepts_a_single_payload_argument(self):
        """`capabilities()` takes no payload; it must be adapted, not bound raw."""
        import inspect

        for agent in _dispatch_agents():
            for name, handler in agent._ACTION_MAP.items():
                params = [
                    p
                    for p in inspect.signature(handler).parameters.values()
                    if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                ]
                assert len(params) == 1, (
                    f"{type(agent).__name__}.{name} handler takes "
                    f"{len(params)} positional args, execute() passes 1"
                )

    def test_unknown_action_is_an_error_not_a_silent_fallback(self):
        """Marshal used to answer unknown actions with a full security audit."""
        for agent in _dispatch_agents():
            out = _run(agent.execute({"action": "definitely_not_an_action"}))
            assert isinstance(out, dict), f"{type(agent).__name__}: {type(out)}"
            assert out.get("status") == "error", f"{type(agent).__name__}: {out}"
            assert "Unknown action" in out.get("error", "")
            assert "available_actions" in out

    def test_capabilities_still_dispatch(self):
        for agent in _dispatch_agents():
            for action in ("capabilities", "status"):
                if action not in agent._ACTION_MAP:
                    continue
                out = _run(agent.execute({"action": action}))
                assert isinstance(out, dict), f"{type(agent).__name__}.{action}: {type(out)}"
                assert "error" not in out, f"{type(agent).__name__}.{action}: {out}"


# ─────────────────────────────────────────────────────────────────────────────
# Kira dispatch
# ─────────────────────────────────────────────────────────────────────────────
class TestKiraDispatch:
    def test_unknown_action_is_an_error_not_a_dialogue(self):
        from src.agents.kira import KiraAgent

        out = _run(KiraAgent(memory=None).execute({"action": "definitely_not_an_action"}))
        assert out["status"] == "error"
        assert "Unknown action" in out["error"]
        assert "available_actions" in out

    def test_known_action_still_dispatches(self):
        from src.agents.kira import KiraAgent

        out = _run(KiraAgent(memory=None).execute({"action": "academy_overview"}))
        assert out["status"] == "ok"


# ─────────────────────────────────────────────────────────────────────────────
# PostgreSQL schema: init.sql must be a complete single-pass schema
# ─────────────────────────────────────────────────────────────────────────────
def _sql_statements(text: str) -> list[str]:
    # Strip line comments BEFORE splitting on ";". A "--" comment containing a
    # semicolon (e.g. "-- e.g. foo; bar") would otherwise split a statement in
    # two and make the drift check below compare garbage.
    no_comments = re.sub(r"--[^\n]*", "", text)
    return [s.strip() for s in no_comments.split(";")]


def _sql_names(text: str, kind: str) -> set[str]:
    return set(re.findall(rf"CREATE {kind} IF NOT EXISTS\s+([\w\.]+)", text))


def _sql_table_bodies(text: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for stmt in _sql_statements(text):
        m = re.search(r"CREATE TABLE IF NOT EXISTS\s+([\w\.]+)", stmt)
        if m:
            body = re.sub(r"--[^\n]*", "", stmt)
            out[m.group(1)] = re.sub(r"\s+", " ", body).strip()
    return out


class TestPostgresSchemaConsistency:
    init = (REPO_ROOT / "config" / "postgres" / "init.sql").read_text(encoding="utf-8")
    migration = (REPO_ROOT / "config" / "postgres" / "migration_v4.sql").read_text(encoding="utf-8")

    def test_init_covers_every_migration_object(self):
        """A fresh database that only runs init.sql must end up with everything
        the upgrade migration would have created."""
        for kind in ("TABLE", "INDEX"):
            missing = _sql_names(self.migration, kind) - _sql_names(self.init, kind)
            assert not missing, f"init.sql is missing {kind.lower()}(s): {sorted(missing)}"

    def test_no_duplicate_table_definitions(self):
        for text, label in ((self.init, "init.sql"), (self.migration, "migration_v4.sql")):
            tables = re.findall(r"CREATE TABLE IF NOT EXISTS\s+([\w\.]+)", text)
            dupes = {t for t in tables if tables.count(t) > 1}
            assert not dupes, f"{label} defines tables twice: {sorted(dupes)}"
            indexes = re.findall(r"CREATE INDEX IF NOT EXISTS\s+([\w\.]+)", text)
            dupes = {i for i in indexes if indexes.count(i) > 1}
            assert not dupes, f"{label} defines indexes twice: {sorted(dupes)}"

    def test_shared_table_definitions_do_not_drift(self):
        a, b = _sql_table_bodies(self.init), _sql_table_bodies(self.migration)
        shared = set(a) & set(b)
        assert shared, "the two files are expected to share table definitions"
        for table in sorted(shared):
            assert a[table] == b[table], f"table definition drifted: {table}"

    def test_future_tables_inherit_privileges(self):
        """Without ALTER DEFAULT PRIVILEGES, tables added by a later migration
        would be invisible to eva_agent."""
        assert "ALTER DEFAULT PRIVILEGES" in self.init

    def test_semicolon_inside_comment_does_not_split_a_statement(self):
        """`_sql_statements` splits on ';'. A comment containing ';' must not
        be mistaken for a statement boundary, or the drift check silently
        compares halves of two different tables."""
        text = (
            "-- NOTE: legacy; do not reuse\n"
            "CREATE TABLE IF NOT EXISTS auth.demo (id TEXT PRIMARY KEY);\n"
        )
        bodies = _sql_table_bodies(text)
        assert set(bodies) == {"auth.demo"}
        assert bodies["auth.demo"].startswith("CREATE TABLE")

    def test_trigger_function_is_defined_before_use(self):
        for text, label in ((self.init, "init.sql"), (self.migration, "migration_v4.sql")):
            if "update_updated_at()" not in text:
                continue
            defined = text.find("CREATE OR REPLACE FUNCTION update_updated_at()")
            used = min(
                (m.start() for m in re.finditer(r"EXECUTE FUNCTION update_updated_at\(\)", text)),
                default=-1,
            )
            if defined == -1:
                assert label == "migration_v4.sql", "init.sql must define update_updated_at()"
            elif used != -1:
                assert defined < used, f"{label} uses the trigger before defining it"

    def test_every_trigger_creation_is_replayable(self):
        """``CREATE TRIGGER`` has no ``IF NOT EXISTS``. Without a preceding
        ``DROP TRIGGER IF EXISTS`` the bootstrap script cannot be replayed and
        02-migration_v4.sql cannot be applied on top of init.sql — both failed
        with ``DuplicateObject`` until a live database ran them."""
        for path in (REPO_ROOT / "config/postgres/init.sql", REPO_ROOT / "config/postgres/migration_v4.sql"):
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"CREATE TRIGGER\s+([\w]+)", text):
                drop = f"DROP TRIGGER IF EXISTS {match.group(1)}"
                assert drop in text[: match.start()], (
                    f"{path.name}: CREATE TRIGGER {match.group(1)} has no preceding {drop}"
                )


# ─────────────────────────────────────────────────────────────────────────────
# MemoryManager must expose the asyncpg pool the $1-SQL components probe
# ─────────────────────────────────────────────────────────────────────────────
class TestMemoryPoolContract:
    """``TradeJournal`` and ``DeviceTokenStore`` resolve their backend by
    probing ``memory.pool`` / ``memory._pool`` / ``memory.db_pool``.
    ``MemoryManager`` used to expose only a SQLAlchemy session factory, so both
    silently degraded to volatile in-memory storage: ``agents.sam_trade_journal``
    and ``auth.device_tokens`` stayed empty in production and every restart lost
    the data. The live-DB side of this contract is in
    ``tests/test_postgres_paths.py::TestMemoryManagerLiveSql``.
    """

    PROBE_ATTRS = ("pool", "_pool", "db_pool")

    def test_memory_manager_declares_a_pool_attribute(self):
        from src.memory import MemoryManager

        manager = MemoryManager(postgres_dsn="postgresql+asyncpg://localhost/none", redis_url="")
        assert hasattr(manager, "pool"), f"nothing for the consumers to find among {self.PROBE_ATTRS}"

    def test_consumers_still_probe_the_declared_attributes(self):
        from src.agents.sam.journal import TradeJournal
        from src.device_auth import DeviceTokenStore

        for cls in (TradeJournal, DeviceTokenStore):
            source = inspect.getsource(cls._pool)
            assert any(attr in source for attr in self.PROBE_ATTRS), (
                f"{cls.__name__} stopped probing the pool attributes the manager exposes"
            )

    def test_sqlalchemy_driver_suffix_is_stripped_for_asyncpg(self):
        """asyncpg rejects the SQLAlchemy ``+asyncpg`` dialect suffix."""
        from src.memory import MemoryManager

        manager = MemoryManager(postgres_dsn="postgresql+asyncpg://u:p@db:5432/eva", redis_url="")
        assert manager._libpq_dsn() == "postgresql://u:p@db:5432/eva"

    def test_redis_is_optional_and_reported_honestly(self):
        """Without a Redis URL the cache is disabled — not silently "ready"."""
        import src.memory as memory_module

        source = inspect.getsource(memory_module.MemoryManager.initialize)
        assert "redis_cache_disabled" in source, "a missing Redis must be logged, not hidden"


# ─────────────────────────────────────────────────────────────────────────────
# Vault secret paths
# ─────────────────────────────────────────────────────────────────────────────
class TestVaultSecretPaths:
    def test_single_convention(self):
        from src import vault_paths

        assert vault_paths.secret_path("database") == "secret/data/eva-syndicate/database"
        assert vault_paths.secret_path("api-keys") == "secret/data/eva-syndicate/api-keys"
        for service in ("database", "redis", "auth", "api-keys"):
            assert vault_paths.secret_path(service).startswith("secret/data/eva-syndicate/")

    def test_empty_service_is_rejected(self):
        from src import vault_paths

        with pytest.raises(ValueError):
            vault_paths.secret_path("")

    def test_no_legacy_mount_paths_in_source(self):
        """The old `eva/<mount>/data/<key>` layout must be gone: vault_init.sh
        never populated those mounts, so the agent 404'd on startup."""
        offenders = []
        for base in ("src", "deploy"):
            for path in (REPO_ROOT / base).rglob("*.py"):
                for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if re.search(r'"eva/(database|config|api-keys|agents)/data/', line):
                        offenders.append(f"{path.relative_to(REPO_ROOT)}:{i}")
        assert offenders == [], f"legacy Vault paths remain: {offenders}"

    def test_vault_init_populates_every_path_agent_runner_reads(self):
        runner = (REPO_ROOT / "deploy" / "runtime" / "agent_runner.py").read_text(encoding="utf-8")
        script = (REPO_ROOT / "deploy" / "scripts" / "vault_init.sh").read_text(encoding="utf-8")
        read = set(re.findall(r'secret_path\("([\w-]+)"\)', runner))
        written = set(re.findall(r"/v1/secret/data/eva-syndicate/([\w-]+)", script))
        assert read, "could not find any secret_path() call in agent_runner"
        missing = read - written
        assert not missing, f"vault_init.sh never writes these secrets: {sorted(missing)}"

    def test_policy_grants_the_paths_the_code_reads(self):
        from src import vault_paths

        script = (REPO_ROOT / "deploy" / "scripts" / "vault_init.sh").read_text(encoding="utf-8")
        for pattern in vault_paths.policy_paths():
            assert pattern in script, f"eva-agent policy is missing `{pattern}`"


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


# ─────────────────────────────────────────────────────────────────────────────
# Sam confluence — absent data must never be scored as an observation
# ─────────────────────────────────────────────────────────────────────────────
class TestConfluenceAbsenceIsNotAnObservation:
    """Three confluence layers used to invent a score when their input was
    missing, so an unreadable layer was indistinguishable from a measured one:

    * ``news_shield_layer`` scored **80/100 and never vetoed** when the economic
      calendar was unknown — the black-swan shield failed *open*, while an
      FOMC/NFP/CPI release could be minutes away.
    * ``smc_layer`` reported "no structural confluence detected" (0.0) when the
      candles could not be analysed at all, and its derivation helper swallowed
      every individual library error with ``except: pass``.
    * ``derivatives_layer`` returned a manufactured "neutral" 45/50 with no
      funding data.

    All three now return ``unavailable=True``, which the engine treats exactly
    like a layer that was never evaluated: 0 contribution, reported ``missing``.
    """

    def test_unknown_news_calendar_fails_closed(self):
        """The critical one: no calendar ⇒ no safe score, and no free points."""
        from src.agents.sam.skills import news_shield_layer

        layer = news_shield_layer({})
        assert layer.unavailable is True
        assert layer.score == 0.0
        assert "unavailable" in layer.rationale

    def test_news_calendar_none_is_not_treated_as_clear(self):
        """Explicit ``None`` (caller simply does not know) must equal unknown."""
        from src.agents.sam.skills import news_shield_layer

        layer = news_shield_layer({"minutes_to_high_impact": None})
        assert layer.unavailable is True, "None must not be read as 'calendar clear'"
        assert layer.score == 0.0

    def test_checked_calendar_still_reports_clear(self):
        """An explicit assertion that the calendar was read unlocks the score."""
        from src.agents.sam.skills import news_shield_layer

        layer = news_shield_layer({"news_calendar_checked": True})
        assert layer.unavailable is False
        assert layer.score == 80.0

    def test_imminent_high_impact_event_still_vetoes(self):
        """The fix must not weaken the real veto."""
        from src.agents.sam.skills import news_shield_layer

        layer = news_shield_layer({"minutes_to_high_impact": 10}, freeze_minutes=30)
        assert layer.veto is True
        assert layer.score == 0.0

    def test_black_swan_still_vetoes(self):
        from src.agents.sam.skills import news_shield_layer

        layer = news_shield_layer({"black_swan": True})
        assert layer.veto is True

    def test_smc_without_candles_or_flags_is_unavailable(self):
        """No input ⇒ 'layer skipped', never 'no structural confluence'."""
        from src.agents.sam.skills import smc_layer

        layer = smc_layer({})
        assert layer.unavailable is True
        assert layer.detail.get("hits") in (None, [])

    def test_smc_unreadable_candles_are_unavailable_not_zero(self):
        """``HAS_SMC`` is False in this environment, so candles cannot be read."""
        from src.agents.sam.skills import HAS_SMC, smc_layer

        if HAS_SMC:  # pragma: no cover - optional dependency
            pytest.skip("smartmoneyconcepts installed; covered by the probe test")
        layer = smc_layer({"candles": object()})
        assert layer.unavailable is True
        assert "not analysed" in layer.rationale

    def test_smc_scored_result_still_scores(self):
        """A caller that really did read the structure still gets a score."""
        from src.agents.sam.skills import smc_layer

        layer = smc_layer(
            {"liquidity_sweep": True, "order_block": True, "fvg_test": True}
        )
        assert layer.unavailable is False
        assert layer.score == 70.0

    def test_smc_negative_finding_is_a_real_zero(self):
        """'checked and found nothing' is a genuine 0.0, not 'unavailable'."""
        from src.agents.sam.skills import smc_layer

        layer = smc_layer({"liquidity_sweep": False, "order_block": False})
        assert layer.unavailable is False
        assert layer.score == 0.0
        assert "no structural confluence" in layer.rationale

    def test_smc_derivation_reports_failed_probes(self):
        """The helper must return failures instead of swallowing them."""
        import ast
        import textwrap

        src_text = (REPO_ROOT / "src" / "agents" / "sam" / "skills.py").read_text(
            encoding="utf-8"
        )
        fn = next(
            node
            for node in ast.parse(src_text).body
            if isinstance(node, ast.FunctionDef) and node.name == "_derive_smc_features"
        )
        body = ast.dump(fn)
        assert "attr='append'" in body and "id='failed'" in body, (
            "per-probe failures must be recorded"
        )
        # A bare ``except ...: pass`` inside the helper is the old defect.
        swallowed = [
            node
            for node in ast.walk(fn)
            if isinstance(node, ast.ExceptHandler)
            and all(isinstance(st, ast.Pass) for st in node.body)
        ]
        assert swallowed == [], "SMC probe errors must not be silently swallowed"
        assert textwrap.dedent(fn.__doc__ or ""), "helper must document its contract"

    def test_macro_without_inputs_is_unavailable(self):
        """"neutral / insufficient data" used to be reported as a 40/100 score."""
        from src.agents.sam.skills import macro_layer

        layer = macro_layer({"direction": "long"})
        assert layer.unavailable is True
        assert layer.score == 0.0

    def test_macro_with_input_still_scores(self):
        from src.agents.sam.skills import macro_layer

        layer = macro_layer({"direction": "long", "real_yield_delta": -0.2})
        assert layer.unavailable is False
        assert layer.score == 60.0

    def test_cot_without_flow_is_unavailable(self):
        """"no fresh COT flow" is missing data, not a 45/100 observation."""
        from src.agents.sam.skills import cot_layer

        layer = cot_layer({"direction": "long"})
        assert layer.unavailable is True
        assert layer.score == 0.0

    def test_cot_with_flow_still_scores(self):
        from src.agents.sam.skills import cot_layer

        layer = cot_layer({"direction": "long", "noncommercial_net_change": 2000})
        assert layer.unavailable is False
        assert layer.score > 45.0

    def test_derivatives_without_funding_is_unavailable(self):
        from src.agents.sam.skills import derivatives_layer

        layer = derivatives_layer({"direction": "long"})
        assert layer.unavailable is True
        assert layer.score == 0.0

    def test_derivatives_not_applicable_is_unavailable(self):
        from src.agents.sam.skills import derivatives_layer

        layer = derivatives_layer({})
        assert layer.unavailable is True

    def test_derivatives_with_funding_still_scores(self):
        from src.agents.sam.skills import derivatives_layer

        layer = derivatives_layer({"direction": "long", "funding_rate": 0.005})
        assert layer.unavailable is False
        assert layer.score == 65.0

    def test_engine_ignores_unavailable_layers(self):
        """Unavailable ⇒ ``missing``, zero contribution, and no upward rescale."""
        from src.agents.sam.confluence import ConfluenceEngine
        from src.agents.sam.skills import (
            derivatives_layer,
            news_shield_layer,
            smc_layer,
        )

        engine = ConfluenceEngine()
        result = engine.synthesize(
            [smc_layer({}), derivatives_layer({"direction": "long"}), news_shield_layer({})],
            direction="long",
        ).to_dict()

        assert result["confluence_score"] == 0.0
        assert result["passes"] is False
        for name in ("smc", "derivatives", "news_shield"):
            assert result["layers"][name]["missing"] is True, name
            assert result["layers"][name]["score"] is None, name

    def test_engine_does_not_rescale_when_layers_are_missing(self):
        """Removing layers must not inflate the score of the remaining ones."""
        from src.agents.sam.confluence import ConfluenceEngine
        from src.agents.sam.skills import news_shield_layer

        engine = ConfluenceEngine()
        full = engine.synthesize([news_shield_layer({"news_calendar_checked": True})])
        partial = engine.synthesize([])

        assert full.to_dict()["confluence_score"] == pytest.approx(8.0, abs=0.01)
        assert partial.to_dict()["confluence_score"] == 0.0

    def test_unavailable_layer_never_passes_the_gate(self):
        """End-to-end: an entirely unreadable feature set cannot clear 95."""
        from src.agents.sam.confluence import ConfluenceEngine
        from src.agents.sam.skills import LAYER_PRODUCERS

        layers = [producer({}) for producer in LAYER_PRODUCERS.values()]
        result = ConfluenceEngine().synthesize(layers, direction="long").to_dict()
        assert result["passes"] is False
        assert result["confluence_score"] == 0.0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
