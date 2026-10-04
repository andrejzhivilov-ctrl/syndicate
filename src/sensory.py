"""
Floor 1 — Sensory Router ("mini-branches without a brain").

Deterministic classification and pre-processing of inbound Telegram updates.
Nothing here calls an LLM: voice goes to STT, photos to OCR, documents to a
text extractor, and only clean text reaches the orchestrator. Unknown chats
are rejected before any work is done (zero-trust allow-list).
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import structlog

logger = structlog.get_logger(__name__)

MAX_STT_BYTES = 25 * 1024 * 1024        # Whisper API upload limit
TELEGRAM_TEXT_LIMIT = 4096
TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".csv", ".json", ".log"}
SUPPORTED_DOC_EXTENSIONS = TEXT_EXTENSIONS | {".docx", ".pdf"}


@dataclass
class SensoryEvent:
    kind: str                      # text | voice | audio | photo | document | video_note | unknown
    route: str                     # orchestrator | stt | audio_split | ocr | extract | reject
    chat_id: Optional[int] = None
    text: str = ""
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    file_size: int = 0
    duration_s: float = 0.0
    needs_llm: bool = False
    reason: str = ""
    update_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


class SensoryRouter:
    """Classify inbound updates and prepare payloads without any LLM call."""

    def __init__(
        self,
        allowed_chat_ids: Optional[Sequence[int]] = None,
        max_audio_bytes: int = MAX_STT_BYTES,
        telegram_limit: int = TELEGRAM_TEXT_LIMIT,
        max_audio_chunk_bytes: Optional[int] = None,
    ) -> None:
        self._allowed: Set[int] = {int(c) for c in (allowed_chat_ids or [])}
        self._max_audio = max_audio_chunk_bytes or max_audio_bytes
        self._tg_limit = telegram_limit
        self._seen_updates: Dict[int, None] = {}

    def split_audio_for_whisper(self, audio_bytes: bytes, filename: str = "audio.ogg") -> List[Dict[str, Any]]:
        """Split raw audio bytes into chunks under STT limit."""
        if not audio_bytes:
            return []
        limit = self._max_audio
        chunks = []
        for i in range(0, len(audio_bytes), limit):
            chunk = audio_bytes[i:i + limit]
            chunks.append({
                "index": len(chunks),
                "filename": f"{filename}.part{len(chunks)}",
                "size": len(chunk),
                "bytes": chunk,
            })
        return chunks

    def extract_document(self, file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
        """Extract plain text and metadata from document bytes."""
        res = self.extract_document_text(filename, file_bytes)
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return res.get("text", ""), {"type": ext, "status": res.get("status", "ok"), "chars": res.get("chars", 0)}

    def route_telegram_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Route a Telegram update payload and return classification."""
        event = self.classify(payload)
        return event.to_dict()

    def split_telegram_message(self, text: str, limit: Optional[int] = None) -> List[str]:
        return self.split_for_telegram(text, limit)

    # ── access control ────────────────────────────────────────────────────
    def is_authorized(self, chat_id: Optional[int]) -> bool:
        """Zero-trust: an empty allow-list denies everyone."""
        return chat_id is not None and int(chat_id) in self._allowed

    def _seen(self, update_id: Optional[int]) -> bool:
        """Idempotency guard against Telegram redelivery."""
        if update_id is None:
            return False
        if update_id in self._seen_updates:
            return True
        self._seen_updates[update_id] = None
        if len(self._seen_updates) > 5000:
            self._seen_updates.pop(next(iter(self._seen_updates)))
        return False

    # ── classification ────────────────────────────────────────────────────
    def classify(self, update: Dict[str, Any]) -> SensoryEvent:
        msg = update.get("message") or update.get("edited_message") or update.get("channel_post") or {}
        update_id = update.get("update_id")
        chat_id = (msg.get("chat") or {}).get("id")

        if not self.is_authorized(chat_id):
            logger.warning("sensory_unauthorized_chat", chat_id=chat_id)
            return SensoryEvent("unknown", "reject", chat_id=chat_id, reason="chat_not_allowed", update_id=update_id)
        if self._seen(update_id):
            return SensoryEvent("unknown", "reject", chat_id=chat_id, reason="duplicate_update", update_id=update_id)

        if msg.get("voice") or msg.get("audio") or msg.get("video_note"):
            media = msg.get("voice") or msg.get("audio") or msg.get("video_note")
            size = int(media.get("file_size") or 0)
            kind = "voice" if msg.get("voice") else ("audio" if msg.get("audio") else "video_note")
            route = "audio_split" if size > self._max_audio else "stt"
            return SensoryEvent(
                kind, route, chat_id=chat_id, file_id=media.get("file_id"), file_size=size,
                duration_s=float(media.get("duration") or 0), update_id=update_id,
            )

        if msg.get("photo"):
            best = max(msg["photo"], key=lambda p: int(p.get("file_size") or 0))
            return SensoryEvent(
                "photo", "ocr", chat_id=chat_id, file_id=best.get("file_id"),
                file_size=int(best.get("file_size") or 0), text=msg.get("caption", ""), update_id=update_id,
            )

        if msg.get("document"):
            doc = msg["document"]
            name = doc.get("file_name") or ""
            ext = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
            if ext not in SUPPORTED_DOC_EXTENSIONS:
                return SensoryEvent(
                    "document", "reject", chat_id=chat_id, file_name=name,
                    reason=f"unsupported_extension:{ext or 'none'}", update_id=update_id,
                )
            return SensoryEvent(
                "document", "extract", chat_id=chat_id, file_id=doc.get("file_id"), file_name=name,
                file_size=int(doc.get("file_size") or 0), text=msg.get("caption", ""), update_id=update_id,
            )

        text = msg.get("text")
        if text:
            return SensoryEvent("text", "orchestrator", chat_id=chat_id, text=text, needs_llm=True, update_id=update_id)

        return SensoryEvent("unknown", "reject", chat_id=chat_id, reason="empty_or_unsupported", update_id=update_id)

    # ── deterministic transforms ──────────────────────────────────────────
    def plan_audio_split(self, size_bytes: int, duration_s: float, safety: float = 0.8) -> List[Tuple[float, float]]:
        """Plan (start, end) second windows so each chunk stays under the STT limit."""
        if size_bytes <= self._max_audio or duration_s <= 0:
            return [(0.0, float(duration_s))] if duration_s > 0 else []
        bytes_per_s = size_bytes / duration_s
        window = max(1.0, (self._max_audio * safety) / bytes_per_s)
        chunks: List[Tuple[float, float]] = []
        start = 0.0
        while start < duration_s:
            end = min(duration_s, start + window)
            chunks.append((round(start, 2), round(end, 2)))
            start = end
        return chunks

    def split_for_telegram(self, text: str, limit: Optional[int] = None) -> List[str]:
        """Split text on paragraph / sentence / word boundaries within Telegram's limit."""
        limit = limit or self._tg_limit
        if len(text) <= limit:
            return [text] if text else []
        parts: List[str] = []
        remaining = text
        while len(remaining) > limit:
            window = remaining[:limit]
            cut = max(window.rfind("\n\n"), window.rfind("\n"), window.rfind(". "), window.rfind(" "))
            if cut < limit // 2:
                cut = limit
            else:
                cut += 1
            parts.append(remaining[:cut].rstrip())
            remaining = remaining[cut:].lstrip()
        if remaining:
            parts.append(remaining)
        return parts

    @staticmethod
    def chunk_for_embedding(text: str, max_chars: int = 1200, overlap: int = 150, chunk_size: Optional[int] = None) -> List[str]:
        """Paragraph-aware chunking with overlap for RAG indexing."""
        max_chars = chunk_size or max_chars
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks: List[str] = []
        buf = ""
        for para in paragraphs:
            if len(para) > max_chars:
                if buf:
                    chunks.append(buf)
                    buf = ""
                step = max(1, max_chars - overlap)
                for i in range(0, len(para), step):
                    chunks.append(para[i:i + max_chars])
                continue
            if len(buf) + len(para) + 2 <= max_chars:
                buf = f"{buf}\n\n{para}" if buf else para
            else:
                chunks.append(buf)
                tail = buf[-overlap:] if overlap else ""
                buf = f"{tail}\n\n{para}" if tail else para
        if buf:
            chunks.append(buf)
        return chunks

    def extract_document_text(self, filename: str, data: bytes) -> Dict[str, Any]:
        """Extract plain text from a document without any LLM."""
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        try:
            if ext in {".txt", ".md", ".markdown", ".log"}:
                text = data.decode("utf-8", errors="replace")
            elif ext == ".json":
                text = json.dumps(json.loads(data.decode("utf-8")), ensure_ascii=False, indent=2)
            elif ext == ".csv":
                rows = list(csv.reader(io.StringIO(data.decode("utf-8", errors="replace"))))
                text = "\n".join(" | ".join(r) for r in rows)
            elif ext == ".docx":
                with zipfile.ZipFile(io.BytesIO(data)) as zf:
                    xml = zf.read("word/document.xml").decode("utf-8", errors="replace")
                xml = re.sub(r"</w:p>", "\n", xml)
                text = re.sub(r"<[^>]+>", "", xml)
                text = (text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                        .replace("&quot;", '"').replace("&apos;", "'"))
            elif ext == ".pdf":
                try:
                    from pypdf import PdfReader  # optional dependency
                except ImportError:
                    return {"status": "needs_extractor", "text": "", "reason": "pypdf_not_installed"}
                reader = PdfReader(io.BytesIO(data))
                text = "\n".join((p.extract_text() or "") for p in reader.pages)
            else:
                return {"status": "unsupported", "text": "", "reason": f"extension:{ext}"}
        except Exception as exc:  # noqa: BLE001
            logger.warning("sensory_extract_failed", filename=filename, error=str(exc))
            return {"status": "error", "text": "", "reason": str(exc)}

        text = text.strip()
        return {
            "status": "ok",
            "text": text,
            "chars": len(text),
            "chunks": self.chunk_for_embedding(text),
        }
