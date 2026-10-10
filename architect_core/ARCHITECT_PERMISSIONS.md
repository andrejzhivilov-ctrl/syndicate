# Architect — дозволи на розгортання (завтра)

**Чинні права в профілі (Андрій, 2026-10-10):**
`n8n.workflow.design`, `n8n.workflow.mount` на scope `n8n/live`.
`n8n.workflow.activate` **не** видана. n8n не control plane і не джерело прав.
Секрети лише з env `N8N_BASE_URL` / `N8N_API_KEY`, не з JSON профілю.

## Дозволено (після HITL Андрія)

| Дія | Код | Умова |
|---|---|---|
| Взяти задачу | `architect_accepts_task` | лише `andrii` |
| Показати схему n8n | `architect_preview.build_preview` | mermaid, без API |
| FlowLint | `flowlint.lint_workflow` | локально |
| Живий монтаж inactive | `mount_inactive_workflow` | HITL + env; `active=false` |
| Здати після «так» | `deliver_after_confirm` | lint → mount inactive |
| Звіт Єві | `architect_report` | лише payload |
| Скіли draft | `architect_core/skills/` | не Hermes install |

## Заборонено без нового точного id

| Дія | Як закрито |
|---|---|
| Activate / увімкнути workflow | `n8n.workflow.activate` не видана |
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
