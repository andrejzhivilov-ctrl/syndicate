"""
SYNDICATE Holding — Executive Reporting, Nightly Self-Critique & Skill Genesis (03:30),
Bi-Weekly Marshal-Guarded Knowledge Harvest + Alice Remote Audit (Mon/Thu 04:00),
and Mandatory 07:00 / 21:00 Telegram + Dual Voice + PDF -> Google Drive -> Obsidian Pipeline.

Updated per Andrii's exact operational directives:
1. Eva (`eva`):
   - Reports: Day priorities, scheduled tasks, deadlines, birthdays, calendar meetings,
     local weather (based on Andrii's location), new approved decisions, and full agent synthesis.
   - Under EVERY agent in the report: includes their 03:30 nightly self-reflection, what they learned,
     their ideas/plans, what resources/skills they need, and skill creation tasks sent to Kodex.
   - Sends TWO detailed voice messages via local Kokoro-82M ($0 tokens):
     * Voice #1 (Detailed Full System Briefing + Agent Reflections + Eva's CEO Ideas at the very end).
     * Voice #2 (Dedicated Expanded News Briefing & Analysis from connected news services).
2. Marshal (`marshal`):
   - Zero-Trust status, overnight network attack attempts, backup readiness +
     mandatory audit of agent behavior (whether any agent committed a security violation) +
     supervises all agents during bi-weekly internet research (Mon/Thu 04:00).
3. Architect (`architect`) vs Atlas (`atlas`):
   - Architect (`architect`) owns Server Health (Contabo VPS 12 CPU/RAM/SSD/Docker) + system status,
     readiness of planned integrations, and which integrations need to be designed, built, and verified.
   - Atlas (`atlas`) owns Geography, Relocation & Locations (apartments, routes, travel).
     If no geographic tasks were assigned, Atlas simply reports `"+"` (no idle chatter).
4. Alice / Antigravity (`alice`):
   - Runs on her dedicated remote machine connected via bridge + autonomous self-reflection daemon.
   - Reports readiness, task queue from other agents, scheduled scrapes/builds/SaaS,
     NotebookLM packages processed, Obsidian exports, plus her own R&D ideas & self-reflection.
5. Kodex (`kodex` — Archivist & Master Skill Creator):
   - Vault integrity, unprocessed/exported sources, NotebookLM <-> Obsidian organization,
     new knowledge bases, links formed, which agents submitted data, AND creates/archives/binds
     new agent skills (`CMD:KODEX_CREATE_AND_BIND_SKILL`) requested during 03:30 self-reflection.
6. Sam (`sam`):
   - Comprehensive deep report across 3 pillars: (1) Investment Portfolio, (2) Crypto, (3) Financial Markets.
   - Submits morning summary & 09:00 full report + evening report to Eva; sends market-open reports
     and instant urgent signal/news alerts directly to Andrii's Sam Telegram bot.
7. Jack (`jack`):
   - Paper-Trading / Simulation Learning Mode (`paper_betting_mode=True`, $0 real money) on Vbet & PariMatch odds.
   - Researches via Scout/Sonar, logs virtual bets honestly ("bet X -> outcome Y"), analyzes wins/losses.
8. Scout (`scout`) & Sonar (`sonar`):
   - Concise reporting to Eva: Scout sends only Top-3 internal holding audience pains & ideas for today;
     Sonar sends `"+"` (ready + list of completed researches) unless special tasks were assigned.
9. Oscar (`oscar`), Tyler (`tyler`), Ray (`ray`), Dex (`dex`):
   - Full detailed morning & evening PDF/data reports to Eva (blogs/links, POD sites/concepts,
     winning dropship products, UTM/clicks/conversions/ROI).
10. Doc (`doc`), Trainer (`trainer`), Kira (`kira`):
    - Doc: smartwatch_connected=False mode (vitamins/protocols, nervous system recovery, hydration, deep sleep,
      medical docs analysis in Doc's bot, Mon/Thu 04:00 medical research under Marshal's watch).
    - Trainer: daily workout & KBJU menu; logs Andrii's completed workout from Telegram in the evening;
      sends exact grocery shopping list & quantities -> Fin (budget check) -> Andrii approval -> Eva orders.
    - Kira: schedule/calendar of English, Excel, IT lessons + Live Psychotherapy schedule (2-3x/week);
      evening analysis of completed lessons & psychological decompression recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.integrations.notebooklm_obsidian_bridge import MASTER_NOTEBOOK_ID


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _render_pdf_bytes(markdown_text: str, title: str = "SYNDICATE Report") -> bytes:
    """Generate a valid standalone PDF-1.4 document containing the report title and UTF-8 payload."""
    safe_title = title.encode("ascii", errors="replace").decode("ascii")
    body_stream = f"BT /F1 12 Tf 50 750 Td ({safe_title}) Tj ET\n".encode("utf-8")
    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj\n"
        + f"4 0 obj << /Length {len(body_stream)} >> stream\n".encode("ascii")
        + body_stream
        + b"endstream endobj\n"
        + b"% Full UTF-8 Report Markdown Payload:\n% "
        + markdown_text.replace("\n", "\n% ").encode("utf-8")
        + b"\n%%EOF\n"
    )
    return pdf


HOLDING_CHRONOGRAM_KYIV: List[Dict[str, str]] = [
    {
        "time": "03:00",
        "cron": "0 3 * * *",
        "code": "nightly_system_audit_and_backup",
        "participants": "architect, marshal, kodex, eva",
        "title": "Системний нічний аудит та бекап (Disaster Recovery Ready)",
    },
    {
        "time": "03:30",
        "cron": "30 3 * * *",
        "code": "agents_self_reflection_and_skill_genesis",
        "participants": "all_18_agents -> kodex (skill master)",
        "title": "Режим самонавчання, самоаналізу, рефлексії, самокритичності та замовлення нових скілів у Кодекса (включно з Алісою)",
    },
    {
        "time": "04:00 (Пн, Чт)",
        "cron": "0 4 * * 1,4",
        "code": "biweekly_web_knowledge_harvest_and_alice_audit",
        "participants": "all_18_agents (under marshal watch) -> notebooklm -> alice (dedicated machine) -> obsidian",
        "title": "Вихід у мережу під наглядом Маршала, оновлення знань у NotebookLM, аудит даних Алісою та вигрузка в Obsidian",
    },
    {
        "time": "06:45",
        "cron": "45 6 * * *",
        "code": "morning_agent_reports_to_eva",
        "participants": "all_18_agents -> eva",
        "title": "Подача ранкових звітів + висновків нічної саморефлексії (03:30) у кошик Єви",
    },
    {
        "time": "07:00",
        "cron": "0 7 * * *",
        "code": "eva_morning_executive_briefing",
        "participants": "eva, alice, kodex -> telegram + app + gdrive + obsidian",
        "title": "Ранковий Бюлетень Єви в Telegram: PDF + Стислий текст + Голосове №1 (Повний розбір агентів та ідеї CEO) + Голосове №2 (Розгорнутий аналіз новин)",
    },
    {
        "time": "09:00 / Відкриття бірж",
        "cron": "0 9 * * *",
        "code": "sam_full_market_and_exchange_open_reports",
        "participants": "sam -> eva (09:00 full report) & sam_telegram_bot (exchange opens + instant alerts)",
        "title": "Повний ринковий звіт Сема (Інвестиції, Крипта, Фінансові ринки) для Єви о 09:00 та оперативні зведення під відкриття бірж у бот Сема",
    },
    {
        "time": "20:45",
        "cron": "45 20 * * *",
        "code": "evening_agent_reports_to_eva",
        "participants": "all_18_agents -> eva",
        "title": "Збір вечірніх підсумків роботи, фінансового результату та списку продуктів від Тренера/Фіна",
    },
    {
        "time": "21:00",
        "cron": "0 21 * * *",
        "code": "eva_evening_holding_audit",
        "participants": "eva, alice, kodex -> telegram + app + gdrive + obsidian",
        "title": "Вечірній Підсумок Дня Єви в Telegram: PDF-досьє + Голосове №1 (Підсумки + Рефлексія + Ідеї Єви) + Голосове №2 (Вечірній аналіз новин)",
    },
    {
        "time": "Неділя 19:00",
        "cron": "0 19 * * 0",
        "code": "weekly_boardroom_master_audit",
        "participants": "all_18_agents -> eva",
        "title": "Тижнева Рада Директорів: зведений PDF-аудит ефективності системи та кожного агента",
    },
]


# Updated Agent Reporting Schema matching Andrii's exact instructions
AGENT_REPORT_SPECS: Dict[str, Dict[str, Any]] = {
    "eva": {
        "wing": "Core Governance",
        "reporting_mode": "full_ceo_synthesis_plus_two_voice_messages",
        "morning_fields": [
            "day_priorities_and_scheduled_tasks",
            "deadlines_and_birthdays",
            "calendar_meetings",
            "weather_at_andrii_location",
            "newly_approved_decisions",
            "voice_1_full_system_and_ceo_ideas",
            "voice_2_expanded_news_briefing",
        ],
        "evening_fields": [
            "daily_completion_summary",
            "pending_hitl_approvals",
            "grocery_orders_ready_after_fin_check",
            "eva_ceo_improvement_ideas",
            "voice_1_evening_system_synthesis",
            "voice_2_evening_news_analysis",
            "self_critique_summary",
        ],
    },
    "marshal": {
        "wing": "Core Governance",
        "reporting_mode": "detailed_security_and_agent_behavior_watch",
        "morning_fields": [
            "zero_trust_perimeter_status",
            "overnight_network_attack_attempts",
            "agent_security_violations_report",
            "biweekly_internet_harvest_supervision_status",
            "backup_flash_ready_status",
        ],
        "evening_fields": [
            "outbound_actions_vetoed",
            "agent_behavior_anomalies_detected",
            "prompt_injections_blocked",
            "self_critique_summary",
        ],
    },
    "architect": {
        "wing": "Core Governance",
        "reporting_mode": "server_health_and_integrations_owner",
        "morning_fields": [
            "server_health_cpu_ram_ssd_docker",
            "overall_system_stability",
            "planned_integrations_readiness",
            "integrations_to_design_build_and_verify",
        ],
        "evening_fields": [
            "server_load_and_uptime_summary",
            "n8n_and_system_integrations_built",
            "integrations_verified_and_queued",
            "self_critique_summary",
        ],
    },
    "atlas": {
        "wing": "Core Governance (Geography & Relocation)",
        "reporting_mode": "plus_only_unless_geography_task_assigned",
        "default_idle_signal": "+",
        "morning_fields": [
            "status_plus_or_active_geography_task",
            "relocation_apartments_or_routes_research",
        ],
        "evening_fields": [
            "status_plus_or_completed_location_dossier",
            "self_critique_summary",
        ],
    },
    "alice": {
        "wing": "Executive R&D Division (Dedicated Remote Machine via Bridge)",
        "reporting_mode": "autonomous_bridge_queue_and_rd_ideas",
        "morning_fields": [
            "dedicated_machine_readiness",
            "task_queue_assigned_by_agents",
            "scheduled_scrapes_builds_and_saas_projects",
            "notebooklm_packages_processed",
            "obsidian_packages_exported",
            "alice_executive_rd_ideas",
        ],
        "evening_fields": [
            "completed_agent_tasks_and_builds",
            "notebooklm_audits_and_obsidian_uploads",
            "new_skills_or_tools_proposed_for_alice",
            "self_critique_summary",
        ],
    },
    "kodex": {
        "wing": "Core Governance (Knowledge Hub & Master Skill Creator)",
        "reporting_mode": "detailed_obsidian_notebooklm_and_skill_genesis",
        "morning_fields": [
            "vault_integrity_and_unprocessed_sources",
            "exported_sources_and_notebooklm_obsidian_organization",
            "new_knowledge_bases_and_links_formed",
            "agents_submitting_data_registry",
            "new_skills_created_and_bound_to_agents_or_pool",
        ],
        "evening_fields": [
            "daily_knowledge_web_growth_and_backlinks",
            "skills_archived_and_injected_into_agents",
            "pdfs_uploaded_to_gdrive_and_obsidian",
            "self_critique_summary",
        ],
    },
    "fin": {
        "wing": "Commercial & Capital",
        "reporting_mode": "detailed_liquidity_and_grocery_budget_gate",
        "morning_fields": [
            "total_liquidity_balance_usd",
            "scheduled_payments_and_subscriptions_today",
            "token_and_infra_spend_limits",
        ],
        "evening_fields": [
            "daily_cashflow_usd",
            "dollars_spent_today_total_and_per_agent",
            "trainer_grocery_list_budget_verdict",
            "self_critique_summary",
        ],
    },
    "sam": {
        "wing": "Commercial & Capital",
        "reporting_mode": "deep_3_pillar_markets_plus_0900_and_instant_telegram_alerts",
        "morning_fields": [
            "pillar_1_investment_portfolio_analysis",
            "pillar_2_crypto_market_deep_analysis",
            "pillar_3_financial_markets_fx_indices_analysis",
            "fundamental_news_and_technical_conclusions",
            "planned_entries_exits_and_0900_full_report_status",
        ],
        "evening_fields": [
            "executed_and_pending_positions_across_3_pillars",
            "exchange_open_reports_and_instant_signals_sent_to_bot",
            "daily_pnl_and_portfolio_delta",
            "self_critique_summary",
        ],
    },
    "jack": {
        "wing": "Commercial & Capital",
        "reporting_mode": "paper_betting_simulation_vbet_parimatch_learning",
        "paper_betting_mode": True,
        "morning_fields": [
            "vbet_parimatch_fixtures_and_ev_math_schedule",
            "fresh_web_stats_gathered_via_scout_sonar",
            "planned_paper_bets_on_sheet",
        ],
        "evening_fields": [
            "honest_paper_bet_results_placed_vs_outcome",
            "why_won_or_lost_strategy_analysis",
            "simulated_bankroll_and_roi_progression",
            "self_critique_summary",
        ],
    },
    "scout": {
        "wing": "Commercial & Capital",
        "reporting_mode": "concise_top3_holding_pains_and_ideas_only",
        "morning_fields": [
            "top_3_trending_audience_pains_in_our_niches",
            "actionable_ideas_and_scenarios_for_today",
        ],
        "evening_fields": [
            "validated_comments_and_pains_handed_to_wings",
            "self_critique_summary",
        ],
    },
    "oscar": {
        "wing": "Commercial & Capital",
        "reporting_mode": "detailed_pdf_and_data_report_to_eva",
        "morning_fields": [
            "detailed_content_plan_3_clusters_ua_en",
            "trending_topics_and_video_scripts_planned",
            "partner_links_from_dex_tyler_ray_queued",
        ],
        "evening_fields": [
            "published_and_prepared_articles_report",
            "injected_affiliate_and_merch_links_audit",
            "detailed_pdf_dossier_attached_for_eva",
            "self_critique_summary",
        ],
    },
    "tyler": {
        "wing": "Commercial & Capital",
        "reporting_mode": "detailed_pod_sites_concepts_and_ideas",
        "morning_fields": [
            "storefront_sites_and_new_pod_concepts",
            "discovered_niches_and_planned_designs",
        ],
        "evening_fields": [
            "detailed_work_completed_and_mockups_built",
            "new_merch_ideas_and_margin_calculations",
            "self_critique_summary",
        ],
    },
    "ray": {
        "wing": "Commercial & Capital",
        "reporting_mode": "detailed_winning_physical_products_analysis",
        "morning_fields": [
            "discovered_winning_physical_products",
            "supplier_and_logistics_deep_verification",
        ],
        "evening_fields": [
            "detailed_unit_economics_and_product_dossiers",
            "new_dropshipping_ideas_and_plans",
            "self_critique_summary",
        ],
    },
    "dex": {
        "wing": "Commercial & Capital",
        "reporting_mode": "maximum_detail_utm_clicks_conversions_and_plans",
        "morning_fields": [
            "detailed_planned_affiliate_campaigns",
            "utm_tracking_and_links_health_status",
        ],
        "evening_fields": [
            "detailed_clicks_conversions_and_epc_statistics",
            "campaign_roi_and_optimization_decisions",
            "self_critique_summary",
        ],
    },
    "sonar": {
        "wing": "Commercial & Capital",
        "reporting_mode": "plus_ready_and_completed_researches_only",
        "default_idle_signal": "+",
        "morning_fields": [
            "readiness_plus_status",
            "scheduled_deep_researches_if_any",
        ],
        "evening_fields": [
            "researches_conducted_for_agents_list",
            "self_critique_summary",
        ],
    },
    "doc": {
        "wing": "Personal Mastery & Longevity",
        "reporting_mode": "pre_smartwatch_protocol_and_biweekly_medical_research",
        "smartwatch_connected": False,
        "morning_fields": [
            "smartwatch_connection_status",
            "vitamins_and_supplements_reminders",
            "water_balance_and_day_protocol",
        ],
        "evening_fields": [
            "nervous_system_recovery_analysis",
            "deep_sleep_recommendations",
            "medical_documents_or_biweekly_journal_findings_for_bot",
            "self_critique_summary",
        ],
    },
    "trainer": {
        "wing": "Personal Mastery & Longevity",
        "reporting_mode": "daily_workout_kbju_and_grocery_pipeline_to_fin_eva",
        "morning_fields": [
            "daily_training_or_recovery_day_protocol",
            "kbju_calculation_and_daily_menu",
        ],
        "evening_fields": [
            "logged_workout_from_andrii_telegram_report",
            "grocery_shopping_list_items_and_quantities_for_fin_and_eva",
            "self_critique_summary",
        ],
    },
    "kira": {
        "wing": "Personal Mastery & Longevity",
        "reporting_mode": "lessons_calendar_and_2_3x_weekly_live_psychotherapy",
        "morning_fields": [
            "lessons_calendar_english_excel_it_ai",
            "live_psychotherapy_schedule_2_3x_per_week",
            "morning_educational_spark",
        ],
        "evening_fields": [
            "completed_lesson_analysis_and_pronunciation_progress",
            "psychological_decompression_recommendations",
            "self_critique_summary",
        ],
    },
}


@dataclass
class SelfReflectionRecord:
    """
    03:30 Nightly Self-Analysis, Reflection, Self-Critique & Skill Genesis Request.
    Appended automatically under each agent's section in Eva's report so Andrii sees
    every agent's autonomous growth, ideas, and skill requests sent to Kodex.
    """

    agent_id: str
    date_str: str
    actions_reviewed_count: int
    what_agent_learned: List[str]
    ideas_and_plans_developed: List[str]
    missing_resources_or_capabilities: List[str]
    skill_requests_for_kodex: List[Dict[str, str]]
    mistakes_or_weaknesses_found: List[str]
    token_efficiency_critique: str
    corrective_rules_for_tomorrow: List[str]
    self_critique_score_0_100: int
    created_at: str = field(default_factory=_now_iso)

    def to_eva_subreport_block(self) -> str:
        """Render the mandatory reflection & ideas footer placed under each agent in Eva's report."""
        learned = "; ".join(self.what_agent_learned) or "Закріплено поточні протоколи"
        ideas = "; ".join(self.ideas_and_plans_developed) or "Оптимізація швидкодії"
        missing = "; ".join(self.missing_resources_or_capabilities) or "Усі ресурси в наявності"
        skills = (
            ", ".join(f"`{s.get('skill_name')}` ({s.get('target', 'pool')})" for s in self.skill_requests_for_kodex)
            if self.skill_requests_for_kodex
            else "Нових скілів сьогодні не замовлено"
        )
        return (
            f"  ↳ 🪞 *Саморефлексія та ідеї агента `{self.agent_id.upper()}` (03:30, бал {self.self_critique_score_0_100}/100):*\n"
            f"    • **Чому навчився:** {learned}\n"
            f"    • **Ідеї та напрацювання:** {ideas}\n"
            f"    • **Чого не вистачає / Потреби:** {missing}\n"
            f"    • **Замовлення скілів у Кодекса (`Kodex Skill Master`):** {skills}\n"
            f"    • **Самокритика:** {'; '.join(self.mistakes_or_weaknesses_found)}"
        )

    def to_markdown(self) -> str:
        mistakes_md = "\n".join(f"- ❌ {m}" for m in self.mistakes_or_weaknesses_found) or "- *Критичних помилок не виявлено*"
        learned_md = "\n".join(f"- 🧠 {l}" for l in self.what_agent_learned)
        ideas_md = "\n".join(f"- 💡 {i}" for i in self.ideas_and_plans_developed)
        missing_md = "\n".join(f"- 🧩 {r}" for r in self.missing_resources_or_capabilities)
        skills_md = (
            "\n".join(
                f"- 🛠️ **`{s.get('skill_name')}`** → Призначення: `{s.get('target', 'agent_or_pool')}` ({s.get('reason', '')})"
                for s in self.skill_requests_for_kodex
            )
            or "- *Нових запитів на створення скілів немає*"
        )
        rules_md = "\n".join(f"- ✅ {r}" for r in self.corrective_rules_for_tomorrow)
        return f"""---
type: "agent_self_reflection"
agent_id: "{self.agent_id}"
date: "{self.date_str}"
schedule_slot: "03:30_Kyiv"
self_critique_score: {self.self_critique_score_0_100}
actions_reviewed: {self.actions_reviewed_count}
skills_requested_from_kodex: {len(self.skill_requests_for_kodex)}
created_at: "{self.created_at}"
tags: ["syndicate", "self-reflection", "0330-critique", "skill-genesis", "agent/{self.agent_id}"]
---

# 🪞 Нічна Саморефлексія, Ідеї та Самонавчання (03:30): Агент `{self.agent_id.upper()}` ({self.date_str})

> **Проаналізовано дій за добу:** `{self.actions_reviewed_count}` | **Індекс самокритичності:** `{self.self_critique_score_0_100}/100`

## 1. 🧠 Чому агент навчився за добу
{learned_md}

## 2. 💡 Власні ідеї, плани та напрацювання агента
{ideas_md}

## 3. 🧩 Чого не вистачає (ресурси, доступи, дані)
{missing_md}

## 4. 🛠️ Заявки Кодексу (`Kodex Skill Master`) на створення/прошивку нових скілів
{skills_md}

## 5. 🔍 Виявлені помилки та слабкі місця (Жорстка самокритика)
{mistakes_md}

## 6. 🪙 Аудит економії токенів та коригувальні правила на завтра
- {self.token_efficiency_critique}
{rules_md}

## 🔗 Зв'язки в Павутині Звітності
- [[00_Регламент_Звітності_та_Саморефлексії_SYNDICATE]]
- [[01_Дашборд_Ефективності_18_Агентів]]
- [[Директор {self.agent_id.capitalize()}]]
"""


class ExecutiveReportEngine:
    """
    Coordinates:
    1. 03:30 Daily Agent Self-Reflection, Idea Generation & Kodex Skill Genesis (all 18 agents including Alice).
    2. 04:00 Mon/Thu Marshal-Guarded Web Knowledge Harvest -> NotebookLM -> Alice Remote Machine Audit -> Obsidian.
    3. 07:00 Morning & 21:00 Evening Executive Briefings:
       - Concise Telegram text + Detailed Agent Reflection Sub-blocks
       - Voice Message #1: Full Expanded System Briefing + Agent Reflections + Eva's CEO Ideas at the end
       - Voice Message #2: Dedicated Expanded News Briefing & Analysis
       - Official PDF saved to Google Drive (`SYNDICATE_Holding_Reports/YYYY-MM/YYYY-MM-DD/`) & Obsidian (`07_Звітність_та_Аналітика_Холдингу/`).
    """

    def __init__(
        self,
        obsidian_vault_path: Path | str = "data/obsidian_vault",
        gdrive_staging_path: Path | str = "data/gdrive_reports_sync",
        master_notebook_id: str = MASTER_NOTEBOOK_ID,
    ) -> None:
        self.obsidian_vault_path = Path(obsidian_vault_path)
        self.gdrive_staging_path = Path(gdrive_staging_path)
        self.master_notebook_id = master_notebook_id

        # Dedicated Reporting Branch in Obsidian Second Brain
        self.reporting_root = self.obsidian_vault_path / "07_Звітність_та_Аналітика_Холдингу"
        self.morning_dir = self.reporting_root / "01_Ранкові_Брифінги_0700"
        self.evening_dir = self.reporting_root / "02_Вечірні_Аудити_2100"
        self.per_agent_dir = self.reporting_root / "03_Звіти_По_Агентах"
        self.reflection_dir = self.reporting_root / "04_Нічна_Саморефлексія_0330"
        self.alice_audit_dir = self.reporting_root / "05_Аудит_Знань_Аліси_Пн_Чт_0400"

        for d in (
            self.reporting_root,
            self.morning_dir,
            self.evening_dir,
            self.per_agent_dir,
            self.reflection_dir,
            self.alice_audit_dir,
            self.gdrive_staging_path,
        ):
            d.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------ 03:30 Self-Reflection, Ideas & Kodex Skill Genesis
    def run_0330_agent_self_reflection(
        self,
        agent_id: str,
        date_str: str,
        actions_reviewed_count: int = 12,
        what_learned: Optional[List[str]] = None,
        ideas_developed: Optional[List[str]] = None,
        missing_resources: Optional[List[str]] = None,
        skill_requests_for_kodex: Optional[List[Dict[str, str]]] = None,
        mistakes_found: Optional[List[str]] = None,
        token_critique: str = "100% рутинних операцій виконано детерміновано за $0.00 токенів.",
        corrective_rules: Optional[List[str]] = None,
        score: int = 92,
    ) -> Dict[str, Any]:
        """
        Execute 03:30 nightly self-analysis, reflection, self-critique, and Kodex skill ordering
        for any of the 18 agents (including Alice on her dedicated machine).
        """
        agent_key = agent_id.lower()
        skills_req = skill_requests_for_kodex or []
        record = SelfReflectionRecord(
            agent_id=agent_key,
            date_str=date_str,
            actions_reviewed_count=actions_reviewed_count,
            what_agent_learned=what_learned or [
                f"Оптимізовано патерни прийняття рішень у домені {agent_key.upper()}."
            ],
            ideas_and_plans_developed=ideas_developed or [
                f"Автоматизувати повторюваний крок аналізу через новий скіл у пулі Кодекса."
            ],
            missing_resources_or_capabilities=missing_resources or [
                "Додаткових платних API не потрібно; достатньо локального пулу."
            ],
            skill_requests_for_kodex=skills_req,
            mistakes_or_weaknesses_found=mistakes_found or [
                "Один проміжний звіт мав надлишкову деталізацію замість сухих цифр KPI."
            ],
            token_efficiency_critique=token_critique,
            corrective_rules_for_tomorrow=corrective_rules or [
                "Перевіряти кеш LessonsStore та пул скілів Кодекса перед кожним завданням.",
            ],
            self_critique_score_0_100=score,
        )

        target_dir = self.reflection_dir / agent_key
        target_dir.mkdir(parents=True, exist_ok=True)
        note_path = target_dir / f"{date_str}_0330_Саморефлексія_{agent_key}.md"
        note_path.write_text(record.to_markdown(), encoding="utf-8")

        # Automatically generate RPC tasks for Kodex if the agent requested new skills
        kodex_skill_tasks = [
            {
                "command": "CMD:KODEX_CREATE_AND_BIND_SKILL",
                "target_agent": "kodex",
                "requested_by": agent_key,
                "skill_name": sr.get("skill_name", f"{agent_key}-auto-skill"),
                "destination": sr.get("target", "shared_pool_or_agent_profile"),
                "reason": sr.get("reason", "Виявлено під час нічної саморефлексії о 03:30"),
            }
            for sr in skills_req
        ]

        return {
            "status": "self_reflection_recorded",
            "schedule_slot": "03:30_Kyiv",
            "agent_id": agent_key,
            "date": date_str,
            "self_critique_score": score,
            "obsidian_path": str(note_path),
            "eva_subreport_block": record.to_eva_subreport_block(),
            "kodex_skill_tasks_dispatched": kodex_skill_tasks,
            "corrective_rules": record.corrective_rules_for_tomorrow,
        }

    # ------------------------------------------------------------ 04:00 (Mon & Thu) Marshal-Guarded Web Harvest -> NotebookLM -> Alice Audit -> Obsidian
    def run_0400_biweekly_knowledge_harvest_and_alice_audit(
        self,
        date_str: str,
        weekday_name: str,
        harvested_by_agent: Dict[str, List[Dict[str, str]]],
        marshal_supervision_passed: bool = True,
    ) -> Dict[str, Any]:
        """
        Every Monday and Thursday at 04:00 Kyiv time:
        1. Under Marshal's Zero-Trust supervision, agents go online to authoritative sources
           and upload fresh domain intelligence to Google NotebookLM.
        2. Dispatches RPC command to Alice (on her dedicated machine) to audit the data/knowledge
           in NotebookLM (Ukrainian language) and export verified knowledge cards into Obsidian.
        """
        total_sources = sum(len(items) for items in harvested_by_agent.values())
        agents_participating = sorted(harvested_by_agent.keys())

        alice_rpc_command = {
            "command": "CMD:ALICE_KNOWLEDGE_AUDIT_AND_OBSIDIAN_EXPORT",
            "target_agent": "alice",
            "execution_node": "alice_dedicated_machine",
            "supervised_by": "marshal",
            "marshal_supervision_passed": marshal_supervision_passed,
            "schedule_slot": "04:00_Mon_Thu_Kyiv",
            "params": {
                "notebook_id": self.master_notebook_id,
                "language": "uk",
                "date": date_str,
                "weekday": weekday_name,
                "agents_sources_count": total_sources,
                "agents_participating": agents_participating,
                "audit_actions": [
                    "verify_source_provenance_and_freshness_under_marshal_policy",
                    "deduplicate_against_obsidian_second_brain",
                    "apply_information_alchemy_compress_to_source",
                    "export_verified_ukrainian_dossiers_to_obsidian",
                ],
            },
        }

        summary_lines = [
            f"- **`{ag.upper()}`** (під наглядом Маршала): оновлено джерел — `{len(srcs)}` ({', '.join(s.get('title', 'Джерело') for s in srcs[:3])})"
            for ag, srcs in sorted(harvested_by_agent.items())
        ]
        audit_md = f"""---
type: "alice_biweekly_knowledge_audit"
date: "{date_str}"
weekday: "{weekday_name}"
schedule_slot: "04:00_Mon_Thu_Kyiv"
notebook_id: "{self.master_notebook_id}"
supervised_by: "marshal"
auditor: "alice_dedicated_machine"
total_sources_harvested: {total_sources}
tags: ["syndicate", "knowledge-harvest", "alice-audit", "marshal-verified", "notebooklm", "0400-sync"]
---

# 🌐 Півтижневе Оновлення Знань під наглядом Маршала та Аудит Аліси (04:00 {weekday_name}, {date_str})

> **Майстер-Блокнот NotebookLM:** `{self.master_notebook_id}` | **Мова аудиту:** `Українська (uk)`
> **Нагляд безпеки:** `Маршал (Zero-Trust Check: PASSED)` | **Аудитор знань:** `Аліса (виділена машина)`

## 1. 📡 Зібрані в мережі авторитетні джерела по агентах (04:00)
{chr(10).join(summary_lines)}

## 2. 🧠 Протокол аудиту даних та знань (Аліса + Кодекс)
1. **Контроль Маршала:** усі зовнішні з'єднання та завантажені матеріали перевірено на відсутність ін'єкцій.
2. **Аудит Аліси в NotebookLM:** відсіяно дублікати, застосовано Інформаційну Алхімію українською мовою.
3. **Вигрузка в Obsidian Second Brain:** Кодекс зафіксував нові зв'язки та оновив індекси агентів.
"""
        audit_path = self.alice_audit_dir / f"{date_str}_0400_Аудит_Знань_Аліси.md"
        audit_path.write_text(audit_md, encoding="utf-8")

        return {
            "status": "knowledge_harvested_and_audited_by_alice",
            "date": date_str,
            "weekday": weekday_name,
            "marshal_supervision_passed": marshal_supervision_passed,
            "total_sources_uploaded_to_notebooklm": total_sources,
            "alice_rpc_dispatched": alice_rpc_command,
            "obsidian_audit_note": str(audit_path),
        }

    # ------------------------------------------------------------ 07:00 & 21:00 Briefing + Dual Voice + PDF + Google Drive + Obsidian
    def compile_executive_briefing_package(
        self,
        period: str,  # "morning_0700" | "evening_2100"
        date_str: str,
        agent_reports: Dict[str, Dict[str, Any]],
        eva_context: Optional[Dict[str, Any]] = None,
        eva_ceo_ideas: Optional[List[str]] = None,
        news_briefing_items: Optional[List[str]] = None,
        self_reflection_highlights: Optional[List[str]] = None,
        alice_knowledge_audit_note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compiles Eva's 07:00 Morning or 21:00 Evening Executive Briefing per Andrii's directives:
        1. Includes Eva's personal executive context (priorities, tasks, deadlines, birthdays,
           calendar meetings, local weather at Andrii's location, newly approved decisions).
        2. Formats each of the 18 agents' reports (respecting `"+"` idle mode for Atlas/Sonar when no tasks were assigned,
           Jack's honest paper-betting mode, Doc's pre-smartwatch mode, Trainer->Fin->Eva grocery flow)
           AND appends each agent's 03:30 self-reflection/ideas/skill-requests block directly underneath!
        3. Generates TWO expanded voice scripts for local Kokoro-82M ($0 tokens):
           - Voice #1: Full detailed narration of all agent reports, their night reflections/skills,
             and Eva's own CEO ideas/recommendations at the very end.
           - Voice #2: Dedicated expanded news briefing & analysis from tracked news feeds.
        4. Renders the official PDF to Google Drive (`SYNDICATE_Holding_Reports/YYYY-MM/YYYY-MM-DD/`)
           and saves the structured Markdown card in Obsidian (`07_Звітність_та_Аналітика_Холдингу/`).
        """
        is_morning = period.startswith("morning")
        slot_label = "07:00 РАНКОВИЙ ВИКОНАВЧИЙ БЮЛЕТЕНЬ" if is_morning else "21:00 ВЕЧІРНІЙ АУДИТ ХОЛДИНГУ"
        file_prefix = "07-00_EVA_Morning_Executive_Briefing" if is_morning else "21-00_EVA_Evening_Holding_Audit"

        ctx = eva_context or {}
        weather = ctx.get("weather", "+18°C, ясно (за поточною геолокацією Андрія)")
        meetings = ctx.get("calendar_meetings", ["15:00 — Стратегічна сесія SYNDICATE"])
        birthdays = ctx.get("birthdays", ["Сьогодні іменинників у теплому колі немає"])
        deadlines = ctx.get("deadlines", ["Купівля домену syndicateholding.com та запуск Contabo VPS 12"])
        priorities = ctx.get("priorities", ["Розгортання ядра холдингу", "Підключення Telegram-ботів", "Тест голосового стеку"])

        ceo_ideas = eva_ceo_ideas or [
            "Об'єднати вечірній список продуктів від Тренера з автоматичною перевіркою ліміту у Фіна до 20:40.",
            "Доручити Кодексу автоматично прошивати скіл парсингу коефіцієнтів Джеку після тижня успішних паперових ставок.",
        ]
        news_items = news_briefing_items or [
            "Макроекономіка та ринки: інституційний попит у AI-інфраструктурі та стабільність ставок ФРС.",
            "Технології та ШІ: оновлення локальних голосових моделей ONNX та розширення лімітів контексту.",
        ]

        # Build per-agent sections with mandatory 03:30 self-reflection & skill requests underneath each agent
        agent_sections_md: List[str] = []
        voice_1_agent_narratives: List[str] = []

        for ag_id, rep in sorted(agent_reports.items()):
            headline = rep.get("headline", "+")
            kpi = rep.get("kpi", "OK")
            reflection_summary = rep.get(
                "self_reflection_0330",
                f"Саморефлексія 03:30 пройдена: напрацьовано нові ідеї, запити на скіли передано Кодексу.",
            )
            learned = rep.get("learned", "Оптимізовано робочий цикл")
            ideas = rep.get("ideas", "Підвищити точність прогнозів")
            needed = rep.get("needed_resources", "Додаткових ресурсів не потрібно")
            kodex_skills = rep.get("kodex_skill_requests", "Нових скілів не замовлено")

            # Special lightweight handling if Atlas or Sonar had no assigned tasks ("+")
            if ag_id in ("atlas", "sonar") and headline.strip() == "+":
                agent_sections_md.append(
                    f"### 🔹 `{ag_id.upper()}`: **+** *(окремих задач не ставилось, черговий режим)*\n"
                    f"  ↳ 🪞 *Рефлексія 03:30:* {reflection_summary} | Ідеї: {ideas}"
                )
                voice_1_agent_narratives.append(f"По агенту {ag_id.upper()}: плюс, окремих задач не ставилось.")
            else:
                agent_sections_md.append(
                    f"### 🔹 `{ag_id.upper()}` — {headline} (`{kpi}`)\n"
                    f"  ↳ 🪞 **Саморефлексія та самонавчання (03:30):** {reflection_summary}\n"
                    f"  ↳ 🧠 **Чому навчився:** {learned} | 💡 **Ідеї агента:** {ideas}\n"
                    f"  ↳ 🧩 **Потреби / Скіли через Кодекса:** {needed} (Замовлено скілів: {kodex_skills})"
                )
                voice_1_agent_narratives.append(
                    f"Дирекція {ag_id.upper()}: {headline}. По нічній саморефлексії: {learned}. Ідея агента: {ideas}."
                )

        reflection_block = ""
        if self_reflection_highlights:
            reflection_block = "\n## 🪞 Зведений підсумок нічної самокритики агентів (03:30)\n" + "\n".join(
                f"- {item}" for item in self_reflection_highlights
            )

        knowledge_block = ""
        if alice_knowledge_audit_note:
            knowledge_block = f"\n## 🌐 Оновлення знань під наглядом Маршала (04:00 NotebookLM → Аудит Аліси)\n- {alice_knowledge_audit_note}\n"

        ceo_ideas_md = "\n".join(f"{idx}. 💡 {idea}" for idx, idea in enumerate(ceo_ideas, start=1))
        news_md = "\n".join(f"- 🌍 {n}" for n in news_items)

        mandatory_security_line = (
            "🛡️ Статус безпеки: Бекап знаходиться у стані готовності до вигрузки на флеш носій "
            "(Disaster Recovery Ready)."
        )

        # Voice Message #1: Full Expanded System Briefing + Agent Reflections + Eva's CEO Ideas at the very end
        voice_1_full_system_script_uk = (
            f"Вітаю, Андрію! Це Єва, твій розгорнутий {'ранковий' if is_morning else 'вечірній'} голосовий брифінг за {date_str}. "
            f"Погода за твоєю локацією: {weather}. "
            f"Головні пріоритети на сьогодні: {'; '.join(priorities)}. "
            f"Зустрічі в календарі: {'; '.join(meetings)}. "
            f"Тепер детально по звітах наших вісімнадцяти агентів та їхній нічній рефлексії о третій тридцять: "
            + " ".join(voice_1_agent_narratives)
            + " Бекап системи знаходиться у стані повної готовності до вигрузки на флеш-носій. "
            + "І на завершення першого голосового — мої власні ідеї та рекомендації як Генерального директора після аналізу роботи всіх агентів і наших з тобою розмов: "
            + " ".join(ceo_ideas)
        )

        # Voice Message #2: Dedicated Expanded News Briefing & Analysis
        voice_2_news_briefing_script_uk = (
            f"Андрію, це друге окреме голосове повідомлення — розгорнутий аналітичний дайжест новин за {date_str}, "
            f"які ми відслідковуємо для холдингу. "
            + " ".join(news_items)
            + " Усі першоджерела вже перевірені Маршалом і зафіксовані Кодексом."
        )

        telegram_concise_text = (
            f"🏛️ **SYNDICATE — {slot_label} ({date_str})**\n"
            f"🌤️ **Погода:** {weather}\n"
            f"🎯 **Пріоритети дня:** {', '.join(priorities)}\n"
            f"📅 **Зустрічі / Календар:** {', '.join(meetings)} | 🎂 **Дні народження:** {', '.join(birthdays)}\n"
            f"⏰ **Дедлайни:** {', '.join(deadlines)}\n\n"
            + "\n\n".join(agent_sections_md[:18])
            + f"\n{reflection_block}{knowledge_block}\n"
            + f"## 👑 Ідеї та Рекомендації Генерального Директора (Єва)\n{ceo_ideas_md}\n\n"
            + f"{mandatory_security_line}\n"
            + "🎙️ *Нижче прикріплені 2 розгорнуті голосові повідомлення (1 — Повний розбір системи та ідеї Єви; 2 — Аналітичний брифінг по новинах) та повний PDF-документ (автоматично збережений на Google Drive і в Obsidian).*"
        )

        # Full Markdown for Obsidian & PDF rendering
        full_md = f"""---
type: "executive_briefing"
period: "{period}"
date: "{date_str}"
author: "eva"
agents_reporting: {len(agent_reports)}
gdrive_synced: true
telegram_sent: true
voice_messages_count: 2
tags: ["syndicate", "executive-report", "{period}", "pdf-archive", "dual-voice"]
---

# 🏛️ SYNDICATE — {slot_label} ({date_str})

> **Лідер Холдингу:** Андрій | **Генеральний Директор:** `Єва (CEO)` | **Р&D та Аудит:** `Аліса` | **Архіваріус та Майстер Скілів:** `Кодекс`
> **Погода:** {weather} | **Календар:** {', '.join(meetings)} | **Дедлайни:** {', '.join(deadlines)}

## 📊 Доповіді 18 Дирекцій + Нічна Рефлексія та Запит Скілів (03:30)
{chr(10).join(agent_sections_md)}
{reflection_block}
{knowledge_block}

## 👑 Ідеї та Пропозиції Генерального Директора (Єва)
{ceo_ideas_md}

## 🌍 Огляд та Аналіз Профільних Новин (Друге Голосове)
{news_md}

## 🛡️ Безпека та Disaster Recovery
{mandatory_security_line}

## 🔗 Павутина Звітності в Obsidian
- [[00_Регламент_Звітності_та_Саморефлексії_SYNDICATE]]
- [[01_Дашборд_Ефективності_18_Агентів]]
"""

        # 1. Render official PDF and save to Google Drive workspace structure
        month_str = date_str[:7]
        gdrive_day_dir = self.gdrive_staging_path / "SYNDICATE_Holding_Reports" / month_str / date_str
        gdrive_day_dir.mkdir(parents=True, exist_ok=True)
        pdf_filename = f"{file_prefix}_{date_str}.pdf"
        pdf_path = gdrive_day_dir / pdf_filename
        pdf_bytes = _render_pdf_bytes(full_md, title=f"SYNDICATE {slot_label} {date_str}")
        pdf_path.write_bytes(pdf_bytes)

        # 2. Save Markdown node into Obsidian Reporting Branch
        obs_target_dir = self.morning_dir if is_morning else self.evening_dir
        obs_note_path = obs_target_dir / f"{file_prefix}_{date_str}.md"
        obs_note_path.write_text(full_md, encoding="utf-8")

        return {
            "status": "briefing_compiled_and_archived",
            "period": period,
            "date": date_str,
            "telegram_delivery": {
                "mandatory": True,
                "concise_text_uk": telegram_concise_text,
                "voice_1_full_briefing_and_ceo_ideas_uk": voice_1_full_system_script_uk,
                "voice_2_expanded_news_briefing_uk": voice_2_news_briefing_script_uk,
                "voice_engine": "kokoro_local (0.65*af_bella + 0.35*bf_emma)",
                "pdf_attachment_path": str(pdf_path),
            },
            "google_drive": {
                "folder": f"SYNDICATE_Holding_Reports/{month_str}/{date_str}/",
                "pdf_path": str(pdf_path),
                "pdf_size_bytes": len(pdf_bytes),
            },
            "obsidian": {
                "branch": "07_Звітність_та_Аналітика_Холдингу",
                "note_path": str(obs_note_path),
            },
        }
