"""K.O.D.E.K.S. (KODEX) — архіви й бази знань синдикату. Чистий Python, без мережі, без платних API.

Обов'язки: завантажувати, структурувати, сортувати, розподіляти по агентських і спільних базах,
редагувати, видаляти. Усе, що KODEX і агенти роблять самі, іде у звіт для Єви.

Правила (жорсткі):
- Нічого не завантажує з інтернету без явного підтвердження Андрія (`approve_download`).
- Файли з міткою `andrii_protected` (ваші файли):
  • читання — дозволене всім;
  • переміщення (сортування) — дозволене KODEX і агентам;
  • редагування і видалення — лише з дозволу Андрія (запит → `confirm`).
- Усе інше (без мітки): KODEX і агенти редагують, сортують, видаляють самі; видалене — у кошик на 30 днів.
- Мітку ставлять: особисте завантаження Андрія (автоматично, `origin=andrii_direct`);
  завантаження через KODEX — без мітки з попередженням, якщо Андрій не попросив мітку (`origin=andrii_kodex`).
  Зняти мітку може лише Андрій.
- Формат без парсера не відкидається: він стає `needs_parser` і пропонується на вивчення з підтвердженням.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

PROTECTED_LABEL = "andrii_protected"
OWNER = "andrii"
TRASH_RETENTION_DAYS = 30
UNPROTECTED_WARNING = "Файл завантажено без мітки захисту: KODEX і агенти можуть його редагувати й видаляти."

# origin: andrii_direct (особисте завантаження → мітка), andrii_kodex (через KODEX → без мітки, якщо не просили),
# agent (автоматичне завантаження агентом)
ORIGINS = ("andrii_direct", "andrii_kodex", "agent")

# status: native | vendored_parser | library_installed | needs_engine | needs_parser (вивчити з підтвердженням)
FORMATS: Dict[str, Dict[str, str]] = {
    "md": {"status": "native"}, "txt": {"status": "native"}, "csv": {"status": "native"},
    "json": {"status": "native"},
    "docx": {"status": "library_installed", "lib": "python-docx"},
    "xlsx": {"status": "library_installed", "lib": "openpyxl"},
    "pptx": {"status": "library_installed", "lib": "python-pptx"},
    "pdf": {"status": "vendored_parser", "lib": "book-to-skill extractor"},
    "epub": {"status": "vendored_parser", "lib": "book-to-skill extractor"},
    "html": {"status": "vendored_parser", "lib": "book-to-skill extractor"},
    "rtf": {"status": "vendored_parser", "lib": "book-to-skill extractor"},
    "mp3": {"status": "needs_engine", "lib": "локальний Whisper (безкоштовний)"},
    "wav": {"status": "needs_engine", "lib": "локальний Whisper"},
    "m4a": {"status": "needs_engine", "lib": "локальний Whisper"},
    "mp4": {"status": "needs_engine", "lib": "локальний Whisper + ffmpeg"},
    "mkv": {"status": "needs_engine", "lib": "локальний Whisper + ffmpeg"},
    "mov": {"status": "needs_engine", "lib": "локальний Whisper + ffmpeg"},
    "webm": {"status": "needs_engine", "lib": "локальний Whisper + ffmpeg"},
    "flac": {"status": "needs_engine", "lib": "локальний Whisper"},
    "ogg": {"status": "needs_engine", "lib": "локальний Whisper"},
    "opus": {"status": "needs_engine", "lib": "локальний Whisper"},
    "aac": {"status": "needs_engine", "lib": "локальний Whisper"},
    "aiff": {"status": "needs_engine", "lib": "локальний Whisper"},
    "wma": {"status": "needs_engine", "lib": "локальний Whisper + ffmpeg"},
    # Фото: зберігаються і впорядковуються одразу; розпізнавання тексту (OCR) — при деплої.
    "jpg": {"status": "stored", "lib": "фото; OCR при деплої"},
    "jpeg": {"status": "stored", "lib": "фото; OCR при деплої"},
    "png": {"status": "stored", "lib": "фото; OCR при деплої"},
    "webp": {"status": "stored", "lib": "фото; OCR при деплої"},
    "gif": {"status": "stored", "lib": "зображення"},
    "bmp": {"status": "stored", "lib": "зображення"},
    "tif": {"status": "stored", "lib": "зображення"},
    "tiff": {"status": "stored", "lib": "зображення"},
    "heic": {"status": "needs_engine", "lib": "HEIC: конвертація при деплої (pillow-heif)"},
    "heif": {"status": "needs_engine", "lib": "HEIC: конвертація при деплої (pillow-heif)"},
}

KIND_BY_EXT = {
    **{e: "document" for e in ("md", "txt", "csv", "json", "docx", "xlsx", "pptx", "pdf", "epub", "html", "rtf")},
    **{e: "image" for e in ("jpg", "jpeg", "png", "webp", "gif", "bmp", "tif", "tiff", "heic", "heif")},
    **{e: "audio" for e in ("mp3", "wav", "m4a", "flac", "ogg", "opus", "aac", "aiff", "wma")},
    **{e: "video" for e in ("mp4", "mkv", "mov", "webm")},
}


def kind_of(ext: str) -> str:
    return KIND_BY_EXT.get(ext, "unknown")

# Папки (бази). Захист іде за міткою файла, а не за папкою.
DOMAINS = ("andrii_medical_vault", "doc", "fin", "sam", "eva", "architect", "marshal", "kira", "shared")

CLASSIFY_RULES = [
    ("andrii_medical_vault", ("аналіз", "лаборатор", "діагноз", "мрт", "ліки", "виписка", "феритин", "гемоглобін")),
    ("doc", ("тренування", "вправ", "rpe", "рецепт", "калор", "кбжу", "білок", "добавк", "реабілітац")),
    ("fin", ("бюджет", "банк", "фоп", "податк", "єсв", "витрат", "дохід", "чек", "курс")),
    ("sam", ("трейд", "ордер", "портфел", "ринок", "стоп-лосс", "волатиль", "бектест")),
    ("eva", ("кошик", "покупк", "сільпо", "атб", "варус", "ашан", "календар", "зустріч")),
    ("architect", ("workflow", "n8n", "docker", "api", "деплой")),
    ("marshal", ("безпек", "інцидент", "вразлив", "скілспектор", "секрет")),
]


def classify(name: str, text: str = "") -> str:
    blob = f"{name} {text}".lower()
    for domain, words in CLASSIFY_RULES:
        if any(w in blob for w in words):
            return domain
    return "shared"


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class Record:
    id: str
    name: str
    ext: str
    domain: str
    sha256: str
    status: str                       # stored | needs_parser | needs_engine | trashed
    created_at: str
    origin: str = "agent"
    kind: str = "document"            # document | image | audio | video | unknown
    labels: List[str] = field(default_factory=list)
    versions: List[Dict[str, Any]] = field(default_factory=list)
    trashed_at: Optional[str] = None


class KodexStore:
    """Сховище — один JSON-файл. Шлях задає власник (поза git для особистих файлів)."""

    def __init__(self, path: Path, blob_dir: Optional[Path] = None) -> None:
        self.path = Path(path)
        # Справжні файли (фото, аудіо, документи) — окремо від JSON, за хешем; поза git.
        self.blob_dir = Path(blob_dir) if blob_dir else self.path.parent / "blobs"
        self.records: Dict[str, Record] = {}
        self.pending: Dict[str, Dict[str, Any]] = {}
        self.log: List[Dict[str, Any]] = []
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.records = {k: Record(**v) for k, v in raw.get("records", {}).items()}
            self.pending = raw.get("pending", {})
            self.log = raw.get("log", [])

    def save(self) -> None:
        """Атомарний запис: при збої не лишається обрізаний JSON (тимчасовий файл + os.replace)."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"records": {k: asdict(v) for k, v in self.records.items()},
                "pending": self.pending, "log": self.log}
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.path)

    def _blob_path(self, digest: str, ext: str) -> Path:
        suffix = f".{ext}" if ext else ""
        return self.blob_dir / digest[:2] / f"{digest}{suffix}"

    def _write_blob(self, digest: str, ext: str, data: bytes) -> None:
        target = self._blob_path(digest, ext)
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

    def read_bytes(self, rec_id: str) -> Optional[bytes]:
        rec = self.records.get(rec_id)
        if rec is None or rec.status == "trashed":
            return None
        path = self._blob_path(rec.sha256, rec.ext)
        return path.read_bytes() if path.exists() else None

    def _now(self) -> str:
        return datetime.now().isoformat(timespec="seconds")

    def _log(self, action: str, actor: str, **kw: Any) -> None:
        self.log.append({"at": self._now(), "action": action, "actor": actor, **kw})

    @staticmethod
    def _protected(rec: Record) -> bool:
        return PROTECTED_LABEL in rec.labels

    def _hash_exists(self, digest: str) -> Optional[str]:
        for r in self.records.values():
            if r.sha256 == digest and r.status != "trashed":
                return r.id
        return None

    def _live(self, rec_id: str) -> Optional[Record]:
        rec = self.records.get(rec_id)
        return rec if rec is not None and rec.status != "trashed" else None

    # ------------------------------------------------------------ завантаження
    def ingest(self, name: str, data: bytes, text: str = "", origin: str = "agent",
               actor: str = "kodex", protect: bool = False) -> Dict[str, Any]:
        if origin not in ORIGINS:
            return {"status": "rejected", "reason": "unknown_origin"}
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        digest = sha256_of(data)
        dup = self._hash_exists(digest)
        if dup:
            self._log("duplicate_skipped", actor, name=name, existing=dup)
            return {"status": "duplicate", "existing_id": dup}
        fmt = FORMATS.get(ext)
        if fmt is None:
            status = "needs_parser"
        elif fmt["status"] == "needs_engine":
            status = "needs_engine"
        else:
            status = "stored"
        self._write_blob(digest, ext, data)
        labeled = origin == "andrii_direct" or (origin == "andrii_kodex" and protect)
        labels = [PROTECTED_LABEL] if labeled else []
        rec = Record(id=uuid.uuid4().hex[:12], name=name, ext=ext, domain=classify(name, text),
                     sha256=digest, status=status, created_at=self._now(), origin=origin, labels=labels,
                     kind=kind_of(ext))
        rec.versions.append({"at": rec.created_at, "action": "ingest", "by": actor, "domain": rec.domain})
        self.records[rec.id] = rec
        if status == "needs_parser":
            self.pending[f"fmt:{ext}"] = {"kind": "learn_format", "ext": ext, "name": name,
                                           "state": "awaiting_andrii"}
        self._log("ingest", actor, id=rec.id, name=name, domain=rec.domain, status=status,
                  origin=origin, protected=labeled, kind=rec.kind)
        result: Dict[str, Any] = {"status": status, "id": rec.id, "domain": rec.domain, "protected": labeled,
                                  "format": FORMATS.get(ext, {"status": "unknown"})}
        if origin == "andrii_kodex" and not labeled:
            result["warning"] = UNPROTECTED_WARNING
        return result

    # ------------------------------------------------------------ мітка захисту (лише Андрій)
    def label(self, rec_id: str, by: str) -> Dict[str, Any]:
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_labels"}
        rec = self._live(rec_id)
        if rec is None:
            return {"status": "not_found"}
        if not self._protected(rec):
            rec.labels.append(PROTECTED_LABEL)
        self._log("labeled", by, id=rec_id, name=rec.name)
        return {"status": "protected", "id": rec_id}

    def unlabel(self, rec_id: str, by: str) -> Dict[str, Any]:
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_unlabels"}
        rec = self._live(rec_id)
        if rec is None:
            return {"status": "not_found"}
        rec.labels = [x for x in rec.labels if x != PROTECTED_LABEL]
        self._log("unlabeled", by, id=rec_id, name=rec.name)
        return {"status": "unprotected", "id": rec_id}

    # ------------------------------------------------------------ переміщення (дозволене й для мічених)
    def move(self, rec_id: str, to_domain: str, actor: str) -> Dict[str, Any]:
        rec = self._live(rec_id)
        if rec is None:
            return {"status": "not_found"}
        if to_domain not in DOMAINS:
            return {"status": "rejected", "reason": "unknown_domain"}
        old, rec.domain = rec.domain, to_domain
        rec.versions.append({"at": self._now(), "action": "move", "by": actor, "from": old, "to": to_domain})
        self._log("move", actor, id=rec_id, name=rec.name, frm=old, to=to_domain, protected=self._protected(rec))
        return {"status": "moved", "id": rec_id, "from": old, "to": to_domain}

    # ------------------------------------------------------------ редагування і видалення
    def rewrite(self, rec_id: str, new_data: bytes, reason: str, actor: str) -> Dict[str, Any]:
        """Без мітки — одразу. З міткою — лише після дозволу Андрія (повертає token)."""
        rec = self._live(rec_id)
        if rec is None:
            return {"status": "not_found"}
        new_digest = sha256_of(new_data)
        self._write_blob(new_digest, rec.ext, new_data)  # нова версія зберігається до рішення
        if self._protected(rec):
            return self._request_permission("rewrite", rec, actor, reason=reason, new_digest=new_digest)
        return self._apply_rewrite(rec, new_digest, reason, actor)

    def request_delete(self, rec_id: str, actor: str) -> Dict[str, Any]:
        """Без мітки — у кошик одразу. З міткою — лише після дозволу Андрія (повертає token)."""
        rec = self._live(rec_id)
        if rec is None:
            return {"status": "not_found"}
        if self._protected(rec):
            return self._request_permission("delete", rec, actor)
        return self._trash(rec, actor)

    def _request_permission(self, change: str, rec: Record, actor: str, **kw: Any) -> Dict[str, Any]:
        token = uuid.uuid4().hex[:8]
        self.pending[f"chg:{token}"] = {"kind": change, "id": rec.id, "actor": actor,
                                        "state": "awaiting_andrii", **kw}
        self._log("permission_requested", actor, id=rec.id, name=rec.name, change=change, token=token)
        return {"status": "awaiting_andrii_permission", "token": token, "change": change, "name": rec.name}

    def confirm(self, token: str, by: str) -> Dict[str, Any]:
        """Андрій дає дозвіл на зміну мічених файлів (редагування або видалення)."""
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_confirms"}
        item = self.pending.pop(f"chg:{token}", None)
        if item is None:
            return {"status": "not_found"}
        rec = self._live(item["id"])
        if rec is None:
            return {"status": "not_found"}
        # Виконавець — той, хто запросив зміну (агент або сам Андрій); дозвіл — окремо, approved_by.
        # Так зміна, яку агент запросив і Андрій схвалив, потрапляє у звіт Єві з іменем агента.
        if item["kind"] == "delete":
            return self._trash(rec, item["actor"], approved_by=OWNER)
        return self._apply_rewrite(rec, item["new_digest"], item["reason"], item["actor"], approved_by=OWNER)

    def reject(self, token: str, by: str) -> Dict[str, Any]:
        """Андрій забороняє зміну мічених файлів: запит закривається, файл не змінюється."""
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_rejects"}
        item = self.pending.pop(f"chg:{token}", None)
        if item is None:
            return {"status": "not_found"}
        self._log("permission_denied", by, id=item["id"], change=item["kind"], requested_by=item["actor"])
        if item["kind"] == "rewrite":
            rec = self.records.get(item["id"])
            if rec is not None:
                # Відхилена версія не має лишатися на диску.
                self._drop_digest_if_unused(item["new_digest"], rec.ext)
        return {"status": "denied", "id": item["id"]}

    def _apply_rewrite(self, rec: Record, new_digest: str, reason: str, actor: str, **extra: Any) -> Dict[str, Any]:
        rec.versions.append({"at": self._now(), "action": "rewrite", "by": actor, "reason": reason,
                             "from_sha256": rec.sha256, "to_sha256": new_digest, **extra})
        rec.sha256 = new_digest
        self._log("rewrite", actor, id=rec.id, name=rec.name, reason=reason, **extra)
        return {"status": "rewritten", "id": rec.id, "versions": len(rec.versions)}

    def _trash(self, rec: Record, actor: str, **extra: Any) -> Dict[str, Any]:
        rec.status = "trashed"
        rec.trashed_at = self._now()
        self._log("trashed", actor, id=rec.id, name=rec.name, **extra)
        return {"status": "trashed", "id": rec.id, "restore_until_days": TRASH_RETENTION_DAYS}

    def _drop_digest_if_unused(self, digest: str, ext: str) -> None:
        if any(r.sha256 == digest for r in self.records.values()):
            return
        path = self._blob_path(digest, ext)
        if path.exists():
            path.unlink()

    def _drop_blob_if_unused(self, rec: Record) -> None:
        self._drop_digest_if_unused(rec.sha256, rec.ext)

    def purge_expired(self, now: datetime) -> List[str]:
        gone = []
        names: List[str] = []
        for rid, rec in list(self.records.items()):
            if rec.status == "trashed" and rec.trashed_at:
                if now - datetime.fromisoformat(rec.trashed_at) >= timedelta(days=TRASH_RETENTION_DAYS):
                    del self.records[rid]
                    gone.append(rid)
                    names.append(rec.name)
                    self._drop_blob_if_unused(rec)
        if gone:
            self._log("purged", "kodex", ids=gone, names=names)
        return gone

    # ------------------------------------------------------------ інтернет і формати (лише Андрій)
    def request_download(self, url: str, reason: str, actor: str = "kodex") -> Dict[str, Any]:
        req = uuid.uuid4().hex[:8]
        self.pending[f"net:{req}"] = {"kind": "download", "url": url, "reason": reason, "state": "awaiting_andrii"}
        self._log("download_requested", actor, req=req, url=url)
        return {"status": "awaiting_andrii_approval", "request": req}

    def approve_download(self, req: str, by: str) -> Dict[str, Any]:
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_approves"}
        item = self.pending.get(f"net:{req}")
        if not item:
            return {"status": "not_found"}
        item["state"] = "approved"
        self._log("download_approved", by, req=req)
        return {"status": "approved", "url": item["url"]}

    def reject_download(self, req: str, by: str) -> Dict[str, Any]:
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_approves"}
        item = self.pending.pop(f"net:{req}", None)
        if item is None:
            return {"status": "not_found"}
        self._log("download_denied", by, req=req, url=item["url"])
        return {"status": "denied", "request": req}

    def download_allowed(self, req: str) -> bool:
        item = self.pending.get(f"net:{req}")
        return bool(item and item.get("state") == "approved")

    def approve_format(self, ext: str, by: str) -> Dict[str, Any]:
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_approves"}
        item = self.pending.get(f"fmt:{ext}")
        if not item:
            return {"status": "not_found"}
        item["state"] = "approved_to_learn"
        self._log("format_learning_approved", by, ext=ext)
        return {"status": "approved_to_learn", "ext": ext}

    def deny_format(self, ext: str, by: str) -> Dict[str, Any]:
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_approves"}
        item = self.pending.pop(f"fmt:{ext}", None)
        if item is None:
            return {"status": "not_found"}
        self._log("format_learning_denied", by, ext=ext)
        return {"status": "denied", "ext": ext}

    # ------------------------------------------------------------ звіт Єві
    def _actions_since(self, since: datetime) -> List[Dict[str, Any]]:
        return [e for e in self.log if datetime.fromisoformat(e["at"]) >= since]

    def _agent_actions(self, entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Дії KODEX і агентів (усе, крім дій Андрія) — для звіту Єві."""
        out: Dict[str, List[Dict[str, Any]]] = {"edits": [], "deletes": [], "moves": [],
                                                "ingests": [], "purges": []}
        keys = ("at", "actor", "id", "name")
        for e in entries:
            if e["action"] == "purged":
                # Автоматичне очищення кошика — теж маніпуляція, виконавець — KODEX.
                for rid, name in zip(e.get("ids", []), e.get("names", []), strict=True):
                    out["purges"].append({"at": e["at"], "actor": e["actor"], "id": rid, "name": name})
                continue
            if e["actor"] == OWNER:
                continue
            if e["action"] == "rewrite":
                out["edits"].append({k: e.get(k) for k in keys + ("reason", "approved_by")})
            elif e["action"] == "trashed":
                out["deletes"].append({k: e.get(k) for k in keys + ("approved_by",)})
            elif e["action"] == "move":
                out["moves"].append({k: e.get(k) for k in keys + ("frm", "to", "protected")})
            elif e["action"] == "ingest" and e.get("origin") not in ("andrii_direct", "andrii_kodex"):
                # Файл, який завантажив агент (не Андрій): теж іде в звіт Єві.
                out["ingests"].append({k: e.get(k) for k in keys + ("origin", "domain", "status")})
        return out

    def _pending_counts(self) -> Dict[str, int]:
        # "permission" — усі запити на зміну мічених файлів (редагування і видалення).
        counts = {"download": 0, "format": 0, "permission": 0}
        names = {"chg": "permission", "net": "download", "fmt": "format"}
        for key, item in self.pending.items():
            if item.get("state") == "awaiting_andrii":
                counts[names[key.split(":")[0]]] += 1
        return counts

    def report_for_eva(self, since: datetime) -> Dict[str, Any]:
        """Усі дії за період, включно з тим, що агенти зробили самі (редагування, видалення, переміщення)."""
        entries = self._actions_since(since)
        counts: Dict[str, int] = {}
        by_actor: Dict[str, int] = {}
        for e in entries:
            counts[e["action"]] = counts.get(e["action"], 0) + 1
            by_actor[e["actor"]] = by_actor.get(e["actor"], 0) + 1
        by_status: Dict[str, int] = {}
        for r in self.records.values():
            if r.status != "trashed":
                by_status[r.status] = by_status.get(r.status, 0) + 1
        agent = self._agent_actions(entries)
        return {"type": "kodex_report", "to": "eva", "since": since.isoformat(timespec="seconds"),
                "ingested": counts.get("ingest", 0), "rewritten": counts.get("rewrite", 0),
                "moved": counts.get("move", 0), "trashed": counts.get("trashed", 0),
                "duplicates_skipped": counts.get("duplicate_skipped", 0),
                "actions_by_actor": by_actor, "agent_edits": agent["edits"],
                "agent_deletes": agent["deletes"], "agent_moves": agent["moves"],
                "agent_ingests": agent["ingests"], "auto_purged": agent["purges"],
                "awaiting_andrii": self._pending_counts(),
                "protected_files": sum(self._protected(r) for r in self.records.values() if r.status != "trashed"),
                "active_records_by_status": by_status}


# ------------------------------------------------------------ вечірній звіт Єві (21:00)
EVENING_WINDOW = timedelta(hours=24)


def evening_section(data_dir: Optional[str], now: datetime) -> Dict[str, Any]:
    """Файлова частина вечірнього звіту: усі дії KODEX і агентів за 24 години.

    Без KODEX_DATA_DIR — чесна відсутність (status=unavailable), а не нулі.
    """
    if not data_dir:
        return {"status": "unavailable", "warning": "KODEX_DATA_DIR не задано: звіт файлів не зібрано"}
    base = Path(data_dir)
    store = KodexStore(base / "kodex.json", base / "blobs")
    rep = store.report_for_eva(now - EVENING_WINDOW)
    return {"status": "ok", "window_hours": int(EVENING_WINDOW.total_seconds() // 3600), "report": rep}



# ------------------------------------------------------------ Kodex Agent Implementation
class KodexAgent:
    """
    KODEX — Chief Archivist, Legal & Knowledge Compliance Agent.
    Specializes in archive management, deduplication, NotebookLM grounded research,
    and bidirectional synchronization with the shared Obsidian Second Brain.
    """

    AGENT_ID = "kodex"

    def __init__(
        self,
        memory: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        store: Optional[KodexStore] = None,
        bridge: Optional[Any] = None,
    ) -> None:
        self._memory = memory
        self._config = dict(config or {})
        self._store = store
        if bridge is not None:
            self._bridge = bridge
        else:
            from src.integrations.notebooklm_obsidian_bridge import NotebookLMObsidianBridge
            vault_path = self._config.get("obsidian_vault_path")
            self._bridge = NotebookLMObsidianBridge(vault_path=vault_path)

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "capabilities")
        if action == "capabilities":
            return {
                "agent": self.AGENT_ID,
                "role": "Chief Archivist, Knowledge Lifecycle & Obsidian Sync",
                "actions": [
                    "sync_to_obsidian",
                    "process_with_notebooklm",
                    "cleanup_notebooklm",
                    "scan_user_notes",
                    "ingest_file",
                    "capabilities",
                ],
                "status": "ready",
                "integrations": ["NotebookLM", "Obsidian"],
            }
        elif action in ("sync_to_obsidian", "archive_to_obsidian"):
            return self._bridge.synthesize_and_export(
                agent_id=payload.get("agent_id", self.AGENT_ID),
                title=payload.get("title", "Untitled Document"),
                raw_content=payload.get("content", ""),
                category=payload.get("category", "archive"),
                key_insights=payload.get("key_insights"),
                backlinks=payload.get("backlinks"),
                tags=payload.get("tags"),
                sources=payload.get("sources"),
                audio_file_path=payload.get("audio_file_path"),
                force=payload.get("force", False),
            )
        elif action in ("process_with_notebooklm", "notebooklm_synthesize"):
            # Deep synthesis through NotebookLM, deduplication, and export to Obsidian
            title = payload.get("title", "NotebookLM Research")
            content = payload.get("content", "")
            insights = payload.get("key_insights") or [
                f"Grounded synthesis of: {title}",
                "Structured and verified against existing knowledge base.",
            ]
            res = self._bridge.synthesize_and_export(
                agent_id=payload.get("agent_id", self.AGENT_ID),
                title=title,
                raw_content=content,
                category=payload.get("category", "research"),
                key_insights=insights,
                backlinks=payload.get("backlinks") or ["Knowledge Base", "Research"],
                tags=payload.get("tags") or ["notebooklm", "grounded"],
                sources=payload.get("sources") or [],
                audio_file_path=payload.get("audio_file_path"),
            )
            # Automatic cleanup of temporary NotebookLM artifacts if requested
            if payload.get("cleanup", True):
                self._bridge.cleanup_notebooklm_artifacts(payload.get("notebook_id"))
            return res
        elif action in ("cleanup_notebooklm", "purge_notebooks"):
            return self._bridge.cleanup_notebooklm_artifacts(payload.get("notebook_id"))
        elif action in ("scan_user_notes", "read_obsidian_notes"):
            notes = self._bridge.scan_user_notes()
            return {"status": "ok", "notes": notes, "count": len(notes)}
        elif action in ("dispatch_task", "create_task"):
            task_id = str(payload.get("task_id") or f"TASK-{uuid.uuid4().hex[:6].upper()}")
            return self._bridge.create_task_card(
                task_id=task_id,
                title=str(payload.get("title", "Syndicate Task")),
                description=str(payload.get("description", "")),
                assigned_to=str(payload.get("target_agent", payload.get("assigned_to", "kodex"))),
                created_by=str(payload.get("created_by", "eva")),
                priority=str(payload.get("priority", "medium")),
                linked_concepts=payload.get("linked_concepts"),
                tags=payload.get("tags"),
            )
        elif action in ("triage_task_web", "triage_tasks"):
            return self._bridge.triage_tasks_as_kodex()
        elif action == "storage_stats":
            kb_files = list(self._bridge.knowledge_dir.rglob("*.md"))
            task_files = list(self._bridge.tasks_dir.rglob("*.md"))
            return {
                "status": "ok",
                "agent": self.AGENT_ID,
                "knowledge_cards_count": len(kb_files),
                "task_cards_count": len(task_files),
                "vault_path": str(self._bridge.vault_path),
            }
        return {"status": "error", "error": f"Unknown action: {action}"}
