"""Agent jobs the schedule runs: reminders and check-ins without a model, and a weekly learning inbox.

Called by ``src/agent_schedule.py`` (n8n used to call it until stage 6). A reminder or check-in is
fixed text sent by the agent's own bot to the owner; no model is called, so it costs no tokens.
Learning items are accepted only from sources Andrii connected in ``src/learning_sources.json``
(src is mounted into syndicate-agent) and land in a per-week file the agent reads with its
``learning_inbox`` tool.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
from urllib.parse import urlparse

import structlog

from src.data_paths import ensure_dir

logger = structlog.get_logger(__name__)

SOURCES_PATH = Path(__file__).with_name("learning_sources.json")
#: Agents with scheduled jobs, and the kinds each may run.
AGENT_KINDS: Dict[str, frozenset] = {
    "trainer": frozenset({"reminder", "checkin", "learning", "morning_brief", "reflection"}),
}
#: Each agent's folder in Obsidian; the morning brief is a note Andrii edits there.
OBSIDIAN_DIRS = {"trainer": "Health_Coach"}
PLAN_NOTE = "План_дня.md"
MAX_TEXT = 1000
#: Telegram allows 4096 characters; the brief stays under it.
MAX_BRIEF = 3500
REFLECTION_PROMPT = (
    "Тижнева саморефлексія. Прочитай learning_inbox (нове з підключених джерел за тиждень) і свою пам'ять "
    "про Андрія. Коротко: 1) що нового й достовірного, з джерелом; 2) що це змінює в його програмі, "
    "харчуванні чи відновленні; 3) що запам'ятати і який скіл запропонувати Андрію на погодження. "
    "Нічого не вигадуй: якщо нового немає або даних про прогрес бракує, так і скажи."
)
MAX_ITEMS = 50
MAX_ITEM_TEXT = 4000
INBOX_LIMIT = 10


def connected_sources(agent: str, path: Path = SOURCES_PATH) -> List[str]:
    """Hosts Andrii connected for this agent; an empty list accepts nothing."""
    try:
        hosts = json.loads(path.read_text(encoding="utf-8")).get(agent, [])
    except (OSError, ValueError):
        return []
    return [str(host).lower() for host in hosts if isinstance(host, str)]


def _host_allowed(url: str, hosts: List[str]) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return bool(host) and any(host == allowed or host.endswith("." + allowed) for allowed in hosts)


def _week_file(agent: str, now: datetime) -> Path:
    year, week, _ = now.isocalendar()
    return ensure_dir("learning") / agent / f"{year}-W{week:02d}.jsonl"


def _clean_item(raw: Any, hosts: List[str]) -> Optional[Dict[str, str]]:
    if not isinstance(raw, Mapping):
        return None
    url, text = str(raw.get("url") or ""), str(raw.get("text") or "").strip()
    if not text or not _host_allowed(url, hosts):
        return None
    return {"url": url, "title": str(raw.get("title") or "")[:200], "text": text[:MAX_ITEM_TEXT]}


def accept_learning(agent: str, items: Any, *, now: Optional[datetime] = None,
                    sources_path: Path = SOURCES_PATH) -> Dict[str, Any]:
    """Keep items from connected sources only; report what was refused, never guess."""
    hosts = connected_sources(agent, sources_path)
    raw = items if isinstance(items, list) else []
    kept = [item for item in (_clean_item(entry, hosts) for entry in raw[:MAX_ITEMS]) if item]
    stamp = (now or datetime.now(timezone.utc)).isoformat(timespec="seconds")
    if kept:
        path = _week_file(agent, now or datetime.now(timezone.utc))
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            for item in kept:
                stream.write(json.dumps({**item, "received_at": stamp}, ensure_ascii=False) + "\n")
    refused = len(raw) - len(kept)
    reason = None if hosts else "no_source_connected"
    return {"status": "ok" if kept else "unavailable", "kept": len(kept), "refused": refused,
            **({"reason": reason} if reason and not kept else {})}


def learning_inbox(agent: str) -> List[Dict[str, str]]:
    """Newest items of the two latest weeks; text from outside is reference, not instruction."""
    folder = ensure_dir("learning") / agent
    files = sorted(folder.glob("*.jsonl"), reverse=True)[:2] if folder.is_dir() else []
    items: List[Dict[str, str]] = []
    for path in files:
        for line in reversed(path.read_text(encoding="utf-8").splitlines()):
            try:
                items.append(json.loads(line))
            except ValueError:
                continue
    return items[:INBOX_LIMIT]


def plan_note(agent: str) -> Optional[str]:
    """The day plan Andrii keeps in Obsidian, or ``None``: a missing plan is never invented."""
    from src.obsidian_notes import vault_dir_from_env

    root = vault_dir_from_env()
    if root is None or agent not in OBSIDIAN_DIRS:
        return None
    try:
        text = (root / OBSIDIAN_DIRS[agent] / PLAN_NOTE).read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text[:MAX_BRIEF] or None


async def _deliver(agent: str, text: str, gateway: Any, missing: str) -> Dict[str, Any]:
    owner = await gateway.owner_user_id() if text and gateway else None
    sent = bool(owner) and await gateway.send(agent, owner, text)
    return {"status": "ok" if sent else "unavailable", "sent": sent,
            **({} if sent else {"reason": missing if not text else "telegram_unavailable"})}


async def _reflection(agent: str, gateway: Any) -> Dict[str, Any]:
    """The weekly self-review is one Hermes turn; without Hermes it is reported, not faked."""
    from src import hermes_gateway

    owner = await gateway.owner_user_id() if gateway else None
    if agent not in hermes_gateway.enabled_agents() or not owner:
        return {"status": "unavailable", "sent": False, "reason": "hermes_not_enabled" if owner else "no_owner"}
    reply = await hermes_gateway.hermes_chat(agent, REFLECTION_PROMPT, owner)
    return await _deliver(agent, str(reply.get("response") or ""), gateway, "reflection_failed")


async def handle(agent: str, payload: Any, gateway: Any) -> Dict[str, Any]:
    """One job run: text to the owner, the day plan, the weekly review, or learning items."""
    kind = payload.get("kind") if isinstance(payload, Mapping) else None
    if kind not in AGENT_KINDS.get(agent, frozenset()):
        return {"status": "error", "error": "unknown_kind", "available_kinds": sorted(AGENT_KINDS.get(agent, ()))}
    if kind == "learning":
        result = accept_learning(agent, payload.get("items"))
    elif kind == "morning_brief":
        result = await _deliver(agent, plan_note(agent) or "", gateway, "plan_note_missing")
    elif kind == "reflection":
        result = await _reflection(agent, gateway)
    else:
        result = await _deliver(agent, str(payload.get("text") or "").strip()[:MAX_TEXT], gateway, "empty_text")
    return result
