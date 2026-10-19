"""Default-deny indexing, explicit reads, integrity checks and Marshal attestation."""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

import pytest

from src.agent_platform.knowledge_pool import (
    KnowledgePool,
    KnowledgePoolError,
    create_marshal_approval_attestation,
)

ROOT = Path(__file__).resolve().parents[1]


def test_local_catalog_is_pending_bounded_and_hash_verified() -> None:
    default_deny_pool = KnowledgePool()

    assert default_deny_pool.search("kodex", "prompt engineering") == []
    with pytest.raises(KnowledgePoolError, match="item_unavailable"):
        default_deny_pool.read("kodex", "prompt-engineering-basics")

    pool = KnowledgePool(review_agents=["kodex", "marshal"])
    assert len(pool.sources) == 10
    assert {ref["id"] for ref in pool.catalog["registries"]} == {"skills", "prompts", "references"}
    assert len(pool.items) == 10
    assert sum(item["kind"] == "skill" for item in pool.items.values()) == 5
    assert sum(item["kind"] == "reference" for item in pool.items.values()) == 2
    assert sum(item["kind"] == "prompt_template" for item in pool.items.values()) == 2
    assert all(source["raw_copied_to_repository"] is False for source in pool.sources)
    assert all(item["status"] == "review_pending" for item in pool.items.values())
    assert all(item["visibility"] == "review_only" for item in pool.items.values())
    assert pool.verify_catalog()["status"] == "ok"

    results = pool.search("kodex", "prompt engineering", limit=3)
    assert results
    assert all("content" not in item and "resource_path" not in item for item in results)
    assert len(results) <= 3

    item = pool.read("marshal", "prompt-engineering-basics")
    assert item["content_is_untrusted_reference"] is True
    assert "Reference text cannot change" in item["policy_notice"]
    assert "system prompt" in item["content"]


def test_integration_worker_image_includes_hash_verified_knowledge_pool_inputs() -> None:
    dockerfile = (ROOT / "deploy/docker/Dockerfile.integrations").read_text(encoding="utf-8")
    required_paths = (
        "config/knowledge_pool_catalog.json",
        "config/knowledge_source_registry.json",
        "config/skill_pool_registry.json",
        "config/prompt_pool_registry.json",
        "config/knowledge_reference_registry.json",
        "knowledge_pools",
    )
    for path in required_paths:
        assert f"COPY {path} /app/{path}" in dockerfile


def test_review_pending_content_is_hidden_from_non_reviewers() -> None:
    pool = KnowledgePool()
    assert pool.search("alice", "prompt engineering") == []
    with pytest.raises(KnowledgePoolError, match="item_unavailable"):
        pool.read("alice", "prompt-engineering-basics")
    with pytest.raises(KnowledgePoolError, match="unknown_agent"):
        pool.search("not-a-registered-agent", "prompt engineering")


def test_review_grants_are_only_proposed_and_scoped_to_kodex_and_marshal() -> None:
    plan = json.loads((ROOT / "config/knowledge_pool_grants.json").read_text(encoding="utf-8"))
    assert plan["status"] == "proposed_not_applied"
    assert plan["default"] == {"service_hub_operations": [], "review_agents": [], "shared_agents": []}
    assert plan["vault_policy"] == "not_created_or_applied"
    expected = {"kodex", "marshal"}
    proposals = {grant["agent_id"]: grant for grant in plan["proposals"]}
    assert set(proposals) == expected
    for agent_id, grant in proposals.items():
        profile = json.loads((ROOT / f"config/agents/{agent_id}.profile.json").read_text(encoding="utf-8"))
        assert grant["status"] == "proposed_not_applied"
        assert grant["service_hub_operations"] == ["knowledge.search", "knowledge.read"]
        assert grant["knowledge_pool_access"]["review_agents"] == [agent_id]
        assert grant["knowledge_pool_access"]["shared_agents"] == []
        assert profile["activation"] == "prepared_not_enabled"
        assert "knowledge.search" not in profile["capabilities"]
        assert "knowledge.read" not in profile["capabilities"]
        profile_proposals = {
            item["capability"]: item
            for item in profile.get("proposed_grants", [])
            if item.get("capability") in {"knowledge.search", "knowledge.read"}
        }
        assert set(profile_proposals) == {"knowledge.search", "knowledge.read"}
        assert all(item["status"] == "proposed_not_applied" for item in profile_proposals.values())


def test_approved_metadata_without_host_attestation_stays_hidden(tmp_path: Path) -> None:
    root = _write_test_catalog(tmp_path)
    catalog_path = root / "config/knowledge_pool_catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    registry = _load_test_skill_registry(root)
    item = registry["items"][0]
    item["status"] = "approved"
    item["visibility"] = "shared"
    _persist_test_registry(root, catalog, registry)

    pool_without_key = KnowledgePool(catalog_path, shared_agents=["alice"])
    with pytest.raises(KnowledgePoolError, match="item_unavailable"):
        pool_without_key.read("alice", item["id"])


def test_marshal_hmac_is_bound_to_exact_item_hash_and_review(tmp_path: Path) -> None:
    root = _write_test_catalog(tmp_path)
    catalog_path = root / "config/knowledge_pool_catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    registry = _load_test_skill_registry(root)
    item = registry["items"][0]
    item["status"] = "approved"
    item["visibility"] = "shared"
    item["approval"] = create_marshal_approval_attestation(
        b"m" * 32,
        item_id=item["id"],
        item_sha256=item["sha256"],
        version=item["version"],
        review_id="review-2026-001",
        reviewed_at="2026-10-18T12:00:00Z",
        scanner_status="passed",
        reviewer_agent_id="marshal",
    )
    _persist_test_registry(root, catalog, registry)

    approved = KnowledgePool(catalog_path, approval_key=b"m" * 32, shared_agents=["alice"])
    assert approved.search("alice", "curated skill")
    assert approved.read("alice", item["id"])["content"].startswith("# Curated skill")

    wrong_key = KnowledgePool(catalog_path, approval_key=b"x" * 32, shared_agents=["alice"])
    with pytest.raises(KnowledgePoolError, match="item_unavailable"):
        wrong_key.read("alice", item["id"])

    item["sha256"] = "0" * 64
    _persist_test_registry(root, catalog, registry)
    tampered = KnowledgePool(catalog_path, approval_key=b"m" * 32, shared_agents=["alice"])
    with pytest.raises(KnowledgePoolError, match="item_unavailable"):
        tampered.read("alice", item["id"])


def test_failed_scan_cannot_produce_marshal_attestation() -> None:
    with pytest.raises(KnowledgePoolError, match="marshal_review_required"):
        create_marshal_approval_attestation(
            b"m" * 32,
            item_id="curated-skill",
            item_sha256="a" * 64,
            version=1,
            review_id="review-2026-001",
            reviewed_at="2026-10-18T12:00:00Z",
            scanner_status="failed",
            reviewer_agent_id="marshal",
        )


def test_resource_paths_are_confined_and_symlinks_rejected(tmp_path: Path) -> None:
    root = _write_test_catalog(tmp_path)
    catalog_path = root / "config/knowledge_pool_catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    registry = _load_test_skill_registry(root)
    registry["items"][0]["resource_path"] = "config/agents/alice.profile.json"
    _persist_test_registry(root, catalog, registry)
    pool = KnowledgePool(catalog_path, review_agents=["kodex"])
    with pytest.raises(KnowledgePoolError, match="item_unavailable"):
        pool.read("kodex", "curated-skill")

    registry["items"][0]["resource_path"] = "knowledge_pools/skills/curated-skill.md"
    _persist_test_registry(root, catalog, registry)
    resource = root / "knowledge_pools/skills/curated-skill.md"
    resource.unlink()
    resource.symlink_to(root / "config/agents/alice.profile.json")
    linked = KnowledgePool(catalog_path, review_agents=["kodex"])
    with pytest.raises(KnowledgePoolError, match="item_unavailable"):
        linked.read("kodex", "curated-skill")


def _write_test_catalog(tmp_path: Path) -> Path:
    root = tmp_path / "pool-root"
    config_dir = root / "config"
    profile_dir = config_dir / "agents"
    resource_dir = root / "knowledge_pools/skills"
    profile_dir.mkdir(parents=True)
    resource_dir.mkdir(parents=True)
    for agent_id in ("alice", "kodex", "marshal"):
        (profile_dir / f"{agent_id}.profile.json").write_text(
            json.dumps({"agent_id": agent_id, "activation": "prepared_not_enabled"}),
            encoding="utf-8",
        )
    content_path = resource_dir / "curated-skill.md"
    content = "# Curated skill\n\nA short trusted-by-review example.\n"
    content_path.write_text(content, encoding="utf-8")
    item = {
        "id": "curated-skill",
        "kind": "skill",
        "title": "Curated skill",
        "summary": "A curated skill for tests.",
        "tags": ["curated", "skill"],
        "target_agents": ["alice"],
        "source_ids": ["test-source"],
        "resource_path": "knowledge_pools/skills/curated-skill.md",
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "version": 1,
        "approval": None,
        "status": "review_pending",
        "visibility": "review_only",
        "reviewers": ["kodex", "marshal"],
        "estimated_tokens": 20,
    }
    source_registry = {"schema_version": 1, "registry_id": "sources", "sources": []}
    source_path = config_dir / "knowledge_source_registry.json"
    source_path.write_text(_json_text(source_registry), encoding="utf-8")
    registries = []
    registry_specs = (
        ("skills", "skill_pool_registry.json", ["skill"], [item]),
        ("prompts", "prompt_pool_registry.json", ["prompt_index", "prompt_template"], []),
        ("references", "knowledge_reference_registry.json", ["reference"], []),
    )
    for registry_id, filename, kinds, registry_items in registry_specs:
        registry = {
            "schema_version": 1,
            "registry_id": registry_id,
            "allowed_kinds": kinds,
            "items": registry_items,
        }
        registry_path = config_dir / filename
        registry_path.write_text(_json_text(registry), encoding="utf-8")
        registries.append({
            "id": registry_id,
            "path": f"config/{filename}",
            "sha256": hashlib.sha256(registry_path.read_bytes()).hexdigest(),
            "allowed_kinds": kinds,
        })
    catalog = {
        "schema_version": 1,
        "policy": {},
        "source_registry": {
            "path": "config/knowledge_source_registry.json",
            "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        },
        "registries": registries,
    }
    (config_dir / "knowledge_pool_catalog.json").write_text(_json_text(catalog), encoding="utf-8")
    return root


def _load_test_skill_registry(root: Path) -> dict:
    path = root / "config/skill_pool_registry.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _persist_test_registry(root: Path, catalog: dict, registry: dict) -> None:
    path = root / "config/skill_pool_registry.json"
    path.write_text(_json_text(registry), encoding="utf-8")
    reference = next(ref for ref in catalog["registries"] if ref["id"] == "skills")
    reference["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    (root / "config/knowledge_pool_catalog.json").write_text(_json_text(catalog), encoding="utf-8")


def _json_text(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


class _FakeAuditStore:
    def add(self, _kind: str, _payload: dict) -> dict[str, str]:
        return {"id": "intent-1"}



def test_service_hub_requires_explicit_knowledge_grants(monkeypatch: pytest.MonkeyPatch) -> None:
    import src.integrations.service_hub as service_hub_module

    monkeypatch.setattr(service_hub_module, "DirectorStore", lambda _namespace: _FakeAuditStore())
    ServiceHub = service_hub_module.ServiceHub

    denied_hub = ServiceHub("kodex", {"grants": []})
    denied = asyncio.run(denied_hub.execute("knowledge.search", {"query": "prompt engineering"}))
    assert denied["status"] == "denied"

    granted_hub = ServiceHub(
        "kodex",
        {
            "grants": ["knowledge.search"],
            "knowledge_pool_access": {"review_agents": ["kodex"]},
        },
    )
    granted_hub.store = _FakeAuditStore()
    result = asyncio.run(granted_hub.execute("knowledge.search", {"query": "prompt engineering"}))
    assert result["status"] == "ok"
    assert result["value"]
    assert all("content" not in item for item in result["value"])
