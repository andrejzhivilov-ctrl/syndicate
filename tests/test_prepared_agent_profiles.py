"""Default-deny checks for every prepared agent manifest."""

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

ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = ROOT / "config" / "agents"
EXPECTED_IDS = frozenset({"eva", "architect", "marshal", "fin", "doc", "kira", "sam"})
FORMED_IDENTITY = frozenset({"eva", "architect", "marshal"})


def _manifests() -> dict[str, dict]:
    files = sorted(PROFILES_DIR.glob("*.profile.json"))
    loaded = {path.stem.replace(".profile", ""): json.loads(path.read_text(encoding="utf-8")) for path in files}
    return loaded


def _profile(manifest: dict) -> AgentProfile:
    return AgentProfile(
        agent_id=manifest["agent_id"],
        hermes_profile=manifest["hermes_profile"],
        memory_namespace=manifest["memory_namespace"],
        capabilities=frozenset(manifest["capabilities"]),
        resource_scopes=frozenset(manifest["resource_scopes"]),
        runtime=RuntimeKind(manifest["runtime"]),
    )


def test_all_prepared_manifests_are_default_deny_and_isolated() -> None:
    manifests = _manifests()
    assert set(manifests) == EXPECTED_IDS

    profiles = []
    for agent_id, manifest in manifests.items():
        assert manifest["agent_id"] == agent_id
        assert manifest["activation"] == "prepared_not_enabled"
        assert manifest["runtime"] == "hermes"
        assert manifest["model_status"] == "not_selected"
        assert manifest["capabilities"] == []
        assert manifest["resource_scopes"] == []
        assert manifest["services_enabled"] == []
        if agent_id == "eva":
            assert manifest["skills"]
            assert all(item.get("activation") == "draft" for item in manifest["skills"])
        else:
            assert manifest["skills"] == []
        assert manifest["hermes_profile"] == agent_id
        assert manifest["memory_namespace"] == f"agents/{agent_id}"
        if agent_id in FORMED_IDENTITY:
            assert manifest["role_status"] in {"identity_draft", "agreed_draft"}
        else:
            assert manifest["role_status"] == "not_agreed"
            assert manifest["prompt_status"] == "not_prepared"
        profiles.append(_profile(manifest))

    registry = AgentRegistry(profiles)
    assert {item.agent_id for item in registry.profiles} == EXPECTED_IDS


def test_policy_denies_ungranted_capabilities_for_every_prepared_profile() -> None:
    policy = AgentPolicy()
    for manifest in _manifests().values():
        profile = _profile(manifest)
        decision = policy.evaluate(
            profile,
            AccessRequest(
                agent_id=profile.agent_id,
                capability="agent.invoke",
                action_class=ActionClass.INFORMATIONAL,
            ),
        )
        assert decision.status is DecisionStatus.DENIED
        assert decision.code is DecisionCode.CAPABILITY_NOT_GRANTED
