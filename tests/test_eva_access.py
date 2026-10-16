"""Fail-closed Eva access: empty grants, own-namespace memory, Telegram deny."""

from __future__ import annotations

import asyncio
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
from src.agents.eva import EvaAgent
from src.agents.eva_access import (
    eva_agent_profile,
    eva_memory_namespace_allowed,
    eva_telegram_inbound_allowed,
    extract_telegram_chat_id,
    load_eva_manifest,
    telegram_inbound_allowed,
)
from src.vault_md import MarkdownVault

ROOT = Path(__file__).resolve().parents[1]


def _run(coro):
    return asyncio.run(coro)


def test_eva_manifest_grants_remain_empty_and_telegram_is_disabled() -> None:
    manifest = load_eva_manifest()
    profile = eva_agent_profile(manifest)
    telegram = manifest["inbound_channels"]["telegram"]

    assert manifest["activation"] == "prepared_not_enabled"
    assert profile.capabilities == frozenset()
    assert profile.resource_scopes == frozenset()
    assert manifest["services_enabled"] == []
    assert telegram["enabled"] is False
    assert telegram["bot_id"] is None
    assert telegram["chat_allowlist"] == []
    assert manifest["knowledge_bases"]["psychology"]["status"] == "not_loaded"
    sources = (ROOT / "eva_core/knowledge/psychology/SOURCES.yaml").read_text(encoding="utf-8")
    assert "sources: []" in sources


def test_empty_grants_deny_own_and_foreign_memory_capabilities() -> None:
    profile = eva_agent_profile()
    policy = AgentPolicy()
    for capability, scope in (
        ("memory.read", "agents/eva"),
        ("memory.write", "agents/eva"),
        ("memory.read", "agents/fin"),
        ("memory.write", "agents/doc"),
    ):
        decision = policy.evaluate(
            profile,
            AccessRequest(
                agent_id="eva",
                capability=capability,
                action_class=ActionClass.BOUNDED_WRITE if capability.endswith("write") else ActionClass.INFORMATIONAL,
                resource_scope=scope,
            ),
        )
        assert decision.status is DecisionStatus.DENIED
        assert decision.code is DecisionCode.CAPABILITY_NOT_GRANTED


def test_memory_capability_would_still_deny_foreign_namespace() -> None:
    """Proposed boundary: even with a future own-namespace grant, others stay deny."""
    profile = AgentProfile(
        agent_id="eva",
        runtime_profile="eva",
        memory_namespace="agents/eva",
        capabilities=frozenset({"memory.read", "memory.write"}),
        runtime=RuntimeKind.HERMES,
    )
    policy = AgentPolicy()
    own = policy.evaluate(
        profile,
        AccessRequest(
            agent_id="eva",
            capability="memory.read",
            action_class=ActionClass.INFORMATIONAL,
            resource_scope="agents/eva",
        ),
    )
    foreign = policy.evaluate(
        profile,
        AccessRequest(
            agent_id="eva",
            capability="memory.read",
            action_class=ActionClass.INFORMATIONAL,
            resource_scope="agents/fin",
        ),
    )
    assert own.status is DecisionStatus.ALLOWED
    assert foreign.status is DecisionStatus.DENIED
    assert foreign.code is DecisionCode.RESOURCE_SCOPE_NOT_GRANTED
    assert json.loads((ROOT / "config/agents/eva.profile.json").read_text(encoding="utf-8"))["capabilities"] == []


def test_empty_telegram_allowlist_is_deny() -> None:
    assert telegram_inbound_allowed(enabled=True, allowlist=[], chat_id="1") is False
    assert telegram_inbound_allowed(enabled=False, allowlist=["1"], chat_id="1") is False
    assert telegram_inbound_allowed(enabled=True, allowlist=["1"], chat_id=None) is False
    assert eva_telegram_inbound_allowed("123") is False
    assert extract_telegram_chat_id({"message": "hello"}) is None
    assert not eva_memory_namespace_allowed("fin")
    assert eva_memory_namespace_allowed("eva") is True


def test_eva_chat_refuses_cross_agent_remember(tmp_path) -> None:
    vault = MarkdownVault(vault_root=tmp_path / "vault")
    agent = EvaAgent(memory=None, llm=None, vault=vault)
    result = _run(agent.execute({
        "action": "chat",
        "message": "Запам'ятай мій пульс у спокої 58 уд/хв та вага 80 кг",
    }))
    assert result["status"] == "refused"
    assert result["error"] == "cross_agent_memory_denied"
    assert not vault.exists("agents/doc/memory.md")
    assert not vault.exists("agents/eva/memory.md")


def test_eva_recall_ignores_other_agent_memory(tmp_path) -> None:
    vault = MarkdownVault(vault_root=tmp_path / "vault")
    vault.remember("fin", "Foreign budget fact", source="test", confirmed=True)
    vault.remember("eva", "Eva own archive fact", source="test", confirmed=True)
    prompts: list = []

    class _LLM:
        async def ainvoke(self, messages):
            prompts.append(messages)
            return type("Reply", (), {"content": "ok"})()

    agent = EvaAgent(memory=None, llm=_LLM(), vault=vault)
    result = _run(agent.execute({"action": "chat", "message": "Привіт"}))
    assert result["status"] == "completed"
    prompt_text = prompts[0][0].content
    assert "Eva own archive fact" in prompt_text
    assert "Foreign budget fact" not in prompt_text


def test_webhook_telegram_is_denied_when_allowlist_is_empty() -> None:
    from src.orchestrator import EvaOrchestrator

    class OrchestratorStub:
        _memory = None
        _llm = None
        _config = {}
        _vault = None

    state = {
        "task_type": "webhook_telegram",
        "payload": {"message": {"text": "hello", "chat": {"id": 99}}},
    }
    _run(EvaOrchestrator._eva_direct_handler(OrchestratorStub(), state))
    assert state["result"]["status"] == "denied"
    assert state["result"]["error"] == "telegram_inbound_denied"
    assert state["status"] == "completed"
