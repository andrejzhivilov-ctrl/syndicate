"""Deployment-readiness checks for the Marshal identity-draft profile."""

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
from src.agents.marshal_access import marshal_agent_profile, load_marshal_manifest

ROOT = Path(__file__).resolve().parents[1]
MARSHAL_PROFILE_PATH = ROOT / "config" / "agents" / "marshal.profile.json"
EVA_PROFILE_PATH = ROOT / "config" / "agents" / "eva.profile.json"
FULL_SPEC_PATH = ROOT / "marshal_core" / "MARSHAL_FULL_SPEC.md"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_marshal_manifest_is_prepared_not_enabled_and_has_no_grants() -> None:
    manifest = load_marshal_manifest()
    profile = marshal_agent_profile(manifest)

    assert manifest["activation"] == "prepared_not_enabled"
    assert manifest["role_status"] == "identity_draft"
    assert manifest["model_status"] == "not_selected"
    assert manifest["prompt_status"] == "draft"
    assert profile.runtime is RuntimeKind.HERMES
    assert profile.capabilities == frozenset()
    assert profile.resource_scopes == frozenset()
    assert manifest["services_enabled"] == []
    assert manifest["skills"] == []
    assert not hasattr(profile, "role")

    prompt_path = ROOT / manifest["prompt_file"]
    assert prompt_path.is_file()
    prompt = prompt_path.read_text(encoding="utf-8")
    assert "Ніколи не проси вставити" in prompt
    assert "не автономний CSO" in prompt


def test_marshal_manifest_does_not_select_model_or_integrations() -> None:
    manifest = _load(MARSHAL_PROFILE_PATH)
    telegram = manifest["inbound_channels"]["telegram"]
    assert manifest["model_status"] == "not_selected"
    assert telegram["enabled"] is False
    assert telegram["bot_id"] is None
    assert telegram["chat_allowlist"] == []
    assert manifest["live_modes"]["host_control"] is False
    assert manifest["live_modes"]["emergency_lockdown"] is False
    assert manifest["live_modes"]["telegram_bot"] is False
    assert all(value is False for value in manifest["live_modes"].values())
    dumped = json.dumps(manifest)
    for credential_shape in ("sk-", "ghp_", "xoxb-", "AIza", "Bearer "):
        assert credential_shape not in dumped


def test_full_spec_is_not_copied_into_grants() -> None:
    manifest = _load(MARSHAL_PROFILE_PATH)
    dumped = json.dumps(manifest)
    assert FULL_SPEC_PATH.is_file()
    assert manifest["capabilities"] == []
    assert manifest["resource_scopes"] == []
    assert manifest["services_enabled"] == []
    assert "@marshal_security_bot" not in dumped
    assert "MARSHAL_FULL_SPEC" not in dumped


def test_marshal_and_eva_namespaces_are_isolated() -> None:
    marshal = _load(MARSHAL_PROFILE_PATH)
    eva = _load(EVA_PROFILE_PATH)
    assert marshal["agent_id"] != eva["agent_id"]
    assert marshal["hermes_profile"] != eva["hermes_profile"]
    assert marshal["memory_namespace"] != eva["memory_namespace"]

    registry = AgentRegistry(
        [
            marshal_agent_profile(marshal),
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
    assert registry.get("marshal") is not None
    assert registry.get("eva") is not None


def test_policy_denies_every_marshal_capability_while_grants_are_empty() -> None:
    profile = marshal_agent_profile()
    policy = AgentPolicy()
    for capability, action, scope in (
        ("agent.invoke", ActionClass.INFORMATIONAL, None),
        ("memory.read", ActionClass.INFORMATIONAL, "agents/marshal"),
        ("memory.write", ActionClass.BOUNDED_WRITE, "agents/marshal"),
        ("host.control", ActionClass.PRODUCTION_DEPLOYMENT, "host"),
        ("service.telegram.call", ActionClass.SERVICE_CONNECTION, "telegram"),
    ):
        decision = policy.evaluate(
            profile,
            AccessRequest(
                agent_id="marshal",
                capability=capability,
                action_class=action,
                resource_scope=scope,
            ),
        )
        assert decision.status is DecisionStatus.DENIED
        assert decision.code is DecisionCode.CAPABILITY_NOT_GRANTED
