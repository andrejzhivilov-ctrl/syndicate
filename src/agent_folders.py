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
    # 18.11.2026: the holding inbox and each agent's materials, so Eva has somewhere to route to.
    # The full layout of each agent comes with that agent's rollout.
    "eva": ("00_Inbox", ("Вхідні", "На перевірку")),
    "eva_base": ("09_База_Знань", ("Матеріали",)),
    # 19.11.2026: Sam's rollout on Hermes.
    "sam": ("Сем", (
        "Стратегії", "Журнал/Паперовий", "Звіти", "Ринки/Форекс і метали", "Ринки/Крипта/Проекти", "Ринки/Акції й ф'ючерси",
        "Ставки", "Дослідження", "Конспекти/Відео", "Таблиці", "Матеріали", "База",
    )),
    "tyler": ("Тайлер", ("Матеріали",)),
    "fin": ("Фін", ("Матеріали",)),
    "kira": ("Кіра", ("Матеріали",)),
    "marshal": ("Маршал", ("Матеріали",)),
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
SAM_MAP = """---
summary: "Де що лежить у теці Сема; читай спершу це"
tags: [сем, карта]
---

# Карта теки Сема

- **База/** — правила, які встановив Андрій: ризик ($100-протокол), HITL і кнопки, операційна модель, перемикач виконання, шорт-ліст брокерів. Їх лише читаєш.
- **Стратегії/** — кожна стратегія окремою нотаткою: правила входу й виходу, ринок, таймфрейм, результати бектесту з джерелом даних.
- **Журнал/Паперовий/** — паперові угоди й ставки по днях (`РРРР-ММ-ДД.md`); `Журнал/Уроки.md` — негативні уроки.
- **Ринки/** — нотатки по форексу й металах, крипті, акціях і ф'ючерсах.
- **Ставки/** — моделі й журнал ставок (CLV, маржа, дробовий Келлі).
- **Дослідження/**, **Конспекти/** (і **Конспекти/Відео/**) — що вивчено, з посиланнями.
- **Таблиці/** — графіки й таблиці з run_python і table_save.
- **Матеріали/** — що Андрій закинув; Єва розкладає й веде `Матеріали/Каталог.md`.
"""
MAPS = {"trainer": TRAINER_MAP, "sam": SAM_MAP}
#: Rules Andrii already set for an agent (repo docs), copied into its Obsidian folder once, read-only for it.
BASE_DOCS: Dict[str, Tuple[str, Tuple[str, ...]]] = {
    "sam": ("База", ("SAM_RISK_BLOCKS.md", "SAM_HITL_CONTRACT.md", "SAM_OPERATING_MODEL.md",
                     "SAM_EXECUTION_SWITCH.md", "SAM_BROKER_SHORTLIST_2026-10-10.md", "SAM_ROLE_BOUNDARIES.md")),
}
DOCS_ROOT = Path(__file__).resolve().parents[1] / "sam_core"


def _copy_base(agent: str, root: Path) -> List[str]:
    if agent not in BASE_DOCS:
        return []
    folder, names = BASE_DOCS[agent]
    target_dir = root / LAYOUT[agent][0] / folder
    copied = []
    for name in names:
        source, target = DOCS_ROOT / name, target_dir / name
        if source.is_file() and not target.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
            target.write_text("---\nandrii_protected: true\nsource: \"repo sam_core/" + name + "\"\n---\n\n"
                              + source.read_text(encoding="utf-8"), encoding="utf-8")
            copied.append(f"{LAYOUT[agent][0]}/{folder}/{name}")
    return copied


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
    return created + _copy_base(agent, root)
