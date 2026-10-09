"""Deployment-readiness checks for the Architect contract-only profile."""

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
from src.agents.architect import n8n_builder

ROOT = Path(__file__).resolve().parents[1]
ARCHITECT_PROFILE_PATH = ROOT / "config" / "agents" / "architect.profile.json"
EVA_PROFILE_PATH = ROOT / "config" / "agents" / "eva.profile.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _architect_profile(manifest: dict | None = None) -> AgentProfile:
    manifest = manifest or _load(ARCHITECT_PROFILE_PATH)
    return AgentProfile(
        agent_id=manifest["agent_id"],
        hermes_profile=manifest["hermes_profile"],
        memory_namespace=manifest["memory_namespace"],
        capabilities=frozenset(manifest["capabilities"]),
        resource_scopes=frozenset(manifest["resource_scopes"]),
        runtime=RuntimeKind(manifest["runtime"]),
    )


def test_architect_manifest_is_prepared_not_enabled_and_has_no_grants() -> None:
    manifest = _load(ARCHITECT_PROFILE_PATH)
    profile = _architect_profile(manifest)

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
    assert not hasattr(profile, "role")

    prompt_path = ROOT / manifest["prompt_file"]
    assert prompt_path.is_file()
    prompt = prompt_path.read_text(encoding="utf-8")
    assert "Ніколи не проси вставити" in prompt
    assert "лише від Андрія" in prompt
    assert "Єва не ставить тобі завдань" in prompt


def test_architect_manifest_does_not_select_model_or_integrations() -> None:
    manifest = _load(ARCHITECT_PROFILE_PATH)
    assert manifest["model_status"] == "not_selected"
    assert manifest["role_status"] == "identity_draft"
    assert manifest["services_enabled"] == []
    assert manifest["n8n"]["control_plane"] is False
    assert manifest["n8n"]["permission_source"] is False
    assert manifest["n8n"]["activation"] == "not_enabled"
    assert manifest["n8n"]["live_api"] is False
    assert manifest["n8n"]["credentials_managed_in_profile"] is False
    assert manifest["task_source"] == "andrii_only"
    assert manifest["reports"]["eva_can_assign"] is False
    assert manifest["reports"]["daily_brief_to_eva"] == "payload_only"
    assert manifest["knowledge_bases"]["architecture"]["status"] == "not_loaded"
    assert manifest["workspace"]["drive"]["folder_id"] is None
    sources = (ROOT / "architect_core/knowledge/architecture/SOURCES.yaml").read_text(encoding="utf-8")
    assert "sources: []" in sources
    assert manifest["live_modes"]["telegram_bot"] is False
    assert manifest["live_modes"]["gitops_push"] is False
    assert manifest["live_modes"]["n8n_editor"] is False
    assert all(value is False for value in manifest["live_modes"].values())
    dumped = json.dumps(manifest)
    for credential_shape in ("sk-", "ghp_", "xoxb-", "AIza", "Bearer "):
        assert credential_shape not in dumped


def test_architect_and_eva_namespaces_are_isolated() -> None:
    architect = _load(ARCHITECT_PROFILE_PATH)
    eva = _load(EVA_PROFILE_PATH)
    assert architect["agent_id"] != eva["agent_id"]
    assert architect["hermes_profile"] != eva["hermes_profile"]
    assert architect["memory_namespace"] != eva["memory_namespace"]

    registry = AgentRegistry(
        [_architect_profile(architect), AgentProfile(
            agent_id=eva["agent_id"],
            hermes_profile=eva["hermes_profile"],
            memory_namespace=eva["memory_namespace"],
            capabilities=frozenset(eva["capabilities"]),
            resource_scopes=frozenset(eva["resource_scopes"]),
            runtime=RuntimeKind(eva["runtime"]),
        )]
    )
    assert registry.get("architect") is not None
    assert registry.get("eva") is not None


def test_policy_denies_every_architect_capability_while_grants_are_empty() -> None:
    profile = _architect_profile()
    policy = AgentPolicy()
    for capability, action, scope in (
        ("agent.invoke", ActionClass.INFORMATIONAL, None),
        ("n8n.workflow.design", ActionClass.BOUNDED_WRITE, None),
        ("n8n.workflow.activate", ActionClass.PRODUCTION_DEPLOYMENT, "n8n/production"),
        ("memory.read", ActionClass.INFORMATIONAL, "agents/architect"),
        ("service.n8n.call", ActionClass.SERVICE_CONNECTION, "n8n"),
    ):
        decision = policy.evaluate(
            profile,
            AccessRequest(
                agent_id="architect",
                capability=capability,
                action_class=action,
                resource_scope=scope,
            ),
        )
        assert decision.status is DecisionStatus.DENIED
        assert decision.code is DecisionCode.CAPABILITY_NOT_GRANTED


def test_generated_and_golden_workflows_remain_inactive() -> None:
    generated = n8n_builder.build_workflow(name="contract-draft", trigger="manual")
    assert generated["active"] is False
    for name, factory in n8n_builder.GOLDEN_TEMPLATES.items():
        workflow = factory()
        assert workflow["active"] is False, name
