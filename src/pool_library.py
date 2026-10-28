"""Shared skill, prompt and MCP pools readable by every director.

Operator decision 28.10: all 18 agents may search and read the pools so nobody is
limited in ideas. Pool content is reference material only: it never becomes a
system prompt, grant, tool or instruction by itself. Installing a skill into an
agent, adopting a prompt as an agent's system prompt, and installing, launching
or calling an MCP server stay operator approvals (``config/pool_access.json``);
nothing here performs them.

Courses and site templates are knowledge bases (Obsidian), not pools, and are
not indexed. Search is local and lexical, so it costs no model tokens.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import structlog

from src.vault_paths import DIRECTOR_IDS

logger = structlog.get_logger(__name__)

ROOT = Path(__file__).resolve().parents[1]
ACCESS_PATH = "config/pool_access.json"
KINDS = ("skill", "prompt", "mcp")

#: Where each kind lives, relative to the repository root.
SKILL_DIRS = (
    ".agents/skills", "skills", "antigravity_identity/skills", "antigravity_core",
    "architect_core", "eva_core", "jack_core", "kodex_core", "marshal_core",
    "oscar_core", "sam_core", "tyler_core",
)
SKILL_NOTE_DIRS = ("knowledge_pools/skills",)
PROMPT_DIRS = (
    "Arena_Knowledge_Pool/01_Промпты_по_категориям",
    "Arena_Knowledge_Pool/08_PRO_Промпты_XML_1703",
    "knowledge_pools/prompts",
    "antigravity_identity/prompts",
)
MCP_REGISTRY = "mcp_servers/mcp_servers_registry.json"

SEARCH_LIMIT_MAX = 5
READ_CHARS_MAX = 3500
SUMMARY_CHARS = 220
_MAX_FILE_BYTES = 512 * 1024
_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


class PoolError(ValueError):
    """A safe, non-content-bearing pool error."""


@dataclass(frozen=True)
class PoolItem:
    item_id: str
    kind: str
    title: str
    summary: str
    category: str
    path: str = ""
    url: str = ""

    def card(self) -> Dict[str, str]:
        out = {"id": self.item_id, "kind": self.kind, "title": self.title,
               "category": self.category, "summary": self.summary}
        if self.url:
            out["url"] = self.url
        return out


def _tokens(text: str) -> List[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 1]


def _stem(token: str) -> str:
    # Crude Ukrainian/Russian/English stem: inflection mostly changes the ending.
    return token[:5] if len(token) > 5 else token


def _item_id(kind: str, key: str) -> str:
    return f"{kind[0]}-{hashlib.sha1(f'{kind}:{key}'.encode('utf-8')).hexdigest()[:10]}"


def _frontmatter(text: str) -> Dict[str, str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fields: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "-")):
            fields[key.strip()] = value.strip().strip("\"'")
    return fields


def _body(text: str) -> str:
    match = _FRONTMATTER_RE.match(text)
    return text[match.end():] if match else text


def _clip(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


class PoolLibrary:
    """Lazy index over the pools; search is lexical, read is bounded text."""

    def __init__(self, root: Path | str = ROOT) -> None:
        self.root = Path(root).resolve()
        self._items: Optional[Dict[str, PoolItem]] = None
        self._terms: Dict[str, Tuple[frozenset, frozenset]] = {}
        self.access = self._load_access()

    # ── access ─────────────────────────────────────────────────────────────
    def _load_access(self) -> Dict[str, Any]:
        try:
            return json.loads((self.root / ACCESS_PATH).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            # Fail closed: without the operator's access file nobody reads.
            logger.warning("pool_access_unavailable")
            return {"read": {"agents": []}}

    def readers(self) -> frozenset:
        agents = self.access.get("read", {}).get("agents", [])
        if agents == "all_directors":
            return frozenset(DIRECTOR_IDS)
        return frozenset(a for a in agents if a in DIRECTOR_IDS) if isinstance(agents, list) else frozenset()

    def _check_reader(self, agent_id: str) -> None:
        if agent_id not in self.readers():
            raise PoolError("pool_read_not_granted")

    # ── index ──────────────────────────────────────────────────────────────
    @property
    def items(self) -> Dict[str, PoolItem]:
        if self._items is None:
            items: Dict[str, PoolItem] = {}
            for item in (*self._scan_skills(), *self._scan_prompts(), *self._scan_mcp()):
                items[item.item_id] = item
            self._items = items
            logger.info("pool_index_built", **self.counts())
        return self._items

    def counts(self) -> Dict[str, int]:
        result = {kind: 0 for kind in KINDS}
        for item in (self._items or {}).values():
            result[item.kind] += 1
        return result

    def _files(self, dirs: Iterable[str], pattern: str) -> Iterable[Path]:
        for rel in dirs:
            base = self.root / rel
            if not base.is_dir():
                continue
            for path in sorted(base.rglob(pattern)):
                if path.is_file() and not path.is_symlink() and path.stat().st_size <= _MAX_FILE_BYTES:
                    yield path

    def _read(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def _rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def _scan_skills(self) -> Iterable[PoolItem]:
        for path in self._files(SKILL_DIRS, "SKILL.md"):
            text = self._read(path)
            meta = _frontmatter(text)
            title = meta.get("name") or path.parent.name
            summary = meta.get("description") or _body(text)
            yield PoolItem(_item_id("skill", self._rel(path)), "skill", title,
                           _clip(summary, SUMMARY_CHARS), self._rel(path).split("/")[0], self._rel(path))
        for path in self._files(SKILL_NOTE_DIRS, "*.md"):
            text = self._read(path)
            meta = _frontmatter(text)
            yield PoolItem(_item_id("skill", self._rel(path)), "skill", meta.get("name") or path.stem,
                           _clip(meta.get("description") or _body(text), SUMMARY_CHARS), "knowledge_pools",
                           self._rel(path))

    def _scan_prompts(self) -> Iterable[PoolItem]:
        for path in self._files(PROMPT_DIRS, "*.md"):
            if path.name.startswith("00_"):
                continue  # category index pages, not prompts
            text = self._read(path)
            meta = _frontmatter(text)
            title = meta.get("title") or re.sub(r"^\d+_", "", path.stem)
            category = meta.get("category") or re.sub(r"^\d+_", "", path.parent.name)
            yield PoolItem(_item_id("prompt", self._rel(path)), "prompt", title,
                           _clip(_body(text).replace("#", ""), SUMMARY_CHARS), category, self._rel(path))

    def _scan_mcp(self) -> Iterable[PoolItem]:
        try:
            registry = json.loads((self.root / MCP_REGISTRY).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            logger.warning("pool_mcp_registry_unavailable")
            return
        for server in registry.get("servers", []):
            if not isinstance(server, dict) or not server.get("name"):
                continue
            yield PoolItem(_item_id("mcp", str(server["name"])), "mcp", str(server["name"]),
                           _clip(str(server.get("description", "")), SUMMARY_CHARS),
                           str(server.get("category", "")), url=str(server.get("url", "")))

    def _item_terms(self, item: PoolItem) -> Tuple[frozenset, frozenset]:
        cached = self._terms.get(item.item_id)
        if cached is None:
            title = frozenset(_stem(t) for t in _tokens(f"{item.title} {item.category}"))
            cached = (title, frozenset(_stem(t) for t in _tokens(item.summary)))
            self._terms[item.item_id] = cached
        return cached

    # ── public API ─────────────────────────────────────────────────────────
    def search(self, agent_id: str, query: str, kind: Optional[str] = None,
               limit: int = 3) -> List[Dict[str, str]]:
        self._check_reader(agent_id)
        if kind is not None and kind not in KINDS:
            raise PoolError("unknown_pool_kind")
        terms = {_stem(t) for t in _tokens(query[:512])}
        if not terms:
            return []
        limit = max(1, min(int(limit), SEARCH_LIMIT_MAX))
        scored = []
        for item in self.items.values():
            if kind is not None and item.kind != kind:
                continue
            title, summary = self._item_terms(item)
            score = 3 * len(terms & title) + len(terms & summary)
            if score:
                scored.append((score, item.title, item))
        scored.sort(key=lambda s: (-s[0], s[1]))
        return [item.card() for _, _, item in scored[:limit]]

    def read(self, agent_id: str, item_id: str, max_chars: int = READ_CHARS_MAX) -> Dict[str, Any]:
        self._check_reader(agent_id)
        item = self.items.get(item_id)
        if item is None:
            raise PoolError("unknown_pool_item")
        out: Dict[str, Any] = {**item.card(), "untrusted_reference": True}
        if item.kind == "mcp":
            # Catalog metadata only: nothing is installed, launched or called.
            out["note"] = "catalog_entry_only_install_requires_operator_approval"
            return out
        path = (self.root / item.path).resolve()
        if self.root not in path.parents or path.is_symlink():
            raise PoolError("pool_path_rejected")
        text = self._read(path)
        limit = max(200, min(int(max_chars), READ_CHARS_MAX))
        out["text"] = text if len(text) <= limit else text[: limit - 1] + "…"
        out["truncated"] = len(text) > limit
        return out


_LIBRARY: Optional[PoolLibrary] = None


def pool_library() -> PoolLibrary:
    global _LIBRARY
    if _LIBRARY is None:
        _LIBRARY = PoolLibrary()
    return _LIBRARY
