# СИНДИКАТ — системний паспорт

- **Зріз стану:** 2026-10-16
- **Мова:** українська
- **Репозиторій:** `andrejzhivilov-ctrl/syndicate`
- **Призначення:** оновлювана Markdown-основа та PDF-знімок коду, профілів і підготовлених інтеграцій.
- **Важливо:** це не звіт про стан production-сервера. Сервер, Compose, Vault, n8n, зовнішні API та облікові записи під час підготовки цього документа не запускалися й не перевірялися наживо.

PDF генерується з цього файла: `python tools/md_to_pdf.py docs/SYSTEM_PASSPORT_2026-10-16.md`. Наступний знімок створюйте окремим датованим файлом; попередній `docs/SYSTEM_PASSPORT.md` залишено без перезапису.

## 1. Короткий висновок

SYNDICATE — кодова платформа для координації персональних і бізнес-агентів, окремих domain workers, знань, безпекових перевірок та майбутніх інтеграцій. У репозиторії є оркестрація LangGraph, профілі агентів, локальні Python-обробники, правила доступу, Compose-опис сервісів, кілька підготовлених worker overlays і генератори n8n-шаблонів.

Стан профілів на дату зрізу:

- У `config/agents/` є **12 агентських профілів**: Alice, Architect, Doc, Eva, Fin, Jack, Kira, KODEX, Marshal, Oscar, Sam і Tyler.
- Усі 12 мають `activation: prepared_not_enabled`. Це означає, що профіль підготовлений, але його значення не є доказом запущеного агента, виданих live-доступів або готового зовнішнього сервісу.
- Для деяких профілів поле `capabilities` містить декларації на майбутнє/для policy-перевірок. Їх слід читати разом зі статусом активації, ресурсними scope, кодом dispatcher, операторськими allowlist і фактичним runtime. Не вважати сам запис у JSON підтвердженням, що інтеграція працює.
- `model_status` — `not_selected` у профілях. Успішні локальні тести не є перевіркою provider API, ціни, квоти чи модельного результату.
- A/B-модель розгортання лишається відкритою: один основний `eva-agent` чи майбутні окремі Hermes-контейнери. У репозиторії є базовий Compose і окремі підготовлені overlays, але жоден з них у цій роботі не запускався.

Перевірки коду, зафіксовані в робочому середовищі: `EVA_SKIP_PGSERVER=1 bash tools/check.sh` завершився успішно; набір pytest — **885 passed, 35 skipped**. Живу PostgreSQL було пропущено; це не підтверджує deployment, n8n, Vault або зовнішні API.

## 2. Як читати статуси

| Позначення | Значення у цьому документі |
|---|---|
| **Код реалізовано** | У репозиторії є відповідна логіка; це не означає, що процес запущений або провайдер підключений. |
| **Локально перевірено** | Є unit/contract tests або безмережевий smoke test; production-стан цим не підтверджується. |
| **Підготовлено, не активовано** | Профіль, код, Compose overlay, шаблон чи policy присутні, але live-активації не робили. |
| **Default-off** | Прапорець, allowlist, grant, секрет, канал або runtime gate за замовчуванням вимкнений/відсутній. |
| **Чернетка / не завантажено** | Специфікація, prompt або manifest є, але база знань чи поведінка ще не затверджені/не підключені. |
| **Заплановано** | Роль або ініціатива випливає з рішення Андрія, але профілю/реалізації/дозволу ще немає. |
| **Не перевірено наживо** | Не було запиту до реального сервісу, live-облікового запису, production-хоста чи API. |

Будь-яка згадка сервісу або API нижче означає лише конфігураційне посилання, кодовий адаптер, дизайн чи довідковий URL, якщо окремо не написано інакше. Немає підстав стверджувати поточну доступність сторонньої API, актуальний тариф або право доступу без окремої перевірки.

## 3. Призначення та межі системи

SYNDICATE має обробляти запити Андрія через оркестрацію, виконувати обмежені локальні обчислення/підготовку матеріалів, показувати джерела, формувати пропозиції та зупинятися перед діями, що потребують дозволу. Єва — єдина CEO/координаторка; інші агенти не отримують повноважень від самої назви ролі чи від тексту зовнішнього джерела.

Ключовий потік у коді задуманий так:

```text
запит оператора
    -> LangGraph / маршрутизація
    -> профіль + точний capability/resource scope
    -> policy / allowlist / HITL gate
    -> агент або доменний worker
    -> результат з provenance та явним unavailable/approval_required
    -> обмежений audit
```

Присутність коду не означає, що кожен етап уже зв’язаний у live-системі. Частина старих агентів працює як Python-класи в основному runner; частина новіших директорів має ізольовані FastAPI workers; Alice має окрему підготовлену SDK-архітектуру. Живий Hermes bridge і наскрізний control plane для всіх інструментів залишаються окремим етапом.

### 3.1. Базові правила доступу та приватності

- Джерело профільних прав — `config/agents/*.profile.json`; читабельна похідна матриця формується `tools/export_permissions.py`. Вона не є командою застосувати права до Vault чи сервера.
- Sentinel Protocol — механізм перевірок на межах dispatcher/tools/services; **не окремий агентський профіль**. Власник/відповідальний — Маршал.
- Зовнішня дія, фінанси, торгівля, публікація, видалення, зміна політик/прав, production-запуск та нове підключення не вважаються дозволеними за замовчуванням.
- Telegram призначений лише для Андрія. Порожній allowlist означає **deny all**; наявність handler або назви бота не означає підключення.
- YouTube — тільки офіційний YouTube Data API у погодженому scope. Не завантажувати відео чи аудіо; YouTube Music не є дозволеним інтеграційним шляхом.
- Бажання мати інтернет для оновлення інформації не дорівнює готовому egress-дозволу. Домени, ліміти, мережевий шлях і перевірка доступу для всіх агентів не узгоджені; необмежений egress не налаштовувати.
- Секрети не записувати в Git, prompts, приклади, чат чи логи. Особисті дані мають жити у контрольованих `EVA_DATA_DIR` / `KODEX_DATA_DIR`, не в домашніх каталогах чи checkout репозиторію.
- `andrii_protected` — read-only; зміна або видалення потребують окремого дозволу Андрія. Немічені файлові дії KODEX мають потрапляти до звіту Єві о 21:00, але live-розклад/доставка не підтверджені.
- Журнал повного діалогу не є джерелом цього паспорта; його вміст тут не цитувався й не використовувався.
- Google One не є API credential. Не автоматизувати Google-вхід через cookies/session. Desktop/browser fallback не є дозволом на автоматизацію реального desktop.

## 4. Архітектура та карта сервісів

### 4.1. Підготовлені компоненти репозиторію

| Компонент | Призначення | Репозиторний стан / межа |
|---|---|---|
| `eva-agent` | FastAPI runner (`runtime.agent_runner:app`), LangGraph, частина агентів і services | Описаний у базовому Compose; не запущений у цій роботі. |
| PostgreSQL + pgvector | Системна БД, історія/вектори за схемою репозиторію | Compose/config є; live DB цього зрізу не перевірялась. |
| Redis | Короткостроковий стан/черги за поточним runtime | Compose/config є; live Redis не перевірявся. |
| Vault | Секрети, AppRole та HCL policy | Код і статичні policy є; production Vault не підключався, policy не застосовувалась. |
| Embeddings (BGE-M3) | Локальна embedding-служба; Compose задає 1024-вимірний вектор | Image/config є; модельний сервіс не запускався. |
| n8n | Самостійний workflow runtime, URL через конфігурацію | Compose описує `n8nio/n8n:1.68.0`; workflow/API стан сервера не перевірявся. |
| Whisper | Локальний ASR для окремих погоджених сценаріїв | Образ і конфіг є; не запускали. Це не дозвіл на завантаження соцмережевого аудіо. |
| Nginx | Reverse proxy/TLS edge | Конфігурація/deploy scripts є; сертифікати та сервер не перевірялися. |
| Alice worker | Окремий SDK/FastAPI runtime з workspace gate | `deploy/docker-compose.alice.yml`, Dockerfile та runner підготовлені; default-off, не побудований і не запущений. |
| Oscar/Tyler/Jack workers | Доменні FastAPI workers із розділеними volumes/networks та операторським allowlist | Compose overlay присутній; за замовчуванням доступна дія `capabilities`; не запускали. Це не Hermes runtime. |
| Integration worker | Шаблон пер-агентних інтеграційних сервісів | Compose template є; потребує окремих AppRole, grants, мережі й налаштування провайдера. Не запускався. |

Основні файли: `docker-compose.yml`, `deploy/docker-compose.yml`, `deploy/docker-compose.alice.yml`, `deploy/docker-compose.directors.yml`, `deploy/docker-compose.integrations.yml`, `deploy/runtime/agent_runner.py`, `deploy/runtime/alice_runner.py`, `deploy/runtime/director_runner.py`, `deploy/runtime/integration_runner.py`.

Compose та Docker у межах цього завдання не запускалися. Docker CLI у попередньо перевіреному sandbox відсутній; тому не заявляється, що образи зібрані, мережі існують чи контейнери працюють.

### 4.2. Контроль доступу та секрети

- Канонічний KV v2 prefix визначений у `src/vault_paths.py`: `secret/syndicate/...`; під час підготовленої міграції код має 404-only fallback і точкові grants для legacy-шляху. Це **шляхи, не значення секретів**; live Vault не змінювався. План: [`docs/NAMESPACE_MIGRATION.md`](NAMESPACE_MIGRATION.md).
- Alice має окрему статичну HCL policy `config/vault/policies/eva-alice.hcl` і окремі env-імена AppRole. Політика обмежена власною auth/Gemini-парою та token self-renewal/lookup; не застосована до live Vault.
- Статична перевірка `python tools/vault_policies.py --check` пройшла: 11 policy definitions, 12 code-read services. Перевірка генератора не є Vault login або policy apply.
- Є різні за рівнем security-механізми: `AgentPolicy`/dispatcher, per-agent profile, worker action allowlist, API auth, PII redaction, Vault policy та audit. Їхній наскрізний зв’язок треба перевіряти у цільовому deployment; один прапорець не замінює інші.
- На окремих workers дані записуються в локальні ізольовані store/volumes. Інтеграція цих store з центральною пам’яттю/аудитом не скрізь завершена.

### 4.3. Runtime-рішення, які ще відкриті

У профілях більшості агентів зазначений `runtime: hermes`, але це не підтверджує, що Hermes встановлений і безпечно під’єднаний. Основний Compose зараз описує Python/FastAPI runner Єви та LangGraph; окремі native workers існують як підготовлені пакети. Перед вибором між одним `eva-agent` та окремими Hermes-контейнерами потрібно узгодити adapter/tool gateway, memory isolation, мережі, AppRole, бюджети й audit. Не вважати наявність Compose overlay вирішенням цієї архітектури.

## 5. n8n: фактичне з’єднання, код і чернетки

### 5.1. Що існує в коді

- `src/n8n_templates.py` будує локальні шаблони: sensory switch, error handler, ранковий briefing і вечірній reflection. Шаблони мають `active: false`.
- `src/agents/architect/n8n_builder.py` створює workflow JSON; `src/agents/architect/flowlint.py` перевіряє форму, core nodes, секрети, обробку помилок та ідемпотентність; `src/agents/architect_preview.py` готує Mermaid-перегляд без n8n API-виклику.
- `src/agents/architect_n8n.py` містить шлях створення workflow як **inactive** після approval/gates і наявності `N8N_BASE_URL`/`N8N_API_KEY` у зовнішньому середовищі. У тесті використаний mock transport; реальний n8n endpoint не викликався. Код не має capability `n8n.workflow.activate`.
- `config/agents/architect.profile.json` містить декларації `n8n.workflow.design`, `n8n.workflow.mount`, scope `n8n/live` та `services_enabled: ["n8n"]`, але сам профіль залишається `prepared_not_enabled`; `live_modes.n8n_editor` і `gitops_push` — false. Це не свідчить про живу авторизацію. Contract: `architect_core/ARCHITECT_WORKFLOW_CONTRACT.md`.
- У Compose n8n має encrypted credentials key як обов’язкову env-змінну, community packages вимкнені, `executeCommand` і `ssh` nodes виключені. Це лише бажана конфігурація.
- У перевірених repository paths не знайдено експортованих production workflow JSON. Це не є інспекцією live n8n instance або його persistent volume.

### 5.2. Історичні сценарії — не активні n8n workflows

`eva_core/EVA_N8N_WORKFLOWS.md` описує вісім задумів. Вони не мають трактуватися як створені/запущені воркфлоу:

| Назва у старій специфікації | Опис у документі | Поточний статус |
|---|---|---|
| `EVA-GATEWAY-INBOUND` | Telegram intake та routing | Чернетка; Telegram bot/allowlist не підключені. |
| `EVA-DAILY-BRIEFING-ORCHESTRATOR` | Паралельні звіти агентів і погода | Чернетка; немає підтвердженого live schedule/provider. |
| `EVA-HITL-ACTION-GATE` | Погодження дій у Telegram | Чернетка; не є фактичним approval channel. |
| `EVA-NOTEBOOKLM-ARCHIVE-SYNC` | Drive/NotebookLM синхронізація | Чернетка; NotebookLM/Drive не налаштовані. |
| `EVA-VOICE-CALL-DISPATCHER` | Голосовий виклик/повідомлення | Чернетка; не відповідає автоматично погодженому OpenRouter voice route. |
| `EVA-NAVIGATOR-AND-HOTELS` | Карти/транспорт/бронювання | Чернетка; provider/API credentials не налаштовані. |
| `EVA-SMART-SCANNER` | OCR та документний архів | Чернетка; не активувати для медичних/особистих матеріалів без окремого privacy review. |
| `EVA-CANVA-CREATIVE-SUITE` | Canva/Mermaid-креативи | Чернетка; Canva API/browser automation не підключені. |

### 5.3. Безпечний майбутній шлях

```text
workflow draft (active=false)
    -> local FlowLint + preview
    -> change request / human approval
    -> за наявності окремого grant/API - mount inactive
    -> окремий ручний дозвіл на будь-яке activation
```

n8n не є control plane і не може створювати capabilities/resource grants. Зміна workflow, передача credentials, live import або активація потребують окремого дозволу; цей документ дозволу не надає. Для Architect не можна вважати зміст старої специфікації джерелом фактичних прав.

## 6. Паспорт 12 профілів

У всіх наведених нижче записах `prepared_not_enabled` і `model_status: not_selected` — профільні значення, а не health-check. У розділі «декларації» наведено саме поля репозиторного профілю; вони не є твердженням, що service увімкнений у поточному середовищі.

| ID / ім’я | Цільова роль | `role_status` | Профіль |
|---|---|---|---|
| `eva` — Єва | Єдина CEO, персональна асистентка й координаторка | `agreed_draft` | `prepared_not_enabled` |
| `alice` — Аліса | Head of Engineering; звітує Єві | `agreed_draft` | `prepared_not_enabled` |
| `architect` — Архітектор | Архітектура й n8n workflow drafts | `identity_draft` | `prepared_not_enabled` |
| `marshal` — Маршал | Безпека; owner Sentinel Protocol | `identity_draft` | `prepared_not_enabled` |
| `fin` — Фін | Фінансова аналітика; без платежів | `identity_draft` | `prepared_not_enabled` |
| `doc` — Док | Здоров’я/тренування/харчування — роль ще погоджується | `not_agreed` | `prepared_not_enabled` |
| `kira` — Кіра | SYNDICATE Academy — роль ще погоджується | `not_agreed` | `prepared_not_enabled` |
| `sam` — Сем | Інвестиційне/кількісне дослідження | `identity_draft` | `prepared_not_enabled` |
| `kodex` — KODEX | Знання, архів; майбутня prompt/skill інженерія | `not_agreed` | `prepared_not_enabled` |
| `oscar` — Оскар | Медіа, аудиторія, дослідження коментарів | `agreed_draft` | `prepared_not_enabled` |
| `tyler` — Тайлер | POD/дропшипінг, unit economics | `agreed_draft` | `prepared_not_enabled` |
| `jack` — Джек | Кількісний sports/esports/poker аналіз | `agreed_draft` | `prepared_not_enabled` |

### 6.1. Єва (`eva`)

**Відповідальність.** Єдина CEO/координаторка й основна персональна асистентка Андрія. Може структурувати думки, синтезувати підтверджені матеріали, готувати brief/reflection і маршрутизувати дозволені задачі; не має необмеженої влади та не видає собі/іншим права.

**Функції в коді.** `src/agents/eva.py` містить chat/conversation, compose briefing/reflection, delegation intent, system status, decisions, deadlines та curator actions; `src/orchestrator.py` містить LangGraph task routes і обробку approval/error states. Наявність route не є доказом роботи API в production.

**Декларації та стан.** Профіль `config/agents/eva.profile.json`: activation prepared, capabilities/resource scopes/services порожні; Telegram disabled із порожнім allowlist; voice, screen, camera, Google Meet, message monitoring і geolocation вимкнені. Psychology knowledge source manifest має `not_loaded`. Draft skills `eva-humanizer`, `eva-summary`, `eva-deep-research`, `eva-skill-creator`, `eva-prompt-lab` не є активними tools.

**Джерела/підключення.** Основні джерела — запити Андрія та явно надані/дозволені матеріали; згадки звітів інших агентів — лише фактичні payloads. Профіль фіксує погоджений Андрієм шлях лише через офіційний YouTube Data API (пошук/метадані/явно вказані плейлисти), але ключі очікують окремого deployment. YouTube Music не підключати. Telegram Bot API не налаштований. Нічний аналіз 03:00 має `source_provider: not_configured`; це не активний scheduler.

**Межі.** Не ставить медичних діагнозів; не читає/зберігає секрети; не моніторить повідомлення автоматично; не надсилає листи/публікації та не запускає зовнішні дії без відповідної перевірки й підтвердження. Файли: `src/agents/eva_runtime_prompt.md`, `eva_core/EVA_MEMORY_POLICY.md`, `config/agents/eva.profile.json`.

### 6.2. Аліса (`alice`)

**Відповідальність.** Агентка-керівниця інженерного відділу (Head of Engineering), звітує Єві. «Alice» — ім’я агентки; `antigravity_sdk` — runtime technology, не її ідентичність. Початковий погоджений напрям — API-first engineering/code review у виділеному workspace.

**Функції в коді.** `src/agents/alice.py` містить окремий runner/client, профільні та action gates, обмеження запитів/інструментальних викликів і workspace containment. Явно перелічені SDK file tools: `LIST_DIR`, `FIND_FILE`, `SEARCH_DIR`, `VIEW_FILE`; для engineering дії — також `CREATE_FILE`, `EDIT_FILE`. Shell, browser/desktop, URL fetch, MCP, subagents і production secrets mount не надаються. SDK smoke test з fake Agent пройшов без мережі; реальний provider transport не перевірявся.

**Декларації та стан.** `config/agents/alice.profile.json`: `activation=prepared_not_enabled`, `runtime=antigravity_sdk`, роль agreed draft, модель не вибрана, `capabilities`, `grants`, `resource_scopes`, `services_enabled` порожні. API, internet, browser automation, GitHub, image generation, video render, billing, history ingest, production deployment і Telegram — false. Profile workspace: `alice/workspace`; контейнерний шлях `/data/eva/data/alice/workspace`; shell і production secrets mount вимкнені. Reference skills є лише каталожною довідкою; SDK передає порожній набір skills.

**Залежності/секрети.** Підготовлені окремі Dockerfile, Compose overlay та `google-antigravity==0.1.22`; dependency install/pip check і SDK config smoke локально пройшли. Gemini Developer API key/model path у Vault — лише майбутнє посилання; модель, ціна, квота, billing cap та filtered egress не перевірені. Google One не використовується як API credential; жодних реальних ключів не створено/не додано.

**Посилання.** `docs/ALICE_RUNTIME.md`, `config/agents/alice.profile.json`, `deploy/docker-compose.alice.yml`, `deploy/runtime/alice_runner.py`; upstream: [Antigravity SDK Python](https://github.com/google-antigravity/antigravity-sdk-python), [Gemini API docs](https://ai.google.dev/gemini-api/docs). Усі URL довідкові; live API тут не викликався.

### 6.3. Архітектор (`architect`)

**Відповідальність.** Проєктувати архітектуру й workflow, готувати blueprint, локальний lint/preview та change proposal. Задачі — від Андрія; Єва може отримати короткий звіт payload-ом, але не призначає йому роботу.

**Функції в коді.** `src/agents/architect/agent.py`: workflow design, golden templates, ADR, code review/verification, readiness, proposal-based gitops/drift functions та scaffold. `n8n_builder.py` і `flowlint.py` генерують/перевіряють JSON; `architect_preview.py` будує Mermaid без мережі. Окремий `architect_n8n.py` має inactive-only mount code; контрактний тест використовує mock n8n endpoint, реального виклику не було.

**Декларації та стан.** У `config/agents/architect.profile.json` задекларовано `n8n.workflow.design` і `n8n.workflow.mount`, scope `n8n/live`, `services_enabled=["n8n"]`. Це не active profile: activation `prepared_not_enabled`; `live_modes.n8n_editor=false`, `gitops_push=false`, `host_control=false`, Telegram/geolocation false. Немає capability `n8n.workflow.activate`. `N8N_BASE_URL`/`N8N_API_KEY` — імена env-полів, не налаштовані credentials.

**Дані/обмеження.** Джерела — репозиторні контракти, тестовані API specs, код і локальні CI/test results; architecture knowledge manifest має `not_loaded`. Secrets не входять у workflow JSON; core nodes only; n8n не є джерелом grants. Активацію, імпорт у live instance, Git push, Docker/host, Telegram та зміни production не робити без окремих дозволів. Файли: `architect_core/ARCHITECT_WORKFLOW_CONTRACT.md`, `config/agents/architect.profile.json`, `src/agents/architect_runtime_prompt.md`.

### 6.4. Маршал (`marshal`)

**Відповідальність.** Безпека, контроль меж доступу й аналіз загроз у межах наданих даних. Owner Sentinel Protocol; Sentinel — окремий набір перевірок/служб на межах dispatcher, tools і services, а не агент із власним профілем.

**Функції в коді.** `src/agents/marshal.py` має перевірку задач, outbound action review, prompt-injection/“lethal trifecta” checks, command safety, dependency risk, secret scan, webhook HMAC verification, security audit, incident report і morning payload. `src/agents/sentinel.py` містить Sentinel validation routes; orchestrator викликає їх як service boundary. Marshal identity prompt прямо забороняє заявляти live host control/lockdown/veto.

**Декларації та стан.** Профіль має порожні capabilities/resource scopes/services; `prepared_not_enabled`; host control, emergency lockdown, Telegram, voice і geolocation false. Security sources manifest `not_loaded`. SkillSpector у no-LLM mode — перевірка локального кандидата, не автоінсталяція/дозвіл на скіл.

**Джерела/межі.** Репозиторні правила, локальні manifests, структуровані спостереження, які окремо передав оператор. Немає живого host telemetry, Falco/Tetragon, Drive, Telegram, eBPF, policy veto чи egress control підтвердження. `marshal_core/MARSHAL_ROLE_BOUNDARIES.md` і `marshal_core/MARSHAL_HITL_CONTRACT.md` — правила/чернетки, не доказ увімкнення.

### 6.5. Фін (`fin`)

**Відповідальність.** CFO-аналітика: облік, бюджет, runway, фонди, звірка та звітність. Робота тільки read/recommendation; оплату, переказ, списання чи замовлення виконує Андрій.

**Функції в коді.** `src/agents/fin.py` містить analyze, runway, budget check, tax radar, bank sync request, morning data, funds check та report. Супутні modules охоплюють local ledger, basket audit, receipt reconciliation, export і фінансові buttons. За відсутності фактичних даних має повертатися unavailable, а не оцінений баланс.

**Декларації та стан.** Профіль має `fin.dispatch.eva_basket`, `fin.funds_check`, `fin.reports.local`, `fin.docs.local_generate` і scope `fin/out`, але activation prepared; `services_enabled` порожні. Bank read/write, Telegram, Drive, Obsidian, n8n, voice та monitors вимкнені. Усі profile skills — `draft`; кнопки й розклади не є live delivery.

**Джерела/підключення.** Дозволені input-ами Андрія бюджети, чеки, виписки, фактичні звіти провайдерів та офіційні фінансові джерела. `src/integrations/banking.py` містить Monobank Personal API request shape, але ключі не налаштовані; PrivatBank path повертає порожній результат/недоступність, а не live account sync. Банк read-only при майбутньому окремому погодженні; жодних платежів. Drive/Obsidian не налаштовані. Файли: `fin_core/FIN_ROLE_BOUNDARIES.md`, `config/agents/fin.profile.json`.

### 6.6. Док (`doc`)

**Цільова компетенція.** Wellness, тренування, харчування, самопочуття та підготовка інформації для розмови з лікарем. Профіль поки має `role_status=not_agreed`, тому це напрям роботи коду, не затверджений клінічний мандат. Док не ставить діагнозів і не є лікарем.

**Функції в коді.** `src/agents/doc.py` містить розбір/підсумок даних, readiness score з переданих метрик, тренувальний протокол, nutrition plan, biomarker trend, screening calendar, emergency card, pre-visit dossier, compliance/nervous-system та research actions. Відсутні показники не повинні домислюватися.

**Декларації та стан.** Профіль prepared; prompt `not_prepared`, модель не вибрана, grants/capabilities/services порожні; геолокація вимкнена. Telegram-кнопки позначені як ready, але bot/token pending і канал не підключений. Немає health wearable чи clinical API. Knowledge sources потрібно окремо відібрати й завантажити.

**Дані/межі.** Тільки надані Андрієм показники/документи та вендоровані локальні exercise datasets із відповідними ліцензіями. Медичні дані — чутливі; не класти в репозиторій, загальний лог або публічний векторний index. Файли: `doc_core/DOC_ROLE_BOUNDARIES.md`, `doc_core/DOC_HEALTH_SPEC.md`, `config/agents/doc.profile.json`.

### 6.7. Кіра (`kira`)

**Цільова компетенція.** Навчальна менторка SYNDICATE Academy: сократичні запитання, персональний навчальний план, мовна практика, history synthesis, code-review mentoring та короткі quizzes. Це описує існуючий код, але профіль досі `role_status=not_agreed`.

**Функції в коді.** `src/agents/kira.py`, `kira_catalog.py`, `kira_learning.py` реалізують каталог дисциплін, dialogue, уроки, micro-quiz, learning status/proposals та збереження прогресу. Без LLM відповідь, що потребує генерації, повертає `unavailable`; quiz оцінюється лише за наявним ключем і фактичними відповідями.

**Декларації та стан.** Capabilities/resource scopes/services і власні skills порожні; prompt `not_prepared`; модель не вибрана; Telegram/LMS не підключені; геолокація false. Каталог/seed у репозиторії не означає, що зовнішні курси/бази знань під’єднані.

**Дані/межі.** Джерела — локальний seed, матеріали користувача, ліцензовані курси/документація після окремого вибору й фактичні результати вправ. Не заявляти засвоєння теми без перевірки. Файл меж: `kira_core/KIRA_ROLE_BOUNDARIES.md`.

### 6.8. KODEX (`kodex`)

**Відповідальність за рішенням Андрія.** Знання та архів; prompt engineering; каталог скілів/промптів; майбутня робота з NotebookLM/Obsidian і пошук нових матеріалів. Ці продуктові обов’язки ширші за нинішній profile role, який позначено `not_agreed`.

**Функції в коді.** `src/agents/kodex.py` має ingest/classify/hash, архівний read, labeling, move, rewrite/delete requests, approvals, download approvals, supported-format checks та report for Eva. `src/agents/kodex_telegram.py`/`tools/kodex_bot.py` — handler/runner code, але бот не підключений. Автоматичний scraper і повний набір парсерів форматів відсутні.

**Декларації та стан.** Профіль містить `kodex.archive.read_all`, `kodex.archive.write_unlabeled`, `kodex.labeled.move`, `kodex.labeled.change_with_andrii_permission`, `kodex.report.eva`, scope `kodex/archive`; проте activation `prepared_not_enabled`, `services_enabled` порожнє, prompt не підготовлений. Telegram bot pending token, allowlist default-deny. NotebookLM, Obsidian, Drive і Sheets не налаштовані.

**Дані/межі.** `andrii_protected` можна читати; змінювати/видаляти лише після точкового дозволу Андрія. Не маркувати немічені завантаження як захищені без підтвердження. Файлові операції мають бути прозорі та потрапляти до звіту Єві о 21:00; плановий scheduler не підтверджений. Для нових форматів/URL download — окреме підтвердження. Файли: `config/agents/kodex.profile.json`, `src/agents/kodex.py`, `src/agents/kodex_telegram.py`.

### 6.9. Сем (`sam`)

**Відповідальність.** CIO/кількісний інвестиційний аналіз, оцінка setup-ів, ризик-перевірки й журнал. Виконує лише доручення Андрія; іншим агентам сам задач не ставить. Інвестиційні рішення — обговорення/пропозиції, не автоматична торгівля.

**Функції в коді.** `src/agents/sam/agent.py` реалізує evaluate setup, confluence/constraints, manual decision handling, paper outcome journal, portfolio risk та bounded research. Модулі включають `sam_signal`, `sam_policy`, `sam_broker`, `sam_report`. Відсутність свічок/ринкових даних має бути `unavailable`.

**Декларації та стан.** `role_status=identity_draft`, capabilities/resource scopes/services порожні, activation prepared; брокер, Telegram, voice, live cockpit, auto-FX/crypto, auto-invest, demo/live broker і social-listen вимкнені. Quant source manifest не завантажений; Drive/Obsidian/NotebookLM не налаштовані.

**Дані/межі.** Для локального аналізу потрібні датовані, ліцензовані котирування/історичні дані, офіційні звіти та фактичні fills; джерела треба підключити й звірити окремо. Немає обіцянки alpha/прибутку; модельна впевненість не є дозволом на ордер. Файли: `sam_core/SAM_ROLE_BOUNDARIES.md`, `sam_core/SAM_HITL_CONTRACT.md`, `config/agents/sam.profile.json`.

### 6.10. Оскар (`oscar`)

**Відповідальність.** Контент/редактура, дослідження аудиторії та аналіз коментарів/питань; підготовка матеріалів і drafts, не публікація.

**Функції в коді.** `src/agents/oscar/agent.py` має LLM routing interface, comments normalize/dedup/PII redaction, pain map, classification (`pain/question/hate/lead/other`), аналіз переданих transcript-ів, editorial drafts, thumbnail/diagram, email metric math лише з переданих лічильників і approval-pending queue. `publish`, `send_email`, `add_persona` позначені як blocked external.

**Декларації та стан.** Профіль prepared, capabilities/grants/resource scopes/services порожні; три профільні skills — `draft`; Telegram не підключений, allowlist порожній. Provider models і comment client не підтверджені live. `fetch_comments` без налаштованого клієнта повертає unavailable; `harvest_comments` приймає лише переданий дозволений export і явно фіксує `live_scraping: false`.

**Джерела/межі.** YouTube Data API може бути read-only джерелом після окремого credential setup; не завантажувати аудіо/відео. Для інших мереж код нормалізує передані дані, але не обходить login, не читає довільні профілі й не є соціальним crawler-ом. Історичний опис `oscar_core/OSCAR_FULL_SPEC.md` — дизайн, не права. Oscar є кандидатом на споживання майбутнього соціального набору даних, але жодного доступу не видано.

### 6.11. Тайлер (`tyler`)

**Відповідальність.** POD/дропшипінг та персоналізований фізичний мерч: калькуляція ціни/маржі, перевірка якості й безпечний draft-конвеєр. Користувачеві затверджувати закупівлю/виробництво/публікацію.

**Функції в коді.** `src/agents/tyler/agent.py` і `finance.py` рахують unit economics із наданих котирувань, застосовують quality gate (ліцензії, resolution, операторське підтвердження trademark review), готують локальний preview/order concept, маршрутизують лише передані пропозиції постачальників, роблять Pinterest draft і аналіз supplied reviews. `fulfill`, `publish`, `charge` заблоковані; trademark live search повертає unavailable.

**Декларації та стан.** Профіль prepared, caps/services/grants порожні; три skills draft; Telegram не підключений. Provider quotes/Printify/Printful/Gelato/Prodigi та Pinterest APIs не налаштовані. Кодовий список постачальників не є обліковим записом або інтеграцією.

**Джерела/межі.** Потрібні ручні/ліцензовані котирування, операторські підтвердження арту/шрифтів/blank/доставки. `trademark_reviewed` — введене оператором свідчення, не реєстровий пошук. Не створювати платіж, не надсилати замовлення фабриці, не публікувати pin. Файли: `tyler_core/TYLER_FULL_SPEC.md`, `config/agents/tyler.profile.json`.

### 6.12. Джек (`jack`)

**Відповідальність.** Sports/esports/poker quantitative analyst: оцінки з наданих даних, fair probabilities, паперовий облік та risk guard. Не є букмекером і не виконує ставку.

**Функції в коді.** `src/agents/jack/agent.py`, `engines.py`, `quant.py`, `tracker.py`: model/evaluate/benchmark, paper record/settle/report, odds scout та anti-tilt. Методи явно маркують розрахунки на supplied inputs; оцінки не калібровані й не є прогнозом гарантованої точності.

**Декларації та стан.** Профіль prepared; capabilities/resource scopes/services порожні; skills draft; Telegram не підключений, allowlist порожній. Optional Odds API scout без клієнта повертає unavailable. Окремий worker overlay має замовчування лише `capabilities`; operator allowlist потрібен.

**Джерела/межі.** Котирування та результати мають бути надані/офіційно отримані з перевіреними timestamp/license. `place_bet` — blocked external; немає live execution, брокерських або букмекерських credentials. Paper bankroll — симуляційний ввід, не банківський баланс. Файли: `jack_core/JACK_FULL_SPEC.md`, `config/agents/jack.profile.json`.

## 7. Ініціативи та ролі без профілю

### 7.1. Рей, Декс, Атлас

Імена/цільові ніші, визначені Андрієм, але не знайдено окремих profile/runtime implementations у перевірених `config`, `docs`, `src`:

- **Рей** — дропшипінг.
- **Декс** — маркетинг і лідогенерація.
- **Атлас** — екскурсії.

Це planned roles, не активні агенти; autonomy, зовнішні дії, джерела даних і сервіси не узгоджені. Не створювати профілі чи grants у межах цього паспорта.

### 7.2. Керівна панель

Власний dashboard/desktop client — бажаний майбутній control surface. Його покриття, API contract, authentication, HITL UI та desktop permissions ще потребують визначення; Paperclip не є обов’язковим, якщо власний продукт покриє вимоги. Файл/застосунок у цьому завданні не змінювався.

### 7.3. Інтеграція поточної Arena-сесії

Не вирішено, чи має поточна Arena-сесія стати окремим агентом. Для неї не створювати profile, grants або connector без окремого рішення Андрія.

## 8. Майбутній соціальний парсер: Instagram, Facebook, Threads, Telegram

**Стан:** тільки ініціатива/дизайн. Парсера, crawler-ів, credentials, API apps, integration scopes, розкладу чи живих n8n workflow у межах цієї роботи не створено. Це не є погодженням доступу до будь-якого облікового запису, профілю чи каналу.

### 8.1. Мета та запропонована межа

Ціль — збирати дозволені матеріали з визначених каналів/профілів у knowledge base та аналітику: теми, повторювані питання/болі, часові тренди й вимірювання, які офіційно надає платформа. Можливі користувачі результату — KODEX (індексація/джерела), Oscar (аудиторні/редакційні теми), Eva (підсумки) та, після окремого рішення, інші агенти. «Більшість агентів» не означає спільний або blanket grant: кожному споживачу потрібні власні read scope, призначення й privacy gate.

Перший варіант має бути read-only та allowlist-based: Андрій явно визначає акаунти/канали/сторінки, часовий діапазон і типи об’єктів; система зберігає provenance й мінімізує дані авторів. Публікація, follow/like/comment, DM, реклама, масове outreach, платежі та зміна профілів — поза scope.

### 8.2. Рекомендований потік даних (не реалізований)

```text
погоджений список джерел
    -> офіційний API adapter платформи + read-only OAuth/token
    -> quota/rate-limit + checkpoint + дедуп за platform/object_id
    -> нормалізація + мінімізація авторських даних + PII redaction
    -> перевірка provenance/дозволу/retention
    -> quarantine для prompt-injection/untrusted text
    -> окремий knowledge/analytics store з source URL і collected_at
    -> пер-агентний read-only view за явним scope
```

n8n за потреби може бути лише scheduler/executor після затвердження; він не зберігає policy й не видає grants. Майбутній parser має викликатися через policy-checked service adapter, а не отримувати cookies чи загальну мережу. Рекомендована нормалізована картка: `platform`, `object_id`, `canonical_url`, `parent_id`, `created_at`, `collected_at`, excerpt/text у дозволеному обсязі, доступні офіційні counters, мінімізований `author_ref`, `source_permission`, API/version metadata, content hash, retention expiry та processing status. Raw media не зберігати за замовчуванням.

### 8.3. Межі за платформами

| Платформа | Переважний майбутній шлях | Що ще треба перевірити/погодити |
|---|---|---|
| Instagram | Офіційний Instagram/Meta API у межах дозволених облікових записів і scopes | Які account types/objects доступні; app review, permissions, public-vs-owned data, rate limits, ліцензія/повторне використання. Не припускати доступ до довільних профілів чи приватних матеріалів. |
| Facebook | Офіційний Graph API з вузькими Page/account scopes | Page ownership/consent, дозволені fields, review, коментарі/історія, retention. Не припускати приватний профільний доступ або повний архів. |
| Threads | Офіційний Threads API, лише якщо поточні endpoints/scopes покривають погоджену задачу | Підтвердити об’єкти, access token, app review, rate limits і права на збереження. Наявність `threads` у канал-списку Oscar не є adapter чи grant. |
| Telegram | Bot API у каналах/групах, куди бота явно додано та де є необхідні права; scope тільки на allowlist | Bot membership/admin rights, історія/межі читання, приватність учасників, retention. MTProto/user-client — окрема архітектурно-правова перевірка; не підміняти ним Bot API. |

Заборонений шлях: scraping HTML/внутрішніх endpoint-ів, обхід login/anti-bot/доступів, підміна fingerprint, browser cookies/saved sessions, автоматизація особистого desktop або вилучення даних з приватного профілю без належної авторизації. Окремий browser profile/session не є доказом офіційного API дозволу.

### 8.4. Дані, безпека й acceptance gates

Перед кодом слід узгодити: список джерел та їх власника; власні/партнерські/публічні/конкурентні акаунти; які пости, comments/replies та часову глибину збирати; правову підставу/умови платформи й право повторного використання; retention/deletion; які персональні поля відкидати або хешувати; країну/місце зберігання; споживачів-агентів і запити; джерело tokens, budget/quota та графік. Це не юридична консультація — за потреби потрібна окрема правова оцінка.

Мінімальні критерії до майбутнього implementation proposal:

1. Перевірити актуальні офіційні docs, об’єкти/permissions, app review, тарифи/квоти й platform terms без припущень.
2. Обмежити credentials окремими Vault path/AppRole і read-only scopes; не зберігати значення ключів у Git/логах.
3. Підтвердити allowlist джерел, обробку consent/deletion, retention, redaction, quota, audit та кожного agent consumer.
4. На synthetic/approved exports перевірити дедуп, provenance, rate-limit/backoff, permission failure, deletion і prompt-injection isolation.
5. Усі workflows inactive; ніякого live deployment, API key creation чи account login без окремого дозволу.

### 8.5. Що вже є поруч

`src/agents/oscar/agent.py` нормалізує передані коментарі для YouTube/TikTok/Reddit/X/Threads/blog, маскує PII та дедуплікує за channel/id. `harvest_comments` приймає supplied export і встановлює `live_scraping: false`; `fetch_comments` потребує окремий YouTube client і без нього повертає `unavailable`. Це — downstream processing, не майбутній Instagram/Facebook/Threads/Telegram data collector. Для нового parser-а не використовувати збережені browser sessions, і не вважати, що Oscar має соціальні grants.

## 9. Голос, зовнішні сервіси та інтеграційні розриви

### 9.1. Голос

У `src/voice/` є `VoiceManager`, ElevenLabs direct provider, OpenAI/xAI TTS та local/Groq Whisper STT. Це реалізація інтерфейсів/кодових адаптерів, не підтверджене підключення. Нинішній `src/voice/elevenlabs.py` читає `elevenlabs/api_key` і напряму викликає `api.elevenlabs.io`; це **не** погоджений користувачем цільовий маршрут.

Погоджений напрямок на майбутнє — ElevenLabs через OpenRouter; секрет — лише у Vault `secret/syndicate/api-keys`, поле `openrouter_api_key`. Endpoint, model, voice, billing/ціна й точна сумісність потрібно спершу перевірити. Не додавати реальні ключі й не вважати кодовий direct adapter готовим або дозволеним.

### 9.2. Інші сервісні конектори

`src/integrations/` містить registry/adapters для Google Workspace, Telegram, MCP, banking та `ServiceHub` із пер-агентними grants для skills, Hindsight, OmniRoute, Actual Budget, HyperFrames і MCP. Наявність adapter-коду або contract tests не доводить, що конкретний API key, account, endpoint, network route або користувацький budget існує. У production кожен connector слід включати окремо з мінімальним scope, захистом PII, health/negative tests та revoke-процедурою.

### 9.3. YouTube

Погоджена верхня межа — тільки офіційний YouTube Data API; без завантаження відео/аудіо, без обходу платформи та без YouTube Music automation. Профіль Eva називає ключі pending deployment і радить перевірити квоту при налаштуванні. API key/token не присутній у паспорті.

## 10. Довідкові URL і внутрішні точки підключення

Зовнішні URL нижче — **довідкові покажчики**, не результат live-перевірки. Перед інтеграцією треба перевірити актуальну версію документації, дозволені endpoints/scopes, account eligibility, terms, quota, тарифи й доступність з цільового сервера. Зовнішні API цього документа не викликалися.

### 10.1. Системна архітектура

| Тема | Довідковий URL | Внутрішня точка |
|---|---|---|
| LangGraph | [LangGraph Python overview](https://docs.langchain.com/oss/python/langgraph/overview) | `src/orchestrator.py` |
| Hermes Agent | [Hermes Agent repository](https://github.com/NousResearch/hermes-agent) | `config/agents/*.profile.json`; повний runtime bridge не підтверджений |
| Antigravity SDK | [Python SDK source](https://github.com/google-antigravity/antigravity-sdk-python) | `src/agents/alice.py`, `deploy/requirements-alice.txt` |
| Gemini API | [Gemini API docs](https://ai.google.dev/gemini-api/docs) | Alice provider plan; model/budget not selected |
| n8n | [n8n documentation](https://docs.n8n.io/) · [API](https://docs.n8n.io/api/) | `src/n8n_templates.py`, `src/agents/architect_n8n.py`, `N8N_BASE_URL`/`N8N_API_KEY` env names only |
| Docker Compose | [Docker Compose docs](https://docs.docker.com/compose/) | `docker-compose.yml`, `deploy/docker-compose*.yml` |
| HashiCorp Vault | [Vault documentation](https://developer.hashicorp.com/vault/docs) | `src/vault_paths.py`, `config/vault/policies/`, `tools/vault_policies.py` |
| PostgreSQL / pgvector | [pgvector project](https://github.com/pgvector/pgvector) | `config/postgres/`, memory/database modules |
| Redis | [Redis documentation](https://redis.io/docs/latest/) | `config/redis/`, Compose env only |

### 10.2. Платформи для майбутнього social parser-а

| Платформа/API | Офіційний URL | Невирішене |
|---|---|---|
| Instagram / Meta | [Instagram Platform API](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/) | Account/objects/scopes, app review, rights, quota, storage. |
| Facebook | [Graph API](https://developers.facebook.com/docs/graph-api/) | Page/profile доступ, permissions, approved use cases. |
| Threads | [Threads API](https://developers.facebook.com/docs/threads/) | Чи поточні endpoints/scopes покриють погоджений обсяг. |
| Telegram | [Bot API](https://core.telegram.org/bots/api) · [Telegram API](https://core.telegram.org/api) | Явне додавання бота, права, історія, retention; user-client окремо не погоджений. |
| YouTube | [YouTube Data API v3](https://developers.google.com/youtube/v3) | Лише погоджений read scope; квота/key pending; без media download. |

### 10.3. Інші профільні довідки для можливого майбутнього підключення

| Профіль/сервіс | Ресурс | Стан у цьому репозиторії |
|---|---|---|
| Голос через OpenRouter | [OpenRouter API reference](https://openrouter.ai/docs/api-reference/overview) | Цільовий маршрут; endpoint/model/voice/price не перевірені, ключів немає. |
| ElevenLabs voice format | [Text-to-Speech API](https://elevenlabs.io/docs/api-reference/text-to-speech) | Код містить direct adapter; не використовувати як затверджений route без перегляду. |
| Actual Budget | [Actual Budget docs](https://actualbudget.org/docs/) | Integration code/contract описані; account, server, budget і account IDs не надані. |
| Monobank | [Monobank API docs](https://api.monobank.ua/docs/) | У коді є client request shape; ключів/real account test немає; не платіжний шлях. |
| CFTC COT | [CFTC Commitments of Traders](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) | Можливе джерело дослідження Sam; не live connector. |
| FRED | [FRED API](https://fred.stlouisfed.org/docs/api/fred/) | Можливе дослідницьке джерело Sam; не live connector. |
| The Odds API | [API guide](https://the-odds-api.com/liveapi/guides/v4/) | Jack scout без клієнта повертає unavailable; bookmaker coverage не підтверджено. |
| Obsidian | [Obsidian Help](https://help.obsidian.md/) | Бажаний KODEX напрям; sync/API/доступ до vault не налаштовані. |
| NotebookLM | [NotebookLM Help](https://support.google.com/notebooklm/) | Майбутній дослідницький/knowledge destination; офіційний automation API тут не підтверджений. Browser-cookie login не використовувати. |

### 10.4. Внутрішні точки конфігурації

- Agent identity/role/declared scopes: `config/agents/<agent>.profile.json`.
- Похідна матриця доступів: `docs/PERMISSIONS_MATRIX.md`; генератор `tools/export_permissions.py`.
- Vault logical paths: `src/vault_paths.py`; policy validation `python tools/vault_policies.py --check`.
- Main orchestration: `src/orchestrator.py`; profile task routing і default-off routes.
- n8n draft/build/lint: `src/n8n_templates.py`, `src/agents/architect/n8n_builder.py`, `src/agents/architect/flowlint.py`.
- Сервісні adapters: `src/integrations/`, `src/voice/`; конкретні provider credentials мають надходити через операторський secret management, не з документа/Markdown.
- Локальні особисті файли: `EVA_DATA_DIR` / `KODEX_DATA_DIR`; реальні значення шляхів визначає deployment operator.

## 11. Відкриті рішення та ризики

1. **Runtime/container model:** один `eva-agent` чи per-agent Hermes containers; потрібен дієвий ізольований tool bridge і перевірка кожного service path.
2. **Agent roles:** Doc, Kira, KODEX, Architect, Fin, Marshal та Sam мають статуси, відмінні від погоджених role drafts; завершити роль, prompt, модель і autonomy окремо.
3. **Моделі та бюджет:** жодна profile model не вибрана; API не вважати безкоштовними. Alice потребує Gemini model + billing limit; voice — окремий cost/endpoint review.
4. **Egress:** глобальне бажання доступу до інтернету не визначає домени, провайдери, rates, DNS, проксі або ліміти; мережеві зміни без окремого погодження не робити.
5. **n8n:** local templates/mount code існують, але live URL, API key, workflow inventory і production state не перевірені; старі workflow specs не є фактами.
6. **Social parser:** платформи, sources, permissions, retention, legal basis, metrics, schedules, consumer agents і budget не узгоджені; implementation відсутня.
7. **Voice:** нинішній direct ElevenLabs code не збігається з погодженим OpenRouter route; перед змінами перевірити актуальні тарифи та обмеження.
8. **Телеграм:** bots/handlers не підтверджені; allowlist має deny-all за замовчуванням; використовувати лише для Андрія після підключення.
9. **Knowledge services:** NotebookLM, Obsidian, Drive, Hindsight/MCP та зовнішні accounts не слід вважати активними без account-level test і окремих grants.
10. **Dashboard:** власний dashboard/desktop control surface — майбутня потреба; authentication, approvals, service inventory та audit UI ще не підтверджені.
11. **Planned roles:** Ray/Dex/Atlas не мають конфігів/runtime; autonomy й external action scope ще не погоджені.
12. **Live environment:** сервер, TLS, Vault AppRole, Compose, n8n, database, providers і social accounts не інспектувалися/не змінювалися в цьому завданні.

## 12. Перевірка цього знімка

- Локальний gate: `EVA_SKIP_PGSERVER=1 bash tools/check.sh` — успішно.
- Pytest: **885 passed, 35 skipped**, одна Starlette deprecation warning.
- Статична перевірка Vault policy: `python tools/vault_policies.py --check` — успішно; 11 policy definitions, 12 code-read services.
- YAML/Compose файли можна парсити локально; сам Compose не запускали, образи не збирали.
- Живу PostgreSQL не було: використано `EVA_SKIP_PGSERVER=1`; пропуски не є інтеграційною перевіркою production DB.
- Живі Vault, Telegram, n8n, Gemini, OpenRouter, Meta, YouTube, банки, брокери та інші API не викликалися.
- Паспорт не містить секретів, персональних фінансових показників або медичного вмісту; ніякі API credentials не створювалися.

## 13. Джерела істини для наступного оновлення

Починайте з цих локальних документів/коду й перевіряйте за профілем, не копіюйте застарілі обіцянки зі специфікацій:

- `config/agents/*.profile.json` — фактичні profile поля: activation, role/model status, capabilities, scopes, services, skills і live modes.
- `tools/export_permissions.py`, `docs/PERMISSIONS_MATRIX.md` — зведення profile permissions.
- `src/orchestrator.py`, `src/agent_platform/` — task routing, policy/dispatcher contracts.
- `deploy/docker-compose.yml`, `deploy/docker-compose.alice.yml`, `deploy/docker-compose.directors.yml`, `deploy/docker-compose.integrations.yml` — бажана topology; не proof of running containers.
- `docs/ALICE_RUNTIME.md`, `docs/AGENT_CONTAINERS.md`, `docs/DIRECTORS_DEPLOYMENT.md` — реалізаційні межі; звіряти з поточними профілями й відкритими рішеннями.
- `architect_core/ARCHITECT_WORKFLOW_CONTRACT.md`, `src/n8n_templates.py`, `src/agents/architect_n8n.py`, `eva_core/EVA_N8N_WORKFLOWS.md` — відповідно чинний контракт, локальні templates, mockable inactive-mount code і історичні workflow ideas.
- `src/agents/<agent>.py`, `src/agents/<agent>/` та відповідні `<agent>_core/` — actual local handlers vs draft spec.
- `docs/HANDOFF.md` — зверху останній handoff; старі нотатки не переписувати.

**Оновлення:** змінюйте Markdown-файл для нового зрізу, потім запускайте `python tools/md_to_pdf.py docs/SYSTEM_PASSPORT_2026-10-16.md`. Перевіряйте PDF extraction/посилання, дату й статуси. Нову production-перевірку записуйте окремо з конкретним середовищем, часовою міткою та фактичним результатом; не виводьте її з локального тесту.
