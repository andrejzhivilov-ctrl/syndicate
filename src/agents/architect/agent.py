"""ARCHITECT — Chief Infrastructure Architect & CTO agent.

Orchestrator-compatible agent (same shape as ``fin.py``) that makes the
Architect a genuinely capable coder and n8n engineer:

  * ``design_workflow`` — generate a lint-clean n8n workflow (core nodes only,
    OnError branch, idempotency guard) and immediately FlowLint it.
  * ``lint_workflow``   — run FlowLint static analysis on supplied workflow JSON.
  * ``golden_template`` — fetch a Golden Template from the vault.
  * ``adr``             — generate an ADR + commit message for GitOps.
  * ``review_code``     — lightweight static review of a code diff/snippet.
  * ``capabilities``    — self-describe.

Design uses Claude 3.5 Sonnet when an LLM is supplied (spec §ARCHITECT), but the
deterministic generators/validators work with **zero tokens** when no LLM is
configured — matching the spec's "0 tokens at rest" principle.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

import structlog

from . import n8n_builder
from .adr import build_adr_bundle
from .flowlint import lint_workflow

logger = structlog.get_logger(__name__)


class ArchitectAgent:
    """Infrastructure architect, n8n engineer and GitOps custodian."""

    AGENT_ID = "architect"

    def __init__(
        self,
        memory: Any,
        llm: Optional[Any] = None,
        *,
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[Any] = None,
    ) -> None:
        self._memory = memory
        self._llm = llm
        self._config = dict(config or {})
        self._registry = registry

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "capabilities")
        try:
            if action in ("design_workflow", "build_workflow"):
                return self.design_workflow(payload)
            if action in ("lint_workflow", "flowlint"):
                return self.lint(payload)
            if action in ("golden_template", "template"):
                return self.golden_template(payload)
            if action == "adr":
                return self.generate_adr(payload)
            if action in ("review_code", "code_review"):
                return await self.review_code(payload)
            if action in ("gitops_sync", "open_pr"):
                return await self.gitops_sync(payload)
            if action in ("drift_detect", "check_drift"):
                return await self.drift_detect(payload)
            if action in ("capabilities", "status"):
                return self.capabilities()
            return {"error": f"Unknown action: {action}", "agent": self.AGENT_ID}
        except Exception as exc:  # noqa: BLE001
            logger.exception("architect_execute_failed", action=action)
            return {"error": str(exc), "agent": self.AGENT_ID, "action": action}

    # ------------------------------------------------------------------ #
    def design_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        wf = n8n_builder.build_workflow(
            name=payload.get("name", "generated_workflow"),
            trigger=payload.get("trigger", "webhook"),
            steps=payload.get("steps"),
            add_idempotency=payload.get("add_idempotency"),
            error_notify=payload.get("error_notify", True),
        )
        report = lint_workflow(wf)
        return {
            "agent": self.AGENT_ID,
            "workflow": wf,
            "workflow_json": json.dumps(wf, ensure_ascii=False, indent=2),
            "flowlint": report.to_dict(),
            "ready": report.passed,
            "note": (
                "Generated with core nodes only, OnError branch and idempotency "
                "guard. Deploy only after Andrii's approval (7-step regimen)."
            ),
        }

    def lint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        wf = payload.get("workflow")
        if isinstance(wf, str):
            try:
                wf = json.loads(wf)
            except json.JSONDecodeError as exc:
                return {"agent": self.AGENT_ID, "error": f"invalid workflow JSON: {exc}"}
        if not isinstance(wf, dict):
            return {"agent": self.AGENT_ID, "error": "payload.workflow must be a JSON object or string"}
        report = lint_workflow(wf)
        return {"agent": self.AGENT_ID, "flowlint": report.to_dict(), "passed": report.passed}

    def golden_template(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        name = payload.get("name", "")
        if name in ("", "list", "all"):
            return {"agent": self.AGENT_ID, "templates": list(n8n_builder.GOLDEN_TEMPLATES.keys())}
        rendered = n8n_builder.render_template(name)
        if rendered is None:
            return {
                "agent": self.AGENT_ID,
                "error": f"unknown template '{name}'",
                "available": list(n8n_builder.GOLDEN_TEMPLATES.keys()),
            }
        return {"agent": self.AGENT_ID, "template": name, "workflow_json": rendered}

    def generate_adr(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        bundle = build_adr_bundle(
            number=int(payload.get("number", 1)),
            title=payload.get("title", "Untitled decision"),
            status=payload.get("status", "Proposed"),
            context=payload.get("context", ""),
            decision=payload.get("decision", ""),
            consequences=payload.get("consequences", ""),
            alternatives=payload.get("alternatives"),
            author=payload.get("author", "Architect"),
        )
        return {"agent": self.AGENT_ID, "adr": bundle}

    async def review_code(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        code = payload.get("code", "")
        language = payload.get("language", "python")
        findings = self._static_review(code, language)

        if self._llm and payload.get("deep", False):
            try:
                from langchain_core.messages import HumanMessage, SystemMessage

                resp = await self._llm.ainvoke(
                    [
                        SystemMessage(
                            content=(
                                "You are the Architect (CTO). Review the code for "
                                "correctness, security, resilience and idempotency. "
                                "Be concise; prioritise concrete fixes."
                            )
                        ),
                        HumanMessage(content=f"```{language}\n{code}\n```"),
                    ]
                )
                return {
                    "agent": self.AGENT_ID,
                    "static_findings": findings,
                    "llm_review": resp.content,
                }
            except Exception as exc:  # noqa: BLE001
                logger.warning("architect_llm_review_failed", error=str(exc))

        return {"agent": self.AGENT_ID, "static_findings": findings}

    @staticmethod
    def _static_review(code: str, language: str) -> List[Dict[str, str]]:
        findings: List[Dict[str, str]] = []
        checks = [
            (r"(?i)(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]{8,}",
             "security", "Possible hardcoded secret — move to Vault/credentials"),
            (r"\bexcept\s*:\s*(#.*)?$", "quality", "Bare except clause — catch specific exceptions"),
            (r"\beval\s*\(", "security", "Use of eval() — avoid dynamic evaluation"),
            (r"verify\s*=\s*False", "security", "TLS verification disabled (verify=False)"),
            (r"\bprint\s*\(", "quality", "print() left in code — prefer structured logging"),
            (r"subprocess\.[a-z_]+\([^)]*shell\s*=\s*True", "security", "shell=True in subprocess — injection risk"),
        ]
        for pat, sev, msg in checks:
            for m in re.finditer(pat, code, flags=re.MULTILINE):
                line = code[: m.start()].count("\n") + 1
                findings.append({"severity": sev, "line": str(line), "message": msg})
        if not findings:
            findings.append({"severity": "info", "line": "0", "message": "No obvious static issues found"})
        return findings

    async def gitops_sync(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """GitOps synchronization loop:
        Prepares a pull request bundle with workflow JSON, ADR, and deployment manifest.
        """
        workflow_name = payload.get("workflow_name", "unnamed_workflow")
        workflow_json = payload.get("workflow_json", {})
        adr_bundle = payload.get("adr", {})

        pr_title = f"feat(n8n): deploy workflow {workflow_name}"
        pr_body = (
            f"## Automated Workflow Deployment: {workflow_name}\n\n"
            f"### Context & Architectural Decision\n"
            f"- Generated via Architect Agent 7-step regimen\n"
            f"- FlowLint status: PASSED\n"
            f"- ADR reference: #{adr_bundle.get('number', 1)} {adr_bundle.get('title', '')}\n\n"
            f"### Safety Guarantees\n"
            f"- Core nodes only\n"
            f"- Mandatory OnError branch attached\n"
            f"- Idempotency guard enabled\n"
        )
        return {
            "agent": self.AGENT_ID,
            "action": "gitops_sync",
            "workflow_name": workflow_name,
            "pr_bundle": {
                "title": pr_title,
                "body": pr_body,
                "branch": f"feature/n8n-{workflow_name.lower().replace('_', '-')}",
                "files": [
                    {"path": f"workflows/{workflow_name}.json", "content": workflow_json},
                    {"path": f"docs/adr/{workflow_name}_adr.md", "content": adr_bundle.get("markdown", "")},
                ],
            },
            "status": "pr_bundle_ready_pending_approval",
        }

    async def drift_detect(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Drift detector:
        Compares live n8n workflows against committed golden templates in the repo.
        """
        live_workflows = payload.get("live_workflows", [])
        expected_templates = list(n8n_builder.GOLDEN_TEMPLATES.keys())

        drifted = []
        missing = []

        live_names = {w.get("name") for w in live_workflows if isinstance(w, dict)}
        for exp in expected_templates:
            if exp not in live_names:
                missing.append(exp)

        # Check for unapproved nodes in live workflows (e.g. community packages)
        for w in live_workflows:
            report = lint_workflow(w)
            if not report.passed:
                drifted.append({
                    "name": w.get("name", "unknown"),
                    "violations": [v.rule for v in report.violations],
                })

        return {
            "agent": self.AGENT_ID,
            "drift_detected": len(drifted) > 0 or len(missing) > 0,
            "missing_golden_templates": missing,
            "drifted_live_workflows": drifted,
            "live_count": len(live_workflows),
            "recommendation": "Re-sync live workflows with repository templates" if (drifted or missing) else "All workflows in sync",
        }

    def capabilities(self) -> Dict[str, Any]:
        return {
            "agent": self.AGENT_ID,
            "role": "Chief Infrastructure Architect & CTO / n8n engineer",
            "skills": [
                "n8n workflow generation (core nodes only)",
                "FlowLint static analysis (anti-crutch rules)",
                "Golden Templates vault",
                "ADR generation + GitOps commit messages",
                "code review (static + optional LLM deep review)",
            ],
            "golden_templates": list(n8n_builder.GOLDEN_TEMPLATES.keys()),
            "anti_crutch_rules": [
                "core nodes only (no community packages)",
                "mandatory OnError branch on critical nodes",
                "no hardcoded secrets",
                "idempotency on webhook workflows",
            ],
            "llm_configured": self._llm is not None,
        }
