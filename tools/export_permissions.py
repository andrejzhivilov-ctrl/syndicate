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


def _row(m: Dict[str, Any]) -> str:
    skills = m.get("skills") or []
    active = [s for s in skills if s.get("activation") == "active"]
    return (f"| {m['agent_id']} | {m.get('activation', '—')} | {m.get('role_status', '—')} | "
            f"{_join(m.get('capabilities'))} | {_join(m.get('resource_scopes'))} | "
            f"{_join(m.get('services_enabled'))} | {len(skills)} (активних: {len(active)}) | {_telegram(m)} |")


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
        "| Агент | Активація | Роль | Capabilities | Resource scopes | Сервіси | Skills | Telegram |",
        "|---|---|---|---|---|---|---|---|",
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
