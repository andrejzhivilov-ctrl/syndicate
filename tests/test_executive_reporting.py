"""
Unit tests for SYNDICATE Executive Reporting Protocol:
- 03:00 Nightly System Audit & Backup
- 03:30 Daily Agent Self-Reflection, Self-Critique & Skill Genesis via Kodex (all 18 agents)
- 04:00 Mon & Thu Web Knowledge Harvest (under Marshal supervision) -> NotebookLM -> Alice Remote Machine Audit -> Obsidian
- 07:00 & 21:00 Eva Mandatory Telegram Briefing + TWO Kokoro-82M Voice Messages + PDF -> Google Drive -> Obsidian
- Sam 09:00 full market report & urgent alerts
- Atlas & Sonar '+' idle mode when no tasks assigned
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
    assert len(HOLDING_CHRONOGRAM_KYIV) >= 9
    # Verify Architect owns server health and Atlas owns geography with '+' idle mode
    assert "server_health_cpu_ram_ssd_docker" in AGENT_REPORT_SPECS["architect"]["morning_fields"]
    assert AGENT_REPORT_SPECS["atlas"]["default_idle_signal"] == "+"
    assert AGENT_REPORT_SPECS["jack"]["paper_betting_mode"] is True


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


def test_0330_self_reflection_skill_genesis_0400_alice_audit_and_0700_dual_voice_briefing(tmp_path: Path) -> None:
    vault = tmp_path / "obsidian_vault"
    gdrive = tmp_path / "gdrive"
    engine = ExecutiveReportEngine(obsidian_vault_path=vault, gdrive_staging_path=gdrive)

    # 1. 03:30 Agent Self-Reflection & Skill Genesis via Kodex
    ref_res = engine.run_0330_agent_self_reflection(
        agent_id="sam",
        date_str="2026-10-26",
        actions_reviewed_count=18,
        mistakes_found=["Занадто ранній алерт по ETH до закриття 4H свічки"],
        what_learned=["Новий індикатор ліквідності CME Bitcoin Futures"],
        ideas_developed=["Додати фільтр волатильності на відкритті сесії NYSE о 16:30"],
        missing_resources=["Потрібен прямий вебхук Coinglass Funding Rate"],
        skill_requests_for_kodex=[
            {"skill_name": "crypto-cme-gap-detector", "target": "sam_profile", "reason": "Фільтр гепів CME"}
        ],
        score=94,
    )
    assert ref_res["status"] == "self_reflection_recorded"
    assert len(ref_res["kodex_skill_tasks_dispatched"]) == 1
    assert ref_res["kodex_skill_tasks_dispatched"][0]["command"] == "CMD:KODEX_CREATE_AND_BIND_SKILL"
    assert ref_res["kodex_skill_tasks_dispatched"][0]["skill_name"] == "crypto-cme-gap-detector"
    assert Path(ref_res["obsidian_path"]).exists()

    # 2. 04:00 Mon/Thu Web Harvest (under Marshal supervision) -> NotebookLM -> Alice Remote Audit -> Obsidian
    audit_res = engine.run_0400_biweekly_knowledge_harvest_and_alice_audit(
        date_str="2026-10-26",
        weekday_name="Понеділок",
        harvested_by_agent={
            "sonar": [{"title": "AI Agents 2026 Benchmark"}],
            "sam": [{"title": "CFTC COT Weekly Report"}],
            "doc": [{"title": "HRV Recovery Meta-Analysis"}],
        },
        marshal_supervision_passed=True,
    )
    assert audit_res["status"] == "knowledge_harvested_and_audited_by_alice"
    assert audit_res["marshal_supervision_passed"] is True
    assert audit_res["total_sources_uploaded_to_notebooklm"] == 3
    assert audit_res["alice_rpc_dispatched"]["command"] == "CMD:ALICE_KNOWLEDGE_AUDIT_AND_OBSIDIAN_EXPORT"
    assert audit_res["alice_rpc_dispatched"]["execution_node"] == "alice_dedicated_machine"
    assert Path(audit_res["obsidian_audit_note"]).exists()

    # 3. 07:00 Morning Briefing -> Mandatory Telegram + TWO Kokoro Voice Messages + PDF -> Google Drive -> Obsidian
    reports = {
        ag: {"headline": f"Звіт {ag.upper()} готовий", "kpi": "100%"}
        for ag in AGENT_REPORT_SPECS
    }
    # Test Atlas & Sonar idle '+' mode
    reports["atlas"] = {"headline": "+"}
    reports["sonar"] = {"headline": "+"}

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
    # Verify TWO voice messages (Voice #1 Full Briefing + CEO Ideas, Voice #2 News Briefing & Analysis)
    assert "мої власні ідеї та рекомендації як Генерального директора" in briefing["telegram_delivery"]["voice_1_full_briefing_and_ceo_ideas_uk"]
    assert "розгорнутий аналітичний дайжест новин" in briefing["telegram_delivery"]["voice_2_expanded_news_briefing_uk"]

    pdf_file = Path(briefing["google_drive"]["pdf_path"])
    assert pdf_file.exists()
    assert pdf_file.read_bytes().startswith(b"%PDF-1.4")

    obs_file = Path(briefing["obsidian"]["note_path"])
    assert obs_file.exists()
    obs_text = obs_file.read_text(encoding="utf-8")
    assert "Саморефлексія та самонавчання (03:30)" in obs_text
    assert "**+**" in obs_text


def test_alice_autonomous_daemon_reflection_and_bridge_report(tmp_path: Path) -> None:
    from src.agents.alice_autonomous_daemon import AliceAutonomousDaemon

    daemon = AliceAutonomousDaemon(obsidian_vault_path=tmp_path)
    reflection = daemon.run_0330_self_reflection(date_str="2026-10-26")
    assert reflection["agent_id"] == "alice"
    assert reflection["execution_node"] == "alice_dedicated_machine"
    assert reflection["kodex_skill_requests"][0]["command"] == "CMD:KODEX_CREATE_AND_BIND_SKILL"

    report = daemon.build_bridge_report_for_eva(period="morning_0700", date_str="2026-10-26")
    assert report["agent_id"] == "alice"
    assert len(report["own_rd_ideas_and_proposals"]) >= 2
