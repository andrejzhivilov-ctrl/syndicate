"""Emergency lockdown flag (manifest §11.2).

Engaging is an API call (HITL scope or master key); *releasing* is deliberately
not. The flag is a file on the server's data volume, so it survives restarts,
and only someone with a shell on the server (``tools/unlock_lockdown.py``, which
asks for the master key) can remove it.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from src.data_paths import data_dir


class Lockdown:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path) if path else data_dir("lockdown", "data/lockdown") / "LOCKED"

    def is_locked(self) -> bool:
        return self.path.exists()

    def info(self) -> Optional[Dict[str, Any]]:
        if not self.is_locked():
            return None
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"engaged_at": None, "actor": "unknown", "reason": "unreadable_flag"}

    def engage(self, actor: str, reason: str = "") -> Dict[str, Any]:
        record = {
            "engaged_at": datetime.now(timezone.utc).isoformat(),
            "actor": str(actor)[:80],
            "reason": str(reason)[:300],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), prefix=".lock-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(record, handle)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        return record
