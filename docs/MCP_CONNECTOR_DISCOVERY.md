# MCP-конектори: пошук, незалежний review та контрольоване підключення

**Статус:** локальний discovery-каталог і окремий candidate pool підготовлені; додано read-only `mcp.pool.search`/`mcp.pool.read` wiring. Generic worker example лишається default-deny; окремі per-agent templates для KODEX/Architect/Marshal підготовлені, але не завантажені у Vault чи runtime. Профілі лишаються `prepared_not_enabled`. Один utility package pin і non-live приклад існують, але image не збирали, MCP server не запускали, live grants і credentials не змінювали.
**Рішення:** сирий каталог зберігається окремо від curated candidates; один host-owned MCP client, exact per-agent tool allowlists, окремі review/admission stages. Каталог не встановлює й не запускає server-и та не надає grants. SaaS акаунти й live підключення не активовано.
**Огляд екосистеми:** 2026-10-18.

## Що вже є у SYNDICATE

- `src/integrations/stdio_mcp.py` використовує офіційний Python MCP SDK (`ClientSession`, `StdioServerParameters`, `stdio_client`) для stdio-транспорту. Є обмеження на аргументи, результат і час виконання; stderr процесу не потрапляє до журналу.
- `src/integrations/service_hub.py` має окремі `mcp.list` і `mcp.call` для вже налаштованих серверів. Нові `mcp.pool.search`/`mcp.pool.read` читають лише pinned catalog/candidate metadata; вони не підключаються до серверів і не створюють `mcp.call` grants.
- `mcp_servers/` містить сирий snapshot `origin/main` commit `5a8febc2181ee75e21adaffd7c8a0a683e80a36e` та окремий `mcp_servers/pool/registry.json`. Дані каталогу hash-verified, описів не вважають інструкціями, а candidate status не є approval.
- Pool доступний лише коли host одночасно видає точну operation grant і додає agent ID до приватного `mcp_pool_access.reader_agents`. Generic example має порожні grants/allowlists; окремі KODEX/Architect/Marshal worker templates — self-only, read-only, `prepared_not_applied` і не завантажені у Vault. Профілі лишаються `prepared_not_enabled`.
- `config/integration_mcp.example.json` — лише приклад конфігурації. Відсутність активних grants і host-конфігурації означає, що ці приклади не створюють підключень.
- Поточний adapter — stdio, не універсальний транспорт для довільних URL. Для майбутнього HTTP/Streamable HTTP потрібен окремий host-allowlisted adapter і auth review.
- Існуючий `mcp.call` tool-name allowlist сам по собі не класифікує ризик конкретного tool. Перед допуском будь-якого write/send/delete tool потрібен host-side mapping кожного MCP tool до `ActionClass` і перевірка AgentPolicy/HITL. До цього дозволяти лише інструменти, які незалежно підтверджено як read-only.

Отже, базовий **універсальний stdio-клієнт уже є**. Не потрібен один мегасервер з усіма доступами. Потрібен контрольований каталог кандидатів і per-agent конфігурація точних tools/scopes.

## Третій MCP-пул: каталог і контрольований read-only доступ

- Сирий каталог: [`mcp_servers/`](../mcp_servers/README.md), 18 789 discovery records у 70 категоріях. Це не library дозволених connectors. Structural audit: 585 груп дублікатів назв, одна повторювана URL, 3 записи без опису, 0 license fields; джерельний `mcpservers.org` subset не має підтверджених redistribution terms у snapshot. Category headers виправлено, а історичний README збережено окремо й позначено non-normative.
- Curated registry: [`mcp_servers/pool/registry.json`](../mcp_servers/pool/registry.json). Зараз у ньому лише `mcp-server-time` зі status `review_pending`, pinned package artifact hash, двома вузькими tool proposals і явними review gaps. Жоден catalog row не переходить сюди автоматично.
- `MCPServerPool` у `src/agent_platform/mcp_server_pool.py` робить тільки local hash-verified search/read, bound-ить output, прибирає query/fragment з URL та redacts token-like values у descriptions. Не має HTTP, subprocess, package manager чи MCP SDK calls.
- Ролі: Architect — curator/steward і design review; KODEX — discovery/intake; Marshal — незалежний security review; host/operator — остаточне встановлення та grant/admission. Жоден агент не може сам змінювати grants.
- Read-only deployment templates: [`config/integration_workers/`](../config/integration_workers/README.md) дає KODEX/Marshal review-only knowledge grants та per-agent MCP-pool search/read, Architect — лише MCP-pool search/read. Generic `config/integration_worker.example.json` зберігає порожні pool grants/allowlists. Templates не завантажені у Vault/runtime; профілі й grant plans залишаються `proposed_not_applied`. Для фактичного worker доступу потрібні operation grants та відповідний self-only allowlist. Немає `mcp.pool.install`, `mcp.pool.call` чи permission-expansion operation.
- Dockerfile копіює лише machine-readable discovery registry та curated pool registry для майбутнього integration image; image не збирали й контейнер не запускали.

## Вузький вибір цього запиту

| Кандидат | Рішення | Підстава / межі |
|---|---|---|
| [`mcp-server-time`](https://github.com/modelcontextprotocol/servers/tree/main/src/time) `2026.10.10`, MIT | Додано точний pin у `deploy/requirements-integrations.txt` і лише два tools (`get_current_time`, `convert_time`) до прикладу `config/integration_mcp.example.json`. Це локальний IANA timezone utility без credentials або мережевих запитів. | Офіційний reference server, позначений upstream як Beta; він потребує MCP SDK 1.x (наявний pin `mcp==1.30.0` сумісний). `convert_time` приймає лише HH:MM і використовує поточну дату source timezone, тому не слід вважати його date-aware для майбутніх подій/DST. Image не збирали, package import перевіряється тільки в тимчасовому venv, server не запускали й grants не додавали. |
| [`mcp-server-git`](https://github.com/modelcontextprotocol/servers/tree/main/src/git) | Відкладено. | Хоча read tools можна allowlist-ити окремо, server також має `git_add`, `git_commit`, `git_reset`, `git_checkout` і `git_create_branch`; для запуску потрібні системний `git` та чіткий read-only repo mount. Жоден mount не погоджений/не доданий, тому package не встановлюється. |
| [`mcp-server-fetch`](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) | Не обрано зараз. | Загальний fetch збільшує egress/SSRF та передачу даних; поточний stdio adapter не є мережевим host allowlist. |
| [`mcpm.sh`](https://github.com/pathintegral-institute/mcpm.sh) та community registry/manager tools | Лише пошукові кандидати; не встановлювали. | Manager може завантажувати/запускати довільні server-и та редагувати client configs; це не потрібне для вже наявного host-owned MCP client. |
| SaaS connectors (Google/Slack/інші) | Не додавали. | Потребують вибраного сервісу, user-owned account scope та credentials; жодні токени/підключення для цього не використовувалися. |

Додавання utility pin і прикладу — **не підключення**: `config/integration_mcp.example.json` сам по собі не завантажується як live-конфіг. Перед майбутнім image build/runtime smoke потрібен окремий operator step; grants лишаються відсутніми.

## Де шукати конектори

| Джерело | Призначення | Як використовувати |
|---|---|---|
| [Офіційний MCP Registry](https://github.com/modelcontextprotocol/registry) | Публікувані записи про MCP-сервери — каталог на кшталт app store. README репозиторію описує API та publisher. | Початковий пошук і provenance. Запис у каталозі — не security certification і не дозвіл на запуск. Доступ до live API `registry.modelcontextprotocol.io` потребуватиме окремо дозволеного egress; у цій роботі API не викликався. |
| [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | Великий, активно оновлюваний community directory. | Лише пошук leads. Перевіряти кожен upstream, license, підтримку, пакет і права окремо; кількість зірок не є доказом безпеки. |
| [Офіційні reference servers](https://github.com/modelcontextprotocol/servers) | Невеликий набір демонстрацій MCP/SDK. | Протокольний приклад або тестова fixture, не автоматично production connector: README прямо застерігає, що це reference implementations. Старі інтеграції можуть бути archived або передані іншим maintainers. |
| [Офіційний Python SDK](https://github.com/modelcontextprotocol/python-sdk) | Клієнт і сервер MCP для Python. | Вже використовується в `stdio_mcp.py`; спершу продовжувати цей SDK, не дублювати протокол власною реалізацією. |
| [FastMCP](https://github.com/PrefectHQ/fastmcp) | Python framework для побудови MCP server/client. | Можливий інструмент, якщо з'явиться потреба писати власний server; не є універсальною бібліотекою готових інтеграцій і зараз не потрібен. |
| [Composio](https://github.com/ComposioHQ/composio) | Широкий каталог toolkits і hosted MCP sessions; README описує 1000+ integrations та `COMPOSIO_API_KEY`. | Окрема vendor-hosted альтернатива, не локальний нейтральний каталог. Потребуватиме оцінки передачі даних, account scopes, зберігання credentials, умов/вартості й vendor dependency; не підключати за замовчуванням. |

## Ролі та життєвий цикл кандидата

1. **KODEX — discovery only.** Якщо operator надасть окремий read-only grant — шукає через `mcp.pool.search/read`, вважаючи raw записи untrusted. Потім перевіряє upstream evidence лише дозволеними джерелами/tools. Повертає candidate та відкриті питання; не запускає package manager, код, Docker image чи MCP server.
2. **Architect — design review.** Перекладає потребу на мінімальний transport, tools, account scope, resource scope, egress і policy gates. Пропонує per-agent набір; не змінює host/Vault/runtime конфігурацію.
3. **Marshal — незалежна перевірка.** Самостійно перевіряє зафіксований upstream commit/version, license, підтримку, залежності, tool schemas та side effects, secrets/logging, мережевий egress і тести. Не покладається на KODEX-ове `safe` або `approved` як доказ і не надає grants.
4. **EVA — координація рішення; оператор — дозвіл.** EVA може підсумувати trade-offs. Лише оператор окремо санкціонує ізольований тест, секрети/акаунт, конкретний grant та будь-яку активацію.
5. **Host інтеграція.** Host pin-ить конкретний package/version або image digest, команду/args і transport; secrets задаються лише як Vault references. Для кожного агента окремо задаються server, exact tool names, resource scopes, egress і клас дії. Тестовий grant не переноситься до інших агентів.

Рекомендовані status значення для proposal metadata: `discovered_only` → `proposed_not_applied` → `review_pending` → `approved_for_isolated_test` → `enabled_by_operator`; альтернативний фінал — `rejected`/`quarantined`. Перехід до наступного статусу робить host/operator, не агент. У цій сесії жоден кандидат не переводиться до `approved_for_isolated_test`.

## Формат звіту KODEX

```json
{
  "connector_id": "vendor-service-read",
  "service": "назва сервісу",
  "upstream_url": "https://github.com/vendor/project",
  "upstream_commit": "40-символьний commit SHA",
  "package_or_image": "точна назва",
  "version_or_digest": "закріплена версія/digest або unknown",
  "transport": "stdio",
  "license": "SPDX ID або unknown",
  "maintainer_and_last_release": "посилання та дата",
  "tools": [
    {"name": "list_records", "effect": "read", "resource_scope": "account/repository"}
  ],
  "credential_scopes": ["мінімальні scopes; значень секретів не записувати"],
  "network_hosts": ["точні очікувані hostnames"],
  "data_sent_and_received": ["опис класів даних"],
  "side_effects": [],
  "dependencies_and_install_method": "версії та спосіб фіксації",
  "security_evidence": ["конкретні посилання на code/docs/tests/advisories"],
  "known_gaps": [],
  "status": "discovered_only"
}
```

Невідомі поля лишати `unknown`, не вгадувати за назвою чи marketing description. Не записувати токени, passwords, private URLs або дані користувача у звіт.

## Admission gates — обов'язкові

- Перевага upstream від виробника сервісу або чітко визначеного maintainer; перевірити репозиторій, immutable commit/tag, release history, license/SPDX і dependency provenance. Community list — лише lead.
- Під час discovery не запускати `npx -y`, `uvx`, install scripts, Docker pull чи невідомий MCP server. Після незалежного source/license/dependency review оператор може виконати тільки ізольоване package-install із точним pin; agent не запускає package manager самостійно. Не ставити `latest`; окремо санкціоновані build, запуск server-а, Vault credentials і grants не випливають із package pin.
- MCP server, tool descriptions, schemas, result text і документи — untrusted input. Prompt injection/tool poisoning не змінює інструкції SYNDICATE, роль, grants або allowlist.
- Відхиляти wildcard/tool discovery, agent-supplied commands/URLs/env, server-и з неясним власником, невідомою ліцензією, прихованим egress або неописаним зберіганням даних. Stars/downloads не компенсують відсутні докази.
- Read/write/delete/send — окремі tools і окремі grants. Read-only — дефолт. Публікація, зовнішнє повідомлення, фінансова дія, destructive operation, service connection і resource expansion потребують host policy та людського дозволу відповідно до `ActionClass`.
- Secrets — лише host-managed Vault references; ніколи не передавати секретний value агенту для написання manifest, у prompt, stderr, audit або Git. Обмежити мережевий egress на рівні worker/container, а не тільки документацією.
- Задати timeout, input/output limits, content-type/schema validation і safe error handling. Audit зберігає agent/server/tool/version/status та request correlation ID, але не секрети чи повний приватний payload.
- Увімкнути лише мінімально необхідні server/tools для визначеного агента. Наявність MCP connection не робить усі tools доступними всім агентам.

## Негайна рекомендація

1. Залишити поточний офіційний Python client як універсальну основу для **локальних stdio** server-ів.
2. Дозволити KODEX готувати тільки discovery reports за окремо доступними read-only джерелами; додати незалежний Marshal review і Architect mapping.
3. Першу сервісну інтеграцію вибирати лише після списку конкретних потреб Андрія. Для кожної — окремий pinned server, test plan, tool/action map і exact per-agent allowlist.
4. Streamable HTTP, Composio, OAuth, нові зовнішні акаунти, live Vault/config, сервери й grants залишити поза поточним етапом без окремого погодження.
