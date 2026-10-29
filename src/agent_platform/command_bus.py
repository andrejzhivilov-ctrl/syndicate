"""
SYNDICATE Deterministic Command Bus (Zero-Token RPC).

Allows agents (Jack, Sam, Doc, Trainer, Kira, etc.) to trigger pre-wired operations
(NotebookLM synthesis, n8n build, task transitions, doc generation) without spending
hundreds of conversational LLM tokens on natural language negotiation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)

HUB_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "syndicate_command_hub.json"


@dataclass
class CommandRequest:
    command: str
    caller: str
    payload: Dict[str, Any]


@dataclass
class CommandResponse:
    status: str  # "ok" | "error"
    command: str
    target_agent: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CommandBus:
    """Zero-LLM command registry and dispatcher for inter-agent operations."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        path = config_path or HUB_CONFIG_PATH
        if not path.is_file():
            raise FileNotFoundError(f"Command hub config missing: {path}")
        self.catalog = json.loads(path.read_text(encoding="utf-8"))
        self.commands: Dict[str, Dict[str, Any]] = {
            c["command"]: c for c in self.catalog.get("commands", [])
        }

    def validate_request(self, req: CommandRequest) -> tuple[bool, Optional[str]]:
        """Validate caller permissions and required parameters deterministically."""
        spec = self.commands.get(req.command)
        if not spec:
            return False, f"Unknown command: '{req.command}'"

        if req.caller not in spec["allowed_callers"] and req.caller != "andrii":
            return False, f"Agent '{req.caller}' is not authorized to invoke '{req.command}'"

        for p in spec["required_params"]:
            if p not in req.payload:
                return False, f"Missing required parameter '{p}' for command '{req.command}'"

        return True, None

    def dispatch(self, req: CommandRequest, handlers: Dict[str, Any]) -> CommandResponse:
        """Route request directly to registered agent handler."""
        is_valid, err = self.validate_request(req)
        if not is_valid:
            logger.warning("command_bus_validation_failed", command=req.command, caller=req.caller, error=err)
            return CommandResponse(
                status="error",
                command=req.command,
                target_agent=self.commands.get(req.command, {}).get("target_agent", "unknown"),
                error=err,
            )

        spec = self.commands[req.command]
        target = spec["target_agent"]
        handler = handlers.get(req.command) or handlers.get(target)

        if not handler:
            logger.error("command_handler_missing", command=req.command, target=target)
            return CommandResponse(
                status="error",
                command=req.command,
                target_agent=target,
                error=f"No execution handler registered for '{req.command}'",
            )

        try:
            result = handler(req.payload)
            logger.info("command_executed_successfully", command=req.command, caller=req.caller, target=target)
            return CommandResponse(
                status="ok",
                command=req.command,
                target_agent=target,
                result=result,
            )
        except Exception as ex:
            logger.exception("command_execution_error", command=req.command, caller=req.caller, error=str(ex))
            return CommandResponse(
                status="error",
                command=req.command,
                target_agent=target,
                error=str(ex),
            )
