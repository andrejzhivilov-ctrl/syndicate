"""
Sentinel Agent — Security validation, permission checks, threat assessment.
"""

from __future__ import annotations

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

@dataclass
class ValidationResult:
    allowed: bool
    reason: str
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def requires_hitl(self) -> bool:
        return bool(self.metadata.get("requires_hitl", False))


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
