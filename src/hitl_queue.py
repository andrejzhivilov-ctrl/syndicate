"""Human-in-the-loop queue — the place where held agent actions wait for Andrii.

Before this module the orchestrator's HITL gate only *flagged* a task and then
cleared the flag, so nothing was ever held. Now a task that needs approval is
parked here: its outbound actions are removed from the result and stored, and
they are only released after an explicit decision by an authenticated operator.

Rules enforced here (not by the caller):
  * a held item can be decided exactly once;
  * the decision actor is supplied by the HTTP layer from the authenticated
    credential, never from the request body;
  * ``release`` returns the held actions only for ``approved`` items, and only
    once — a second call returns nothing, so an approval cannot be replayed.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.data_paths import data_dir

PENDING = "pending"
APPROVED = "approved"
REJECTED = "rejected"
RELEASED = "released"
_DECISIONS = {"approve": APPROVED, "reject": REJECTED}


class HitlError(Exception):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class HitlQueue:
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = data_dir("hitl", "data/hitl") / "queue.sqlite3" if path is None else Path(path)

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute(
            "CREATE TABLE IF NOT EXISTS items ("
            "id TEXT PRIMARY KEY, created_at TEXT NOT NULL, agent_id TEXT NOT NULL, "
            "task_type TEXT NOT NULL, task_id TEXT NOT NULL, reason TEXT NOT NULL, "
            "status TEXT NOT NULL, held TEXT NOT NULL, decided_at TEXT, decided_by TEXT, comment TEXT)"
        )
        try:
            self.path.chmod(0o600)
        except OSError:
            pass
        return db

    def enqueue(
        self,
        *,
        agent_id: str,
        task_type: str,
        task_id: str,
        reason: str,
        held_actions: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        item_id = "HQ-" + uuid.uuid4().hex[:12]
        held = json.dumps(held_actions or [], ensure_ascii=False, default=str)
        with closing(self._connect()) as db:
            db.execute(
                "INSERT INTO items (id, created_at, agent_id, task_type, task_id, reason, status, held) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (item_id, _now(), agent_id, task_type, task_id, reason[:500], PENDING, held),
            )
        return item_id

    @staticmethod
    def _view(row: sqlite3.Row, *, with_held: bool = False) -> Dict[str, Any]:
        view = {k: row[k] for k in row.keys() if k != "held"}
        held = json.loads(row["held"])
        view["held_actions_count"] = len(held)
        if with_held:
            view["held_actions"] = held
        return view

    def pending(self) -> List[Dict[str, Any]]:
        with closing(self._connect()) as db:
            rows = db.execute(
                "SELECT * FROM items WHERE status = ? ORDER BY created_at DESC", (PENDING,)
            ).fetchall()
        return [self._view(r) for r in rows]

    def get(self, item_id: str) -> Dict[str, Any]:
        with closing(self._connect()) as db:
            row = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            raise HitlError("hitl_item_not_found")
        return self._view(row, with_held=True)

    def decide(self, item_id: str, decision: str, actor: str, comment: str = "") -> Dict[str, Any]:
        if decision not in _DECISIONS:
            raise HitlError("invalid_decision")
        if not actor or not isinstance(actor, str):
            raise HitlError("actor_required")
        new_status = _DECISIONS[decision]
        with closing(self._connect()) as db:
            cur = db.execute(
                "UPDATE items SET status = ?, decided_at = ?, decided_by = ?, comment = ? "
                "WHERE id = ? AND status = ?",
                (new_status, _now(), actor, comment[:500], item_id, PENDING),
            )
            if cur.rowcount != 1:
                exists = db.execute("SELECT status FROM items WHERE id = ?", (item_id,)).fetchone()
                if exists is None:
                    raise HitlError("hitl_item_not_found")
                raise HitlError("hitl_item_already_decided")
        return self.get(item_id)

    def release(self, item_id: str) -> List[Dict[str, Any]]:
        """Return held actions of an approved item, exactly once."""
        with closing(self._connect()) as db:
            row = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
            if row is None:
                raise HitlError("hitl_item_not_found")
            if row["status"] != APPROVED:
                raise HitlError(f"hitl_item_not_releasable:{row['status']}")
            cur = db.execute(
                "UPDATE items SET status = ? WHERE id = ? AND status = ?", (RELEASED, item_id, APPROVED)
            )
            if cur.rowcount != 1:
                raise HitlError("hitl_item_not_releasable:raced")
            return json.loads(row["held"])
