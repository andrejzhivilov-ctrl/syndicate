"""Files Andrii sends to an agent's bot: documents, tables, slides and audio (16.11.2026).

Before this, the bot saw only photos and videos; a PDF, a spreadsheet, a deck or an audio file in
the chat was ignored. Now the file is kept in the agent's materials folder in Obsidian (Eva shelves
it on her next run and lists it in the catalog), its text is read with ``material_reader`` or its
sound is transcribed by Groq Whisper, and the agent answers with the beginning in hand and the
path to read the rest part by part. A bot may download at most 20 MB from Telegram: a bigger file is
refused with the way round (the agent's Drive "Вхідні"), not cut.
"""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import structlog

from src import material_reader, video_digest

logger = structlog.get_logger(__name__)

#: Agents that keep files from their chat, and where (the folder Eva shelves from).
MATERIALS: Dict[str, tuple] = {
    "trainer": ("Health_Coach", "Матеріали"),
    # 18.11.2026: whatever Andrii sends to Eva's bot goes to the holding inbox; Eva routes it (src/inbox_router.py).
    "eva": ("00_Inbox", "Вхідні"),
}
MAX_BYTES = 20 * 1024 * 1024  # Telegram getFile limit for bots
AUDIO = frozenset({"mp3", "m4a", "ogg", "oga", "opus", "wav", "aac", "flac", "amr", "wma"})
VIDEO = frozenset({"mp4", "mov", "mkv", "webm", "avi", "m4v"})
EXCERPT_CHARS = 8_000
TOO_BIG = ("⚠️ Файл більший за 20 МБ: Telegram не віддає ботам більші. Поклади його в теку «Вхідні» "
           "на Google Drive, за 10 хвилин він буде в Obsidian.")


def extension(name: str, mime: str) -> str:
    ext = Path(name).suffix.lower().lstrip(".")
    if ext:
        return ext
    return {"application/pdf": "pdf", "text/csv": "csv", "text/plain": "txt", "audio/mpeg": "mp3",
            "audio/ogg": "ogg", "audio/mp4": "m4a", "audio/x-wav": "wav", "audio/wav": "wav"}.get(mime, "")


def refusal(agent: str, message: Mapping[str, Any]) -> Optional[str]:
    """Why this file is not taken, in Andrii's words; None when it is."""
    if agent not in MATERIALS:
        return "⚠️ Цей агент поки не приймає файли."
    if int(message.get("file_size") or 0) > MAX_BYTES:
        return TOO_BIG
    ext = extension(str(message.get("file_name") or ""), str(message.get("mime") or ""))
    if ext not in material_reader.EXTENSIONS | AUDIO | VIDEO:
        known = ", ".join(sorted(material_reader.EXTENSIONS | AUDIO))
        return f"⚠️ Формат «{ext or 'невідомий'}» я не читаю. Читаю: {known}, а також відео."
    return None


def _free_path(folder: Path, name: str) -> Path:
    safe = "".join(ch for ch in Path(name).name if ch not in '<>:"/\\|?*').strip() or "файл"
    target, number = folder / safe, 2
    while target.exists():  # nothing is overwritten
        target = folder / f"{Path(safe).stem} ({number}){Path(safe).suffix}"
        number += 1
    return target


def store(root: Path, agent: str, name: str, data: bytes) -> Path:
    folder = root.joinpath(*MATERIALS[agent])
    folder.mkdir(parents=True, exist_ok=True)
    target = _free_path(folder, name)
    target.write_bytes(data)
    return target


async def transcribe(source: Path, keys: Mapping[str, Any], transport: Any = None) -> Dict[str, Any]:
    """The sound of an audio or video file as timed text (Groq Whisper); honest when it cannot."""
    key = str(keys.get("groq_api_key") or "")
    if not key:
        return {"status": "unavailable", "reason": "no_groq_key"}
    with tempfile.TemporaryDirectory() as work:
        try:
            parts = await asyncio.to_thread(video_digest.to_opus, source, Path(work))
            text = await video_digest.groq_transcribe(parts, key, transport)
        except Exception as exc:  # noqa: BLE001 - ffmpeg or the network: reported, not hidden
            logger.warning("telegram_file_transcribe_failed", error_type=type(exc).__name__)
            return {"status": "unavailable", "reason": "transcription_failed"}
    if not text:
        return {"status": "unavailable", "reason": "no_speech"}
    return {"status": "ok", "text": text}


def write_transcript(media: Path, text: str) -> Path:
    """Next to the file, named as the lecture transcriber names it, so it is not transcribed twice."""
    target = media.with_name(media.name + material_reader.TRANSCRIPT_SUFFIX)
    target.write_text(f"---\nsource: \"{media.name}\"\ntranscript: groq\n---\n\n{text}\n", encoding="utf-8")
    return target


async def take(agent: str, root: Path, name: str, mime: str, data: bytes, keys: Mapping[str, Any],
               transport: Any = None) -> Dict[str, Any]:
    """Keep the file, then read or transcribe it; the result says what the agent may rely on."""
    ext = extension(name, mime)
    if not Path(name).suffix and ext:
        name = f"{name or 'файл'}.{ext}"
    path = store(root, agent, name, data)
    relative = path.relative_to(root).as_posix()
    if ext in AUDIO or ext in VIDEO:
        heard = await transcribe(path, keys, transport)
        if heard["status"] != "ok":
            return {"status": "unavailable", "path": relative, "kind": "audio", "reason": heard["reason"]}
        transcript = write_transcript(path, heard["text"])
        return {"status": "ok", "path": relative, "kind": "audio", "text": heard["text"],
                "transcript": transcript.relative_to(root).as_posix()}
    try:
        text = material_reader.extract_text(ext, data)
    except material_reader.MaterialError as exc:
        return {"status": "unavailable", "path": relative, "kind": "text", "reason": str(exc)}
    parts = max(1, -(-len(text) // material_reader.PART_CHARS))
    return {"status": "ok", "path": relative, "kind": "text", "text": text, "parts": parts}


def prompt(result: Mapping[str, Any], name: str, caption: str) -> str:
    """What the agent is told: where the file is, its beginning, and how to read further."""
    said = f"Підпис Андрія: «{caption}»." if caption else "Андрій нічого не дописав."
    where = f"Андрій надіслав файл «{name}». Він збережений у {result['path']} (Єва розкладе його по темі)."
    if result["status"] != "ok":
        return (f"{where} {said} Прочитати його не вдалося: {result.get('reason')}. Скажи Андрію про це прямо, "
                "не переказуй вміст з пам'яті.")
    text = str(result["text"])
    if result["kind"] == "audio":
        head = (f"Розшифровка звуку (Groq Whisper) лежить у {result['transcript']}. "
                f"Початок розшифровки:\n{text[:EXCERPT_CHARS]}")
    else:
        head = (f"Текст файлу: {result['parts']} частин(и); тут перша. Далі читай material_read з цим шляхом. "
                f"Початок:\n{text[:EXCERPT_CHARS]}")
    tail = "" if len(text) <= EXCERPT_CHARS else "\n[…далі не показано]"
    return (f"{where} {said}\n{head}{tail}\n\n{material_reader.NOTE} Відповідай на підпис Андрія; якщо підпису "
            "немає, коротко скажи, що це за файл, і запитай, що з ним зробити.")
