"""Persistent SKILL.md notes captured only from explicitly successful tasks.

A skill is a reusable procedure, not ground truth. New notes start as candidates;
only the same procedure observed in two distinct successful task runs is exposed
for retrieval. Files live in the Markdown vault, which honours ``EVA_DATA_DIR``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog

from src.pii import PIIRedactor
from src.vault_md import MarkdownVault, VaultError

logger = structlog.get_logger(__name__)

_SAFE_AGENT = re.compile(r"^[a-z0-9_-]{1,32}$")
_META_RE = re.compile(r"^<!-- eva-skill-meta-b64: ([A-Za-z0-9_-]+) -->$", re.MULTILINE)
_TOKEN_RE = re.compile(r"[\w-]+", re.UNICODE)


class SkillStore:
    """Store, deduplicate, verify, and retrieve agent-specific skill notes."""

    REQUIRED_SUCCESSES = 2

    def __init__(self, vault: Optional[MarkdownVault] = None) -> None:
        self._vault = vault or MarkdownVault()
        self._redactor = PIIRedactor()

    @staticmethod
    def _slug(value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:56]
        return slug or "learned-skill"

    @staticmethod
    def _fingerprint(title: str, when_to_use: str, procedure: str) -> str:
        payload = "\n".join((title.strip(), when_to_use.strip(), procedure.strip()))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _decode_metadata(content: str) -> Optional[Dict[str, Any]]:
        match = _META_RE.search(content)
        if not match:
            return None
        try:
            encoded = match.group(1)
            encoded += "=" * (-len(encoded) % 4)
            raw = base64.urlsafe_b64decode(encoded.encode("ascii"))
            value = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            return None
        return value if isinstance(value, dict) else None

    @staticmethod
    def _metadata_line(metadata: Dict[str, Any]) -> str:
        raw = json.dumps(metadata, ensure_ascii=False, sort_keys=True).encode("utf-8")
        encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
        return f"<!-- eva-skill-meta-b64: {encoded} -->"

    def _render(self, metadata: Dict[str, Any]) -> str:
        evidence = metadata.get("evidence", [])
        lines = [
            f"# SKILL.md — {metadata['title']}",
            "",
            f"Status: **{metadata['status']}** · successful runs: {len(evidence)}",
            "",
            "This is a reusable procedure captured after successful runs. "
            "Candidates are not trusted instructions; current system and safety rules take precedence.",
            "",
            "## When to use",
            "",
            metadata.get("when_to_use") or "Not specified.",
            "",
            "## Procedure",
            "",
            metadata["procedure"],
            "",
            "## Success evidence",
            "",
        ]
        lines.extend(
            f"- `{item['task_id']}` — {item['task_type']} ({item['recorded_at']})"
            for item in evidence
        )
        lines.extend(("", self._metadata_line(metadata), ""))
        return "\n".join(lines)

    def _prepare_candidate(self, agent_id: str, candidate: Any, success: bool):
        if not success:
            return {"status": "not_recorded", "reason": "task_not_successful"}
        if not _SAFE_AGENT.fullmatch(str(agent_id)):
            return {"status": "error", "reason": "invalid_agent_id"}
        if not isinstance(candidate, dict):
            return {"status": "not_recorded", "reason": "no_skill_candidate"}

        title = str(candidate.get("name") or candidate.get("title") or "").strip()
        when_to_use = str(candidate.get("when_to_use") or "").strip()
        procedure = str(candidate.get("procedure") or "").strip()
        if not title or not procedure:
            return {"status": "error", "reason": "candidate_requires_name_and_procedure"}

        title = title.replace("\n", " ").replace("\r", " ")[:120]
        title, _ = self._redactor.redact(title)
        when_to_use, _ = self._redactor.redact(when_to_use[:800])
        procedure, _ = self._redactor.redact(procedure[:4000])
        return title, when_to_use, procedure

    def record_success(
        self,
        *,
        agent_id: str,
        task_type: str,
        task_id: str,
        candidate: Any,
        success: bool,
    ) -> Dict[str, Any]:
        """Capture an explicit skill candidate only when its task truly succeeded."""
        prepared = self._prepare_candidate(agent_id, candidate, success)
        if isinstance(prepared, dict):
            return prepared
        title, when_to_use, procedure = prepared
        fingerprint = self._fingerprint(title, when_to_use, procedure)
        slug = self._slug(title)
        path = f"agents/{agent_id}/skills/{slug}/SKILL.md"
        try:
            existing = self._vault.read(path) if self._vault.exists(path) else ""
        except VaultError as exc:
            logger.warning("skill_read_failed", agent_id=agent_id, path=path, error=str(exc))
            return {"status": "error", "reason": str(exc)}
        metadata = self._decode_metadata(existing) if existing else None
        if existing and metadata is None:
            return {"status": "error", "reason": "existing_skill_metadata_invalid", "path": path}

        if metadata and metadata.get("fingerprint") != fingerprint:
            return {"status": "conflict", "reason": "skill_procedure_changed", "path": path}
        if metadata is None:
            metadata = {
                "schema": 1,
                "agent_id": agent_id,
                "title": title,
                "when_to_use": when_to_use,
                "procedure": procedure,
                "fingerprint": fingerprint,
                "status": "candidate",
                "evidence": [],
            }

        evidence = list(metadata.get("evidence") or [])
        normalized_task_id = re.sub(r"[^A-Za-z0-9._:-]", "_", str(task_id))[:120] or "unknown"
        if any(item.get("task_id") == normalized_task_id for item in evidence if isinstance(item, dict)):
            return {
                "status": str(metadata.get("status", "candidate")),
                "path": path,
                "success_count": len(evidence),
                "duplicate": True,
            }

        evidence.append({
            "task_id": normalized_task_id,
            "task_type": re.sub(r"[^A-Za-z0-9._:-]", "_", str(task_type))[:120],
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        })
        metadata["evidence"] = evidence[-50:]
        metadata["status"] = "verified" if len(metadata["evidence"]) >= self.REQUIRED_SUCCESSES else "candidate"

        try:
            self._vault.write(path, self._render(metadata))
        except VaultError as exc:
            logger.warning("skill_capture_failed", agent_id=agent_id, path=path, error=str(exc))
            return {"status": "error", "reason": str(exc)}

        return {
            "status": metadata["status"],
            "path": path,
            "success_count": len(metadata["evidence"]),
        }

    def find_relevant(self, agent_id: str, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieve only repeated-success skills for this agent by keyword overlap."""
        if not _SAFE_AGENT.fullmatch(str(agent_id)) or limit <= 0:
            return []
        query_tokens = set(_TOKEN_RE.findall(str(query).lower()))
        if not query_tokens:
            return []

        ranked = []
        try:
            paths = self._vault.list_files(f"agents/{agent_id}/skills")
            for path in paths:
                content = self._vault.read(path)
                metadata = self._decode_metadata(content)
                if not metadata or metadata.get("status") != "verified":
                    continue
                skill_tokens = set(_TOKEN_RE.findall(
                    " ".join((
                        str(metadata.get("title", "")),
                        str(metadata.get("when_to_use", "")),
                        str(metadata.get("procedure", "")),
                    )).lower()
                ))
                overlap = query_tokens & skill_tokens
                if not overlap:
                    continue
                score = len(overlap) / len(query_tokens)
                ranked.append({
                    "name": metadata.get("title", ""),
                    "when_to_use": metadata.get("when_to_use", ""),
                    "procedure": metadata.get("procedure", ""),
                    "success_count": len(metadata.get("evidence", [])),
                    "path": path,
                    "score": round(score, 3),
                })
        except VaultError as exc:
            logger.warning("skill_retrieval_failed", agent_id=agent_id, error=str(exc))
            return []

        return sorted(ranked, key=lambda item: (-item["score"], item["path"]))[:limit]
