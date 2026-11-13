"""Course videos and audio in the vault become text Alex can read (10.11.2026).

A lecture that arrives in ``Health_Coach/Матеріали`` (src/drive_mirror.py) is turned into
``<name>.розшифровка.md`` next to it, which material_list and material_read then serve.

- Deepgram Nova-3, Ukrainian, from the $200 credit Andrii received; ``mip_opt_out=true`` on
  every request, so Deepgram does not keep the audio for model training.
- Only the audio leaves the server: ffmpeg cuts a mono 16 kHz Opus track (about 7 MB an hour).
- A monthly cap on minutes keeps a mistake from spending the credit; over the cap is reported.
- No key, no ffmpeg, a failed call: ``unavailable`` with the reason, never an empty transcript.
"""
from __future__ import annotations

import asyncio
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import structlog

from src.data_paths import ensure_dir
from src.drive_mirror import TARGET_DIR
from src.material_reader import TRANSCRIPT_SUFFIX as SUFFIX
from src.vault_paths import secret_path

logger = structlog.get_logger(__name__)

MEDIA_EXTENSIONS = frozenset({"mp4", "mkv", "mov", "webm", "avi", "mp3", "m4a", "wav", "ogg", "opus", "flac", "aac"})
DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"
PARAMS = {"model": "nova-3", "language": "uk", "smart_format": "true", "paragraphs": "true",
          "mip_opt_out": "true"}
KEY_NAME = "deepgram_api_key"
#: About 20 hours a month; Nova-3 is well under a cent a minute, so this is a few dollars.
MONTHLY_MINUTES_CAP = 1200
MAX_PER_RUN = 1
FFMPEG_TIMEOUT_S = 900
REQUEST_TIMEOUT_S = 600


def transcript_path(media: Path) -> Path:
    return media.with_name(media.name + SUFFIX)


def pending(folder: Path) -> List[Path]:
    """Media files without a transcript, oldest first."""
    if not folder.is_dir():
        return []
    found = [path for path in folder.rglob("*") if path.is_file()
             and path.suffix.lower().lstrip(".") in MEDIA_EXTENSIONS and not transcript_path(path).exists()]
    return sorted(found, key=lambda path: path.stat().st_mtime)


# ── the monthly cap ───────────────────────────────────────────────────────────────────────


def _usage_path() -> Path:
    return ensure_dir("transcription") / "usage.json"


def _month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def minutes_used() -> float:
    try:
        data = json.loads(_usage_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0.0
    return float(data.get(_month(), 0.0))


def _add_minutes(minutes: float) -> None:
    path = _usage_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    data[_month()] = round(float(data.get(_month(), 0.0)) + minutes, 2)
    path.write_text(json.dumps(data), encoding="utf-8")


# ── audio and the call ────────────────────────────────────────────────────────────────────


def duration_minutes(media: Path) -> Optional[float]:
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                              str(media)], capture_output=True, text=True, timeout=60, check=True)
        return float(out.stdout.strip()) / 60
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def extract_audio(media: Path, dest: Path) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(media), "-vn", "-ac", "1", "-ar", "16000",
                    "-c:a", "libopus", "-b:a", "16k", str(dest)],
                   capture_output=True, timeout=FFMPEG_TIMEOUT_S, check=True)


async def deepgram(audio: bytes, key: str, transport: Any = None) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S, transport=transport) as client:
        response = await client.post(DEEPGRAM_URL, params=PARAMS, content=audio,
                                     headers={"Authorization": f"Token {key}", "Content-Type": "audio/ogg"})
    response.raise_for_status()
    return response.json()


def _stamp(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 3600:d}:{total % 3600 // 60:02d}:{total % 60:02d}"


def render(media_name: str, reply: Dict[str, Any]) -> Optional[str]:
    """Markdown with a timestamp per paragraph; None when Deepgram heard no speech."""
    try:
        alternative = reply["results"]["channels"][0]["alternatives"][0]
    except (KeyError, IndexError, TypeError):
        return None
    paragraphs = (alternative.get("paragraphs") or {}).get("paragraphs") or []
    lines = []
    for paragraph in paragraphs:
        text = " ".join(sentence.get("text", "") for sentence in paragraph.get("sentences", [])).strip()
        if text:
            lines.append(f"**[{_stamp(paragraph.get('start', 0))}]** {text}")
    body = "\n\n".join(lines) or str(alternative.get("transcript") or "").strip()
    if not body:
        return None
    return (f"---\nsource: {media_name}\ntranscribed_by: deepgram nova-3\n"
            f"transcribed_at: {datetime.now(timezone.utc).date().isoformat()}\n---\n\n"
            f"# Розшифровка: {media_name}\n\nМашинна розшифровка: імена й терміни перевіряй з відео.\n\n{body}\n")


async def transcribe_one(media: Path, key: str, transport: Any = None) -> Dict[str, Any]:
    minutes = duration_minutes(media)
    if minutes is None:
        return {"status": "unavailable", "reason": "not_readable_media", "file": media.name}
    if minutes_used() + minutes > MONTHLY_MINUTES_CAP:
        return {"status": "unavailable", "reason": "monthly_minutes_cap", "cap": MONTHLY_MINUTES_CAP,
                "used": minutes_used(), "file": media.name}
    with tempfile.TemporaryDirectory() as tmp:
        audio = Path(tmp) / "audio.ogg"
        try:
            await asyncio.to_thread(extract_audio, media, audio)
        except (OSError, subprocess.SubprocessError):
            return {"status": "unavailable", "reason": "audio_extraction_failed", "file": media.name}
        try:
            reply = await deepgram(audio.read_bytes(), key, transport)
        except httpx.HTTPStatusError as exc:
            return {"status": "unavailable", "reason": f"deepgram_http_{exc.response.status_code}", "file": media.name}
        except httpx.HTTPError as exc:
            return {"status": "unavailable", "reason": f"deepgram_unreachable: {type(exc).__name__}", "file": media.name}
    _add_minutes(minutes)  # Deepgram bills the call even when nothing was heard
    text = render(media.name, reply)
    if text is None:
        return {"status": "unavailable", "reason": "no_speech_heard", "file": media.name, "minutes": round(minutes, 1)}
    transcript_path(media).write_text(text, encoding="utf-8")
    return {"status": "ok", "file": media.name, "minutes": round(minutes, 1)}


#: Failures that a retry cannot fix: a note takes the file out of the queue.
PERMANENT = frozenset({"not_readable_media", "audio_extraction_failed", "no_speech_heard"})


def write_failure_note(media: Path, reason: str) -> None:
    """An honest note in place of a transcript, so one bad file never blocks the queue."""
    transcript_path(media).write_text(
        f"---\nsource: {media.name}\ntranscript: none\nreason: {reason}\n---\n\n"
        f"# Розшифровки немає: {media.name}\n\nПричина: `{reason}`. Текст цього файлу невідомий; "
        "не переказуй його, доки Андрій не дасть інший файл або текст.\n",
        encoding="utf-8",
    )


async def run(vault_client: Any, transport: Any = None) -> Dict[str, Any]:
    """The scheduled job: the oldest lecture without a transcript, one per run."""
    from src.obsidian_notes import vault_dir_from_env

    root = vault_dir_from_env()
    if root is None:
        return {"status": "unavailable", "reason": "obsidian_vault_not_mounted"}
    todo = pending(root.joinpath(*TARGET_DIR))
    if not todo:
        return {"status": "ok", "transcribed": 0, "waiting": 0}
    try:
        keys = await vault_client.get_secret(secret_path("api-keys")) if vault_client else None
    except Exception as exc:  # noqa: BLE001
        return {"status": "unavailable", "reason": f"vault_read_failed: {type(exc).__name__}"}
    key = (keys or {}).get(KEY_NAME)
    if not key:
        return {"status": "unavailable", "reason": "no_deepgram_api_key_in_vault", "waiting": len(todo)}
    results = []
    for media in todo[:MAX_PER_RUN]:
        result = await transcribe_one(media, str(key), transport)
        if result.get("reason") in PERMANENT:
            write_failure_note(media, result["reason"])
        results.append(result)
    done = [result for result in results if result["status"] == "ok"]
    status = "ok" if len(done) == len(results) else "unavailable"
    reason = None if status == "ok" else results[-1].get("reason")
    return {"status": status, "reason": reason, "transcribed": len(done), "waiting": len(todo) - len(done),
            "results": results}
