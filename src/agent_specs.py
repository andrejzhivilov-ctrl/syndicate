"""Operator-approved regulations of the directors (config/agent_specs/<agent>.json).

Token economy: every chat turn carries only the short ``core`` of the agent's
regulation; a full section is added only when the message touches its keywords,
and the whole document is readable with ``/spec`` without any model call.

The specs describe the target design. Each lists its integrations with an honest
``status``; an agent must not claim a report, a feed or a broker that is still
``not_connected``.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)

SPEC_DIR = Path(__file__).resolve().parents[1] / "config" / "agent_specs"
SPEC_REFERENCE_CHARS = 1500
SPEC_SECTION_LIMIT = 2
_STATUS = {"connected": "✅ підключено", "not_connected": "⛔ ще не підключено"}


@lru_cache(maxsize=None)
def load_spec(agent_id: str) -> Optional[Dict[str, Any]]:
    """The agent's regulation, or None when it has none (or the file is broken)."""
    path = SPEC_DIR / f"{agent_id}.json"
    if not agent_id.isalnum() or not path.is_file():
        return None
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        logger.warning("agent_spec_unreadable", agent=agent_id, error_type=type(exc).__name__)
        return None
    return spec if isinstance(spec, dict) and spec.get("agent") == agent_id else None


def _missing(spec: Dict[str, Any]) -> List[str]:
    return [i["name"] for i in spec.get("integrations", []) if i.get("status") != "connected"]


def spec_core(agent_id: str) -> Optional[str]:
    """Short regulation for the system prompt, with what is not connected yet."""
    spec = load_spec(agent_id)
    if spec is None:
        return None
    missing = _missing(spec)
    note = ("\nЩе не підключено (не стверджуй, що це працює; кажи, що це заплановано): "
            + "; ".join(missing) + ".") if missing else ""
    return spec["core"] + note


def spec_reference(agent_id: str, text: str) -> Optional[str]:
    """Up to two regulation sections whose keywords the message touches."""
    spec = load_spec(agent_id)
    if spec is None or not isinstance(text, str):
        return None
    lowered = text.lower()
    scored = []
    for section in spec.get("sections", []):
        score = sum(1 for word in section.get("keywords", []) if word in lowered)
        if score:
            scored.append((score, section))
    if not scored:
        return None
    scored.sort(key=lambda pair: -pair[0])
    parts = [f"## {s['title']}\n{s['text']}" for _, s in scored[:SPEC_SECTION_LIMIT]]
    return "\n\n".join(parts)[:SPEC_REFERENCE_CHARS]


def spec_reply(agent_id: str, arg: str) -> Dict[str, Any]:
    """/spec, /spec <section>, /spec розклад, /spec інтеграції — no model call."""
    base = {"agent": agent_id, "mode": "spec"}
    spec = load_spec(agent_id)
    if spec is None:
        return {**base, "status": "unavailable", "reason": "no_spec",
                "response": "Для цього агента регламент ще не затверджено."}
    sections = {s["id"]: s for s in spec.get("sections", [])}
    key = arg.strip().lower()
    if key in sections:
        section = sections[key]
        return {**base, "status": "completed", "response": f"{section['title']}\n\n{section['text']}"}
    if key in {"розклад", "schedule"}:
        lines = [f"Розклад (Europe/Kyiv, cron) — {spec['title']}:"]
        lines += [f"• {job['cron']} — {job['what']}" for job in spec.get("schedule", [])]
        if "Розклад" in " ".join(_missing(spec)):
            lines.append("Автоматичний запуск за розкладом ще не ввімкнено.")
        return {**base, "status": "completed", "response": "\n".join(lines)}
    if key in {"інтеграції", "integrations"}:
        lines = ["Підключення:"] + [f"• {i['name']} — {_STATUS.get(i.get('status'), i.get('status'))}"
                                    for i in spec.get("integrations", [])]
        return {**base, "status": "completed", "response": "\n".join(lines)}
    lines = [spec["title"], "", "Розділи (/spec <id>):"]
    lines += [f"• {sid} — {s['title']}" for sid, s in sections.items()]
    lines += ["• розклад — графік звітів", "• інтеграції — що підключено, а що ні"]
    if key:
        lines.insert(0, f"Розділу «{arg.strip()}» немає.\n")
    return {**base, "status": "completed", "response": "\n".join(lines)}
