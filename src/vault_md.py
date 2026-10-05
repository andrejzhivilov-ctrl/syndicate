"""
Markdown Vault — Ground Truth for the whole Syndicate.

Markdown files (versioned in git) are the source of truth. The vector index
(pgvector) is only a rebuildable search copy: ``reindex`` can regenerate it
from the files at any time, and ``verify_against_source`` re-checks any
retrieved snippet against the original file before an agent acts on it.

Layout (Zuevich-style three folders + per-agent dossiers)::

    raw/        incoming, unprocessed material
    wiki/       curated knowledge base
    statutes/   approved rules (protected: change only through approved CRs)
    agents/<id>/{dossier,memory}.md
    archive/    forgotten / superseded facts (never hard-deleted)
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional

import structlog

logger = structlog.get_logger(__name__)

LAYOUT_DIRS = ("raw", "wiki", "statutes", "agents", "archive")
PROTECTED_DIRS = ("statutes",)
_SAFE_AGENT = re.compile(r"^[a-z0-9_\-]{1,32}$")
_FACT_LINE = re.compile(r"^- \*\*(?P<key>[^*]+)\*\*: (?P<value>.*?)(?: <!-- (?P<meta>.*?) -->)?$")


class TrustLevel(IntEnum):
    """Trust pyramid — lower number wins a conflict."""
    OPERATOR_COMMAND = 1     # fresh direct command / official config
    VERIFIED_MARKDOWN = 2    # vault files
    SEMANTIC_MEMORY = 3      # vector recall of past sessions
    EXTERNAL = 4             # web / third-party / unverified


@dataclass
class SourceClaim:
    statement: str
    level: TrustLevel
    timestamp: float
    source: str = ""


def resolve_conflict(claims: List[SourceClaim]) -> Optional[SourceClaim]:
    """Highest trust wins; ties are broken by freshness."""
    if not claims:
        return None
    return sorted(claims, key=lambda c: (int(c.level), -c.timestamp))[0]


class VaultError(Exception):
    pass


class MarkdownVault:
    def __init__(self, root: Optional[Path | str] = None, vault_root: Optional[Path | str] = None) -> None:
        target = root if root is not None else (vault_root if vault_root is not None else None)
        if target is None:
            # Honour EVA_DATA_DIR so the read-only production container can mount
            # a single writable volume instead of failing to create ./vault_md.
            from src.data_paths import data_dir

            target = data_dir("vault")
        self.root = Path(target).resolve()
        self.ensure_layout()

    # ── paths ─────────────────────────────────────────────────────────────
    def ensure_layout(self) -> None:
        for d in LAYOUT_DIRS:
            (self.root / d).mkdir(parents=True, exist_ok=True)

    def _resolve(self, rel: str) -> Path:
        p = (self.root / rel).resolve()
        if self.root != p and self.root not in p.parents:
            raise VaultError(f"path_escapes_vault:{rel}")
        if p.suffix.lower() != ".md":
            raise VaultError(f"only_markdown_allowed:{rel}")
        return p

    def validate_path(self, rel: str) -> Path:
        """Public counterpart of :meth:`_resolve`.

        Callers outside this module (e.g. ``ChangeRequestStore``) used to reach
        into the private ``_resolve`` to reject path traversal / non-Markdown
        targets before creating a change request.
        """
        return self._resolve(rel)

    @staticmethod
    def is_protected(rel: str) -> bool:
        first = Path(rel).parts[0] if Path(rel).parts else ""
        return first in PROTECTED_DIRS

    # ── file operations ───────────────────────────────────────────────────
    def write(self, rel: str, content: str, *, allow_protected: bool = False) -> str:
        if self.is_protected(rel) and not allow_protected:
            raise VaultError(f"protected_path_requires_approved_change_request:{rel}")
        p = self._resolve(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return self.content_hash(content)

    def read(self, rel: str) -> str:
        p = self._resolve(rel)
        if not p.exists():
            raise VaultError(f"not_found:{rel}")
        return p.read_text(encoding="utf-8")

    def exists(self, rel: str) -> bool:
        try:
            return self._resolve(rel).exists()
        except VaultError:
            return False

    def list_files(self, subdir: str = "") -> List[str]:
        base = (self.root / subdir).resolve() if subdir else self.root
        if self.root != base and self.root not in base.parents:
            raise VaultError("path_escapes_vault")
        return sorted(str(p.relative_to(self.root)).replace("\\", "/") for p in base.rglob("*.md"))

    @staticmethod
    def content_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    # ── facts (semantic memory commands) ──────────────────────────────────
    def _agent_memory_path(self, agent: str) -> str:
        if not _SAFE_AGENT.match(agent):
            raise VaultError(f"bad_agent_id:{agent}")
        return f"agents/{agent}/memory.md"

    def _load_facts(self, agent: str) -> List[Dict[str, str]]:
        rel = self._agent_memory_path(agent)
        if not self.exists(rel):
            return []
        facts = []
        for line in self.read(rel).splitlines():
            m = _FACT_LINE.match(line.strip())
            if m:
                facts.append({"key": m["key"].strip(), "value": m["value"].strip(), "meta": (m["meta"] or "").strip()})
        return facts

    def _save_facts(self, agent: str, facts: List[Dict[str, str]]) -> None:
        lines = [f"# Memory — {agent}", "", "Ground truth. Edit via commands or approved change requests.", ""]
        for f in facts:
            meta = f" <!-- {f['meta']} -->" if f.get("meta") else ""
            lines.append(f"- **{f['key']}**: {f['value']}{meta}")
        self.write(self._agent_memory_path(agent), "\n".join(lines) + "\n")

    @staticmethod
    def _slug(text: str, limit: int = 48) -> str:
        s = re.sub(r"\s+", " ", text.strip().lower())
        s = re.sub(r"[^\w\s\-]", "", s, flags=re.UNICODE)
        return s[:limit].strip() or "fact"

    def remember(self, agent: str, fact: str, key: Optional[str] = None) -> Dict[str, Any]:
        facts = self._load_facts(agent)
        key = key or self._slug(fact, 40)
        for f in facts:
            if f["key"] == key:
                f["value"] = fact
                f["meta"] = f"updated={int(time.time())}"
                self._save_facts(agent, facts)
                return {"status": "updated", "key": key}
        facts.append({"key": key, "value": fact, "meta": f"created={int(time.time())}"})
        self._save_facts(agent, facts)
        return {"status": "created", "key": key}

    def find_fact(self, agent: str, query: str) -> Optional[Dict[str, str]]:
        """Keyword match (token overlap) — fallback to semantic search outside this module."""
        q = set(self._slug(query, 200).split())
        best, best_score = None, 0.0
        for f in self._load_facts(agent):
            tokens = set(self._slug(f["key"] + " " + f["value"], 400).split())
            if not tokens or not q:
                continue
            score = len(q & tokens) / len(q)
            if score > best_score:
                best, best_score = f, score
        return best if best_score >= 0.34 else None

    def update_fact(self, agent: str, query: str, new_value: str) -> Dict[str, Any]:
        facts = self._load_facts(agent)
        target = self.find_fact(agent, query)
        if not target:
            return self.remember(agent, new_value) | {"note": "no_match_created_new"}
        for f in facts:
            if f["key"] == target["key"]:
                self._archive_fact(agent, f, reason="superseded")
                f["value"], f["meta"] = new_value, f"updated={int(time.time())}"
        self._save_facts(agent, facts)
        return {"status": "updated", "key": target["key"]}

    def forget(self, agent: str, query: str) -> Dict[str, Any]:
        target = self.find_fact(agent, query)
        if not target:
            return {"status": "not_found"}
        facts = [f for f in self._load_facts(agent) if f["key"] != target["key"]]
        self._archive_fact(agent, target, reason="forgotten")
        self._save_facts(agent, facts)
        return {"status": "archived", "key": target["key"]}

    def _archive_fact(self, agent: str, fact: Dict[str, str], reason: str) -> None:
        rel = f"archive/{agent}.md"
        prev = self.read(rel) if self.exists(rel) else f"# Archive — {agent}\n\n"
        prev += f"- **{fact['key']}**: {fact['value']} <!-- {reason}={int(time.time())} -->\n"
        self.write(rel, prev)

    # ── grounding + index ─────────────────────────────────────────────────
    def verify_against_source(self, rel: str, snippet: str) -> bool:
        """A snippet found through the vector index must exist in the Markdown source."""
        try:
            norm = lambda s: re.sub(r"\s+", " ", s).strip().lower()  # noqa: E731
            return norm(snippet) in norm(self.read(rel))
        except VaultError:
            return False

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        q = set(self._slug(query, 300).split())
        out: List[Dict[str, Any]] = []
        for rel in self.list_files():
            if rel.startswith("archive/"):
                continue
            text = self.read(rel)
            tokens = set(self._slug(text, 4000).split())
            if q and tokens:
                score = len(q & tokens) / len(q)
                if score > 0:
                    out.append({"path": rel, "score": round(score, 3), "trust": int(TrustLevel.VERIFIED_MARKDOWN)})
        return sorted(out, key=lambda r: -r["score"])[:limit]

    async def reindex(
        self,
        embed: Callable[[str], Awaitable[List[float]]],
        upsert: Callable[[str, int, str, List[float], str], Awaitable[None]],
        chunker: Optional[Callable[[str], Iterable[str]]] = None,
        only_changed: Optional[Dict[str, str]] = None,
    ) -> Dict[str, int]:
        """Rebuild the vector index from Markdown. ``only_changed`` maps path->known hash."""
        from src.sensory import SensoryRouter
        chunker = chunker or SensoryRouter.chunk_for_embedding
        files = chunks_n = skipped = 0
        for rel in self.list_files():
            if rel.startswith("archive/"):
                continue
            text = self.read(rel)
            h = self.content_hash(text)
            if only_changed is not None and only_changed.get(rel) == h:
                skipped += 1
                continue
            for i, chunk in enumerate(chunker(text)):
                await upsert(rel, i, chunk, await embed(chunk), h)
                chunks_n += 1
            files += 1
        return {"files": files, "chunks": chunks_n, "skipped_unchanged": skipped}
