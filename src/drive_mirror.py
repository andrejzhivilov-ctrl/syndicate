"""Google Drive folder -> Obsidian vault, one way, for Alex's materials (10.11.2026).

Andrii drops books, courses and lectures into the "Вхідні" folder (inside "SYNDICATE Алекс")
on Google Drive from any device;
this job copies what is new or changed into ``Health_Coach/Матеріали`` in the vault,
where Alex reads it locally (src/material_reader.py) and the nightly backup takes it.

- Alex has his own service account (Vault agents/trainer/google). The folder is found by
  name among the items shared with it, so no
  folder id is configured anywhere. Share it with that account as a Viewer.
- Drive is read with the ``drive.readonly`` scope only; nothing is written to Drive.
- Nothing is deleted from the vault. A file removed in Drive stays and is only counted.
- Google Docs arrive as DOCX; other Google-native files are skipped and counted.
- A missing key or folder is reported as ``unavailable`` with the reason, never as ``ok``.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol, Tuple

import structlog

from src.data_paths import ensure_dir
from src.vault_paths import secret_path

logger = structlog.get_logger(__name__)

#: Each agent sees only what was shared with its own service account, so the same name
#: per agent is unambiguous: "Вхідні" (Andrii writes, agent reads), "Вихідні" (agent edits).
FOLDER_NAME = "Вхідні"
TARGET_DIR = ("Health_Coach", "Матеріали")
SCOPE = "https://www.googleapis.com/auth/drive.readonly"
FOLDER_MIME = "application/vnd.google-apps.folder"
DOC_MIME = "application/vnd.google-apps.document"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MAX_FILE_BYTES = 2 * 1024 ** 3  # a long lecture video; bigger is reported, not fetched
MAX_FILES_PER_RUN = 10  # the rest arrives on the next run
MAX_DEPTH = 5
#: Alex's own service account (scripts/syndicate_vault.py set-google-sa trainer <file>).
KEY_PATH = "agents/trainer/google"


class DriveClient(Protocol):
    def find_folder(self, name: str) -> Optional[str]: ...
    def children(self, folder_id: str) -> List[Dict[str, Any]]: ...
    def download(self, item: Dict[str, Any], dest: Path) -> None: ...


def safe_name(name: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", name).strip().strip(".")
    return cleaned[:150] or "без_назви"


def _version(item: Dict[str, Any]) -> str:
    return str(item.get("md5Checksum") or item.get("modifiedTime") or "")


def walk(client: DriveClient, folder_id: str) -> Iterable[Tuple[Tuple[str, ...], Dict[str, Any]]]:
    """Every file under the folder, with its sub-folder path; depth-capped."""
    stack: List[Tuple[str, Tuple[str, ...]]] = [(folder_id, ())]
    while stack:
        current, prefix = stack.pop()
        for item in client.children(current):
            if item.get("mimeType") == FOLDER_MIME:
                if len(prefix) < MAX_DEPTH:
                    stack.append((item["id"], prefix + (safe_name(item.get("name", "")),)))
                continue
            yield prefix, item


def _local_name(item: Dict[str, Any]) -> Optional[str]:
    """File name in the vault; None for a Google-native file other than a Doc."""
    mime = str(item.get("mimeType", ""))
    name = safe_name(str(item.get("name", "")))
    if mime == DOC_MIME:
        return name if name.lower().endswith(".docx") else f"{name}.docx"
    return None if mime.startswith("application/vnd.google-apps.") else name


def _state_path() -> Path:
    return ensure_dir("drive_mirror") / "state.json"


def _load_state() -> Dict[str, Dict[str, str]]:
    try:
        return json.loads(_state_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save_state(state: Dict[str, Dict[str, str]]) -> None:
    path = _state_path()
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(temp, path)


def _fetch(client: DriveClient, item: Dict[str, Any], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(dest.name + ".part")
    try:
        client.download(item, partial)
        os.replace(partial, dest)
    finally:
        partial.unlink(missing_ok=True)


def _plan(prefix: Tuple[str, ...], item: Dict[str, Any], state: Dict[str, Dict[str, str]],
          target: Path) -> Tuple[str, str]:
    """What to do with one Drive file: copy, or the counter it lands in."""
    name = _local_name(item)
    if name is None:
        return "skipped_native", ""
    if int(item.get("size") or 0) > MAX_FILE_BYTES:
        return "too_large", ""
    relative = "/".join(prefix + (name,))
    if state.get(item["id"], {}).get("version") == _version(item) and (target / relative).is_file():
        return "unchanged", relative
    return "copy", relative


def _copy(client: DriveClient, item: Dict[str, Any], target: Path, relative: str,
          state: Dict[str, Dict[str, str]]) -> str:
    try:
        _fetch(client, item, target / relative)
    except Exception as exc:  # noqa: BLE001 - one bad file never stops the others
        logger.warning("drive_mirror_file_failed", file=relative, error=type(exc).__name__)
        return "failed"
    state[item["id"]] = {"path": relative, "version": _version(item)}
    return "copied"


def mirror(client: DriveClient, vault_root: Path) -> Dict[str, Any]:
    """One pass: copy new or changed files; report everything that was not copied."""
    folder_id = client.find_folder(FOLDER_NAME)
    if not folder_id:
        return {"status": "unavailable", "reason": "drive_folder_not_shared", "folder": FOLDER_NAME}
    target = vault_root.joinpath(*TARGET_DIR)
    state = _load_state()
    counts = {"copied": 0, "unchanged": 0, "skipped_native": 0, "too_large": 0, "failed": 0, "deferred": 0}
    seen = set()
    for prefix, item in walk(client, folder_id):
        seen.add(item["id"])
        verdict, relative = _plan(prefix, item, state, target)
        if verdict == "copy" and counts["copied"] + counts["failed"] >= MAX_FILES_PER_RUN:
            verdict = "deferred"
        if verdict == "copy":
            verdict = _copy(client, item, target, relative, state)
        counts[verdict] += 1
    _save_state(state)
    removed = len(set(state) - seen)
    status = "ok" if counts["failed"] == 0 else "partial"
    return {"status": status, **counts, "removed_in_drive_kept": removed, "folder": FOLDER_NAME}


# ── the real Drive, read only ─────────────────────────────────────────────────────────────


class GoogleDrive:
    """googleapiclient behind the DriveClient protocol, with the read-only scope."""

    _FIELDS = "nextPageToken, files(id, name, mimeType, md5Checksum, modifiedTime, size)"

    def __init__(self, service_account_info: Dict[str, Any]) -> None:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build

        credentials = Credentials.from_service_account_info(service_account_info, scopes=[SCOPE])
        self._drive = build("drive", "v3", credentials=credentials, cache_discovery=False)

    def _list(self, query: str) -> List[Dict[str, Any]]:
        items, token = [], None
        while True:
            page = self._drive.files().list(q=query, fields=self._FIELDS, pageSize=200, pageToken=token,
                                            supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
            items += page.get("files", [])
            token = page.get("nextPageToken")
            if not token:
                return items

    def find_folder(self, name: str) -> Optional[str]:
        escaped = name.replace("\\", "\\\\").replace("'", "\\'")
        found = self._list(f"name = '{escaped}' and mimeType = '{FOLDER_MIME}' and trashed = false")
        return found[0]["id"] if found else None

    def children(self, folder_id: str) -> List[Dict[str, Any]]:
        return self._list(f"'{folder_id}' in parents and trashed = false")

    def download(self, item: Dict[str, Any], dest: Path) -> None:
        from googleapiclient.http import MediaIoBaseDownload

        files = self._drive.files()
        if item.get("mimeType") == DOC_MIME:
            request = files.export_media(fileId=item["id"], mimeType=DOCX_MIME)
        else:
            request = files.get_media(fileId=item["id"], supportsAllDrives=True)
        with dest.open("wb") as stream:
            downloader = MediaIoBaseDownload(stream, request, chunksize=16 * 1024 * 1024)
            done = False
            while not done:
                _, done = downloader.next_chunk()


async def run(vault_client: Any) -> Dict[str, Any]:
    """The scheduled job: key from Vault, vault from the environment, one mirror pass."""
    import asyncio

    from src.obsidian_notes import vault_dir_from_env

    root = vault_dir_from_env()
    if root is None:
        return {"status": "unavailable", "reason": "obsidian_vault_not_mounted"}
    try:
        secret = await vault_client.get_secret(secret_path(KEY_PATH)) if vault_client else None
    except Exception as exc:  # noqa: BLE001
        return {"status": "unavailable", "reason": f"vault_read_failed: {type(exc).__name__}"}
    raw = (secret or {}).get("service_account_json")
    if not raw:
        return {"status": "unavailable", "reason": "no_service_account_json_in_vault"}
    try:
        client = GoogleDrive(json.loads(raw))
    except Exception as exc:  # noqa: BLE001 - a malformed key is reported, not raised
        return {"status": "unavailable", "reason": f"service_account_invalid: {type(exc).__name__}"}
    return await asyncio.to_thread(mirror, client, root)
