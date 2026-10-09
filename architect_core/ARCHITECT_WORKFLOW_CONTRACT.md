# Мінімальний n8n workflow-контракт (Архітектор)

**Статус:** контракт підготовки. Жоден workflow не створюється в n8n і не активується цим документом.
**Пов’язані:** `config/agents/architect.profile.json`, `eva_core/EVA_N8N_WORKFLOWS.md`.

n8n виконує workflow. n8n **не** є control plane, **не** зберігає policy і **не** може розширити профіль, capability чи resource scope.

## 1. Інваріанти

1. Новий workflow-артефакт має `"active": false`.
2. Секрети не живуть у JSON, expression, code-node, URL, логах, prompt чи profile manifest.
3. Credentials, якщо колись з’являться, вводить Андрій у контрольованій панелі; JSON тримає лише посилання, не значення.
4. Дозволяються лише офіційні core nodes (`n8n-nodes-base.*`). Community packages вимкнені за політикою репозиторію.
5. Заборонені типи (вже в FlowLint): `executeCommand`, `ssh`, legacy `function` / `functionItem`.
6. Webhook-потоки мають ідемпотентність/дедуп; критичні вузли — гілку помилки або оголошений error workflow.
7. Зміна `active`, імпорт у live n8n, публікація credentials, виклик n8n API — `approval_required` / окремий HITL; поточний профіль цього не вміє, бо grants порожні.
8. Request-body прапорець, модель або «Єва попросила» **не** є дозволом.

## 2. Шлях зміни (коли його окремо дозволять)

Це схема майбутнього процесу, не реалізований live pipeline:

```text
чернетка JSON (active=false)
        │
        ▼
FlowLint (локально)
        │
        ▼
Change Request (pending)
        │
        ▼
Андрій: review → apply
        │
        ▼
git bundle лишається inactive
        │
        ▼
окрема ручна активація в n8n — лише після ще одного явного дозволу
```

Історичний `ArchitectAgent.design_workflow` / `gitops_sync` уже наближений до цього на рівні **коду пропозицій**. Це не дає профілю права викликати n8n.

## 3. Що контракт свідомо не покриває

- Live n8n URL, API-ключ, webhook production.
- Telegram `@architect_infra_bot`, ArchitectBot credentials.
- Vault JWT bridge як працюючий сервіс.
- Shadow staging / dark launch / auto-rollback.
- Активацію `EVA-NIGHTLY-ARCHIVE` (03:00 `Europe/Kyiv`) — це окремий чернетковий контракт Єви; source provider досі `not_configured`.
- Призначення задач іншим агентам з workflow.
- Читання чужих memory namespace.

Golden templates у `docs/patterns/` і генератор `src/agents/architect/n8n_builder.py` — зразки форми. Вони не імпортовані в n8n.

## 4. Мінімальний JSON-скелет чернетки

Будь-яка майбутня чернетка має щонайменше:

```json
{
  "name": "example-draft",
  "active": false,
  "nodes": [],
  "connections": {},
  "settings": {},
  "tags": ["syndicate-draft", "inactive"]
}
```

Ім’я, вузли й розклад **не** затверджені цим контрактом. Порожній скелет не є робочим workflow.

## 5. Зв’язок із профілем

Поля маніфеста:

- `n8n.control_plane` = `false`
- `n8n.permission_source` = `false`
- `n8n.activation` = `not_enabled`
- `n8n.live_api` = `false`
- `live_modes.n8n_editor` = `false`

Поки вони такі, навіть валідний lint-clean JSON залишається файлом у git, не автоматизацією.
