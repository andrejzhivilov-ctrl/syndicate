"""Deployment-readiness checks for the Sam identity-draft profile."""

from __future__ import annotations

import json
from pathlib import Path

from src.agent_platform.contracts import (
    AccessRequest,
    ActionClass,
    AgentProfile,
    DecisionCode,
    DecisionStatus,
    RuntimeKind,
)
from src.agent_platform.policy import AgentPolicy
from src.agent_platform.registry import AgentRegistry
from src.agents.sam_access import load_sam_manifest, sam_agent_profile, sam_auto_invest_allowed

ROOT = Path(__file__).resolve().parents[1]
SAM_PROFILE_PATH = ROOT / "config" / "agents" / "sam.profile.json"
EVA_PROFILE_PATH = ROOT / "config" / "agents" / "eva.profile.json"
QUANT_SPEC_PATH = ROOT / "sam_core" / "SAM_QUANT_SPEC.md"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_sam_manifest_is_prepared_not_enabled_and_has_no_grants() -> None:
    manifest = load_sam_manifest()
    profile = sam_agent_profile(manifest)

    assert manifest["activation"] == "prepared_not_enabled"
    assert manifest["role_status"] == "identity_draft"
    assert manifest["model_status"] == "not_selected"
    assert manifest["prompt_status"] == "draft"
    assert profile.runtime is RuntimeKind.HERMES
    assert profile.capabilities == frozenset()
    assert profile.resource_scopes == frozenset()
    assert manifest["services_enabled"] == []
    assert manifest["skills"]
    assert all(item.get("activation") == "draft" for item in manifest["skills"])
    catalog = (ROOT / "sam_core/SAM_CANDIDATE_CATALOG.md").read_text(encoding="utf-8")
    assert "Нічого з цього не встановлено" in catalog
    assert "ccxt/ccxt" in catalog

    prompt_path = ROOT / manifest["prompt_file"]
    assert prompt_path.is_file()
    prompt = prompt_path.read_text(encoding="utf-8")
    assert "Ніколи не проси вставити" in prompt
    assert "Єва не ставить тобі завдань" in prompt
    assert "Інвестиції" in prompt


def test_sam_manifest_does_not_enable_broker_bot_or_auto() -> None:
    manifest = _load(SAM_PROFILE_PATH)
    assert manifest["execution"]["broker"] == "tbd"
    assert manifest["execution"]["invest_always_hitl"] is True
    assert manifest["live_modes"]["auto_fx_crypto"] is False
    assert manifest["live_modes"]["auto_invest"] is False
    assert sam_auto_invest_allowed(manifest) is False
    assert all(value is False for value in manifest["live_modes"].values())
    assert manifest["inbound_channels"]["telegram"]["enabled"] is False
    assert manifest["n8n"]["control_plane"] is False
    assert manifest["workspace"]["drive"]["folder_id"] is None
    assert manifest["knowledge_bases"]["quant"]["status"] == "not_loaded"
    sources = (ROOT / "sam_core/knowledge/quant/SOURCES.yaml").read_text(encoding="utf-8")
    assert "sources: []" in sources
    dumped = json.dumps(manifest)
    # Quoted prefixes: OpenAI/GitHub/Slack/Google tokens as JSON string values.
    # Bare "sk-" also matches skill id "sam-risk-guard" — that is not a secret.
    for credential_shape in ('"sk-', '"ghp_', '"xoxb-', '"AIza', "Bearer "):
        assert credential_shape not in dumped


def test_quant_spec_is_not_copied_into_grants() -> None:
    manifest = _load(SAM_PROFILE_PATH)
    dumped = json.dumps(manifest)
    assert QUANT_SPEC_PATH.is_file()
    assert manifest["capabilities"] == []
    assert "@sam_quant_bot" not in dumped
    assert "SAM_QUANT_SPEC" not in dumped


def test_sam_and_eva_namespaces_are_isolated() -> None:
    sam = _load(SAM_PROFILE_PATH)
    eva = _load(EVA_PROFILE_PATH)
    assert sam["memory_namespace"] != eva["memory_namespace"]
    registry = AgentRegistry(
        [
            sam_agent_profile(sam),
            AgentProfile(
                agent_id=eva["agent_id"],
                hermes_profile=eva["hermes_profile"],
                memory_namespace=eva["memory_namespace"],
                capabilities=frozenset(eva["capabilities"]),
                resource_scopes=frozenset(eva["resource_scopes"]),
                runtime=RuntimeKind(eva["runtime"]),
            ),
        ]
    )
    assert registry.get("sam") is not None
    assert registry.get("eva") is not None


def test_policy_denies_trade_execute_while_grants_are_empty() -> None:
    profile = sam_agent_profile()
    policy = AgentPolicy()
    for capability, action, scope in (
        ("agent.invoke", ActionClass.INFORMATIONAL, None),
        ("trade.execute", ActionClass.FINANCIAL_OPERATION, "broker/demo"),
        ("service.telegram.call", ActionClass.SERVICE_CONNECTION, "telegram"),
        ("memory.write", ActionClass.BOUNDED_WRITE, "agents/sam"),
    ):
        decision = policy.evaluate(
            profile,
            AccessRequest(
                agent_id="sam",
                capability=capability,
                action_class=action,
                resource_scope=scope,
            ),
        )
        assert decision.status is DecisionStatus.DENIED
        assert decision.code is DecisionCode.CAPABILITY_NOT_GRANTED
