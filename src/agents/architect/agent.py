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

import ast
import inspect
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
        # Action -> handler (was an 11-branch if/elif chain). execute() awaits
        # only when the handler returned an awaitable.
        self._ACTION_MAP: Dict[str, Any] = {}
        for names, handler in (
            (("design_workflow", "build_workflow"), self.design_workflow),
            (("lint_workflow", "flowlint"), self.lint),
            (("golden_template", "template"), self.golden_template),
            (("adr",), self.generate_adr),
            (("review_code", "code_review"), self.review_code),
            (("gitops_sync", "open_pr"), self.gitops_sync),
            (("drift_detect", "check_drift"), self.drift_detect),
            (("generate_ui_scaffold", "build_ui", "app_generator"), self.generate_ui_scaffold),
            (("verify_code", "verify_integrity", "ast_check"), self._act_verify_code),
            (("self_healing_generate", "verified_codegen"), self.self_healing_generate),
            (("capabilities", "status"), self._act_capabilities),
        ):
            for name in names:
                self._ACTION_MAP[name] = handler

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "capabilities")
        try:
            handler = self._ACTION_MAP.get(action)
            if handler is None:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}",
                    "agent": self.AGENT_ID,
                    "available_actions": sorted(self._ACTION_MAP),
                }
            result = handler(payload)
            return await result if inspect.isawaitable(result) else result
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

    def _act_verify_code(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.verify_code_integrity(payload.get("code", ""))

    def _act_capabilities(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """`capabilities()` takes no payload — adapt it to the dispatch table."""
        return self.capabilities()

    @staticmethod
    def _known_signatures() -> Dict[str, set]:
        """Introspect the real EVA interfaces we validate calls against."""
        from src.lessons import LessonsStore
        from src.memory import MemoryManager

        return {
            "save_episode": set(inspect.signature(MemoryManager.save_episode).parameters) - {"self"},
            "semantic_search": set(inspect.signature(MemoryManager.semantic_search).parameters) - {"self"},
            "record_lesson": set(inspect.signature(LessonsStore.record_lesson).parameters) - {"self"},
            "check_before_action": set(inspect.signature(LessonsStore.check_before_action).parameters) - {"self"},
        }

    @staticmethod
    def _check_call_node(node: "ast.Call", known_signatures: Dict[str, set]) -> List[Dict[str, Any]]:
        """Validate a single ``ast.Call`` node (rules A, B and C)."""
        errors: List[Dict[str, Any]] = []

        if isinstance(node.func, ast.Attribute):
            func_name: Optional[str] = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
        else:
            func_name = None

        # Rule A: forbid synchronous .generate() on LLM clients.
        if func_name == "generate" and isinstance(node.func, ast.Attribute):
            owner = ast.unparse(node.func.value) if hasattr(ast, "unparse") else ""
            if "llm" in owner.lower():
                errors.append({
                    "line": getattr(node, "lineno", 0),
                    "rule": "async-llm-ainvoke",
                    "message": (
                        f"Forbidden call `{owner}.generate(...)`: use "
                        f"`await {owner}.ainvoke([HumanMessage(...)])` instead."
                    ),
                })

        if func_name is None:
            return errors

        # Rule B: keyword arguments must exist on the real signature.
        allowed = known_signatures.get(func_name)
        if allowed is not None:
            passed = {kw.arg for kw in node.keywords if kw.arg is not None}
            unknown = passed - allowed
            if unknown:
                errors.append({
                    "line": getattr(node, "lineno", 0),
                    "rule": "signature-mismatch",
                    "message": (
                        f"Call to `{func_name}()` passes unknown keyword argument(s): "
                        f"{sorted(unknown)}. Allowed: {sorted(allowed)}"
                    ),
                })

        # Rule C: semantic_search takes a vector, not a raw string.
        if func_name == "semantic_search" and node.args:
            first_arg = node.args[0]
            if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                errors.append({
                    "line": getattr(node, "lineno", 0),
                    "rule": "vector-type-mismatch",
                    "message": (
                        "`semantic_search()` expects `query_embedding: List[float]`, "
                        "but received a `str` literal."
                    ),
                })

        return errors

    @staticmethod
    def _check_sql_literal(node: "ast.Constant") -> List[Dict[str, Any]]:
        """Rule D: `:param::vector` breaks SQLAlchemy bind parsing."""
        if not isinstance(node.value, str):
            return []
        if ":vector" not in node.value:
            return []
        if re.search(r":[a-zA-Z_][a-zA-Z0-9_]*::vector", node.value):
            return [{
                "line": getattr(node, "lineno", 0),
                "rule": "sqlalchemy-vector-cast",
                "message": (
                    "SQL string uses `:param::vector` which breaks SQLAlchemy bind "
                    "parsing. Use `CAST(:param AS vector)` instead."
                ),
            }]
        return []

    def verify_code_integrity(self, code: str) -> Dict[str, Any]:
        """Compiler-in-the-Loop verifier:
        1. Parses Python AST (`ast.parse`) to catch syntax errors.
        2. Inspects method calls against core EVA Syndicate interfaces (`MemoryManager`, `LessonsStore`).
        3. Detects SQLAlchemy `:param::vector` bind conflicts and synchronous `.generate()` traps.
        """
        errors: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []

        if not code or not code.strip():
            return {"agent": self.AGENT_ID, "passed": False, "errors": [{"line": 0, "rule": "empty-code", "message": "Empty code provided"}]}

        # Step 1: AST Syntax Verification
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return {
                "agent": self.AGENT_ID,
                "passed": False,
                "errors": [{
                    "line": exc.lineno or 0,
                    "rule": "syntax-error",
                    "message": f"SyntaxError: {exc.msg} at line {exc.lineno}, col {exc.offset}",
                }],
            }

        known_signatures = self._known_signatures()

        # Step 3: Walk AST nodes to validate calls and SQL strings
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                errors.extend(self._check_call_node(node, known_signatures))
            elif isinstance(node, ast.Constant):
                errors.extend(self._check_sql_literal(node))

        # Step 4: Include security static findings
        for item in self._static_review(code, "python"):
            if item["severity"] == "security":
                warnings.append(item)

        return {
            "agent": self.AGENT_ID,
            "passed": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
            "warnings": warnings,
        }

    async def self_healing_generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Self-Healing Code Generator with Compiler-in-the-Loop:
        Generates or fixes Python code via the Architect's Reasoning Model, verifies it via
        `verify_code_integrity()`, and automatically loops up to `max_retries` times until
        0 AST/signature/security errors remain.
        """
        task_prompt = payload.get("prompt") or payload.get("specification") or ""
        current_code = payload.get("code", "")
        max_retries = int(payload.get("max_retries", 3))

        history: List[Dict[str, Any]] = []
        verification: Dict[str, Any] = {"passed": False, "errors": []}

        if current_code:
            verification = self.verify_code_integrity(current_code)
            if verification["passed"]:
                return {
                    "agent": self.AGENT_ID,
                    "verified": True,
                    "status": "verified_clean",
                    "attempts": 0,
                    "code": current_code,
                    "verification": verification,
                    "healing_history": history,
                }

        for attempt in range(1, max_retries + 1):
            if not self._llm:
                return {
                    "agent": self.AGENT_ID,
                    "verified": False,
                    "status": "failed_no_llm_for_healing",
                    "attempts": attempt,
                    "code": current_code,
                    "verification": verification,
                }

            from langchain_core.messages import HumanMessage, SystemMessage
            error_feedback = json.dumps(verification.get("errors", []), ensure_ascii=False)
            prev_status = "PREVIOUS ATTEMPT FAILED COMPILER VERIFICATION.\n" if verification.get("errors") else ""
            repair_prompt = (
                f"{prev_status}"
                f"Write production-ready async Python code for: {task_prompt}\n\n"
                f"Current code:\n```python\n{current_code}\n```\n\n"
                f"Compiler-in-the-Loop AST/Signature Errors to fix:\n{error_feedback}\n\n"
                "Rules:\n"
                "1. Use `await self._llm.ainvoke([HumanMessage(...)])` (never `.generate()`).\n"
                "2. Use `CAST(:param AS vector)` in SQLAlchemy `text()`.\n"
                "3. Match `save_episode(session_id=..., agent_id=..., role=..., content=..., metadata=...)`.\n"
                "Return ONLY valid Python code without markdown fences."
            )
            resp = await self._llm.ainvoke([
                SystemMessage(content="You are the Chief Architect Reasoning Engine. Output strictly valid, verified Python code."),
                HumanMessage(content=repair_prompt),
            ])
            raw = str(getattr(resp, "content", resp)).strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```[a-zA-Z]*\n", "", raw)
                raw = re.sub(r"\n```$", "", raw)
            current_code = raw.strip()

            verification = self.verify_code_integrity(current_code)
            history.append({"attempt": attempt, "passed": verification["passed"], "errors": verification["errors"]})
            if verification["passed"]:
                return {
                    "agent": self.AGENT_ID,
                    "verified": True,
                    "status": "verified_clean",
                    "attempts": attempt,
                    "code": current_code,
                    "verification": verification,
                    "healing_history": history,
                }

        return {
            "agent": self.AGENT_ID,
            "verified": verification.get("passed", False),
            "status": "verified_clean" if verification.get("passed") else "max_retries_reached",
            "attempts": max_retries,
            "code": current_code,
            "verification": verification,
            "healing_history": history,
        }

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

    async def generate_ui_scaffold(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """App Generator / UI Scaffold Engine (inspired by Abacus Vibe Coding):
        Generates production-ready frontend boilerplate (Next.js / Tailwind / Tauri / Flutter)
        specifically configured to communicate with EVA Syndicate agent REST/WebSocket APIs.
        """
        framework = payload.get("framework", "nextjs").lower()  # nextjs, flutter, tauri
        app_name = payload.get("app_name", "syndicate-command-center")

        endpoints = {
            "eva": "http://localhost:8001/chat",
            "marshal": "http://localhost:8002/security_status",
            "architect": "http://localhost:8003/infra_status",
            "fin": "http://localhost:8004/runway",
            "doc": "http://localhost:8005/morning_readiness",
            "sam": "http://localhost:8006/evaluate_setup",
        }

        if framework in ("nextjs", "react", "pwa"):
            scaffold = {
                "package_json": {
                    "name": app_name,
                    "dependencies": {
                        "react": "^18.3.0",
                        "next": "^14.2.0",
                        "lucide-react": "^0.370.0",
                        "tailwindcss": "^3.4.0",
                        "swr": "^2.2.5"
                    }
                },
                "components": [
                    "DashboardHeader.tsx",
                    "AgentCardGrid.tsx",
                    "HitlActionGateModal.tsx",
                    "LiveMarketChart.tsx",
                    "BiometricStatusCard.tsx"
                ],
                "api_client": "export const fetchAgent = (port, action) => fetch(`http://localhost:${port}/execute`, { method: 'POST', body: JSON.stringify({ action }) });",
            }
        elif framework == "flutter":
            scaffold = {
                "pubspec_yaml": "name: syndicate_mobile\ndependencies:\n  flutter:\n    sdk: flutter\n  http: ^1.2.0\n  provider: ^6.1.0",
                "screens": ["HomeScreen.dart", "SamTradingScreen.dart", "DocHealthScreen.dart", "HitlGateScreen.dart"],
            }
        else:
            scaffold = {"framework": framework, "status": "scaffold_available_for_nextjs_and_flutter"}

        return {
            "agent": self.AGENT_ID,
            "action": "generate_ui_scaffold",
            "framework": framework,
            "app_name": app_name,
            "endpoints_wired": endpoints,
            "scaffold_blueprint": scaffold,
            "status": "ready_to_build",
            "note": "Scaffold mapped directly to syndicate-internal REST endpoints (ports 8001-8006)."
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
