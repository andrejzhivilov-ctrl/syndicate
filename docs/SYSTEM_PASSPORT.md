# EVA SYNDICATE — технічний паспорт системи

Версія документа: 2026-10-15. Мова: українська. Репозиторій: https://github.com/andrejzhivilov-ctrl/syndicate. Документ описує стан коду цієї гілки, а не підтвердження запуску на production-сервері.

## 1. Для чого потрібен SYNDICATE

SYNDICATE — модульна система персональних і бізнес-асистентів. Вона поєднує координацію задач, знання, фінанси, навчання, здоров’я, медіа, мерч і кількісний аналіз. Виміряні дані мають джерело; без джерела повертається unavailable. Система не гарантує прибуток, ROI, точність медичних висновків чи безкоштовність зовнішніх моделей.

У маніфесті описано дев’ять директорів; у поточному config/agents є 12 профілів: до директорів додано KODEX та технічні ролі. Профілі підготовлені, але prepared_not_enabled не означає запущеного Hermes агента. Native Python workers уже виконують конкретні функції, окремо від повного Hermes control plane.

## 2. Архітектура і потоки

Оператор → захищений API → координатор LangGraph → профіль/дозволи → domain worker або integration worker → перевірений результат → журнал. Для критичних дій потрібне HITL. Device tokens відокремлені від master API key; новий integration route доступний лише master key.

PostgreSQL+pgvector зберігає системні дані та вектори; Redis підтримує короткостроковий стан; Vault зберігає секрети; n8n виконує погоджені workflows; Nginx/TLS забезпечує зовнішню межу. Для локальних domain records використовується SQLite на окремих volumes. BGE-M3 має 1024 виміри — інша embedding модель потребує узгодження індексу.

Ізоляція: окремі agent IDs, memory namespaces, AppRoles, API keys та volumes. Root filesystem контейнерів read-only; процеси UID1001; capability drop; ліміти CPU/RAM/PIDs. Не монтувати docker.sock і домашні директорії з ключами в агентні контейнери.

### Системні компоненти поза 12 профілями

Sentinel — перевірка команд/секретів і webhook HMAC; OrcVerifier — перевірка тверджень; Council — колективний розгляд рішень; ChangeRequests — погодження змін; Office Copilot — допоміжний офісний інструментарій; Floor2 Coordinator — контент/операції; Sensory Router — маршрутизація входів; Error Collector — помилки; Scheduler — заплановані задачі. Ці компоненти не слід рахувати як додаткових автономних директорів. Поверхи 3–6 зарезервовані; прапорець active у floor registry описує архітектуру, не health живого процесу.

## 3. Реалізовані інтеграції цього пакета

- skills.list / skills.read: бібліотека 21 pinned skills, із SHA256 і per-agent mappings; доступна в образі integration worker.
- hindsight.retain / recall / reflect: офіційні HTTP endpoints, власний bank syndicate-<agent>, PII redaction, bounded text/token budgets. Потрібні Hindsight та його LLM provider.
- omniroute.chat: OpenAI-compatible /chat/completions, дозволені моделі, PII redaction, без streaming. Потрібні provider accounts і перевірені квоти; gateway не надає безкоштовні токени сам по собі.
- actual.snapshot: офіційний @actual-app/api 26.10.0; дозволені account IDs; дати до 366 днів; integer minor units збережено; немає payment/mutation API.
- hyperframes.render: hyperframes 0.8.162, локальний Chromium/FFmpeg, операторський project ID, новий MP4 artifact. HTML/JS не приймаються через API; готуйте trusted project в agent volume.
- mcp.list / mcp.call: official MCP SDK 1.30.0 stdio initialize/list/call; host-owned argv/env, явний список tool names. Передача довільної shell-команди в payload неможлива. Поведінка конкретного MCP tool потребує власного дозволу й перевірки.

Захист transport: fixed startup endpoints, заборона redirects, bounded HTTP/process output, subprocess timeout і kill process group; credentials не передаються аргументами CLI. Інтеграційний журнал містить operation/agent/status, а не контент і секрети. Наявність health=ok означає готовність worker, не авторизацію всіх провайдерів.

## 4. Паспорт кожного агента

## ЄВА — координатор і персональний хаб

Приймає запити оператора, маршрутизує роботу, збирає брифінги та перевіряє впевненість. Це головний вхід до системи, а не власник необмежених прав.

### Реалізовані функції

- Маршрутизація через LangGraph і диспетчер задач
- Добовий брифінг із наданих звітів; відсутні дані позначаються
- Чернетки пошти, пошук та систематизація інформації
- Memory/Vault, оцінка confidence, Change Requests і HITL

### Необхідні сервіси й функції підключення

- PostgreSQL+pgvector: довгострокова пам’ять і журнал
- Redis: сесії/черги
- Vault AppRole і master API key
- LLM endpoint із дозволеним model ID

### Рекомендовані сервіси

- Telegram Bot API: вхідні команди/доставка після налаштування
- Google Workspace OAuth: Gmail drafts, Calendar, Drive
- OmniRoute: єдиний контрольований маршрут до моделей
- Hindsight: окрема пам’ять банку syndicate-eva
- ElevenLabs/Groq/OpenAI: голос лише після окремого налаштування

### Джерела даних

- Звіти директорів із джерелами та датами
- Власні документи оператора з мітками доступу
- Офіційна документація підключених сервісів

### Скіли та права

Власні draft skills: eva-humanizer, eva-summary, eva-deep-research, eva-skill-creator, eva-prompt-lab.

Встановлені upstream reference skills: grill-me, handoff, grilling, context-engineering, planning-breakdown, internal-comms, market-research.

Поточні capabilities: порожній список; default deny. Memory namespace: agents/eva.

### Порядок роботи та обмеження

Запит → дозволена задача → виконавець → перевірка → звіт. Пошта тільки draft. Не трактувати рекламні ціни/ROI з маніфесту як перевірені показники.

### Підключення на сервері

Створити окрему Vault policy/AppRole, API key і volume; перевірити потрібні джерела на synthetic даних. Внести лише необхідні grants у agents/eva/integrations; адреси/ключі задаються оператором. Запустити worker з SYNDICATE_INTEGRATION_AGENT=eva. Перевірити 401 без ключа, правильний agent у відповіді й відмову на непризначену операцію. Увімкнення зовнішніх дій — окремий крок після функціонального тесту.

## АРХІТЕКТОР — інженерія та автоматизація

Проєктує агентів, workflow та інтеграції; готує зміни до перевірки. Завдання надходять від Андрія згідно з профілем.

### Реалізовані функції

- Blueprint нового агента і перевірка готовності
- Проєктування n8n workflow та mount після HITL
- Аналіз помилок, code verification і пропозиції self-healing
- Архітектурні ADR, контроль меж API та залежностей

### Необхідні сервіси й функції підключення

- Git-репозиторій і локальний test runner
- Vault для service credentials
- n8n API для фактичного mount workflow; без нього лише проєктування

### Рекомендовані сервіси

- Understand-Anything: граф коду як окремий developer plugin
- Skill Seekers MCP: перетворення джерел у knowledge assets
- REA MCP: аналіз власних артефактів
- context-mode MCP: вибірка контексту
- CI/CD runner, registry образів, error monitoring

### Джерела даних

- AGENTS.md, HANDOFF, специфікації та API contract
- Офіційні API docs із pinned revisions
- CI logs і відтворювані failing tests

### Скіли та права

Власні draft skills: architect-new-agent, architect-n8n-link, architect-self-learn.

Встановлені upstream reference skills: grill-me, handoff, grilling, api-and-interface-design, debugging-and-error-recovery, context-engineering, documentation-and-adrs, source-driven-development, test-driven-development, planning-breakdown, ponytail, replica-recon, agent-security-hardening.

Поточні capabilities: n8n.workflow.design, n8n.workflow.mount. Memory namespace: agents/architect.

### Порядок роботи та обмеження

Спочатку план і контракт, потім мінімальна реалізація, тести, PR. Новий сервіс або розширення прав не випливає з тексту стороннього скіла.

### Підключення на сервері

Створити окрему Vault policy/AppRole, API key і volume; перевірити потрібні джерела на synthetic даних. Внести лише необхідні grants у agents/architect/integrations; адреси/ключі задаються оператором. Запустити worker з SYNDICATE_INTEGRATION_AGENT=architect. Перевірити 401 без ключа, правильний agent у відповіді й відмову на непризначену операцію. Увімкнення зовнішніх дій — окремий крок після функціонального тесту.

## МАРШАЛ — безпека та контроль

Аналізує стан безпеки, пропозиції змін і сторонні скіли. Не підміняє рішення оператора.

### Реалізовані функції

- No-LLM SkillSpector scan із чесними risk/findings/completeness
- Звіти безпеки, read-only observations та readiness checks
- Обробка HITL-подій і security proposals
- Перевірка меж доступу, секретів і небезпечних команд

### Необхідні сервіси й функції підключення

- Vault та окремий профіль доступу
- SkillSpector Python3.12 для перевірки сторонніх skills
- Журнал аудиту і доступ до дозволених system observations

### Рекомендовані сервіси

- Prometheus/Grafana/Loki: спостереження
- Tetragon/Falco: події ядра на сумісному Linux-хості
- BDC Bridge: зовнішня оцінка workflow за окремим account/token
- Geo-sleuth: лише окремий погоджений сценарій геолокації
- Compact Guard: developer hook для підтримуваного Claude Code

### Джерела даних

- Структуровані журнали без секретів
- Звіти SkillSpector, підписи/контрольні суми
- CVE та advisory виробників

### Скіли та права

Власні draft skills: не задані в профілі.

Встановлені upstream reference skills: replica-test, agent-security-hardening.

Поточні capabilities: порожній список; default deny. Memory namespace: agents/marshal.

### Порядок роботи та обмеження

Спочатку доказ і оцінка, потім пропозиція. Scan exit0 не означає відсутність ризику. Network scans, host control і геолокація не активовані автоматично.

### Підключення на сервері

Створити окрему Vault policy/AppRole, API key і volume; перевірити потрібні джерела на synthetic даних. Внести лише необхідні grants у agents/marshal/integrations; адреси/ключі задаються оператором. Запустити worker з SYNDICATE_INTEGRATION_AGENT=marshal. Перевірити 401 без ключа, правильний agent у відповіді й відмову на непризначену операцію. Увімкнення зовнішніх дій — окремий крок після функціонального тесту.

## ФІН — фінанси та казначейство

Веде фінансовий облік, перевіряє кошти, витрати, runway і звіти. Не вигадує залишки й не здійснює платежі самостійно.

### Реалізовані функції

- Expense ledger і reconciliation чеків
- Funds check, планування, runway та аудит кошика
- Локальні PDF/XLSX/CSV звіти
- Token-cost guard, FX-monitor і tax-calendar на наданих джерелах
- Actual snapshot: читання дозволеного рахунку за діапазон дат

### Необхідні сервіси й функції підключення

- Реальне джерело транзакцій або перевірений імпорт
- Vault і локальне persistent сховище
- Actual server + budget sync ID + account IDs для actual.snapshot
- Node24 і @actual-app/api 26.10.0 у integration image

### Рекомендовані сервіси

- Google Sheets/Drive для контрольованого експорту
- Офіційний read-only banking API; без BankID automation
- НБУ: курси валют; податкова/офіційні юридичні джерела
- Hindsight: контекст рішень без немаскованих платіжних реквізитів

### Джерела даних

- Actual budget, банківські виписки, чеки
- Офіційні FX feeds і дати курсів
- Рахунки провайдерів LLM і тарифні документи

### Скіли та права

Власні draft skills: fin-funds-check, fin-sources, fin-planner, fin-expense-ledger, fin-buttons, fin-report-full, fin-report-export, fin-basket-audit, fin-receipt-reconcile, fin-runway, fin-token-guard, fin-fx-monitor, fin-tax-calendar, fin-law-scan.

Встановлені upstream reference skills: internal-comms, scientific-critical-thinking, behavioral-finance, market-research.

Поточні capabilities: fin.dispatch.eva_basket, fin.funds_check, fin.reports.local, fin.docs.local_generate. Memory namespace: agents/fin.

### Порядок роботи та обмеження

actual.snapshot з account/start/end → перевірка currency/minor units → reconciliation → локальний звіт. Actual SDK робить технічний sync, але адаптер не викликає створення/редагування транзакцій або платежів.

### Підключення на сервері

Створити окрему Vault policy/AppRole, API key і volume; перевірити потрібні джерела на synthetic даних. Внести лише необхідні grants у agents/fin/integrations; адреси/ключі задаються оператором. Запустити worker з SYNDICATE_INTEGRATION_AGENT=fin. Перевірити 401 без ключа, правильний agent у відповіді й відмову на непризначену операцію. Увімкнення зовнішніх дій — окремий крок після функціонального тесту.

## ДОК — здоров’я, харчування та енергія

Систематизує надані показники здоров’я, вправи, харчування та нагадування. Не замінює лікаря і не створює вимірювань із припущень.

### Реалізовані функції

- Перевірка показників і підготовка брифінгів
- Каталог вправ і планування харчування
- Список покупок із підтверджених рекомендацій
- Нагадування о 13:10 та 19:10: логіка є, доставка потребує scheduler/channel
- Робота з knowledge archive відповідно до andrii_protected

### Необхідні сервіси й функції підключення

- Перевірені персональні дані/вимірювання
- Захищене сховище та ізольований namespace
- Scheduler і канал доставки для фактичних нагадувань

### Рекомендовані сервіси

- Telegram Bot API
- Локальний OCR/транскрибація для аналізів
- Вендоровані free-exercise-db/open-exercisedb
- Офіційні медичні бази/настанови
- Hindsight лише після визначення retention та privacy

### Джерела даних

- Дані, надані користувачем
- Медичні висновки з датами та походженням
- Офіційні клінічні настанови, література з evidence grading

### Скіли та права

Власні draft skills: не задані в профілі.

Встановлені upstream reference skills: scientific-critical-thinking.

Поточні capabilities: порожній список; default deny. Memory namespace: agents/doc.

### Порядок роботи та обмеження

Отримати показник → зберегти джерело/дату → перевірити одиниці → пояснити. Пороги, яких оператор не задав, не вважати затвердженими; складу добавок без даних немає.

### Підключення на сервері

Створити окрему Vault policy/AppRole, API key і volume; перевірити потрібні джерела на synthetic даних. Внести лише необхідні grants у agents/doc/integrations; адреси/ключі задаються оператором. Запустити worker з SYNDICATE_INTEGRATION_AGENT=doc. Перевірити 401 без ключа, правильний agent у відповіді й відмову на непризначену операцію. Увімкнення зовнішніх дій — окремий крок після функціонального тесту.

## КІРА — навчання та Academy

Підтримує навчальні траєкторії, каталог матеріалів та сократичний діалог.

### Реалізовані функції

- Каталог і вибір навчального матеріалу
- Socratic dialogue і пояснення
- Навчальні сесії та фіксація прогресу
- Оцінка якості наукових тверджень через reference skill

### Необхідні сервіси й функції підключення

- Джерела курсу та визначена навчальна мета
- Ізольоване сховище сесій
- LLM endpoint для діалогу

### Рекомендовані сервіси

- KODEX/Skill Seekers: підготовка навчальних джерел
- Hindsight: пам’ять навчального прогресу
- Telegram/клієнтський застосунок
- Офіційні освітні ресурси та LMS API за потреби

### Джерела даних

- Підручники/документація з ліцензіями
- Матеріали користувача
- Результати фактично виконаних вправ

### Скіли та права

Власні draft skills: не задані в профілі.

Встановлені upstream reference skills: scientific-critical-thinking.

Поточні capabilities: порожній список; default deny. Memory namespace: agents/kira.

### Порядок роботи та обмеження

Мета → діагностика на наданих відповідях → пояснення/питання → вправа → перевірка. Не оголошувати засвоєння теми без результату перевірки.

### Підключення на сервері

Створити окрему Vault policy/AppRole, API key і volume; перевірити потрібні джерела на synthetic даних. Внести лише необхідні grants у agents/kira/integrations; адреси/ключі задаються оператором. Запустити worker з SYNDICATE_INTEGRATION_AGENT=kira. Перевірити 401 без ключа, правильний agent у відповіді й відмову на непризначену операцію. Увімкнення зовнішніх дій — окремий крок після функціонального тесту.

## СЕМ — ринки та інвестиції

Готує ринкові дослідження, інвестиційні пропозиції та журнал. Реальні угоди вимагають окремого дозволу.

### Реалізовані функції

- Confluence та risk guard
- Paper/demo lab і журнал висновків
- Обговорення інвестицій та portfolio analysis
- Broker readiness і bounded proposals
- Behavioral-finance як методика, не гарантія alpha

### Необхідні сервіси й функції підключення

- Достовірні market data з часовими мітками
- Визначені ризик-ліміти та paper account
- Vault для provider credentials

### Рекомендовані сервіси

- IBKR/TWS або Gateway для підтвердженої брокерської інтеграції
- MT5: окремий сумісний gateway; не native Linux assumption
- CCXT/офіційний exchange API з read-only keys на старті
- CFTC COT, FRED, SEC filings, DefiLlama
- Hindsight: журнал рішень; Telegram для ручних погоджень

### Джерела даних

- Ринкові котирування й historical datasets із ліцензією
- Офіційні звіти емітентів
- Фактичні trade/fill records

### Скіли та права

Власні draft skills: sam-confluence, sam-risk-guard, sam-journal, sam-demo-lab, sam-invest-discuss.

Встановлені upstream reference skills: scientific-critical-thinking, behavioral-finance, market-research.

Поточні capabilities: порожній список; default deny. Memory namespace: agents/sam.

### Порядок роботи та обмеження

Дані → перевірка свіжості → дослідження → backtest/paper → пропозиція → HITL. Vibe-Trading як окремий сервіс не підключено; перенесено behavioral-finance guidance.

### Підключення на сервері

Створити окрему Vault policy/AppRole, API key і volume; перевірити потрібні джерела на synthetic даних. Внести лише необхідні grants у agents/sam/integrations; адреси/ключі задаються оператором. Запустити worker з SYNDICATE_INTEGRATION_AGENT=sam. Перевірити 401 без ключа, правильний agent у відповіді й відмову на непризначену операцію. Увімкнення зовнішніх дій — окремий крок після функціонального тесту.

## KODEX — архів і пам’ять

Організовує знання й архіви, зберігає provenance та контролює мітки особистих файлів.

### Реалізовані функції

- Читання архівів і робота з неміченими файлами
- Переміщення мічених файлів; зміна/видалення тільки з дозволом
- Звіти про дії для Єви
- Підтримка Telegram ingress та файлів
- Hindsight retain/recall/reflect через власний bank

### Необхідні сервіси й функції підключення

- Persistent archive і резервне копіювання
- Мітки andrii_protected та trusted identity завантажувача
- Vault і agent namespace
- Hindsight endpoint та LLM backend для нових memory operations

### Рекомендовані сервіси

- Skill Seekers MCP для knowledge conversion
- Obsidian/Drive через офіційні API
- OCR та ASR локально
- Object storage для великих медіа
- NotebookLM як ручний workflow до появи перевіреного API

### Джерела даних

- Особисті файли з походженням і мітками
- Ліцензовані knowledge sources
- Журнали дій і фактичні результати задач

### Скіли та права

Власні draft skills: не задані в профілі.

Встановлені upstream reference skills: handoff, context-engineering, documentation-and-adrs, internal-comms.

Поточні capabilities: kodex.archive.read_all, kodex.archive.write_unlabeled, kodex.labeled.move, kodex.labeled.change_with_andrii_permission, kodex.report.eva. Memory namespace: agents/kodex.

### Порядок роботи та обмеження

Імпорт → мітка/доступ → індекс → bounded recall → звіт. Hindsight не робить автоматичну міграцію старого архіву й не замінює source-of-truth Postgres.

### Підключення на сервері

Створити окрему Vault policy/AppRole, API key і volume; перевірити потрібні джерела на synthetic даних. Внести лише необхідні grants у agents/kodex/integrations; адреси/ключі задаються оператором. Запустити worker з SYNDICATE_INTEGRATION_AGENT=kodex. Перевірити 401 без ключа, правильний agent у відповіді й відмову на непризначену операцію. Увімкнення зовнішніх дій — окремий крок після функціонального тесту.

## ANTIGRAVITY — клієнтський продукт

Профіль для розробки клієнтського застосунку й UX. Не автономний production-директор із необмеженим доступом.

### Реалізовані функції

- Клієнтська інтеграція з apps/shared/api-contract
- UI/UX, frontend design, accessibility
- Recon власного/дозволеного продукту та QA
- Робота через PR і узгоджені API

### Необхідні сервіси й функції підключення

- Git checkout, Node toolchain відповідно до apps/
- Актуальний API contract
- Dev backend і test fixtures

### Рекомендовані сервіси

- OpenDesign: окремий workspace для прототипів
- agent-browser у відповідному browser sandbox
- taste-skill після перевірки JS assets/inspector
- Playwright/accessibility tooling для власного продукту

### Джерела даних

- Специфікації екранів та API contract
- Власні дизайн-матеріали
- Відтворені помилки й user flows

### Скіли та права

Власні draft skills: не задані в профілі.

Встановлені upstream reference skills: handoff, api-and-interface-design, debugging-and-error-recovery, context-engineering, source-driven-development, test-driven-development, ponytail, frontend-design, replica-recon, replica-test.

Поточні capabilities: порожній список; default deny. Memory namespace: agents/antigravity.

### Порядок роботи та обмеження

Contract → UI → інтеграція → перевірка станів/error/accessibility → PR. Код apps/ не переписувався цією backend інтеграцією; змінено лише генерований контракт.

### Підключення на сервері

Створити окрему Vault policy/AppRole, API key і volume; перевірити потрібні джерела на synthetic даних. Внести лише необхідні grants у agents/antigravity/integrations; адреси/ключі задаються оператором. Запустити worker з SYNDICATE_INTEGRATION_AGENT=antigravity. Перевірити 401 без ключа, правильний agent у відповіді й відмову на непризначену операцію. Увімкнення зовнішніх дій — окремий крок після функціонального тесту.

## ОСКАР — медіа та аудиторія

Готує контент для трьох брендів: Marcus Vance, Nicole “Nika” Sterling і Julian Pierce.

### Реалізовані функції

- Tri-LLM router: Grok creative, Gemini research, Haiku classification
- Імпорт/дедуплікація коментарів і YouTube read adapter
- Editorial drafts, відповіді, newsletters і pending queue
- PNG thumbnail, SVG diagram, email metrics із наданих чисел
- HyperFrames: рендер оператором підготовленого HTML-проєкту в MP4

### Необхідні сервіси й функції підключення

- Persistent volume для drafts/media/SQLite
- Vault per-agent keys; хоча б один provider для LLM-функцій
- YouTube Data API key для живого збору коментарів
- HyperFrames0.8.162, Chromium, FFmpeg для render
- Права на вихідні медіа та матеріали

### Рекомендовані сервіси

- OmniRoute для контрольованої маршрутизації
- Офіційні social APIs для потрібних платформ
- Email-провайдер для чернеток/метрик; send окремо
- LivePortrait/ASR/TTS як окремі перевірені конвеєри
- OpenDesign для дизайн-проєктів

### Джерела даних

- Власні transcripts, comments і brand voice samples
- Офіційні метрики каналів
- Ліцензовані зображення, шрифти й аудіо

### Скіли та права

Власні draft skills: oscar-editorial, oscar-audience-research, oscar-community.

Встановлені upstream reference skills: internal-comms, frontend-design, content-engine, market-research, brand-voice.

Поточні capabilities: порожній список; default deny. Memory namespace: agents/oscar.

### Порядок роботи та обмеження

Джерело → персона → draft → перевірка → render → preview → погодження публікації. Worker не публікує ролики. Повний LivePortrait та subscriber DB не реалізовані.

### Підключення на сервері

Створити окрему Vault policy/AppRole, API key і volume; перевірити потрібні джерела на synthetic даних. Внести лише необхідні grants у agents/oscar/integrations; адреси/ключі задаються оператором. Запустити worker з SYNDICATE_INTEGRATION_AGENT=oscar. Перевірити 401 без ключа, правильний agent у відповіді й відмову на непризначену операцію. Увімкнення зовнішніх дій — окремий крок після функціонального тесту.

## ТАЙЛЕР — POD та персоналізований мерч

Розраховує економіку й готує концепти преміального мерчу з мінімальною чистою маржею 35%.

### Реалізовані функції

- Decimal margin guard із доставкою, податками й комісіями
- Premium blank allowlist та перевірка evidence прав на дизайн
- Concierge concept: PNG3600×4500 300DPI та схематичний preview
- Порівняння наданих quotes Printify/Printful/Gelato/Prodigi
- Pinterest drafts і аналіз наданих відгуків

### Необхідні сервіси й функції підключення

- Підтверджені supplier quotes, blank costs, shipping/tax policy
- Докази ліцензій на artwork/fonts/trademarks
- Persistent storage для PNG/order concepts
- Storefront/payment/factory account для фактичного продажу — окреме підключення

### Рекомендовані сервіси

- Printful/Printify/Gelato/Prodigi APIs: обрати потрібні
- Stripe Checkout/webhooks для платежів після реалізації transactional flow
- Pinterest developer app для дозволеного publishing
- OpenDesign/дизайн-сервіси для макетів
- Fin/Actual для звірки фактичних надходжень

### Джерела даних

- Офіційні каталоги supplier і актуальні тарифи
- Власні customer briefs/затверджені дизайни
- Офіційні trademark databases і права на шрифти

### Скіли та права

Власні draft skills: tyler-margin-quality, tyler-concierge, tyler-pinterest.

Встановлені upstream reference skills: frontend-design, replica-recon, content-engine, market-research, brand-voice.

Поточні capabilities: порожній список; default deny. Memory namespace: agents/tyler.

### Порядок роботи та обмеження

Brief → права/DPI → cost/margin → preview → approval. Зараз немає production storefront/live-chat, оплати, фабричного submit або Pinterest publish; підготовка worker не видається за повний магазин.

### Підключення на сервері

Створити окрему Vault policy/AppRole, API key і volume; перевірити потрібні джерела на synthetic даних. Внести лише необхідні grants у agents/tyler/integrations; адреси/ключі задаються оператором. Запустити worker з SYNDICATE_INTEGRATION_AGENT=tyler. Перевірити 401 без ключа, правильний agent у відповіді й відмову на непризначену операцію. Увімкнення зовнішніх дій — окремий крок після функціонального тесту.

## ДЖЕК — спортивний, кіберспортивний та poker quant

Розраховує ймовірності, EV і paper risk. Прибутковість потребує незалежної перевірки на реальних даних.

### Реалізовані функції

- Football Poisson/Dixon–Coles, basketball possessions baseline
- Tennis IID-point Markov set, independent-map esports series
- Poker chip EV та ICM до 9 учасників
- EV≥4.5%, quarter-Kelly, event cap1% default /2.5% max
- Перевірка свіжості odds, vig removal, paper settlement/anti-tilt
- The Odds API scout з чесним bookmaker coverage

### Необхідні сервіси й функції підключення

- Odds API account для живих ліній
- Джерела historical outcomes та калібрування
- Визначений paper bankroll і risk limits
- SQLite persistent volume і UTC clock

### Рекомендовані сервіси

- Офіційні/ліцензовані Pinnacle/Betfair дані
- PariMatch/Vbet: лише після перевірки доступного легального API/умов
- Статистика футболу/xG, NBA, tennis, CS2/Dota
- Telegram delivery/approval після налаштування каналу
- Hindsight для журналу висновків

### Джерела даних

- Timestamped odds, результати матчів, closing lines
- Підтверджені статистичні datasets
- Paper ledger і фактичні settlements

### Скіли та права

Власні draft skills: jack-quant-models, jack-paper-risk, jack-line-scout.

Встановлені upstream reference skills: scientific-critical-thinking, behavioral-finance.

Поточні capabilities: порожній список; default deny. Memory namespace: agents/jack.

### Порядок роботи та обмеження

Лінія → freshness → calibrated probability → EV → capped stake → paper entry → settle → аудит. Не робить реальних ставок; basketball baseline не є навченою regression, tennis engine моделює set, не повний матч.

### Підключення на сервері

Створити окрему Vault policy/AppRole, API key і volume; перевірити потрібні джерела на synthetic даних. Внести лише необхідні grants у agents/jack/integrations; адреси/ключі задаються оператором. Запустити worker з SYNDICATE_INTEGRATION_AGENT=jack. Перевірити 401 без ключа, правильний agent у відповіді й відмову на непризначену операцію. Увімкнення зовнішніх дій — окремий крок після функціонального тесту.

## 5. Скіли: встановлення, використання й аудит

SkillLibrary — бібліотека інструкцій, не механізм надання прав. Роль може завантажити тільки призначений скіл і відомий ресурс; перевіряються hashes, розмір, symlinks і межі шляху. Умови/allowed-tools стороннього SKILL.md не перекривають політику системи.

SkillSpector2.12.0:21 встановлений скіл,21 finding,11 complete і 10 incomplete reports. Findings розглянуті в контексті; є спрацювання на приклади й заборони. security-and-hardening вилучено після score100/partial analysis. Це не сертифікація безпеки. Збережені config/skill_scan_report.json, skill_library.json та skill_sources_audit.json. Перед оновленням перевірити нову версію/ліцензію, перегенерувати hashes і пройти regression gate.

### grill-me

Джерело: https://github.com/mattpocock/skills

Commit: 49dd158d1076134a641b33efb035946536778336. Ліцензія: MIT. Агенти: eva, architect. Шлях: skills/vendor/mattpocock/skills/skills/productivity/grill-me/SKILL.md.

### handoff

Джерело: https://github.com/mattpocock/skills

Commit: 49dd158d1076134a641b33efb035946536778336. Ліцензія: MIT. Агенти: eva, architect, kodex, antigravity. Шлях: skills/vendor/mattpocock/skills/skills/productivity/handoff/SKILL.md.

### grilling

Джерело: https://github.com/mattpocock/skills

Commit: 49dd158d1076134a641b33efb035946536778336. Ліцензія: MIT. Агенти: eva, architect. Шлях: skills/vendor/mattpocock/skills/skills/productivity/grilling/SKILL.md.

### api-and-interface-design

Джерело: https://github.com/addyosmani/agent-skills

Commit: aeac41d4d005999432bb7312f7ff06383a91d59d. Ліцензія: MIT. Агенти: architect, antigravity. Шлях: skills/vendor/addyosmani/agent-skills/skills/api-and-interface-design/SKILL.md.

### debugging-and-error-recovery

Джерело: https://github.com/addyosmani/agent-skills

Commit: aeac41d4d005999432bb7312f7ff06383a91d59d. Ліцензія: MIT. Агенти: architect, antigravity. Шлях: skills/vendor/addyosmani/agent-skills/skills/debugging-and-error-recovery/SKILL.md.

### context-engineering

Джерело: https://github.com/addyosmani/agent-skills

Commit: aeac41d4d005999432bb7312f7ff06383a91d59d. Ліцензія: MIT. Агенти: eva, architect, kodex, antigravity. Шлях: skills/vendor/addyosmani/agent-skills/skills/context-engineering/SKILL.md.

### documentation-and-adrs

Джерело: https://github.com/addyosmani/agent-skills

Commit: aeac41d4d005999432bb7312f7ff06383a91d59d. Ліцензія: MIT. Агенти: architect, kodex. Шлях: skills/vendor/addyosmani/agent-skills/skills/documentation-and-adrs/SKILL.md.

### source-driven-development

Джерело: https://github.com/addyosmani/agent-skills

Commit: aeac41d4d005999432bb7312f7ff06383a91d59d. Ліцензія: MIT. Агенти: architect, antigravity. Шлях: skills/vendor/addyosmani/agent-skills/skills/source-driven-development/SKILL.md.

### test-driven-development

Джерело: https://github.com/addyosmani/agent-skills

Commit: aeac41d4d005999432bb7312f7ff06383a91d59d. Ліцензія: MIT. Агенти: architect, antigravity. Шлях: skills/vendor/addyosmani/agent-skills/skills/test-driven-development/SKILL.md.

### planning-breakdown

Джерело: https://github.com/addyosmani/agent-skills

Commit: aeac41d4d005999432bb7312f7ff06383a91d59d. Ліцензія: MIT. Агенти: eva, architect. Шлях: skills/vendor/addyosmani/agent-skills/skills/planning-and-task-breakdown/SKILL.md.

### ponytail

Джерело: https://github.com/DietrichGebert/ponytail

Commit: 84740e3d344b69b4a133201fa519eb37a62a2b2a. Ліцензія: MIT. Агенти: architect, antigravity. Шлях: skills/vendor/DietrichGebert/ponytail/skills/ponytail/SKILL.md.

### internal-comms

Джерело: https://github.com/anthropics/skills

Commit: dbd4588f9e1033efb41dad4bef2f7947c8993d44. Ліцензія: Apache-2.0 (skill-local LICENSE.txt). Агенти: eva, fin, kodex, oscar. Шлях: skills/vendor/anthropics/skills/skills/internal-comms/SKILL.md.

### frontend-design

Джерело: https://github.com/anthropics/skills

Commit: dbd4588f9e1033efb41dad4bef2f7947c8993d44. Ліцензія: Apache-2.0 (skill-local LICENSE.txt). Агенти: antigravity, tyler, oscar. Шлях: skills/vendor/anthropics/skills/skills/frontend-design/SKILL.md.

### scientific-critical-thinking

Джерело: https://github.com/K-Dense-AI/scientific-agent-skills

Commit: a1043ef544e3a100c28e70a736b6cf32554d0677. Ліцензія: MIT. Агенти: doc, kira, jack, sam, fin. Шлях: skills/vendor/K-Dense-AI/scientific-agent-skills/skills/scientific-critical-thinking/SKILL.md.

### behavioral-finance

Джерело: https://github.com/HKUDS/Vibe-Trading

Commit: 29aa084fb7866087c612ddd55ef5449824374e22. Ліцензія: MIT. Агенти: sam, fin, jack. Шлях: skills/vendor/HKUDS/Vibe-Trading/agent/src/skills/behavioral-finance/SKILL.md.

### replica-recon

Джерело: https://github.com/Jakeschincariol/replica-skill

Commit: 77c9436fb3d18c3d58169efb8caf4fe906b0dc51. Ліцензія: MIT. Агенти: architect, antigravity, tyler. Шлях: skills/vendor/Jakeschincariol/replica-skill/replica-recon/SKILL.md.

### replica-test

Джерело: https://github.com/Jakeschincariol/replica-skill

Commit: 77c9436fb3d18c3d58169efb8caf4fe906b0dc51. Ліцензія: MIT. Агенти: antigravity, marshal. Шлях: skills/vendor/Jakeschincariol/replica-skill/replica-test/SKILL.md.

### content-engine

Джерело: https://github.com/affaan-m/ECC

Commit: b92f181b3b748d1abbc2afd94af6aa7d8c8fca29. Ліцензія: MIT. Агенти: oscar, tyler. Шлях: skills/vendor/affaan-m/ECC/skills/content-engine/SKILL.md.

### market-research

Джерело: https://github.com/affaan-m/ECC

Commit: b92f181b3b748d1abbc2afd94af6aa7d8c8fca29. Ліцензія: MIT. Агенти: eva, fin, sam, oscar, tyler. Шлях: skills/vendor/affaan-m/ECC/skills/market-research/SKILL.md.

### agent-security-hardening

Джерело: https://github.com/affaan-m/ECC

Commit: b92f181b3b748d1abbc2afd94af6aa7d8c8fca29. Ліцензія: MIT. Агенти: marshal, architect. Шлях: skills/vendor/affaan-m/ECC/skills/agent-security-hardening/SKILL.md.

### brand-voice

Джерело: https://github.com/affaan-m/ECC

Commit: b92f181b3b748d1abbc2afd94af6aa7d8c8fca29. Ліцензія: MIT. Агенти: oscar, tyler. Шлях: skills/vendor/affaan-m/ECC/skills/brand-voice/SKILL.md.

## 6. Усі 26 репозиторіїв: роль і межі підключення

### Lum1104/Understand-Anything

https://github.com/Egonex-AI/Understand-Anything

Ліцензія: MIT. Закріплена ревізія: f2d0164f72fe678805c34245a6df36acededfebd.

GitHub перенаправляє на Egonex-AI. Плагін має граф, dashboard та власні залежності; потрібен окремий запуск і адаптер, копія SKILL.md не створить карту коду.

### nexu-io/open-design

https://github.com/nexu-io/open-design

Ліцензія: Apache-2.0. Закріплена ревізія: 7abd6fc2b11987c3940eb4ffc461478ff37c0b33.

Окремий collaborative workspace/daemon; не замінюємо наявний apps/. Потрібні preview/export smoke tests та окрема конфігурація.

### mattpocock/skills

https://github.com/mattpocock/skills

Ліцензія: MIT. Закріплена ревізія: 49dd158d1076134a641b33efb035946536778336.

Встановлено grill-me разом із залежністю grilling та handoff. Інтерв’ю лише коли потрібне користувачу; інструкції делегування не є дозволом запускати агентів.

### JuliusBrussee/caveman

https://github.com/JuliusBrussee/caveman

Ліцензія: Apache-2.0. Закріплена ревізія: d262ab3882952a59312ff3537cd86d894523c5ab.

Стиль може втрачати пояснення та змінювати поведінку всієї сесії. CLI також змінює налаштування/проксі. Стислість забезпечується без глобального переписування інструкцій.

### yusufkaraaslan/Skill_Seekers

https://github.com/yusufkaraaslan/Skill_Seekers

Ліцензія: MIT. Закріплена ревізія: 5b5d8dfca263fa76e6daae9f292890b311ef36aa.

SKILL.md очікує MCP із 40 інструментами; він тут не налаштований. Генерацію знань слід запускати окремо з перевіркою джерел, ліцензій та PII.

### heygen-com/hyperframes

https://github.com/heygen-com/hyperframes

Ліцензія: Apache-2.0. Закріплена ревізія: cea8aa8a7dee9d669e47e4b488213008bbe305cd.

Переглянуто hyperframes-core та pr-to-video: залежності на sibling skills, CLI/render та frame workers. Потрібен цілісний окремий відеоконвеєр; два файли не дадуть робочий рендер.

### leonxlnx/taste-skill

https://github.com/Leonxlnx/taste-skill

Ліцензія: MIT. Закріплена ревізія: f624f37a8c650b9cc550253104925efe4c8de246.

Поточний v2 містить Node scripts, завантаження зображень і browser inspector. Потребує окремої перевірки JS та браузерного середовища; базовий дизайн покрито frontend-design.

### vercel-labs/agent-browser

https://github.com/vercel-labs/agent-browser

Ліцензія: Apache-2.0. Закріплена ревізія: dac13bb87468fe9d74a040d862720f6cc17a9565.

SKILL.md тепер є bootstrap для CLI skills get core. Для цієї пісочниці використовується coderabbit-agent-browser; production browser isolation і tool gateway ще не підключені.

### mksglu/context-mode

https://github.com/mksglu/context-mode

Ліцензія: NOASSERTION. Закріплена ревізія: 40813fe886798bad07c69a43d2ae00a52b4b934d.

MCP та hooks із Node >=22.5; LICENSE — Elastic License 2.0, не MIT. Потрібна окрема інтеграція, збереження помилок і аудит routing hooks.

### ddavv1d/compact-guard-plugin

https://github.com/ddavv1d/compact-guard-plugin

Ліцензія: MIT. Закріплена ревізія: 7dcda79f97957e9c8ad2ab02e25a14d5be4c8cbb.

Claude Code hooks, Node >=20; не універсальний Hermes skill. Наявний validation record зберігає помилки; production hooks ще не інтегровані.

### malishomen/bdc-bridge-passport

https://github.com/malishomen/bdc-bridge-passport

Ліцензія: MIT. Закріплена ревізія: fdf684b54688c6c937984183b010e85ef49d0757.

Starter kit для зовнішнього BDC verdict API, не набір скілів. Потрібні account/token та окреме рішення щодо надсилання workflow evidence.

### actualbudget/actual

https://github.com/actualbudget/actual

Ліцензія: MIT. Закріплена ревізія: d5d6035a8f5867717a80635d270fbe64e370ea08.

Повноцінний бюджетний застосунок, Node і сховище/sync. Його .claude skills призначені для розробки Actual. Наступна інтеграція: read-only імпорт транзакцій із reconciliation; баланс не вигадувати.

### oriveo/oriveo

https://github.com/oriveo/oriveo

Ліцензія: AGPL-3.0. Закріплена ревізія: 284505910591ccaa2cbf81d352138db9afb9cb4a.

Окремий BYOK клієнт, AGPL-3.0. Не дублюємо наявний клієнт та не переносимо код без плану ліцензій і синхронізації.

### vectorize-io/hindsight

https://github.com/vectorize-io/hindsight

Ліцензія: MIT. Закріплена ревізія: 9a499b1759084a86598eff8af30ed59f7354e76c.

Сервіс retain/recall/reflect; потрібні isolated banks, PII redaction, retention та перевірка provider costs. Наявну пам’ять автоматично не мігрували.

### Oldcircle/geo-sleuth

https://github.com/Oldcircle/geo-sleuth

Ліцензія: MIT. Закріплена ревізія: 836d70eea196b194391017e6e018e04ccc85aaa4.

Скіл містить OCR, reverse image search, OSM, CLIP/DINO та мережеві скрипти. Потрібні окремі залежності й дозволи на передавання фото; геолокація в профілі лишається вимкненою.

### Jakeschincariol/replica-skill

https://github.com/Jakeschincariol/replica-skill

Ліцензія: MIT. Закріплена ревізія: 77c9436fb3d18c3d58169efb8caf4fe906b0dc51.

Встановлено replica-recon та replica-test з шаблонами. Лише дослідження функцій і перевірка власного застосунку; браузерні тести не запускались цим встановленням.

### DietrichGebert/ponytail

https://github.com/DietrichGebert/ponytail

Ліцензія: MIT. Закріплена ревізія: 84740e3d344b69b4a133201fa519eb37a62a2b2a.

Встановлено основну інструкцію мінімальних повних змін, без CLI та session hooks.

### diegosouzapw/OmniRoute

https://github.com/diegosouzapw/OmniRoute

Ліцензія: MIT. Закріплена ревізія: c4d1f3edabdcc7e3e51c2c90e1d36859bbc560a1.

Gateway потребує окремого сервісу, provider accounts, allowlist та перевірки fallback/PII. Безкоштовний код не означає безкоштовні моделі або гарантовані квоти.

### addyosmani/agent-skills

https://github.com/addyosmani/agent-skills

Ліцензія: MIT. Закріплена ревізія: aeac41d4d005999432bb7312f7ff06383a91d59d.

Сім engineering skills; security-and-hardening вилучено після SkillSpector score 100 та неповного static analysis.

### anthropics/skills

https://github.com/anthropics/skills

Ліцензія: перевіряється для конкретного skill. Закріплена ревізія: dbd4588f9e1033efb41dad4bef2f7947c8993d44.

internal-comms та frontend-design мають локальні Apache-2.0 LICENSE. Office document skills мають інші source-available умови; їх не вендорили.

### Shubhamsaboo/awesome-llm-apps

https://github.com/Shubhamsaboo/awesome-llm-apps

Ліцензія: Apache-2.0. Закріплена ревізія: 4bf51ab704fb2c5b3803cd5191b30d7dcdb51dc2.

Каталог прикладів і окремих skills. Не переносимо демонстраційні оркестратори, їхні провайдери та гаманці в production; інженерні функції вже покриті вибраними skills.

### K-Dense-AI/scientific-agent-skills

https://github.com/K-Dense-AI/scientific-agent-skills

Ліцензія: MIT. Закріплена ревізія: a1043ef544e3a100c28e70a736b6cf32554d0677.

Встановлено scientific-critical-thinking та всі його references. Statistical-analysis потребує Python >=3.12 й ізольованого наукового оточення; clinical claims не стають діагнозами.

### VoltAgent/awesome-agent-skills

https://github.com/VoltAgent/awesome-agent-skills

Ліцензія: MIT. Закріплена ревізія: 3cd17ca9f40796a5dc564ebc6d76b4aa1303ff07.

Індекс посилань, не первинний автор усіх скілів. Встановлюємо з оригінальних джерел, не весь каталог.

### HKUDS/Vibe-Trading

https://github.com/HKUDS/Vibe-Trading

Ліцензія: MIT. Закріплена ревізія: 29aa084fb7866087c612ddd55ef5449824374e22.

Встановлено behavioral-finance як методичний матеріал. Backtest-diagnose прив’язаний до чужого SignalEngine/artifacts; live trading не підключено, твердження про прибутковість не перевірені.

### affaan-m/ECC

https://github.com/affaan-m/ECC

Ліцензія: MIT. Закріплена ревізія: b92f181b3b748d1abbc2afd94af6aa7d8c8fca29.

content-engine, залежність brand-voice, market-research та agent-security-hardening. Hooks, автопублікація та автонавчання політик не встановлювались.

### morluto/rea

https://github.com/morluto/rea

Ліцензія: MIT. Закріплена ревізія: 08a897b2cd7b359fcb0674c82baec3f1a74af632.

MCP для reverse engineering з Node і native engines. Потрібен конкретний дозволений об’єкт аналізу та окреме середовище; для поточної системи не обов’язковий.

Нові direct adapters цього етапу замінюють попередній статус integration_candidate для Actual/Hindsight/OmniRoute/HyperFrames на «код адаптера реалізований, live account/production перевірка окремо». MCP adapter дозволяє під’єднати сумісні stdio інструменти, але не конвертує автоматично Claude hooks чи UI-застосунок у Hermes tool. OpenDesign, Understand-Anything, Oriveo, Compact Guard і Geo-sleuth не заявляються як повністю активовані runtime services. Їхні специфічні сценарії/доступи потрібно перевірити перед використанням.

## 7. Розгортання сервера

Початкова конфігурація з маніфесту: Ubuntu24.04 LTS,12vCPU,48GB RAM,400GB SSD. Це план, не підтверджені параметри поточного production. GPU не обов’язковий для основного API; локальні LLM/LivePortrait/важкий render можуть вимагати окремого GPU node. Пам’ять і CPU потрібно розподіляти за реально активними workers, не запускати 12 важких образів без capacity planning.

### Крок 1 — підготовка

Встановити Docker Engine/Compose, git, TLS reverse proxy, синхронізацію часу. Створити системного користувача, каталоги volumes, firewall і backup target. Відкрити назовні лише потрібний TLS порт; Postgres/Redis/Vault/n8n/worker endpoints лишити в приватних мережах. Підтвердити DNS/сертифікати. Не використовувати dev Vault у production.

### Крок 2 — основа

Прочитати DEPLOYMENT_RUNBOOK.md, docs/DEPLOY_SYNDICATE.md та .env.example. Запустити Postgres+pgvector, Redis і Vault відповідно до deploy/docker-compose.yml. Ініціалізація/розпечатування Vault виконується оператором; recovery keys тримати поза сервером. Застосувати згенеровані policies через tools/vault_policies.py. Створити AppRole для кожного runtime. Перевірити backup і restore ще до завантаження особистих даних.

### Крок 3 — секрети

Єдине джерело шляхів — src/vault_paths.py. Integration worker читає secret/data/eva-syndicate/agents/<agent>/integrations. Запис KV: vault kv put secret/eva-syndicate/agents/<agent>/integrations @/secure/<agent>-integrations.json. JSON готується із config/integration_worker.example.json у приватному каталозі з mode0600; приклад із placeholder значеннями не придатний до запуску. Не комітити заповнений файл. Для KODEX/Antigravity, якщо готової policy немає, видати read лише власного integration path плюс token renewal, не wildcard усіх агентів.

Coordinator читає лише worker API keys з secret/eva-syndicate/auth, поле integration_worker_keys з mapping agent→key. Provider keys живуть у власних worker secrets. Не перезаписувати інші auth поля при додаванні mapping; використовувати KV patch. Додайте не-секретний SYNDICATE_INTEGRATION_URLS JSON з agent→private-worker-origin до runtime coordinator.

### Крок 4 — збірка й запуск інтеграцій

З кореня репозиторію: docker compose -f deploy/docker-compose.integrations.yml -p syndicate-fin build. У приватному env встановити SYNDICATE_INTEGRATION_AGENT=fin, VAULT_ADDR, INTEGRATION_VAULT_ROLE_ID, INTEGRATION_VAULT_SECRET_ID. Потім docker compose -f deploy/docker-compose.integrations.yml -p syndicate-fin up -d. Окремі project names потрібні, щоб 12 профілів не ділили один volume/AppRole. Worker не публікує host port. Приєднати coordinator до відповідної private network і задати стабільний network alias; default однакове ім’я integration-worker у різних мережах не слід використовувати як неоднозначний hostname.

На старті grants містить лише skills.list і skills.read. Додати hindsight.recall/retain/reflect або інші потрібні operations лише після конфігурації джерела й перевірки відповідного облікового запису. Для MCP вказувати абсолютний command, args, cwd, очищений env та точні tools; не надавати execute/shell/delete/publish інструменти як нібито read-only. Provider process isolation не заміняє semantics approval на небезпечну дію.

### Крок 5 — підключення сервісів

Actual: окремий self-hosted server, створений budget, sync ID і whitelist account IDs. Password/encryption password через Vault. Зробити snapshot короткого періоду і звірити кількість/суми з Actual UI. Не додавати різні валюти без конвертації за датованим курсом.

Hindsight: окремий server і database, його provider key/модель і budget. Створити/перевірити banks syndicate-<agent>. Встановити retention, backup і transport auth. Перевірити retain→recall із synthetic фразою та відсутність доступу до іншого bank через worker. Reflect може витрачати токени; встановити provider budget.

OmniRoute: побудувати server з pinned upstream revision або перевіреного digest; увімкнути API-key auth, провайдери та дозволені моделі. Для worker url використати базу з /v1. Перевірити billing, fallback, timeout і відсутність немаскованого PII. Не підключати обхідні web-cookie providers замість офіційних API.

HyperFrames: створити trusted проєкт у EVA_DATA_DIR/integrations/render_projects/<agent>/<project>. Вхід index.html, assets і timeline. Виклик hyperframes.render приймає тільки project ID; вихід syndicate-render.mp4 має бути новим. HOME=/tmp, HYPERFRAMES_BROWSER_PATH=/usr/bin/chromium, telemetry off. Temporary scratch потребує достатнього вільного простору; у Compose виділено tmpfs4GB, але реальний RAM cap може бути нижчий за суму scratch і процесів. Великі render jobs краще винести в окремий bounded worker із дисковим scratch. Preview перед публікацією обов’язковий.

MCP: transport stdio SDK перевірений на local synthetic server, а також на встановлених Context Mode 1.0.169, REA 6.5.0 та Skill Seekers 3.10.0: initialize, list_tools і виклики ctx_stats, list_unknowns, list_configs відповідно. Готові мінімальні конфігурації: config/integration_mcp.example.json; вставити потрібні записи в поле mcp власного Vault JSON, додати grants mcp.list і mcp.call. Ці приклади надають лише діагностичні операції. Context Mode запускається на кожний запит окремо: сесійні метрики не агрегують всю історію агента. Для тривалої пам’яті використовується Hindsight. REA native engines/desktop/device bridges не входять у цей контейнер; discovery не доводить їхню готовність. Для кожного реального пакета спочатку list_tools, потім вузький allowlist, потім smoke конкретної операції. Context Mode hooks/Compact Guard не монтувати глобально в production supervisor. Skill Seekers outputs повторно сканувати, зберігати source/license/hash і не виконувати generated code автоматично.

### Крок 6 — клієнт і domain workers

Запустити основний runtime і client за repo runbook. Для Oscar/Tyler/Jack окремо використовувати deploy/docker-compose.directors.yml та docs/DIRECTORS_DEPLOYMENT.md. Задати per-agent ACTIONS/PROVIDERS і coordinator action allowlists. Власний integration worker доповнює domain worker; він не заміняє його бізнес-логіку. Перевірити state/volume persistence після restart.

### Крок 7 — приймання

Перевірки: health,401 без ключа,403/denied для непризначеної дії, identity match, PII masking, недоступний provider→unavailable, bounded output, backup restore, audit intent/result, фактичний artifact, відсутність real payments/publications. Записати exact image digests, commit, конфігурацію без secrets, version dependencies і результати. Дозвіл на live activation має називати конкретні operations/resources.

## 8. Приклади викликів

POST /integrations/oscar/execute з operator master key та JSON: {"operation":"skills.read","payload":{"skill":"content-engine"}}. Worker повертає reference content із provenance/policy, не виконує його.

POST /integrations/fin/execute: {"operation":"actual.snapshot","payload":{"account":"<allowed-account-id>","start":"2026-10-01","end":"2026-10-15"}}. Для пустого періоду transactions=[]; це не вигаданий нульовий баланс.

POST /integrations/kodex/execute: {"operation":"hindsight.recall","payload":{"text":"Що було вирішено щодо резервних копій?"}}. Поле bank із payload не використовується — bank обирається за worker identity.

POST /integrations/oscar/execute: {"operation":"hyperframes.render","payload":{"project":"release-demo"}}. Проєкт має існувати в дозволеному volume. Повторний виклик не перезаписує готовий artifact.

## 9. Експлуатація, збої та відновлення

Щодня перевіряти останні помилки, latency, disk, queue depth, expiry provider keys і фактичні витрати. Наявність HTTP200 не гарантує успіх бізнес-операції: перевіряти JSON status та artifact. Не перетворювати unavailable на правдоподібні числа.

Backup: Postgres logical dump плюс перевірений restore; SQLite online backup або зупинка worker перед копією WAL/DB; Vault snapshots/recovery procedures; медіа й archive volumes; encrypted off-host copy. SecretID/API keys не повинні бути в загальному backup manifest. Перевіряти відновлення на synthetic даних.

Rollback: зупинити нові виклики, повернути попередній image digest/config, не робити blind downgrade DB schema, зберегти журнал і artifacts. Для невідомого результату зовнішнього side effect спочатку reconciliation; не повторювати автоматично.

Оновлення: pinned revision/package lock → review → isolated test → full tools/check.sh → CI → merge → canary → контрольоване ввімкнення. Не запускати npx latest або curl|bash із prompt-контексту в production.

## 10. Стан перевірки та незавершені роботи

Перевірено локальний HyperFrames render: справжній MP4, 640×360, 1 секунда, 10 кадрів, контейнер без мережі. Для Chromium потрібні HYPERFRAMES_BROWSER_PATH=/usr/bin/chromium і writable HOME=/tmp; tmpfs /tmp має бути щонайменше 4 GiB за поточної конфігурації. Actual SDK init/shutdown перевірено; бюджет реального користувача не синхронізувався. Усі 12 профілів пройшли authenticated skills API smoke.

GitHub: PR https://github.com/andrejzhivilov-ctrl/syndicate/pull/13. Персональний доступ GitHub відновлено; пакет опубліковано з акаунта andrejzhivilov-ctrl. Поточний статус CI та злиття перевіряється на сторінці PR. Злиття коду не означає запуску production-сервера.

Пакет містить реалізований код адаптерів, API boundary, образ і документацію. Локальні synthetic contract tests не підтверджують доступ до production budgets, LLM accounts, bookmaker coverage або social permissions. Сервера/домену/credentials від оператора ще не отримано, тому production activation не виконана.

Незавершені продуктові інтеграції: повний Hermes tool gateway для всіх бізнес-операцій; storefront/live concierge UI; Stripe payment/webhook→factory transactional flow; Pinterest/YouTube/social publishing; Telegram approval delivery; full LivePortrait; subscriber database; автоматична міграція архівів/knowledge DB; native integration із кожним стороннім desktop/plugin. Ці функції не слід рекламувати як уже діючі.

Джерела стану: docs/HANDOFF.md, docs/DIRECTORS_DEPLOYMENT.md, docs/SKILL_LIBRARY.md, config/agents/*.profile.json, config/skill_scan_report.json, apps/shared/api-contract.yaml, deploy/runtime/integration_runner.py та src/integrations/service_hub.py. Повні validation results зберігаються в workspace-context/validation-record.md; repo документація містить підсумок без секретів.
