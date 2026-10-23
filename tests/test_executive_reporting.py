"""
Unit tests for SYNDICATE Executive Reporting Protocol:
- 03:00 Nightly System Audit & Backup
- 03:30 Daily Agent Self-Reflection & Self-Critique (all 18 agents)
- 04:00 Mon & Thu Web Knowledge Harvest -> NotebookLM -> Alice Remote Machine Audit -> Obsidian
- 07:00 & 21:00 Eva Mandatory Telegram Briefing + Kokoro-82M Voice + PDF -> Google Drive -> Obsidian
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.proactive import build_full_holding_scheduler
from src.reporting import (
    AGENT_REPORT_SPECS,
    HOLDING_CHRONOGRAM_KYIV,
    ExecutiveReportEngine,
)


def test_all_18_agents_have_morning_evening_and_self_critique_specs() -> None:
    expected_18 = {
        "eva", "marshal", "architect", "atlas", "alice", "kodex",
        "fin", "sam", "jack", "scout", "oscar", "tyler", "ray", "dex", "sonar",
        "doc", "trainer", "kira",
    }
    assert set(AGENT_REPORT_SPECS.keys()) == expected_18
    for agent_id, spec in AGENT_REPORT_SPECS.items():
        assert len(spec["morning_fields"]) >= 2, agent_id
        assert "self_critique_summary" in spec["evening_fields"], agent_id
    assert len(HOLDING_CHRONOGRAM_KYIV) >= 8


def test_full_holding_scheduler_triggers_0330_reflection_0400_mon_thu_and_0700_2100() -> None:
    sched = build_full_holding_scheduler()

    # 03:30 any day -> agents_self_reflection_0330
    due_0330 = [j.name for j in sched.due(datetime(2026, 10, 26, 3, 30))]
    assert due_0330 == ["agents_self_reflection_0330"]

    # 04:00 Monday (2026-10-26 is Monday) -> biweekly_web_knowledge_harvest_0400
    due_mon_0400 = [j.name for j in sched.due(datetime(2026, 10, 26, 4, 0))]
    assert due_mon_0400 == ["biweekly_web_knowledge_harvest_0400"]

    # 04:00 Thursday (2026-10-29 is Thursday) -> biweekly_web_knowledge_harvest_0400
    due_thu_0400 = [j.name for j in sched.due(datetime(2026, 10, 29, 4, 0))]
    assert due_thu_0400 == ["biweekly_web_knowledge_harvest_0400"]

    # 04:00 Tuesday (2026-10-27 is Tuesday) -> empty!
    due_tue_0400 = [j.name for j in sched.due(datetime(2026, 10, 27, 4, 0))]
    assert due_tue_0400 == []

    # 07:00 Morning & 21:00 Evening Telegram + PDF Briefings
    assert [j.name for j in sched.due(datetime(2026, 10, 26, 7, 0))] == ["eva_morning_telegram_briefing_0700"]
    assert [j.name for j in sched.due(datetime(2026, 10, 26, 21, 0))] == ["eva_evening_telegram_briefing_2100"]


def test_0330_self_reflection_0400_alice_audit_and_0700_pdf_gdrive_obsidian_pipeline(tmp_path: Path) -> None:
    vault = tmp_path / "obsidian_vault"
    gdrive = tmp_path / "gdrive"
    engine = ExecutiveReportEngine(obsidian_vault_path=vault, gdrive_staging_path=gdrive)

    # 1. 03:30 Agent Self-Reflection & Self-Critique
    ref_res = engine.run_0330_agent_self_reflection(
        agent_id="sam",
        date_str="2026-10-26",
        actions_reviewed_count=18,
        mistakes_found=["Занадто ранній алерт по ETH до закриття 4H свічки"],
        score=94,
    )
    assert ref_res["status"] == "self_reflection_recorded"
    assert Path(ref_res["obsidian_path"]).exists()

    # 2. 04:00 Mon/Thu Web Harvest -> NotebookLM -> Alice Remote Audit -> Obsidian
    audit_res = engine.run_0400_biweekly_knowledge_harvest_and_alice_audit(
        date_str="2026-10-26",
        weekday_name="Понеділок",
        harvested_by_agent={
            "sonar": [{"title": "AI Agents 2026 Benchmark"}],
            "sam": [{"title": "CFTC COT Weekly Report"}],
            "doc": [{"title": "HRV Recovery Meta-Analysis"}],
        },
    )
    assert audit_res["status"] == "knowledge_harvested_and_audited_by_alice"
    assert audit_res["total_sources_uploaded_to_notebooklm"] == 3
    assert audit_res["alice_rpc_dispatched"]["command"] == "CMD:ALICE_KNOWLEDGE_AUDIT_AND_OBSIDIAN_EXPORT"
    assert audit_res["alice_rpc_dispatched"]["execution_node"] == "alice_dedicated_machine"
    assert Path(audit_res["obsidian_audit_note"]).exists()

    # 3. 07:00 Morning Briefing -> Mandatory Telegram + Kokoro Voice + PDF -> Google Drive -> Obsidian
    reports = {
        ag: {"headline": f"Звіт {ag.upper()} готовий", "kpi": "100%"}
        for ag in AGENT_REPORT_SPECS
    }
    briefing = engine.compile_executive_briefing_package(
        period="morning_0700",
        date_str="2026-10-26",
        agent_reports=reports,
        self_reflection_highlights=["Усі 18 агентів провели самокритику о 03:30 (середній бал: 93/100)."],
        alice_knowledge_audit_note="Аліса провела аудит 3 нових джерел у NotebookLM та оновила Obsidian.",
    )
    assert briefing["status"] == "briefing_compiled_and_archived"
    assert briefing["telegram_delivery"]["mandatory"] is True
    assert "Disaster Recovery Ready" in briefing["telegram_delivery"]["concise_text_uk"]

    pdf_file = Path(briefing["google_drive"]["pdf_path"])
    assert pdf_file.exists()
    assert pdf_file.read_bytes().startswith(b"%PDF-1.4")

    obs_file = Path(briefing["obsidian"]["note_path"])
    assert obs_file.exists()
