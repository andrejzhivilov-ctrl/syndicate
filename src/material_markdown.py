"""Every material becomes Markdown in Obsidian; the original lives on Google Drive (18.11.2026).

Andrii: the server keeps knowledge as Markdown only; originals are stored elsewhere (Google Drive
now, OneDrive or an own store later); agents read Markdown and spend few tokens. For each file
Eva has shelved (src/material_sorter.py) this job writes a card ``<file>.md`` next to it:

- properties first: summary, tags, kind, size, where the original is;
- then the content: the full text of documents, tables and slides (src/material_reader.py), the
  timed transcript of audio and video (Deepgram, Groq as the fallback), the description and the
  text of an image (a vision model).

Then the original leaves the server, but only when it is safe on Drive: a file mirrored from Drive
is checked there by its id; a file that came through the chat is uploaded to Eva's Drive folder
first (images and WAV made smaller without loss on the way). With no way to keep the original on
Drive it stays on the server and the card says so. A file that cannot be read keeps its original.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import structlog

from src import lecture_transcriber, material_reader, media_vision, telegram_files
from src.data_paths import ensure_dir

logger = structlog.get_logger(__name__)

CARD_SUFFIX = ".md"
IMAGE_MIME = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp", "gif": "image/gif"}
MEDIA = lecture_transcriber.MEDIA_EXTENSIONS
TEXT = material_reader.EXTENSIONS - {"md"}
MAX_PER_RUN = 5
MAX_MEDIA_PER_RUN = 1
#: A lone Markdown or service file is not a material to convert.
SKIP_NAMES = frozenset({"Каталог.md"})
LIBRARY = "library"  # media_vision prompt for the knowledge base


def card_path(original: Path) -> Path:
    return original.with_name(original.name + CARD_SUFFIX)


def _now() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _md5(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def pending(folder: Path) -> List[Path]:
    """Originals in an agent's materials without a card yet; Markdown and transcripts are not originals."""
    if not folder.is_dir():
        return []
    found = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.parent == folder:
            continue  # not shelved yet: Eva first gives it a topic
        if any(part.startswith(".") or part == "_Дублікати" for part in path.relative_to(folder).parts):
            continue
        name = path.name
        if name.endswith((CARD_SUFFIX, material_reader.TRANSCRIPT_SUFFIX, ".part")) or name in SKIP_NAMES:
            continue
        if not card_path(path).exists():
            found.append(path)
    return found


# ── content ───────────────────────────────────────────────────────────────────────────────


async def _media_text(path: Path, keys: Dict[str, Any]) -> Dict[str, Any]:
    """A transcript already beside the file, else Deepgram (Andrii's credit), else Groq."""
    beside = path.with_name(path.name + material_reader.TRANSCRIPT_SUFFIX)
    if beside.is_file():
        return {"status": "ok", "text": beside.read_text(encoding="utf-8", errors="replace"), "by": "earlier",
                "consumed": beside}
    if keys.get(lecture_transcriber.KEY_NAME):
        heard = await lecture_transcriber.transcribe_one(path, str(keys[lecture_transcriber.KEY_NAME]))
        if heard["status"] == "ok":
            return {"status": "ok", "text": beside.read_text(encoding="utf-8"), "by": "deepgram", "consumed": beside}
        if heard.get("reason") in lecture_transcriber.PERMANENT:
            return {"status": "unavailable", "reason": heard["reason"]}
    heard = await telegram_files.transcribe(path, keys)
    return {**heard, "by": "groq"} if heard["status"] == "ok" else heard


async def _image_text(path: Path, keys: Dict[str, Any]) -> Dict[str, Any]:
    mime = IMAGE_MIME[path.suffix.lower().lstrip(".")]
    data = path.read_bytes()
    if len(data) > media_vision.MAX_IMAGE_BYTES:
        return {"status": "unavailable", "reason": "image_too_large"}
    seen = await media_vision.describe(LIBRARY, data, mime, "", str(keys.get("openrouter_api_key") or ""))
    return {"status": "ok", "text": seen["description"], "by": "vision"} if seen["status"] == "ok" else seen


async def content(path: Path, keys: Dict[str, Any]) -> Dict[str, Any]:
    """The Markdown body of one file, or why there is none (never a guess)."""
    ext = path.suffix.lower().lstrip(".")
    if ext in TEXT:
        try:
            text = await asyncio.to_thread(material_reader.extract_text, ext, path.read_bytes())
        except material_reader.MaterialError as exc:
            return {"status": "unavailable", "reason": str(exc), "kind": "document"}
        return {"status": "ok", "text": text, "by": "text", "kind": "document"}
    if ext in MEDIA:
        return {**await _media_text(path, keys), "kind": "audio_video"}
    if ext in IMAGE_MIME:
        return {**await _image_text(path, keys), "kind": "image"}
    return {"status": "unavailable", "reason": "unsupported_format", "kind": "other"}


def render(path: Path, body: Dict[str, Any], entry: Dict[str, Any], original: str) -> str:
    title = entry.get("title") or path.stem
    summary = (entry.get("summary") or "").replace('"', "'")
    props = {"summary": summary, "title": title, "kind": body.get("kind"), "topic": entry.get("topic", ""),
             "language": entry.get("language", ""), "original_name": path.name, "original": original,
             "size_bytes": path.stat().st_size, "converted": _now(), "converted_by": body.get("by", "")}
    lines = ["---", *[f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in props.items()], "---", "",
             f"# {title}", ""]
    if summary:
        lines += [f"> {summary}", ""]
    if body["status"] == "ok":
        text = str(body["text"])
        if text.startswith("---"):  # a transcript's own properties are not repeated
            text = text.split("---", 2)[-1].strip()
        lines.append(text)
    else:
        lines.append(f"Вміст не розпізнано: {body.get('reason')}. Оригінал: {original}.")
    return "\n".join(lines).rstrip() + "\n"


# ── where the original goes ───────────────────────────────────────────────────────────────


def lossless(path: Path) -> Path:
    """Smaller without loss on the way to Drive: PNG re-packed, WAV to FLAC; the rest as it is."""
    ext = path.suffix.lower()
    try:
        if ext == ".png":
            from PIL import Image

            out = path.with_name(path.stem + ".min.png")
            with Image.open(path) as image:
                image.save(out, optimize=True)
            return out if out.stat().st_size < path.stat().st_size else _drop(out, path)
        if ext == ".wav":
            out = path.with_suffix(".flac")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-c:a", "flac", str(out)],
                           capture_output=True, timeout=900, check=True)
            return out
    except Exception as exc:  # noqa: BLE001 - the original goes as it is
        logger.warning("lossless_failed", error_type=type(exc).__name__)
    return path


def _drop(extra: Path, keep: Path) -> Path:
    extra.unlink(missing_ok=True)
    return keep


def drive_original(path: Path, mirrored: Dict[str, Dict[str, str]]) -> Optional[str]:
    """The Drive id of a file mirrored from Drive: by content (Drive's md5), else by name for an exported Doc."""
    md5 = _md5(path)
    by_content = next((file_id for file_id, info in mirrored.items() if info.get("version") == md5), None)
    if by_content:
        return by_content
    return next((file_id for file_id, info in mirrored.items()
                 if Path(str(info.get("path", ""))).name == path.name and not _is_md5(info.get("version", ""))), None)


def _is_md5(value: str) -> bool:
    return len(value) == 32 and all(ch in "0123456789abcdef" for ch in value)


Uploader = Callable[[str, bytes], Any]  # (name, data) -> {"id": ...}
Checker = Callable[[str], Any]  # drive id -> bool


async def place_original(path: Path, mirrored: Dict[str, Dict[str, str]], checker: Optional[Checker],
                         uploader: Optional[Uploader]) -> Dict[str, Any]:
    """Where the original is now: on Drive (and gone from the server), or still here and why."""
    file_id = drive_original(path, mirrored)
    if file_id and checker is not None and await checker(file_id):
        return {"where": f"https://drive.google.com/file/d/{file_id}/view", "remove": True}
    if file_id:
        return {"where": "сервер (на Drive не підтверджено)", "remove": False}
    if uploader is None:
        return {"where": "сервер (запису на Drive немає)", "remove": False}
    packed = await asyncio.to_thread(lossless, path)
    try:
        reply = await uploader(packed.name, packed.read_bytes())
    except Exception as exc:  # noqa: BLE001 - the original stays until it is safely on Drive
        logger.warning("original_upload_failed", error_type=type(exc).__name__)
        return {"where": "сервер (завантаження на Drive не вдалося)", "remove": False}
    finally:
        if packed != path:
            packed.unlink(missing_ok=True)
    if not reply or not reply.get("id"):
        return {"where": "сервер (Drive не підтвердив)", "remove": False}
    return {"where": f"https://drive.google.com/file/d/{reply['id']}/view", "remove": True}


# ── one run ───────────────────────────────────────────────────────────────────────────────


def _log(entry: Dict[str, Any]) -> None:
    with (ensure_dir("material_sorter") / "markdown.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"at": _now(), **entry}, ensure_ascii=False) + "\n")


async def convert_one(path: Path, entry: Dict[str, Any], keys: Dict[str, Any], mirrored: Dict[str, Dict[str, str]],
                      checker: Optional[Checker], uploader: Optional[Uploader]) -> Dict[str, Any]:
    body = await content(path, keys)
    if body["status"] != "ok" and body.get("reason") in ("monthly_minutes_cap", "no_groq_key", "model_key_unavailable",
                                                          "daily_limit_reached", "transcription_failed", "vision_failed"):
        return {"file": path.name, "status": "later", "reason": body.get("reason")}  # try again next run
    placed = await place_original(path, mirrored, checker, uploader) if body["status"] == "ok" \
        else {"where": "сервер (вміст не розпізнано, оригінал лишається)", "remove": False}
    card_path(path).write_text(render(path, body, entry, placed["where"]), encoding="utf-8")
    consumed = body.get("consumed")
    if isinstance(consumed, Path):
        consumed.unlink(missing_ok=True)  # its text is inside the card now
    if placed["remove"]:
        path.unlink(missing_ok=True)
    result = {"file": path.name, "status": body["status"], "kind": body.get("kind"), "original": placed["where"],
              "removed_from_server": placed["remove"]}
    _log(result)
    return result


def _entry_for(path: Path, folder: Path, state: Dict[str, Any]) -> Dict[str, Any]:
    relative = path.relative_to(folder).as_posix()
    entry = state.get("files", {}).get(relative)
    if entry is None:  # a file inside a course folder takes the course's entry
        entry = next((e for p, e in state.get("files", {}).items() if relative.startswith(p + "/")), {})
    return entry


async def convert_folder(folder: Path, state: Dict[str, Any], keys: Dict[str, Any], mirrored: Dict[str, Dict[str, str]],
                         checker: Optional[Checker], uploader: Optional[Uploader]) -> List[Dict[str, Any]]:
    done, media = [], 0
    for path in pending(folder):
        if len(done) >= MAX_PER_RUN:
            break
        if path.suffix.lower().lstrip(".") in MEDIA:
            if media >= MAX_MEDIA_PER_RUN:
                continue
            media += 1
        try:
            done.append(await convert_one(path, _entry_for(path, folder, state), keys, mirrored, checker, uploader))
        except OSError as exc:
            logger.warning("markdown_convert_failed", file=path.name, error_type=type(exc).__name__)
    return done


async def run(gateway: Any) -> Dict[str, Any]:
    """The scheduled job: every agent's shelved materials, a few files a run."""
    from src import drive_mirror, drive_writer, material_sorter
    from src.obsidian_notes import vault_dir_from_env
    from src.vault_paths import secret_path

    root = vault_dir_from_env()
    if root is None:
        return {"status": "unavailable", "reason": "obsidian_vault_not_mounted"}
    vault = getattr(gateway, "vault", None)
    try:
        keys = (await vault.get_secret(secret_path("api-keys")) if vault else None) or {}
    except Exception:  # noqa: BLE001 - documents still convert without keys
        keys = {}
    mirrored: Dict[str, Dict[str, str]] = {}
    for agent in drive_mirror.MIRRORS:
        mirrored.update(drive_mirror._load_state(agent))
    checker = await _checker(vault)
    writer = await drive_writer.writer_for("eva", vault) if vault else None
    uploader = (lambda name, data: writer.save_bytes(name, data)) if writer else None
    report: Dict[str, Any] = {"status": "ok", "converted": []}
    for agent, (parts, _topics) in material_sorter.SHELVES.items():
        state = material_sorter.load_state(agent)
        report["converted"] += await convert_folder(root.joinpath(*parts), state, keys, mirrored, checker, uploader)
    return report


async def _checker(vault: Any) -> Optional[Checker]:
    """Drive read access to confirm an original before its vault copy goes (any mirror's key will do)."""
    from src import drive_mirror
    from src.vault_paths import secret_path

    clients = []
    for key_path, _target, _state in drive_mirror.MIRRORS.values():
        try:
            secret = await vault.get_secret(secret_path(key_path)) if vault else None
            raw = (secret or {}).get("service_account_json")
            if raw:
                clients.append(drive_mirror.GoogleDrive(json.loads(raw)))
        except Exception:  # noqa: BLE001 - no reader: originals simply stay
            continue
    if not clients:
        return None

    async def check(file_id: str) -> bool:
        # Each service account sees only what was shared with it: Eva's inbox or Alex's.
        for client in clients:
            if await asyncio.to_thread(client.exists, file_id):
                return True
        return False

    return check

