"""
Unit tests for Architect ↔ Antigravity n8n Workflow Construction Bridge.
Validates FlowLint compliance, Zero-Trust security, and compilation.
"""

import pytest
from pathlib import Path
from src.integrations.architect_n8n_builder import (
    ArchitectN8nBuilder,
    WorkflowBlueprint,
    WorkflowNode,
)


def test_architect_n8n_builder_successful_compilation(tmp_path: Path):
    builder = ArchitectN8nBuilder(output_dir=tmp_path)

    nodes = [
        WorkflowNode(
            id="node-webhook",
            name="Telegram Webhook Trigger",
            type="n8n-nodes-base.webhook",
            parameters={"path": "syndicate-telegram", "httpMethod": "POST"},
            position=[100, 300],
        ),
        WorkflowNode(
            id="node-code",
            name="Cleanse and Route Payload",
            type="n8n-nodes-base.code",
            parameters={"mode": "runOnceForEachItem", "jsCode": "return { json: item.json };"},
            position=[350, 300],
        ),
    ]

    connections = {
        "Telegram Webhook Trigger": {
            "main": [[{"node": "Cleanse and Route Payload", "type": "main", "index": 0}]]
        }
    }

    blueprint = WorkflowBlueprint(
        id="wf-telegram-router-v1",
        name="Telegram Inbound Command Router",
        description="Routes incoming Commander commands to Eva and radial directors.",
        category="routing",
        target_agents=["eva", "architect", "antigravity"],
        nodes=nodes,
        connections=connections,
        active=False,
        tags=["telegram", "router", "flowlint"],
    )

    is_valid, errors = builder.validate_flowlint(blueprint)
    assert is_valid is True
    assert len(errors) == 0

    compiled = builder.compile_workflow(blueprint)
    assert compiled["active"] is False
    assert compiled["meta"]["designed_by"] == "architect"
    assert compiled["meta"]["built_by"] == "antigravity"
    assert len(compiled["nodes"]) == 2

    staged_file = builder.build_and_stage(blueprint)
    assert staged_file.is_file()
    assert staged_file.name == "wf-telegram-router-v1.n8n.json"


def test_architect_n8n_builder_rejects_active_and_secrets(tmp_path: Path):
    builder = ArchitectN8nBuilder(output_dir=tmp_path)

    # Violation 1: active=True without Commander approval
    # Violation 2: Hardcoded secret pattern in node parameters
    nodes = [
        WorkflowNode(
            id="node-bad",
            name="Leaked Secret Node",
            type="n8n-nodes-base.httpRequest",
            parameters={"url": "https://api.example.com", "header": "Bearer ghp_LeakedGitHubToken1234567890abcdef"},
        )
    ]

    blueprint = WorkflowBlueprint(
        id="wf-leaked-secret",
        name="Bad Workflow",
        description="Contains hardcoded secret",
        category="security-fail",
        target_agents=["architect"],
        nodes=nodes,
        connections={},
        active=True,
    )

    is_valid, errors = builder.validate_flowlint(blueprint)
    assert is_valid is False
    assert any("active=False" in e for e in errors)
    assert any("Hardcoded secret pattern" in e for e in errors)

    with pytest.raises(ValueError, match="FlowLint validation failed"):
        builder.compile_workflow(blueprint)
