"""Optional compatibility smoke test for the isolated Antigravity SDK image.

The core application does not install this SDK. Run this file in the Alice
requirements environment to validate its construction surface without a network
call or real provider credentials.
"""

from __future__ import annotations

import asyncio

import pytest

pytest.importorskip("google.antigravity")

from src.agents.alice import AliceAgent  # noqa: E402


def test_sdk_adapter_builds_direct_gemini_config_without_network(tmp_path, monkeypatch):
    from google import antigravity

    captured = {}

    class FakeResponse:
        async def text(self):
            return "synthetic response"

    class FakeAgent:
        def __init__(self, config):
            captured["config"] = config

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def chat(self, prompt):
            captured["prompt"] = prompt
            return FakeResponse()

    monkeypatch.setattr(antigravity, "Agent", FakeAgent)
    workspace = tmp_path / "alice-workspace"
    workspace.mkdir()
    agent = AliceAgent(api_key="synthetic-never-used", model="gemini-2.5-flash")

    result = asyncio.run(
        agent._invoke_antigravity_sdk(
            action="review",
            prompt="Review a synthetic test fixture.",
            workspace=workspace,
        )
    )

    assert result["text"] == "synthetic response"
    config = captured["config"]
    assert config.vertex is False
    assert config.workspaces == [str(workspace)]
    assert config.capabilities.enable_subagents is False
    workspace_policy_tools = {
        item.tool for item in config.policies if item.name == "workspace_only"
    }
    assert workspace_policy_tools == {"view_file", "create_file", "edit_file"}
    assert {tool.value for tool in config.capabilities.enabled_tools} == {
        "list_directory",
        "find_file",
        "search_directory",
        "view_file",
    }
    assert config.budget_config.max_model_calls == 3
    assert config.budget_config.max_tool_calls == 8
    assert "synthetic response" not in captured["prompt"]
