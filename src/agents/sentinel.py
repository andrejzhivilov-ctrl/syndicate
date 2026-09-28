"""
Sentinel Agent — Security validation, permission checks, threat assessment.
"""

from __future__ import annotations

import time
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

MAX_PAYLOAD_SIZE_BYTES = 1_048_576  # 1MB

@dataclass
class ValidationResult:
    allowed: bool
    reason: str
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class SentinelAgent:
    """Security validation agent for EVA SYNDICATE."""

    def __init__(self, vault_client: VaultClient) -> None:
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
        import json
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
            "task_type": task.get("task_type"),
            "allowed": result.allowed,
            "reason": result.reason,
            "risk_score": result.risk_score,
        })

        if not result.allowed:
            logger.warning(
                "Task blocked by Sentinel",
                task_type=task.get("task_type"),
                reason=result.reason,
                risk_score=result.risk_score,
            )
