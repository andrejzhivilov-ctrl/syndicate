# Sam — дозволи (підготовка до викладки, 2026-10-10)

**Чинні права в профілі:** порожні `capabilities` / `resource_scopes` / `services_enabled`. Нічого нижче не є grant.

| Елемент | Стан у коді | Стан у профілі | Потрібен окремий дозвіл Андрія |
|---|---|---|---|
| Прийом задач | `sam_accepts_task` (лише Андрій) | `task_source=andrii_only` | ні (вже так) |
| Confluence / HITL | `ConfluenceEngine`, `decide_execution` | `hitl_only` | ні |
| Брокерський міст | `submit_lot` → `broker_unavailable` | `broker=tbd` | так (вибір + конектор) |
| Demo-торгівля | перемикач `broker_demo` (закритий) | `broker_demo=false` | так |
| Live-торгівля | `broker_live` (закритий) | `broker_live=false` | так, окремо |
| Auto FX/crypto ≥99 | тільки з `trade.execute` + switch | `auto_fx_crypto=false` | так (flip + HITL + grant) |
| Auto інвестиції | `sam_auto_invest_allowed()` == False | `auto_invest=false` | **не існує** |
| Вендоровані скіли (8) | код у `sam_core/vendor/`, тести пройдено | `vendored_inactive` | так (ввімкнення в Hermes) |
| Мережа скілів | FMP-адаптер видалено; COT лише download | — | так (додати хост в allowlist) |
| Telegram / voice / cockpit | вимкнено | `false` | так |
| Drive / Obsidian / NotebookLM | не підключено | `not_configured` | так |
| Social listen | вимкнено | `false` | так (observe-only) |
| n8n | `control_plane=false`, `permission_source=false` | `not_enabled` | так (окремий HITL-дизайн) |
| Hermes start / install | не запущено | — | так |

## Заборонено без окремого рішення
- `trade.execute`, `broker_demo`, `broker_live`, `auto_fx_crypto` як true.
- Брокерські SDK / ключі / `order_send` / `place_order` у коді Сема.
- Постинг у соцмережах.
- Зміна `floor`, `NEVER_AUTO_ACT`, HITL-шляхів.

## Дозволено зараз (без capability)
- Прийом задач від Андрія, порахунок confluence, HITL-рішення, payload для Єви.
- Читання і тестування вендорених скілів локально (без мережі).
