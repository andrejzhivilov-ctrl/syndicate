"""
SYNDIKAT Compliance — Intellectual Property & Community Safety Sentinel.
Vetos copyright violations (Disney, Marvel, Nike, Apple in POD designs)
and scans copy against social platform shadowban triggers.
"""

from __future__ import annotations

import re
from typing import List, Tuple
import structlog

logger = structlog.get_logger(__name__)


class PolicySentinel:
    """Enforces zero-trust brand IP safety and community guideline compliance."""

    # High-risk registered trademarks strictly prohibited in automated POD
    PROTECTED_TRADEMARKS = [
        "disney", "marvel", "star wars", "mickey", "avengers", "spiderman",
        "nike", "just do it", "adidas", "gucci", "louis vuitton",
        "apple", "iphone", "pokemon", "nintendo", "lego", "tesla"
    ]

    # Stop words that trigger algorithm suppression or shadowbans on TikTok/X/Meta
    SHADOWBAN_STOPWORDS = [
        "dm for details", "get rich quick", "100% guaranteed profit",
        "crypto giveaway", "free money", "hack account", "buy followers"
    ]

    def check_design_compliance(
        self, design_reference: str, tags: List[str]
    ) -> Tuple[bool, List[str]]:
        """Verify that merchandise artwork does not infringe on protected IP.

        ``design_reference`` is the artwork path / title / description — the
        parameter used to be called ``prompt``, which made the only caller pass
        a filesystem path and look like a bug.
        """
        violations = []
        combined_text = f"{design_reference.lower()} {' '.join(t.lower() for t in tags)}"
        # Sanitize delimiters so underscores/slashes/dots are treated as word separators
        sanitized = re.sub(r"[_\-/.\\+:]+", " ", combined_text)

        for brand in self.PROTECTED_TRADEMARKS:
            # Word boundary matching
            if re.search(r"\b" + re.escape(brand) + r"\b", sanitized):
                violations.append(f"Trademark IP Violation: Protected brand '{brand}' detected.")

        allowed = len(violations) == 0
        if not allowed:
            logger.warning("design_compliance_veto", violations=violations)
        return allowed, violations

    def check_copy_compliance(self, text: str) -> Tuple[bool, List[str]]:
        """Verify that marketing copy will not trigger social media shadowbans."""
        warnings = []
        lowered = text.lower()

        for stopword in self.SHADOWBAN_STOPWORDS:
            if stopword in lowered:
                warnings.append(f"Platform Safety Warning: '{stopword}' risks algorithmic penalty.")

        is_safe = len(warnings) == 0
        return is_safe, warnings
