# Політика пам’яті Sam v0.2

**Namespace:** `agents/sam` (зарезервований).
**Статус:** `memory.read` / `memory.write` як Hermes-grants не видані.
Історичний `TradeJournal` у Postgres — окремий runtime-код, не grant профілю.

**Корпус:** `sam_core/knowledge/quant/SOURCES.yaml` — `sources: []`.
**Джерела (слоти, не підключені):** Google Drive, Obsidian, NotebookLM, extra_connectors=[].

## Архів лотів

Сортування обов’язкове: день → місяць → venue (demo/live) → symbol → direction.
Не змішувати демо-fills з live.

## Правила

- У пам’ять (коли з’явиться grant): сигнали, HITL, outcomes, negative constraints — з датою, без секретів.
- Не класти ключі брокера, токени бота, сирі виписки.
- `[ANDRII_IMMUTABLE]` — лише читання.
- Єва не читає `agents/sam`. Сем не читає `agents/eva`.
- Історичні ціни в пам’яті ≠ живий ринок.
