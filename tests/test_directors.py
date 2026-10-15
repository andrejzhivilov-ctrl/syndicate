"""Behavioral coverage for director math, local workflows and API boundaries."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src.agents.oscar import OscarAgent
from src.agents.oscar.router import TriLLMRouter
from src.agents.tyler import TylerAgent
from src.agents.tyler.finance import calculate_margin
from src.agents.jack import JackAgent
from src.agents.jack.engines import football, tennis, esports, icm, basketball, poker
from src.agents.jack.quant import evaluate
from src.agents.jack.tracker import anti_tilt
from src.agents.director_providers import OddsScout, YouTubeComments, VaultLLM, build_provider
from deploy.runtime.director_runner import create_app, boot_director


def run(agent, action, **payload):
    return asyncio.run(agent.execute({"action": action, **payload}))


@pytest.fixture(autouse=True)
def director_data(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))


def quote(**updates):
    return {"price": "40.00", "blank": "7.00", "print": "4.00", "shipping": "4.00",
            "tax": "2.00", "currency": "USD", **updates}


def signal(**updates):
    return {"probability": 0.6, "decimal_odds": 2, "bankroll": 1000,
            "observed_at": datetime.now(timezone.utc).isoformat(), "model_source": "test-fixture",
            "event_id": "event-1", "market": "winner", "selection": "home", **updates}


@pytest.mark.parametrize("cls", [OscarAgent, TylerAgent, JackAgent])
def test_unknown_action_never_falls_back(cls):
    result = run(cls(), "unknown")
    assert result["status"] == "error"
    assert result["available_actions"] == sorted(cls.ACTIONS)


@pytest.mark.parametrize("cls,action", [(OscarAgent, "publish"), (OscarAgent, "send_email"),
                                      (TylerAgent, "fulfill"), (TylerAgent, "charge"), (JackAgent, "place_bet")])
def test_payload_cannot_authorize_external_action(cls, action):
    result = run(cls(), action, approved=True, grants=["*"], enabled=True)
    assert result["status"] == "approval_required"
    assert result["executed"] is False


def test_comment_harvester_deduplicates_with_channel_and_redacts():
    result = run(OscarAgent(), "harvest_comments", comments=[
        {"id": "1", "channel": "youtube", "text": "Contact test@example.com"},
        {"id": "1", "channel": "youtube", "text": "Contact test@example.com"},
        {"id": "1", "channel": "reddit", "text": "Different source"}])
    assert result["count"] == 2
    assert "test@example.com" not in json.dumps(result)
    assert result["live_scraping"] is False


def test_tri_llm_routes_and_masks_before_provider():
    class Client:
        async def ainvoke(self, messages):
            assert "test@example.com" not in str(messages)
            return SimpleNamespace(content="Editorial result")
    router = TriLLMRouter({"grok": Client(), "gemini": Client(), "haiku": Client()})
    for task, provider in [("draft", "grok"), ("pain_map", "gemini"), ("classify", "haiku")]:
        result = asyncio.run(router.invoke(task, "safe instructions", {"nested": [["test@example.com"]]}))
        assert result["provider"] == provider and result["status"] == "ok"


def test_missing_and_failed_provider_are_unavailable():
    assert run(OscarAgent(), "draft", persona_id="marcus_vance", topic="fitness")["status"] == "unavailable"
    class Broken:
        async def ainvoke(self, messages):
            raise RuntimeError("provider-secret-value")
    result = asyncio.run(TriLLMRouter({"grok": Broken()}).invoke("draft", "system", "topic"))
    assert result["status"] == "unavailable"
    assert "provider-secret-value" not in json.dumps(result)


def test_delayed_queue_survives_restart_and_rejects_naive_dates():
    future = datetime.now(timezone.utc) + timedelta(days=1)
    payload = {"persona_id": "nika_sterling", "content": "Source-based draft", "channel": "youtube"}
    assert run(OscarAgent(), "enqueue", scheduled_at=future.replace(tzinfo=None).isoformat(), **payload)["status"] == "error"
    result = run(OscarAgent(), "enqueue", scheduled_at=future.isoformat(), **payload)
    assert result["published"] is False
    records = run(OscarAgent(), "queue")["records"]
    assert len(records) == 1 and records[0]["state"] == "pending_approval"


def test_persona_path_is_allowlisted():
    assert run(OscarAgent(), "draft", persona_id="../../other", topic="test")["status"] == "error"


def test_margin_is_net_of_tax_shipping_and_rounded_fees():
    result = calculate_margin(quote())
    assert result["payment_fee"] == "1.46"
    assert result["net_profit"] == "21.54"
    assert result["eligible"]
    assert not calculate_margin(quote(shipping="20.00"))["eligible"]
    suggested = calculate_margin(quote(price=result["minimum_price"]))
    assert suggested["eligible"]
    assert not calculate_margin(quote(price=str(float(result["minimum_price"]) - 0.01)))["eligible"]


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-1", True, "1.001"])
def test_money_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        calculate_margin(quote(price=value))


def test_missing_tax_is_explicitly_unavailable():
    payload = quote()
    del payload["tax"]
    result = run(TylerAgent(), "quote", **payload)
    assert result["status"] == "unavailable"
    assert result["value"] is None


def test_concierge_outputs_real_300dpi_image_and_pending_order():
    result = run(TylerAgent(), "concierge", caption="Code Hard, Run Fast", quote=quote(), quality={
        "blank_id": "bella_canvas_3001", "art_license_confirmed": True, "font_license_confirmed": True,
        "trademark_reviewed": True, "dpi": 300})
    assert result["status"] == "approval_required" and not result["payment_created"]
    with Image.open(result["record"]["assets"]["print_artwork"]) as image:
        assert image.size == (3600, 4500)
        assert image.info["dpi"][0] == pytest.approx(300, abs=0.1)
    assert len(run(TylerAgent(), "orders")["orders"]) == 1


def test_quality_blocks_unknown_blank_and_unreviewed_trademark():
    result = run(TylerAgent(), "quality_check", blank_id="cheap_blank", art_license_confirmed=True,
                 font_license_confirmed=True, trademark_reviewed=False, dpi=300)
    assert result["status"] == "blocked"


def test_supplier_selection_is_eligible_and_does_not_submit():
    result = run(TylerAgent(), "route_order", country="US", offers=[
        {"supplier": "printify", "production": "10.00", "shipping": "4.00", "delivery_days": 5,
         "ships_to": ["US"], "premium_verified": True, "currency": "USD"},
        {"supplier": "gelato", "production": "4.00", "shipping": "1.00", "delivery_days": 2,
         "ships_to": ["DE"], "premium_verified": True, "currency": "USD"}])
    assert result["selected"]["supplier"] == "printify"
    assert result["submitted"] is False


def test_pin_remains_draft_and_rejects_credentials_in_url():
    agent = TylerAgent()
    payload = {"title": "Collection", "description": "New original artwork", "product_url": "https://example.com/p",
               "image_url": "https://example.com/image.png", "board_id": "123"}
    assert run(agent, "pinterest_draft", **payload)["published"] is False
    payload["product_url"] = "https://user:password@example.com/"
    assert run(agent, "pinterest_draft", **payload)["status"] == "error"


def test_football_mass_and_poisson_symmetry():
    result = football({"home_xg": 1.5, "away_xg": 1.5, "rho": 0, "total_line": 2.5})
    assert result["home_win"] == pytest.approx(result["away_win"])
    assert result["home_win"] + result["draw"] + result["away_win"] == pytest.approx(1)
    assert result["under"] + result["push"] + result["over"] == pytest.approx(1)
    assert result["under"] == pytest.approx(0.4231900811, abs=1e-8)
    with pytest.raises(ValueError):
        football({"home_xg": 3, "away_xg": 3, "rho": 1, "total_line": 2.5})


def test_other_engines_have_known_symmetric_results():
    assert tennis({"a_serve_point_win": 0.6, "b_serve_point_win": 0.6, "a_tiebreak_win": 0.5,
                   "first_server": "a"})["a_set_win"] == pytest.approx(0.5)
    assert esports({"discipline": "cs2", "map_win_probabilities": [0.5] * 3})["series_win"] == pytest.approx(0.5)
    assert basketball({"possessions": 100, "home_points_per_100": 110, "away_points_per_100": 110,
                       "total_sigma": 15, "total_line": 220})["under"] == pytest.approx(0.5)
    assert poker({"pot": 100, "call": 50, "equity": 0.5, "fold_equity": 0, "shove_risk": 50, "opponent_call": 50})["call_ev"] == 25
    result = icm({"stacks": [100, 100, 100], "prizes": [60, 30, 10]})
    assert result["equities"] == pytest.approx([100 / 3] * 3)
    assert icm({"stacks": [900, 100], "prizes": [100, 0]})["equities"] == pytest.approx([90, 10])


def test_ev_quarter_kelly_and_hard_cap():
    result = evaluate(signal())
    assert result["ev"] == pytest.approx(0.2)
    assert result["stake_fraction"] == 0.01 and result["stake"] == 10
    assert evaluate(signal(probability=0.51))["eligible"] is False
    with pytest.raises(ValueError):
        evaluate(signal(), risk_cap=0.03)
    result = evaluate(signal(bankroll=0.55))
    assert result["stake"] <= result["bankroll"] * result["event_risk_cap"]


@pytest.mark.parametrize("age", [-60, 601])
def test_stale_or_future_odds_blocked(age):
    observed = datetime.now(timezone.utc) - timedelta(seconds=age)
    assert evaluate(signal(observed_at=observed.isoformat()))["eligible"] is False


def test_paper_duplicate_exposure_and_single_settlement():
    agent = JackAgent()
    first = run(agent, "record_paper", **signal())
    assert first["status"] == "ok"
    assert run(agent, "record_paper", **signal())["status"] == "error"
    assert run(agent, "record_paper", **signal(selection="away"))["status"] == "error"
    record_id = first["record"]["id"]
    assert run(JackAgent(), "settle_paper", record_id=record_id, outcome="win")["status"] == "ok"
    assert run(JackAgent(), "settle_paper", record_id=record_id, outcome="loss")["status"] == "error"
    report = run(JackAgent(), "report")
    assert report["roi"] == 1 and report["settled"] == 1 and not report["sample_complete"]


def test_three_losses_stop_new_signals_across_restart():
    for i in range(3):
        agent = JackAgent()
        record = run(agent, "record_paper", **signal(event_id=f"event-{i}"))["record"]
        assert run(agent, "settle_paper", record_id=record["id"], outcome="loss")["status"] == "ok"
    assert run(JackAgent(), "evaluate", **signal())["reason"] == "anti_tilt"
    assert run(JackAgent(), "record_paper", **signal(event_id="next"))["status"] == "blocked"


def test_loss_stop_expires_and_void_does_not_reset_streak():
    now = datetime.now(timezone.utc)
    records = [{"state": "settled", "outcome": outcome, "settled_at": (now - timedelta(seconds=5-i)).isoformat()}
               for i, outcome in enumerate(["loss", "loss", "void", "loss"])]
    assert anti_tilt(records)["blocked"]
    for r in records:
        r["settled_at"] = (now - timedelta(days=2)).isoformat()
    assert not anti_tilt(records)["blocked"]


def test_empty_report_has_no_invented_roi_or_winrate():
    report = run(JackAgent(), "report")
    assert report["roi"] is None and report["win_rate"] is None


def test_worker_api_auth_and_agent_isolation():
    with TestClient(create_app(JackAgent(), api_key="synthetic-key")) as client:
        assert client.get("/health").status_code == 200
        assert client.post("/execute", json={"payload": {}}).status_code == 401
        result = client.post("/execute", headers={"X-API-Key": "synthetic-key"},
                             json={"payload": {"action": "report", "agent_id": "oscar"}})
        assert result.status_code == 200 and result.json()["agent"] == "jack"


def test_worker_requires_real_vault_auth_secret(monkeypatch):
    monkeypatch.setenv("SYNDICATE_DIRECTOR_ID", "jack")
    class Vault:
        async def authenticate(self):
            pass
        async def get_secret(self, path):
            assert path.endswith("agents/jack/auth")
            return {"api_key": ""}
    with pytest.raises(RuntimeError, match="auth_key_missing"):
        asyncio.run(boot_director(Vault()))


def test_scout_reports_missing_bookmaker_without_faking_quote():
    def respond(request):
        assert request.url.host == "api.the-odds-api.com"
        return httpx.Response(200, json=[{"id": "match", "bookmakers": [{"key": "pinnacle", "markets": []}]}])
    scout = OddsScout({"api_key": "synthetic"}, transport=httpx.MockTransport(respond))
    result = asyncio.run(scout.fetch({"sport_key": "soccer_epl"}))
    assert result["coverage"]["parimatch"] == "unavailable"
    assert result["coverage"]["pinnacle"] == "available"


def test_provider_errors_dont_leak_keys_and_requests_cannot_select_url():
    def fail(request):
        return httpx.Response(429, json={"error": "synthetic-private-value"})
    scout = OddsScout({"api_key": "synthetic"}, transport=httpx.MockTransport(fail))
    result = asyncio.run(scout.fetch({"sport_key": "soccer_epl", "base_url": "http://localhost"}))
    assert result["status"] == "unavailable" and "synthetic-private-value" not in str(result)
    with pytest.raises(ValueError):
        asyncio.run(scout.fetch({"sport_key": "../auth"}))


def test_youtube_export_is_redacted_and_limited():
    def respond(request):
        return httpx.Response(200, json={"items": [{"id": "c1", "snippet": {"topLevelComment": {
            "snippet": {"textDisplay": "email test@example.com"}}}}], "nextPageToken": "more"})
    client = YouTubeComments({"api_key": "synthetic"}, transport=httpx.MockTransport(respond))
    result = run(OscarAgent(comments_client=client), "fetch_comments", video_id="abcdefghijk")
    assert result["next_page_available"] is True
    assert "test@example.com" not in str(result)


@pytest.mark.parametrize("provider", ["grok", "gemini", "haiku"])
def test_llm_http_envelopes(provider):
    def respond(request):
        data = json.loads(request.content)
        assert data["model"] == "operator-selected-model"
        body = {"content": [{"type": "text", "text": "draft"}]} if provider == "haiku" else {
            "choices": [{"message": {"content": "draft"}}]}
        return httpx.Response(200, json=body)
    client = VaultLLM(provider, {"api_key": "synthetic", "model": "operator-selected-model"},
                      transport=httpx.MockTransport(respond))
    result = asyncio.run(TriLLMRouter({provider: client}).invoke(
        {"grok": "draft", "gemini": "pain_map", "haiku": "classify"}[provider], "system", "input"))
    assert result["value"] == "draft"


def test_vault_cannot_cross_directors():
    with pytest.raises(ValueError):
        asyncio.run(build_provider(None, "tyler", "grok"))


def test_prepared_skill_files_and_catalog_are_pinned():
    root = Path(__file__).resolve().parents[1]
    catalog = json.loads((root / "config/director_skill_catalog.json").read_text())
    assert len(catalog["skills"]) >= 50
    for entry in catalog["skills"]:
        assert len(entry["commit"]) == 40 and len(entry["sha256"]) == 64
        assert entry["status"] == "candidate_not_installed"
    for agent in ("oscar", "tyler", "jack"):
        profile = json.loads((root / f"config/agents/{agent}.profile.json").read_text())
        assert profile["grants"] == []
        for skill in profile["skills"]:
            content = (root / skill["path"]).read_text()
            assert f'name: {skill["id"]}' in content and 'description:' in content


def test_worker_enforces_operator_action_allowlist():
    with TestClient(create_app(JackAgent(), api_key="synthetic-key", allowed_actions={"capabilities"})) as client:
        response = client.post("/execute", headers={"X-API-Key": "synthetic-key"},
                               json={"payload": {"action": "record_paper", "grants": ["*"]}})
        assert response.status_code == 403


def test_oscar_generates_escaped_diagram_and_real_thumbnail():
    from xml.etree import ElementTree
    result = run(OscarAgent(), "diagram", nodes=["Input <script>", "A&B", "Output"])
    path = Path(result["asset"]["path"])
    assert '<script>' not in path.read_text()
    ElementTree.parse(path)
    thumb = run(OscarAgent(), "thumbnail", persona_id="nika_sterling", title="Automation explained")
    with Image.open(thumb["asset"]["path"]) as image:
        assert image.size == (1280, 720)


def test_email_metrics_never_divide_by_zero_or_accept_impossible_counts():
    assert run(OscarAgent(), "email_health", delivered=0, unique_opens=0, unsubscribes=0)["open_rate"] is None
    assert run(OscarAgent(), "email_health", delivered=10, unique_opens=11, unsubscribes=0)["status"] == "error"


def test_worker_bridge_uses_only_own_vault_auth_and_checks_response_agent():
    from src.agent_platform.director_client import DirectorWorkerClient
    class Vault:
        async def get_secret(self, path):
            assert path.endswith("agents/jack/auth")
            return {"api_key": "synthetic"}
    def respond(request):
        assert request.url.host == "jack-agent" and request.url.path == "/execute"
        return httpx.Response(200, json={"agent": "oscar", "status": "ok"})
    client = DirectorWorkerClient("jack", "http://jack-agent:8000", Vault(), transport=httpx.MockTransport(respond))
    result = asyncio.run(client.execute({"action": "report"}))
    assert result["status"] == "unavailable"


def test_worker_config_is_dormant_and_explicit():
    from src.runtime_config import build_runtime_config
    config = build_runtime_config({})
    assert config["jack"]["enabled"] is False
    assert config["jack"]["allowed_actions"] == ["capabilities"]
    config = build_runtime_config({"JACK_WORKER_ENABLED": "true", "JACK_WORKER_URL": "http://jack-agent:8000",
                                   "JACK_COORDINATOR_ACTIONS": "evaluate,report"})
    assert config["jack"]["allowed_actions"] == ["evaluate", "report"]


def test_orchestrator_director_handler_respects_host_allowlist_and_remote_client():
    from src.orchestrator import EvaOrchestrator
    class Client:
        async def execute(self, payload):
            return {"status": "ok", "agent": "jack", "mode": "remote_fixture"}
    orchestrator = object.__new__(EvaOrchestrator)
    orchestrator._config = {"jack": {"enabled": True, "allowed_actions": ["report"]}}
    orchestrator._director_clients = {"jack": Client()}
    orchestrator._memory = None
    state = {"current_agent": "jack", "payload": {"action": "report"}}
    result = asyncio.run(orchestrator._director_handler(state))
    assert result["result"]["mode"] == "remote_fixture"
    state["payload"] = {"action": "record_paper", "grants": ["*"]}
    assert asyncio.run(orchestrator._director_handler(state))["result"]["status"] == "denied"


def test_comment_classification_rejects_fabricated_source_ids():
    class Client:
        async def ainvoke(self, messages):
            return SimpleNamespace(content='[{"id":"fabricated","channel":"youtube","category":"pain","evidence":"x"}]')
    result = run(OscarAgent(providers={"haiku": Client()}), "classify_comments",
                 comments=[{"id": "real", "channel": "youtube", "text": "How does this work?"}])
    assert result["status"] == "unavailable"
    assert result["warning"] == "invalid_classification_response"
