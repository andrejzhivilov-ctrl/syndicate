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
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
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
    def write(
        self,
        rel: str,
        content: str,
        *,
        allow_protected: bool = False,
        allow_memory_write: bool = False,
    ) -> str:
        p = self._resolve(rel)
        parts = p.relative_to(self.root).parts
        if parts and parts[0] == "statutes" and not allow_protected:
            raise VaultError("protected_path_requires_approved_change_request")
        is_managed_memory = (
            bool(parts)
            and (parts[0] in {"raw", "archive"} or (len(parts) >= 3 and parts[0] == "agents" and parts[2] == "memory.md"))
        )
        if is_managed_memory and not allow_memory_write:
            raise VaultError("managed_memory_path_requires_policy_gate")
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
        self.write(self._agent_memory_path(agent), "\n".join(lines) + "\n", allow_memory_write=True)

    @staticmethod
    def _slug(text: str, limit: int = 48) -> str:
        s = re.sub(r"\s+", " ", text.strip().lower())
        s = re.sub(r"[^\w\s\-]", "", s, flags=re.UNICODE)
        return s[:limit].strip() or "fact"

    @staticmethod
    def _memory_metadata(source: str, confirmed: bool) -> str:
        """Attach auditable provenance to an explicitly approved memory write."""
        safe_source = re.sub(r"[^a-z0-9_-]", "", str(source).lower())[:40] or "unknown"
        recorded_at = datetime.now(ZoneInfo("Europe/Kyiv")).isoformat(timespec="seconds")
        confirmation = "yes" if confirmed is True else "no"
        return f"date={recorded_at};source={safe_source};confirmed={confirmation}"

    def _memory_candidate_gate(self, agent: str, candidate: str, source: str) -> Optional[Dict[str, Any]]:
        from src.agents.eva_memory_policy import EvaMemoryPolicy, MemoryDisposition

        decision = EvaMemoryPolicy().evaluate(candidate, explicit_save_request=True)
        if decision.disposition is MemoryDisposition.ARCHIVE:
            return None
        if decision.disposition is MemoryDisposition.REJECT:
            return {"status": "refused", "reason_code": decision.reason_code, "active_memory_written": False}
        draft = self.add_memory_review_draft(agent, candidate, decision.reason_code, source=source)
        return {**draft, "active_memory_written": False, "reason_code": decision.reason_code}

    def remember(
        self,
        agent: str,
        fact: str,
        key: Optional[str] = None,
        *,
        source: str = "unknown",
        confirmed: bool = False,
    ) -> Dict[str, Any]:
        """Append an approved fact; replacing an existing key needs an update command."""
        if confirmed is not True:
            return {"status": "confirmation_required"}
        normalized_fact = " ".join(str(fact).split())
        if not normalized_fact:
            return {"status": "error", "reason": "empty_fact"}
        policy_result = self._memory_candidate_gate(agent, normalized_fact, source)
        if policy_result is not None:
            return policy_result
        facts = self._load_facts(agent)
        key = key or self._slug(normalized_fact, 40)
        for existing in facts:
            if existing["key"] == key:
                return {
                    "status": "confirmation_required",
                    "reason": "existing_fact_requires_explicit_update",
                    "key": key,
                }
        facts.append(
            {
                "key": key,
                "value": normalized_fact,
                "meta": self._memory_metadata(source, confirmed),
            }
        )
        self._save_facts(agent, facts)
        return {"status": "created", "key": key}

    def archive_nightly_summary(self, summary: str, local_date: str) -> Dict[str, str]:
        """Create one dated, explicitly unconfirmed nightly text summary without overwriting."""
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(local_date)):
            return {"status": "error", "reason": "invalid_local_date"}
        try:
            datetime.strptime(local_date, "%Y-%m-%d")
        except ValueError:
            return {"status": "error", "reason": "invalid_local_date"}
        normalized = str(summary).strip()
        if not normalized:
            return {"status": "error", "reason": "empty_summary"}
        if len(normalized) > 2_000:
            return {"status": "review_required", "reason": "summary_too_long"}
        from src.agents.eva_memory_policy import EvaMemoryPolicy, MemoryDisposition

        decision = EvaMemoryPolicy().evaluate(
            normalized, explicit_save_request=False, nightly_summary=True
        )
        if decision.disposition is not MemoryDisposition.ARCHIVE:
            status = "refused" if decision.disposition is MemoryDisposition.REJECT else "review_required"
            return {"status": status, "reason": decision.reason_code}
        rel = f"archive/nightly/{local_date}.md"
        if self.exists(rel):
            return {"status": "already_archived", "path": rel}
        metadata = self._memory_metadata("nightly_analysis", False)
        content = (
            f"# Нічний підсумок — {local_date}\n\n"
            "Статус: автоматично згенерований архівний підсумок; не є підтвердженою пам'яттю.\n"
            "Джерело: лише текстові матеріали, окремо дозволені для аналізу Євою.\n"
            f"<!-- {metadata} -->\n\n{normalized}\n"
        )
        self.write(rel, content, allow_memory_write=True)
        return {"status": "archived", "path": rel}

    def add_memory_review_draft(
        self,
        agent: str,
        candidate: str,
        reason_code: str,
        *,
        source: str = "explicit_memory_request",
    ) -> Dict[str, str]:
        """Place one bounded, unapproved item in the manual review queue."""
        self._agent_memory_path(agent)  # validate the target without granting active-memory access
        if not isinstance(candidate, str):
            return {"status": "error", "reason": "text_candidate_required"}
        from src.agents.eva_memory_policy import EvaMemoryPolicy

        policy = EvaMemoryPolicy()
        if policy.contains_secret_like_value(candidate) or policy.contains_location_data(candidate):
            return {"status": "refused", "reason": "secret_or_location_data_not_stored"}
        normalized = " ".join(str(candidate).split())
        if not normalized:
            return {"status": "error", "reason": "empty_candidate"}
        if len(normalized) > 2_000:
            normalized = normalized[:1_997].rstrip() + "..."
        safe_reason = re.sub(r"[^a-z0-9_-]", "", str(reason_code).lower())[:64] or "review_required"
        safe_candidate = normalized.replace("<!--", "< !--").replace("-->", "-- >")
        draft_id = str(uuid.uuid4())[:8]
        rel = "raw/memory_review.md"
        previous = self.read(rel) if self.exists(rel) else "# Memory Review Queue\n\nUnapproved items; not active memory.\n\n"
        metadata = self._memory_metadata(source, False)
        previous += (
            f"- [ ] `{draft_id}` agent={agent} reason={safe_reason} "
            f"<!-- {metadata} -->\n  - Candidate: {safe_candidate}\n"
        )
        self.write(rel, previous, allow_memory_write=True)
        return {"status": "review_required", "draft_id": draft_id, "path": rel}

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

    def update_fact(
        self,
        agent: str,
        query: str,
        new_value: str,
        *,
        confirmed: bool = False,
        source: str = "explicit_update_command",
    ) -> Dict[str, Any]:
        if confirmed is not True:
            return {"status": "confirmation_required"}
        normalized_value = " ".join(str(new_value).split())
        if not normalized_value:
            return {"status": "error", "reason": "empty_fact"}
        policy_result = self._memory_candidate_gate(agent, f"{query}: {normalized_value}", source)
        if policy_result is not None:
            return policy_result
        facts = self._load_facts(agent)
        target = self.find_fact(agent, query)
        if not target:
            result = self.remember(
                agent, normalized_value, source=source, confirmed=confirmed
            )
            return result | {"note": "no_match_created_new"}
        for fact in facts:
            if fact["key"] == target["key"]:
                self._archive_fact(agent, fact, reason="superseded", source=source, confirmed=confirmed)
                fact["value"] = normalized_value
                fact["meta"] = self._memory_metadata(source, confirmed)
        self._save_facts(agent, facts)
        return {"status": "updated", "key": target["key"]}

    def forget(
        self,
        agent: str,
        query: str,
        *,
        confirmed: bool = False,
        source: str = "explicit_forget_command",
    ) -> Dict[str, Any]:
        if confirmed is not True:
            return {"status": "confirmation_required"}
        target = self.find_fact(agent, query)
        if not target:
            return {"status": "not_found"}
        facts = [fact for fact in self._load_facts(agent) if fact["key"] != target["key"]]
        self._archive_fact(agent, target, reason="forgotten", source=source, confirmed=confirmed)
        self._save_facts(agent, facts)
        return {"status": "archived", "key": target["key"]}

    def _archive_fact(
        self,
        agent: str,
        fact: Dict[str, str],
        reason: str,
        *,
        source: str,
        confirmed: bool,
    ) -> None:
        rel = f"archive/{agent}.md"
        prev = self.read(rel) if self.exists(rel) else f"# Archive — {agent}\n\n"
        metadata = self._memory_metadata(source, confirmed)
        prev += f"- **{fact['key']}**: {fact['value']} <!-- {reason};{metadata} -->\n"
        self.write(rel, prev, allow_memory_write=True)

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
