"""FlowLint — static analysis for n8n workflow JSON.

Enforces the Architect's ANTI-CRUTCH rules (ARCHITECT_N8N_SPEC.md §3):

  1. Core nodes only — no community / unverified node types.
  2. Error handling mandatory — every critical node reachable via an OnError
     path (or the workflow declares an ``errorWorkflow`` / error-trigger).
  3. No hardcoded secrets — API keys / passwords must come from n8n credentials
     or the Vault bridge, never inline in node parameters.
  4. Idempotency — workflows triggered by a webhook must contain a
     deduplication guard (e.g. a Redis/Function dedup node keyed on body hash).

The linter is dependency-free (pure stdlib) so it can run anywhere, including
inside CI before a workflow is committed to ``/n8n_workflows/``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


# Node types considered part of the official n8n core set (prefixes). Anything
# not matching these is flagged as a potential community/unverified node.
CORE_NODE_PREFIXES = (
    "n8n-nodes-base.",
    "@n8n/n8n-nodes-langchain.",
)

# Trigger nodes start a workflow; they never need an OnError branch themselves
# (their failures are surfaced via the global error workflow / Error Trigger).
TRIGGER_NODE_HINTS = ("trigger", "webhook", "cron", "interval")

# Node types that make outbound calls / mutations and therefore MUST be
# protected by error handling.
CRITICAL_NODE_HINTS = (
    "httpRequest", "postgres", "mySql", "redis", "emailSend",
    "telegram", "executeCommand", "ftp", "ssh", "awsS3", "googleSheets",
    "noOp",  # allow noOp but not counted as risky; kept for completeness
)
RISKY_NODES = tuple(h for h in CRITICAL_NODE_HINTS if h != "noOp")


def _is_trigger(node_type: str) -> bool:
    low = node_type.lower()
    return any(h in low for h in TRIGGER_NODE_HINTS)

# Heuristic patterns that look like inlined secrets.
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|password|token|bearer)\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"xoxb-[A-Za-z0-9-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
]

# Node types / expressions that indicate an idempotency / dedup guard.
DEDUP_HINTS = ("dedup", "idempoten", "removeduplicate", "redis", "setnx", "cache")

SEVERITY_ORDER = {"error": 3, "warning": 2, "info": 1}


@dataclass
class LintIssue:
    severity: str      # error | warning | info
    rule: str
    message: str
    node: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"severity": self.severity, "rule": self.rule, "message": self.message, "node": self.node}


@dataclass
class LintReport:
    passed: bool
    issues: List[LintIssue] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "error_count": len(self.errors()),
            "issue_count": len(self.issues),
            "issues": [i.to_dict() for i in self.issues],
            "stats": self.stats,
        }


def _iter_nodes(workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
    nodes = workflow.get("nodes")
    return nodes if isinstance(nodes, list) else []


def _node_type(node: Dict[str, Any]) -> str:
    return str(node.get("type", ""))


def _is_core(node_type: str) -> bool:
    return node_type.startswith(CORE_NODE_PREFIXES)


def _short_type(node_type: str) -> str:
    return node_type.rsplit(".", 1)[-1]


def _has_error_coverage(workflow: Dict[str, Any], node_name: str) -> bool:
    """A node is covered if it has continueOnFail, an onError setting, or an
    outgoing connection on the ``error`` output, or the workflow declares a
    global error workflow / contains an Error Trigger node."""
    connections = workflow.get("connections", {})
    node_conns = connections.get(node_name, {})
    if isinstance(node_conns, dict) and node_conns.get("error"):
        return True
    return False


def lint_workflow(workflow: Dict[str, Any]) -> LintReport:
    """Run all FlowLint rules over a parsed n8n workflow dict."""
    issues: List[LintIssue] = []
    nodes = _iter_nodes(workflow)

    if not nodes:
        issues.append(LintIssue("error", "structure", "Workflow contains no nodes"))
        return LintReport(passed=False, issues=issues, stats={"nodes": 0})

    node_types = [_node_type(n) for n in nodes]
    has_error_trigger = any("errorTrigger" in t.lower() for t in node_types)
    has_error_workflow = bool(
        (workflow.get("settings") or {}).get("errorWorkflow")
    )
    has_webhook_trigger = any("webhook" in t.lower() for t in node_types)

    # Rule 1 — core nodes only.
    for n in nodes:
        t = _node_type(n)
        if t and not _is_core(t):
            issues.append(
                LintIssue(
                    "error", "core-nodes-only",
                    f"Non-core / community node '{t}' is forbidden "
                    "(N8N_COMMUNITY_PACKAGES_ENABLED=false)",
                    node=n.get("name"),
                )
            )

    # Rule 2 — error handling on critical nodes (trigger nodes are exempt).
    for n in nodes:
        if _is_trigger(_node_type(n)):
            continue
        short = _short_type(_node_type(n))
        if any(short.startswith(r) or r in short for r in RISKY_NODES):
            covered = (
                _has_error_coverage(workflow, n.get("name", ""))
                or bool(n.get("continueOnFail"))
                or bool(n.get("onError"))
                or has_error_trigger
                or has_error_workflow
            )
            if not covered:
                issues.append(
                    LintIssue(
                        "error", "error-handling",
                        f"Critical node '{n.get('name')}' ({short}) has no OnError "
                        "branch, continueOnFail, or global error workflow",
                        node=n.get("name"),
                    )
                )

    # Rule 3 — no hardcoded secrets.
    import json as _json

    for n in nodes:
        params_blob = _json.dumps(n.get("parameters", {}), ensure_ascii=False)
        for pat in SECRET_PATTERNS:
            if pat.search(params_blob):
                issues.append(
                    LintIssue(
                        "error", "no-hardcoded-secrets",
                        f"Node '{n.get('name')}' appears to contain an inline secret; "
                        "use n8n credentials or the Vault bridge instead",
                        node=n.get("name"),
                    )
                )
                break

    # Rule 4 — idempotency for webhook-triggered workflows.
    if has_webhook_trigger:
        blob = _json.dumps(workflow, ensure_ascii=False).lower()
        if not any(h in blob for h in DEDUP_HINTS):
            issues.append(
                LintIssue(
                    "warning", "idempotency",
                    "Webhook-triggered workflow has no visible deduplication / "
                    "idempotency guard (Redis SETNX or body-hash dedup recommended)",
                )
            )

    # Info — naming hygiene.
    unnamed = [i for i, n in enumerate(nodes) if not n.get("name")]
    if unnamed:
        issues.append(
            LintIssue("warning", "naming", f"{len(unnamed)} node(s) have no name")
        )

    passed = not any(i.severity == "error" for i in issues)
    stats = {
        "nodes": len(nodes),
        "core_nodes": sum(1 for t in node_types if _is_core(t)),
        "has_error_trigger": has_error_trigger,
        "has_error_workflow": has_error_workflow,
        "webhook_triggered": has_webhook_trigger,
    }
    return LintReport(passed=passed, issues=issues, stats=stats)
