"""Каталог Академії Кіри: дисципліни, банк питань, ранкові елементи.

Дані, не код. Базовий файл — ``kira_catalog_seed.json`` (лежить у ``src/``, бо образ
agent-контейнера копіює ``src/``). Доповнення, схвалені Андрієм, зберігаються окремо
в ``KIRA_DATA_DIR`` (через ``kira_learning``) і зливаються поверх базового каталогу.

Правило: недійсний елемент каталогу не потрапляє в навчання. Перевірка — тут.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

SEED_PATH = Path(__file__).with_name("kira_catalog_seed.json")
ANSWER_KEYS = ("A", "B", "C", "D")
MORNING_KINDS = ("word_of_the_day", "coding_spark", "history_model")
_KEY_RE = re.compile(r"^[a-z][a-z0-9_]{1,40}$")
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,60}$")


class CatalogError(ValueError):
    """Елемент каталогу не пройшов перевірку схеми."""


def validate_discipline(key: str, d: Any) -> Dict[str, Any]:
    if not isinstance(key, str) or not _KEY_RE.match(key):
        raise CatalogError(f"invalid discipline key: {key!r}")
    if not isinstance(d, dict):
        raise CatalogError(f"discipline {key} must be an object")
    for field in ("title", "icon", "focus"):
        if not isinstance(d.get(field), str) or not d[field].strip():
            raise CatalogError(f"discipline {key}: field {field} is required")
    topics = d.get("topics")
    if not isinstance(topics, list) or not topics or not all(isinstance(t, str) and t.strip() for t in topics):
        raise CatalogError(f"discipline {key}: topics must be a non-empty list of strings")
    return {"title": d["title"], "icon": d["icon"], "focus": d["focus"], "topics": list(topics)}


def validate_quiz_item(item: Any, disciplines: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(item, dict):
        raise CatalogError("quiz item must be an object")
    qid = item.get("id")
    if not isinstance(qid, str) or not _ID_RE.match(qid):
        raise CatalogError(f"invalid quiz id: {qid!r}")
    if item.get("discipline") not in disciplines:
        raise CatalogError(f"quiz {qid}: unknown discipline {item.get('discipline')!r}")
    if item.get("topic") not in disciplines[item["discipline"]]["topics"]:
        raise CatalogError(f"quiz {qid}: topic is not in discipline {item['discipline']}")
    for field in ("question", "explanation"):
        if not isinstance(item.get(field), str) or not item[field].strip():
            raise CatalogError(f"quiz {qid}: field {field} is required")
    options = item.get("options")
    if not isinstance(options, dict) or sorted(options) != sorted(ANSWER_KEYS):
        raise CatalogError(f"quiz {qid}: options must have exactly keys A, B, C, D")
    if not all(isinstance(v, str) and v.strip() for v in options.values()):
        raise CatalogError(f"quiz {qid}: every option needs text")
    if item.get("answer") not in ANSWER_KEYS:
        raise CatalogError(f"quiz {qid}: answer must be one of A-D")
    return {
        "id": qid,
        "discipline": item["discipline"],
        "topic": item["topic"],
        "question": item["question"],
        "options": {k: options[k] for k in ANSWER_KEYS},
        "answer": item["answer"],
        "explanation": item["explanation"],
        "status": str(item.get("status", "approved")),
    }


def validate_morning_item(kind: str, item: Any) -> Dict[str, Any]:
    if kind not in MORNING_KINDS:
        raise CatalogError(f"unknown morning kind: {kind!r}")
    if not isinstance(item, dict) or not isinstance(item.get("text"), str) or not item["text"].strip():
        raise CatalogError(f"morning {kind}: text is required")
    return {"text": item["text"], "source": str(item.get("source", "approved"))}


def load_seed(path: Path = SEED_PATH) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _merge_disciplines(seed: Dict[str, Any], approved: Dict[str, Any]) -> Dict[str, Any]:
    disciplines: Dict[str, Any] = {}
    for key, d in (seed.get("disciplines") or {}).items():
        disciplines[key] = validate_discipline(key, d)
    for key, d in (approved.get("disciplines") or {}).items():
        if key in disciplines:
            raise CatalogError(f"discipline {key} already exists")
        disciplines[key] = validate_discipline(key, d)
    return disciplines


def _merge_bank(seed: Dict[str, Any], approved: Dict[str, Any], disciplines: Dict[str, Any]) -> List[Dict[str, Any]]:
    bank: List[Dict[str, Any]] = []
    seen_ids = set()
    for item in list(seed.get("quiz_bank") or []) + list(approved.get("quiz_bank") or []):
        clean = validate_quiz_item(item, disciplines)
        if clean["id"] in seen_ids:
            raise CatalogError(f"duplicate quiz id: {clean['id']}")
        seen_ids.add(clean["id"])
        bank.append(clean)
    return bank


def _merge_morning(seed: Dict[str, Any], approved: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    morning: Dict[str, List[Dict[str, Any]]] = {k: [] for k in MORNING_KINDS}
    for source in (seed.get("morning_items") or {}, approved.get("morning_items") or {}):
        for kind, items in source.items():
            for item in items:
                morning[kind].append(validate_morning_item(kind, item))
    for kind in MORNING_KINDS:
        if not morning[kind]:
            raise CatalogError(f"morning kind {kind} has no items")
    return morning


def build_catalog(seed: Dict[str, Any], approved: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Злити базовий каталог і схвалені доповнення. Усе перевіряється; помилка → CatalogError."""
    approved = approved or {}
    disciplines = _merge_disciplines(seed, approved)
    return {
        "disciplines": disciplines,
        "quiz_bank": _merge_bank(seed, approved, disciplines),
        "morning_items": _merge_morning(seed, approved),
    }
