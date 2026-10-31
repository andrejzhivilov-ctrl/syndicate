"""KODEX as archivist of the synced Obsidian vault: rules, a dry-run plan and the activity log.

Operator rules (31.10):
- A note carrying Andrii's mark (``andrii_protected``) may be created, read and moved by
  agents, never edited or deleted. Agents put the mark on a note only when Andrii asks;
  only Andrii takes it off.
- Every other note agents may organise by their own judgement, deletions go to a trash
  folder first. Anything that looks important (linked from other notes, touched this
  week, hubs and regulations, secret-like content) needs Andrii's permission.
- Everything an agent does to the vault is written to the activity log, and the log
  feeds the morning and evening reports of KODEX, Eva and the other agents.

Step 1 is read-only: :meth:`Archivist.plan` proposes, nothing is changed by it.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import structlog

from src.agents.eva_memory_policy import EvaMemoryPolicy
from src.agents.kodex import PROTECTED_LABEL
from src.obsidian_notes import _notes, vault_dir_from_env

logger = structlog.get_logger(__name__)

TRASH_DIR = "_Кошик_агентів"  # inside the vault, so it is visible to Andrii; excluded from the plan
INBOX = "00_Inbox"
STALE_INBOX_DAYS = 14
RECENT_DAYS = 7
NEAR_DUPLICATE = 0.85
MAX_COMPARE_PER_FOLDER = 400
LOG_ITEMS_IN_DIGEST = 40
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
_WIKILINK = re.compile(r"\[\[([^\]|#]+)")
_HUB_NAME = re.compile(r"(?i)(хаб|регламент|реєстр|дашборд|hub|index|readme|moc\b|майстер)")
_MARK = re.compile(rf"(?im)^\s*{PROTECTED_LABEL}\s*:\s*(true|yes|так)\b|(?<![\w-])#{PROTECTED_LABEL}\b")
_SKIP = (TRASH_DIR,)


def _body(text: str) -> str:
    return _FRONTMATTER.sub("", text, count=1).strip()


def is_protected(text: str) -> bool:
    """True for a note with ``andrii_protected: true`` in the frontmatter or the ``#andrii_protected`` tag."""
    return bool(_MARK.search(text))


def _normalised(text: str) -> str:
    return re.sub(r"\s+", " ", _body(text)).strip().lower()


def _shingles(text: str, size: int = 5) -> Set[str]:
    words = _normalised(text).split()
    return {" ".join(words[i:i + size]) for i in range(max(0, len(words) - size + 1))}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ActivityLog:
    """Append-only JSONL of what agents did in the vault; read back for the daily reports."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def record(self, agent: str, action: str, path: str, **detail: Any) -> None:
        entry = {"at": _utcnow().isoformat(timespec="seconds"), "agent": agent, "action": action, "path": path, **detail}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def entries(self, since: datetime) -> List[Dict[str, Any]]:
        if not self._path.is_file():
            return []
        found: List[Dict[str, Any]] = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
                if datetime.fromisoformat(entry["at"]) >= since:
                    found.append(entry)
            except (ValueError, KeyError):
                continue  # one damaged line must not hide the rest of the day
        return found

    def digest(self, since: datetime) -> Dict[str, Any]:
        """What the morning/evening report prints; an empty log is an honest zero, not a missing source."""
        entries = self.entries(since)
        by_agent: Dict[str, int] = {}
        by_action: Dict[str, int] = {}
        for entry in entries:
            by_agent[entry["agent"]] = by_agent.get(entry["agent"], 0) + 1
            by_action[entry["action"]] = by_action.get(entry["action"], 0) + 1
        return {"since": since.isoformat(timespec="seconds"), "total": len(entries), "by_agent": by_agent,
                "by_action": by_action, "items": entries[-LOG_ITEMS_IN_DIGEST:],
                "awaiting_permission": by_action.get("permission_requested", 0)}


def default_log() -> Optional[ActivityLog]:
    from src.data_paths import data_dir

    try:
        return ActivityLog(data_dir("obsidian_activity") / "activity.jsonl")
    except Exception as exc:  # noqa: BLE001 - reporting must not take the agent down
        logger.warning("obsidian_activity_log_unavailable", error_type=type(exc).__name__)
        return None


def activity_digest(hours: int = 24) -> Dict[str, Any]:
    log = default_log()
    if log is None:
        return {"status": "unavailable", "warning": "журнал дій у сховищі недоступний"}
    return {"status": "ok", **log.digest(_utcnow() - timedelta(hours=hours))}


class Archivist:
    """Rules and the dry-run plan over one vault directory."""

    def __init__(self, root: Path, log: Optional[ActivityLog] = None, agent: str = "kodex") -> None:
        self._root = root
        self._log = log
        self._agent = agent
        self._policy = EvaMemoryPolicy()

    # -- reading ---------------------------------------------------------------------------
    def _all(self) -> List[Tuple[float, Path]]:
        return [(m, p) for m, p in _notes(self._root) if p.relative_to(self._root).parts[0] not in _SKIP]

    def _text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def _backlinks(self, texts: Dict[Path, str]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for source, text in texts.items():
            for target in {t.strip().lower() for t in _WIKILINK.findall(text)}:
                if target != source.stem.lower():
                    counts[target] = counts.get(target, 0) + 1
        return counts

    # -- rules -------------------------------------------------------------------------------
    def importance(self, path: Path, text: str, backlinks: int, mtime: float) -> List[str]:
        """Why a note needs Andrii's permission before an agent edits or deletes it (empty = agents may act)."""
        reasons: List[str] = []
        if is_protected(text):
            reasons.append("позначена вашою міткою")
        if backlinks >= 2:
            reasons.append(f"на неї посилаються {backlinks} нотаток")
        if _utcnow().timestamp() - mtime < RECENT_DAYS * 86400:
            reasons.append(f"змінювалась протягом {RECENT_DAYS} днів")
        if _HUB_NAME.search(path.stem):
            reasons.append("хаб, реєстр чи регламент")
        if self._policy.contains_secret_like_value(text):
            reasons.append("схоже на секрет")
        return reasons

    def check(self, action: str, rel: str) -> Dict[str, Any]:
        """May an agent do ``action`` (read|create|move|edit|delete) to ``rel`` on its own?"""
        target = (self._root / rel).resolve()
        if self._root.resolve() not in target.parents:
            return {"allowed": False, "reason": "path_escapes_vault"}
        if action in ("read", "create"):
            return {"allowed": True}
        if not target.is_file():
            return {"allowed": False, "reason": "not_found"}
        text = self._text(target)
        if action == "move":
            return {"allowed": True}  # moving is allowed even for marked notes
        if action not in ("edit", "delete"):
            return {"allowed": False, "reason": "unknown_action"}
        if is_protected(text):
            return {"allowed": False, "needs_permission": True, "reason": "protected"}
        texts = {p: self._text(p) for _, p in self._all()}
        reasons = self.importance(target, text, self._backlinks(texts).get(target.stem.lower(), 0),
                                  target.stat().st_mtime)
        if reasons:
            return {"allowed": False, "needs_permission": True, "reason": "important", "because": reasons}
        return {"allowed": True}

    # -- the dry-run plan --------------------------------------------------------------------
    def plan(self) -> Dict[str, Any]:
        notes = self._all()
        texts = {p: self._text(p) for _, p in notes}
        backlinks = self._backlinks(texts)
        mtimes = {p: m for m, p in notes}
        items: List[Dict[str, Any]] = []

        def add(kind: str, paths: Iterable[Path], proposal: str, delete_candidates: Iterable[Path] = ()) -> None:
            rels = [p.relative_to(self._root).as_posix() for p in paths]
            reasons: List[str] = []
            for candidate in delete_candidates:
                reasons += [f"{candidate.name}: {r}" for r in
                            self.importance(candidate, texts[candidate], backlinks.get(candidate.stem.lower(), 0),
                                            mtimes[candidate])]
            items.append({"kind": kind, "paths": rels, "proposal": proposal,
                          "needs_permission": bool(reasons), "because": reasons})

        for _, path in notes:
            if len(_body(texts[path])) <= 10:
                add("empty", [path], "у кошик агентів (порожня нотатка)", [path])
        self._duplicates(notes, texts, add)
        cutoff = _utcnow().timestamp() - STALE_INBOX_DAYS * 86400
        for mtime, path in notes:
            if path.relative_to(self._root).parts[0] == INBOX and mtime < cutoff:
                add("stale_inbox", [path], f"розібрати: у {INBOX} понад {STALE_INBOX_DAYS} днів")
        protected = sum(is_protected(t) for t in texts.values())
        return {"status": "ok", "dry_run": True, "notes": len(notes), "protected": protected, "items": items,
                "needs_permission": sum(1 for i in items if i["needs_permission"])}

    def _duplicates(self, notes: List[Tuple[float, Path]], texts: Dict[Path, str], add: Any) -> None:
        by_hash: Dict[str, List[Path]] = {}
        for _, path in notes:
            norm = _normalised(texts[path])
            if len(norm) > 10:
                by_hash.setdefault(hashlib.sha256(norm.encode("utf-8")).hexdigest(), []).append(path)
        grouped: Set[Path] = set()
        for group in by_hash.values():
            if len(group) > 1:
                keep, extra = self._split_group(group, texts)
                add("duplicate", group, f"залишити {keep.name}, решту в кошик агентів", extra)
                grouped.update(group)
        folders: Dict[str, List[Path]] = {}
        for _, path in notes:
            if path not in grouped and 200 <= len(texts[path]) <= 50_000:
                folders.setdefault(path.relative_to(self._root).parts[0], []).append(path)
        for paths in folders.values():
            self._near_duplicates(paths[:MAX_COMPARE_PER_FOLDER], texts, add)

    def _split_group(self, group: List[Path], texts: Dict[Path, str]) -> Tuple[Path, List[Path]]:
        protected = [p for p in group if is_protected(texts[p])]
        keep = protected[0] if protected else min(group, key=lambda p: p.stat().st_mtime)
        return keep, [p for p in group if p != keep and not is_protected(texts[p])]

    def _near_duplicates(self, paths: List[Path], texts: Dict[Path, str], add: Any) -> None:
        shingles = {p: _shingles(texts[p]) for p in paths}
        seen: Set[Path] = set()
        for index, first in enumerate(paths):
            for second in paths[index + 1:]:
                if first in seen or second in seen or not shingles[first] or not shingles[second]:
                    continue
                union = shingles[first] | shingles[second]
                if len(shingles[first] & shingles[second]) / len(union) >= NEAR_DUPLICATE:
                    add("near_duplicate", [first, second], "схожі майже повністю: об'єднати вручну чи Кодексом за вашим дозволом")
                    seen.update({first, second})

    # -- the report note and the mark --------------------------------------------------------
    def write_plan_note(self, plan: Dict[str, Any]) -> str:
        """Create ``00_Inbox/Звіт_Кодекса_<date>.md`` (never overwrites); returns its relative path."""
        stamp = datetime.now().strftime("%Y-%m-%d")
        inbox = self._root / INBOX
        inbox.mkdir(parents=True, exist_ok=True)
        target = inbox / f"Звіт_Кодекса_{stamp}.md"
        counter = 1
        while target.exists():
            counter += 1
            target = inbox / f"Звіт_Кодекса_{stamp}_{counter}.md"
        target.write_text(render_plan(plan), encoding="utf-8")
        rel = target.relative_to(self._root).as_posix()
        if self._log:
            self._log.record(self._agent, "create", rel, note="plan_report")
        return rel

    def protect(self, rel: str, requested_by: str) -> Dict[str, Any]:
        """Put the mark on a note. Only on Andrii's request; agents never remove it."""
        if requested_by != "andrii":
            return {"status": "refused", "reason": "mark_only_on_andrii_request"}
        target = (self._root / rel).resolve()
        if self._root.resolve() not in target.parents or target.suffix.lower() != ".md" or not target.is_file():
            return {"status": "error", "reason": "note_not_found"}
        text = self._text(target)
        if is_protected(text):
            return {"status": "already_protected", "path": rel}
        match = _FRONTMATTER.match(text)
        if match:
            new = f"---\n{match.group(1)}\n{PROTECTED_LABEL}: true\n---\n" + text[match.end():]
        else:
            new = f"---\n{PROTECTED_LABEL}: true\n---\n{text}"
        target.write_text(new, encoding="utf-8")
        if self._log:
            self._log.record(self._agent, "protect", rel, requested_by=requested_by)
        return {"status": "protected", "path": rel}

    def trash(self, rel: str) -> Dict[str, Any]:
        """Move an unprotected, unimportant note to the agents' trash folder; refuses anything else."""
        verdict = self.check("delete", rel)
        if not verdict.get("allowed"):
            if verdict.get("needs_permission") and self._log:
                self._log.record(self._agent, "permission_requested", rel, **{k: v for k, v in verdict.items() if k != "allowed"})
            return {"status": "needs_permission" if verdict.get("needs_permission") else "refused", **verdict}
        source = self._root / rel
        destination = self._root / TRASH_DIR / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        if self._log:
            self._log.record(self._agent, "trash", rel, to=destination.relative_to(self._root).as_posix())
        return {"status": "trashed", "path": rel}


def render_plan(plan: Dict[str, Any]) -> str:
    """Markdown for the plan note, in Ukrainian; says plainly that nothing was changed."""
    lines = ["---", "тип: звіт_кодекса", "---", "# Звіт Кодекса: план чистки сховища", "",
             "**Режим: лише план. Нічого не змінено, не переміщено й не видалено.**", "",
             f"Нотаток: {plan['notes']}; з вашою міткою: {plan['protected']}; "
             f"пропозицій: {len(plan['items'])}; потрібен ваш дозвіл: {plan['needs_permission']}.", ""]
    titles = {"empty": "Порожні нотатки", "duplicate": "Точні дублікати", "near_duplicate": "Майже однакові",
              "stale_inbox": f"Застрягло в {INBOX}"}
    for kind, title in titles.items():
        chosen = [i for i in plan["items"] if i["kind"] == kind]
        if not chosen:
            continue
        lines.append(f"## {title} ({len(chosen)})")
        for item in chosen:
            flag = " **(потрібен дозвіл)**" if item["needs_permission"] else ""
            lines.append(f"- {', '.join(f'[[{p}]]' for p in item['paths'])}: {item['proposal']}{flag}")
            lines += [f"  - причина: {reason}" for reason in item["because"][:4]]
        lines.append("")
    if not plan["items"]:
        lines.append("Сховище чисте: пропозицій немає.")
    return "\n".join(lines) + "\n"


def from_env(agent: str = "kodex") -> Optional[Archivist]:
    root = vault_dir_from_env()
    return Archivist(root, default_log(), agent) if root is not None else None


#: Directors that may act on the vault from Andrii's Telegram commands.
COMMAND_AGENTS = frozenset({"kodex", "eva"})


def chat_command(agent_id: str, command: str, arg: str) -> Dict[str, Any]:
    """``/protect <note>`` and ``/vaultplan`` from Andrii's own chat (the webhook is owner-only)."""
    base = {"agent": agent_id, "mode": "obsidian"}
    if agent_id not in COMMAND_AGENTS:
        return {**base, "status": "refused", "response": "Ця команда працює лише в Кодекса й Єви."}
    archivist = from_env(agent_id)
    if archivist is None:
        return {**base, "status": "unavailable", "response": "Сховище Obsidian недоступне: нічого не змінено."}
    if command == "/protect":
        if not arg:
            return {**base, "status": "error", "response": "Вкажи шлях нотатки: /protect 00_Inbox/Назва.md"}
        result = archivist.protect(arg, "andrii")
        texts = {"protected": f"Мітку {PROTECTED_LABEL} поставлено: {arg}. Агенти її не редагують і не видаляють.",
                 "already_protected": f"На {arg} мітка вже є.",
                 "error": f"Нотатку {arg} не знайдено."}
        return {**base, **result, "response": texts.get(result["status"], "Мітку не поставлено.")}
    plan = archivist.plan()
    note = archivist.write_plan_note(plan)
    return {**base, "status": "ok", "plan": {k: plan[k] for k in ("notes", "protected", "needs_permission")},
            "response": (f"План чистки готовий, нічого не змінено: нотаток {plan['notes']}, пропозицій "
                         f"{len(plan['items'])}, потрібен твій дозвіл на {plan['needs_permission']}. Звіт: {note}")}
