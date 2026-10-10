"""K.O.D.E.K.S. (KODEX) — архіви й бази знань синдикату. Чистий Python, без мережі, без платних API.

Обов'язки: завантажувати, структурувати, розподіляти по агентських і спільних базах,
редагувати, перезаписувати, видаляти. Звітує Єві.

Правила (жорсткі):
- Нічого не завантажує з інтернету без явного підтвердження Андрія (`approve_download`).
- Видалення — двоетапне: запит → підтвердження Андрієм. Видалене йде в кошик (soft delete).
- Архів `andrii_medical_vault` [ANDRII_IMMUTABLE]: читання дозволене; запис і видалення — заборонені
  для всіх агентів, включно з KODEX.
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

IMMUTABLE_DOMAIN = "andrii_medical_vault"
TRASH_RETENTION_DAYS = 30

# ---------------------------------------------------------------- формати
# status: native (текст читаємо напряму), vendored_parser (через вендорений book-to-skill),
# library_installed (бібліотека в venv), needs_engine (потрібен окремий безкоштовний рушій),
# needs_parser (невідомий формат — вивчити з підтвердженням).
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
    "mp3": {"status": "needs_engine", "lib": "локальний Whisper (безкоштовний), транскрибація"},
    "wav": {"status": "needs_engine", "lib": "локальний Whisper"},
    "m4a": {"status": "needs_engine", "lib": "локальний Whisper"},
    "mp4": {"status": "needs_engine", "lib": "локальний Whisper + ffmpeg"},
}

# ---------------------------------------------------------------- домени
# Агентські бази. KODEX може писати в усі, крім IMMUTABLE_DOMAIN.
DOMAINS = ("andrii_medical_vault", "doc", "fin", "sam", "eva", "architect", "marshal", "kira", "shared")

# Класифікація — детермінована, за ключовими словами. Без LLM.
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
    status: str                     # stored | needs_parser | needs_engine | trashed
    created_at: str
    versions: List[Dict[str, Any]] = field(default_factory=list)
    trashed_at: Optional[str] = None


class KodexStore:
    """Сховище — один JSON-файл. Шлях задає власник (поза git, для медичних даних — окремо)."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.records: Dict[str, Record] = {}
        self.pending: Dict[str, Dict[str, Any]] = {}     # підтвердження: видалення, інтернет, формат
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

    def _log(self, action: str, **kw: Any) -> None:
        self.log.append({"at": datetime.now().isoformat(timespec="seconds"), "action": action, **kw})

    def _hash_exists(self, digest: str) -> Optional[str]:
        for r in self.records.values():
            if r.sha256 == digest and r.status != "trashed":
                return r.id
        return None

    # ------------------------------------------------------------ завантаження
    def ingest(self, name: str, data: bytes, text: str = "", sensitivity: str = "public") -> Dict[str, Any]:
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        digest = sha256_of(data)
        dup = self._hash_exists(digest)
        if dup:
            self._log("duplicate_skipped", name=name, existing=dup)
            return {"status": "duplicate", "existing_id": dup}
        fmt = FORMATS.get(ext)
        if fmt is None:
            status = "needs_parser"
        elif fmt["status"] == "needs_engine":
            status = "needs_engine"
        else:
            status = "stored"
        domain = IMMUTABLE_DOMAIN if sensitivity == "medical" else classify(name, text)
        rec = Record(id=uuid.uuid4().hex[:12], name=name, ext=ext, domain=domain, sha256=digest,
                     status=status, created_at=datetime.now().isoformat(timespec="seconds"))
        rec.versions.append({"at": rec.created_at, "action": "ingest", "domain": domain})
        self.records[rec.id] = rec
        if status == "needs_parser":
            self.pending[f"fmt:{ext}"] = {"kind": "learn_format", "ext": ext, "name": name, "by": "andrii",
                                           "state": "awaiting_andrii"}
        self._log("ingest", id=rec.id, name=name, domain=domain, status=status)
        return {"status": status, "id": rec.id, "domain": domain, "format": FORMATS.get(ext, {"status": "unknown"})}

    # ------------------------------------------------------------ редагування
    def rewrite(self, rec_id: str, new_text_digest: str, reason: str) -> Dict[str, Any]:
        rec = self.records.get(rec_id)
        if rec is None or rec.status == "trashed":
            return {"status": "not_found"}
        if rec.domain == IMMUTABLE_DOMAIN:
            return {"status": "rejected", "reason": "immutable_domain"}
        rec.versions.append({"at": datetime.now().isoformat(timespec="seconds"), "action": "rewrite",
                             "from_sha256": rec.sha256, "to_sha256": new_text_digest, "reason": reason})
        rec.sha256 = new_text_digest
        self._log("rewrite", id=rec_id, reason=reason)
        return {"status": "rewritten", "id": rec_id, "versions": len(rec.versions)}

    def move(self, rec_id: str, to_domain: str) -> Dict[str, Any]:
        rec = self.records.get(rec_id)
        if rec is None or rec.status == "trashed":
            return {"status": "not_found"}
        if rec.domain == IMMUTABLE_DOMAIN or to_domain == IMMUTABLE_DOMAIN:
            return {"status": "rejected", "reason": "immutable_domain"}
        if to_domain not in DOMAINS:
            return {"status": "rejected", "reason": "unknown_domain"}
        old = rec.domain
        rec.domain = to_domain
        rec.versions.append({"at": datetime.now().isoformat(timespec="seconds"), "action": "move",
                             "from": old, "to": to_domain})
        self._log("move", id=rec_id, frm=old, to=to_domain)
        return {"status": "moved", "id": rec_id, "from": old, "to": to_domain}

    # ------------------------------------------------------------ видалення (двоетапне)
    def request_delete(self, rec_id: str) -> Dict[str, Any]:
        rec = self.records.get(rec_id)
        if rec is None or rec.status == "trashed":
            return {"status": "not_found"}
        if rec.domain == IMMUTABLE_DOMAIN:
            return {"status": "rejected", "reason": "immutable_domain"}
        token = uuid.uuid4().hex[:8]
        self.pending[f"del:{token}"] = {"kind": "delete", "id": rec_id, "state": "awaiting_andrii"}
        self._log("delete_requested", id=rec_id, token=token)
        return {"status": "awaiting_confirmation", "token": token, "name": rec.name}

    def confirm_delete(self, token: str, by: str) -> Dict[str, Any]:
        if by != "andrii":
            return {"status": "rejected", "reason": "only_andrii_confirms"}
        item = self.pending.pop(f"del:{token}", None)
        if not item:
            return {"status": "not_found"}
        rec = self.records[item["id"]]
        rec.status = "trashed"
        rec.trashed_at = datetime.now().isoformat(timespec="seconds")
        self._log("trashed", id=rec.id)
        return {"status": "trashed", "id": rec.id, "restore_until_days": TRASH_RETENTION_DAYS}

    def purge_expired(self, now: datetime) -> List[str]:
        """Остаточне видалення з кошика через 30 днів."""
        gone = []
        for rid, rec in list(self.records.items()):
            if rec.status == "trashed" and rec.trashed_at:
                if now - datetime.fromisoformat(rec.trashed_at) >= timedelta(days=TRASH_RETENTION_DAYS):
                    del self.records[rid]
                    gone.append(rid)
        if gone:
            self._log("purged", ids=gone)
        return gone

    # ------------------------------------------------------------ інтернет і формати (підтвердження)
    def request_download(self, url: str, reason: str) -> Dict[str, Any]:
        req = uuid.uuid4().hex[:8]
        self.pending[f"net:{req}"] = {"kind": "download", "url": url, "reason": reason, "state": "awaiting_andrii"}
        self._log("download_requested", req=req, url=url)
        return {"status": "awaiting_andrii_approval", "request": req}

    def approve_download(self, req: str, by: str) -> Dict[str, Any]:
        if by != "andrii":
            return {"status": "rejected", "reason": "only_andrii_approves"}
        item = self.pending.get(f"net:{req}")
        if not item:
            return {"status": "not_found"}
        item["state"] = "approved"
        self._log("download_approved", req=req)
        return {"status": "approved", "url": item["url"]}

    def download_allowed(self, req: str) -> bool:
        """Завантаження дозволене лише після підтвердження Андрія. Без нього — False."""
        item = self.pending.get(f"net:{req}")
        return bool(item and item.get("state") == "approved")

    def approve_format(self, ext: str, by: str) -> Dict[str, Any]:
        if by != "andrii":
            return {"status": "rejected", "reason": "only_andrii_approves"}
        item = self.pending.get(f"fmt:{ext}")
        if not item:
            return {"status": "not_found"}
        item["state"] = "approved_to_learn"
        self._log("format_learning_approved", ext=ext)
        return {"status": "approved_to_learn", "ext": ext}

    # ------------------------------------------------------------ звіт Єві
    def report_for_eva(self, since: datetime) -> Dict[str, Any]:
        counts: Dict[str, int] = {}
        for e in self.log:
            if datetime.fromisoformat(e["at"]) >= since:
                counts[e["action"]] = counts.get(e["action"], 0) + 1
        awaiting = {"delete": 0, "download": 0, "format": 0}
        for key, item in self.pending.items():
            if item.get("state") == "awaiting_andrii":
                awaiting[{"del": "delete", "net": "download", "fmt": "format"}[key.split(":")[0]]] += 1
        by_status: Dict[str, int] = {}
        for r in self.records.values():
            if r.status != "trashed":
                by_status[r.status] = by_status.get(r.status, 0) + 1
        return {"type": "kodex_report", "to": "eva", "since": since.isoformat(timespec="seconds"),
                "ingested": counts.get("ingest", 0), "rewritten": counts.get("rewrite", 0),
                "moved": counts.get("move", 0), "trashed": counts.get("trashed", 0),
                "duplicates_skipped": counts.get("duplicate_skipped", 0),
                "awaiting_andrii": awaiting, "active_records_by_status": by_status}
