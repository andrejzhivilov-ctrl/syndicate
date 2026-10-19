import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_time_mcp_server_is_pinned_and_example_allowlist_is_read_only():
    requirements = (ROOT / "deploy/requirements-integrations.txt").read_text().splitlines()
    assert "mcp-server-time==2026.10.10" in requirements

    examples = json.loads((ROOT / "config/integration_mcp.example.json").read_text())
    server = examples["mcp-time"]
    assert server["command"] == "/usr/local/bin/python"
    assert server["args"] == [
        "-m",
        "mcp_server_time",
        "--local-timezone=Europe/Kyiv",
    ]
    assert server["tools"] == ["get_current_time", "convert_time"]
    assert server["env"] == {"HOME": "/tmp"}
    assert not any("key" in key.lower() or "token" in key.lower() for key in server["env"])


def test_tyler_store_review_is_assigned_as_reference_without_activation():
    profile = json.loads((ROOT / "config/agents/tyler.profile.json").read_text())
    assert profile["activation"] == "prepared_not_enabled"
    assert "tyler-store-legitimacy-review" in profile["reference_skills"]
    assert profile["capabilities"] == []
    assert profile["grants"] == []
    assert profile["services_enabled"] == []

    from src.agent_platform.skill_library import SkillLibrary

    library = SkillLibrary(ROOT)
    result = library.read("tyler", "tyler-store-legitimacy-review")
    assert result["mode"] == "reference_only"
    assert result["commit"] == "2fb9337c53bd164c2c8d6bad04894ea3d6846e18"
    assert "Не перенось правила ЄС, Данії" in result["content"]
    assert "не гарантія" in result["content"]

    with pytest.raises(ValueError, match="unknown_skill_resource"):
        library.read("tyler", "tyler-store-legitimacy-review", "UPSTREAM_SKILL.md")
