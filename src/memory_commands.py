"""
Semantic memory commands: «запам'ятай», «онови про мене», «забудь», «запиши думку».

Parsing is deterministic (no LLM). Each command is routed to the agent that owns
the topic, so memory lands in the right dossier.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.vault_md import MarkdownVault

_APOS = "['’ʼ`]"
_PATTERNS = [
    ("remember", re.compile(rf"^\s*(?:запам{_APOS}?ятай|запомни|remember)\s*[:\-—]?\s*(?P<t>.+)$", re.I | re.S)),
    ("thought", re.compile(r"^\s*(?:запиши\s+думку|запиши\s+мысль|note)\s*[:\-—]?\s*(?P<t>.+)$", re.I | re.S)),
    ("update", re.compile(r"^\s*(?:онови|обнови|update)(?:\s+(?:інформацію|информацию))?\s*(?:про|о|about)?\s*(?P<t>.+)$", re.I | re.S)),
    ("forget", re.compile(r"^\s*(?:забудь|видали|удали|forget)\s*[:\-—]?\s*(?P<t>.+)$", re.I | re.S)),
    ("about_me", re.compile(r"^\s*(?:про\s+мене|обо\s+мне|about\s+me)\s*[?!.]*\s*$", re.I)),
]

_TOPIC_ROUTES = [
    ("doc", ("здоров", "сон", "трен", "вага", "вес", "харчув", "питан", "hrv", "пульс", "аналіз", "анализ", "ліки", "лекарств")),
    ("fin", ("бюджет", "портфел", "податок", "налог", "рахунок", "счет", "витрат", "расход", "інвестиц", "борг", "долг")),
    ("sam", ("торг", "ордер", "btc", "eth", "ризик", "стоп", "трейд", "позиці", "позици")),
    ("kira", ("англійськ", "английск", "урок", "навчан", "обучен", "програм", "код", "history", "історі", "нейромереж")),
    ("marshal", ("сервер", "ssh", "порт", "docker", "n8n", "контент", "завод", "публікац")),
    ("architect", ("архітектур", "архитектур", "схема", "api", "міграц", "workflow", "репозитор")),
]


@dataclass
class MemoryCommand:
    kind: str                # remember | thought | update | forget | about_me
    text: str
    target_agent: str
    raw: str


def detect_agent(text: str) -> str:
    low = text.lower()
    best, best_hits = "eva", 0
    for agent, kws in _TOPIC_ROUTES:
        hits = sum(1 for k in kws if k in low)
        if hits > best_hits:
            best, best_hits = agent, hits
    return best


def parse_command(message: str) -> Optional[MemoryCommand]:
    for kind, rx in _PATTERNS:
        m = rx.match(message or "")
        if m:
            text = (m.groupdict().get("t") or "").strip()
            if kind != "about_me" and not text:
                return None
            return MemoryCommand(kind, text, detect_agent(text), message)
    return None


def execute_command(cmd: MemoryCommand, vault: MarkdownVault, operator_confirmed_forget: bool = True) -> Dict[str, Any]:
    agent = cmd.target_agent
    if cmd.kind == "remember":
        return {"agent": agent, **vault.remember(agent, cmd.text)}
    if cmd.kind == "thought":
        rel = "raw/thoughts.md"
        prev = vault.read(rel) if vault.exists(rel) else "# Thoughts\n\n"
        vault.write(rel, prev + f"- {cmd.text}\n")
        return {"agent": "eva", "status": "thought_saved"}
    if cmd.kind == "update":
        # "про X: нове значення" -> query is the part before ':' when present
        if ":" in cmd.text:
            query, value = (s.strip() for s in cmd.text.split(":", 1))
        else:
            query, value = cmd.text, cmd.text
        return {"agent": agent, **vault.update_fact(agent, query, value)}
    if cmd.kind == "forget":
        if not operator_confirmed_forget:
            return {"agent": agent, "status": "confirmation_required"}
        return {"agent": agent, **vault.forget(agent, cmd.text)}
    if cmd.kind == "about_me":
        facts = vault._load_facts("eva")
        return {"agent": "eva", "status": "ok", "facts": facts}
    return {"status": "unknown_command"}
