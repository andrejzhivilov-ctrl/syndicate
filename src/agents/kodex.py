"""K.O.D.E.K.S. (KODEX) — архіви й бази знань синдикату. Чистий Python, без мережі, без платних API.

Обов'язки: завантажувати, структурувати, розподіляти по агентських і спільних базах,
редагувати, перезаписувати, видаляти. Звітує Єві.

Правила (жорсткі):
- Нічого не завантажує з інтернету без явного підтвердження Андрія (`approve_download`).
- Захист — лише для файлів з міткою `andrii_protected`. Особисті завантаження Андрія мітяться автоматично.
  Мітка: лише читання — без редагування, переміщення і видалення. Зняти мітку може лише Андрій.
- Видалення файла з міткою: тільки через KODEX за командою Андрія і з його підтвердженням.
- Файли без мітки: KODEX і агенти можуть редагувати, сортувати, видаляти (видалене — в кошик на 30 днів).
  Усе, що агенти роблять самі, фіксується у звіті для Єви.
- Формат без парсера не відкидається: він стає `needs_parser` і пропонується на вивчення з підтвердженням.
"""

from __future__ import annotations
import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

PROTECTED_LABEL = "andrii_protected"
OWNER = "andrii"
TRASH_RETENTION_DAYS = 30

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
}

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
    origin: str = "agent"             # andrii (особисте завантаження) | agent (автоматичне)
    labels: List[str] = field(default_factory=list)
    versions: List[Dict[str, Any]] = field(default_factory=list)
    trashed_at: Optional[str] = None


class KodexStore:
    """Сховище — один JSON-файл. Шлях задає власник (поза git для особистих файлів)."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.records: Dict[str, Record] = {}
        self.pending: Dict[str, Dict[str, Any]] = {}
        self.log: List[Dict[str, Any]] = []
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.records = {k: Record(**v) for k, v in raw.get("records", {}).items()}
            self.pending = raw.get("pending", {})
            self.log = raw.get("log", [])

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"records": {k: asdict(v) for k, v in self.records.items()},
                "pending": self.pending, "log": self.log}
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

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

    # ------------------------------------------------------------ завантаження
    def ingest(self, name: str, data: bytes, text: str = "", origin: str = "agent",
               actor: str = "kodex") -> Dict[str, Any]:
        """origin=andrii — особисте завантаження: автоматично з міткою захисту."""
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
        labels = [PROTECTED_LABEL] if origin == OWNER else []
        rec = Record(id=uuid.uuid4().hex[:12], name=name, ext=ext, domain=classify(name, text),
                     sha256=digest, status=status, created_at=self._now(), origin=origin, labels=labels)
        rec.versions.append({"at": rec.created_at, "action": "ingest", "by": actor, "domain": rec.domain})
        self.records[rec.id] = rec
        if status == "needs_parser":
            self.pending[f"fmt:{ext}"] = {"kind": "learn_format", "ext": ext, "name": name, "state": "awaiting_andrii"}
        self._log("ingest", actor, id=rec.id, name=name, domain=rec.domain, status=status, protected=bool(labels))
        return {"status": status, "id": rec.id, "domain": rec.domain, "protected": bool(labels),
                "format": FORMATS.get(ext, {"status": "unknown"})}

    # ------------------------------------------------------------ мітка захисту (лише Андрій)
    def label(self, rec_id: str, by: str) -> Dict[str, Any]:
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_labels"}
        rec = self.records.get(rec_id)
        if rec is None or rec.status == "trashed":
            return {"status": "not_found"}
        if not self._protected(rec):
            rec.labels.append(PROTECTED_LABEL)
        self._log("labeled", by, id=rec_id)
        return {"status": "protected", "id": rec_id}

    def unlabel(self, rec_id: str, by: str) -> Dict[str, Any]:
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_unlabels"}
        rec = self.records.get(rec_id)
        if rec is None or rec.status == "trashed":
            return {"status": "not_found"}
        rec.labels = [x for x in rec.labels if x != PROTECTED_LABEL]
        self._log("unlabeled", by, id=rec_id)
        return {"status": "unprotected", "id": rec_id}

    # ------------------------------------------------------------ редагування
    def rewrite(self, rec_id: str, new_digest: str, reason: str, actor: str) -> Dict[str, Any]:
        rec = self.records.get(rec_id)
        if rec is None or rec.status == "trashed":
            return {"status": "not_found"}
        if self._protected(rec):
            return {"status": "rejected", "reason": "protected_label"}
        rec.versions.append({"at": self._now(), "action": "rewrite", "by": actor, "reason": reason,
                             "from_sha256": rec.sha256, "to_sha256": new_digest})
        rec.sha256 = new_digest
        self._log("rewrite", actor, id=rec_id, name=rec.name, reason=reason)
        return {"status": "rewritten", "id": rec_id, "versions": len(rec.versions)}

    def move(self, rec_id: str, to_domain: str, actor: str) -> Dict[str, Any]:
        rec = self.records.get(rec_id)
        if rec is None or rec.status == "trashed":
            return {"status": "not_found"}
        if self._protected(rec):
            return {"status": "rejected", "reason": "protected_label"}
        if to_domain not in DOMAINS:
            return {"status": "rejected", "reason": "unknown_domain"}
        old, rec.domain = rec.domain, to_domain
        rec.versions.append({"at": self._now(), "action": "move", "by": actor, "from": old, "to": to_domain})
        self._log("move", actor, id=rec_id, name=rec.name, frm=old, to=to_domain)
        return {"status": "moved", "id": rec_id, "from": old, "to": to_domain}

    # ------------------------------------------------------------ видалення
    def request_delete(self, rec_id: str, actor: str) -> Dict[str, Any]:
        """Файл з міткою: тільки Андрій (через KODEX) і з підтвердженням.
        Без мітки: агент видаляє сам (у кошик), дія йде у звіт Єві."""
        rec = self.records.get(rec_id)
        if rec is None or rec.status == "trashed":
            return {"status": "not_found"}
        if self._protected(rec):
            if actor != OWNER:
                return {"status": "rejected", "reason": "protected_label"}
            token = uuid.uuid4().hex[:8]
            self.pending[f"del:{token}"] = {"kind": "delete", "id": rec_id, "state": "awaiting_andrii"}
            self._log("delete_requested", actor, id=rec_id, token=token)
            return {"status": "awaiting_confirmation", "token": token, "name": rec.name}
        if actor == OWNER:
            token = uuid.uuid4().hex[:8]
            self.pending[f"del:{token}"] = {"kind": "delete", "id": rec_id, "state": "awaiting_andrii"}
            self._log("delete_requested", actor, id=rec_id, token=token)
            return {"status": "awaiting_confirmation", "token": token, "name": rec.name}
        return self._trash(rec, actor)

    def confirm_delete(self, token: str, by: str) -> Dict[str, Any]:
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_confirms"}
        item = self.pending.pop(f"del:{token}", None)
        if not item:
            return {"status": "not_found"}
        rec = self.records[item["id"]]
        return self._trash(rec, OWNER)

    def _trash(self, rec: Record, actor: str) -> Dict[str, Any]:
        rec.status = "trashed"
        rec.trashed_at = self._now()
        self._log("trashed", actor, id=rec.id, name=rec.name)
        return {"status": "trashed", "id": rec.id, "restore_until_days": TRASH_RETENTION_DAYS}

    def purge_expired(self, now: datetime) -> List[str]:
        gone = []
        for rid, rec in list(self.records.items()):
            if rec.status == "trashed" and rec.trashed_at:
                if now - datetime.fromisoformat(rec.trashed_at) >= timedelta(days=TRASH_RETENTION_DAYS):
                    del self.records[rid]
                    gone.append(rid)
        if gone:
            self._log("purged", "kodex", ids=gone)
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

    # ------------------------------------------------------------ звіт Єві
    def report_for_eva(self, since: datetime) -> Dict[str, Any]:
        """Усі дії за період, включно з тим, що агенти зробили самі (редагування, видалення)."""
        counts: Dict[str, int] = {}
        by_actor: Dict[str, int] = {}
        agent_edits: List[Dict[str, Any]] = []
        agent_deletes: List[Dict[str, Any]] = []
        for e in self.log:
            if datetime.fromisoformat(e["at"]) < since:
                continue
            counts[e["action"]] = counts.get(e["action"], 0) + 1
            by_actor[e["actor"]] = by_actor.get(e["actor"], 0) + 1
            if e["actor"] not in (OWNER, "kodex"):
                if e["action"] in ("rewrite", "move"):
                    agent_edits.append({k: e.get(k) for k in ("at", "actor", "action", "id", "name", "reason", "frm", "to")})
                if e["action"] == "trashed":
                    agent_deletes.append({k: e.get(k) for k in ("at", "actor", "id", "name")})
        awaiting = {"delete": 0, "download": 0, "format": 0}
        for key, item in self.pending.items():
            if item.get("state") == "awaiting_andrii":
                awaiting[{"del": "delete", "net": "download", "fmt": "format"}[key.split(":")[0]]] += 1
        by_status: Dict[str, int] = {}
        protected = 0
        for r in self.records.values():
            if r.status != "trashed":
                by_status[r.status] = by_status.get(r.status, 0) + 1
                protected += self._protected(r)
        return {"type": "kodex_report", "to": "eva", "since": since.isoformat(timespec="seconds"),
                "ingested": counts.get("ingest", 0), "rewritten": counts.get("rewrite", 0),
                "moved": counts.get("move", 0), "trashed": counts.get("trashed", 0),
                "duplicates_skipped": counts.get("duplicate_skipped", 0),
                "actions_by_actor": by_actor, "agent_edits": agent_edits, "agent_deletes": agent_deletes,
                "awaiting_andrii": awaiting, "protected_files": protected,
                "active_records_by_status": by_status}
