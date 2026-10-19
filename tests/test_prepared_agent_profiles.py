"""Default-deny checks for every prepared agent manifest."""

from __future__ import annotations

import json
from pathlib import Path

from src.agent_platform.contracts import (
    AccessRequest,
    ActionClass,
    ActivationStatus,
    AgentProfile,
    DecisionCode,
    DecisionStatus,
    RuntimeKind,
)
from src.agent_platform.policy import AgentPolicy
from src.agent_platform.registry import AgentRegistry

ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = ROOT / "config" / "agents"
EXPECTED_IDS = frozenset({"eva", "architect", "marshal", "fin", "doc", "kira", "sam", "kodex", "alice", "oscar", "tyler", "jack", "ray", "dex", "atlas", "trainer"})
FORMED_IDENTITY = frozenset({"eva", "architect", "marshal", "sam", "fin", "alice", "oscar", "tyler", "jack"})


def _manifests() -> dict[str, dict]:
    files = sorted(PROFILES_DIR.glob("*.profile.json"))
    loaded = {path.stem.replace(".profile", ""): json.loads(path.read_text(encoding="utf-8")) for path in files}
    return loaded


def _profile(manifest: dict) -> AgentProfile:
    return AgentProfile(
        agent_id=manifest["agent_id"],
        runtime_profile=manifest["runtime_profile"],
        memory_namespace=manifest["memory_namespace"],
        capabilities=frozenset(manifest["capabilities"]),
        resource_scopes=frozenset(manifest["resource_scopes"]),
        runtime=RuntimeKind(manifest["runtime"]),
        activation_status=ActivationStatus(manifest["activation"]),
    )


def test_all_prepared_manifests_are_default_deny_and_isolated() -> None:
    manifests = _manifests()
    assert set(manifests) == EXPECTED_IDS

    profiles = []
    for agent_id, manifest in manifests.items():
        assert manifest["agent_id"] == agent_id
        assert manifest["activation"] == "prepared_not_enabled"
        expected_runtime = "antigravity_sdk" if agent_id == "alice" else "hermes"
        assert manifest["runtime"] == expected_runtime
        assert manifest["model_status"] == "not_selected"
        if agent_id == "architect":
            assert manifest["capabilities"] == []
            assert manifest["resource_scopes"] == []
            assert manifest["services_enabled"] == []
            assert all(grant["status"] == "proposed_not_applied" for grant in manifest["proposed_grants"])
            assert manifest["n8n"]["status"] == "not_configured"
            assert manifest["n8n"]["live_api"] is False
        elif agent_id == "fin":
            # Фін: лише внутрішні права (автовиклик Єви, локальні звіти); зовнішніх сервісів немає.
            assert manifest["capabilities"] == ["fin.dispatch.eva_basket", "fin.funds_check",
                                                "fin.reports.local", "fin.docs.local_generate"]
            assert manifest["resource_scopes"] == ["fin/out"]
            assert manifest["services_enabled"] == []
        elif agent_id == "kodex":
            # KODEX: читання всіх архівів, зміна файлів без мітки, переміщення мічених, зміна мічених — з дозволом Андрія.
            assert manifest["capabilities"] == ["kodex.archive.read_all", "kodex.archive.write_unlabeled",
                                                "kodex.labeled.move",
                                                "kodex.labeled.change_with_andrii_permission", "kodex.report.eva",
                                                "kodex.prompt.catalog", "kodex.skill.research",
                                                "kodex.integration.notebooklm", "kodex.integration.obsidian"]
            assert manifest["resource_scopes"] == ["kodex/archive"]
            assert manifest["services_enabled"] == []
            assert manifest["knowledge_base"]["protection"]["label"] == "andrii_protected"
            assert manifest["knowledge_base"]["protection"]["labeled_files"]["edit_or_delete"] == "лише з дозволом Андрія"
        elif agent_id in {"ray", "dex", "atlas", "trainer"}:
            assert manifest["capabilities"] == []
            assert manifest["resource_scopes"] == []
            assert manifest["services_enabled"] == []
            assert manifest["grants"] == []
            assert manifest["skills"] == []
            assert manifest["internet"]["enabled"] is False
            assert manifest["internet"]["allowed_domains"] == []
            assert manifest["egress"]["default"] == "deny"
            assert manifest["egress"]["allowed_domains"] == []
        else:
            assert manifest["capabilities"] == []
            assert manifest["resource_scopes"] == []
            assert manifest["services_enabled"] == []
        if agent_id in {"eva", "architect", "sam", "fin", "oscar", "tyler", "jack"}:
            assert manifest["skills"]
            assert all(item.get("activation") == "draft" for item in manifest["skills"])
        else:
            assert manifest["skills"] == []
        assert manifest["runtime_profile"] == agent_id
        assert manifest["memory_namespace"] == f"agents/{agent_id}"
        if agent_id in FORMED_IDENTITY:
            assert manifest["role_status"] in {"identity_draft", "agreed_draft"}
        else:
            assert manifest["role_status"] == "not_agreed"
            assert manifest["prompt_status"] == "not_prepared"
        if agent_id == "alice":
            assert manifest["role_status"] == "agreed_draft"
            assert manifest["prompt_status"] == "draft"
            assert manifest["runtime_profile"] == "alice"
            assert manifest["proposed_grants"]
            assert all(g["status"] == "proposed_not_applied" for g in manifest["proposed_grants"])
        profiles.append(_profile(manifest))

    registry = AgentRegistry(profiles)
    assert {item.agent_id for item in registry.profiles} == EXPECTED_IDS


def test_legacy_antigravity_manifest_is_retired_and_default_deny() -> None:
    manifest = json.loads(
        (PROFILES_DIR / "antigravity.live_profile.json").read_text(encoding="utf-8")
    )
    assert manifest["manifest_status"] == "legacy_alias_retired"
    assert manifest["agent_id"] == "alice"
    assert manifest["runtime"] == "antigravity_sdk"
    assert manifest["activation"] == "prepared_not_enabled"
    assert manifest["capabilities"] == []
    assert manifest["grants"] == []
    assert manifest["resource_scopes"] == []
    assert manifest["services_enabled"] == []
    assert "antigravity" not in _manifests()


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
        assert decision.code is DecisionCode.AGENT_NOT_ENABLED


def test_reference_skill_catalog_matches_profile_assignments() -> None:
    manifests = _manifests()
    catalog = json.loads((ROOT / "config" / "skill_library.json").read_text(encoding="utf-8"))
    assigned_by_agent = {agent_id: set(manifest.get("reference_skills", [])) for agent_id, manifest in manifests.items()}
    catalog_by_agent = {agent_id: set() for agent_id in manifests}

    for item in catalog["skills"]:
        for agent_id in item.get("agents", []):
            assert agent_id in catalog_by_agent
            catalog_by_agent[agent_id].add(item["id"])

    assert catalog_by_agent == assigned_by_agent
