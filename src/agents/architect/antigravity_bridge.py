"""
SYNDICATE — Antigravity Super-Agent Secure Bridge.

Cryptographic delegation bridge between SYNDICATE's Architect (Chief Technology Officer)
and the external Antigravity runtime (High-Tier Engineering Contractor / Super-Agent).

Enables delegating complex tasks (APK reverse engineering, web application cloning,
deep multi-file refactoring, production UI generation) with:
1. HMAC-SHA256 signed task envelopes preventing tampering.
2. Asynchronous file-based or HTTP/IPC delivery.
3. Sentinel/Marshal gate verification of contractor outputs (prompt injection scanning,
   secret leakage scanning, and AST syntax validation) before code ingestion into SYNDICATE.
"""

from __future__ import annotations

import ast
import hashlib
import hmac
import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger(__name__)

DEFAULT_BRIDGE_SECRET = os.environ.get("ANTIGRAVITY_BRIDGE_SECRET", "syndicate-antigravity-bridge-secret-key-2026")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_bytes(data: Dict[str, Any]) -> bytes:
    """Deterministic JSON serialization for cryptographic signature calculation."""
    filtered = {k: v for k, v in data.items() if k != "signature"}
    return json.dumps(filtered, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


@dataclass
class AntigravityTaskEnvelope:
    """HMAC-signed task envelope for delegating work to Antigravity."""

    task_id: str
    task_type: str
    title: str
    prompt: str
    sender: str = "architect@syndicate"
    recipient: str = "antigravity@contractor"
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now_iso)
    signature: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AntigravityBridge:
    """Secure delegation bridge connecting Architect with external Antigravity agent."""

    def __init__(
        self,
        bridge_dir: Optional[Path | str] = None,
        secret_key: Optional[str] = None,
        sentinel: Optional[Any] = None,
    ) -> None:
        self.secret_key = (secret_key or DEFAULT_BRIDGE_SECRET).encode("utf-8")
        self.bridge_dir = Path(bridge_dir) if bridge_dir else Path.cwd() / "data" / "antigravity_bridge"
        self.sentinel = sentinel

        self.tasks_dir = self.bridge_dir / "tasks"
        self.results_dir = self.bridge_dir / "results"
        self.completed_dir = self.bridge_dir / "completed"
        self.rejected_dir = self.bridge_dir / "rejected"

        for d in (self.tasks_dir, self.results_dir, self.completed_dir, self.rejected_dir):
            d.mkdir(parents=True, exist_ok=True)

    def compute_signature(self, envelope_dict: Dict[str, Any]) -> str:
        """Compute HMAC-SHA256 signature for envelope."""
        canonical = _canonical_bytes(envelope_dict)
        return hmac.new(self.secret_key, canonical, hashlib.sha256).hexdigest()

    def verify_signature(self, envelope_dict: Dict[str, Any]) -> bool:
        """Verify HMAC-SHA256 signature of envelope."""
        received_sig = envelope_dict.get("signature")
        if not received_sig:
            return False
        expected_sig = self.compute_signature(envelope_dict)
        return hmac.compare_digest(received_sig, expected_sig)

    def dispatch_task(
        self,
        task_type: str,
        title: str,
        prompt: str,
        payload: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Package and dispatch a task for Antigravity."""
        tid = task_id or f"ag-{uuid.uuid4().hex[:12]}"
        envelope = AntigravityTaskEnvelope(
            task_id=tid,
            task_type=task_type,
            title=title,
            prompt=prompt,
            payload=payload or {},
            created_at=_now_iso(),
        )
        envelope_dict = envelope.to_dict()
        envelope_dict["signature"] = self.compute_signature(envelope_dict)

        task_path = self.tasks_dir / f"{tid}.json"
        task_path.write_text(json.dumps(envelope_dict, indent=2, ensure_ascii=False), encoding="utf-8")

        logger.info(
            "antigravity_task_dispatched",
            task_id=tid,
            task_type=task_type,
            path=str(task_path),
        )
        return envelope_dict

    def verify_and_ingest_result(
        self,
        result_envelope: Dict[str, Any],
        strict_syntax: bool = True,
    ) -> Dict[str, Any]:
        """
        Verify incoming result from Antigravity:
        1. HMAC signature verification
        2. Sentinel prompt injection scan
        3. Sentinel secret leakage scan
        4. Python AST syntax validation for any provided code snippets
        """
        task_id = result_envelope.get("task_id", "unknown")

        # 1. Signature check
        if not self.verify_signature(result_envelope):
            logger.warning("antigravity_bridge_invalid_signature", task_id=task_id)
            self._archive_rejected(task_id, result_envelope, "HMAC-SHA256 signature mismatch or missing")
            return {
                "status": "rejected",
                "task_id": task_id,
                "reason": "HMAC-SHA256 signature mismatch or missing",
            }

        result_data = result_envelope.get("result", {})
        code_snippets: Dict[str, str] = result_data.get("files", {})

        # 2. Sentinel checks if available, 3. Python AST check for code files
        rejection = self._sentinel_rejection(result_data, code_snippets)
        if rejection is None and strict_syntax:
            rejection = self._syntax_rejection(task_id, code_snippets)
        if rejection is not None:
            archived_reason, reason = rejection
            self._archive_rejected(task_id, result_envelope, archived_reason)
            return {"status": "rejected", "task_id": task_id, "reason": reason}

        # All checks passed -> accept
        self._archive_completed(task_id, result_envelope)
        logger.info("antigravity_bridge_result_accepted", task_id=task_id)
        return {
            "status": "accepted",
            "task_id": task_id,
            "verified_at": _now_iso(),
            "file_count": len(code_snippets),
            "result": result_data,
        }

    def _sentinel_rejection(
        self, result_data: Dict[str, Any], code_snippets: Dict[str, str]
    ) -> Optional[Tuple[str, str]]:
        """(archived reason, returned reason) when Sentinel blocks the result, else None."""
        if not self.sentinel:
            return None
        # Check prompt injection in narrative / summary
        narrative = str(result_data.get("summary", "")) + " " + str(result_data.get("notes", ""))
        if narrative.strip() and hasattr(self.sentinel, "scan_prompt_injection"):
            injection_result = self.sentinel.scan_prompt_injection(narrative)
            if not getattr(injection_result, "allowed", True):
                reason = f"Sentinel prompt injection alert: {injection_result.reason}"
                return reason, reason
        # Check secrets in code snippets
        if hasattr(self.sentinel, "scan_output_for_secrets"):
            for fname, code in code_snippets.items():
                sec_check = self.sentinel.scan_output_for_secrets(code)
                if not getattr(sec_check, "allowed", True):
                    return (f"Secret leakage detected in file {fname}",
                            f"Secret leakage detected in contractor output: {fname}")
        return None

    @staticmethod
    def _syntax_rejection(task_id: str, code_snippets: Dict[str, str]) -> Optional[Tuple[str, str]]:
        for fname, content in code_snippets.items():
            if fname.endswith(".py") and isinstance(content, str):
                try:
                    ast.parse(content, filename=fname)
                except SyntaxError as e:
                    reason = f"SyntaxError in contractor code {fname}: {e}"
                    logger.error("antigravity_bridge_syntax_error", task_id=task_id, error=str(e))
                    return reason, reason
        return None

    def _archive_completed(self, task_id: str, envelope: Dict[str, Any]) -> None:
        path = self.completed_dir / f"{task_id}.json"
        path.write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8")
        # Cleanup pending task if exists
        task_f = self.tasks_dir / f"{task_id}.json"
        if task_f.exists():
            task_f.unlink()

    def _archive_rejected(self, task_id: str, envelope: Dict[str, Any], reason: str) -> None:
        envelope["rejection_reason"] = reason
        path = self.rejected_dir / f"{task_id}.json"
        path.write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8")

    def list_pending_tasks(self) -> List[Dict[str, Any]]:
        """List tasks waiting to be processed by Antigravity contractor."""
        tasks = []
        for f in self.tasks_dir.glob("*.json"):
            try:
                tasks.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                continue
        return sorted(tasks, key=lambda x: x.get("created_at", ""), reverse=True)

    def get_status(self) -> Dict[str, Any]:
        """Summary of bridge queues."""
        return {
            "bridge_dir": str(self.bridge_dir),
            "pending_tasks": len(list(self.tasks_dir.glob("*.json"))),
            "completed_tasks": len(list(self.completed_dir.glob("*.json"))),
            "rejected_tasks": len(list(self.rejected_dir.glob("*.json"))),
            "sentinel_active": self.sentinel is not None,
        }
