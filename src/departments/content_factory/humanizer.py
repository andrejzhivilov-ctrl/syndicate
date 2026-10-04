"""
Humanizer — detects and removes "AI voice" before anything is published.

Deterministic: phrase lists (uk/ru/en), structural tells (uniform sentence
length, em-dash overuse, tidy triplets, filler openers), an AI-ness score
0-100 and a conservative scrubber that only deletes/replaces safe patterns —
it never invents facts or rewrites meaning.
"""

from __future__ import annotations

import re
import statistics
from typing import Any, Dict, List, Tuple

CLICHES = [
    # uk
    "в сучасному світі", "у сучасному світі", "не секрет, що", "давайте розберемося", "давай розберемося",
    "підсумовуючи", "насамкінець", "варто зазначити", "важливо відзначити", "у цій статті ми розглянемо",
    "світ штучного інтелекту", "революційний", "game-changer", "відкрийте для себе",
    # ru
    "в современном мире", "не секрет, что", "давайте разберёмся", "давайте разберемся", "подводя итог",
    "стоит отметить", "важно отметить", "в этой статье мы рассмотрим", "революционный",
    # en
    "in today's fast-paced world", "it's important to note", "it is important to note", "in conclusion",
    "delve into", "dive into", "testament to", "unlock the power", "game-changing", "let's explore",
    "navigate the landscape", "tapestry", "in the realm of",
]
REPLACEMENTS: List[Tuple[str, str]] = [
    (r"\bдавайте розберемося,?\s*", ""), (r"\bдавай розберемося,?\s*", ""),
    (r"\bварто зазначити,? що\s*", ""), (r"\bважливо відзначити,? що\s*", ""),
    (r"\bне секрет,? що\s*", ""), (r"\bстоит отметить,? что\s*", ""), (r"\bважно отметить,? что\s*", ""),
    (r"\bit(?:'s| is) important to note that\s*", ""), (r"\bin conclusion,?\s*", ""),
    (r"\bin today's fast-paced world,?\s*", ""), (r"\bdelve into\b", "look at"), (r"\bdive into\b", "look at"),
    (r"\bв сучасному світі,?\s*", ""), (r"\bу сучасному світі,?\s*", ""), (r"\bв современном мире,?\s*", ""),
]


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text) if s.strip()]


class Humanizer:
    def analyze(self, text: str) -> Dict[str, Any]:
        low = text.lower()
        flagged = [c for c in CLICHES if c in low]
        sents = _sentences(text)
        lens = [len(s.split()) for s in sents]
        burstiness = (statistics.pstdev(lens) / statistics.mean(lens)) if len(lens) >= 4 and statistics.mean(lens) else 1.0
        words = max(1, len(text.split()))
        em_dash_rate = (text.count("—") + text.count(" – ")) / words * 100
        triplets = len(re.findall(r"[^,.;]+,\s+[^,.;]+,\s+(?:і|та|и|and)\s+[^,.;]+", text))
        opener_repeats = 0
        if len(sents) >= 4:
            firsts = [s.split()[0].lower() for s in sents if s.split()]
            opener_repeats = max((firsts.count(w) for w in set(firsts)), default=0)

        score = 0.0
        score += min(len(flagged) * 12, 50)
        score += 15 if burstiness < 0.35 else 0
        score += min(max(em_dash_rate - 0.8, 0) * 6, 15)
        score += min(triplets * 4, 12)
        score += 8 if opener_repeats >= 3 else 0
        score = min(round(score, 1), 100.0)

        return {
            "ai_score": score,
            "verdict": "human" if score < 25 else ("mixed" if score < 50 else "robotic"),
            "flagged_phrases": flagged,
            "burstiness": round(burstiness, 3),
            "em_dash_per_100_words": round(em_dash_rate, 2),
            "triplet_lists": triplets,
            "repeated_openers": opener_repeats,
            "checklist": [
                "Є конкретика (цифра, ім'я, приклад) у перших двох реченнях?",
                "Чергуються короткі та довгі речення?",
                "Немає вступів-заповнювачів і підсумкових банальностей?",
                "Текст звучить так, як ти сказав би це вголос?",
            ],
        }

    def scrub(self, text: str) -> Dict[str, Any]:
        out = text
        for pattern, repl in REPLACEMENTS:
            out = re.sub(pattern, repl, out, flags=re.I)
        out = out.replace(" — ", ", ").replace("—", "-")
        out = re.sub(r"[ \t]{2,}", " ", out)
        out = re.sub(r"\n{3,}", "\n\n", out).strip()
        out = re.sub(r"(^|[.!?]\s+)([a-zа-яіїєґ])", lambda m: m.group(1) + m.group(2).upper(), out)
        return {
            "text": out,
            "before": self.analyze(text)["ai_score"],
            "after": self.analyze(out)["ai_score"],
            "changed": out != text,
        }

    def humanize(self, text: str) -> Dict[str, Any]:
        """Analyze and scrub AI clichés from text."""
        analysis = self.analyze(text)
        scrubbed = self.scrub(text)
        return {
            "original_text": text,
            "scrubbed_text": scrubbed["text"],
            "original_robotic_score": analysis["ai_score"],
            "scrubbed_score": scrubbed["after"],
            "clichés_detected": [{"cliché": c} for c in analysis["flagged_phrases"]],
            "verdict": analysis["verdict"],
            "changed": scrubbed["changed"],
        }

