"""Генерує docs/PERMISSIONS_MATRIX.md з config/agents/*.profile.json.

Запуск: python tools/export_permissions.py

Джерело істини — профілі. Матрицю не редагують вручну: тест перевіряє, що файл відповідає профілям.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "config" / "agents"
OUT = ROOT / "docs" / "PERMISSIONS_MATRIX.md"


def _join(items: Any) -> str:
    if not items:
        return "—"
    if isinstance(items, dict):
        return ", ".join(sorted(items))
    return ", ".join(str(i) for i in items)


def _telegram(m: Dict[str, Any]) -> str:
    status = (m.get("telegram") or {}).get("status")
    if status:
        return status
    enabled = (m.get("inbound_channels") or {}).get("telegram", {}).get("enabled")
    return "enabled" if enabled else "—"


def _proposed_grants(m: Dict[str, Any]) -> str:
    grants = m.get("proposed_grants") or []
    if not isinstance(grants, list):
        return "—"
    values = [
        f"{item.get('capability')} ({item.get('status', 'unspecified')})"
        for item in grants
        if isinstance(item, dict) and isinstance(item.get("capability"), str)
    ]
    return ", ".join(sorted(values)) if values else "—"


def _row(m: Dict[str, Any]) -> str:
    skills = m.get("skills") or []
    active = [s for s in skills if s.get("activation") == "active"]
    reference_skills = m.get("reference_skills") or []
    return (f"| {m['agent_id']} | {m.get('activation', '—')} | {m.get('role_status', '—')} | "
            f"{_join(m.get('capabilities'))} | {_join(m.get('resource_scopes'))} | "
            f"{_join(m.get('services_enabled'))} | {_proposed_grants(m)} | "
            f"{len(skills)} (активних: {len(active)}) | {_join(reference_skills)} | {_telegram(m)} |")


def build() -> str:
    manifests: List[Dict[str, Any]] = []
    for path in sorted(PROFILES.glob("*.profile.json")):
        manifests.append(json.loads(path.read_text(encoding="utf-8")))
    lines = [
        "# Матриця прав агентів (генерується)",
        "",
        "> Не редагувати вручну. Джерело — `config/agents/*.profile.json`.",
        "> Перегенерація: `python tools/export_permissions.py`. "
        "Тест `tests/test_permissions_matrix.py` перевіряє відповідність.",
        "",
        "За замовчуванням — відмова (default-deny): усе, чого немає в колонках, заборонено.",
        "",
        "| Агент | Активація | Роль | Capabilities | Resource scopes | Сервіси | Proposed grants (не застосовані) | Skills | Reference skills (read-only) | Telegram |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    lines += [_row(m) for m in manifests]
    lines += [
        "",
        "## Спільні правила доступу (поза профілями)",
        "",
        "- Мітка `andrii_protected`: читання — всі; переміщення — KODEX і агенти; "
        "редагування/видалення — лише з дозволу Андрія.",
        "- Файли без мітки: KODEX і агенти редагують, сортують, видаляють самі; усе йде у звіт Єві.",
        "- Інтернет і будь-яке завантаження (включно з YouTube) — лише з підтвердження Андрія.",
        "- Видалення — у кошик на 30 днів; остаточне видалення автоматичне.",
        "- Telegram: лише Андрій (allowlist); порожній allowlist = відмова.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    OUT.write_text(build(), encoding="utf-8")
    print(f"written {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
