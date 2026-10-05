"""Writable-data path resolution for EVA SYNDICATE.

Several subsystems persist state to disk (the Markdown ground-truth vault,
rendered videos / mockups, anti-detect browser profiles). The production
container runs with ``read_only: true`` and only ``/tmp`` writable, so any of
these that defaulted to a path relative to the CWD raised ``PermissionError``
during startup — the agent could not boot at all.

Set ``EVA_DATA_DIR`` to move every writable artefact under one mount point
(e.g. ``/data/eva``). When it is unset the historical repository-relative
layout is kept so local development and the sandbox tests behave as before.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union

ENV_VAR = "EVA_DATA_DIR"

#: Logical sub-directories below the data root.
DIRS = {
    "vault": "vault_md",
    "videos": "media/videos",
    "mockups": "media/mockups",
    "captions": "media/captions",
    "broll_cache": "media/broll_cache",
    "browser_profiles": "config/browser_profiles",
    "reports": "media/reports",
}


def data_root() -> Optional[Path]:
    """Return the configured writable root, or ``None`` when unset."""
    raw = os.getenv(ENV_VAR)
    if not raw or not raw.strip():
        return None
    return Path(raw.strip()).expanduser().resolve()


def data_dir(key: str, default: Optional[Union[str, Path]] = None) -> Path:
    """Resolve a writable directory for ``key``.

    Falls back to ``default`` (or the repository-relative legacy path) when
    ``EVA_DATA_DIR`` is not configured.
    """
    fallback = Path(default) if default is not None else Path(DIRS[key])
    root = data_root()
    if root is None or fallback.is_absolute():
        return fallback
    return root / DIRS.get(key, str(fallback))


def ensure_dir(key: str, default: Optional[Union[str, Path]] = None) -> Path:
    """Resolve and create (``mkdir -p``) a writable directory."""
    path = data_dir(key, default)
    path.mkdir(parents=True, exist_ok=True)
    return path
