"""Tests for the role-neutral SYNDICATE control-plane foundation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.agent_platform import (  # noqa: E402
    AccessRequest,
    ActionClass,
    AgentDispatcher,
    AgentInvocation,
    AgentPolicy,
    AgentProfile,
    AgentRegistry,
    DecisionCode,
    DecisionStatus,
    DispatchStatus,
    MemoryAccessDenied,
    MemoryManagerAdapter,
    MemoryManagerAuditSink,
)
from src.agent_platform.audit import AgentAuditEvent  # noqa: E402
from src.agent_platform.policy import HUMAN_APPROVAL_ACTIONS  # noqa: E402


class FakeRuntime:
    def __init__(self, response: Any = "ok", error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.calls: list[tuple[AgentProfile, AgentInvocation]] = []

    async def invoke(self, *, profile: AgentProfile, request: AgentInvocation) -> str:
        self.calls.append((profile, request))
        if self.error is not None:
            raise self.error
        return self.response


class FakeAuditSink:
    def __init__(self, error: Exception | None = None) -> None:
        self.events: list[AgentAuditEvent] = []
        self.error = error

    async def record(self, event: AgentAuditEvent) -> bool:
        if self.error is not None:
            raise self.error
        self.events.append(event)
        return True


class FakeDecisionWriter:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def write_audit_decision(self, **kwargs: Any) -> bool:
        self.calls.append(kwargs)
        return True


class FakeMemoryManager:
    def __init__(self) -> None:
        self.read_calls: list[dict[str, object]] = []
        self.write_calls: list[dict[str, object]] = []

    async def get_recent_episodes(self, session_id: str, agent_id: str, limit: int = 20):
        self.read_calls.append({"session_id": session_id, "agent_id": agent_id, "limit": limit})
        return [{"content": "stored"}]

    async def save_episode(
        self,
        session_id: str | None = None,
        agent_id: str = "eva",
        role: str = "assistant",
        content: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        self.write_calls.append(
            {
                "session_id": session_id,
                "agent_id": agent_id,
                "role": role,
                "content": content,
                "metadata": metadata or {},
            }
        )
        return "episode-1"


def _profile(
    *,
    capabilities: frozenset[str] = frozenset({"agent.invoke"}),
    resource_scopes: frozenset[str] = frozenset(),
) -> AgentProfile:
    return AgentProfile(
        agent_id="generic-agent",
        hermes_profile="generic-agent",
        memory_namespace="agents/generic-agent",
        capabilities=capabilities,
        resource_scopes=resource_scopes,
    )


def _invocation(
    *,
    capability: str = "agent.invoke",
    action_class: ActionClass = ActionClass.INFORMATIONAL,
    resource_scope: str | None = None,
    agent_id: str = "generic-agent",
    prompt: str = "Please help.",
) -> AgentInvocation:
    return AgentInvocation(
        request_id="request-001",
        task_id="task-001",
        access=AccessRequest(
            agent_id=agent_id,
            capability=capability,
            action_class=action_class,
            resource_scope=resource_scope,
        ),
        prompt=prompt,
    )


def test_profile_is_hermes_by_default_and_has_no_implicit_grants() -> None:
    profile = AgentProfile(
        agent_id="generic-agent",
        hermes_profile="generic-agent",
        memory_namespace="agents/generic-agent",
    )

    assert profile.runtime.value == "hermes"
    assert profile.capabilities == frozenset()
    assert profile.resource_scopes == frozenset()
    assert not hasattr(profile, "role")


def test_profile_rejects_wildcards_and_prohibited_grants() -> None:
    with pytest.raises(ValueError, match="wildcards"):
        _profile(capabilities=frozenset({"*"}))
    with pytest.raises(ValueError, match="prohibited_capability"):
        _profile(capabilities=frozenset({"communication.email.send"}))
    with pytest.raises(ValueError, match="wildcards"):
        _profile(resource_scopes=frozenset({"drive.folder:*"}))


def test_registry_requires_isolated_hermes_profiles_and_memory_namespaces() -> None:
    first = _profile()
    same_runtime_profile = AgentProfile(
        agent_id="other-agent",
        hermes_profile=first.hermes_profile,
        memory_namespace="agents/other-agent",
        capabilities=frozenset(),
    )
    same_memory = AgentProfile(
        agent_id="other-agent",
        hermes_profile="other-agent",
        memory_namespace=first.memory_namespace,
        capabilities=frozenset(),
    )

    with pytest.raises(ValueError, match="hermes_profile_must_be_isolated"):
        AgentRegistry([first, same_runtime_profile])
    with pytest.raises(ValueError, match="memory_namespace_must_be_isolated"):
        AgentRegistry([first, same_memory])


def test_registry_does_not_invent_a_default_profile() -> None:
    registry = AgentRegistry()

    assert registry.get("generic-agent") is None
    assert registry.profiles == ()


def test_policy_denies_missing_capability_and_unknown_agent() -> None:
    policy = AgentPolicy()
    no_grants = _profile(capabilities=frozenset())

    no_grant = policy.evaluate(no_grants, _invocation().access)
    unknown = policy.evaluate(None, _invocation(agent_id="unconfigured-agent").access)

    assert no_grant == type(no_grant)(DecisionStatus.DENIED, DecisionCode.CAPABILITY_NOT_GRANTED)
    assert unknown == type(unknown)(DecisionStatus.DENIED, DecisionCode.UNKNOWN_AGENT)


def test_profile_cannot_be_reused_under_another_agent_id() -> None:
    decision = AgentPolicy().evaluate(
        _profile(),
        _invocation(agent_id="other-agent").access,
    )

    assert decision.status is DecisionStatus.DENIED
    assert decision.code is DecisionCode.AGENT_MISMATCH


def test_resource_access_requires_an_exact_explicit_scope() -> None:
    profile = _profile(
        capabilities=frozenset({"service.google_drive.read", "memory.read"}),
        resource_scopes=frozenset({"drive.folder:owned", "memory.namespace:generic-agent"}),
    )
    policy = AgentPolicy()

    allowed = policy.evaluate(
        profile,
        _invocation(
            capability="service.google_drive.read",
            resource_scope="drive.folder:owned",
        ).access,
    )
    missing_scope = policy.evaluate(
        profile,
        _invocation(capability="memory.read").access,
    )
    other_scope = policy.evaluate(
        profile,
        _invocation(
            capability="service.google_drive.read",
            resource_scope="drive.folder:someone-else",
        ).access,
    )

    assert allowed.status is DecisionStatus.ALLOWED
    assert missing_scope.code is DecisionCode.RESOURCE_SCOPE_REQUIRED
    assert other_scope.code is DecisionCode.RESOURCE_SCOPE_NOT_GRANTED


def test_resource_scoped_capability_alias_cannot_omit_its_scope() -> None:
    profile = _profile(capabilities=frozenset({"memory_read"}))

    decision = AgentPolicy().evaluate(
        profile,
        _invocation(capability="memory_read").access,
    )

    assert decision.status is DecisionStatus.DENIED
    assert decision.code is DecisionCode.RESOURCE_SCOPE_REQUIRED


def test_all_protected_action_classes_require_human_approval() -> None:
    profile = _profile(capabilities=frozenset({"action.execute"}))
    policy = AgentPolicy()

    for action_class in HUMAN_APPROVAL_ACTIONS:
        decision = policy.evaluate(
            profile,
            _invocation(capability="action.execute", action_class=action_class).access,
        )
        assert decision.status is DecisionStatus.APPROVAL_REQUIRED, action_class
        assert decision.code is DecisionCode.HUMAN_APPROVAL_REQUIRED


def test_prohibited_capabilities_are_denied_even_without_a_matching_grant() -> None:
    profile = _profile()

    decision = AgentPolicy().evaluate(
        profile,
        _invocation(
            capability="authentication.diia.login",
            action_class=ActionClass.EXTERNAL_COMMUNICATION,
        ).access,
    )

    assert decision.status is DecisionStatus.DENIED
    assert decision.code is DecisionCode.PROHIBITED_CAPABILITY


@pytest.mark.parametrize(
    "capability",
    [
        "communication.email.send",
        "communication.email.send_email",
        "authentication.diia.login",
        "authentication.army_plus.login",
        "authentication.bankid.login",
        "browser.fingerprint.spoof",
        "network.residential_proxy.rotate",
    ],
)
def test_explicitly_out_of_scope_capabilities_cannot_dispatch(capability: str) -> None:
    runtime = FakeRuntime()
    sink = FakeAuditSink()
    dispatcher = AgentDispatcher(
        registry=AgentRegistry([_profile()]),
        runtime=runtime,
        audit_sink=sink,
    )

    result = asyncio_run(dispatcher.dispatch(_invocation(capability=capability)))

    assert result.status is DispatchStatus.DENIED
    assert result.decision.code is DecisionCode.PROHIBITED_CAPABILITY
    assert runtime.calls == []
    assert sink.events[0].status is DispatchStatus.DENIED


def test_protected_financial_action_never_reaches_hermes_without_approval() -> None:
    runtime = FakeRuntime()
    sink = FakeAuditSink()
    dispatcher = AgentDispatcher(
        registry=AgentRegistry([_profile(capabilities=frozenset({"trade.execute"}))]),
        runtime=runtime,
        audit_sink=sink,
    )

    result = asyncio_run(
        dispatcher.dispatch(
            _invocation(
                capability="trade.execute",
                action_class=ActionClass.FINANCIAL_OPERATION,
            )
        )
    )

    assert result.status is DispatchStatus.APPROVAL_REQUIRED
    assert result.decision.status is DecisionStatus.APPROVAL_REQUIRED
    assert runtime.calls == []
    assert sink.events[0].requires_hitl is True


def test_dispatch_redacts_pii_before_runtime_and_keeps_audit_payload_free() -> None:
    runtime = FakeRuntime(response="completed")
    sink = FakeAuditSink()
    dispatcher = AgentDispatcher(
        registry=AgentRegistry([_profile()]),
        runtime=runtime,
        audit_sink=sink,
    )
    private_prompt = "Email andrii.test@example.com or call +380671234567; token ghp_dummyexample123."

    result = asyncio_run(dispatcher.dispatch(_invocation(prompt=private_prompt)))

    assert result.status is DispatchStatus.COMPLETED
    assert result.content == "completed"
    sent_prompt = runtime.calls[0][1].prompt
    assert "andrii.test@example.com" not in sent_prompt
    assert "+380671234567" not in sent_prompt
    assert "ghp_dummyexample123" not in sent_prompt
    assert len(sink.events) == 1
    audit_text = repr(sink.events[0])
    assert "andrii.test@example.com" not in audit_text
    assert "+380671234567" not in audit_text
    assert "ghp_dummyexample123" not in audit_text
    assert "private_prompt" not in sink.events[0].__dataclass_fields__


def test_runtime_failure_does_not_expose_exception_text() -> None:
    runtime = FakeRuntime(error=RuntimeError("do not leak this user-controlled string"))
    sink = FakeAuditSink()
    dispatcher = AgentDispatcher(
        registry=AgentRegistry([_profile()]),
        runtime=runtime,
        audit_sink=sink,
    )

    result = asyncio_run(dispatcher.dispatch(_invocation()))

    assert result.status is DispatchStatus.FAILED
    assert result.error_code == "runtime_error"
    assert result.content is None
    assert "user-controlled" not in repr(result)
    assert sink.events[0].status is DispatchStatus.FAILED


def test_audit_outage_is_best_effort_and_never_logs_or_blocks_on_payload() -> None:
    runtime = FakeRuntime(response="ok")
    sink = FakeAuditSink(error=RuntimeError("private audit backend detail"))
    dispatcher = AgentDispatcher(
        registry=AgentRegistry([_profile()]),
        runtime=runtime,
        audit_sink=sink,
    )

    result = asyncio_run(dispatcher.dispatch(_invocation()))

    assert result.status is DispatchStatus.COMPLETED
    assert len(runtime.calls) == 1


def test_location_access_is_not_enabled_by_a_capability_alone() -> None:
    profile = _profile(
        capabilities=frozenset({"location.gps.read"}),
        resource_scopes=frozenset({"device.location"}),
    )

    decision = AgentPolicy().evaluate(
        profile,
        _invocation(
            capability="location.gps.read",
            action_class=ActionClass.LOCATION_ACCESS,
            resource_scope="device.location",
        ).access,
    )

    assert decision.status is DecisionStatus.APPROVAL_REQUIRED
    assert decision.code is DecisionCode.HUMAN_APPROVAL_REQUIRED


def test_bounded_skill_learning_is_allowed_only_inside_an_explicit_grant() -> None:
    profile = _profile(capabilities=frozenset({"skills.learn"}))

    allowed = AgentPolicy().evaluate(
        profile,
        _invocation(capability="skills.learn", action_class=ActionClass.BOUNDED_WRITE).access,
    )
    without_grant = AgentPolicy().evaluate(
        _profile(capabilities=frozenset()),
        _invocation(capability="skills.learn", action_class=ActionClass.BOUNDED_WRITE).access,
    )

    assert allowed.status is DecisionStatus.ALLOWED
    assert without_grant.status is DecisionStatus.DENIED


def test_service_and_policy_expansion_are_never_ordinary_writes() -> None:
    profile = _profile(capabilities=frozenset({"change.request"}))
    policy = AgentPolicy()

    service = policy.evaluate(
        profile,
        _invocation(capability="change.request", action_class=ActionClass.SERVICE_CONNECTION).access,
    )
    policy_change = policy.evaluate(
        profile,
        _invocation(capability="change.request", action_class=ActionClass.AUTHORITY_CHANGE).access,
    )

    assert service.status is DecisionStatus.APPROVAL_REQUIRED
    assert policy_change.status is DecisionStatus.APPROVAL_REQUIRED


def test_scoped_memory_adapter_binds_the_profiles_namespace_and_redacts_on_write() -> None:
    memory = FakeMemoryManager()
    adapter = MemoryManagerAdapter(
        memory=memory,
        profile=_profile(capabilities=frozenset({"memory.read", "memory.write"})),
        session_id="task-001",
    )

    recalled = asyncio_run(adapter.recall(limit=7))
    saved = asyncio_run(
        adapter.save(
            role="assistant",
            content="Contact andrii.test@example.com about this.",
            metadata={
                "phone": "+380671234567",
                "category": "lesson",
                "status": "ok",
                "free_text": "andrii.test@example.com",
            },
        )
    )

    assert recalled == [{"content": "stored"}]
    assert memory.read_calls == [
        {"session_id": "task-001", "agent_id": "agents/generic-agent", "limit": 7}
    ]
    assert saved == "episode-1"
    assert memory.write_calls[0]["agent_id"] == "agents/generic-agent"
    assert memory.write_calls[0]["session_id"] == "task-001"
    assert "andrii.test@example.com" not in memory.write_calls[0]["content"]
    assert memory.write_calls[0]["metadata"] == {"category": "lesson", "status": "ok"}
    assert "+380671234567" not in str(memory.write_calls[0]["metadata"])
    assert "andrii.test@example.com" not in str(memory.write_calls[0]["metadata"])


def test_scoped_memory_adapter_denies_memory_without_explicit_read_write_grants() -> None:
    memory = FakeMemoryManager()
    adapter = MemoryManagerAdapter(
        memory=memory,
        profile=_profile(capabilities=frozenset()),
        session_id="task-001",
    )

    with pytest.raises(MemoryAccessDenied, match="memory_access_denied:capability_not_granted"):
        asyncio_run(adapter.recall())
    with pytest.raises(MemoryAccessDenied, match="memory_access_denied:capability_not_granted"):
        asyncio_run(adapter.save(role="assistant", content="not stored"))
    assert memory.read_calls == []
    assert memory.write_calls == []


def test_scoped_memory_adapter_bounds_reads_and_validates_roles() -> None:
    adapter = MemoryManagerAdapter(
        memory=FakeMemoryManager(),
        profile=_profile(capabilities=frozenset({"memory.read", "memory.write"})),
        session_id="task-001",
    )

    with pytest.raises(ValueError, match="recall_limit_out_of_range"):
        asyncio_run(adapter.recall(limit=51))
    with pytest.raises(ValueError, match="invalid_memory_role"):
        asyncio_run(adapter.save(role="admin", content="not allowed"))


def test_memory_manager_audit_sink_writes_only_fixed_metadata() -> None:
    writer = FakeDecisionWriter()
    sink = MemoryManagerAuditSink(writer)
    event = AgentAuditEvent(
        request_id="request-001",
        task_id="task-001",
        agent_id="generic-agent",
        action_class=ActionClass.FINANCIAL_OPERATION,
        decision_code=DecisionCode.HUMAN_APPROVAL_REQUIRED,
        status=DispatchStatus.APPROVAL_REQUIRED,
        requires_hitl=True,
        allowed=False,
    )

    stored = asyncio_run(sink.record(event))

    assert stored is True
    assert len(writer.calls) == 1
    audit_call = writer.calls[0]
    assert audit_call["action"] == "agent_platform_human_approval_required"
    assert audit_call["task_type"] == "financial_operation"
    assert audit_call["outcome"] == "pending"
    assert audit_call["hitl_override"] is False
    assert audit_call["details"] == {
        "task_id": "task-001",
        "result_status": "approval_required",
        "requires_hitl": True,
        "allowed": False,
    }
    assert "prompt" not in repr(audit_call)
    assert "resource_scope" not in repr(audit_call)


def asyncio_run(awaitable):
    """Run one coroutine in tests without depending on pytest-asyncio."""
    import asyncio

    return asyncio.run(awaitable)
