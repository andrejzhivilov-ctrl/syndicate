"""Sensitive skills wait for Andrii's buttons; ordinary ones the agent makes itself (16.11.2026).

Andrii: the agent creates its own skills; a skill about medicines, preparations and doses, tests,
money or security goes to him first, as two buttons, and the decision lands in Eva's report.
The agent proposes such a skill by putting one marker line in its reply:

    <<СКІЛ: назва | навіщо>>

The bot sends the reply without the marker and one message per proposal with «Погодити» /
«Відхилити». The press comes back as a callback; the agent gets Andrii's decision as a turn and
creates the skill only after «Погодити». Every proposal and decision is kept in
``EVA_DATA_DIR/skills/decisions.jsonl`` for Eva's report.
"""
from __future__ import annotations

import json
import re
import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.data_paths import ensure_dir

MARKER = re.compile(r"<<\s*СКІЛ\s*:\s*([^|>]{1,80}?)\s*(?:\|\s*([^>]{0,300}?))?\s*>>")
PREFIX = "skill"
APPROVE, REJECT = "ok", "no"
MAX_PER_REPLY = 3


def _log_path():
    return ensure_dir("skills") / "decisions.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _append(entry: Dict[str, Any]) -> None:
    with _log_path().open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")


def entries() -> List[Dict[str, Any]]:
    path = _log_path()
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def split(agent: str, reply: str) -> Tuple[str, List[Dict[str, str]]]:
    """The reply without markers, and the proposals it carried (each recorded with a short id)."""
    proposals = []
    for found in MARKER.finditer(reply):
        if len(proposals) == MAX_PER_REPLY:
            break
        proposal = {"id": secrets.token_hex(4), "agent": agent, "name": found.group(1).strip(),
                    "why": (found.group(2) or "").strip()}
        _append({"at": _now(), "event": "proposed", **proposal})
        proposals.append(proposal)
    clean = MARKER.sub("", reply).strip()
    return clean, proposals


def question(proposal: Dict[str, str]) -> Tuple[str, Dict[str, Any]]:
    """The message and its two buttons; callback data stays under Telegram's 64 bytes."""
    why = f"\nНавіщо: {proposal['why']}" if proposal["why"] else ""
    text = f"🧩 Новий скіл на погодження: «{proposal['name']}»{why}"
    markup = {"inline_keyboard": [[
        {"text": "✅ Погодити", "callback_data": f"{PREFIX}:{APPROVE}:{proposal['id']}"},
        {"text": "❌ Відхилити", "callback_data": f"{PREFIX}:{REJECT}:{proposal['id']}"},
    ]]}
    return text, markup


def decide(agent: str, data: str) -> Optional[Dict[str, Any]]:
    """A button press: the decision recorded, and the turn the agent gets; None if not ours."""
    parts = data.split(":")
    if len(parts) != 3 or parts[0] != PREFIX or parts[1] not in (APPROVE, REJECT):
        return None
    proposal = next((e for e in entries() if e.get("event") == "proposed" and e.get("id") == parts[2]
                     and e.get("agent") == agent), None)
    if proposal is None:
        return {"status": "unknown", "notice": "⚠️ Цієї пропозиції вже немає."}
    if any(e.get("event") == "decided" and e.get("id") == parts[2] for e in entries()):
        return {"status": "already", "notice": "Рішення по цьому скілу вже є."}
    approved = parts[1] == APPROVE
    _append({"at": _now(), "event": "decided", "id": parts[2], "agent": agent, "name": proposal["name"],
             "approved": approved})
    turn = (f"Андрій погодив скіл «{proposal['name']}». Створи його зараз і коротко скажи, що в ньому."
            if approved else f"Андрій відхилив скіл «{proposal['name']}». Не створюй його.")
    notice = f"{'✅ Погоджено' if approved else '❌ Відхилено'}: «{proposal['name']}»"
    return {"status": "decided", "approved": approved, "turn": turn, "notice": notice}
