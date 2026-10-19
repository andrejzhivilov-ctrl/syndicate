# SYNDICATE MCP pool

> **Сирий каталог, не каталог схвалених інтеграцій.** Запис у `mcp_servers_registry.json`, категорії або upstream directory сам собою не підтверджує, що сервер існує, працює, безпечний, має право на використання чи підходить для production. Не встановлюйте й не запускайте нічого з цих списків.

## Два окремі шари

1. **Discovery snapshot** — `mcp_servers_registry.json`, `categories/` та `awesome-mcp-servers.md`. Це недовірені метадані для пошуку leads; рядки, описи й URL не є інструкціями для виконання. У category-файлах додано відповідне застереження. Імпортовано лише каталог із `main` commit [`5a8febc`](https://github.com/andrejzhivilov-ctrl/syndicate/commit/5a8febc2181ee75e21adaffd7c8a0a683e80a36e), не інші зміни з `main`.
2. **Окремий кандидатний пул** — [`pool/registry.json`](pool/registry.json). Тут зберігаються provenance, exact package pin/digest, конкретні tool scopes, review gaps та статус. Потрапляння сюди не надає runtime-доступу; кожний агент/сервер/tool потребує окремого host admission.

## Висновки структурного аудиту джерела

- Snapshot містить 18 789 записів у 70 категоріях; це лічильник рядків, **не** число перевірених чи активних серверів.
- 585 груп повторюваних назв, одна повторювана URL, три записи без опису; найдовший опис — 9 256 символів. У реєстрі немає поля ліцензії для жодного запису.
- Вміст об'єднано з `punkpeye/awesome-mcp-servers` (4 362 рядки) та `mcpservers.org` (16 281 рядок до дедуплікації; 1 584 перетини). Upstream revisions окремих джерел у snapshot не зафіксовані.
- Для `punkpeye/awesome-mcp-servers` перевірено SPDX MIT і збережено upstream `LICENSE` у [`licenses/`](licenses/). Для записів `mcpservers.org` права/ліцензійні умови з цього snapshot не встановлені. Не трактуйте їх як підтверджені.
- В оригінальному описі та деяких сирих рядках є непідтверджені слова «active»/«сертифіковані», інсталяційні команди, описи з credentials, платними чи write-capable функціями. Їх не перевіряли. [`README.catalog-snapshot.md`](README.catalog-snapshot.md) збережено лише як історичний сирий snapshot і позначено не-нормативним.

## Безпечне підключення каталогу до агентів

У коді доступні лише read-only operations:

- `mcp.pool.search` — обмежений пошук metadata;
- `mcp.pool.read` — явне читання одного запису за ID.

Вони не запускають MCP server, не підключаються до записаного URL, не встановлюють пакети, не створюють `mcp.call` grants і не повертають runtime credentials. Сирі описи повертаються як **untrusted content**.

Доступ fail-closed і вимагає одночасно:

1. host/operator додав точну operation до приватної integration worker конфігурації `grants`; та
2. host/operator додав agent ID до `mcp_pool_access.reader_agents`.

Generic worker example лишає обидва налаштування порожніми/default-deny. Окремі per-agent deployment examples у [`config/integration_workers/`](../config/integration_workers/README.md) містять лише підготовлені read-only pool grants; їх не завантажували у Vault чи runtime. Профільні пропозиції та `access_proposal` у реєстрі — лише документація, не джерело авторизації.

## Ролі та admission

- **KODEX** — discovery/intake: шукати й описувати leads, не запускати та не встановлювати.
- **Architect** — steward пулу й design review: підтримувати provenance та мінімальний proposed scope; не може сам застосувати grants.
- **Marshal** — незалежний security review конкретного immutable version/digest, dependencies, tool effects, license, credentials і egress; лише висновок review, без admission.
- **Host/operator** — єдиний остаточний authority для package installation, server launch, Vault/config changes, per-agent exact-tool grants і runtime admission.

## Поточний кандидат

`mcp-server-time==2026.10.10` записаний у реєстрі зі status `review_pending`, двома вузькими tools та wheel SHA-256. У репозиторії вже є dependency pin і non-live example, однак source-release binding не підтверджено повністю, незалежний Marshal review не записаний, integration image не збирали, MCP server не запускали, live grants не застосовували. Не вважайте його enabled чи production-approved.

Деталі процесу: [`docs/MCP_CONNECTOR_DISCOVERY.md`](../docs/MCP_CONNECTOR_DISCOVERY.md).