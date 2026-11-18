"""Each agent's own folder in Obsidian, laid out before the agent writes its first note (16.11.2026).

Andrii: the agent's folder is the agent's; it builds there what it needs, and gives him on Drive
only what he asked for. The layout and one map note are created at start when missing; nothing
that exists is changed. The map is what the agent reads first, so it does not walk the vault.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

#: agent -> (own folder, sub-folders). Матеріали is fed by the Drive mirror and shelved by Eva.
LAYOUT: Dict[str, Tuple[str, Tuple[str, ...]]] = {
    "trainer": ("Health_Coach", (
        "Щоденник/Рефлексія", "Щоденник/Заміри", "Щоденник/Тренування", "Щоденник/Харчування",
        "Щоденник/Самопочуття", "Програми", "Харчування/Рецепти", "Харчування/Продукти", "Аналізи",
        "Добавки", "Психологія", "Дослідження", "Конспекти/Відео", "Таблиці", "Матеріали",
    )),
}
MAP_NOTE = "Карта.md"
TRAINER_MAP = """---
summary: "Де що лежить у теці Алекса; читай спершу це, а не все сховище"
tags: [алекс, карта]
---

# Карта теки Алекса

- **Щоденник/** — день за днем: `Рефлексія/` (щоночі о 04:00), `Заміри/`, `Тренування/`, `Харчування/`, `Самопочуття/`. Одна нотатка на день: `РРРР-ММ-ДД.md`.
- **Програми/** — програми тренувань; поточна позначена `status: active` у властивостях.
- **Харчування/** — `Рецепти/` (рецепти Андрія й перероблені), `Продукти/` (КБЖУ з джерелом).
- **Аналізи/** — аналізи крові й обстеження; лише факти з бланків, з датою.
- **Добавки/**, **Психологія/** — протоколи й нотатки.
- **Дослідження/** — конспекти свіжих досліджень з неділі: посилання, дизайн, вибірка, висновок.
- **Конспекти/** — книги й курси; **Конспекти/Відео/** — відео за посиланням.
- **Таблиці/** — таблиці Алекса (`.xlsx`) і їхні копії `.md` для пошуку.
- **Матеріали/** — що Андрій закинув на Drive чи в чат; Єва розкладає й веде `Матеріали/Каталог.md`.

Як шукати дешево: спершу ця карта й `Матеріали/Каталог.md`, далі `summary` у властивостях нотатки, і лише тоді весь текст.
"""
MAPS = {"trainer": TRAINER_MAP}


def ensure(agent: str, root: Path) -> List[str]:
    """Create what is missing; return what was created. Existing folders and notes stay as they are."""
    if agent not in LAYOUT:
        return []
    own, subs = LAYOUT[agent]
    created = []
    for sub in ("", *subs):
        folder = root / own / sub if sub else root / own
        if not folder.is_dir():
            folder.mkdir(parents=True, exist_ok=True)
            created.append(f"{own}/{sub}".rstrip("/"))
    note = root / own / MAP_NOTE
    if agent in MAPS and not note.exists():
        note.write_text(MAPS[agent], encoding="utf-8")
        created.append(f"{own}/{MAP_NOTE}")
    return created
