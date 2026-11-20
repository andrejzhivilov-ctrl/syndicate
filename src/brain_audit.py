"""Eva's monthly audit of the Second Brain (Andrii, 20.11.2026: once a month Eva clears the rubbish).

Built on the archivist's rules (src/obsidian_archivist.py), so nothing new is allowed here:

- Rubbish Eva may clear on her own: empty notes and the extra copies of exact duplicates, and only
  when none of the archivist's reasons apply (Andrii's mark, links from other notes, changed this
  week, a hub or regulation, something that looks like a secret). "Clear" is a move into
  ``_Кошик_агентів``: nothing is deleted, Andrii empties the bin himself.
- Everything else (near duplicates, notes stuck in the inbox, anything important) is a proposal in
  the report, waiting for Andrii's word.

The report is a note in Eva's folder and a short message to Andrii from Eva's bot.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from src import brain

CLEARS = ("empty", "duplicate")
REPORT_DIR = ("Єва", "Аудит")


def _extras(item: Dict[str, Any]) -> List[str]:
    """The paths of an item that would go to the bin (a duplicate group keeps its first copy)."""
    if item["kind"] == "empty":
        return item["paths"]
    keep = item["proposal"].split("залишити ", 1)[-1].split(",", 1)[0].strip()
    return [p for p in item["paths"] if not p.endswith("/" + keep) and p != keep]


def run(root: Any, apply: bool = True) -> Dict[str, Any]:
    from src.obsidian_archivist import Archivist, default_log

    archivist = Archivist(root, default_log(), "eva")
    plan = archivist.plan()
    moved: List[str] = []
    asked: List[Dict[str, Any]] = []
    for item in plan["items"]:
        if item["kind"] in CLEARS and not item["needs_permission"] and apply:
            for rel in _extras(item):
                if archivist.trash(rel).get("status") == "trashed":
                    moved.append(rel)
        else:
            asked.append(item)
    note = _report(root, plan, moved, asked)
    brain.record("eva", "job", f"Місячний аудит Second Brain: у кошик {len(moved)}, на твій дозвіл {len(asked)}",
                 {"moved": moved, "asked": asked}, [note])
    return {"status": "ok", "notes": plan["notes"], "moved": len(moved), "asked": len(asked), "report": note}


def _report(root: Any, plan: Dict[str, Any], moved: List[str], asked: List[Dict[str, Any]]) -> str:
    stamp = datetime.now().strftime("%Y-%m-%d")
    folder = root.joinpath(*REPORT_DIR)
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"Аудит_{stamp}.md"
    counter = 1
    while target.exists():
        counter += 1
        target = folder / f"Аудит_{stamp}_{counter}.md"
    lines = ["---", "тип: аудит_єви", f"date: {stamp}", "tags: [єва, аудит, second-brain]", "---", "",
             f"# Аудит Second Brain, {stamp}", "",
             f"Нотаток: {plan['notes']}; з твоєю міткою: {plan['protected']}. Нічого не видалено: прибране лежить у "
             "`_Кошик_агентів`, кошик очищаєш ти.", "", f"## У кошик ({len(moved)})", ""]
    lines += [f"- {rel}" for rel in moved] or ["- нічого"]
    lines += ["", f"## Чекає твого слова ({len(asked)})", ""]
    for item in asked:
        why = "; ".join(item["because"][:3])
        lines.append(f"- {item['kind']}: {', '.join(f'[[{p}]]' for p in item['paths'][:4])} — {item['proposal']}"
                     + (f" ({why})" if why else ""))
    if not asked:
        lines.append("- нічого")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target.relative_to(root).as_posix()


async def run_job(gateway: Any) -> Dict[str, Any]:
    import asyncio

    from src.obsidian_notes import vault_dir_from_env

    root = vault_dir_from_env()
    if root is None:
        return {"status": "unavailable", "reason": "vault_not_mounted"}
    result = await asyncio.to_thread(run, root)
    owner = await gateway.owner_user_id() if gateway else None
    if owner:
        await gateway.send("eva", owner, f"Місячний аудит Second Brain: у кошик агентів {result['moved']} "
                                         f"(нічого не видалено), на твій дозвіл {result['asked']}. Звіт: {result['report']}")
    return result
