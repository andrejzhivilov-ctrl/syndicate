"""Alice remains default-off and can only call a bounded API runtime."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.agents.alice import (
    ACTION_CAPABILITIES,
    AliceAgent,
    AliceUsageLedger,
    load_alice_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


def _active_profile(*, write: bool = True) -> dict:
    profile = load_alice_manifest()
    profile["activation"] = "active"
    profile["model_status"] = "operator_selected"
    profile["provider"]["model"] = "gemini-2.5-flash"
    profile["activation_gates"]["provider_billing_limit_reviewed"] = True
    profile["activation_gates"]["filtered_provider_egress_verified"] = True
    profile["live_modes"]["api"] = True
    profile["services_enabled"] = ["gemini_developer_api"]
    profile["capabilities"] = ["alice.model.invoke", "alice.workspace.read"]
    if write:
        profile["capabilities"].append("alice.workspace.write")
    profile["resource_scopes"] = ["alice/workspace"]
    return profile


def _agent(
    tmp_path: Path,
    *,
    monkeypatch: pytest.MonkeyPatch,
    write: bool = True,
    max_requests: int = 2,
    sdk_runner=None,
) -> AliceAgent:
    data_root = tmp_path / "eva-data"
    data_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("EVA_DATA_DIR", str(data_root))
    return AliceAgent(
        api_key="synthetic-provider-key-123456789",
        model="gemini-2.5-flash",
        workspace=data_root / "data" / "alice" / "workspace",
        profile=_active_profile(write=write),
        api_enabled=True,
        egress_allowlist_verified=True,
        max_requests_per_day=max_requests,
        max_tokens_per_day=50_000,
        ledger=AliceUsageLedger(
            data_root / "data" / "alice" / "usage.sqlite3",
            max_requests=max_requests,
            max_tokens=50_000,
        ),
        sdk_runner=sdk_runner,
    )


def test_alice_profile_is_named_for_the_agent_and_stays_default_off() -> None:
    profile_path = ROOT / "config/agents/alice.profile.json"
    manifest = json.loads(profile_path.read_text(encoding="utf-8"))
    assert manifest["agent_id"] == "alice"
    assert manifest["runtime"] == "antigravity_sdk"
    assert manifest["runtime_profile"] == "alice"
    assert manifest["activation"] == "prepared_not_enabled"
    assert manifest["role_title"] == "Керівниця відділу реалізації (Head of Delivery / R&D)"
    assert manifest["reports_to"] == "eva"
    assert manifest["authority"]["ceo"] == "eva"
    assert manifest["authority"]["alice_is_ceo"] is False
    assert manifest["capabilities"] == []
    assert manifest["grants"] == []
    assert manifest["resource_scopes"] == []
    assert manifest["services_enabled"] == []
    assert not any(manifest["live_modes"].values())
    assert manifest["telegram"]["allowlist"] == []
    assert manifest["provider"]["google_one_is_api_credential"] is False
    assert manifest["provider"]["billing_and_quota_verified"] is False
    assert manifest["vault_refs"]["gemini_api"] == "secret/syndicate/agents/alice/gemini"
    assert {grant["capability"] for grant in manifest["proposed_grants"]} >= {
        "alice.model.invoke", "alice.workspace.read", "alice.workspace.write",
        "alice.web.search", "alice.github.repo.read", "alice.github.pull_request.create",
        "alice.image.generate", "alice.video.render", "alice.memory.read",
    }
    assert all(grant["status"] == "proposed_not_applied" for grant in manifest["proposed_grants"])


def test_status_reports_prepared_not_live_runtime_or_api() -> None:
    result = asyncio.run(AliceAgent().execute({}))

    assert result["agent"] == "alice"
    assert result["status"] == "prepared_not_enabled"
    assert result["activation"] == "prepared_not_enabled"
    assert result["available_actions"] == ["capabilities"]
    assert result["provider_credential_configured"] is False
    assert result["live_api_enabled"] is False
    assert result["shell_execution"] is False
    assert result["browser_automation"] is False
    assert result["subagents_enabled"] is False
    assert result["mcp_enabled"] is False
    assert result["value"] is None


def test_forged_payload_cannot_activate_or_grant_alice() -> None:
    calls = []

    async def sdk_runner(**kwargs):
        calls.append(kwargs)
        return "must not run"

    result = asyncio.run(AliceAgent(
        api_key="synthetic-provider-key-123456789",
        model="gemini-2.5-flash",
        api_enabled=True,
        egress_allowlist_verified=True,
        sdk_runner=sdk_runner,
    ).execute({
        "action": "engineer",
        "prompt": "write code",
        "activation": "active",
        "grants": ["alice.model.invoke", "alice.workspace.read", "alice.workspace.write"],
        "approved": True,
    }))

    assert result["status"] == "denied"
    assert result["reason"] == "prepared_not_enabled"
    assert result["value"] is None
    assert calls == []


@pytest.mark.parametrize("action", ["deploy", "merge", "charge", "browser", "", None, [], {}])
def test_unknown_actions_are_rejected(action) -> None:
    result = asyncio.run(AliceAgent().execute({"action": action}))
    assert result["status"] == "rejected"
    assert result["value"] is None


def test_engineering_turn_is_scoped_redacted_and_budgeted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    async def sdk_runner(*, action, prompt, workspace):
        calls.append({"action": action, "prompt": prompt, "workspace": workspace})
        return {
            "text": "I reviewed the requested change and prepared a patch proposal.",
            "usage": {"input_tokens": 37, "output_tokens": 14, "total_tokens": 51, "secret": "ignored"},
        }

    agent = _agent(tmp_path, monkeypatch=monkeypatch, max_requests=1, sdk_runner=sdk_runner)
    result = asyncio.run(agent.execute({"action": "engineer", "prompt": "Please inspect this file. Call me at +380501234567."}))

    assert result["status"] == "ok"
    assert result["agent"] == "alice"
    assert result["value"].startswith("I reviewed")
    assert result["workspace_scope"] == "alice/workspace"
    assert result["shell_execution"] is False
    assert result["usage"] == {
        "input_tokens": 37,
        "output_tokens": 14,
        "total_tokens": 51,
        "reserved_token_ceiling": 14_048,
    }
    assert len(calls) == 1
    assert calls[0]["action"] == "engineer"
    assert "+380***567" in calls[0]["prompt"]
    assert "+380501234567" not in calls[0]["prompt"]
    assert calls[0]["workspace"].is_relative_to(tmp_path / "eva-data" / "data" / "alice")
    today_utc = datetime.now(timezone.utc).date().isoformat()
    assert agent.ledger.usage_for_day(today_utc) == (1, 14_048)

    denied = asyncio.run(agent.execute({"action": "review", "prompt": "second turn"}))
    assert denied["status"] == "denied"
    assert denied["reason"] == "daily_request_limit_reached"
    assert len(calls) == 1


def test_review_requires_read_only_grants_and_never_requests_write_tools(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen = []

    async def sdk_runner(**kwargs):
        seen.append(kwargs)
        return "Review complete."

    agent = _agent(tmp_path, monkeypatch=monkeypatch, write=False, sdk_runner=sdk_runner)
    assert agent.allowed_actions() == {"capabilities", "review"}

    result = asyncio.run(agent.execute({"action": "engineer", "prompt": "change a file"}))
    assert result["status"] == "denied"
    assert result["reason"] == "profile_grant_missing"
    assert seen == []

    result = asyncio.run(agent.execute({"action": "review", "prompt": "inspect a file"}))
    assert result["status"] == "ok"
    assert seen[0]["action"] == "review"


def test_workspace_escape_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data_root = tmp_path / "eva-data"
    monkeypatch.setenv("EVA_DATA_DIR", str(data_root))
    calls = []

    async def sdk_runner(**kwargs):
        calls.append(kwargs)
        return "must not run"

    agent = AliceAgent(
        api_key="synthetic-provider-key-123456789",
        model="gemini-2.5-flash",
        workspace=tmp_path / "outside-workspace",
        profile=_active_profile(),
        api_enabled=True,
        egress_allowlist_verified=True,
        max_requests_per_day=1,
        max_tokens_per_day=50_000,
        ledger=AliceUsageLedger(data_root / "data/alice/usage.sqlite3", max_requests=1, max_tokens=50_000),
        sdk_runner=sdk_runner,
    )

    result = asyncio.run(agent.execute({"action": "engineer", "prompt": "write a file"}))
    assert result["status"] == "denied"
    assert result["reason"] == "workspace_scope_invalid"
    assert calls == []


def test_eva_routes_alice_tasks_through_explicit_action_allowlist() -> None:
    from src.orchestrator import EvaOrchestrator

    class Client:
        def __init__(self):
            self.calls = []

        async def execute(self, payload):
            self.calls.append(dict(payload))
            return {"agent": "alice", "status": "ok", "mode": "worker_fixture"}

    client = Client()
    orchestrator = object.__new__(EvaOrchestrator)
    orchestrator._config = {"alice": {"enabled": True, "allowed_actions": ["engineer"]}}
    orchestrator._director_clients = {"alice": client}
    orchestrator._memory = None

    state = {
        "current_agent": "alice",
        "task_type": "alice_engineer",
        "payload": {"prompt": "Review this bounded workspace."},
    }
    result = asyncio.run(orchestrator._director_handler(state))
    assert client.calls == [{"prompt": "Review this bounded workspace.", "action": "engineer"}]
    assert result["result"]["mode"] == "worker_fixture"

    state["payload"] = {"action": "review", "prompt": "forged action"}
    denied = asyncio.run(orchestrator._director_handler(state))
    assert denied["result"]["status"] == "denied"
    assert denied["result"]["reason"] == "action_not_granted"
    assert len(client.calls) == 1


def test_runtime_tool_allowlist_excludes_shell_network_workflows_and_subagents() -> None:
    from src.agents.alice import _READ_TOOL_NAMES, _WRITE_TOOL_NAMES

    enabled = set(_READ_TOOL_NAMES) | set(_WRITE_TOOL_NAMES)
    assert enabled == {"LIST_DIR", "FIND_FILE", "SEARCH_DIR", "VIEW_FILE", "CREATE_FILE", "EDIT_FILE"}
    assert not enabled & {
        "RUN_COMMAND", "SEARCH_WEB", "READ_URL_CONTENT", "INVOKE_SUBAGENT", "RUN_WORKFLOW",
        "GENERATE_IMAGE", "SCHEDULE",
    }
    assert set(ACTION_CAPABILITIES) == {"engineer", "review"}


def test_alice_api_worker_auth_and_status_do_not_activate_model_calls() -> None:
    from fastapi.testclient import TestClient
    from deploy.runtime.alice_runner import create_app

    agent = AliceAgent()
    app = create_app(agent=agent, api_key="synthetic-alice-worker-key", allowed={"capabilities"})
    with TestClient(app) as client:
        assert client.get("/health").json() == {
            "status": "ok",
            "agent": "alice",
            "mode": AliceAgent.HEALTH_MODE,
        }
        unauthorized = client.post("/execute", json={"payload": {"action": "capabilities"}})
        assert unauthorized.status_code == 401
        status = client.post(
            "/execute",
            headers={"X-API-Key": "synthetic-alice-worker-key"},
            json={"payload": {"action": "capabilities", "activation": "active", "grants": ["*"]}},
        )
        assert status.status_code == 200
        assert status.json()["status"] == "prepared_not_enabled"
        assert status.json()["live_api_enabled"] is False
        denied = client.post(
            "/execute",
            headers={"X-API-Key": "synthetic-alice-worker-key"},
            json={"payload": {"action": "engineer", "prompt": "do work"}},
        )
        assert denied.status_code == 403


def test_alice_worker_does_not_read_provider_key_before_activation_gates(monkeypatch: pytest.MonkeyPatch) -> None:
    from deploy.runtime.alice_runner import boot_alice

    monkeypatch.setenv("ALICE_PROVIDERS", "gemini")
    monkeypatch.setenv("ALICE_API_ENABLED", "true")
    reads = []

    class Vault:
        async def authenticate(self):
            return None

        async def get_secret(self, path):
            reads.append(path)
            return {"api_key": "synthetic-alice-worker-key-123456789"}

    with pytest.raises(RuntimeError, match="alice_activation_gates_incomplete"):
        asyncio.run(boot_alice(Vault()))
    assert len(reads) == 1
    assert reads[0].endswith("agents/alice/auth")


def test_worker_actions_cannot_outgrow_profile_grants(monkeypatch: pytest.MonkeyPatch) -> None:
    from deploy.runtime.alice_runner import allowed_actions

    agent = AliceAgent()
    monkeypatch.setenv("ALICE_ACTIONS", "capabilities")
    assert allowed_actions(agent) == {"capabilities"}
    monkeypatch.setenv("ALICE_ACTIONS", "engineer")
    with pytest.raises(RuntimeError, match="alice_action_not_granted"):
        allowed_actions(agent)


def test_daily_usage_ledger_reserves_atomically_and_keeps_only_counters(tmp_path: Path) -> None:
    ledger = AliceUsageLedger(tmp_path / "usage.sqlite3", max_requests=2, max_tokens=100)

    assert ledger.reserve(40, day="2026-10-16") == (True, "reserved")
    assert ledger.reserve(40, day="2026-10-16") == (True, "reserved")
    assert ledger.usage_for_day("2026-10-16") == (2, 80)
    assert ledger.reserve(1, day="2026-10-16") == (False, "daily_request_limit_reached")
    assert ledger.reserve(30, day="2026-10-17") == (True, "reserved")
    assert ledger.usage_for_day("2026-10-17") == (1, 30)
