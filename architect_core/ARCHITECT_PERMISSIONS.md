# Architect — дозволи на розгортання (завтра)

**Чинні права в профілі:** порожні `capabilities` / `resource_scopes` / `services_enabled`.
Це **і є** дозвіл на викладку: профіль їде вимкненим і fail-closed. Не copypaste CTO-спеки в grants.

## Дозволено завтра (хост-код, без capability)

| Дія | Код | Умова |
|---|---|---|
| Взяти задачу | `architect_accepts_task` | лише `andrii` |
| Показати схему n8n | `architect_preview.build_preview` | JSON `active=false`, без n8n API |
| FlowLint | `flowlint.lint_workflow` | локально |
| Blueprint HITL | `architect_blueprint` | не Telegram send |
| Здати після «так» | `deliver_after_confirm` | inactive JSON + lint |
| Звіт Єві | `architect_report` | лише payload |
| Скіли draft | `architect_core/skills/` | не Hermes install |

## Заборонено без нового точного id

| Дія | Як закрито |
|---|---|
| Live n8n import/activate | `n8n.live_api=false`, `architect_n8n_live_allowed()→false` |
| GitOps push / PR | `gitops_push=false`; `gitops_sync` готує bundle, **не** пушить |
| Telegram `@architect_infra_bot` | `telegram_bot=false` |
| Host / Docker / rollback | `host_control=false` |
| Memory R/W | немає `memory.read`/`write` |
| Єва ставить задачу | `eva_can_assign=false` |
| Модель / Hermes live | `model_status=not_selected` |

## Що означає «завершений» для завтра

Профіль можна класти в git і на сервер як `prepared_not_enabled`.
`python tools/architect_ready.py` → `deployable_as_prepared_profile: true`, `grants_empty: true`.
Це не live CTO і не увімкнений n8n.
