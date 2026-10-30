"""Two-way sync between the Obsidian vault on the server and the Garage bucket.

Operator decision 29.10: Garage is the hub. Andrii's PC and phone sync to the
``obsidian-vault`` bucket with the Remotely Save plugin (their own key, shown to
him by ``scripts/syndicate_vault.py obsidian-key --reveal``); this loop keeps
``OBSIDIAN_VAULT_DIR`` and the bucket in step with ``rclone bisync`` so Eva can
read and write plain Markdown files.

Credentials are Eva's own Garage key from Vault (``agents/eva/storage``), passed
to rclone through environment variables only (never argv, never a file).
"""
from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from src.vault_paths import STORAGE, agent_secret_path

logger = structlog.get_logger(__name__)

OBSIDIAN_BUCKET = "obsidian-vault"
SYNC_INTERVAL_S = 120
RUN_TIMEOUT_S = 600
_REMOTE = "garage"


def rclone_env(key: Dict[str, Any], workdir: Path) -> Dict[str, str]:
    """An on-the-fly rclone remote for Garage; the secret only ever lives in this env."""
    return {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": str(workdir),
        "XDG_CACHE_HOME": str(workdir / "cache"),
        "RCLONE_CONFIG": str(workdir / "rclone.conf"),
        f"RCLONE_CONFIG_{_REMOTE.upper()}_TYPE": "s3",
        f"RCLONE_CONFIG_{_REMOTE.upper()}_PROVIDER": "Other",
        f"RCLONE_CONFIG_{_REMOTE.upper()}_ENDPOINT": str(key.get("endpoint") or "http://garage:3900"),
        f"RCLONE_CONFIG_{_REMOTE.upper()}_REGION": "garage",
        f"RCLONE_CONFIG_{_REMOTE.upper()}_FORCE_PATH_STYLE": "true",
        f"RCLONE_CONFIG_{_REMOTE.upper()}_ACCESS_KEY_ID": str(key["access_key_id"]),
        f"RCLONE_CONFIG_{_REMOTE.upper()}_SECRET_ACCESS_KEY": str(key["secret_access_key"]),
    }


def bisync_args(local_dir: Path, workdir: Path, *, resync: bool) -> List[str]:
    args = ["rclone", "bisync", str(local_dir), f"{_REMOTE}:{OBSIDIAN_BUCKET}",
            "--workdir", str(workdir / "bisync"),
            "--resilient", "--recover", "--max-lock", "5m",
            "--conflict-resolve", "newer", "--conflict-loser", "num",
            "--create-empty-src-dirs", "--compare", "size,modtime",
            "--exclude", ".obsidian/workspace*.json", "--exclude", ".trash/**",
            "--log-level", "NOTICE"]
    if resync:
        args.append("--resync")  # first run: build the baseline from both sides
    return args


class ObsidianSync:
    """Runs ``rclone bisync`` every few minutes; a failed run is logged, never fatal."""

    def __init__(self, vault: Any, local_dir: Path, workdir: Path) -> None:
        self._vault = vault
        self._local = local_dir
        self._workdir = workdir

    def _baseline_exists(self) -> bool:
        listings = self._workdir / "bisync"
        return listings.is_dir() and any(listings.glob("*.lst"))

    async def run_once(self) -> Dict[str, Any]:
        if shutil.which("rclone") is None:
            return {"status": "unavailable", "reason": "rclone_not_installed"}
        try:
            key = await self._vault.get_secret(agent_secret_path("eva", STORAGE))
        except Exception as exc:  # noqa: BLE001
            return {"status": "unavailable", "reason": "storage_key_unreadable", "error_type": type(exc).__name__}
        if not key or not key.get("access_key_id") or not key.get("secret_access_key"):
            return {"status": "unavailable", "reason": "storage_key_missing"}
        (self._workdir / "bisync").mkdir(parents=True, exist_ok=True)
        (self._workdir / "rclone.conf").touch(exist_ok=True)
        resync = not self._baseline_exists()
        proc = await asyncio.create_subprocess_exec(
            *bisync_args(self._local, self._workdir, resync=resync),
            env=rclone_env(key, self._workdir),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        try:
            _, err = await asyncio.wait_for(proc.communicate(), timeout=RUN_TIMEOUT_S)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return {"status": "error", "reason": "timeout"}
        if proc.returncode != 0:
            tail = err.decode("utf-8", "replace").strip().splitlines()[-3:]
            return {"status": "error", "reason": f"rclone_exit_{proc.returncode}", "detail": tail, "resync": resync}
        return {"status": "ok", "resync": resync}

    async def loop(self) -> None:
        while True:
            try:
                result = await self.run_once()
            except Exception as exc:  # noqa: BLE001 - the loop must survive any single run
                result = {"status": "error", "reason": "exception", "error_type": type(exc).__name__}
            if result["status"] == "ok":
                logger.info("obsidian_sync_ok", resync=result.get("resync"))
            else:
                logger.warning("obsidian_sync_failed", **{k: v for k, v in result.items() if k != "status"})
            await asyncio.sleep(SYNC_INTERVAL_S)


def from_env(vault: Any) -> Optional[ObsidianSync]:
    """The sync loop when the vault directory is mounted; None otherwise (sync is off)."""
    local = os.environ.get("OBSIDIAN_VAULT_DIR")
    data = os.environ.get("EVA_DATA_DIR")
    if not local or not data or not Path(local).is_dir():
        return None
    return ObsidianSync(vault, Path(local), Path(data) / "obsidian_sync")
