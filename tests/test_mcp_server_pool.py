"""MCP catalog is a default-deny, read-only metadata pool—not a runtime connector."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from src.agent_platform.mcp_server_pool import MCPServerPool, MCPServerPoolError

ROOT = Path(__file__).resolve().parents[1]


def test_pinned_catalog_is_discovery_only_and_candidate_is_not_enabled() -> None:
    pool = MCPServerPool(reader_agents=["kodex", "architect", "marshal"])
    assert len(pool.records) == 18_789
    assert pool.manifest["source_catalog"]["category_count"] == 70

    results = pool.search("kodex", "mcp-server-time", limit=5)
    candidate = next(result for result in results if result["source_type"] == "curated_candidate")
    assert candidate["id"] == "candidate:mcp-server-time-2026-10-10"
    assert candidate["status"] == "review_pending"
    assert "description" not in candidate
    assert "mcp.call" not in candidate

    item = pool.read("marshal", candidate["id"])
    assert item["status"] == "review_pending"
    assert item["runtime_enabled"] is False
    assert item["grants_applied"] is False
    assert item["review"]["independent_marshal_review"] == "not_recorded"
    assert {tool["name"] for tool in item["tools"]} == {"get_current_time", "convert_time"}

    raw_result = next(result for result in pool.search("architect", "inth3shadows terse", limit=5)
                      if result["source_type"] == "untrusted_catalog")
    assert raw_result["status"] == "discovered_only"
    assert "description" not in raw_result
    raw_item = pool.read("architect", raw_result["id"])
    assert raw_item["description_is_untrusted"] is True
    assert raw_item["catalog_license"] == "unknown_not_present_in_source_record"
    assert "install" in raw_item["description"].lower()
    assert raw_item["runtime_enabled"] is False


def test_pool_is_default_deny_and_bounds_inputs() -> None:
    pool = MCPServerPool()
    with pytest.raises(MCPServerPoolError, match="pool_access_denied"):
        pool.search("kodex", "time")
    with pytest.raises(MCPServerPoolError, match="pool_access_denied"):
        pool.read("kodex", "catalog:00001")

    allowed = MCPServerPool(reader_agents=["kodex"])
    with pytest.raises(MCPServerPoolError, match="invalid_query"):
        allowed.search("kodex", " " * 4)
    with pytest.raises(MCPServerPoolError, match="invalid_limit"):
        allowed.search("kodex", "time", limit=6)
    with pytest.raises(MCPServerPoolError, match="invalid_limit"):
        allowed.search("kodex", "time", limit=True)
    with pytest.raises(MCPServerPoolError, match="invalid_item_id"):
        allowed.read("kodex", "../mcp_servers_registry.json")
    with pytest.raises(MCPServerPoolError, match="item_unavailable"):
        allowed.read("kodex", "catalog:99999")


def test_description_redacts_secret_shaped_literals_and_bearer_tokens() -> None:
    text = "Use API_KEY=" + "FAKE_TEST_ONLY_NOT_SECRET_123456 or Bearer " + "FAKE_BEARER_NOT_SECRET_1234567890"
    redacted, changed = MCPServerPool._redact_sensitive_text(text)
    assert changed is True
    assert "FAKE_TEST_ONLY_NOT_SECRET_123456" not in redacted
    assert "FAKE_BEARER_NOT_SECRET_1234567890" not in redacted
    assert "[REDACTED]" in redacted


def test_raw_read_omits_url_query_and_returns_bounded_untrusted_text(tmp_path: Path) -> None:
    root = _write_test_pool(tmp_path)
    pool = MCPServerPool(root=root, reader_agents=["kodex"])
    item = pool.read("kodex", "catalog:00001")
    assert item["url"] == "https://example.invalid/mcp"
    assert item["url_query_or_fragment_omitted"] is True
    assert "QUERY_FIXTURE_NOT_SECRET_123456" not in json.dumps(item)
    assert item["description_is_untrusted"] is True
    assert "install" in item["risk_flags"][0]


def test_source_digest_mismatch_and_symlinks_fail_closed(tmp_path: Path) -> None:
    root = _write_test_pool(tmp_path)
    catalog_path = root / "mcp_servers/mcp_servers_registry.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog["servers"][0]["name"] = "tampered"
    catalog_path.write_text(_json_text(catalog), encoding="utf-8")
    with pytest.raises(MCPServerPoolError, match="catalog_integrity_failed"):
        MCPServerPool(root=root, reader_agents=["kodex"])

    root = _write_test_pool(tmp_path / "symlink-test")
    catalog_path = root / "mcp_servers/mcp_servers_registry.json"
    outside = tmp_path / "outside.json"
    outside.write_text(catalog_path.read_text(encoding="utf-8"), encoding="utf-8")
    catalog_path.unlink()
    catalog_path.symlink_to(outside)
    with pytest.raises(MCPServerPoolError, match="pool_unavailable"):
        MCPServerPool(root=root, reader_agents=["kodex"])


def test_pool_grant_proposals_remain_separate_from_runtime_and_host_config() -> None:
    plan = json.loads((ROOT / "config/mcp_pool_grants.json").read_text(encoding="utf-8"))
    example = json.loads((ROOT / "config/integration_worker.example.json").read_text(encoding="utf-8"))
    assert plan["status"] == "proposed_not_applied"
    assert plan["default"] == {"service_hub_operations": [], "reader_agents": []}
    assert plan["vault_policy"] == "not_created_or_applied"
    assert plan["deployment_templates"]["status"] == "prepared_not_applied"
    assert example["mcp_pool_access"] == {"reader_agents": []}
    assert example["knowledge_pool_access"] == {"review_agents": [], "shared_agents": []}
    assert not {"knowledge.search", "knowledge.read", "mcp.pool.search", "mcp.pool.read"} & set(example["grants"])

    proposals = {item["agent_id"]: item for item in plan["proposals"]}
    assert set(proposals) == {"kodex", "architect", "marshal"}
    expected_worker_grants = {
        "kodex": ["skills.list", "skills.read", "knowledge.search", "knowledge.read", "mcp.pool.search", "mcp.pool.read"],
        "architect": ["skills.list", "skills.read", "mcp.pool.search", "mcp.pool.read"],
        "marshal": ["skills.list", "skills.read", "knowledge.search", "knowledge.read", "mcp.pool.search", "mcp.pool.read"],
    }
    for agent_id, proposal in proposals.items():
        profile = json.loads((ROOT / f"config/agents/{agent_id}.profile.json").read_text(encoding="utf-8"))
        template = json.loads((ROOT / f"config/integration_workers/{agent_id}.example.json").read_text(encoding="utf-8"))
        assert profile["activation"] == "prepared_not_enabled"
        assert plan["status"] == "proposed_not_applied"
        assert proposal["service_hub_operations"] == ["mcp.pool.search", "mcp.pool.read"]
        assert proposal["reader_agents"] == [agent_id]
        assert template["grants"] == expected_worker_grants[agent_id]
        assert template["mcp_pool_access"]["reader_agents"] == [agent_id]
        assert template["mcp"] == {}
        assert not {"mcp.list", "mcp.call"} & set(template["grants"])
        if agent_id in {"kodex", "marshal"}:
            assert template["knowledge_pool_access"] == {"review_agents": [agent_id], "shared_agents": []}
        else:
            assert "knowledge_pool_access" not in template
        assert "mcp.pool.search" not in profile["capabilities"]
        assert "mcp.pool.read" not in profile["capabilities"]
        profile_proposals = {
            grant["capability"]: grant
            for grant in profile.get("proposed_grants", [])
            if grant.get("capability") in {"mcp.pool.search", "mcp.pool.read"}
        }
        assert set(profile_proposals) == {"mcp.pool.search", "mcp.pool.read"}
        assert all(grant["status"] == "proposed_not_applied" for grant in profile_proposals.values())


def test_service_hub_requires_operation_grant_and_host_reader_allowlist(tmp_path: Path, monkeypatch) -> None:
    from src.integrations.service_hub import ServiceHub

    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))

    async def exercise() -> None:
        denied = ServiceHub("kodex", {"grants": []})
        assert (await denied.execute("mcp.pool.search", {"query": "time"}))["status"] == "denied"

        no_reader = ServiceHub("kodex", {"grants": ["mcp.pool.search"]})
        assert (await no_reader.execute("mcp.pool.search", {"query": "time"}))["status"] == "unavailable"

        allowed = ServiceHub(
            "kodex",
            {
                "grants": ["mcp.pool.search", "mcp.pool.read"],
                "mcp_pool_access": {"reader_agents": ["kodex"]},
            },
        )
        result = await allowed.execute("mcp.pool.search", {"query": "mcp-server-time", "limit": 2})
        assert result["status"] == "ok"
        item_id = next(value["id"] for value in result["value"] if value["source_type"] == "curated_candidate")
        item = await allowed.execute("mcp.pool.read", {"item_id": item_id})
        assert item["status"] == "ok"
        assert item["value"]["runtime_enabled"] is False
        assert item["value"]["grants_applied"] is False

        only_search = ServiceHub(
            "kodex",
            {"grants": ["mcp.pool.search"], "mcp_pool_access": {"reader_agents": ["kodex"]}},
        )
        assert (await only_search.execute("mcp.pool.read", {"item_id": item_id}))["status"] == "denied"

    import asyncio

    asyncio.run(exercise())


def _write_test_pool(tmp_path: Path) -> Path:
    root = tmp_path / "pool-root"
    catalog_dir = root / "mcp_servers"
    pool_dir = catalog_dir / "pool"
    pool_dir.mkdir(parents=True)
    catalog = {
        "version": "2.0.0",
        "total_servers": 1,
        "servers": [
            {
                "name": "example-server",
                "url": "https://example.invalid/mcp?fixture=QUERY_FIXTURE_NOT_SECRET_123456",
                "category": "Testing",
                "description": "Install with npx example-server",
            }
        ],
    }
    catalog_bytes = _json_text(catalog).encode("utf-8")
    (catalog_dir / "mcp_servers_registry.json").write_bytes(catalog_bytes)
    manifest = {
        "schema_version": 1,
        "pool_id": "mcp_server_pool",
        "status": "prepared_not_enabled",
        "policy": {
            "default_reader_allowlist": [],
            "only_read_only_pool_operations": ["mcp.pool.search", "mcp.pool.read"],
            "catalog_records_never_create_runtime_servers": True,
            "catalog_records_never_create_agent_grants": True,
            "no_install_or_launch_from_catalog": True,
        },
        "source_catalog": {
            "path": "mcp_servers/mcp_servers_registry.json",
            "sha256": hashlib.sha256(catalog_bytes).hexdigest(),
            "record_count": 1,
        },
        "items": [],
    }
    (pool_dir / "registry.json").write_text(_json_text(manifest), encoding="utf-8")
    return root


def _json_text(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"
