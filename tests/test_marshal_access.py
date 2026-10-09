"""Fail-closed Marshal access: empty grants, host control deny, Telegram deny."""

from __future__ import annotations

from src.agent_platform.contracts import (
    AccessRequest,
    ActionClass,
    AgentProfile,
    DecisionCode,
    DecisionStatus,
    RuntimeKind,
)
from src.agent_platform.policy import AgentPolicy
from src.agents.marshal_access import (
    load_marshal_manifest,
    marshal_agent_profile,
    marshal_host_control_allowed,
    marshal_memory_namespace_allowed,
    marshal_telegram_inbound_allowed,
)


def test_marshal_manifest_grants_remain_empty_and_channels_disabled() -> None:
    manifest = load_marshal_manifest()
    profile = marshal_agent_profile(manifest)
    telegram = manifest["inbound_channels"]["telegram"]

    assert manifest["activation"] == "prepared_not_enabled"
    assert profile.capabilities == frozenset()
    assert profile.resource_scopes == frozenset()
    assert manifest["services_enabled"] == []
    assert telegram["enabled"] is False
    assert telegram["chat_allowlist"] == []
    assert marshal_host_control_allowed(manifest) is False
    assert marshal_telegram_inbound_allowed("123") is False
    assert marshal_memory_namespace_allowed("eva") is False
    assert marshal_memory_namespace_allowed("marshal") is True


def test_empty_grants_deny_own_and_foreign_memory_capabilities() -> None:
    profile = marshal_agent_profile()
    policy = AgentPolicy()
    for capability, scope in (
        ("memory.read", "agents/marshal"),
        ("memory.write", "agents/marshal"),
        ("memory.read", "agents/eva"),
        ("memory.write", "agents/fin"),
    ):
        decision = policy.evaluate(
            profile,
            AccessRequest(
                agent_id="marshal",
                capability=capability,
                action_class=ActionClass.BOUNDED_WRITE if capability.endswith("write") else ActionClass.INFORMATIONAL,
                resource_scope=scope,
            ),
        )
        assert decision.status is DecisionStatus.DENIED
        assert decision.code is DecisionCode.CAPABILITY_NOT_GRANTED


def test_memory_capability_would_still_deny_foreign_namespace() -> None:
    profile = AgentProfile(
        agent_id="marshal",
        hermes_profile="marshal",
        memory_namespace="agents/marshal",
        capabilities=frozenset({"memory.read", "memory.write"}),
        runtime=RuntimeKind.HERMES,
    )
    policy = AgentPolicy()
    own = policy.evaluate(
        profile,
        AccessRequest(
            agent_id="marshal",
            capability="memory.read",
            action_class=ActionClass.INFORMATIONAL,
            resource_scope="agents/marshal",
        ),
    )
    foreign = policy.evaluate(
        profile,
        AccessRequest(
            agent_id="marshal",
            capability="memory.read",
            action_class=ActionClass.INFORMATIONAL,
            resource_scope="agents/eva",
        ),
    )
    assert own.status is DecisionStatus.ALLOWED
    assert foreign.status is DecisionStatus.DENIED
    assert foreign.code is DecisionCode.RESOURCE_SCOPE_NOT_GRANTED
    assert load_marshal_manifest()["capabilities"] == []
