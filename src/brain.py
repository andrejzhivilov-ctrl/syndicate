"""The Second Brain records every move of every agent (Andrii, 20.11.2026).

Andrii's rule: every action, everything created, written or thought by any agent is kept in the
Second Brain (the Obsidian vault on the server, synced to his PC and phone), so the knowledge grows
like new neurons and nothing is lost; once a month Eva clears the rubbish (src/brain_audit.py).

Every move goes to two places:

- ``<agent folder>/Журнал/Дії/<YYYY-MM-DD>.md`` in the vault: one line per move, Kyiv time, with
  ``[[links]]`` to the notes it touched, so Obsidian's graph and search connect them;
- ``<EVA_DATA_DIR>/brain/<agent>/<YYYY-MM-DD>.jsonl``: the same move with its full detail, for code.

The four doors every move passes through write here: a chat turn and a task in the orchestrator,
a gateway tool call of a Hermes agent, a scheduled job. Secrets and coordinates are removed before
anything is written (Andrii is military: no location leaves without his word). Writing never takes an
agent down: a failure is logged and the move goes on.
"""
from __future__ import annotations

import functools
import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional
from zoneinfo import ZoneInfo

import structlog

from src.data_paths import data_root, ensure_dir

logger = structlog.get_logger(__name__)

KYIV = ZoneInfo("Europe/Kyiv")
#: Each agent's own folder in the vault (Alex still runs under the id ``trainer``).
FOLDERS: Dict[str, str] = {"eva": "Єва", "trainer": "Health_Coach", "kira": "Кіра", "fin": "Фін", "sam": "Сем",
                           "tyler": "Тайлер", "marshal": "Маршал", "kodex": "Кодекс", "alice": "Аліса",
                           "claude": "Claude", "codex": "Codex"}
JOURNAL = ("Журнал", "Дії")
#: The line in the vault stays readable; the full text is in the JSONL.
LINE_CHARS = 600
DETAIL_CHARS = 20_000
KINDS = ("chat", "task", "tool", "job", "note", "strategy", "decision", "thought")
_LOCK = threading.Lock()
_WIKILINK = re.compile(r"\[\[([^\]|#]+)")


def _patterns():
    from src.agents.eva_memory_policy import _COORDINATE_PAIR, _SECRET_PATTERNS

    return (*_SECRET_PATTERNS, _COORDINATE_PAIR)


def scrub(text: Any) -> str:
    """Text safe to keep: secrets and coordinates are replaced, never stored."""
    value = text if isinstance(text, str) else json.dumps(text, ensure_ascii=False, default=str)
    for pattern in _patterns():
        value = pattern.sub("[прибрано]", value)
    return value


def folder_for(agent: str) -> str:
    return FOLDERS.get(agent, agent if re.fullmatch(r"[\w-]{2,32}", agent or "") else "Інші")


def _vault() -> Optional[Path]:
    from src.obsidian_notes import vault_dir_from_env

    return vault_dir_from_env()


def _one_line(text: str, limit: int) -> str:
    flat = re.sub(r"\s+", " ", text).strip()
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def _links(paths: Iterable[str]) -> str:
    names = []
    for path in paths:
        stem = Path(str(path)).with_suffix("").as_posix()
        if stem and stem not in names:
            names.append(stem)
    return " ".join(f"[[{name}]]" for name in names[:8])


def record(agent: str, kind: str, summary: str, detail: Any = None, links: Iterable[str] = (),
           now: Optional[datetime] = None) -> bool:
    """Keep one move; True when it reached the vault, False when only the JSONL (or nothing) has it."""
    try:
        return _record(agent or "unknown", kind if kind in KINDS else "task", summary, detail, list(links), now)
    except Exception as exc:  # noqa: BLE001 - the Second Brain must never take an agent down
        logger.warning("brain_record_failed", agent=agent, kind=kind, error=type(exc).__name__)
        return False


def _record(agent: str, kind: str, summary: str, detail: Any, links: list, now: Optional[datetime]) -> bool:
    moment = (now or datetime.now(timezone.utc)).astimezone(KYIV)
    day = moment.strftime("%Y-%m-%d")
    text = scrub(summary or "")
    full = scrub(detail)[:DETAIL_CHARS] if detail is not None else ""
    links += _WIKILINK.findall(full)
    entry = {"at": moment.isoformat(timespec="seconds"), "agent": agent, "kind": kind, "summary": text,
             "detail": full, "links": links}
    with _LOCK:
        if data_root() is not None:  # without EVA_DATA_DIR (a test, a laptop) nothing is written next to the code
            jsonl = ensure_dir("brain") / agent / f"{day}.jsonl"
            jsonl.parent.mkdir(parents=True, exist_ok=True)
            with jsonl.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
        root = _vault()
        if root is None:
            return False
        note = root / folder_for(agent) / Path(*JOURNAL) / f"{day}.md"
        note.parent.mkdir(parents=True, exist_ok=True)
        if not note.exists():
            note.write_text(f"---\nagent: {agent}\ndate: {day}\ntags: [журнал, дії, {folder_for(agent)}]\n"
                            f"generated: brain\n---\n\n# {folder_for(agent)}: дії за {day}\n\n", encoding="utf-8")
        line = f"- {moment.strftime('%H:%M')} **{kind}** {_one_line(text, LINE_CHARS)}"
        if full and full != text:
            line += f" — {_one_line(full, LINE_CHARS)}"
        if links:
            line += f" {_links(links)}"
        with note.open("a", encoding="utf-8") as stream:
            stream.write(line + "\n")
    return True


def _safe(door: Callable[..., None]) -> Callable[..., None]:
    """A door never raises into the agent it records."""
    @functools.wraps(door)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            door(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            logger.warning("brain_door_failed", door=door.__name__, error=type(exc).__name__)
    return wrapper


def _short(value: Any, limit: int = 300) -> str:
    return _one_line(scrub(value), limit)


@_safe
def chat(agent: str, text: Optional[str], result: Optional[Mapping[str, Any]]) -> None:
    reply = (result or {}).get("reply") or (result or {}).get("response") or (result or {}).get("error") or ""
    record(agent, "chat", f"Андрій: {_short(text or '', 400)}", f"Відповідь: {scrub(reply)}")


@_safe
def task(agent: Optional[str], task_type: str, payload: Mapping[str, Any], status: str, result: Any) -> None:
    record(agent or "eva", "task", f"{task_type} → {status}", {"payload": payload, "result": result})


@_safe
def tool(agent: str, name: str, args: Mapping[str, Any], result: Any) -> None:
    status = result.get("status") if isinstance(result, Mapping) else "ok"
    paths = [str(args[k]) for k in ("path", "id") if isinstance(args.get(k), str) and args[k].endswith(".md")]
    record(agent, "tool", f"{name}({_short({k: v for k, v in args.items() if k != 'code'}, 200)}) → {status}",
           {"args": args, "result": result}, paths)


#: Engine ticks that found nothing to do say nothing new; the schedule's own JSONL keeps them.
_QUIET_JOBS = {"sam_paper_mark": "closed", "sam_scalp": "opened", "sam_tournament": "opened",
               "brain_index": "indexed"}


@_safe
def job(agent: str, name: str, result: Mapping[str, Any]) -> None:
    counter = _QUIET_JOBS.get(name)
    if counter and result.get("status") == "ok" and not result.get(counter):
        return
    record(agent, "job", f"{name} → {result.get('status')}", result)
