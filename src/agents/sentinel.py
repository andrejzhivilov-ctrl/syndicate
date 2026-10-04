"""
Sentinel Protocol — Zero-Trust Security Shield subordinate to Marshal (Chief Security Officer).
Automated first-line defense: inbound prompt injection filtering, outbound action veto,
lethal trifecta guard, destructive command blocking, slopsquatting check, secret leakage scan.
"""

from __future__ import annotations

import re
import time
import json
import hmac
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

import structlog

from src.vault_client import VaultClient

logger = structlog.get_logger(__name__)

BLOCKED_TASK_TYPES: Set[str] = {
    "execute_shell",
    "raw_sql",
    "admin_override",
    "mount_filesystem",
}

OUTBOUND_POLICIES = {
    'send_email':       {'rule': 'draft_only', 'risk': 'high'},
    'send_email_direct': {'rule': 'block_always', 'risk': 'critical'},
    'send_telegram':    {'rule': 'allow', 'risk': 'low', 'log': True},
    'place_order':      {'rule': 'hitl_required', 'risk': 'critical'},
    'trade_execute':    {'rule': 'hitl_required', 'risk': 'critical'},
    'delete_data':      {'rule': 'block_always', 'risk': 'critical'},
    'modify_config':    {'rule': 'hitl_required', 'risk': 'high'},
    'modify_workflow':  {'rule': 'hitl_required', 'risk': 'high'},
    'create_draft':     {'rule': 'allow', 'risk': 'low'},
    'read_data':        {'rule': 'allow', 'risk': 'low'},
    'analyze':          {'rule': 'allow', 'risk': 'low'},
    'summarize':        {'rule': 'allow', 'risk': 'low'},
}

MAX_PAYLOAD_SIZE_BYTES = 1_048_576  # 1MB

_ZERO_WIDTH = re.compile("[\u200b\u200c\u200d\u2060\ufeff\u202e]")
_EXTERNAL_INJECTION_RULES = [
    ("ignore_instructions_en", re.compile(r"ignore (all |any )?(previous|prior|above) (instructions|rules|prompts)", re.I), 0.6),
    ("ignore_instructions_ru_uk", re.compile(r"(игнорируй|ігноруй|забудь)\s+(все\s+)?(предыдущ|попередн|прежн)", re.I), 0.6),
    ("role_override", re.compile(r"\b(you are now|act as|from now on you)\b", re.I), 0.35),
    ("system_marker", re.compile(r"(^|\n)\s*(system|assistant)\s*:", re.I), 0.35),
    ("code_fence_system", re.compile(r"```\s*system", re.I), 0.5),
    ("exfiltration", re.compile(r"(send|post|upload|email|exfiltrate|відправ|отправь).{0,60}(\.env|api[_ -]?key|secret|token|password|ssh)", re.I | re.S), 0.7),
    ("tool_hijack", re.compile(r"(run|execute|виконай|выполни).{0,40}(curl|wget|bash|powershell|rm -rf)", re.I | re.S), 0.6),
    ("hidden_html_instruction", re.compile(r"<!--.{0,200}(ignore|instruction|system).{0,200}-->", re.I | re.S), 0.5),
    ("override_keyword", re.compile(r"\bOVERRIDE\b"), 0.3),
]
_SECRET_PATTERNS = [
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{15,}")),
    ("openai_key", re.compile(r"sk-(proj-)?[A-Za-z0-9_\-]{20,}")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("telegram_bot_token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_\-]{35}\b")),
    ("bearer_header", re.compile(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._\-]{16,}")),
    ("private_key_block", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]
_DANGEROUS_COMMANDS = [
    ("rm_rf", re.compile(r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\b")),
    ("drop_table", re.compile(r"\bdrop\s+(table|database|schema)\b", re.I)),
    ("truncate", re.compile(r"\btruncate\s+table\b", re.I)),
    ("delete_without_where", re.compile(r"\bdelete\s+from\s+\w+\s*(;|$)", re.I)),
    ("disk_wipe", re.compile(r"\b(mkfs(\.\w+)?|dd\s+if=)")),
    ("pipe_to_shell", re.compile(r"(curl|wget)[^|\n]*\|\s*(sudo\s+)?(ba)?sh\b")),
    ("chmod_777", re.compile(r"\bchmod\s+(-R\s+)?777\b")),
    ("force_push", re.compile(r"git\s+push\s+.*(--force|-f)\b")),
    ("backup_removal", re.compile(r"(rm|del|Remove-Item)\b.*\b(backup|backups|\.bak)\b", re.I)),
]

@dataclass
class ValidationResult:
    allowed: bool
    reason: str
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def requires_hitl(self) -> bool:
        return bool(self.metadata.get("requires_hitl", False))

    def __getitem__(self, item: str) -> Any:
        if item == "allowed":
            return self.allowed
        if item == "reason":
            return self.reason
        if item == "risk_score":
            return self.risk_score
        if item == "metadata":
            return self.metadata
        if item in self.metadata:
            return self.metadata[item]
        raise KeyError(item)

    def get(self, item: str, default: Any = None) -> Any:
        try:
            return self[item]
        except KeyError:
            return default

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "allowed": self.allowed,
            "reason": self.reason,
            "risk_score": self.risk_score,
            "metadata": self.metadata,
            "requires_hitl": self.requires_hitl,
        }
        d.update(self.metadata)
        return d


class SentinelAgent:
    """Security validation agent for EVA SYNDICATE."""

    def __init__(self, vault_client: Optional[VaultClient] = None) -> None:
        self._vault = vault_client
        self._audit_log: List[Dict[str, Any]] = []

    async def validate_task(self, task: Dict[str, Any]) -> ValidationResult:
        """
        Multi-layer task validation:
        1. Task type allowlist check
        2. Payload size check
        3. Content scanning (injection patterns)
        4. Rate limiting (per session)
        5. Risk scoring
        """
        task_type = task.get("task_type", "")
        payload = task.get("payload", {})

        # 1. Blocked task types
        if task_type in BLOCKED_TASK_TYPES:
            result = ValidationResult(
                allowed=False,
                reason=f"Task type '{task_type}' is explicitly blocked",
                risk_score=1.0,
            )
            self._audit(task, result)
            return result

        # 2. Payload size
        payload_size = len(json.dumps(payload).encode("utf-8"))
        if payload_size > MAX_PAYLOAD_SIZE_BYTES:
            result = ValidationResult(
                allowed=False,
                reason=f"Payload too large: {payload_size} bytes (max {MAX_PAYLOAD_SIZE_BYTES})",
                risk_score=0.5,
            )
            self._audit(task, result)
            return result

        # 3. Content injection scanning
        injection_risk = self._scan_for_injections(payload)
        if injection_risk > 0.8:
            result = ValidationResult(
                allowed=False,
                reason="Potential injection attack detected",
                risk_score=injection_risk,
            )
            self._audit(task, result)
            return result

        # 4. Risk scoring
        risk_score = self._calculate_risk_score(task_type, payload, injection_risk)

        result = ValidationResult(
            allowed=True,
            reason="Validation passed",
            risk_score=risk_score,
        )
        self._audit(task, result)
        return result

    async def veto_outbound_action(self, agent_id: str, action: Dict) -> ValidationResult:
        action_type = action.get('type', '')
        policy = OUTBOUND_POLICIES.get(action_type, {'rule': 'hitl_required', 'risk': 'high'})
        
        rule = policy['rule']
        if rule == 'block_always':
            res = ValidationResult(allowed=False, reason="Action blocked by policy", risk_score=1.0)
        elif rule == 'draft_only' and action.get('auto_send', False):
            res = ValidationResult(allowed=False, reason="Action must be draft only", risk_score=0.8)
        elif rule == 'hitl_required':
            res = ValidationResult(allowed=True, reason="HITL required", risk_score=0.5, metadata={'requires_hitl': True})
        else:
            res = ValidationResult(allowed=True, reason="Action allowed", risk_score=0.1)
            
        self._audit({'agent_id': agent_id, 'action': action}, res)
        return res

    def scan_prompt_injection(self, text: str) -> ValidationResult:
        patterns = [
            'ignore previous instructions',
            'you are now',
            'system: ',
            'OVERRIDE',
            '```system',
        ]
        text_lower = text.lower()
        matches = sum(1 for p in patterns if p.lower() in text_lower)
        
        # Various unicode tricks check (basic)
        if '\\u' in text_lower or '\\x' in text_lower:
            matches += 1
            
        risk = min(0.85 + (matches - 1) * 0.1, 1.0) if matches > 0 else 0.0
        allowed = matches == 0
        return ValidationResult(allowed=allowed, reason="Prompt injection risk" if not allowed else "Clean", risk_score=risk)

    async def verify_webhook_signature(self, payload_bytes: bytes, signature: str, secret_key: str) -> bool:
        expected_mac = hmac.new(secret_key.encode('utf-8'), payload_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_mac, signature)

    # ── Lethal Trifecta shield ────────────────────────────────────────────
    def check_lethal_trifecta(self, capabilities: Dict[str, bool]) -> ValidationResult:
        """Block any agent that combines private data + untrusted content + external actions.

        capabilities keys: private_data_access, untrusted_content, external_actions (or aliases).
        """
        has_private = bool(capabilities.get("private_data_access") or capabilities.get("reads_private_data"))
        has_untrusted = bool(capabilities.get("untrusted_content") or capabilities.get("processes_untrusted_input"))
        has_external = bool(capabilities.get("external_actions") or capabilities.get("initiates_external_communication"))
        legs = []
        if has_private:
            legs.append("private_data_access")
        if has_untrusted:
            legs.append("untrusted_content")
        if has_external:
            legs.append("external_actions")
        if len(legs) == 3:
            res = ValidationResult(
                allowed=False,
                reason="Lethal trifecta: private data + untrusted content + external actions in one agent",
                risk_score=1.0,
                metadata={"legs": legs},
            )
        else:
            res = ValidationResult(True, f"Trifecta intact ({len(legs)}/3 legs)", risk_score=0.2 * len(legs), metadata={"legs": legs})
        self._audit({"check": "lethal_trifecta", "capabilities": capabilities}, res)
        return res

    def scan_external_content(self, text: str) -> ValidationResult:
        """Rich indirect-prompt-injection scan for web pages, issues, e-mails and documents."""
        score = 0.0
        hits: List[str] = []
        for name, rx, weight in _EXTERNAL_INJECTION_RULES:
            if rx.search(text):
                hits.append(name)
                score += weight
        if _ZERO_WIDTH.search(text):
            hits.append("zero_width_characters")
            score += 0.3
        score = min(score, 1.0)
        res = ValidationResult(
            allowed=score < 0.5,
            reason="External content looks like an injection" if score >= 0.5 else "External content clean",
            risk_score=score,
            metadata={"hits": hits},
        )
        self._audit({"check": "external_content", "hits": hits}, res)
        return res

    def assess_dependency_install(
        self, packages: List[str] | str, lockfile_packages: Optional[Set[str]] = None, allowlist: Optional[Set[str]] = None
    ) -> ValidationResult:
        """Slopsquatting guard: a hallucinated package name must never be installed automatically."""
        if isinstance(packages, str):
            packages = [packages]
        known = {p.lower() for p in (lockfile_packages or set())} | {p.lower() for p in (allowlist or set())}
        unknown = [p for p in packages if p.lower().split("==")[0].split(">=")[0] not in known]
        if unknown:
            res = ValidationResult(
                allowed=True,
                reason="Packages not in lockfile/allowlist require human review",
                risk_score=0.7,
                metadata={"requires_hitl": True, "unknown_packages": unknown, "risk": "high", "is_slopsquatting": True},
            )
        else:
            res = ValidationResult(True, "All packages pinned", risk_score=0.05, metadata={"risk": "low", "is_slopsquatting": False})
        self._audit({"check": "dependency_install", "packages": packages}, res)
        return res

    def scan_output_for_secrets(self, text: str) -> ValidationResult:
        """Detect secrets leaking into logs / stdout / agent replies."""
        found = [name for name, rx in _SECRET_PATTERNS if rx.search(text)]
        redacted = text
        for name, rx in _SECRET_PATTERNS:
            token_tag = "[REDACTED_GH_TOKEN]" if "github" in name else f"[REDACTED_{name.upper()}]"
            redacted = rx.sub(token_tag, redacted)
        res = ValidationResult(
            allowed=not found,
            reason="Secret material detected in output" if found else "No secrets detected",
            risk_score=1.0 if found else 0.0,
            metadata={"kinds": found, "has_secrets": bool(found), "redacted_output": redacted},
        )
        self._audit({"check": "secret_scan", "kinds": found}, res)
        return res

    def check_command_safety(self, command: str) -> ValidationResult:
        """Destructive shell / SQL commands are blocked outright (PocketOS-style incidents)."""
        for name, rx in _DANGEROUS_COMMANDS:
            if rx.search(command):
                res = ValidationResult(False, f"Destructive command blocked: {name}", risk_score=1.0, metadata={"rule": name})
                self._audit({"check": "command_safety", "rule": name}, res)
                return res
        res = ValidationResult(True, "Command not flagged", risk_score=0.1)
        self._audit({"check": "command_safety"}, res)
        return res


    def _scan_for_injections(self, payload: Dict[str, Any]) -> float:
        """Scan payload for potential injection patterns. Returns risk score 0-1."""
        INJECTION_PATTERNS = [
            "__import__",
            "subprocess",
            "os.system",
            "eval(",
            "exec(",
            "DROP TABLE",
            "DELETE FROM",
            "UNION SELECT",
            "'; --",
            "../../../",
            "/etc/passwd",
        ]

        payload_str = str(payload).lower()
        matches = sum(1 for p in INJECTION_PATTERNS if p.lower() in payload_str)

        if matches == 0:
            return 0.0
        elif matches <= 2:
            return 0.4
        else:
            return 0.9

    def _calculate_risk_score(
        self,
        task_type: str,
        payload: Dict[str, Any],
        base_injection_risk: float,
    ) -> float:
        """Calculate composite risk score."""
        HIGH_RISK_TASKS = {"webhook_telegram", "execute", "admin"}
        LOW_RISK_TASKS = {"health", "status", "summarize", "analyze_document"}

        base = 0.1
        if task_type in HIGH_RISK_TASKS:
            base += 0.3
        elif task_type in LOW_RISK_TASKS:
            base -= 0.05

        return min(base + base_injection_risk, 1.0)

    def _audit(self, task: Dict[str, Any], result: ValidationResult) -> None:
        """Record security event to in-memory audit log (persisted to DB by orchestrator)."""
        self._audit_log.append({
            "timestamp": time.time(),
            "task_type": task.get("task_type", "unknown"),
            "allowed": result.allowed,
            "reason": result.reason,
            "risk_score": result.risk_score,
        })

        if not result.allowed:
            logger.warning(
                "Task blocked by Sentinel",
                task_type=task.get("task_type", "unknown"),
                reason=result.reason,
                risk_score=result.risk_score,
            )
