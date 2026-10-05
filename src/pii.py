from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Match, Optional, Tuple

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class RedactionEvent:
    pattern_name: str
    original_match: str


# How each detected pattern is masked. Keeping this as data (instead of a long
# if/elif chain inside the replacer) makes every mask auditable at a glance.
_MASKERS: Dict[str, Callable[[Match], str]] = {
    "ukrainian_phone": lambda m: f"{m.group(1)}***{m.group(4)}",
    "intl_phone": lambda m: f"{m.group(1)}***{m.group(4)}",
    "email": lambda m: f"{m.group(1)}***@{m.group(3)}",
    "credit_card": lambda m: f"****{m.group(1)}",
    "ukrainian_ipn": lambda m: f"IPN:****{m.group(2)}",
    "passport": lambda m: f"{m.group(1)}******",
    "iban": lambda m: f"{m.group(1)}**...{m.group(2)}",
    "ipv4": lambda m: f"{m.group(1)}***.***",
}

# Patterns whose entire match is a secret — never partially preserved.
_KEY_PATTERNS = frozenset({"api_key_sk_ant", "api_key_ghp", "api_key_gsk"})
_KEY_MASK = "[REDACTED_KEY]"
_DEFAULT_MASK = "***"


def _mask(match: Match, pattern_name: str) -> str:
    if pattern_name in _KEY_PATTERNS:
        return _KEY_MASK
    masker = _MASKERS.get(pattern_name)
    return masker(match) if masker else _DEFAULT_MASK


class PIIRedactor:
    """
    PII Redaction module. Masks sensitive data before sending to external LLMs.
    """

    # Pre-compiled regex patterns for performance
    PATTERNS = {
        "ukrainian_phone": re.compile(r"(\+380)(\d{3})(\d{3})(\d{3})"),
        "intl_phone": re.compile(r"(\+1)(\d{3})(\d{3})(\d{4})"),
        "email": re.compile(r"([a-zA-Z0-9])([a-zA-Z0-9._%+-]*)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"),
        "credit_card": re.compile(r"\b(?:\d[ -]*?){12,15}(\d{4})\b"),
        "ukrainian_ipn": re.compile(r"\b(\d{4})(\d{6})\b"),
        "passport": re.compile(r"\b([A-Za-z]{2})(\d{6})\b"),
        # A Ukrainian IBAN is exactly 29 chars: UA + 2 check digits + 25.
        # The old pattern only spanned 27 of them, so real IBANs were never
        # masked at all — they went to the LLM verbatim.
        "iban": re.compile(r"\b(UA\d{2})[A-Z0-9]{21}([A-Z0-9]{4})\b"),
        "api_key_sk_ant": re.compile(r"\bsk-ant-[A-Za-z0-9_-]+\b"),
        "api_key_ghp": re.compile(r"\bghp_[A-Za-z0-9]+\b"),
        "api_key_gsk": re.compile(r"\bgsk_[A-Za-z0-9]+\b"),
        "ipv4": re.compile(r"\b(\d{1,3}\.\d{1,3}\.)(\d{1,3}\.\d{1,3})\b"),
    }

    def create_replacer(
        self,
        pattern_name: str,
        events: Optional[List[RedactionEvent]] = None,
    ) -> Callable[[Match], str]:
        """Build a ``re.sub`` replacer that records an audit event per match."""

        def replacer(match: Match) -> str:
            original = match.group(0)
            if events is not None:
                events.append(RedactionEvent(pattern_name=pattern_name, original_match=original))
            return _mask(match, pattern_name)

        return replacer

    def redact(self, text: str) -> Tuple[str, List[RedactionEvent]]:
        """
        Apply all patterns, return redacted text + list of what was redacted (for audit).
        """
        events: List[RedactionEvent] = []

        if not isinstance(text, str):
            # Non-strings pass through untouched (the caller keeps its types).
            return text, events

        redacted_text = text
        for name, pattern in self.PATTERNS.items():
            redacted_text = pattern.sub(self.create_replacer(name, events), redacted_text)

        if events:
            logger.debug("text_redacted", event_count=len(events))

        return redacted_text, events

    def redact_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively redact all string values in a dict.
        """
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self.redact_dict(value)
            elif isinstance(value, list):
                redacted_list = []
                for item in value:
                    if isinstance(item, dict):
                        redacted_list.append(self.redact_dict(item))
                    elif isinstance(item, str):
                        redacted, _ = self.redact(item)
                        redacted_list.append(redacted)
                    else:
                        redacted_list.append(item)
                result[key] = redacted_list
            elif isinstance(value, str):
                redacted_str, _ = self.redact(value)
                result[key] = redacted_str
            else:
                result[key] = value

        return result
