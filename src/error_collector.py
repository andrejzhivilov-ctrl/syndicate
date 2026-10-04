"""
Error Collector (Dead Letter Queue).

Every failure (n8n node, LLM timeout, exchange API, script crash) is turned
into a normalized, PII-redacted report, de-duplicated by fingerprint, queued
for Marshal's audit and recorded as a lesson so the Architect never repeats
the same mistake silently.
"""

from __future__ import annotations

import hashlib
import re
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional

import structlog

from src.pii import PIIRedactor

logger = structlog.get_logger(__name__)

_VOLATILE = re.compile(r"(\b[0-9a-f]{8}-[0-9a-f-]{27}\b|\b\d{4,}\b|0x[0-9a-fA-F]+)")


@dataclass
class ErrorReport:
    fingerprint: str
    source: str
    node: Optional[str]
    message: str
    severity: str
    payload_sample: str
    first_seen: float
    last_seen: float
    count: int = 1
    routed_to: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = self.__dict__.copy()
        d["occurrences"] = self.count
        return d


class ErrorCollector:
    """Normalize, dedupe, queue and learn from failures."""

    SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2, "critical": 3}

    def __init__(
        self,
        lessons_store: Optional[Any] = None,
        pii_redactor: Optional[PIIRedactor] = None,
        max_queue: int = 500,
        dedupe_window_s: float = 900.0,
    ) -> None:
        self._lessons = lessons_store
        self._pii = pii_redactor or PIIRedactor()
        self._window = dedupe_window_s
        self.marshal_queue: Deque[ErrorReport] = deque(maxlen=max_queue)
        self._by_fp: Dict[str, ErrorReport] = {}

    @staticmethod
    def fingerprint(source: str, node: Optional[str], message: str) -> str:
        norm = _VOLATILE.sub("#", message.lower())[:300]
        return hashlib.sha256(f"{source}|{node or ''}|{norm}".encode()).hexdigest()[:16]

    async def report(
        self,
        source: str,
        error_message: str,
        node: Optional[str] = None,
        payload_sample: Any = None,
        severity: str = "error",
    ) -> ErrorReport:
        now = time.time()
        severity = severity if severity in self.SEVERITY_ORDER else "error"
        clean_msg, _ = self._pii.redact(str(error_message))
        clean_sample, _ = self._pii.redact(str(payload_sample)[:500]) if payload_sample is not None else ("", [])
        fp = self.fingerprint(source, node, clean_msg)

        existing = self._by_fp.get(fp)
        if existing and now - existing.last_seen <= self._window:
            existing.count += 1
            existing.last_seen = now
            if self.SEVERITY_ORDER[severity] > self.SEVERITY_ORDER[existing.severity]:
                existing.severity = severity
            return existing

        rep = ErrorReport(fp, source, node, clean_msg, severity, clean_sample, now, now)
        self._by_fp[fp] = rep
        self.marshal_queue.append(rep)
        rep.routed_to.append("marshal")

        if self._lessons is not None and self.SEVERITY_ORDER[severity] >= self.SEVERITY_ORDER["error"]:
            try:
                await self._lessons.record_lesson(
                    agent_id="architect",
                    kind="failure",
                    summary=f"[{source}{'/' + node if node else ''}] {clean_msg[:240]}",
                    context={"fingerprint": fp, "payload_sample": clean_sample},
                    category="incident",
                    severity="critical" if severity == "critical" else "high",
                )
                rep.routed_to.append("architect_lessons")
            except Exception as exc:  # noqa: BLE001
                logger.warning("error_collector_lesson_failed", error=str(exc))

        logger.info("error_reported", fingerprint=fp, source=source, node=node, severity=severity)
        return rep

    def audit_digest(self, min_severity: str = "error") -> Dict[str, Any]:
        """Compact digest for Marshal's audit queue."""
        floor = self.SEVERITY_ORDER.get(min_severity, 2)
        items = [r for r in self.marshal_queue if self.SEVERITY_ORDER[r.severity] >= floor]
        items.sort(key=lambda r: (-self.SEVERITY_ORDER[r.severity], -r.count))
        return {
            "total_open": len(items),
            "unique_incidents": len({r.fingerprint for r in items}),
            "top": [r.to_dict() for r in items[:10]],
        }

    def acknowledge(self, fingerprint: str) -> bool:
        rep = self._by_fp.pop(fingerprint, None)
        if rep and rep in self.marshal_queue:
            self.marshal_queue.remove(rep)
            return True
        return False

    async def record_error(
        self,
        source: str,
        error_message: str,
        node: Optional[str] = None,
        payload: Any = None,
        stack_trace: Optional[str] = None,
        severity: str = "error",
    ) -> Dict[str, Any]:
        """Record an error and return a structured summary dict."""
        rep = await self.report(
            source=source,
            error_message=error_message,
            node=node,
            payload_sample=payload,
            severity=severity,
        )
        return {
            "status": "deduplicated" if rep.count > 1 else "recorded",
            "fingerprint": rep.fingerprint,
            "fingerprint_summary": rep.message,
            "occurrences": rep.count,
            "severity": rep.severity,
            "routed_to": rep.routed_to,
        }

    def get_recent_errors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent errors from the audit queue."""
        return [r.to_dict() for r in list(self.marshal_queue)[-limit:]]
