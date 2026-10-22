"""
Architect ↔ Antigravity (Alice) n8n Workflow Construction Bridge.

Implements the collaborative tandem:
- Architect (CTO / Planner): Designs workflow topology, node contracts, and FlowLint validation.
- Antigravity / Alice (Chief Technical Builder): Compiles, builds, validates, and stages the execution.
- Commander Andrii (HITL): Final review and authorization gate.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class WorkflowNode:
    """A single node specification in an n8n workflow."""
    id: str
    name: str
    type: str  # e.g. 'n8n-nodes-base.webhook', 'n8n-nodes-base.code', 'n8n-nodes-base.httpRequest'
    type_version: int = 1
    position: List[int] = field(default_factory=lambda: [250, 300])
    parameters: Dict[str, Any] = field(default_factory=dict)
    credentials: Optional[Dict[str, Any]] = None


@dataclass
class WorkflowBlueprint:
    """Blueprint planned by Architect and built by Antigravity."""
    id: str
    name: str
    description: str
    category: str
    target_agents: List[str]
    nodes: List[WorkflowNode]
    connections: Dict[str, Any]
    active: bool = False  # Default-inactive per Zero-Trust policy
    tags: List[str] = field(default_factory=list)


class ArchitectN8nBuilder:
    """Tandem bridge between Architect (System Design) and Alice (Builder Engine)."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = output_dir or Path(r"C:\Users\Admin\.gemini\antigravity\scratch\antigravity_workspace\apps\n8n_workflows")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def validate_flowlint(self, blueprint: WorkflowBlueprint) -> tuple[bool, List[str]]:
        """Validate workflow against FlowLint & Zero-Trust security rules."""
        errors: List[str] = []

        if not re.fullmatch(r"[a-z0-9_-]+", blueprint.id):
            errors.append(f"Invalid workflow ID format: '{blueprint.id}'")

        if blueprint.active is True:
            errors.append("Violation: New workflows must have active=False until Commander approval.")

        # Check for exposed secrets or hardcoded tokens in parameters
        secret_patterns = [
            r"sk-[a-zA-Z0-9]{20,}",
            r"ghp_[a-zA-Z0-9]{20,}",
            r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}",
            r"password\s*[:=]\s*['\"][^'\"]+['\"]",
        ]
        blueprint_json = json.dumps([n.parameters for n in blueprint.nodes])
        for pat in secret_patterns:
            if re.search(pat, blueprint_json, re.IGNORECASE):
                errors.append(f"FlowLint Security: Hardcoded secret pattern detected in node parameters ({pat})")

        # Validate nodes count and essential handlers
        if not blueprint.nodes:
            errors.append("Workflow must contain at least one node.")

        has_trigger = any("webhook" in n.type.lower() or "cron" in n.type.lower() or "trigger" in n.type.lower() for n in blueprint.nodes)
        if not has_trigger and len(blueprint.nodes) > 1:
            errors.append("FlowLint Warning: No explicit trigger node (webhook/cron) defined.")

        is_valid = len(errors) == 0
        return is_valid, errors

    def compile_workflow(self, blueprint: WorkflowBlueprint) -> Dict[str, Any]:
        """Compile the verified blueprint into official n8n workflow format."""
        is_valid, errors = self.validate_flowlint(blueprint)
        if not is_valid:
            raise ValueError(f"FlowLint validation failed: {'; '.join(errors)}")

        n8n_nodes = []
        for node in blueprint.nodes:
            node_dict: Dict[str, Any] = {
                "id": node.id,
                "name": node.name,
                "type": node.type,
                "typeVersion": node.type_version,
                "position": node.position,
                "parameters": node.parameters,
            }
            if node.credentials:
                node_dict["credentials"] = node.credentials
            n8n_nodes.append(node_dict)

        compiled = {
            "name": f"SYNDICATE — {blueprint.name}",
            "nodes": n8n_nodes,
            "connections": blueprint.connections,
            "active": False,
            "settings": {
                "executionOrder": "v1",
                "saveManualExecutions": True,
                "callerPolicy": "workflowsFromSameOwner",
            },
            "meta": {
                "templateCredsSetupCompleted": True,
                "syndicate_blueprint_id": blueprint.id,
                "designed_by": "architect",
                "built_by": "antigravity",
                "target_agents": blueprint.target_agents,
                "category": blueprint.category,
                "tags": blueprint.tags,
            },
        }

        logger.info(
            "n8n_workflow_compiled",
            blueprint_id=blueprint.id,
            nodes_count=len(blueprint.nodes),
            target_agents=blueprint.target_agents,
        )
        return compiled

    def build_and_stage(self, blueprint: WorkflowBlueprint) -> Path:
        """Physical build and staging of the n8n workflow JSON by Antigravity."""
        compiled = self.compile_workflow(blueprint)
        file_path = self.output_dir / f"{blueprint.id}.n8n.json"
        file_path.write_text(json.dumps(compiled, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        logger.info("n8n_workflow_staged", path=str(file_path))
        return file_path
