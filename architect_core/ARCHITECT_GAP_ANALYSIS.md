# Архітектор — gap analysis (фаза контракту)

**Дата:** 2026-10-09
**Статус:** аналітичний звіт, не дозвіл і не активація.
**Мета:** зафіксувати розрив між історичними специфікаціями/кодом Архітектора та чинною платформою SYNDICATE. Конкретні права, роль, модель і інтеграції **ще не визначені** й тут не призначаються.

## 1. Що вже є в платформі (не live)

- Нейтральний control plane: `AgentProfile`, immutable `AgentRegistry`, fail-closed `AgentPolicy`, `AgentDispatcher` у `src/agent_platform/`.
- Новий профіль починається без capability та resource grants; wildcard заборонений.
- n8n у цільовій схемі — виконавець workflow, не control plane і не джерело дозволів.
- Єва має `config/agents/eva.profile.json` зі статусом `prepared_not_enabled` і порожніми grants.
- Hermes, n8n production, LangGraph↔Dispatcher bridge і сервісні адаптери **не підключені**.

`config/agents/` до цієї фази містив лише профіль Єви. Окремого platform-маніфесту Архітектора не було.

## 2. Історичні джерела (не чинні grants)

Ці файли описують **задум минулих ітерацій**. Вони не є джерелом активної ролі, моделі, доступів чи інтеграцій.

| Джерело | Що стверджує | Чинний статус |
|---|---|---|
| `architect_core/ARCHITECT_CTO_SPEC.md` | CTO 24/7, GitHub write, Telegram-бот, Gemini+Claude, Shadow Staging, auto-rollback, FinOps restart, R&D-радар, Trivy, C4 | історична специфікація |
| `architect_core/ARCHITECT_N8N_SPEC.md` | On-demand інженер, Claude 3.5 Sonnet, Blueprint 3-в-1 у Telegram, 7-кроковий монтаж, активація через Єву, watchdog Маршала | історична специфікація; суперечить CTO-спеці (24/7 vs сон/0 токенів) |
| `INTEGRATIONS_AND_CAPABILITIES.md` | «Архітектор (CTO / N8N-інженер)» як розширена можливість | історичний опис; не platform grant |
| `src/agents/architect/` | LangGraph-агент з діями design/lint/gitops/codegen/UI scaffold | історична реалізація, не Hermes-профіль |
| `docs/patterns/golden_*.json` | шаблони з Telegram/`ArchitectBot` | артефакти коду; `active: false`; live n8n немає |

Дві історичні специфікації **суперечать одна одній** (модель, режим роботи, канал, обсяг автономії). Жодну не можна вважати погодженою роллю.

## 3. Розриви

### 3.1 Роль і ідентичність

- Платформа навмисно не зберігає `role` у `AgentProfile`.
- Історичний код називає агента «Chief Infrastructure Architect & CTO».
- Погодженої persona/prompt для Hermes немає.
- Модель не вибрана. Згадки Claude/Gemini у специфікаціях — не рішення.

### 3.2 Control plane vs історичний оркестратор

- Новий `AgentDispatcher` **не** маршрутизує Архітектора.
- `src/orchestrator.py` уже має task types (`design_workflow`, `gitops_sync`, `self_healing_generate`, …) і handler `ArchitectAgent`.
- Це означає: історичний шлях існує **поза** fail-closed platform policy. Наявність handler ≠ надані capability.

### 3.3 Capability / scope / секрети

- Platform-профілю Архітектора досі не було; отже grants = відсутні.
- Історичний Vault-мап `src/vault_paths.py` містить `architect: ("mcp",)` — це least-privilege чернетка **старого** runtime-процесу, не `services_enabled` нового профілю.
- `n8n_builder` посилається на `$env.ARCHITECT_ALERT_CHAT_ID`, `$env.N8N_TELEGRAM_CRED_ID`, `ArchitectBot`. Це шаблонні імена, не підключений бот і не дозвіл на Telegram.
- `generate_ui_scaffold` жорстко прописує `localhost:8001–8006` — це не чинний API SYNDICATE і не preview-контракт.

### 3.4 n8n

Задекларовано / є в коді:

- генерація JSON (core nodes), FlowLint, `active=false`;
- Markdown Change Request і fail-closed `gitops_sync` (bundle лише після `applied` CR і точного fingerprint);
- golden templates і Floor-1 шаблони в `src/n8n_templates.py`.

Немає:

- live n8n API, credentials, staging/production workspace;
- права читати/писати/активувати workflow від імені профілю;
- дозволу вважати n8n джерелом policy;
- workflow Єви `EVA-NIGHTLY-ARCHIVE` (лишається `pending_n8n_workflow`);
- тіньового staging, auto-rollback, drift проти живого n8n (drift приймає `live_workflows` з payload, не з API).

### 3.5 Те, що архітектура SYNDICATE прямо виключає або відкладає

- Sentinel — виключений; історичні тексти згадують сканування Маршалом/Falco.
- Council — не вмикати.
- Hermes — не встановлювати й не запускати без окремого дозволу.
- Production deployment, Docker/host control, `docker.sock` — поза цією фазою.
- Геолокація — default-deny.
- Агенти не призначають задач одне одному без прямого прохання користувача.
- Модель/prompt/payload не можуть самі видати права.

### 3.6 Документи готовності

`eva_core/EVA_DEPLOYMENT_READINESS.md` називає Архітектора «окремою наступною фазою для n8n». Це порядок робіт, не grant. До цієї фази не було:

- `config/agents/architect.profile.json`;
- меж ролі, які б **не** копіювали CTO-специфікацію;
- мінімального workflow-контракту, узгодженого з `AgentPolicy`.

## 4. Що ця фаза свідомо не робить

- Не активує профіль і не запускає Hermes/n8n/workflow.
- Не призначає роль CTO, модель, Telegram, GitHub, MCP, Docker чи host control.
- Не додає capability/resource_scope/services_enabled.
- Не змінює `apps/`, production compose і не підключає Dispatcher до LangGraph.
- Не трактує зелений `tools/check.sh` як готовність runtime.

## 5. Відкриті рішення (потрібне окреме схвалення)

Поки Андрій не затвердить точний scope, залишається лише default-deny маніфест і контракт. Кандидати на пізніше обговорення — **не** запропоновані grants:

1. Чи потрібен окремий Hermes-профіль `architect` зараз, чи лише контракт?
2. Яка вузька функція (якщо взагалі) дозволена: тільки чернетка JSON, тільки lint, нічого?
3. Чи лишати історичний LangGraph-handler, чи ізолювати його, доки Dispatcher не стане єдиним входом?
4. Що робити зі старим Vault-рядком `architect → mcp`.
5. Чи потрібен окремий workflow для нічного аналізу Єви, і хто його **проєктує**, не активуючи.

Наступні файли цієї фази:

- `ARCHITECT_ROLE_BOUNDARIES.md` — межі без призначення ролі;
- `ARCHITECT_WORKFLOW_CONTRACT.md` — мінімальний n8n-контракт;
- `config/agents/architect.profile.json` — `prepared_not_enabled`, порожні grants.
