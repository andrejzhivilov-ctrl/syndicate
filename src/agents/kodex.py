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
    origin: str = "agent"
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
        labeled = origin == "andrii_direct" or (origin == "andrii_kodex" and protect)
        labels = [PROTECTED_LABEL] if labeled else []
        rec = Record(id=uuid.uuid4().hex[:12], name=name, ext=ext, domain=classify(name, text),
                     sha256=digest, status=status, created_at=self._now(), origin=origin, labels=labels)
        rec.versions.append({"at": rec.created_at, "action": "ingest", "by": actor, "domain": rec.domain})
        self.records[rec.id] = rec
        if status == "needs_parser":
            self.pending[f"fmt:{ext}"] = {"kind": "learn_format", "ext": ext, "name": name,
                                           "state": "awaiting_andrii"}
        self._log("ingest", actor, id=rec.id, name=name, domain=rec.domain, status=status,
                  origin=origin, protected=labeled)
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
    def rewrite(self, rec_id: str, new_digest: str, reason: str, actor: str) -> Dict[str, Any]:
        """Без мітки — одразу. З міткою — лише після дозволу Андрія (повертає token)."""
        rec = self._live(rec_id)
        if rec is None:
            return {"status": "not_found"}
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
        if item["kind"] == "delete":
            return self._trash(rec, OWNER, requested_by=item["actor"])
        return self._apply_rewrite(rec, item["new_digest"], item["reason"], OWNER, requested_by=item["actor"])

    def reject(self, token: str, by: str) -> Dict[str, Any]:
        """Андрій забороняє зміну мічених файлів: запит закривається, файл не змінюється."""
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_rejects"}
        item = self.pending.pop(f"chg:{token}", None)
        if item is None:
            return {"status": "not_found"}
        self._log("permission_denied", by, id=item["id"], change=item["kind"], requested_by=item["actor"])
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
    def _actions_since(self, since: datetime) -> List[Dict[str, Any]]:
        return [e for e in self.log if datetime.fromisoformat(e["at"]) >= since]

    def _agent_actions(self, entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Дії KODEX і агентів (усе, крім дій Андрія) — для звіту Єві."""
        out: Dict[str, List[Dict[str, Any]]] = {"edits": [], "deletes": [], "moves": []}
        keys = ("at", "actor", "id", "name")
        for e in entries:
            if e["actor"] == OWNER:
                continue
            if e["action"] == "rewrite":
                out["edits"].append({k: e.get(k) for k in keys + ("reason",)})
            elif e["action"] == "trashed":
                out["deletes"].append({k: e.get(k) for k in keys})
            elif e["action"] == "move":
                out["moves"].append({k: e.get(k) for k in keys + ("frm", "to", "protected")})
        return out

    def _pending_counts(self) -> Dict[str, int]:
        counts = {"delete": 0, "download": 0, "format": 0, "permission": 0}
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
                "awaiting_andrii": self._pending_counts(),
                "protected_files": sum(self._protected(r) for r in self.records.values() if r.status != "trashed"),
                "active_records_by_status": by_status}
