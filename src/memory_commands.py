"""
Semantic memory commands: «запам'ятай», «онови про мене», «забудь», «запиши думку».

Parsing is deterministic (no LLM). Each command is routed to the agent that owns
the topic, so memory lands in the right dossier.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.agents.eva_memory_policy import EvaMemoryPolicy, MemoryDisposition
from src.vault_md import MarkdownVault

_MEMORY_POLICY = EvaMemoryPolicy()

_APOS = "['’ʼ`]"
_PATTERNS = [
    ("remember", re.compile(rf"^\s*(?:запам{_APOS}?ятай|запомни|remember)\s*[:\-—]?\s*(?P<t>.+)$", re.I | re.S)),
    ("thought", re.compile(r"^\s*(?:запиши\s+думку|запиши\s+мысль|note)\s*[:\-—]?\s*(?P<t>.+)$", re.I | re.S)),
    (
        "update",
        re.compile(
            r"^\s*(?:онови|обнови|update)(?:\s+(?:інформацію|информацию))?"
            r"(?:\s+(?:про\s+мене|о\s+мне|about\s+me))?\s*[:\-—]?\s*(?P<t>.+)$",
            re.I | re.S,
        ),
    ),
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


def _policy_result(cmd: MemoryCommand, vault: MarkdownVault) -> Optional[Dict[str, Any]]:
    decision = _MEMORY_POLICY.evaluate(cmd.text, explicit_save_request=True)
    if decision.disposition is MemoryDisposition.ARCHIVE:
        return None
    if decision.disposition is MemoryDisposition.REJECT:
        return {
            "agent": cmd.target_agent,
            "status": "refused",
            "reason_code": decision.reason_code,
            "active_memory_written": False,
            "draft_stored": False,
        }

    if decision.reason_code == "overlong_item_review_required":
        return {
            "agent": cmd.target_agent,
            "status": "review_required",
            "reason_code": decision.reason_code,
            "active_memory_written": False,
            "draft_stored": False,
        }
    draft = vault.add_memory_review_draft(cmd.target_agent, cmd.text, decision.reason_code)
    return {
        "agent": cmd.target_agent,
        **draft,
        "reason_code": decision.reason_code,
        "active_memory_written": False,
        "draft_stored": draft.get("status") == "review_required",
    }


def _execute_write_command(cmd: MemoryCommand, vault: MarkdownVault) -> Dict[str, Any]:
    policy_result = _policy_result(cmd, vault)
    if policy_result is not None:
        return policy_result

    agent = cmd.target_agent
    if cmd.kind == "remember":
        return {
            "agent": agent,
            **vault.remember(agent, cmd.text, source="explicit_memory_request", confirmed=True),
        }
    if cmd.kind == "thought":
        rel = "raw/thoughts.md"
        previous = vault.read(rel) if vault.exists(rel) else "# Thoughts\n\n"
        normalized = " ".join(cmd.text.split())
        metadata = vault._memory_metadata("explicit_thought_request", True)
        vault.write(rel, previous + f"- {normalized} <!-- {metadata} -->\n", allow_memory_write=True)
        return {"agent": "eva", "status": "thought_saved"}

    # "про X: нове значення" -> query is the part before ':' when present
    if ":" in cmd.text:
        query, value = (part.strip() for part in cmd.text.split(":", 1))
    else:
        query, value = cmd.text, cmd.text
    return {
        "agent": agent,
        **vault.update_fact(
            agent,
            query,
            value,
            confirmed=True,
            source="explicit_update_request",
        ),
    }


def _execute_forget_command(
    cmd: MemoryCommand, vault: MarkdownVault, operator_confirmed_forget: bool
) -> Dict[str, Any]:
    if operator_confirmed_forget is not True:
        return {"agent": cmd.target_agent, "status": "confirmation_required", "stored": False}
    return {
        "agent": cmd.target_agent,
        **vault.forget(
            cmd.target_agent,
            cmd.text,
            confirmed=True,
            source="explicit_forget_confirmation",
        ),
    }


def execute_command(
    cmd: MemoryCommand,
    vault: MarkdownVault,
    operator_confirmed_forget: bool = False,
) -> Dict[str, Any]:
    """Execute a parsed command only after the privacy and confirmation gates."""
    if EvaMemoryPolicy.contains_secret_like_value(cmd.text):
        return {
            "agent": cmd.target_agent,
            "status": "refused",
            "reason_code": "secret_like_content",
            "stored": False,
        }
    if cmd.kind in {"remember", "thought", "update"}:
        return _execute_write_command(cmd, vault)
    if cmd.kind == "forget":
        return _execute_forget_command(cmd, vault, operator_confirmed_forget)
    if cmd.kind == "about_me":
        return {"agent": "eva", "status": "ok", "facts": vault._load_facts("eva")}
    return {"status": "unknown_command"}
