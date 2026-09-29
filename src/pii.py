from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class RedactionEvent:
    pattern_name: str
    original_match: str


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
        "iban": re.compile(r"\b(UA\d{2})[A-Z0-9]{19}([A-Z0-9]{4})\b"),
        "api_key_sk_ant": re.compile(r"\bsk-ant-[A-Za-z0-9_-]+\b"),
        "api_key_ghp": re.compile(r"\bghp_[A-Za-z0-9]+\b"),
        "api_key_gsk": re.compile(r"\bgsk_[A-Za-z0-9]+\b"),
        "ipv4": re.compile(r"\b(\d{1,3}\.\d{1,3}\.)(\d{1,3}\.\d{1,3})\b"),
    }

    def redact(self, text: str) -> Tuple[str, List[RedactionEvent]]:
        """
        Apply all patterns, return redacted text + list of what was redacted (for audit).
        """
        redacted_text = text
        events = []
        
        if not isinstance(text, str):
            return text, events
            
        def create_replacer(pattern_name: str):
            def replacer(match: re.Match) -> str:
                original = match.group(0)
                events.append(RedactionEvent(pattern_name=pattern_name, original_match=original))
                
                if pattern_name == "ukrainian_phone":
                    return f"{match.group(1)}***{match.group(4)}"
                elif pattern_name == "intl_phone":
                    return f"{match.group(1)}***{match.group(4)}"
                elif pattern_name == "email":
                    return f"{match.group(1)}***@{match.group(3)}"
                elif pattern_name == "credit_card":
                    return f"****{match.group(1)}"
                elif pattern_name == "ukrainian_ipn":
                    return f"IPN:****{match.group(2)}"
                elif pattern_name == "passport":
                    return f"{match.group(1)}******"
                elif pattern_name == "iban":
                    return f"{match.group(1)}**...{match.group(2)}"
                elif pattern_name in ("api_key_sk_ant", "api_key_ghp", "api_key_gsk"):
                    return "[REDACTED_KEY]"
                elif pattern_name == "ipv4":
                    return f"{match.group(1)}***.***"
                    
                return "***"
            return replacer
            
        for name, pattern in self.PATTERNS.items():
            redacted_text = pattern.sub(create_replacer(name), redacted_text)
            
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
