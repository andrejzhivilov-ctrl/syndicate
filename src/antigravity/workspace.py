"""Owner-only local storage; never fall back to the repository.

The operator must own EVA_DATA_DIR and prevent other users writing its parents.
This is not a sandbox for executing untrusted code or defending against root.
"""

from __future__ import annotations

import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

REPO = Path(__file__).resolve().parents[2]
MAX_INPUT_BYTES = 5 * 1024 * 1024


class StudioError(ValueError):
    """Safe public error code. Never include user content or secrets."""


class Workspace:
    def __init__(self) -> None:
        raw = os.environ.get("EVA_DATA_DIR", "").strip()
        if not raw or not Path(raw).is_absolute():
            raise StudioError("absolute_EVA_DATA_DIR_required")
        base = Path(raw)
        self._no_links(base)
        if base.resolve().is_relative_to(REPO):
            raise StudioError("workspace_must_be_outside_repository")
        self.root = base / "antigravity-studio"
        for name in ("", "tasks", "inbox", "artifacts", "history", "audit"):
            path = self.root / name
            self._no_links(path)
            path.mkdir(parents=True, exist_ok=True, mode=0o700)
            path.chmod(0o700)

    @staticmethod
    def _no_links(path: Path) -> None:
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise StudioError("symlinks_forbidden")

    def path(self, relative: str) -> Path:
        fragment = Path(relative)
        if not relative or fragment.is_absolute() or ".." in fragment.parts:
            raise StudioError("invalid_workspace_path")
        path = self.root / fragment
        self._no_links(path)
        if not path.resolve().is_relative_to(self.root.resolve()):
            raise StudioError("path_outside_workspace")
        return path

    def write(self, relative: str, content: bytes) -> Path:
        path = self.path(relative)
        # Callers may only write into the fixed directories created above.
        if not path.parent.is_dir():
            raise StudioError("parent_not_found")
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        except FileExistsError as exc:
            raise StudioError("output_already_exists") from exc
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
        return path

    def read(self, relative: str, limit: int = MAX_INPUT_BYTES) -> bytes:
        path = self.path(relative)
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
                raise StudioError("input_not_regular_or_too_large")
            content = stream.read(limit + 1)
        if len(content) > limit:
            raise StudioError("input_too_large")
        return content

    def audit(self, operation: str, object_id: str) -> None:
        record = {
            "operation": operation, "object_id": object_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "report_to_eva": "pending_manual_export",
        }
        self.write(f"audit/{uuid4().hex}.json", json.dumps(record).encode())
