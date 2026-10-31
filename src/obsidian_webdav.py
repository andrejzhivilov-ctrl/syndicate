"""WebDAV door to the Obsidian vault on the server.

Operator decision 31.10: Obsidian is the archive and Garage is the agents' working
memory, so the vault no longer passes through a bucket. The Remotely Save plugin on
Andrii's PC and phone talks WebDAV directly to ``OBSIDIAN_VAULT_DIR``, the same files
Eva and KODEX read, so there is no copy to keep in step.

``rclone serve webdav`` runs inside eva-agent, reachable only through nginx on
``sync.syndicateholding.com``. The login comes from Vault (``agents/eva/obsidian``) and
reaches rclone through the environment only, never argv or a file.
"""
from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from src.vault_paths import agent_secret_path

logger = structlog.get_logger(__name__)

WEBDAV_PORT = 8081
REMOTE_BASE_DIR = "vault"  # the plugin always works inside a named folder: this one is the vault root
OBSIDIAN_SECRET = "obsidian"
RETRY_S = 60


def serve_env(creds: Dict[str, Any], workdir: Path) -> Dict[str, str]:
    """The login lives only in this environment; HOME and the cache point at writable data."""
    return {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": str(workdir),
        "XDG_CACHE_HOME": str(workdir / "cache"),
        "RCLONE_CONFIG": str(workdir / "rclone.conf"),
        "RCLONE_USER": str(creds["webdav_user"]),
        "RCLONE_PASS": str(creds["webdav_password"]),
    }


def serve_args(local_dir: Path, workdir: Path) -> List[str]:
    return ["rclone", "serve", "webdav", str(local_dir),
            "--addr", f"0.0.0.0:{WEBDAV_PORT}", "--baseurl", REMOTE_BASE_DIR,
            "--cache-dir", str(workdir / "cache"),
            "--dir-cache-time", "5s",  # notes written by agents show up at once
            "--log-level", "NOTICE"]


class ObsidianWebDAV:
    """Keeps the WebDAV server running; a missing login or a crash is logged, never fatal."""

    def __init__(self, vault: Any, local_dir: Path, workdir: Path) -> None:
        self._vault = vault
        self._local = local_dir
        self._workdir = workdir

    async def _credentials(self) -> Optional[Dict[str, Any]]:
        try:
            creds = await self._vault.get_secret(agent_secret_path("eva", OBSIDIAN_SECRET))
        except Exception as exc:  # noqa: BLE001
            logger.warning("obsidian_webdav_login_unreadable", error_type=type(exc).__name__)
            return None
        if not creds or not creds.get("webdav_user") or not creds.get("webdav_password"):
            logger.warning("obsidian_webdav_login_missing", hint="scripts/syndicate_vault.py obsidian-webdav --reveal")
            return None
        return creds

    async def run_once(self) -> Dict[str, Any]:
        if shutil.which("rclone") is None:
            return {"status": "unavailable", "reason": "rclone_not_installed"}
        creds = await self._credentials()
        if creds is None:
            return {"status": "unavailable", "reason": "login_missing"}
        self._workdir.mkdir(parents=True, exist_ok=True)
        (self._workdir / "rclone.conf").touch(exist_ok=True)
        proc = await asyncio.create_subprocess_exec(
            *serve_args(self._local, self._workdir), env=serve_env(creds, self._workdir),
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE,
        )
        logger.info("obsidian_webdav_started", port=WEBDAV_PORT)
        try:
            _, err = await proc.communicate()
        except asyncio.CancelledError:
            proc.terminate()
            await proc.wait()
            raise
        tail = err.decode("utf-8", "replace").strip().splitlines()[-3:]
        return {"status": "error", "reason": f"rclone_exit_{proc.returncode}", "detail": tail}

    async def loop(self) -> None:
        while True:
            try:
                result = await self.run_once()
            except Exception as exc:  # noqa: BLE001 - the door must come back after any failure
                result = {"status": "error", "reason": "exception", "error_type": type(exc).__name__}
            logger.warning("obsidian_webdav_stopped", **{k: v for k, v in result.items() if k != "status"})
            await asyncio.sleep(RETRY_S)


def from_env(vault: Any) -> Optional[ObsidianWebDAV]:
    """The server when the vault directory is mounted; None otherwise."""
    local = os.environ.get("OBSIDIAN_VAULT_DIR")
    data = os.environ.get("EVA_DATA_DIR")
    if not local or not data or not Path(local).is_dir():
        return None
    return ObsidianWebDAV(vault, Path(local), Path(data) / "obsidian_webdav")
