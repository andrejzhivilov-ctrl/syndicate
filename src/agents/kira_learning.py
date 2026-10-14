"""Самонавчання Кіри: облік відповідей, слабкі теми, пропозиції на схвалення Андрія.

Межі (з правил проєкту):
- Кіра вимірює тільки те, що реально перевірила: відповідь на питання з банку, яку порівняно
  з ключем. Оцінка знань без достатньої кількості відповідей не виводиться (``accuracy=None``).
- Кіра може **пропонувати** дисципліни, питання й ранкові елементи. Застосовує їх лише
  ``decide(..., by="andrii")``. Єва і сама Кіра схвалювати не можуть.
- Дані зберігаються в ``KIRA_DATA_DIR`` (поза git). Без шляху навчання недоступне, а не імітується.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.agents.kira_catalog import CatalogError, build_catalog, load_seed

OWNER = "andrii"
PROPOSAL_KINDS = ("new_discipline", "new_quiz_item", "new_morning_item")
MIN_ANSWERS_FOR_STATS = 3
WEAK_ACCURACY = 0.6


def _empty_overlay() -> Dict[str, Any]:
    return {"disciplines": {}, "quiz_bank": [], "morning_items": {}}


class KiraLearningStore:
    def __init__(self, path: Optional[Path], seed: Optional[Dict[str, Any]] = None) -> None:
        self.path = Path(path) if path else None
        self._seed = seed if seed is not None else load_seed()
        self.answers: List[Dict[str, Any]] = []
        self.proposals: List[Dict[str, Any]] = []
        self.approved: Dict[str, Any] = _empty_overlay()
        if self.path and self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.answers = raw.get("answers", [])
            self.proposals = raw.get("proposals", [])
            self.approved = raw.get("approved", _empty_overlay())

    @property
    def available(self) -> bool:
        return self.path is not None

    def save(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"answers": self.answers, "proposals": self.proposals, "approved": self.approved}
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.path)

    def catalog(self) -> Dict[str, Any]:
        """Актуальний каталог: базовий seed + схвалені Андрієм доповнення (перевірені)."""
        return build_catalog(self._seed, self.approved)

    # ------------------------------------------------------------ відповіді й статистика
    def record_answer(self, item_id: str, choice: str, student: str = "andrii") -> Dict[str, Any]:
        if not self.available:
            return {"status": "unavailable", "reason": "learning_store_not_configured"}
        item = next((q for q in self.catalog()["quiz_bank"] if q["id"] == item_id), None)
        if item is None:
            return {"status": "not_found", "question_id": item_id}
        choice = str(choice).strip().upper()
        if choice not in item["options"]:
            return {"status": "rejected", "reason": "choice_must_be_A_to_D"}
        correct = choice == item["answer"]
        self.answers.append({
            "at": datetime.now().isoformat(timespec="seconds"),
            "student": student,
            "question_id": item_id,
            "discipline": item["discipline"],
            "topic": item["topic"],
            "correct": correct,
        })
        self.save()
        return {
            "status": "recorded",
            "question_id": item_id,
            "correct": correct,
            "correct_answer": item["answer"],
            "explanation": item["explanation"],
        }

    def topic_stats(self) -> Dict[str, Dict[str, Any]]:
        out: Dict[str, Dict[str, Any]] = {}
        for a in self.answers:
            key = f"{a['discipline']}/{a['topic']}"
            row = out.setdefault(key, {"answered": 0, "correct": 0})
            row["answered"] += 1
            row["correct"] += 1 if a["correct"] else 0
        for row in out.values():
            n = row["answered"]
            row["accuracy"] = round(row["correct"] / n, 2) if n >= MIN_ANSWERS_FOR_STATS else None
            if n < MIN_ANSWERS_FOR_STATS:
                row["note"] = f"недостатньо відповідей (потрібно {MIN_ANSWERS_FOR_STATS})"
        return out

    def weak_topics(self) -> List[str]:
        return sorted(
            key for key, row in self.topic_stats().items()
            if row["accuracy"] is not None and row["accuracy"] < WEAK_ACCURACY
        )

    def next_quiz_item(self, discipline: str, topic: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Питання для наступної перевірки: спершу слабка тема, далі невідповідані, далі будь-яке."""
        bank = [q for q in self.catalog()["quiz_bank"] if q["discipline"] == discipline]
        if topic:
            bank = [q for q in bank if q["topic"] == topic]
        if not bank:
            return None
        weak = {w.split("/", 1)[1] for w in self.weak_topics() if w.startswith(f"{discipline}/")}
        answered = {a["question_id"] for a in self.answers}
        # Слабка тема тренується далі, навіть якщо її питання вже були (повторення — суть тренування).
        for pool in (
            [q for q in bank if q["topic"] in weak and q["id"] not in answered],
            [q for q in bank if q["topic"] in weak],
            [q for q in bank if q["id"] not in answered],
            bank,
        ):
            if pool:
                return pool[0]
        return None

    # ------------------------------------------------------------ пропозиції
    def propose(self, kind: str, payload: Dict[str, Any], reason: str, proposed_by: str = "kira") -> Dict[str, Any]:
        if not self.available:
            return {"status": "unavailable", "reason": "learning_store_not_configured"}
        if kind not in PROPOSAL_KINDS:
            return {"status": "rejected", "reason": "unknown_kind", "allowed": list(PROPOSAL_KINDS)}
        if not isinstance(reason, str) or not reason.strip():
            return {"status": "rejected", "reason": "reason_required"}
        try:
            self._validate_as_overlay(kind, payload)
        except CatalogError as exc:
            return {"status": "rejected", "reason": "invalid_payload", "detail": str(exc)}
        pid = uuid.uuid4().hex[:8]
        self.proposals.append({
            "id": pid,
            "kind": kind,
            "payload": payload,
            "reason": reason.strip(),
            "proposed_by": proposed_by,
            "state": "pending",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        })
        self.save()
        return {"status": "pending", "proposal_id": pid, "kind": kind}

    def pending(self) -> List[Dict[str, Any]]:
        return [p for p in self.proposals if p["state"] == "pending"]

    def decide(self, proposal_id: str, decision: str, by: str) -> Dict[str, Any]:
        if by != OWNER:
            return {"status": "rejected", "reason": "only_andrii_decides"}
        if decision not in ("approve", "reject"):
            return {"status": "rejected", "reason": "decision_must_be_approve_or_reject"}
        item = next((p for p in self.proposals if p["id"] == proposal_id), None)
        if item is None or item["state"] != "pending":
            return {"status": "not_found", "proposal_id": proposal_id}
        if decision == "reject":
            item["state"] = "rejected"
            item["decided_by"] = by
            self.save()
            return {"status": "rejected", "proposal_id": proposal_id}
        try:
            self._apply(item["kind"], item["payload"])
        except CatalogError as exc:
            return {"status": "rejected", "reason": "invalid_payload", "detail": str(exc)}
        item["state"] = "approved"
        item["decided_by"] = by
        self.save()
        return {"status": "approved", "proposal_id": proposal_id, "kind": item["kind"]}

    # ------------------------------------------------------------ внутрішнє
    def _validate_as_overlay(self, kind: str, payload: Dict[str, Any]) -> None:
        trial = json.loads(json.dumps(self.approved))
        self._add_to_overlay(trial, kind, payload)
        build_catalog(self._seed, trial)

    def _apply(self, kind: str, payload: Dict[str, Any]) -> None:
        trial = json.loads(json.dumps(self.approved))
        self._add_to_overlay(trial, kind, payload)
        build_catalog(self._seed, trial)  # перевірка перед записом
        self.approved = trial

    @staticmethod
    def _add_to_overlay(overlay: Dict[str, Any], kind: str, payload: Dict[str, Any]) -> None:
        if kind == "new_discipline":
            key = payload.get("key")
            if not isinstance(key, str):
                raise CatalogError("new_discipline: key is required")
            overlay["disciplines"][key] = {k: payload.get(k) for k in ("title", "icon", "focus", "topics")}
        elif kind == "new_quiz_item":
            overlay["quiz_bank"].append(dict(payload, status="approved_by_andrii"))
        elif kind == "new_morning_item":
            overlay["morning_items"].setdefault(payload.get("kind", ""), []).append(
                {"text": payload.get("text"), "source": "approved_by_andrii"}
            )
        else:
            raise CatalogError(f"unknown kind {kind}")
