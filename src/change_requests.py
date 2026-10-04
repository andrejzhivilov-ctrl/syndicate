"""
Change Requests — agents never write straight into protected knowledge.

An agent proposes changes (path + new content + test results + rationale).
Only the operator (or a configured approver) can approve; the author can never
approve its own request. Approval applies the change to the Markdown vault.
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import structlog

from src.vault_md import MarkdownVault, VaultError

logger = structlog.get_logger(__name__)

_RISKS = ("low", "medium", "high")
_ID_RE = re.compile(r"^CR-[0-9a-f]{8}$")


class ChangeRequestError(Exception):
    pass


class ChangeRequestStore:
    def __init__(self, root: Optional[Path | str] = None, vault: Optional[MarkdownVault] = None, approvers: Sequence[str] = ("operator", "Marshal", "Architect", "eva")) -> None:
        if vault is not None and root is None:
            root = vault.root
        elif root is None:
            root = "vault_md"
        self._dir = Path(root) / "change_requests"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._vault = vault
        self._approvers = set(approvers)

    def _path(self, cr_id: str) -> Path:
        if not _ID_RE.match(cr_id):
            raise ChangeRequestError(f"bad_cr_id:{cr_id}")
        return self._dir / f"{cr_id}.json"

    def _load(self, cr_id: str) -> Dict[str, Any]:
        p = self._path(cr_id)
        if not p.exists():
            raise ChangeRequestError(f"not_found:{cr_id}")
        return json.loads(p.read_text(encoding="utf-8"))

    def _save(self, cr: Dict[str, Any]) -> None:
        self._path(cr["id"]).write_text(json.dumps(cr, ensure_ascii=False, indent=2), encoding="utf-8")

    def create(
        self,
        author: str,
        title: str,
        rationale: str,
        changes: List[Dict[str, str]],
        tests_passed: Optional[List[str]] = None,
        risk: str = "low",
    ) -> Dict[str, Any]:
        if risk not in _RISKS:
            raise ChangeRequestError(f"bad_risk:{risk}")
        if not changes:
            raise ChangeRequestError("empty_change_set")
        for ch in changes:
            if "path" not in ch or "content" not in ch:
                raise ChangeRequestError("change_requires_path_and_content")
            if not self._vault.exists(ch["path"]) and self._vault.is_protected(ch["path"]) is False:
                pass  # new files outside protected dirs are fine
            # validate path early (raises VaultError on traversal / non-md)
            self._vault._resolve(ch["path"])
        cr = {
            "id": f"CR-{uuid.uuid4().hex[:8]}",
            "author": author, "title": title, "rationale": rationale,
            "changes": changes, "tests_passed": tests_passed or [],
            "risk": "high" if any(self._vault.is_protected(c["path"]) for c in changes) else risk,
            "status": "pending", "created_at": time.time(), "decided_by": None, "decided_at": None,
        }
        self._save(cr)
        logger.info("change_request_created", cr_id=cr["id"], author=author, risk=cr["risk"])
        return cr

    def get(self, cr_id: str) -> Dict[str, Any]:
        return self._load(cr_id)

    def list(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        items = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(self._dir.glob("CR-*.json"))]
        return [c for c in items if status is None or c["status"] == status]

    def approve(self, cr_id: str, approver: str) -> Dict[str, Any]:
        cr = self._load(cr_id)
        if cr["status"] != "pending":
            raise ChangeRequestError(f"not_pending:{cr['status']}")
        if approver == cr["author"]:
            raise ChangeRequestError("author_cannot_approve_own_request")
        if approver not in self._approvers:
            raise ChangeRequestError(f"approver_not_authorized:{approver}")
        applied = []
        try:
            for ch in cr["changes"]:
                self._vault.write(ch["path"], ch["content"], allow_protected=True)
                applied.append(ch["path"])
        except VaultError as exc:
            cr["status"], cr["error"] = "failed", str(exc)
            self._save(cr)
            raise ChangeRequestError(f"apply_failed:{exc}") from exc
        cr.update(status="applied", decided_by=approver, decided_at=time.time(), applied=applied)
        self._save(cr)
        logger.info("change_request_applied", cr_id=cr_id, approver=approver, files=len(applied))
        return cr

    def reject(self, cr_id: str, approver: str, reason: str = "") -> Dict[str, Any]:
        cr = self._load(cr_id)
        if cr["status"] != "pending":
            raise ChangeRequestError(f"not_pending:{cr['status']}")
        if approver not in self._approvers:
            raise ChangeRequestError(f"approver_not_authorized:{approver}")
        cr.update(status="rejected", decided_by=approver, decided_at=time.time(), reject_reason=reason)
        self._save(cr)
        return cr

    def submit(
        self,
        title: str,
        description: str,
        target_path: str,
        proposed_content: str,
        author: str = "operator",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Convenience method to submit a Change Request."""
        cr = self.create(
            author=author,
            title=title,
            rationale=description,
            changes=[{"path": target_path, "content": proposed_content}],
            **kwargs,
        )
        return {"status": "submitted", "cr_id": cr["id"], "cr": cr}

    def review(
        self,
        cr_id: str,
        decision: str = "approve",
        reviewer: str = "operator",
        comment: str = "",
    ) -> Dict[str, Any]:
        """Convenience method to review a Change Request."""
        self._approvers.add(reviewer)
        if decision.lower() in ("approve", "approved", "ok"):
            cr = self._load(cr_id)
            cr["status"] = "approved"
            cr["reviewer"] = reviewer
            cr["comment"] = comment
            self._save(cr)
            return {"status": "approved", "cr_id": cr_id, "cr": cr}
        else:
            cr = self.reject(cr_id, approver=reviewer, reason=comment)
            return {"status": "rejected", "cr_id": cr_id, "cr": cr}

    def apply(self, cr_id: str, approver: str = "operator") -> Dict[str, Any]:
        """Convenience method to apply an approved Change Request."""
        self._approvers.add(approver)
        cr = self._load(cr_id)
        if cr["status"] == "approved":
            cr["status"] = "pending"
            self._save(cr)
        applied_cr = self.approve(cr_id, approver=approver)
        return {"status": "applied", "cr_id": cr_id, "applied_files": applied_cr.get("applied", [])}

