"""Deterministic privacy gate for Eva's durable memory writes.

This module makes no psychological inference. It is intentionally conservative:
ordinary turns are not long-term memory, explicit low-sensitivity requests may
be archived, review-worthy material is returned as a draft, and secret-like
input is rejected before it reaches an LLM or a persistent store.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from src.pii import PIIRedactor


class MemoryDisposition(str, Enum):
    """What the caller may do with one candidate memory item."""

    ARCHIVE = "archive"
    DRAFT = "draft"
    IGNORE = "ignore"
    REJECT = "reject"


@dataclass(frozen=True, slots=True)
class MemoryDecision:
    disposition: MemoryDisposition
    reason_code: str


_SECRET_PATTERNS = (
    re.compile(
        r"(?i)\b(?:password|passwd|пароль|api[_ -]?key|access[_ -]?token|"
        r"refresh[_ -]?token|client[_ -]?secret|secret|cookie|set-cookie|otp|2fa)"
        r"\s*[:=]\s*[^\s,;]{6,}"
    ),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{16,}"),
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,})\b"),
    re.compile(r"\b(?:sk-ant-|sk-live-|sk-proj-|gsk_|xox[baprs]-)[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
)

_SENSITIVE_TOPIC = re.compile(
    r"(?i)\b(?:психолог\w*|психотерап\w*|психічн\w*|ментальн\w*|"
    r"діагноз\w*|діагност\w*|депрес\w*|тривож\w*|паніч\w*|травм\w*|"
    r"самогуб\w*|суїцид\w*|лікар\w*|медичн\w*|лікуван\w*|ліки|"
    r"емоці\w*|настро\w*|втом\w*|мотив\w*|характер\w*|патерн\w*|стрес\w*|"
    r"health|mental health|diagnos\w*|therapy|medication|trauma|suicid\w*|"
    r"emotion\w*|mood|tired|motivation|personality|psychological pattern|stress)\b"
)
_LOCATION_DATA = re.compile(
    r"(?i)\b(?:gps|геолокац\w*|координат\w*|широт\w*|довгот\w*|"
    r"latitude|longitude|geotag\w*|geo[- ]?tag\w*|геоміт\w*|геотег\w*|"
    r"address(?:es)?|home\s+address|my\s+location|current\s+location|my\s+city|"
    r"i\s+live\s+(?:in|at)|"
    r"адрес\w*|місцезнаходжен\w*|місце\s+перебуван\w*|локац\w*|"
    r"моє\s+місто|я\s+живу\s+(?:в|у)|проживаю\s+(?:в|у))\b"
)
_COORDINATE_PAIR = re.compile(
    r"(?<!\d)[+-]?\d{1,2}\.\d{2,}\s*[,/]\s*[+-]?\d{1,3}\.\d{2,}(?!\d)"
)
_UNCERTAINTY = re.compile(
    r"(?i)\b(?:maybe|perhaps|probably|possibly|i think|i guess|assum\w*|unconfirmed|uncertain|"
    r"unknown|might|could be|можливо|ймовірно|мабуть|припуска\w*|припущен\w*|невідомо|"
    r"непев\w*|може бути)\b"
)
_REVIEW_REQUIRED_TOPIC = re.compile(
    r"(?i)\b(?:my friend|my partner|my colleague|my wife|my husband|"
    r"друг\w*|подруг\w*|дружин\w*|чоловік\w*|колег\w*|дитин\w*|"
    r"рекомендац\w*|порад\w*|recommend\w*|should|must|ought to|"
    r"варто|треба|потрібн\w*|маєш|"
    r"доступ\w*|дозвіл\w*|дозвол\w*|правил\w*|політик\w*|scope|grant|"
    r"policy|permission\w*|access\s+right\w*|"
    r"contact\w*|birthday|birthdate|relationship\w*|соцмереж\w*|контакт\w*|стосунк\w*|"
    r"дата\s+народжен\w*|день\s+народжен\w*)\b"
)


class EvaMemoryPolicy:
    """Apply an explicit-save and sensitivity gate before durable storage."""

    MAX_ITEM_CHARS = 2_000

    def __init__(self, pii_redactor: PIIRedactor | None = None) -> None:
        self._pii = pii_redactor or PIIRedactor()

    @staticmethod
    def contains_secret_like_value(text: object) -> bool:
        """Return a boolean only; never return or log the matched secret."""
        if not isinstance(text, str):
            return False
        return any(pattern.search(text) for pattern in _SECRET_PATTERNS)

    @staticmethod
    def contains_location_data(text: object) -> bool:
        """Detect explicit addresses/geolocation content without exposing the value."""
        return isinstance(text, str) and bool(
            _LOCATION_DATA.search(text) or _COORDINATE_PAIR.search(text)
        )

    def evaluate(
        self,
        text: object,
        *,
        explicit_save_request: bool,
        nightly_summary: bool = False,
    ) -> MemoryDecision:
        """Classify a proposed memory write without mutating any store."""
        if not isinstance(text, str) or not text.strip():
            return MemoryDecision(MemoryDisposition.REJECT, "empty_or_non_text")
        if self.contains_secret_like_value(text):
            return MemoryDecision(MemoryDisposition.REJECT, "secret_like_content")
        if self.contains_location_data(text):
            return MemoryDecision(MemoryDisposition.REJECT, "location_data_not_stored")
        if len(text) > self.MAX_ITEM_CHARS:
            return MemoryDecision(MemoryDisposition.DRAFT, "overlong_item_review_required")

        _redacted, pii_events = self._pii.redact(text)
        if pii_events:
            return MemoryDecision(MemoryDisposition.DRAFT, "personal_identifier_review_required")
        if _SENSITIVE_TOPIC.search(text):
            return MemoryDecision(MemoryDisposition.DRAFT, "sensitive_topic_review_required")
        if _REVIEW_REQUIRED_TOPIC.search(text) or _UNCERTAINTY.search(text):
            return MemoryDecision(MemoryDisposition.DRAFT, "uncertain_sensitive_or_policy_review_required")
        if nightly_summary:
            return MemoryDecision(MemoryDisposition.ARCHIVE, "low_sensitivity_nightly_summary")
        if not explicit_save_request:
            return MemoryDecision(MemoryDisposition.IGNORE, "no_explicit_save_request")
        return MemoryDecision(MemoryDisposition.ARCHIVE, "explicit_low_sensitivity_request")
