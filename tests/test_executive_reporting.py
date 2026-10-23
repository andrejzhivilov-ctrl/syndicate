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


def test_all_18_agents_live_modes_telegram_buttons_eva_telephony_and_hitl_skill_gate() -> None:
    from src.voice import (
        AGENT_LIVE_AND_BOT_SPECS,
        KNOWLEDGE_ACCESS_ARCHITECTURE,
        EvaTelephonySIPBridge,
        SkillIdeaApprovalGate,
        build_agent_telegram_keyboard,
    )

    # 1. All 18 agents have Live modes, voices, and interactive Telegram buttons
    assert len(AGENT_LIVE_AND_BOT_SPECS) == 18
    for agent_id in AGENT_LIVE_AND_BOT_SPECS:
        kb = build_agent_telegram_keyboard(agent_id)
        assert kb["agent_id"] == agent_id
        assert len(kb["inline_keyboard"]) >= 4

    # Content factory agents have content_factory_live mode
    for cf_agent in ("oscar", "tyler", "ray", "dex", "scout"):
        assert "content_factory_live" in AGENT_LIVE_AND_BOT_SPECS[cf_agent]["live_modes"]

    # 2. Eva SIP Telephony (Outbound call to Andrii, Inbound call from Andrii, Agent bridging)
    sip = EvaTelephonySIPBridge()
    out_call = sip.initiate_outbound_call_to_andrii(call_id="call-001", reason="Терміновий ранковий звіт")
    assert out_call["status"] == "outbound_sip_call_ringing_and_connected"
    in_call = sip.receive_inbound_call_from_andrii(call_id="call-002", caller_number="+380990000000")
    assert in_call["status"] == "inbound_sip_call_answered"
    bridged = sip.switch_or_bridge_agent_into_call(call_id="call-002", new_agent_id="ray")
    assert bridged["active_agent"] == "ray"

    # 3. Strict HITL Skill/Idea Approval Gate (Pending -> Personal Live Interview -> Approve via Eva -> Central System)
    gate = SkillIdeaApprovalGate()
    prop = gate.register_0330_proposal(
        proposal_id="prop-ray-01",
        agent_id="ray",
        title="cj-dropshipping-margin-scanner",
        what_it_gives_and_improves_uk="Автоматичний розрахунок чистої маржі з урахуванням доставки в ЄС та США",
    )
    assert prop.status == "PENDING_ANDRII_APPROVAL"

    interview = gate.request_personal_agent_interview("prop-ray-01")
    assert interview["status"] == "personal_interview_scheduled"
    assert "syndicate-ray" in interview["livekit_room"]

    approved = gate.approve_and_connect_via_eva("prop-ray-01")
    assert approved["status"] == "skill_approved_and_connected_to_central_system"
    assert approved["approved_by"] == "andrii"
    assert approved["gated_by"] == "eva"
    assert approved["central_registry_connected"] is True

    # 4. Shared Obsidian Read-All + 18 Dedicated NotebookLM Working Notebooks
    assert KNOWLEDGE_ACCESS_ARCHITECTURE["obsidian_second_brain"]["mode"] == (
        "SHARED_READ_ALL_WITH_SCOPED_WRITE_AND_KODEX_CURATION"
    )
    assert len(KNOWLEDGE_ACCESS_ARCHITECTURE["notebooklm_workspaces"]["per_agent_dedicated_notebooks"]) == 18


def test_selective_live_meetups_leader_seal_notebooklm_300_lifecycle_and_eva_alarm(tmp_path: Path) -> None:
    from src.voice import (
        EvaSmartAlarmAndReminderSystem,
        LeaderDocumentGuard,
        NotebookLMHubLifecycleManager,
        SyndicateLiveMeetupHub,
    )

    # 1. Selective Multi-Agent Live Meetup Room (e.g. Oscar + Ray + Dex) with $0 audio tokens
    meetup = SyndicateLiveMeetupHub()
    room = meetup.create_selective_meetup_room(
        room_id="cf-01",
        selected_agents=["oscar", "ray", "dex"],
        title="Контент-Завод: Інтеграція оферів",
    )
    assert room["status"] == "selective_meetup_room_ready"
    round_res = meetup.run_brainstorm_round(
        room_id="cf-01",
        andrii_prompt_uk="Обговоріть між собою зв'язку статей Оскара з товарами Рея та лінками Декса",
        obsidian_vault_path=tmp_path,
    )
    assert round_res["participants_count"] == 3
    assert round_res["audio_token_cost_usd"] == 0.0
    assert Path(round_res["obsidian_protocol_path"]).exists()

    # 2. Leader Digital Signature (`ANDRII_SOVEREIGN_SEAL_ED25519`): Read-All, Never Edit/Delete, Move only with approval
    signed_doc = LeaderDocumentGuard.sign_leader_markdown(
        content_md="# Стратегічний приватний документ Андрія",
        doc_title="Leader_Strategy_2026",
    )
    assert LeaderDocumentGuard.check_agent_operation(signed_doc, "ray", "read")["allowed"] is True
    assert LeaderDocumentGuard.check_agent_operation(signed_doc, "ray", "edit")["allowed"] is False
    assert LeaderDocumentGuard.check_agent_operation(signed_doc, "kodex", "delete")["allowed"] is False
    assert LeaderDocumentGuard.check_agent_operation(signed_doc, "kodex", "move", andrii_move_approved=False)["allowed"] is False
    assert LeaderDocumentGuard.check_agent_operation(signed_doc, "kodex", "move", andrii_move_approved=True)["allowed"] is True

    # 3. NotebookLM 300-Source Ephemeral Hub (Agent sources purged after full lossless MD export; Andrii's kept!)
    nlm = NotebookLMHubLifecycleManager(obsidian_vault_path=tmp_path)
    agent_batch = nlm.process_and_export_notebook_batch(
        agent_id="sam",
        sources=[{"title": "Macro Report", "full_text": "Повний розгорнутий текст звіту без стиснення."}],
        owner="agent",
    )
    assert agent_batch["full_expanded_uncompressed"] is True
    assert agent_batch["purged_from_notebooklm_after_export"] is True
    assert agent_batch["remaining_sources_in_notebooklm"] == 0

    andrii_batch = nlm.process_and_export_notebook_batch(
        agent_id="eva",
        sources=[{"title": "Особиста книга Андрія", "full_text": "Повний текст книги."}],
        owner="andrii",
    )
    assert andrii_batch["leader_signed"] is True
    assert andrii_batch["purged_from_notebooklm_after_export"] is False
    assert andrii_batch["remaining_sources_in_notebooklm"] == 1

    # 4. Eva 3-Stage Escalating Alarm Clock (60s Telegram -> 60s Telegram -> Real Mobile Phone Call on 3rd attempt)
    alarm = EvaSmartAlarmAndReminderSystem()
    att1 = alarm.trigger_alarm_attempt("06:50", attempt_number=1)
    assert att1["status"] == "telegram_sound_alarm_ringing_60s"
    assert att1["ring_duration_seconds"] == 60
    att3 = alarm.trigger_alarm_attempt("06:56", attempt_number=3)
    assert att3["status"] == "escalated_to_real_mobile_phone_call"

    # Reminder routing (Trainer handles meal/workout, escalates to Eva if unanswered >= 60 min)
    rem_meal = alarm.route_reminder("meal_calories", "Обід та підрахунок КБЖВ", "13:30", unanswered_minutes=0)
    assert rem_meal["primary_agent_bot"] == "trainer"
    assert rem_meal["active_delivery_agent"] == "trainer"
    rem_esc = alarm.route_reminder("vitamins", "Прийом вітамінів", "09:00", unanswered_minutes=65)
    assert rem_esc["backup_eva_escalation_triggered"] is True
    assert rem_esc["active_delivery_agent"] == "eva"


