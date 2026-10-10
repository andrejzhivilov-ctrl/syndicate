"""Док — бібліотека вправ (вендорений free-exercise-db, Unlicense; дані без зображень).

Пошук і фільтр. Нічого не завантажує з мережі.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DB = Path(__file__).resolve().parents[2] / "doc_core" / "vendor" / "free-exercise-db" / "dist" / "exercises.json"
LEVELS = ("beginner", "intermediate", "expert")


def load_exercises(path: Path = DEFAULT_DB) -> List[Dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    # Зображення не беремо: поле images лишається в даних, але не використовується.
    return [{k: v for k, v in e.items() if k != "images"} for e in data]


def search(exercises: List[Dict[str, Any]], muscle: Optional[str] = None,
           equipment: Optional[str] = None, level: Optional[str] = None,
           limit: int = 10) -> List[Dict[str, Any]]:
    if level is not None and level not in LEVELS:
        raise ValueError(f"level must be one of {LEVELS}")
    out = []
    for e in exercises:
        if muscle and muscle not in (e.get("primaryMuscles") or []) + (e.get("secondaryMuscles") or []):
            continue
        if equipment and e.get("equipment") != equipment:
            continue
        if level and e.get("level") != level:
            continue
        out.append({"name": e.get("name"), "level": e.get("level"), "equipment": e.get("equipment"),
                    "primaryMuscles": e.get("primaryMuscles", []), "category": e.get("category")})
        if len(out) >= limit:
            break
    return out
