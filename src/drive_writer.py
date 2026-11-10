"""An agent writes its own files to Andrii's Google Drive (10.11.2026).

A service account has no Drive quota and cannot create files in a personal My Drive, so
writing goes through OAuth on Andrii's behalf with the narrowest scope, ``drive.file``:
the agent sees and changes only the files it created itself, never the rest of the Drive.

- One folder per agent, created by the agent: "SYNDICATE Алекс — від Алекса". Andrii may move
  it anywhere; the agent keeps access because it created it.
- ``save_text`` creates a note or replaces the content of the agent's own file of that name.
- ``save_file`` uploads a file from the agent's own Obsidian folder.
- Nothing is ever deleted: this module has no delete call.
- The refresh token lives in Vault ``agents/<id>/google_oauth`` (scripts/syndicate_vault.py
  google-device-login); the agent only reads it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
import structlog

from src.data_paths import ensure_dir
from src.vault_paths import secret_path

logger = structlog.get_logger(__name__)

TOKEN_URL = "https://oauth2.googleapis.com/token"
FILES_URL = "https://www.googleapis.com/drive/v3/files"
UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files"
FOLDER_MIME = "application/vnd.google-apps.folder"
FOLDERS = {"trainer": "SYNDICATE Алекс — від Алекса"}
OWN_VAULT_DIRS = {"trainer": "Health_Coach"}
TEXT_TYPES = {".md": "text/markdown", ".txt": "text/plain", ".csv": "text/csv"}
FILE_TYPES = {**TEXT_TYPES, ".pdf": "application/pdf", ".json": "application/json",
              ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
              ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
              ".png": "image/png", ".jpg": "image/jpeg", ".canvas": "application/json"}
MAX_TEXT_CHARS = 200_000
MAX_FILE_BYTES = 50 * 1024 * 1024
TIMEOUT_S = 60


def oauth_path(agent: str) -> str:
    return f"agents/{agent}/google_oauth"


def safe_name(name: str, default_ext: str = ".md") -> str:
    cleaned = re.sub(r'[\\/:*?"<>|\x00-\x1f]', " ", name).strip().strip(".")
    cleaned = re.sub(r"\s+", " ", cleaned)[:120] or "нотатка"
    return cleaned if Path(cleaned).suffix.lower() in FILE_TYPES else cleaned + default_ext


def _q(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


class DriveWriter:
    def __init__(self, agent: str, credentials: Dict[str, Any], transport: Any = None) -> None:
        self.agent = agent
        self._credentials = credentials
        self._transport = transport
        self._token: Optional[str] = None

    async def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=TIMEOUT_S, transport=self._transport)

    async def _access_token(self, client: httpx.AsyncClient) -> str:
        if self._token:
            return self._token
        response = await client.post(TOKEN_URL, data={
            "client_id": self._credentials["client_id"], "client_secret": self._credentials["client_secret"],
            "refresh_token": self._credentials["refresh_token"], "grant_type": "refresh_token"})
        response.raise_for_status()
        self._token = str(response.json()["access_token"])
        return self._token

    async def _headers(self, client: httpx.AsyncClient) -> Dict[str, str]:
        return {"Authorization": f"Bearer {await self._access_token(client)}"}

    def _state_path(self) -> Path:
        return ensure_dir("drive_writer") / f"{self.agent}.json"

    async def _find(self, client: httpx.AsyncClient, query: str) -> Optional[Dict[str, Any]]:
        response = await client.get(FILES_URL, headers=await self._headers(client),
                                    params={"q": query, "fields": "files(id,name,webViewLink)", "pageSize": 1})
        response.raise_for_status()
        files = response.json().get("files") or []
        return files[0] if files else None

    async def folder_id(self, client: httpx.AsyncClient) -> str:
        """The agent's own folder; created once, found again by the id kept in its state."""
        try:
            known = json.loads(self._state_path().read_text(encoding="utf-8")).get("folder_id")
        except (OSError, ValueError):
            known = None
        if known:
            check = await client.get(f"{FILES_URL}/{known}", headers=await self._headers(client),
                                     params={"fields": "id,trashed"})
            if check.status_code == 200 and not check.json().get("trashed"):
                return str(known)
        name = FOLDERS[self.agent]
        found = await self._find(client, f"name = '{_q(name)}' and mimeType = '{FOLDER_MIME}' and trashed = false")
        if found is None:
            created = await client.post(FILES_URL, headers=await self._headers(client),
                                        params={"fields": "id"}, json={"name": name, "mimeType": FOLDER_MIME})
            created.raise_for_status()
            found = created.json()
        self._state_path().write_text(json.dumps({"folder_id": found["id"]}), encoding="utf-8")
        return str(found["id"])

    async def _put(self, client: httpx.AsyncClient, name: str, data: bytes, mime: str) -> Dict[str, Any]:
        folder = await self.folder_id(client)
        existing = await self._find(client, f"name = '{_q(name)}' and '{_q(folder)}' in parents and trashed = false")
        headers = await self._headers(client)
        fields = {"fields": "id,name,webViewLink"}
        if existing:
            response = await client.patch(f"{UPLOAD_URL}/{existing['id']}", headers={**headers, "Content-Type": mime},
                                          params={**fields, "uploadType": "media"}, content=data)
            action = "updated"
        else:
            metadata = json.dumps({"name": name, "parents": [folder]})
            files = {"metadata": (None, metadata, "application/json; charset=UTF-8"), "file": (name, data, mime)}
            response = await client.post(UPLOAD_URL, headers=headers, params={**fields, "uploadType": "multipart"},
                                         files=files)
            action = "created"
        response.raise_for_status()
        reply = response.json()
        return {"status": "ok", "action": action, "name": reply.get("name", name), "link": reply.get("webViewLink"),
                "folder": FOLDERS[self.agent]}

    async def save_text(self, name: str, text: str) -> Dict[str, Any]:
        if not text.strip() or len(text) > MAX_TEXT_CHARS:
            return {"status": "error", "error": "empty_or_too_long", "max_chars": MAX_TEXT_CHARS}
        target = safe_name(name)
        mime = TEXT_TYPES.get(Path(target).suffix.lower(), "text/markdown")
        async with await self._client() as client:
            return await self._put(client, target, text.encode("utf-8"), mime)

    async def save_file(self, vault_root: Path, path: str) -> Dict[str, Any]:
        own = (vault_root / OWN_VAULT_DIRS[self.agent]).resolve()
        source = (vault_root / path).resolve()
        if own not in source.parents or not source.is_file():
            return {"status": "refused", "reason": "outside_own_folder_or_missing", "path": path}
        mime = FILE_TYPES.get(source.suffix.lower())
        if mime is None:
            return {"status": "refused", "reason": "unsupported_type", "allowed": sorted(FILE_TYPES)}
        if source.stat().st_size > MAX_FILE_BYTES:
            return {"status": "refused", "reason": "file_too_large"}
        async with await self._client() as client:
            return await self._put(client, safe_name(source.name), source.read_bytes(), mime)


async def writer_for(agent: str, vault_client: Any, transport: Any = None) -> Optional[DriveWriter]:
    if agent not in FOLDERS or vault_client is None:
        return None
    try:
        secret = await vault_client.get_secret(secret_path(oauth_path(agent))) or {}
    except Exception:  # noqa: BLE001 - no grant means unavailable, not a crash
        return None
    if not all(secret.get(key) for key in ("client_id", "client_secret", "refresh_token")):
        return None
    return DriveWriter(agent, secret, transport)


async def save(agent: str, vault_client: Any, vault_root: Optional[Path], *, name: str = "", text: str = "",
               path: str = "", transport: Any = None) -> Dict[str, Any]:
    """The gateway tool: a note (name + text) or a file from the agent's own Obsidian folder."""
    writer = await writer_for(agent, vault_client, transport)
    if writer is None:
        return {"status": "unavailable", "reason": "drive_not_authorized",
                "hint": "Andrii runs scripts/syndicate_vault.py google-device-login " + agent}
    try:
        if path:
            if vault_root is None:
                return {"status": "unavailable", "reason": "obsidian_vault_not_mounted"}
            return await writer.save_file(vault_root, path)
        return await writer.save_text(name, text)
    except httpx.HTTPStatusError as exc:
        reason = "grant_revoked" if exc.response.status_code in (400, 401) else f"drive_http_{exc.response.status_code}"
        return {"status": "unavailable", "reason": reason}
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        logger.warning("drive_save_failed", agent=agent, error=type(exc).__name__)
        return {"status": "unavailable", "reason": f"drive_failed: {type(exc).__name__}"}
