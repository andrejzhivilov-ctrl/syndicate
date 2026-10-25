"""Behavioral tests for Oscar 3-Cluster Bilingual Blog Matrix, Scout, Dex, Ray, and Atlas."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from deploy.runtime.director_runner import AGENTS
from src.agents.atlas import AtlasAgent
from src.agents.dex import DexAgent
from src.agents.oscar import OscarAgent
from src.agents.oscar.agent import LEGAL_DISCLAIMERS
from src.agents.ray import RayAgent
from src.agents.scout import ScoutAgent
from src.agents.sonar import SonarAgent
from src.runtime_config import build_runtime_config


def run(agent, action, **payload):
    return asyncio.run(agent.execute({"action": action, **payload}))


@pytest.fixture(autouse=True)
def director_data(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))


@pytest.mark.parametrize("cls", [ScoutAgent, DexAgent, RayAgent, AtlasAgent, SonarAgent])
def test_new_directors_reject_unknown_actions(cls):
    result = run(cls(), "unknown_action_xyz")
    assert result["status"] == "error"
    assert result["available_actions"] == sorted(cls.ACTIONS)


@pytest.mark.parametrize(
    "cls,blocked_action",
    [
        (ScoutAgent, "launch_campaign"),
        (DexAgent, "activate_paid_traffic"),
        (RayAgent, "place_supplier_order"),
        (AtlasAgent, "book_ticket"),
        (SonarAgent, "live_scrape"),
        (SonarAgent, "autonomous_crawl"),
    ],
)
def test_new_directors_block_external_spend_without_hitl(cls, blocked_action):
    result = run(cls(), blocked_action, approved=True, grants=["*"])
    assert result["status"] == "approval_required"
    assert result["executed"] is False


def test_oscar_clusters_and_bilingual_legal_disclaimers():
    clusters_res = run(OscarAgent(), "clusters")
    assert clusters_res["status"] == "ok"
    cluster_ids = {c["cluster_id"] for c in clusters_res["clusters"]}
    assert cluster_ids == {"health_fitness", "ai_tech", "finance_ecommerce"}

    class MockClient:
        async def ainvoke(self, messages):
            return SimpleNamespace(content="## Bilingual Article Body\n\nEvidence-based insights.")

    oscar = OscarAgent(providers={"grok": MockClient()})

    for cluster_id, expected_type in [
        ("health_fitness", "health"),
        ("ai_tech", "tech_info"),
        ("finance_ecommerce", "finance"),
    ]:
        for lang in ("ua", "en"):
            res = run(
                oscar,
                "blog_article",
                cluster_id=cluster_id,
                language=lang,
                topic="Systemic test topic",
                monetization_links=["https://example.com/aff?subid=oscar_test"],
            )
            assert res["status"] == "ok"
            assert res["cluster_id"] == cluster_id
            assert res["language"] == lang
            assert res["legal_disclaimer"] == LEGAL_DISCLAIMERS[expected_type][lang]
            assert res["non_solicitation_compliant"] is True
            assert res["publication_state"] == "draft"


def test_scout_niche_analysis_and_marketing_brief():
    scout = ScoutAgent()
    niche = run(
        scout,
        "analyze_niche",
        niche="AI Workflow Automation",
        monthly_search_volume=45000,
        competition_index=35,
        avg_cpc_usd=2.50,
    )
    assert niche["status"] == "ok"
    assert niche["analysis"]["niche"] == "AI Workflow Automation"
    assert niche["analysis"]["verdict"] == "high_priority"

    pains = run(
        scout,
        "extract_pains",
        comments=[
            {"id": "c1", "channel": "youtube", "text": "Як налаштувати n8n без помилок? email a@b.com"},
            {"id": "c2", "channel": "reddit", "text": "Too expensive API tokens, problem with billing"},
        ],
    )
    assert pains["status"] == "ok"
    assert pains["total_processed"] == 2
    assert pains["pain_points_count"] == 2
    assert "a@b.com" not in json.dumps(pains)

    brief = run(
        scout,
        "marketing_brief",
        niche="Zero-Token Architecture",
        pain_point="Висока вартість токенів при автоматизації",
        target_wing="oscar",
    )
    assert brief["status"] == "ok"
    assert brief["brief"]["target_wing"] == "oscar"
    assert len(run(scout, "briefs")["records"]) == 1


def test_dex_offer_scoring_and_funnel_builder():
    dex = DexAgent()
    scored = run(
        dex,
        "score_offer",
        offer_name="Cloud GPU SaaS Referral",
        network="saas_direct",
        payout_usd=75.0,
        conversion_rate_pct=3.5,
        refund_rate_pct=4.0,
    )
    assert scored["status"] == "ok"
    assert scored["offer"]["approved"] is True

    funnel = run(
        dex,
        "build_funnel",
        funnel_name="AI SaaS Funnel",
        offer_name="Cloud GPU SaaS Referral",
        cluster="ai_tech",
        lead_magnet="Free n8n Blueprint",
    )
    assert funnel["status"] == "ok"
    assert funnel["funnel"]["state"] == "draft_only"

    links = run(
        dex,
        "package_links",
        base_url="https://partner.example.com/offer",
        cluster="ai_tech",
        campaign="q4_ai_launch",
    )
    assert links["status"] == "ok"
    assert "utm_source=syndicate" in links["tracked_url"]
    assert links["disclosure_required"] is True


def test_ray_dropship_margin_and_supplier_audit():
    ray = RayAgent()
    calc = run(
        ray,
        "calculate_dropship_margin",
        selling_price_usd=69.99,
        supplier_cost_usd=14.50,
        shipping_cost_usd=5.50,
        customs_duty_usd=0.0,
        refund_reserve_pct=5.0,
    )
    assert calc["status"] == "ok"
    assert calc["viable_for_catalog"] is True
    assert calc["net_margin_pct"] >= 30.0

    sup = run(
        ray,
        "audit_supplier",
        supplier_name="EU Express Hub",
        platform="cj_dropshipping",
        positive_rating_pct=97.2,
        avg_dispatch_days=1.5,
        avg_delivery_days=6.5,
        verified_tracking=True,
    )
    assert sup["status"] == "ok"
    assert sup["supplier"]["approved"] is True


def test_atlas_route_planning_and_destination_evaluation():
    atlas = AtlasAgent()
    route = run(
        atlas,
        "plan_route",
        origin="Kyiv",
        destination="Warsaw",
        duration_days=5,
        estimated_budget_usd=600.0,
    )
    assert route["status"] == "ok"
    assert route["route"]["state"] == "planned_draft"

    eval_res = run(
        atlas,
        "evaluate_destination",
        city="Lisbon",
        country="Portugal",
        safety_index=84.0,
    )
    assert eval_res["status"] == "ok"
    assert eval_res["destination"]["recommendation"] == "recommended"


def test_director_runner_and_command_hub_include_all_commercial_agents():
    cfg = build_runtime_config({})
    for agent_id in ("oscar", "tyler", "jack", "scout", "dex", "ray", "atlas", "sonar"):
        assert agent_id in AGENTS
        assert cfg[agent_id]["enabled"] is False
        assert cfg[agent_id]["allowed_actions"] == ["capabilities"]

    root = Path(__file__).resolve().parents[1]
    hub = json.loads((root / "config/syndicate_command_hub.json").read_text(encoding="utf-8"))
    cmd_ids = {c["command"] for c in hub["commands"]}
    assert "CMD:SCOUT_MARKETING_BRIEF" in cmd_ids
    assert "CMD:OSCAR_BLOG_CLUSTER_DRAFT" in cmd_ids
    assert "CMD:DEX_AFFILIATE_BUNDLE" in cmd_ids
    assert "CMD:TYLER_MERCH_SHOWCASE" in cmd_ids
    assert "CMD:RAY_DROPSHIP_SHOWCASE" in cmd_ids
    assert "CMD:SONAR_DEEP_RESEARCH" in cmd_ids
    assert "CMD:SONAR_VERIFY_SOURCES" in cmd_ids
    assert "CMD:SONAR_COMPARE_MATRIX" in cmd_ids


def test_sonar_deep_research_and_intelligence_capabilities():
    sonar = SonarAgent()

    # Deep Research
    research = run(
        sonar,
        "deep_research",
        topic="Multi-Tenant Agent Security Architecture",
        depth="comprehensive",
        target_wing="eva",
        confidence_score=0.96,
        citations=[{"id": "c1", "title": "Doc", "url": "https://example.org/doc", "tier": "Tier A", "excerpt": "x"}],
    )
    # Zero-Faking: without sources there is no dossier at all.
    assert run(sonar, "deep_research", topic="No sources here")["status"] == "unavailable"
    assert research["status"] == "ok"
    dossier = research["dossier"]
    assert dossier["topic"] == "Multi-Tenant Agent Security Architecture"
    assert dossier["engine"] == "sonar-deep-research"
    assert dossier["evidence_grade"] == "Tier A"
    assert dossier["confidence_score"] == 0.96
    assert "unreviewed" in dossier["obsidian_markdown"]
    assert [c["url"] for c in dossier["citations"]] == ["https://example.org/doc"]

    # Quick Search (Fast Lookup)
    quick = run(sonar, "quick_search", query="What is current inflation rate in EU?")
    assert quick["status"] == "unavailable"  # no search client => no invented answer

    # Verify Sources
    verification = run(
        sonar,
        "verify_sources",
        claim="Zero-Token architecture reduces token consumption by 95%",
        sources=[
            {"url": "https://syndicate.internal/benchmarks/zero_token", "tier": "Tier A", "notes": "Empirical run logs"},
            {"url": "https://industry-review.org/analysis", "tier": "Tier B", "notes": "Independent auditor"}
        ]
    )
    assert verification["status"] == "ok"
    assert verification["verification"]["verified"] is True
    assert verification["verification"]["verdict"] == "verified_authoritative"

    # Compare Entities
    compare = run(
        sonar,
        "compare_entities",
        entities=["Firecrawl", "Playwright", "Puppeteer"],
        criteria=["LLM Readiness", "Anti-Bot Bypass", "Token Efficiency"]
    )
    assert compare["status"] == "unavailable"  # no scores supplied => no invented ratings
    compare = run(
        sonar,
        "compare_entities",
        entities=["Firecrawl", "Playwright", "Puppeteer"],
        criteria=["LLM Readiness"],
        scores={"Firecrawl": {"LLM Readiness": 90}, "Playwright": {"LLM Readiness": 70}, "Puppeteer": {"LLM Readiness": 60}},
    )
    assert compare["status"] == "ok"
    assert len(compare["comparison"]["entities"]) == 3
    assert compare["comparison"]["winner"] == "Firecrawl"

    # Crawl and Extract (Sanitized Markdown)
    crawl = run(
        sonar,
        "crawl_and_extract",
        url="https://docs.perplexity.ai/reference/post_chat_completions",
        page_title="Perplexity API Reference"
    )
    assert crawl["status"] == "unavailable"  # nothing is fetched here
    crawl = run(sonar, "crawl_and_extract", url="https://docs.perplexity.ai/x", page_text="Body text")
    assert crawl["status"] == "ok" and crawl["domain"] == "docs.perplexity.ai" and crawl["fetched"] is False

    # Package for Obsidian
    package = run(sonar, "package_for_obsidian", dossier_id=dossier["id"])
    assert package["status"] == "ok"
    assert package["export_target"] == "obsidian_second_brain"
    assert package["notebooklm_ready"] is True

    # Report
    rep = run(sonar, "report")
    assert rep["status"] == "ok"
    assert rep["dossiers_completed"] == 1
    assert rep["verifications_conducted"] == 1
    assert rep["comparisons_built"] == 1
    assert rep["external_actions"] is False


def test_orchestrator_eva_quick_perplexity_search():
    from src.orchestrator import EvaOrchestrator
    orchestrator = object.__new__(EvaOrchestrator)
    orchestrator._config = {"sonar": {"enabled": True}}
    orchestrator._memory = None

    result = asyncio.run(orchestrator.quick_perplexity_search("Quick holding status"))
    assert result["status"] == "unavailable"
