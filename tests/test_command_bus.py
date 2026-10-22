"""
Unit tests for SYNDICATE Command Bus (Deterministic Zero-Token RPC).
"""

import pytest
from pathlib import Path
from src.agent_platform.command_bus import CommandBus, CommandRequest


def test_command_bus_validates_and_dispatches_notebooklm_request():
    bus = CommandBus()

    # Successful call from Jack to Antigravity
    req = CommandRequest(
        command="CMD:NOTEBOOKLM_PROCESS",
        caller="jack",
        payload={
            "notebook_id": "nb-test-123",
            "category": "sports_betting",
            "requested_by": "jack",
            "title": "Pinnacle Odds Analysis",
        },
    )

    is_valid, err = bus.validate_request(req)
    assert is_valid is True
    assert err is None

    # Handler mock
    called = {}
    def mock_handler(payload):
        called["payload"] = payload
        return {"status": "exported", "dossier": "01_Knowledge_Base/sports_betting/test.md"}

    handlers = {"CMD:NOTEBOOKLM_PROCESS": mock_handler}
    resp = bus.dispatch(req, handlers)

    assert resp.status == "ok"
    assert resp.target_agent == "antigravity"
    assert resp.result["status"] == "exported"
    assert called["payload"]["notebook_id"] == "nb-test-123"


def test_command_bus_rejects_unauthorized_caller():
    bus = CommandBus()

    # Unauthorized caller: e.g. unknown agent trying to build n8n
    req = CommandRequest(
        command="CMD:N8N_BUILD_WORKFLOW",
        caller="random_stranger",
        payload={"blueprint_id": "bp-1", "blueprint_data": {}},
    )

    is_valid, err = bus.validate_request(req)
    assert is_valid is False
    assert "not authorized" in err

    resp = bus.dispatch(req, {})
    assert resp.status == "error"
    assert "not authorized" in resp.error


def test_command_bus_rejects_missing_parameters():
    bus = CommandBus()

    # Missing required parameter 'requested_by'
    req = CommandRequest(
        command="CMD:NOTEBOOKLM_PROCESS",
        caller="sam",
        payload={"notebook_id": "nb-123", "category": "quant"},
    )

    is_valid, err = bus.validate_request(req)
    assert is_valid is False
    assert "Missing required parameter 'requested_by'" in err
