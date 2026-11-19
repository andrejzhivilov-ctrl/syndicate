"""Read-only view of Andrii's synced Obsidian vault for the chat of Eva and Kodex.

The vault directory (``OBSIDIAN_VAULT_DIR``) is what the phone and the PC reach through
``src/obsidian_webdav.py``. When a chat message asks about notes or the vault, the newest
notes and the best keyword matches are put in front of the model as untrusted reference
material. Nothing here writes, and a missing or empty vault is reported as such: the
model must never be left to guess whether it can see the notes.
"""
from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set, Tuple
from zoneinfo import ZoneInfo

import structlog

logger = structlog.get_logger(__name__)

#: Directors whose chat may read the vault (Eva: chief of staff, Kodex: knowledge director).
CHAT_AGENTS = frozenset({"eva", "kodex"})

HINT_RE = re.compile(r"(?i)(нотатк|замітк|записк|obsidian|обсид|сховищ|vault|second\s*brain|другий\s*мозок)")
_WORD_RE = re.compile(r"[\w'’-]{3,}", re.UNICODE)
#: Words that only say "look at my notes" and would otherwise match every file.
_GENERIC_PREFIXES = (
    "нотат", "замітк", "записк", "обсид", "obsid", "сховищ", "vault", "бачиш", "створ", "нов", "нещодавн",
    "щойно", "останн", "перевір", "знайд", "покаж", "єва", "єво", "кодекс", "чи", "що", "яка", "який",
    "second", "brain", "другий", "мозок", "мене", "мені", "своє", "моє", "мою", "мої", "цей", "ця",
)
_SKIP_DIRS = frozenset({".obsidian", ".trash", ".stfolder", ".git"})
MAX_FILES = 3000
MAX_FILE_BYTES = 200_000
SNIPPET_CHARS = 700
MAX_HITS = 3
MIN_SCORE = 3  # a title match, or a term repeated in the body; one stray mention is noise
RECENT_NOTES = 5
PREVIEW_CHARS = 350
REFERENCE_CHARS = 3500
_KYIV = ZoneInfo("Europe/Kyiv")


def vault_dir_from_env() -> Optional[Path]:
    raw = os.environ.get("OBSIDIAN_VAULT_DIR")
    path = Path(raw) if raw else None
    return path if path is not None and path.is_dir() else None


def _notes(root: Path) -> List[Tuple[float, Path]]:
    """(mtime, path) of every Markdown note, newest first; capped so a huge vault stays cheap."""
    found: List[Tuple[float, Path]] = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS and not d.startswith(".")]
        for name in files:
            path = Path(base) / name
            if not name.lower().endswith(".md") or path.is_symlink():
                continue
            try:
                found.append((path.stat().st_mtime, path))
            except OSError:
                continue
            if len(found) >= MAX_FILES:
                return sorted(found, reverse=True)
    return sorted(found, reverse=True)


def _stem(word: str) -> str:
    return word[:6] if len(word) > 7 else word[: max(4, len(word) - 2)]


def _terms(text: str) -> Set[str]:
    words = (w.lower().strip("'’-") for w in _WORD_RE.findall(text))
    return {_stem(w) for w in words if not w.startswith(_GENERIC_PREFIXES)}


def _read(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _score(path: Path, terms: Set[str]) -> int:
    title = path.stem.lower()
    body = _read(path).lower()
    return sum((3 if term in title else 0) + min(body.count(term), 5) for term in terms)


def _when(mtime: float) -> str:
    return datetime.fromtimestamp(mtime, _KYIV).strftime("%d.%m %H:%M")


def _snippet(path: Path) -> str:
    text = re.sub(r"\A---\n.*?\n---\n", "", _read(path), flags=re.DOTALL).strip()
    return text[:SNIPPET_CHARS]


def reference_for(text: str, root: Optional[Path]) -> Optional[str]:
    """Reference block for a chat message that mentions notes; None for ordinary chat."""
    if not HINT_RE.search(text):
        return None
    if root is None:
        return "Obsidian не підключено до Єви: тека зі сховищем недоступна. Не вигадуй вміст нотаток."
    notes = _notes(root)
    if not notes:
        return "Сховище Obsidian підключено, але в ньому немає жодної нотатки .md."
    lines = [f"Сховище Obsidian підключено: нотаток {len(notes)}, остання зміна {_when(notes[0][0])} (Київ).",
             "Найновіші нотатки:"]
    lines += [f"- {path.relative_to(root).as_posix()} ({_when(mtime)})" for mtime, path in notes[:RECENT_NOTES]]
    terms = _terms(text)
    hits = sorted(((_score(path, terms), path) for _, path in notes), key=lambda item: -item[0]) if terms else []
    hits = [(score, path) for score, path in hits if score >= MIN_SCORE][:MAX_HITS]
    if hits:
        lines.append("Збіги за запитом:")
        for _, path in hits:
            lines.append(f"## {path.relative_to(root).as_posix()}\n{_snippet(path)}")
    elif terms:
        lines.append("За цим запитом збігів у нотатках немає.")
    if not hits:
        lines.append("Початок найновіших нотаток:")
        lines += [f"## {path.name}\n{_snippet(path)[:PREVIEW_CHARS]}" for _, path in notes[:RECENT_NOTES]]
    return "\n".join(lines)[:REFERENCE_CHARS]


def obsidian_reference(agent_id: str, text: str) -> Optional[str]:
    """Entry point for the chat path: only Eva and Kodex, only when the message asks about notes."""
    if agent_id not in CHAT_AGENTS or not HINT_RE.search(text):
        return None
    try:
        return reference_for(text, vault_dir_from_env())
    except Exception as exc:  # noqa: BLE001 - reference is optional context, chat must go on
        logger.warning("obsidian_reference_failed", agent=agent_id, error_type=type(exc).__name__)
        return "Не вдалося прочитати сховище Obsidian. Не вигадуй вміст нотаток."


# ── search for agents (19.11.2026) ────────────────────────────────────────────────────────
#
# The chat reference above answers only when a message speaks about notes. An agent's
# ``obsidian_search`` always means "search", so it must not wait for such a word; it must see
# big cards (a whole book as Markdown) by their head, prefer the agent's own folder, and give
# each hit's summary so the agent decides what to open without reading it.

SEARCH_HEAD_BYTES = 60_000
SEARCH_LIMIT = 8
OWN_FOLDER_BONUS = 4
_FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def _head(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            return stream.read(SEARCH_HEAD_BYTES)
    except OSError:
        return ""


def _summary(text: str) -> str:
    front = _FRONT.match(text)
    if front:
        found = re.search(r'^summary:\s*"?(.*?)"?\s*$', front.group(1), re.MULTILINE)
        if found and found.group(1).strip():
            return found.group(1).strip()[:300]
    body = _FRONT.sub("", text).strip()
    return re.sub(r"\s+", " ", body)[:300]


def search_notes(query: str, root: Optional[Path], own: str = "", limit: int = SEARCH_LIMIT) -> str:
    """Notes matching the words of a query, best first, each with its path and summary."""
    if root is None:
        return "Сховище Obsidian недоступне."
    terms = {_stem(w.lower().strip("'’-")) for w in _WORD_RE.findall(query)}
    if not terms:
        return "Порожній запит: напиши, що шукати."
    scored = []
    for _mtime, path in _notes(root):
        relative = path.relative_to(root).as_posix()
        head = _head(path).lower()
        title = path.stem.lower()
        front = (_FRONT.match(head).group(1) if _FRONT.match(head) else "")
        score = sum((4 if term in title else 0) + (3 if term in front else 0) + min(head.count(term), 5)
                    for term in terms)
        if score and own and relative.startswith(own.rstrip("/") + "/"):
            score += OWN_FOLDER_BONUS
        if score >= MIN_SCORE:
            scored.append((score, relative, path))
    if not scored:
        return f"За запитом «{query}» у нотатках нічого не знайдено."
    scored.sort(key=lambda item: -item[0])
    lines = [f"Знайдено {len(scored)}; найкращі {min(limit, len(scored))}. Відкривай obsidian_read (нотатка) "
             "або material_read частинами (великий текст):"]
    for _score_value, relative, path in scored[:limit]:
        lines.append(f"- {relative} — {_summary(_head(path))}")
    return "\n".join(lines)
