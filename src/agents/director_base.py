"""Shared dispatch, validation and transactional local records for directors."""
from __future__ import annotations

import json
import math
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from typing import Any

from src.data_paths import data_dir


def number(value: Any, name: str, minimum: float = 0, maximum: float = math.inf) -> float:
    if isinstance(value, bool):
        raise ValueError(f"invalid_{name}")
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise ValueError(f"invalid_{name}")
    return result


def text(value: Any, name: str, limit: int = 10000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"invalid_{name}")
    return value.strip()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DirectorStore:
    """One SQLite database per director; transitions use a write transaction.

    Record IDs are generated internally. No caller-controlled paths or SQL.
    Payloads never leave the local volume or enter application logs.
    """

    def __init__(self, agent_id: str) -> None:
        self.path = data_dir(agent_id, f"data/{agent_id}") / "records.sqlite3"

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("CREATE TABLE IF NOT EXISTS records (id TEXT PRIMARY KEY, kind TEXT NOT NULL, "
                   "created_at TEXT NOT NULL, payload TEXT NOT NULL)")
        self.path.chmod(0o600)
        return db

    def add(self, kind: str, payload: dict) -> dict:
        record = {**payload, "id": uuid.uuid4().hex, "created_at": utc_now().isoformat()}
        with closing(self.connect()) as db:
            db.execute("INSERT INTO records VALUES (?, ?, ?, ?)",
                       (record["id"], kind, record["created_at"], json.dumps(record, allow_nan=False)))
        return record

    def list(self, kind: str) -> list[dict]:
        if not self.path.exists():
            return []
        with closing(self.connect()) as db:
            rows = db.execute("SELECT payload FROM records WHERE kind=? ORDER BY created_at, id", (kind,)).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def transition(self, record_id: str, kind: str, expected: str, updates: dict) -> dict:
        db = self.connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT payload FROM records WHERE id=? AND kind=?", (record_id, kind)).fetchone()
            if row is None:
                raise ValueError("unknown_record")
            record = json.loads(row["payload"])
            if record["state"] != expected:
                raise ValueError("invalid_record_transition")
            record.update(updates)
            db.execute("UPDATE records SET payload=? WHERE id=?", (json.dumps(record, allow_nan=False), record_id))
            db.commit()
            return record
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


class DirectorAgent:
    AGENT_ID = ""
    ACTIONS: dict[str, str] = {}

    def __init__(self, memory: Any = None, llm: Any = None, *, config: dict | None = None,
                 registry: Any = None) -> None:
        self.memory = memory
        self.config = dict(config or {})
        self.store = DirectorStore(self.AGENT_ID)

    async def execute(self, payload: dict) -> dict:
        if not isinstance(payload, dict):
            return {"agent": self.AGENT_ID, "status": "error", "error": "payload_must_be_object"}
        action = payload.get("action", "capabilities")
        if not isinstance(action, str) or action not in self.ACTIONS:
            return {"agent": self.AGENT_ID, "status": "error", "error": "unknown_action",
                    "available_actions": sorted(self.ACTIONS)}
        try:
            result = await getattr(self, self.ACTIONS[action])(payload)
        except KeyError as exc:
            result = {"status": "unavailable", "value": None, "warning": f"missing_input:{exc.args[0]}"}
        except (ValueError, TypeError, OverflowError):
            result = {"status": "error", "error": "invalid_input"}
        except (sqlite3.Error, OSError):
            result = {"status": "unavailable", "value": None, "warning": "local_storage_unavailable"}
        return {**result, "agent": self.AGENT_ID}

    async def capabilities(self, payload: dict) -> dict:
        return {"status": "ok", "available_actions": sorted(self.ACTIONS),
                "external_actions": False, "activation": "prepared_not_enabled"}

    async def blocked_external(self, payload: dict) -> dict:
        return {"status": "approval_required", "requires_hitl": True, "executed": False,
                "reason": "external_execution_not_enabled"}
