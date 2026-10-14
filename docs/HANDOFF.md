# HANDOFF — журнал передачі між агентами

**Читай це першим, починаючи сесію.** Ні Arena Agent, ні Google Antigravity не мають
пам'яті про попередні сесії — весь контекст живе тут і в git-історії.

Формат запису — newest first. Один запис на сесію/задачу.

```markdown
## <YYYY-MM-DD> — <хто: Arena Agent | Antigravity | людина>

**Гілка:** ...  **Коміт:** ...  **Ворота:** ✅/❌

### Зроблено
- ...

### Не дороблено / свідомо залишено
- ...

### Наступне
1. ...

### Ризики й спостереження
- ...
```

---

## 2026-10-14 — Arena Agent: домашній ПК зараз, сервер пізніше

**Гілка:** arena/ce93afb9-syndicate  **Ворота:** ✅ `bash tools/check.sh` (exit 0)

### Зроблено
- **Інструкція:** `docs/HOME_DEPLOYMENT.md`. Відповідь: домашній ПК придатний як LAN-стенд для стеку (postgres, redis, vault, embeddings, eva-agent, n8n, whisper, nginx). Для 24/7 і продакшну — ні. Агенти не запускаються: Hermes-runtime лише як контракти.
- **`DATA_ROOT`** у `docker-compose.yml` і `deploy/docker-compose.yml` (копії ідентичні): усі хост-шляхи `/data/*` тепер `${DATA_ROOT:-/data}/*`. Сервер не змінюється (за замовчуванням `/data`).
- **`.env.example`:** `DATA_ROOT`, коментар про `ASR_MODEL` для слабкого ПК.
- **Посилання** з `docs/DEPLOY_SYNDICATE.md` (розділ 7a).

### Не перевірено
- Жодного запуску `docker compose` у sandbox: Docker немає. Перший реальний запуск — на ПК.
- Характеристики ПК невідомі. Вимоги в документі — мінімум і рекомендація.
- Розмір сервера для поточного стеку — оцінка, не вимірювання.
- Тест `test_trash_is_purged_on_next_update_after_30_days` мав дефект: змішував фіксований годинник (2026-10-10) з реальним. Годинник сховища в тесті зафіксовано на NOW. Логіку очищення не змінювано.

### Інцидент з середовищем
- Під час сесії sandbox переклонували: локальні коміти зникли з локальної гілки, але були на `origin/arena/ce93afb9-syndicate` (до `b532e11`). Локальна гілка переведена на origin через `reset --mixed` після перевірки, що робоче дерево збігається з origin. Втрат немає.

### Наступне
1. Ти: характеристики ПК (CPU, RAM, диск, ОС, годин роботи на добу).
2. Перший запуск стеку на ПК за розділом 4 `docs/HOME_DEPLOYMENT.md`; результат `docker stats` і `verify_deployment.sh` — у HANDOFF.
3. Hermes-клієнт і образ runtime (план у `docs/AGENT_CONTAINERS.md`).

---

## 2026-10-10 — Arena Agent: вечірній звіт Єві о 21:00 з файлами KODEX

**Гілка:** arena/ce93afb9-syndicate  **Ворота:** ✅ `bash tools/check.sh` (exit 0)

### Зроблено
- **Файлова частина 21:00:** `evening_section()` у `src/agents/kodex.py` збирає всі дії KODEX і агентів за 24 год з `KODEX_DATA_DIR`. Без каталогу — `unavailable`, не нулі.
- **Єва:** `kodex` — обов'язковий розділ вечірньої рефлексії. Підсумок у відповіді з реальних лічильників. Без даних у `missing_inputs` написано `kodex`.
- **Ендпоінт `/proactive/evening`:** передає файлову частину (раніше викликався без даних, рефлексія завжди була `no_precollected_reports`).
- Тести: `tests/test_regressions.py` (зміна контракту: список обов'язкових даних розширено), 317 зелених у зачеплених наборах.

### Не дороблено / свідомо залишено
- Доставка загального звіту Андрію (Telegram / n8n) не перевірялась: нічого не відправляється з сандбокса.
- Розділи Дока й Kira у вечірньому потоці не збираються (агентів не запускаємо на вечірньому кроці). Позначено як відсутні.
- Hermes-клієнта й образу runtime в репозиторії немає: є лише контракти в `src/agent_platform/`.

### Наступне
1. Перевірити на деплої: n8n `0 21 * * *` → `/proactive/evening` з `KODEX_DATA_DIR`, відповідь містить `kodex`.
2. Реалізувати Hermes-клієнт і образ runtime (план у `docs/AGENT_CONTAINERS.md`).

### Ризики й спостереження
- `KODEX_DATA_DIR` не задано → вечірній звіт каже, що файлів не зібрано. Це має бути видно на деплої.
- Вікно 24 год: якщо n8n затримається, частина дій попаде у звіт наступного дня.

---

## 2026-10-10 — Arena Agent: YouTube через Google Cloud, звіт Єві по файлах, контейнери агентів

**Гілка:** arena/ce93afb9-syndicate  **Ворота:** ✅ `bash tools/check.sh` (exit 0)

### Зроблено
- **Звіт Єві:** тепер містить завантаження файлів агентами (`agent_ingests`) і автоочищення кошика з іменами (`auto_purged`). Раніше ці дії не потрапляли в звіт. Тести: `tests/test_kodex.py` (32 зелені).
- **YouTube:** сервіс `youtube` додано в `src/vault_paths.py` (доступ Єві через `CONNECTOR_SERVICES`). Політики перегенеровано: змінилась лише `eva-agent.hcl`.
- **Документи:** `docs/YOUTUBE_GCP_SETUP.md` (кроки для Андрія в Google Cloud), `docs/AGENT_CONTAINERS.md` (план контейнерів).
- Рішення записано в `docs/DECISIONS_ANDRII.md`.

### Не дороблено / свідомо залишено
- Конектор YouTube (`src/integrations/youtube.py`) не написано: потрібні облікові дані Google Cloud і перевірка на живому API. Сандбокс до googleapis не має доступу.
- Контейнери агентів у `docker-compose.yml` не додано: не обрано Hermes runtime, активація без погодження заборонена.
- Права (`grants`) порожні. Жоден агент не активовано.

### Наступне
1. Андрій створює проєкт Google Cloud і передає облікові дані через Vault (кроки в `docs/YOUTUBE_GCP_SETUP.md`).
2. Вибрати Hermes runtime для контейнерів агентів.
3. Планувальник щоденного звіту Єві для KODEX: функція є, розкладу немає.

### Ризики й спостереження
- Файли без мітки з правом видалення агентами (рішення Андрія). Звіт Єві тепер повний, але без розкладу його ніхто не відправляє.

---

## 2026-10-10 — Arena Agent: рішення Андрія (розділ 6) і правки конфігів

**Гілка:** arena/ce93afb9-syndicate  **Ворота:** ✅ `bash tools/check.sh` (exit 0)

### Зроблено
- Журнал рішень: `docs/DECISIONS_ANDRII.md`.
- Медичний архів Дока: читання для файлів з міткою `andrii_protected`. Суперечність у `knowledge_base.json` і `doc.profile.json` знято.
- Файли без мітки: агенти можуть читати, редагувати й видаляти (рішення Андрія, ризик прийнято свідомо).
- Кошик: 30 днів (уже було в `kodex.py`, не змінювалось).
- YouTube (офіційний Data API) для Єви: статус `approved_by_andrii_2026-10-10_keys_pending_deploy`. Права порожні, ключі — у Vault при деплої.
- Пороги харчування Дока не задаємо.
- Журнал діалогу `EVA_SYNDICATE_FULL_DIALOGUE.txt` лишається в репозиторії.
- Архітектура: кожен агент — в окремому контейнері, LangGraph — зовнішній координатор (`docs/SYNDICATE_PLATFORM_BASE.md`).
- `docs/PERMISSIONS_MATRIX.md` перегенеровано.

### Не дороблено / свідомо залишено
- YouTube Music: рішення не прийнято (неофіційний доступ — ризик акаунта).
- Жоден агент не активовано. Контейнери для агентів у `docker-compose.yml` не додано (потрібне окреме погодження запуску).
- Етап 1 (сервер) не запускався.

### Наступне
1. Вирішити YouTube Music.
2. Погодити Етап 1 (базовий стек на сервері) і шлях до контейнерів агентів.

### Ризики й спостереження
- Медичні файли без мітки з правом видалення: переглянути, коли з'являться реальні файли в архіві.

---

## 2026-10-10 — Arena Agent: Етап 0 поетапного запуску (перевірка, без активації агентів)

**Гілка:** arena/ce93afb9-syndicate  **Ворота:** ✅ `bash tools/check.sh` (exit 0, після встановлення залежностей у `.venv`)

### Зроблено
- Перевірено стан за `docs/STAGE0_STATUS.md`: перелік агентів, сервіси compose, файли KODEX-бота.
- Файли KODEX-Telegram (`src/agents/kodex_telegram.py`, `tools/kodex_bot.py`, `tests/test_kodex_telegram.py`) **є на `origin/main`**. Промпт «новий чат» це заперечував, це застаріла інформація.
- Жодних змін коду, прав чи профілів.

### Не дороблено / свідомо залишено
- Етап 1 (базовий стек на сервері) не запускався: потрібне погодження Андрія і доступ до сервера.
- KODEX не в `docker-compose.yml`; токен Telegram не задано.

### Наступне
1. Рішення Андрія з розділу 6 промпту (медичний архів, файли без мітки, версії, YouTube, пороги Дока, журнал діалогу).
2. Погодження запуску Етапу 1.

### Ризики й спостереження
- `origin/main` у промпті вказано як `30828c8`, фактично `0165aa4`. Промпти з застарілим хешем варто оновлювати.

## 2026-10-10 — Arena Agent: KODEX — обробники Telegram і виправлення дефектів сховища

**Гілка:** arena/f1e67097-syndicate  **Коміт:** див. git log  **Ворота:** ✅ (`bash tools/check.sh` зелений)

### Зроблено
- **Обробники Telegram KODEX** (`src/agents/kodex_telegram.py`): кожна кнопка викликає метод `KodexStore` (`chg:yes` → `confirm`, `chg:no` → `reject`, `del:start` → вибір → `request_delete`, `net:*`, `fmt:*`, `lbl:*`, `edit:*`, `up:*`, звіти). Тести на кожен callback: `tests/test_kodex_telegram.py` (44 тести, без мережі).
- **Прив'язка callback до запиту:** `chg:yes:<token>`, `del:pick:<id>`, `net:yes:<req>`, `fmt:yes:<ext>`. Голі `chg:yes` тепер відхиляються. Раніше кнопка «Так» не знала, на яку зміну відповідає.
- **Запуск:** `tools/kodex_bot.py` (long polling). Без токена, `KODEX_DATA_DIR` або непорожнього `KODEX_TELEGRAM_ALLOWED_CHAT_IDS` не стартує. Логи — лише тип помилки (URL з токеном не пишеться).
- **Дефект звіту виправлено:** агентське видалення або редагування мічених файлів, яке схвалив Андрій, зникало зі звіту Єві (запис писався від імені Андрія). Тепер виконавець — агент, поле `approved_by` — Андрій.
- **Дефект даних виправлено:** відхилена версія мічених файлів (`reject`) лишалася на диску. Тепер видаляється.
- **Дефект лічильників:** `awaiting_andrii.delete` ніколи не збільшувався. Ключ прибрано, «permission» охоплює всі запити на зміну.
- **Атомарний запис** `kodex.json` (тимчасовий файл + `os.replace`).
- Нові методи: `reject_download`, `deny_format`.
- Профіль `kodex.json`: `telegram.status = handlers_ready_bot_pending_token`. Матриця прав перегенерована.

### Не дороблено / свідомо залишено
- Транскрибація, переклад, розпізнавання фото/HEIC, вивчення форматів (парсер), саме завантаження за дозволеним посиланням: кнопки відповідають «не підключено» і нічого не змінюють.
- Мережевий шар (`tools/kodex_bot.py`) не перевірено з живим Telegram: API недоступний із пісочниці. Перевірка при деплої.
- Планувальник щоденного звіту Єві не зроблено (лише функція).
- Старі байти версії після звичайного (немічений) перезапису лишаються на диску без посилання. Питання: чи зберігати попередню версію 30 днів, як кошик.

### Наступне
1. Деплой: `TELEGRAM_BOT_TOKEN_KODEX`, `KODEX_TELEGRAM_ALLOWED_CHAT_IDS` (ID Андрія), `KODEX_DATA_DIR`; перевірити запуск і одну кнопку наживо.
2. Розпізнавання фото і аудіо: OCR, HEIC (pillow-heif), локальний Whisper. Після цього `needs_engine` → `stored` з текстом.
3. Вирішити з Андрієм: зберігати попередні версії немічених файлів чи ні.

### Ризики й спостереження
- **Суперечність у правилах (потребує рішення Андрія):** `config/shared_skills/knowledge_base.json` каже «Ваш медичний архів — лише Андрій», а `doc.profile.json` і це рішення — «лише читання для файлів з міткою». Код (`doc_knowledge.py`) відповідає другому. Поле `doc_access: read_labeled_only` у `DOMAINS` назване двозначно.
- **Ризик медичних файлів без мітки:** `classify()` кладе медичні файли в `andrii_medical_vault`, але без мітки (через KODEX) агенти можуть їх редагувати й видаляти. Це узгоджено як «за звичайними правилами», але варто підтвердити.
- Тест `test_bare_change_callbacks...` і `test_buttons_only_andrii...` змінено під новий контракт callback. Старий контракт не був безпечним.
- Файли `docs/NEXT_CHAT_BRIEF.md` і `docs/PROMPT_NEXT_CHAT_KODEX.md`, згадані в промпті сесії, у репозиторії відсутні.

---

## 2026-10-10 — Arena Agent: Док — здоров'я, тренер, кухар, база знань (правила і каркас)

**Гілка:** arena/41a10104-syndicate  **Коміт:** див. git log (наступний після fcbfe8c)  **Ворота:** ✅

### Зроблено
- Код: `doc_nutrition.py` (Mifflin-St Jeor, КБЖУ, вода; без даних — `not_configured`), `doc_knowledge.py` (домени, рівні джерел A/B/C, допуск фактів, неділя, дозволені хости), `doc_buttons.py` (кнопки бота, лише Андрій), `doc_shopping.py` (список для Єви).
- Архів Андрія — лише читання для Дока. Медичні поля — `not_configured` до верифікації.
- Спільний скіл `knowledge_base`: читання всім, запис — лише власникам (`config/shared_skills/knowledge_base.json`).
- Документи: `doc_core/DOC_KNOWLEDGE_PLAN.md`, `doc_core/DOC_GITHUB_SCOUT.md`, `doc_core/DOC_TELEGRAM_BOT.md`.
- GitHub: кандидати book-to-skill (MIT), pdf-reader-skills (MIT), free-exercise-db (Unlicense, без зображень). Нічого не встановлено.

### Не дороблено / свідомо залишено
- Токен бота, інтернет і неділя, годинник, передача файлів, NotebookLM/OCR/Perplexity — при розгортанні.

### Наступне
1. Вирішити, які кандидати GitHub вендорити (з перевіркою ліцензії).
2. Пороги нутрієнтів затверджує Док з Андрієм.

### Ризики й спостереження
- NotebookLM може не мати публічного API. Перевірити перед вибором сховища архіву.
- `tests/test_postgres_paths.py::test_durable_audit...` інколи падає в повному прогоні (спільний стан живого Postgres); окремо і повторно — зелено. Розібрати окремо.

---

## 2026-10-10 — Arena Agent: Єва — кошики (перевірка можливості) і Док як власник списку

**Коміти:** a121f30, fcbfe8c  **Ворота:** ✅

### Зроблено
- Сільпо: внутрішній API, неофіційний; кошик можливий лише через браузерний воркер у n8n з обліковим записом. АТБ — технічні роботи під час перевірки. Varus — лише акції й магазини. Ашан — не перевірено.
- `eva_basket.py`: реєстр мереж (усі `not_connected`), пропозиція з `order_allowed: false`. Док веде список і нутрієнти; Єва формує кошик, якщо зможе.
- Воркер дозволено за умов перевірки умов користування кожної мережі.

### Наступне
- Перевірка умов користування перед підключенням воркера.

---

## 2026-10-10 — Arena Agent: Фін — автоматичний виклик Єви, фонди картки/готівка/платіжні системи

**Коміти:** a73982d, e4d14d3  **Ворота:** ✅

### Зроблено
- Маршрутизація: Фін відповідає лише Єві (і Андрію). Док до Фіна не звертається.
- Фонди: `card`, `cash`, `payment_system`; безпека (`safety`) недоторканна. Назви — при налаштуванні доступів. Категорії: Продукти, Відпочинок, Інше.
- Автовиклик `eva_basket_ready` → Фін (`funds_check`); прямий запит Андрія: `fin_funds_check`.
- Банк: рішення A — читання закрите за замовчуванням (`fin_bank_gate.py`, `bank_read_grants=[]`).
- Звіти: ЗВІТ (повний) — лише Андрій; стандартні; блок «Заплановано» завжди. Експорт PDF/DOCX/XLSX/PPTX/Obsidian локально; Google — `blocked_not_granted`.
- Активовано (внутрішнє): dispatch Єви, розрахунок коштів, локальні звіти. Не активовано: банк, Telegram, Google, Obsidian, n8n.

### Наступне
- Крок «Єва сформувала кошик» має викликати `eva_basket_ready` (з'явиться при підключенні Єви).
- PDF і інші файли перевірити при запуску.

---

## 2026-10-10 — Arena Agent: Фін — пряме доручення Андрія (затверджено)

**Коміт:** a73982d  **Ворота:** ✅

### Зроблено
- Фін відповідає лише Єві. ФОП — окрема документація, не рахунок. Джерела: готівка, Монобанк, ПриватБанк, А-Банк, Payoneer, PayPal, криптогаманець (без реквізитів).
- Не підключено: сам крок Єви, Telegram, банки, Google.

---

## 2026-10-10 — Arena Agent: Фін і Сем — підготовка (локально, відтворено після втрати sandbox)

**Коміти:** 22cff78 (запушено)  **Ворота:** ✅

### Зроблено
- Сем: 8 скілів вендоровано (`sam_core/vendor/`, `vendored_inactive`), SOURCES.lock.yaml з SHA, FMP-адаптер прибрано. Тести вендору зелені (709). `requirements-sam.txt` окремо.
- Фін: `fin_policy.py` (runway, самозвірка, basket advisory, allocate_purchase), профіль з 9 драфт-скілами, `banking.not_granted`, `payment_data_stored=false`.

### Ризики й спостереження
- Локальні коміти `97b2dbe`, `60f7927`, `1666b3b` зникли після перезавантаження sandbox. Не покладатися на незапушене.

---

## 2026-10-10 — Сем: перевірка скілів + шорт-ліст брокерів (не вибрано)

Перевірено ліцензії/код: `sam_core/SAM_SKILL_REVIEW_2026-10-10.md`. У профілі `skill_candidates` (activation=candidate_not_installed). Брокери: `sam_core/SAM_BROKER_SHORTLIST_2026-10-10.md`. Жодного install/ключа/брокера.

## 2026-10-10 — Arena Agent: Сем — розклад 07:00 Азія, щоденник, аналітика, розвідка скілів

Азія **07:00** Kyiv. Щоденник обов’язковий щодня. Аналітика: понеділок 10:00 (тиждень), 1-ше 10:00 (місяць). Розвідка: `sam_core/SAM_SKILLS_REPO_SCOUT_2026-10-10.md` (не встановлено). Брокери — почекати.

## 2026-10-10 — Arena Agent: Сем — бриф Єви, Азія, демо+live, слоти LLM

Запам’ятовано, grants не чіпали: стислий JSON у бриф Єви **обов’язковий** (не скасовується). Торгівля і демо, і live — окремі контури. Слот азійської сесії ~03:00 Kyiv. Моделі (не вибрані): Grok=соцмережі, Gemini=аналіз/календар, Claude=ризик/10-K; математика без LLM.
Брокерів не підключали. Довіра брокера ≠ «знайшов у чаті»; реєстри регуляторів + окреме «так».

---

## 2026-10-10 — Arena Agent: ідентичність Сема + міст + перемикач (grants порожні)

Сформовано SAM v0.2: HITL за замовчуванням. Auto FX/crypto @99 — схема й код, прапор `false`, без `trade.execute`.
Інвестиції завжди обговорення; `sam_auto_invest_allowed()` завжди False. Брокер TBD; `submit_lot` → `broker_unavailable`.
Бот, голос, Drive, n8n, Hermes — вимкнені. Поверх 7.

---

## 2026-10-10 — Arena Agent: живий монтаж n8n (inactive, HITL)

Андрій: потрібен live mount. Видано точно `n8n.workflow.design` + `n8n.workflow.mount` / `n8n/live`.
`n8n.workflow.activate` не видана. n8n не control plane. Ключі лише `N8N_BASE_URL` + `N8N_API_KEY` у env.
Код: `src/agents/architect_n8n.py`. Без env → `mount_unavailable`, не фейковий успіх.

---

## 2026-10-10 — Arena Agent: Architect завершений для викладки

Пакет prepared: ранбук + `ARCHITECT_PERMISSIONS.md` (порожні grants = fail-closed дозвіл на деплой).
CLI `tools/architect_preview.py`. `gitops_push=false`; агент не пушить у GitHub.
Не live n8n, не merge в main. Гілка `arena/41a10104-syndicate`.

---

## 2026-10-09 — Arena Agent: Architect preview/archive/draft skills (без grants)

Архів і knowledge — порожні слоти. Скіли new-agent / n8n-link / self-learn = `draft`.
Локальний mermaid-прев’ю `architect_preview.py`: показати → HITL → lint, **не** live n8n.
Каталог GitHub: `ARCHITECT_CANDIDATE_CATALOG.md` (n8nmermaid, LikeC4) — не встановлені.
«Контроль системи» = креслення, не host_control.

---

## 2026-10-09 — Arena Agent: Architect identity v0.2 (Єва не ставить задач)

Досьє CTO розібране: архетип/антикостилі/Blueprint — ідентичність; live n8n, бот, GitOps, моделі — ні.
**Корекція Андрія:** задачі лише він; Архітектор → Єва тільки звіт у payload.
Код: `architect_access`, `architect_blueprint`, `architect_report`, `architect_ready`. Grants порожні. PR не злито.

---

## 2026-10-09 — Arena Agent: Marshal prepared-пакет + install SkillSpector

Код observe/HITL/brief/ready в `src/agents/marshal_*.py`. Ранбук `MARSHAL_DEPLOYMENT_RUNBOOK.md`.
`tools/install_skillspector.sh` ставить бінарник у `.tools/` (gitignore), не в `requirements.txt` і не в `capabilities`.
Python 3.12+ потрібен для NVIDIA CLI; на 3.11 — fail-closed `scan_unavailable`.
`python tools/marshal_ready.py` вимагає порожні grants. Live бот/veto/Hermes не вмикались.

---

## 2026-10-09 — Arena Agent: SkillSpector як сканер пропозицій (не grant)

Андрій сказав «так» на SkillSpector `--no-llm` як сканер, не як право вмикати скіли.
- Хост-обгортка `src/agents/marshal_skill_scan.py` + `tools/marshal_skill_scan.py`.
- Лише локальний шлях; remote URL deny; LLM-pass вимкнений; env з ключами здирається; секрети в stdout редагуються.
- Немає бінарника → `scan_unavailable`, не SAFE. Немає рядка в `requirements.txt` і не в `skills`.
- `capabilities` порожні.

---

## 2026-10-09 — Arena Agent: каталог кандидатів Marshal (не install)

Огляд GitHub у `marshal_core/MARSHAL_CANDIDATE_CATALOG.md`. Перша черга (окреме «так»): NVIDIA SkillSpector `--no-llm`, Gitleaks, OWASP як SOURCES. Не ставити: archived protectai/llm-guard, оптові skill-packs, live red-team payload. Профіль `skills: []`.

---

## 2026-10-09 — Arena Agent: Marshal observe-only на інтернет за командою Андрія

**Гілка:** `arena/41a10104-syndicate` · **PR #7 не злито**

Пряме «пошукай в інтернеті» не вето і не HITL. Маршал лише пише метадані. Пуш/кнопки — тільки критична загроза (витік, скіл/права, deploy, гроші, delete, exfil). Жовте — у бриф, не в Telegram. Grants не змінювались.

---

## 2026-10-09 — Arena Agent: операційна модель Marshal v0.3 (без grants)

**Гілка:** `arena/41a10104-syndicate` · **Ворота:** `bash tools/check.sh` · **PR #7 не злито**

### Зроблено

- `MARSHAL_OPERATING_MODEL.md` + `MARSHAL_HITL_CONTRACT.md`: вето як HITL (таймаут deny), жовтий/червоний, brief→Єва лише payload, full report — прямий запит, пропозиції скілів з кнопками.
- TTS ні. n8n не control plane. Drive `folder_id=null`. Knowledge `sources: []`.
- Кандидати (`policy.veto`, Telegram, Drive) **не** в полі `capabilities`.

### Не робити без окремого «так»

- Бот (потрібен реальний bot_id + allowlist), шар Observe, n8n aggregator, Drive folder, Dispatcher, `policy.veto`.

---

## 2026-10-09 — Arena Agent: розбір досьє Marshal (ідентичність ≠ grants)

**Гілка:** `arena/41a10104-syndicate` · **Ворота:** `bash tools/check.sh` · **PR #7 не злито**

### Зроблено

- Досьє CSO v4.0 розібране в `marshal_core/MARSHAL_DOSSIER_REVIEW.md`: архетип/голос/кредо — в ідентичність; 9 рівнів, cron, бот, Tetragon, veto, Haiku/Sonnet — не в профіль.
- Persona і runtime prompt v0.2: сталевий рапорт, підпорядкування Андрію, чесний `DENIED` замість вигаданого `SECURE`.
- Grants, Telegram, host_control лишаються порожніми/false. Абсолютне вето не видане.

### Не робити далі без окремого «так»

- Модель, `@marshal_security_bot`, Dispatcher, Tetragon, lockdown, читання пам’яті Єви, `policy.veto`.

---

## 2026-10-09 — Arena Agent: ідентичність Marshal (без активних grants)

**Гілка:** `arena/41a10104-syndicate` · **Ворота:** `bash tools/check.sh` · **PR #7 не злито**

### Зроблено (тільки Marshal)

- Профіль: `prepared_not_enabled`, `role_status=identity_draft`, порожні `capabilities` / `resource_scopes` / `services_enabled`.
- Ідентичність (початково вузька, далі розширена розбором досьє). `MARSHAL_FULL_SPEC.md` не скопійовано в права.
- Telegram inbound вимкнений; `live_modes.host_control` / `emergency_lockdown` / `telegram_bot` = false.
- Оркестраторний `emergency_lockdown` fail-closed (`host_control_not_granted`). `MarshalAgent` і Sentinel-маршрути не підключені до Dispatcher і не вмикались.
- Sentinel виключений; Tetragon/eBPF лишаються Фазою 2.

### Не дороблено / свідомо залишено

- Жодної capability. Hermes, модель, Telegram-бот, host control — ні.
- Dispatcher не ставився на маршрути Marshal.
- Історичний `src/agents/marshal.py` (CSO title, прямий `execute` lockdown) не переписувався, щоб не ламати 10floors; оркестраторний lockdown уже deny.
- PR не злито.

### Наступне

1. Формувати наступного агента (ідентичність, не grants) — за замовчуванням Fin, якщо Андрій не вкаже інакше.
2. Будь-який Marshal capability — окремий точний id після рішення про Dispatcher.

---

## 2026-10-09 — Arena Agent: підготовка Єви (без активних grants)

**Гілка:** `arena/41a10104-syndicate` · **Ворота:** ✅ `bash tools/check.sh` · **PR #7 не злито**

### Зроблено (тільки Єва)

- Grants лишаються порожніми. Запропоновані межі — `eva_core/EVA_ACCESS_BOUNDARIES.md`, не поле `capabilities`.
- `EvaAgent` відхиляє cross-agent memory write; recall читає лише `agents/eva`.
- Telegram inbound: `enabled=false`, порожній allowlist = deny; webhook без allowlist не проходить у чат. Bot/chat id не вигадані.
- Gmail не інтегровано. Nightly dormant. Psychology `sources: []`.
- Тести fail-closed: порожні grants, чужий namespace навіть при гіпотетичному memory.read, порожній Telegram allowlist, cross-agent remember.

### Блокери (не обходити)

1. `AgentDispatcher` не підключений до `chat` / `webhook_telegram` / curator / `parse_memory_command`. Підключення з порожніми grants відхилить і розмову — потрібне окреме рішення.
2. Оркестраторний `parse_memory_command` досі може писати в чужі namespace через `detect_agent()`.
3. Hermes, модель, credentials, n8n, Obsidian mount, voice/camera/geo — не готові.

### Handoff наступному агенту (не починати тут)

Наступний кандидат — **Marshal**: `config/agents/marshal.profile.json` уже `prepared_not_enabled`, `role_status=not_agreed`, grants порожні. Sentinel виключений. Не видавати capability, не підключати Dispatcher «заодно», не копіювати історичний `MARSHAL_FULL_SPEC.md` у права.

### Не дороблено

- Не активовано жодної capability.
- Dispatcher не інтегровано (свідомо).
- PR не злито.

---

## 2026-10-09 — Arena Agent: профіль Архітектора + default-deny слоти інших агентів

**Гілка:** `arena/41a10104-syndicate` · **Ворота:** ✅ `bash tools/check.sh`

### Зроблено

- Андрій підтвердив окремий **профіль** Архітектора. Ідентичність: чернетки n8n, не CTO. `role_status=identity_draft`.
- Capability не видано. LangGraph `ArchitectAgent` не з’єднаний з Dispatcher. Vault `architect → mcp` не скопійовано в `services_enabled` і не змінювалось.
- Додано persona, memory policy, toolkit, readiness, runtime prompt (draft у git).
- Інші агенти (`marshal`, `fin`, `doc`, `kira`, `sam`): лише `prepared_not_enabled` маніфести, `role_status=not_agreed`, порожні grants. Історичні спеки позначені як не-grants.
- Тести: усі маніфести default-deny; policy deny `agent.invoke` без grant.

### Не дороблено

- Немає моделі, live Hermes, n8n activation, жодного capability.
- Ідентичності marshal/fin/doc/kira/sam ще не сформовані (наступні по одному).
- Sentinel/Council не додавались.

### Наступне

1. Формувати наступного агента (ідентичність, не grants) — за замовчуванням Marshal, якщо Андрій не вкаже інакше.
2. Будь-який capability — окремий точний scope.

---

## 2026-10-09 — Arena Agent: Архітектор — gap analysis і default-deny контракт

**Гілка:** `arena/41a10104-syndicate` · **Коміт:** delivery commit цього запису · **Ворота:** ✅ `bash tools/check.sh`

### Зроблено

- Перевірено checkout: HEAD = `a50e8e4` (merge PR #6), робоче дерево було чисте; `git reset`/`clean` не використовувались.
- Gap analysis історичних CTO/n8n-спек і `src/agents/architect/` проти `docs/SYNDICATE_PLATFORM_BASE.md`: роль/модель/інтеграції не визначені; LangGraph-handler існує поза `AgentDispatcher`; n8n не control plane.
- Додано `config/agents/architect.profile.json`: `prepared_not_enabled`, порожні grants, `role_status=not_agreed`, `model_status=not_selected`, n8n flags вимкнені.
- Межі й workflow-контракт: `architect_core/ARCHITECT_ROLE_BOUNDARIES.md`, `ARCHITECT_WORKFLOW_CONTRACT.md`, `ARCHITECT_GAP_ANALYSIS.md`. Історичні специфікації позначені як не-grants.
- Тести `tests/test_architect_profile.py`: порожні grants, ізоляція від Єви, policy deny, golden/generated JSON лишаються `active=false`.
- Профіль не активовано; Hermes/n8n/workflow не запускались; capability не видавались.

### Не дороблено / свідомо залишено

- Не вибрано роль, модель, prompt, skills.
- Не відключено історичний `ArchitectAgent` у LangGraph (потрібне окреме рішення).
- Не змінено Vault-мап `architect → mcp`.
- Не імпортовано й не активовано жодного n8n workflow, включно з нічним аналізом Єви.
- `apps/` не чіпався; production не виконувався.

### Наступне

1. Андрій відповідає на відкриті питання в `ARCHITECT_ROLE_BOUNDARIES.md` §5 точним scope — без цього grants не додавати.
2. Окремо вирішити, чи ізолювати історичний LangGraph-handler до підключення Dispatcher.
3. Лише після явного дозволу — вузька функція (наприклад, статичний lint чернеток) з одним capability id.

### Ризики й спостереження

- Історичний оркестратор усе ще маршрутизує `design_workflow` тощо; це не platform grant, але може створювати хибне враження активації.
- Дві старі специфікації суперечать одна одній (24/7 CTO vs on-demand); не змішувати їх у майбутній ролі.

---

## 2026-10-06 — Arena Agent: нейтральний каркас платформи SYNDICATE (фаза 1)

**Гілка:** `arena/0f6034ef-eva-syndicate` · **Коміт:** delivery commit цього запису · **Ворота:** ✅ `bash tools/check.sh`

### Зроблено

- Додано `src/agent_platform/`: Hermes-only `AgentProfile` без бізнес-ролей і default grants;
  immutable registry з унікальними Hermes profiles та memory namespaces; host-authored access
  requests; fail-closed `AgentPolicy`; runtime/service adapter protocols; dispatcher для вузла
  зовнішнього LangGraph.
- Policy вимагає точний ресурсний scope для memory/service/location; власний memory namespace
  відокремлений; wildcard заборонений. Фінансові/деструктивні/security/deploy/зовнішні дії,
  зміни прав/політик, нові сервіси/ресурси та location повертають `approval_required` і не
  викликають runtime.
- Заблоковано capability для email send, входу до Дії/Армія+/BankID, fingerprint-spoofing і
  residential-proxy rotation. Ніяких профілів окремих агентів або прав поки не оголошено.
- `MemoryManagerAdapter` прив’язаний до одного namespace/session і окремо вимагає `memory.read`
  / `memory.write`; перед записом маскує PII у тексті, а metadata пропускає лише за allowlist.
  `MemoryManagerAuditSink` повторно використовує privacy-minimized append-only `audit.decisions`.
- Hermes transport/runtime та service connections не інстальовані й не підключені. Офіційні
  Hermes integration docs/source перевірені; через Python 3.14 runtime-vs-3.11 SYNDICATE mismatch
  не додавався Hermes до поточного process/dependencies. Висновки та наступні кроки —
  `docs/SYNDICATE_PLATFORM_BASE.md`.
- `docs/NEW_CHAT_PROMPT.md` оновлено для нового напрямку та безпечного branch/dependency/test/
  delivery процесу; простий `git apply` заборонений, записаний 3-way/`--theirs` рецепт.
- `tests/test_agent_platform.py`: **28 нових тестів**. Повний `bash tools/check.sh` зелений.

### Не дороблено / свідомо залишено

- Жодного live Hermes adapter/API, locked Hermes tag, container, model, profile, agent-role,
  permission grants, service adapter чи LangGraph wiring до існуючого production request path.
- Не реалізовано затвердження/re-entry path після `approval_required`; такі дії залишаються
  зупиненими, без side effect. Evening-report proposal pipeline — наступна окрема інтеграція.
- `ServiceAdapter` наразі лише контракт; поточний `ToolRegistry` автоматично не викликає нову
  `AgentPolicy`. З’єднати їх і тестувати кожну операцію треба до видачі Hermes tools.
- `apps/` не змінювався; deployment не виконувався.

### Наступне

1. Андрій обирає разом із нами Hermes version/commit і transport/process boundary після перевірки
   upstream toolset, sandbox, approval pauses, profile/data isolation і версії Python.
2. Реалізувати тільки контрольований tool bridge: кожен Hermes tool call → host-owned tool
   contract → capability/action/resource policy → existing HITL/audit; інші built-ins disabled.
3. Після цього — один майбутній agent profile за раз, тільки з погодженими роллю/моделлю/skills/
   integrations/scopes. NotebookLM, Obsidian і Google Drive залишаються майбутніми adapters.
4. Production deployment — окрема фаза з прямим дозволом користувача.

### Ризики й спостереження

- Новий dispatcher не є runtime security boundary, поки Hermes internal tool calls не проходять
  через tool bridge. Не відкривати API server із широкими Hermes built-in tools і не додавати його
  до Compose до завершення цього етапу.
- Audit writer у наявному `MemoryManager` є best-effort; перевірка коду не заміняє моніторинг
  persisted rows на сервері.
- Нагадати Андрію відкликати PAT у публічному `EVA_SYNDICATE_FULL_DIALOGUE.txt`; значення не
  використовувати/копіювати. Долю публічного файлу вирішує Андрій.

---

> **Примітка:** сесії 8 (гілка `arena/01a10d46-eva-syndicate`) і 9 (гілка
> `arena/01a10d4e-eva-syndicate`) виконувались **паралельно** і не бачили одна одну.
> Обидві спершу назвались «сесія 8»; запис нижче перенумеровано на 9, щоб журнал був
> однозначним. Порядок — newest first.

## 2026-10-06 — Arena Agent: durable audit trail (беклог #17)

**Гілка:** `arena/0f6034ef-eva-syndicate` · **Коміт:** delivery commit цієї гілки · **Ворота:** ✅

### Зроблено

* `MemoryManager.write_audit_decision()` і `write_outbound_veto()` додають append-only записи до
  `audit.decisions` / `audit.outbound_vetoes`; без `UPDATE`/`DELETE` і без читання цих таблиць.
* Оркестратор пише одне рішення на фіналізовану задачу та окремо кожну outbound-перевірку.
  Marshal `allowed=false` стає `blocked`, потрібний HITL — `pending` з ескалацією `ask`,
  відмова — `refused`; risk score і безпечні ознаки зберігаються як bounded metadata.
  Outbound gate також передає `requires_hitl` далі в HITL-гейт.
* Payload, тексти відповіді та вільні reason-повідомлення не потрапляють до audit-таблиць.
  Запис дозволяє лише allowlist ідентифікаторів/статусів/лічильників; reason для outbound —
  лише фіксований код. DB-помилка best-effort: не змінює результат задачі й не логує SQL params.
* Додані unit і live PostgreSQL тести на INSERT/round-trip, приватність через allowlist,
  graceful DB failure та INSERT-only least-privilege права. `pytest tests/`:
  **455 passed, 1 skipped**; `bash tools/check.sh` — усі ворота зелені.

### Не дороблено / свідомо залишено

* `hitl_override` лишається `false`: цей флоу фіксує рішення `pending`, але факт людського
  override/approval поки не надходить як подія в `audit.decisions`.
* Жодних змін у `apps/`; живу БД перевірено локальним PostgreSQL harness, не production-сервером.

### Наступне

1. Перевірити audit inserts у серверному середовищі після розгортання; Mem0 залишається окремим
   рішенням користувача.
2. Людині відкликати PAT із публічного `EVA_SYNDICATE_FULL_DIALOGUE.txt` та вирішити долю файла.

### Ризики й спостереження

* Якщо таблиці/права/БД недоступні, task продовжується без durable рядка; логи показують лише
  тип помилки. Для Zero-Trust deployment варто моніторити такі `durable_audit_write_failed`
  події й алертити на деградацію аудиту.

---

## 2026-10-06 — Arena Agent: пам'ять агентів, N8N HITL і SKILL.md

**Гілка:** `arena/0f6034ef-eva-syndicate` · **Коміт:** delivery commit цієї гілки · **Ворота:** ✅ `bash tools/check.sh`

### Зроблено

* **Пам'ять решти агентів:** Doc, Kira, Fin, Sam і Marshal мають bounded recall та outcome-save
  з окремим agent ID; історія редагується від PII до prompt/save. Медичні, фінансові,
  торгові й security facts позначаються як історичні та не підміняють актуальні виміри,
  ринок чи security decision. Явний top-level `session_id` є авторитетним, навіть якщо
  у payload прийшов інший ID.
* **N8N approval gate:** Architect тримає workflow `active=false` і створює Markdown Change
  Request. `gitops_sync` формує bundle тільки для workflow з CR у стані `applied`, коли
  fingerprint точно збігається й FlowLint проходить. Pending, approved-but-not-applied,
  rejected, altered або active payload-и блокуються. Жодної автоматичної активації n8n немає.
* **SKILL.md:** `src/skill_store.py` записує явний skill candidate після успішної задачі в
  `agents/<agent>/skills/<slug>/SKILL.md`, маскує PII, дедуплікує task ID і відкриває нотатку
  як `verified` лише після двох різних успішних task ID. Kira генерує безпечний кандидат
  після Socratic dialogue; оркестратор відкидає caller-injected notes і поки передає
  релевантні verified skills лише Kira як неповноважні підказки. Медичні, фінансові,
  trading і security decision paths не отримують learned procedures.
* Regression-тести покривають п'ять агентів, session propagation, pending/applied/rejected
  та fingerprint/active N8N gate, skill capture/redaction/dedup/retrieval. `pytest tests/`:
  **451 passed, 1 skipped**; повний `bash tools/check.sh` завершився успішно.

### Не дороблено / свідомо залишено

* Mem0 не впроваджували: це окрема залежність і окреме рішення; bounded token budget та
  SKILL.md layer не залежать від Mem0.
* Docker/n8n у пісковиці не запускали. Approval release перевірено логічно й тестами;
  реальне розгортання потребує серверної перевірки, а активація лишається дією оператора.
* Людині потрібно відкликати PAT із публічного `EVA_SYNDICATE_FULL_DIALOGUE.txt` і вирішити
  долю файлу; секрет не використовувати й не копіювати.

### Наступне

1. На сервері перевірити стек по одному сервісу, включно з embeddings і n8n; не активувати
   workflow до окремого рішення оператора.
2. За рішенням Андрія визначити, чи потрібен Mem0, і вирішити долю публічного діалогу.

### Ризики й спостереження

* `ChangeRequestStore` у цьому флоу — Markdown approval record у Vault; застосування CR
  оператором не виконується автоматично кодом Architect.
* Нова пам'ять і skills деградують без блокування основної задачі, якщо їхній бекенд недоступний.

---

## 2026-10-06 — Arena Agent (сесія 11, продовження 5): Vault — політики, AppRole, відсутність плейсхолдерів

**Гілка:** `arena/01a10d4e-eva-syndicate` · **Коміт:** локальний · **Ворота:** ✅ (**435 тестів**, +26)

Пункт 32 беклогу — той, що Андрій просив вирішити в перших чергах («це безпекова складова»).

### Зроблено

**1. Політики більше не пишуться руками.** Були heredoc-и всередині `vault_init.sh`, і
рантайм-політика давала `secret/data/eva-syndicate/*` — тобто **всі** секрети одному токену,
включно з ключами інших агентів і будь-чим, доданим пізніше. Тепер:

* `tools/vault_policies.py` генерує `config/vault/policies/*.hcl` з `src/vault_paths.py`
  (єдине джерело правди); `vault_init.sh` лише **завантажує** файли;
* на **кожен поверх** своя least-privilege політика: `eva-marshal` бачить `mcp`+`telegram`,
  `eva-fin` — `google_workspace`, `eva-doc`/`eva-kira`/`eva-sam` — нічого, крім
  інфраструктури (`database`, `redis`, `api-keys`) і власної гілки `agents/<id>/*`;
  жодна агентська політика не дає `auth` (ключ API самого сервера) і не дає гілку іншого агента;
* `--check` (новий крок у `tools/check.sh`) ловить три речі: застарілий файл, сервіс, який код
  читає, але `vault_paths` не оголошує, і **будь-який** grant на весь префікс. Сканер бачить
  не лише `secret_path("x")`, а й конектори (`SERVICE_NAME = "x"`) і голос
  (`read_vault_secret(..., "x")`) — 11 сервісів;
* AppRole створюється **на кожну політику**, тож коли поверх переїде в окремий контейнер
  (крок 4/5 плану), йому треба лише інші `VAULT_ROLE_ID/SECRET_ID` — без змін у коді.

**2. Плейсхолдери прибрані з обох боків.**

* `vault_init.sh` більше **не вигадує** секретів: `POSTGRES_PASSWORD`/`REDIS_PASSWORD` беруться
  з `.env` (ті самі, з якими стартували контейнери — це і є класична причина «Vault vs БД
  mismatch»), і скрипт **відмовляється працювати**, якщо там `CHANGE_ME`/`PLACEHOLDER`;
  LLM-ключі зберігаються лише ті, що передані змінними (чого немає — того немає, і агент
  чесно звітує LLM `unavailable`); `api_key`/`webhook_secret` генеруються випадково;
  root-token **відкликається** наприкінці (`KEEP_ROOT_TOKEN=1` — щоб лишити).
* `VaultClient.get_secret()` відкидає значення-заглушки й порожні рядки й пише
  `vault_placeholder_secret_ignored`. Доти вісім викликів мали кожен свою перевірку, і дев'ята
  завжди була відсутня.
* `/health` → `vault_placeholder_secrets: ["secret/data/...:<key>"]` (назви ключів, не
  значення). `_require_secret()` у рантаймі тепер називає шлях і пояснює, що плейсхолдер —
  це відсутність, замість голого `KeyError: 'password'` у трейсбеку.

**3. Скрипт уперше виконується.** У пісковиці немає ні Vault, ні Docker, тому
`deploy/scripts/vault_init.sh` ніколи не запускався. `tests/live_vault.py` піднімає фейковий
Vault API (справжні конверти KV v2, AppRole, політик, audit, unseal) і проганяє скрипт
наскрізно. Перше ж виконання знайшло дві реальні речі: (а) порожня відповідь `sys/init`
мовчки писала 1-байтовий файл і «розпечатувала» порожніми ключами — тепер є guard;
(б) `role_id`/`secret_id` могли бути `null` і потрапити у файл креденшлів — теж guard.

### Не дороблено / свідомо залишено

* Рантайм-політика (`eva-agent`) поки бачить усі поверхи: вони живуть в **одному процесі**.
  Це задокументовано в шапці згенерованої політики й у рунбуку §4.6; перехід на per-agent
  контейнери не потребує змін у коді.
* `vault_unseal.sh` не чіпав (працює), але його теж варто покрити моком.
* Автоматичний unseal після рестарту (HashiCorp Auto-Unseal / транзитний ключ) не робили:
  зараз це ручний крок 8 рунбуку. Для одно-серверного VPS це прийнятно, але це точка відмови.

### Наступне

0. **Пункт 37 беклогу (новий):** ключі `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `XAI_API_KEY`,
   `TELEGRAM_BOT_TOKEN`, `MONOBANK_API_TOKEN`, `PRIVATBANK_PASSWORD`, `EMBEDDINGS_TOKEN`
   читаються напряму з env, тому політики Vault їх не захищають. Сам `agent_runner` має
   правильний порядок (Vault → env) — проблема в модулях, що пішли повз
   `BaseConnector`/`read_vault_secret`.
1. **Пам'ять решти агентів** (пункт 4 плану) — `fin`, `kira`, `marshal`, `sam` поки читають
   пам'ять нуль разів, хоч пишуть.
2. **HITL-гейт для редактора N8N** (`src/agents/architect/n8n_builder.py`).
3. **SKILL.md** і токен-бюджет, далі Mem0 — з задуму лишаються нереалізованими.

### Ризики й спостереження

- Політика — це **deny by default**: новий конектор без оголошення в `src/vault_paths.py`
  отримає 403 на сервері. Саме тому `--check` є воротами, а не «перевіркою за бажанням».
- Знайдено й виправлено при написанні тестів: `vault_init.sh` замовчував користувача БД як
  `eva_agent`, тоді як компоуз і `.env.example` використовують `eva` (три місця в
  `docker-compose.yml`). Якби скрипт запустили без `POSTGRES_USER` у середовищі, Vault
  отримав би користувача, якого в БД немає, і агент не підключився б. Дефолт приведено до
  `eva`; у тестах перевіряється саме значення зі `.env`.

## 2026-10-06 — Arena Agent (сесія 11, продовження 4): чесність метрик

**Гілка:** `arena/01a10d4e-eva-syndicate` · **Коміт:** локальний · **Ворота:** ✅ (**409 тестів**, +16)

### Зроблено

Пункт 36 беклогу: «ніколи не вигадуй дані» порушувалось не лише в Sam-шарах, а й у медичній
лінії та в ранковому брифі. Кожне підставлене число замінено на чесну відсутність.

| Місце | Що підставлялось | Стало |
| :--- | :--- | :--- |
| `doc._morning_readiness` | HRV 50 мс, сон 7.5 год, якість 80, пульс 65, 8000 кроків, стрес 30 | жодного дефолту; без HRV **і** сну → `status: unavailable`, `score/zone = None` |
| `doc._morning_data` | те саме + впевнена «зелена» зона | прокидає `status`, `missing_inputs`, `warning` |
| `doc._training_protocol` | готовність 75 → «high, 60 хв» | без `readiness_score` інтенсивність і тривалість **не призначаються** |
| `doc._nutrition_plan` | 80 кг / 180 см / 35 р. / стать male / активність 1.55 | Mifflin-St Jeor лише на повних даних; невідома активність → `unavailable`, а не 1.55 |
| `doc._nervous_system` | стрес 60 → «фізіологічне зітхання» | без метрик — **неперсоналізований** протокол: `personalised: false`, `inputs: {hrv: None, stress: None}` |
| `doc._screening_calendar` | вік 35 → колоноскопія не пропонувалась | без віку — попередження, а не прихована рекомендація |
| `eva._compose_briefing` | «готовність 85/100 (green), ранвей 12 міс., всі 10 поверхів у штатному режимі» | `missing_inputs` + «дані відсутні» в тексті; `status: unavailable`, якщо немає жодного джерела |
| `eva._compose_reflection` | «день успішно завершено» без даних | «даних про відновлення та навчання немає» + `missing_inputs` |
| `orchestrator.proactive_evening_reflection` | Доку йшли HRV 62 / стрес 35 / сон 85 як виміри носимого пристрою | payload без біометрії — Док відповідає чесно |

Часткові дані не блокуються: ваги **перенормовуються** на те, що реально виміряно, результат
позначається `partial: true` + `warnings`. Математика за повного набору не змінилась (82.8 на
еталонному наборі — той самий бал, що й до правки).

Тести: 16 нових — `TestDocNeverInventsMetrics`, `TestEvaBriefingReportsAbsence`,
`TestScheduledJobsDoNotInventBiometrics`. `_morning_readiness` довелось розбити на дрібні
функції (`_readiness_metrics`, `_readiness_warnings`, `_readiness_zone`, шість `_score_*`),
бо C901 — тверді ворота, а `# noqa` заборонений.

### Наступне

1. **Vault (пункт 32)** — політики за агентами замість wildcard-токена; `vault_init.sh`
   досі містить `CHANGE_ME_BEFORE_PRODUCTION`.
2. Пам'ять решти агентів (пункт 4 плану), HITL-гейт для N8N, SKILL.md.
3. Репетиція відновлення з бекапу (пункт 35).

### Ризики й спостереження

- `_morning_readiness` тепер вимагає **хоч одне** з двох ядрових джерел (HRV або сон). Це
  свідоме рішення: один показник дає дуже вузьку основу для зони, тому `partial: true`
  обов'язково враховувати в тому, хто показує зону оператору.
- Незмінене: `proactive_daily_briefing` усе ще збирає `morning_data` з п'яти агентів, але
  тепер порожні відповіді доходять до Єви як «дані відсутні», а не як правдоподібні цифри.

## 2026-10-06 — Arena Agent (сесія 11, продовження 3): система бекапів

**Гілка:** `arena/01a10d4e-eva-syndicate` · **Коміт:** локальний · **Ворота:** ✅ (**393 тести**, +16)

Бекапи були прямим пунктом першого запиту Андрія (репл. #33 «Технік знімає бекапи») і мали
**нуль рядків коду** — лише три ad-hoc команди в рунбуці, які неможливо було запустити надійно.

### Зроблено

`tools/backup.py` — один набір із трьох артефактів, кожен зі своїм чесним статусом:

| Артефакт | Чому саме він |
| :--- | :--- |
| `postgres.dump` (`--format=custom`) | Єдині невідтворювані дані; `--format=custom` дає вибіркове відновлення, чого `pg_dump \| gzip` не вміє |
| `vault.snap` (Raft snapshot) | Без нього не буде паролів до БД, Redis і всіх API-ключів |
| `env.bootstrap` (`chmod 600`) | Без `.env` відновлення неможливе: unseal-матеріал і AppRole |

Ключові рішення:

- **Дамп верифікується** (`pg_restore --list`) до того, як набір уважається придатним.
  Це ловить пошкоджений дамп, який інакше виявився б у день відновлення. Немає `pg_restore`
  → артефакт лишається, але з позначкою «NOT verified», і набір не є `ok`.
- Крок, який не відбувся (немає інструмента, немає токена, немає DSN), — це **`unavailable`
  з причиною**, ніколи не «ok» і ніколи не тихий пропуск.
- `manifest.json` із sha256 і розмірами — набір можна перевірити через місяці.
- Exit code залежить **лише від дампу БД** (єдиний невідтворюваний артефакт), тому cron
  бачить збій ненульовим кодом.
- Retention видаляє лише **власні** каталоги формату `2026-01-01T00-00-00Z`; чужі не чіпає.
- `restic` — опційно; відсутній репозиторій або бінарник = `unavailable` з поясненням.

### Документація

- Runbook §10 переписано: запуск, cron і systemd timer, **окрема політика Vault лише на
  `sys/storage/raft/snapshot`** (не root-токен у cron).
- Runbook §10.1 — процедура відновлення у правильному порядку (Vault → `.env` → БД → стек)
  з перевіркою `sha256` і **обов'язковою репетицією**.
- Чек-ліст: замість галочки «налаштовано» — перевірювані вимоги (`status: ok`, верифікований
  дамп, відновлення на тестовій машині).
- `deploy/RESOURCE_CALCULATION.md`: виправлено **застарілі версії образів** (документ показував
  `vault:1.17`, `nginx:1.27`, `n8n:1.65`, `redis:7.2` — у compose `1.15`, `1.25`, `1.68.0`, `7-alpine`).

### Не дороблено

- **Відновлення жодного разу не виконувалось** — це неможливо зробити в пісковиці. §10.1
  містить процедуру; пункт 35 у BACKLOG фіксує, що потрібна репетиція.
- Розклад поки через cron/systemd; за задумом його має ініціювати Архітектор (пункт 35).

### Наступне

**Vault** (пункт 32 — Андрій просив у перших чергах): один wildcard-токен на всі секрети,
`vault_init.sh` досі кладе `CHANGE_ME_BEFORE_PRODUCTION` / `PLACEHOLDER_UPDATE_ME`.

---

## 2026-10-06 — Arena Agent (сесія 11, продовження 2): векторна пам'ять — підключено BGE-M3

**Гілка:** `arena/01a10d4e-eva-syndicate` · **Коміт:** локальний · **Ворота:** ✅ (**377 тестів**, +21)

Рішення Андрія: **BGE-M3 локально** (не хмарний API) + індексувати **епізоди й уроки**.
Обґрунтування вибору: пам'ять Синдикату — це приватне життя (медицина, фінанси), а
маскування PII перед ембеддингом знищило б саме ті ідентифікатори, які потім треба шукати.
Локальна модель дає нульову ціну, відсутність витоку і кращий український retrieval.

### Чому це було обов'язково зараз

Розмірність вектора зашита у **7 місцях** (5 колонок у `init.sql`, 2 у `migration_v4.sql`).
Зміна провайдера після появи даних = перерахунок усієї пам'яті. Усі вектори були NULL, тому
це була **остання дешева мить** для зміни 1536 → 1024.

### Зроблено

| Шар | Що |
| :--- | :--- |
| Провайдер | `src/embeddings.py` — `HttpEmbeddingProvider` + `build_embedding_provider()`; відсутній `EMBEDDINGS_URL` = семантичний пошук вимкнено (підтримуваний режим, не помилка) |
| Валідація | Жорстка: чужий розмір, NaN/∞, нульовий вектор, неповна відповідь → `EmbeddingUnavailable`. Все це інакше **індексується без помилок і отруює пошук** |
| Пам'ять | `save_episode` сам рахує вектор; `build_memory_context(query_text=...)` шукає за змістом; `semantic` звітує про стан векторної половини окремо від епізодичної |
| Уроки | `record_lesson` рахує вектор із `kind: summary`; `check_before_action(action_text=...)` — векторна гілка була **мертвим кодом**, бо всі виклики передавали `action_embedding=None` |
| Схема | `init.sql`/`migration_v4.sql` → `vector(1024)`; нова `migration_v5_embeddings_1024.sql` (ідемпотентна, дропає/перебудовує HNSW, **відмовляється** конвертувати колонку з даними, бо 1536→1024 неможливо) |
| Сервіс | `deploy/runtime/embeddings_server.py` + `embeddings.Dockerfile` (CPU-only torch, non-root, модель у volume); у compose — тільки мережа `backend`, без портів, **свідомо не в `depends_on`** агента |
| Рантайм | `agent_runner` будує провайдера, передає в `MemoryManager` і `LessonsStore`, закриває на shutdown; `/health` показує `semantic_search_enabled` + `embedding_failures` (контракт перегенеровано) |
| Рефактор | `build_memory_context` став C901-складним (12) — розбито на `_empty_context`, `_resolve_query_embedding`, `_semantic_matches`, `_merge_candidates`, `_fill_budget`, `_render_context` (без `# noqa`) |

### Тести (+21)

- 15 регресійних: розмірність у коді ↔ схема ↔ compose; валідація (розмір/NaN/нуль/неповна
  відповідь); недосяжний сервіс; деградація без втрати пам'яті.
- 8 живих на PostgreSQL: усі векторні колонки = 1024; `migration_v5` ідемпотентна;
  **наскрізний пошук** (запис епізоду → вектор → семантичний збіг); **урок знаходиться за
  дією**; померлий ембедер не втрачає епізод і рахує збій; епізодичне читання працює, коли
  векторна половина впала (і каже, що саме впало).

### Не перевірено тут (і як перевірити на сервері)

`docker` у пісковиці немає, тому **сам сервіс ембеддингів і його образ не запускалися**.
Перший запуск на сервері:

```bash
docker compose -f deploy/docker-compose.yml --env-file .env build embeddings
docker compose -f deploy/docker-compose.yml --env-file .env up -d embeddings
docker compose -f deploy/docker-compose.yml --env-file .env logs -f embeddings   # завантаження ваг ~2 ГБ
curl -s http://127.0.0.1:8000/health   # зсередини мережі: {"status":"ok","dimensions":1024}
```

Якщо сервіс не піднімається — `EMBEDDINGS_URL=` (порожній) вимикає векторний пошук, і пам'ять
працює далі на епізодах. Це свідома страховка, а не аварійний режим.

### Наступне

Бекапи (пункт 3 плану) → Vault (пункт 32) → поширення пам'яті на решту агентів.

---

## 2026-10-06 — Arena Agent (сесія 11, продовження): Єва почала пам'ятати + Redis і Compose закриті

**Гілка:** `arena/01a10d4e-eva-syndicate` · **Коміт:** локальний · **Ворота:** ✅ (усі кроки зелені, живий PostgreSQL через `pgserver`)

Рішення Андрія цієї сесії: **Tetragon/eBPF = Фаза 2**; клієнтський додаток — **після повної
готовності до деплою на сервері**; **геолокація — абсолютний контроль** (працює лише за його
підтвердженням, інакше завжди вимкнена); **Vault — безпекова складова, вирішувати в перших
чергах**. Порядок робіт — «як ти знаєш краще», почали з пам'яті.

### Зроблено — пункт 1 плану: пам'ять Єви замкнено

- `MemoryManager.build_memory_context()` — блок спогадів для промпту: 20 епізодів, **жорсткий
  бюджет символів** (типово 4000 ≈ 1000 токенів), кожен епізод обрізається, `dropped`/`truncated`
  чесно звітують, скільки старіших не влізло. Це і є «пам'ятати все, не перечитуючи діалог».
- Єва **читає пам'ять перед відповіддю** і зберігає **обидві** репліки (раніше зберігалась
  тільки відповідь асистента — найцінніше, слова оператора, губилось).
- Контракт відсутності: «не змогли прочитати» → `unavailable` + `warning` (агент відповідає,
  але **не вдає**, що пам'ятає); «прочитали, там порожньо» → `ok` і порожній блок.
- `_ensure_uuid` узгоджено між читанням і записом (раніше `get_recent_episodes(None)` давав
  випадковий UUID — запис і читання дивились у різні сесії).

### Зроблено — пункт 2 плану: Redis більше не блокує деплой

- Пароль передається з `.env` через `--requirepass` при старті контейнера; у
  `config/redis/redis.conf` секрету **немає** (нема чого синхронізувати `sed`-ом).
- `_connect_redis` деградує до «кеш вимкнено» замість фатального старту; кеш-операції мають
  circuit-breaker; паролі в DSN маскуються в логах (`_redact_dsn`) — у репо вже був один витік.
- `rename-command` вимикає FLUSHALL/FLUSHDB/CONFIG/DEBUG/EVAL (GAP 5.8 заявляв це зробленим,
  але в конфізі цього не було).
- Runbook §2.3 переписано (замість `sed` по неіснуючому рядку), чек-ліст рядок 320 тепер
  перевіряє справжню поведінку (`PONG` з паролем, `NOAUTH` без).

### Зроблено — Compose (точний аудит, не awk)

- `yaml.safe_load` замість попередніх приблизних підрахунків. **`cap_drop: ALL` тепер на всіх
  7 сервісах** (було відсутнє на `vault` і `n8n` — виправлено; у `vault` збережено `cap_add: IPC_LOCK`).
- Під час правки було створено дубльований ключ `cap_add` — помічено й виправлено одразу
  (саме цей клас бага вже ловили в `eva-agent`); додано перевірку на дублікати в аудиті.

### Тести (усе зелене)

| Що | Де | К-сть |
| :--- | :--- | :--- |
| Пам'ять Єви (читання, обидві репліки, недоступність, бюджет, маскування DSN) | `tests/test_regressions.py::TestEvaMemoryLoop`, `TestMemoryContextBlock` | 11 |
| Збереження після перезапуску + бюджет на довгій історії (**живий PostgreSQL**) | `tests/test_postgres_paths.py::TestEvaRemembersAcrossRestart` | 2 |
| Redis опційний: старт без нього + circuit-breaker (**живий PostgreSQL**) | `tests/test_postgres_paths.py::TestRedisIsOptional` | 2 |
| Пароль Redis, lockdown команд, `cap_drop` на всіх сервісах | `tests/test_regressions.py::TestRepositoryHygiene` | 3 |

### Не дороблено / свідомо залишено

- **Пункт 3 плану (бекапи) не почато** — 0 рядків коду, це наступний крок.
- 🔴 **Генератора ембеддингів немає** (пункт 31): `content_vector` завжди NULL, тому векторний
  пошук недосяжний. Пам'ять тримається на епізодичному читанні — це чесно, але векторний шар
  або підключаємо, або прибираємо з документації.
- Vault (пункт 32) — не чіпано; Андрій просив вирішити в перших чергах.
- `nginx` без `user:` — усвідомлений компроміс (пункт 33), потребує рішення про
  `nginx-unprivileged`, яке неможливо перевірити без `docker` у пісковиці.

### Наступне

1. **Бекапи** (пункт 3): `pg_dump` + снапшот Vault + `restic`, розклад через Архітектора.
2. **Vault** (пункт 32): політики за агентами замість одного wildcard-токена.
3. Поширити пам'ять на решту агентів (`fin`, `doc`, `kira`, `sam`, `marshal`) — патерн уже є.
4. Гейт схвалення для N8N (пункт 26), далі SKILL.md-шар (пункт 27).

### Ризики й спостереження

- Пісковиця знову переклоновувалась: `.venv` і локальні коміти зникають, правки робочого
  дерева лишаються. **Комітити негайно.**
- `docker` у пісковиці немає, тому Compose перевірено парсером, тестами й читанням, але
  **не запуском**. Перший `docker compose up` на сервері лишається обов'язковою перевіркою.

---

## 2026-10-06 — Arena Agent (сесія 11): аудит задуму проти коду + 🔴 секрет у публічному репо

**Гілка:** `arena/01a10d4e-eva-syndicate` · **Коміт:** локальний · **Ворота:** ✅ (340 passed, 1 skipped, живий PostgreSQL через `pgserver`)

👉 **Повний передавальний документ: `docs/SESSION_11_HANDOFF.md`** (читати разом із цим записом).
Аудит задуму: `docs/VISION_VS_DIALOGUE_AUDIT.md`.

### 🔴 Першочергове — дія людини, не код

`EVA_SYNDICATE_FULL_DIALOGUE.txt` у **публічному** репозиторії (`main`, коміт `35b7926`)
містить **справжній GitHub PAT** `ghp_XSC2…Ut9` (рядки 5670 і 5756 — репліка #69 від 25.09).
Токен треба **відкликати** (Settings → Developer settings → PAT → Revoke). Інших справжніх
секретів у діалозі немає (перевірено `sk-ant-`, `sk-proj-`, `AIza`, Telegram-bot, `gsk_`,
`sk_live_`, приватні ключі). Згадки `ghp_` у `src/pii.py` / `flowlint.py` / тестах — regex-патерни.
Повне значення токена в нові файли **не копіювати**, лише замаскованим.

### Зроблено

- Прочитано **весь діалог проєкту** (18209 рядків, 260 реплік Андрія, 16 діб) — діставався
  через зовнішній веб-інструмент (raw-URL), бо пісковиця не має доступу до GitHub; локально
  відтворюється командою `git show origin/main:EVA_SYNDICATE_FULL_DIALOGUE.txt > /tmp/dialogue.txt`.
- `docs/VISION_VS_DIALOGUE_AUDIT.md` — таблиця «задум → рішення в діалозі → стан у коді».
- `docs/SESSION_11_HANDOFF.md` — стан репозиторію, перші команди, план, пастки, відкриті питання.
- Уточнено походження назви: **МАРШАЛ уперше в репліці #29 (22.09)**, не в аудиті 27.09 —
  перейменування ШЕРИФ → МАРШАЛ було свідомим і раннім (ШЕРИФ 14 згадок, МАРШАЛ 57).
- Перевірено стан репозиторію: усе з сесій 8–10 **уже в `main`**, крім чотирьох файлів
  (див. нижче); локальний клон **shallow**, тому перевірка родоводу гілок недостовірна.

### Знайдено (аудит)

- 🔴 **Єва пише пам'ять і ніколи її не читає:** `eva.py:116 save_episode` проти 0 викликів
  `get_recent_episodes` / `semantic_search`. Читання: eva 0, fin 0, kira 0, marshal 0, sam 0, doc 1.
  `MemoryManager` уміє читати — треба лише викликати. Це головна вимога першого запиту Андрія.
- 🔴 **Бекапи: 0 рядків коду** (`pg_dump`/`restic`/`borg` — жодного входження), хоч це пункт задуму.
- 🔴 **Redis блокує деплой:** немає `requirepass`, runbook §2.3 робить `sed` по неіснуючому рядку
  (мовчки), чек-ліст недосяжний, `ping()` без try/except валить старт.
- 🔴 **SKILL.md-шар і Mem0 відсутні** (0 входжень у `src/`), токен-бюджету/стиснення контексту немає.
- 🔴 **Tetragon/eBPF** — лише в специфікації, коду немає; суперечить поточним обмеженням compose.
- 🟨 **N8N-редактор** не має гейта схвалення, хоч задум вимагав «стартує лише після схвалення».

### Не дороблено / свідомо залишено

- **Чотири файли не запушені** (робота сесії 10 + документи сесії 11):
  `deploy/runtime/agent_runner.py`, `tests/test_regressions.py`, `docs/HANDOFF.md`,
  `docs/BACKLOG.md` + нові `docs/VISION_VS_DIALOGUE_AUDIT.md`, `docs/SESSION_11_HANDOFF.md`.
  Причина — сесія закрита для GitHub (PR злито). **Перша дія нової сесії: закомітити й запушити.**
- YAML-аудит Compose повним завантажувачем **не виконано** (у сесії 11 `pyyaml` не ставився);
  цифри `cap_drop`/`network` з попереднього проходу лишаються попередніми.
- Чернетку виправлень для Redis/бекапів **не писав** — спершу потрібне рішення Андрія
  про порядок робіт.

### Наступне

1. Відкликати токен (людина) і вирішити долю публічного діалогу.
2. Закомітити й запушити роботу сесій 10–11.
3. **Пункт 1 плану:** замкнути пам'ять Єви (`get_recent_episodes(20)` + `semantic_search`
   у промпт + тест на збереження після перезапуску).
4. Далі — Redis, бекапи, поширення пам'яті на решту агентів (деталі в `SESSION_11_HANDOFF.md`).

### Ризики й спостереження

- Репліка #258 діалогу твердить «кодова база у виробничому стані, незавершених правок немає» —
  того ж дня сервер не міг стартувати, а в дереві лежали незафіксовані зміни.
  **Висновок: «зелені тести» ≠ «працює на сервері».**
- Останні дві доби діалогу пішли на полірування кокпіта при заблокованому деплої —
  порядок робіт був перевернутий.
- Пісковиця переклоновується (≥5 разів за день): локальні коміти й `.venv` зникають,
  правки дерева лишаються. Комітити негайно.

---

## 2026-10-05 — Arena Agent (сесія 10): 🔴 сервер не міг стартувати + локальний запуск + `.env`

**Гілка:** `arena/01a10d4e-eva-syndicate` · **Коміт:** локальний (див. «Не дороблено») · **Ворота:** ✅

### 🔴 Головне: агент **не міг піднятися взагалі**

`@asynccontextmanager` стояв **двічі**: на `lifespan` (правильно) і на `_purge_device_tokens`
(залишок від рефактору `lifespan` у сесії 4 — тоді помітили, що декоратор «переїхав», і
повернули його на `lifespan`, але **не прибрали** з другої функції).

Наслідок: `lifespan`, крок 8b, робить `asyncio.create_task(_purge_device_tokens())`, а
декорована функція повертає `_AsyncGeneratorContextManager`, не корутину:

```
TypeError: a coroutine was expected, got <contextlib._AsyncGeneratorContextManager object>
```

Це летить у `except` → `Fatal startup error` → процес виходить. Тобто **навіть із робочим
Vault і БД агент не стартував**. Погодинне прибирання device-токенів також **ніколи не
виконувалось** — цикл `while True` не запускався жодного разу, тому в логах не було й натяку.

**Другий дефект поруч:** у `finally` скасовувався `device_purge_task`, а обнулявся
`vault_renewal_task` (копіпаста) — тобто скидався не той об'єкт.

**Чому ворота це не ловили:** жоден тест не торкався `lifespan`, Vault-оточення чи
`device_purge_task`. `grep` по `tests/` не давав нічого. Усі 308 тестів були зелені,
а система в продакшені не піднялась би.

### Зроблено

- Прибрано зайвий `@asynccontextmanager` з `_purge_device_tokens` (тепер звичайна корутина)
  + docstring пояснює, чому це критично, щоб не повторити.
- `finally` тепер обнуляє `device_purge_task` — той, що скасував.
- **Backlog 20:** `python deploy/runtime/agent_runner.py` працює без `PYTHONPATH`. Додано
  `sys.path` bootstrap за тим самим патерном, що вже є в `tools/export_openapi.py`
  (третісторонні імпорти — над блоком, проєктні — з `# noqa: E402`).
- **Backlog 21:** `.env` вантажиться з `override=False` (значення з Compose/systemd завжди
  перемагають), а `_vault_env()` замість голого `KeyError` називає **всі** відсутні змінні
  й вказує на runbook. Порожнє значення = відсутнє: Compose підставляє `""` для незаданої
  змінної, і порожній `VAULT_ADDR` інакше падав би значно пізніше незрозумілою помилкою
  з'єднання. `python-dotenv` перестав бути мертвою залежністю.

### Тести (11 нових, `TestAgentRunnerStartup`)

Кожен перевірено **проти коду до виправлення** — падає на старому, проходить на новому:

- `iscoroutinefunction(_purge_device_tokens)` + реальний `create_task()`
- `lifespan` досі є context manager (дзеркальний бік того ж збою)
- `finally` обнуляє саме `device_purge_task` (AST): на `HEAD` множина = `{vault_renewal_task}`
- прямий запуск у підпроцесі з **видаленим з `sys.path` коренем репо** — точно відтворює
  оригінальний `ModuleNotFoundError: No module named 'src'`
- помилка називає всі три змінні; порожнє значення = відсутнє
- `.env` вантажиться; `.env` **не** перекриває реальне оточення; відсутній `.env` не ламає старт

Перевірено наскрізно запуском сервера: без змінних — дієве повідомлення замість `KeyError`;
з `.env` (недосяжний Vault) — `dotenv_loaded` і старт доходить до спроби з'єднання.

### Не дороблено / свідомо залишено

- ⚠️ **Push у GitHub не відбувся:** сесію закрито для віддалених операцій, щойно її PR злито
  (`git fetch` → «This coding session has ended… Remote GitHub access is no longer available»).
  Коміт `e6c72cf` лежить **локально**. Щоб він потрапив у `main` — потрібна **нова сесія**,
  яка запушить цю гілку й відкриє PR. Це стосується і `d2d50d3` (він уже в `main` через PR #5).
- Повний `lifespan` досі не покритий інтеграційним тестом (потрібен fake Vault + fake БД).
  Захист зараз — модульні тести + AST. Кандидат у наступний крок.
- `shutdown` залишається inline у `finally`; винесення в `_shutdown(state)` зробило б його
  тестованим по-справжньому, а не через AST.

### Ризики й спостереження

- ⚠️ **Пісковиця знову скинулась між ходами.** Цього разу репозиторій **переклоновано з
  GitHub**, а моя гілка відтворена від базового `20ce936` з усіма змінами як
  *незакоміченими*. Перевірив `git hash-object` для 5 файлів з PR #3 і `git diff origin/main`
  для решти: вміст був **побайтово ідентичний** `main`, тому вирівняв гілку через
  `git reset --mixed origin/main` (робоче дерево не чіпалося, втрат нуль).
  **Висновок для наступних сесій:** після кожного скидання спершу порівнюй вміст з
  `origin/main`, а не довіряй стану гілки. `.venv` теж зникає — створювати наново.
- Ворота на цьому стані: **340 passed, 1 skipped** (308 базових + 11 нових + 25 живих SQL,
  які тепер реально виконуються через вбудований `pgserver`; раніше вони скіпались).
  Крок воріт «жива схема + SQL-шляхи» зелений, а не INFO.

---

## 2026-10-05 — Arena Agent (сесія 9): аудит працездатності + вигадані оцінки в confluence Sam

**Гілка:** `arena/01a10d4e-eva-syndicate` → `main` · **PR:** [#4](https://github.com/andrejzhivilov-ctrl/eva-syndicate/pull/4), злитий · **Ворота:** ✅

### Консолідація гілок (за запитом людини: «щоб усі зміни були в main»)

Стан на початок: **дві** відкриті PR від **двох паралельних Arena-сесій**, обидві
базувались на `20ce936`, і жодна не була в `main`.

- **PR #3** (`arena/01a10d46-eva-syndicate`) — від паралельної сесії: живі SQL-шляхи на
  PostgreSQL+pgvector і **перший у репозиторії CI** (backlog 6, 15, 16, 17).
  Перевірив у окремому worktree перед мерджем: ворота зелені, 288 passed + 22 skipped,
  PG-тести скіпаються **через `pytest.skip` з поясненням**, а не тихо «проходять».
  `.github/workflows/ci.yml` має `EVA_REQUIRE_LIVE_DB=1` — це ключове: відсутня БД
  стає помилкою, тому CI не може «позеленіти» на пропущених тестах. ✅ Злив у `main`.
- **PR #4** (моя гілка) — після злиття `main` у гілку конфлікт був **лише в документації**
  (`HANDOFF.md`, `BACKLOG.md`); код і `tests/test_regressions.py` злились автоматично
  (30 класів, 0 маркерів). ✅ Злив у `main`.
- **Пастка, яку треба знати:** обидві сесії незалежно назвались «сесія 8» і **обидві**
  зайняли пункти 17–19 у `BACKLOG.md`. Записи в HANDOFF зберіг обидва (порядок newest
  first), свій перенумерував на **сесію 9** і додав примітку про паралельність. У
  BACKLOG: 17–19 лишились за сесією 8, мої два залишки стали **20–21**, а мій пункт про
  відсутній CI зник — сесія 8 його реально закрила. Номери довелося перерозподіляти
  вручну; наступним агентам варто перевіряти BACKLOG перед вибором номера.
- **Видалено гілку `arena/01a10d46-eva-syndicate`** — перед видаленням перевірено
  `git merge-base --is-ancestor`: tip `fdf553e` є предком `main`, тобто втратити нічого.
- Прибрано тимчасові worktree (`/tmp/pr3`, `/tmp/mergetest`, `/tmp/maincheck`).

**Стан `main` після консолідації:** `393b9eb` — перевірено окремим worktree:
**308 passed + 22 skipped**, 10/10 floors, 8/8 sandbox, ruff чисто, контракт і compose
синхронні, `.github/workflows/ci.yml` на місці, робоче дерево чисте.

**Лишилось гілок на GitHub:** `main` і `arena/01a10d4e-eva-syndicate` (закріплена за цією
сесією — видаляти не можна). Застарілі `arena/01a10abd-eva-syndicate` і
`backup-stable-cockpit` уже не існують; їхній вміст — у тегах `archive/*`.

### Зроблено — аудит працездатності

Повний прогін воріт на чистому пісковиці (`.venv` створено заново — він не зберігається
між сесіями). Усе зелене: 279 pytest, 10/10 floors, 8/8 sandbox, ruff F/E9/B/E/W/C901
чисто, `api-contract.yaml` синхронний, `docker-compose.yml` синхронний,
`compileall` без помилок, всі 91 модуль імпортуються.

**Перевірено вручну й визнано коректним (не дефекти):**
- `src/integrations/banking.py` — пісочниця за `EVA_BANKING_SANDBOX=1`, завжди
  `synthetic: True`, плюс чесний порожній стан `status: "synced"` з 0 рахунків і
  поясненням. Вигаданих балансів без opt-in немає.
- `video_engine_v2` — `status: "ok"` тільки коли файл реально існує; збій Edge-TTS
  потрапляє у `warnings` як `voiceover_unavailable`, а не ховається.
- `datetime.utcnow()` — 0 випадків; усі `_utcnow()` використовують `datetime.now(timezone.utc)`.
- `config/postgres/init.sql` vs `migration_v4.sql` — блок `auth.device_tokens` ідентичний
  в обох (як і заявлено). Різниця набору об'єктів — за задумом: bootstrap vs інкрементальна міграція.

### Зроблено — виправлено вигадані оцінки (порушення §1 AGENTS.md)

Аудит знайшов **п'ять** шарів confluence у Sam, які перетворювали **відсутність даних на
числову оцінку**. Гірший — `news_shield`: «чорнолебедний щит» **відмовляв у бік дозволу**
(score 80/100, без veto), коли економічний календар невідомий. Це годувало гейт 95%.

| Шар | Було | Стало |
|---|---|---|
| `news_shield_layer` | `None` → **80.0**, без veto, «calendar clear / unknown» | `unavailable=True`, 0.0. «Clear» лише за явного `news_calendar_checked: True` |
| `smc_layer` | Деривація неможлива → **0.0** «no structural confluence detected» | `unavailable=True` з причиною (нема бібліотеки / нема свічок / нема флагів / збій) |
| `macro_layer` | Порожній payload → **40.0** «neutral / insufficient data» | `unavailable=True`, 0.0 |
| `cot_layer` | Немає данних → **45.0** «no fresh COT flow» | `unavailable=True`, 0.0 |
| `derivatives_layer` | n/a → **50.0**, без funding → **45.0** | `unavailable=True`, 0.0 |

- `src/agents/sam/confluence.py`: `LayerScore` отримав `unavailable: bool`. Рухоме
  вікно трактує такий шар **точно як неоцінений**: `score: None`, `missing: True`,
  нульовий внесок, без масштабування вгору. Це вже була задокументована філософія
  рухомого вікна («incomplete picture cannot accidentally clear a high gate») — п'ять
  шарів її просто обходили.
- `_derive_smc_features` більше не має трьох `except Exception: pass`: він повертає
  `(features, failed_flags)`, і будь-яка невдала проба чесно позначає шар як недоступний.
  Раніше один збій бібліотеки тихо прибирав один флаг — а «флага немає» читалось як
  «структури немає», тобто як ведмежий сигнал.
- **Розрізнено два різні факти:** «перевірили й нічого не знайшли» — це справжній бал,
  а «не змогли прочитати» — `unavailable`. Тести фіксують обидві гілки.

Тести: `tests/test_regressions.py` → клас `TestConfluenceAbsenceIsNotAnObservation` (20 тестів).

### Наслідок для поведінки (важливо)

Сетап, у якому виклик не передав реальних даних, тепер дає confluence **0.0**, а не ~40.
Це навмисно: щоб пройти гейт 95, потрібні реальні вхідні дані в усіх п'яти шарах, а не
бали за замовчуванням. `requires_hitl` завжди `True`, `auto_execute` завжди `False`.

Перевірено наскрізно через `SamAgent.evaluate_setup`:
- без даних → `score 0.0`, `passes False`, усі 5 шарів `missing: True`;
- з повними реальними даними → `score 82.0`, `passes False` (бо 82 < 95 — чесно).

### Не дороблено / свідомо залишено

- **`macro_layer`/`cot_layer` rate-limits не чіпав** — якщо колись з'явиться реальний
  фетчер календаря/COT, він має передавати `news_calendar_checked` і `noncommercial_net_change`.
- Порогова логіка гейта (95) і ваги шарів не змінювалися.

### Наступне (знайдено аудитом, не виправлено)

1. ✅ **CI закрито паралельною сесією** (PR #3, `.github/workflows/ci.yml`, два job'и:
   ворота без БД і PostgreSQL+pgvector з `EVA_REQUIRE_LIVE_DB=1`). Цей пункт більше не діє.
2. **`python deploy/runtime/agent_runner.py` падає** з `ModuleNotFoundError: No module named 'src'`:
   блок `if __name__ == "__main__"` не додає корінь репозиторію в `sys.path`. У контейнері
   (`PYTHONPATH=/app`, `uvicorn runtime.agent_runner:app`) усе гаразд, і тести додають шляхи
   самі, тому ворота цього не бачать. → **backlog 20**
3. **`VAULT_ADDR` відсутній → `KeyError: 'VAULT_ADDR'`** — криптична помилка замість
   зрозумілого повідомлення; `python-dotenv` є в залежностях, але `.env` на старті не читається.
   → **backlog 21**
4. ✅ **SQL-гілки `TradeJournal` покрито** паралельною сесією (`tests/test_postgres_paths.py`,
   25 живих тестів). Backlog 16 закрито.
5. ⚠️ **CI запускається лише якщо GitHub Actions увімкнено для репозиторію.** Сесія 8 бачила
   зелений run (37356237399), але локально перевірити це неможливо. Якщо Actions вимкнено —
   файл є, а воріт немає. Варто переконатися в налаштуваннях репозиторію.

### Ризики й спостереження

- ⚠️ `.venv` **не переноситься** між сесіями пісковиці (він у списку виключень): кожну
  сесію треба `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt pytest ruff`.
- ⚠️ `news_shield` при `minutes_to_high_impact=None` тепер `unavailable`. Якщо десь у
  замовника є виклик, який свідомо означав «подій немає», його треба оновити на
  `news_calendar_checked: True` — інакше такий сетап більше не набере балів. Це безпечний
  напрямок (fail-closed), але про це треба сказати Antigravity, якщо вона будує UI поверх цього.
## 2026-10-05 — Arena Agent (сесія 8): живий PostgreSQL+pgvector замість статичної перевірки схеми

**Гілка:** `arena/01a10d46-eva-syndicate` · **Ворота:** ✅ (`tools/check.sh`, включно з новим кроком «жива схема + SQL-шляхи»)

| | |
|---|---|
| Тести | **309** (284 без БД + **25 живих SQL**) |
| Наскрізні suite'и | 🏆 10/10 floors · 🏆 8/8 sandbox |
| Лінтер | `ruff F,E9,B,C901,E,W` — чисто |
| Жива БД у воротах | ✅ PostgreSQL 16 + pgvector 0.6.2 (локально `pgserver`, у CI — `pgvector/pgvector:pg16`) |
| CI на GitHub | ✅ обидва job'и зелені (PR #3, run 37356237399) |

### Зроблено (backlog 6 + 16)
- **Кожна SQL-гілка в `src/` мала `# pragma: no cover - needs live DB` і перевірялася лише
  статично проти `init.sql`. Тепер вони виконуються на справжньому сервері.**
  `tests/live_pg.py` піднімає PostgreSQL+pgvector: у CI — сервіс-контейнер
  `pgvector/pgvector:pg16` через `EVA_TEST_DATABASE_URL`, локально — вбудовані бінарники
  `pgserver` (`requirements-dev.txt`, тому їх немає в рантайм-образі). `EVA_REQUIRE_LIVE_DB=1`
  перетворює skip на помилку — CI не може «пройти» на пропущених SQL-тестах.
- `tests/conftest.py` — session-фікстура `live_pg` (схема застосовується один раз; тести
  використовують унікальні ідентифікатори, нічого не чистячи у спільних таблицях).
- `tests/test_postgres_paths.py` — **25 тестів**: схема на живої БД (усі таблиці й індекси з
  `init.sql` реально існують), pgvector+HNSW, least-privilege роль `eva_agent` (INSERT без
  DELETE на журналі, write-only `audit.outbound_vetoes`), MemoryManager (епізоди з UUID5-
  нормалізацією, semantic search, response cache, чекпоїнти, LessonsStore), TradeJournal
  (запис сигналу, HITL-рішення, outcome, **фільтр negative constraints за символом — backlog 16**),
  DeviceTokenStore (enroll/verify/scope/touch/refresh/revoke/list/purge; у БД лише хеш).
- `.github/workflows/ci.yml` — job `gates` (без БД) + job `postgres` (сервіс pgvector,
  `EVA_REQUIRE_LIVE_DB=1`) + в обох перевірка «робоче дерево чисте після воріт».
- `tools/check.sh` — окремий крок PostgreSQL; без бази й без `pgserver` друкує INFO
  (чесно: «SQL-шляхи в цій сесії не перевірено»), а не мовчки пропускає.

### Знайдено живою базою (усе виправлено)
1. 🔴 **`MemoryManager.semantic_search` був повністю зламаний на справжній БД**: `(:agent_id IS NULL OR …)`
   → asyncpg `AmbiguousParameterError: could not determine data type of parameter $2`.
   Фікс: `CAST(:agent_id AS text) IS NULL` (тест ловить регресію).
2. 🔴 **`check_response_cache` — та сама помилка** (кеш відповідей / економія токенів не працював).
3. 🟠 **Схема не була replay-safe**: `init.sql` падав на повторному запуску
   (`DuplicateObject: trg_episodes_updated`), а `migration_v4.sql` не можна було застосувати
   поверх нього (`trg_social_contacts_updated`). Додано `DROP TRIGGER IF EXISTS` в обидва
   файли; перевірено на живої БД: повторний init (88 statements) і міграція поверх (44) — OK.
4. 🔴 **`MemoryManager` не мав `asyncpg`-пулу, який шукають `TradeJournal` і `DeviceTokenStore`**
   (`memory.pool`/`_pool`/`db_pool`). У продакшені обидва **тихо** писали в пам'ять:
   `auth.device_tokens` лишався порожнім (усі device-токени зникали після перезапуску, а це
   основа авторизації клієнтського додатка), журнал угод Сема не потрапляв у PostgreSQL.
   Додано пул; якщо його не вдалося створити — голосний warning із зазначенням наслідків.
   Redis тепер опційний (`redis_url=""` → `redis_cache_disabled`, читання йде в БД).

### Чесно
- **CI виконано на GitHub і він зелений** (PR #3, run
  [#37356237399](https://github.com/andrejzhivilov-ctrl/eva-syndicate/actions/runs/37356237399)):
  job `Gates (no database)` — 1m19s, job `PostgreSQL + pgvector (live SQL paths)` — 1m39s.
  Разом із прогоном додано строгий тест: коли `EVA_REQUIRE_LIVE_DB=1`, образ БД мусить мати **всі**
  розширення, які просить `init.sql`. Оскільки job зелений, `pgvector/pgvector:pg16` справді має
  `vector`, `uuid-ossp` і `pg_trgm` — жодного прихованого shim/skip у CI немає.
- Вбудований `pgserver` містить лише `plpgsql`+`vector`: harness ставить сумісну
  `uuid_generate_v4()` поверх ядрової `gen_random_uuid()` і пропускає `pg_trgm` **із зазначенням
  причини**; кожен пропуск видимий у `skipped_statements`.
- Прибрано 13 застарілих `# pragma: no cover - needs live DB` (`journal.py`, `device_auth.py`) —
  шляхи тепер реально покриті, а не позначені як «неможливі для тестування».
- Не робив: `pip-audit` (backlog 15), resumable-завантаження YouTube (P1), перевірку runbook на
  чистому VPS (потрібне залізо).

### Наступне
1. Antigravity — клієнт у `apps/` (бекенд-блокери 0.1–0.6 готові; контракт —
   `apps/shared/api-contract.yaml`).
2. AA — `pip-audit` у CI; новий пункт у backlog: `audit.decisions`/`audit.outbound_vetoes`
   ніхто не пише (аудит-слід Маршала живе лише в structlog, не в PostgreSQL).
3. 👤 — перевірити runbook на чистому VPS.

### Ризики й спостереження
- Другий пул з'єднань (`asyncpg` поруч із SQLAlchemy, `min_size=1`) — свідомо: `$1`-SQL
  компоненти не переписувати на SQLAlchemy в цій сесії.
- Тести піднімають тимчасовий кластер у `/tmp` на всю сесію pytest (у CI — сервіс-контейнер);
  `pgserver` тягне ~30 МБ бінарників, тому він тільки в `requirements-dev.txt`.
- Порядок тестів у `test_postgres_paths.py` не важливий (унікальні id), але `init.sql` та
  `migration_v4.sql` тепер ідемпотентні — повторний прогін не ламає спільну БД.

---

## 2026-10-05 — Arena Agent (сесія 7): консолідація гілок і видалення тимчасових артефактів

**База PR:** `main` на `3a3bab5` (PR #1 уже злитий) · **Ворота:** `tools/check.sh` — перевірено після очищення.

### Зроблено
- Через GitHub Compare перевірено повну досяжність backup-tip: `backup-stable-cockpit` на `7be2dda` має `ahead_by=0`, `behind_by=29` відносно `main`. Отже, старий tip і вся його історія вже входять до графа `main`; дерево cockpit v4.2 окремо не зливалося, щоб не перезаписати сучасну структуру. Попередня оцінка «736 комітів відсутні» була помилковою через shallow-клон і виправлена.
- Видалено remote-гілки `backup-stable-cockpit` і `arena/01a10abd-eva-syndicate`: їхні tip-коміти вже є предками `main`. Архівні теги зі snapshot'ами залишені.
- У GitHub лишилися `main` і закріплена за поточною Arena-сесією `arena/01a10d25-eva-syndicate`. Її видаляти/перемикати в цьому середовищі не можна; окремої app-гілки поки немає.
- Видалено застарілі відстежувані тестові виходи з `scratch/` і синтетичний `media/mockups/mockup_result.webp`. Додано ignore для `/scratch/`; тестові suite'и вже використовують тимчасові теки, а директорія mockup лишається runtime-виходом.

### Не змінювалося
- Історію Git не переписували, backup не копіювали в активне дерево; backup повністю зберігається в історії `main` та GitHub-тегах.
- У цій Arena-сесії не можна перейти на `main` чи пушити до неї напряму; подальші правки передаються через PR із закріпленої гілки.

---

## 2026-10-05 — Arena Agent (сесія 6): захист cockpit і реєстру поверхів

**Гілка:** `arena/01a10d25-eva-syndicate` · **PR:** [#1](https://github.com/andrejzhivilov-ctrl/eva-syndicate/pull/1), злитий 2026-10-05 (merge `3a3bab5`) · **Ворота:** ✅ (`tools/check.sh`)

### Зроблено (backlog 0.6)
- `GET /`, `/cockpit` і `/floors` тепер потребують мастер-ключ або device-токен зі
  скоупом `read`. Порожній/неповний скоуп не дає доступу; для сторінок повертається
  HTTP Basic challenge. У браузері: username `device`, password — read-токен; у нативному
  клієнті використовувати Bearer або `X-API-Key`.
- `require_read` не використовує приватний-IP dev-фолбек. Загальний auth-фолбек діє
  лише для прямих локальних з'єднань у dev/test; forwarded-запити (Nginx передає
  `X-Real-IP`/`X-Forwarded-For`) і production/staging fail-closed — інакше внутрішня IP
  адреса reverse proxy помилково довіряла б публічному клієнту. Device-admin ендпоінти
  fail-closed без мастер-ключа, щоб через проксі не можна було анонімно видати токен.
- Nginx проксіює `/cockpit` і `/floors` до FastAPI; старий статичний alias cockpit
  прибрано, `/cockpit/` зводиться до захищеного canonical URL, довільні підшляхи дають
  404. `/assets/` лишається публічним: це лише статичні зображення без даних оператора.
- OpenAPI-контракт оновлений із живої схеми; у тестах закріплені read-scope, Basic/Bearer,
  fail-closed без конфігурованого ключа та відсутність статичного Nginx-bypass.
- Документацію брифу й backlog оновлено. Для клієнта, якому потрібні inbox HITL і floor
  registry, видавати потрібні scopes разом (зокрема `read` + `hitl`); master key не
  вбудовувати у клієнт.

### Не дороблено / свідомо залишено
- `/assets/` публічний лише для вмісту `static/assets/`; туди не класти секрети чи дані.
- Справжній nginx binary не встановлений у sandbox, тому `nginx -t` локально не запускався;
  proxy-маршрути закріплені регресійним тестом конфігурації.

### Наступне
- Antigravity: реалізувати клієнт у `apps/` і передавати per-device токен відповідного
  скоупу; бекенд змін більше не потрібно для цього блоку.

### Ризики й спостереження
- У sandbox не було pytest/ruff та бібліотек проєкту; створено ігнороване `.venv`,
  встановлено `requirements.txt`, pytest і ruff. `tools/check.sh` тепер проходить.
- Поточна гілка починала з чистого diff відносно `origin/main`; виконано наступний
  незавершений пункт backlog (0.6), замість приписування змін базовому коміту.

---

## 2026-10-05 — Arena Agent (сесія 4): бекенд під клієнтський додаток

**Гілка:** `arena/01a10abd-eva-syndicate` → `main` · **Ворота:** ✅ (251 тест, 10/10, 8/8, ruff чисто, контракт узгоджений)

### Зроблено
- **`src/device_auth.py`** (новий модуль): per-device токени для ПК/смартфона.
  Логін мастер-ключем → короткоживучий скоупований токен (хеш зберігається, plaintext
  показується один раз), ротація (`/auth/device/refresh`), поштучне відкликання
  (`/auth/device/revoke`, тільки мастер-ключем). Мастер-ключ `EVA_API_KEY` більше
  **не треба** зашивати в клієнт — це закриває найбільший блокер безпеки додатка.
- **`deploy/runtime/agent_runner.py`**: увімкнено OpenAPI (`/openapi.json` + `/docs`),
  env-керований CORS (`EVAS_CORS_ORIGINS`, за замовчуванням закрито),
  `POST /execute/stream` (SSE з heartbeat-ами та безпечними заголовками), 4 endpoint'и
  керування пристроями. Авторизація приймає мастер-ключ **або** device-токен; адмінка
  пристроїв — тільки мастер-ключ (403 для токена).
- **`config/postgres/init.sql` + `migration_v4.sql`**: таблиця `auth.device_tokens`
  (схема, індекси, гранти) — у двох файлах ідентично, щоб пройшов тест на консистентність.
- **`tools/export_openapi.py`** (новий): генерує `apps/shared/api-contract.yaml` (+ JSON-близнюк)
  з живого коду; `--check` виявляє розбіжність (додано в `tools/check.sh`).
- **`tests/test_device_auth.py`** (новий, 42 тести): issuance/verify/revoke/refresh/scopes,
  HTTP-авторизація, whoami, OpenAPI/CORS, SSE-стрімінг. Усього тестів стало **251**.
- Виправлено тест-чекер SQL: коментарі з `;` більше не розрізають statement.

### Чесні застереження
- СТРІМІНГ поки що **тільки heartbeat** (liveness) — оркестратор надає лише `ainvoke`
  цілого графа, тому проміжних станів агента немає. Жодних вигаданих подій прогресу.
  Реальний прогрес з'явиться після переходу графа на `astream_events` (формат подій стабільний).
- `sse_starlette` **не** додавався як залежність — стрімінг на чистому `StreamingResponse`.

### Наступне
- Antigravity: гілка `app/client`, каркас Flutter + екран «реєстр поверхів» із `/floors`.
- 0.5 HITL-пуш, 0.6 закриття `/cockpit` `/floors` за reverse proxy — не зроблені.

### Ризики
- Під час рефактору `lifespan` випадково зсунув `@asynccontextmanager` на `_purge_device_tokens`
  і втратив декоратор на `lifespan` (депрекейшн-варнінг). Помітив і повернув — тести пройшли.

---

## 2026-10-05 — Arena Agent (сесія 5): HITL як поверхня підтвердження в додатку

**Гілка:** `arena/01a10abd-eva-syndicate` → `main` · **Ворота:** ✅ (271 тест: 210 базових + 41 device-auth + 20 hitl; 10/10, 8/8, ruff чисто, контракт узгоджений)

### Зроблено (блокер 0.5)
- **`src/change_requests.py`:** додано `ChangeRequestNotifier` (in-process pub/sub) і в'язання
  в `ChangeRequestStore` — `create()` публікує подію `pending_cr` (no-op без нотифаєра).
- **`deploy/runtime/agent_runner.py`:** inbox-ендпоінти `GET /cr/pending`, `GET /cr/list`,
  `GET /cr/{cr_id}`, SSE-пуш `GET /cr/stream`; `POST /cr/review` і `POST /cr/apply` тепер
  вимагають скоуп `hitl` (нова залежність `require_hitl`). Статичні HITL-роути оголошені
  **перед** `/cr/{cr_id}`, інакше Starlette з'їдає `/cr/stream`.
- **Скоуп-модель:** least-privilege — порожній список скоупів = НЕ успадковує все; явний
  скоуп обов'язковий. Загальний токен (`read`/`execute`) не може підтверджувати.
- **`tests/test_hitl_surface.py`** (новий, 20 тестів): inbox, detail, скоуп-енфорсмент,
  SSE-генератор (детерміновано, без live-socket — TestClient SSE зависає), OpenAPI.
- Контракт `apps/shared/api-contract.yaml` перегенеровано (26 paths, `--check` у CI).

### Чесні застереження
- **SSE — in-process.** Реальний OS-пуш (FCM/APNs) — окрема клієнтська інтеграція.
- Стрім видавав `heartbeat` кожні 30 с як liveness; прогрес агента поки не стрімиться.
- Уникнув вигаданих подій прогресу.

### Наступне
- 0.6: закрити `/cockpit`, `/floors` за reverse proxy (опційно).
- Antigravity: гілка `app/client`, каркас Flutter + екран inbox HITL (підписатися на `/cr/stream`,
  рендерити `/cr/pending`, кнопки Схвалити/Відхилити → `/cr/review`).

### Ризики
- Спочатку SSE-тести через `client.stream` **зависали** (Starlette TestClient + StreamingResponse).
  Переписав на пряме драйвінг генератора `_cr_event_stream` — детерміновано й швидко.

---

## Історичний знімок після сесії 5 (2026-10-05; актуальний стан — у сесії 7 вище)

| | |
|---|---|
| Основна гілка | `main` = `19521ee` |
| Інші гілки | `arena/01a10abd-eva-syndicate` (= main, сесійна), `backup-stable-cockpit` (`7be2dda`, існувала до аудиту) |
| Теги | 6, включно з `archive/pre-audit-main-5c85712`, `archive/cockpit-stable-7be2dda`, `archive/eva-syndicate-2026-10-05` |
| Тести | 271 (210 базових + 41 device-auth + 20 hitl) |
| Наскрізні suite'и | 🏆 10/10 floors · 🏆 8/8 sandbox |
| Лінтер | `ruff F,E9,B,C901,E,W` — чисто |
| Типи задач без помилки | 108 / 108 |

---

## 2026-10-05 — Arena Agent (сесія 3): консолідація гілок + бекап

**Гілка:** `arena/01a10abd-eva-syndicate` → `main` · **Коміт:** `19521ee` · **Ворота:** ✅

### Зроблено
- Усі правки аудиту злито в `main` (окремого merge не знадобилося: `main` і робоча гілка
  вже вказували на один коміт `19521ee`).
- Видалено технічну гілку `backup/main-2026-10-05` (`5c85712`) — вміст збережено у тезі
  `archive/pre-audit-main-5c85712` і в бекапі.
- Створено **три архівні теги**, які тримають усі коміти досяжними навіть без гілок:
  `archive/pre-audit-main-5c85712`, `archive/cockpit-stable-7be2dda`, `archive/eva-syndicate-2026-10-05`.
- Зроблено повний бекап репозиторію в `backup/full/` (73 МБ): bare mirror-клон, bundle,
  три zip-зрізи дерева, `MANIFEST.sha256`, `RESTORE.md`.
- Створено каркас для спільної роботи з Antigravity: `AGENTS.md`, цей файл,
  `docs/BACKLOG.md`, `tools/check.sh`.

### Не дороблено / свідомо залишено
- На GitHub залишилося **три** гілки, не одна — людина вирішила зберегти
  `arena/01a10abd-eva-syndicate` (сесійну) і `backup-stable-cockpit` (існувала до аудиту).
- **Виправлення за результатом сесії 7:** початкова оцінка, ніби `backup-stable-cockpit` (`7be2dda`) має 736 комітів, відсутніх у `main`, була помилковою через shallow-клон. GitHub Compare підтвердив, що `7be2dda` є спільною базою, а `main` на 29 комітів попереду; вся історія backup уже була досяжна з `main`. Дерево v4.2 не зливалося, бо це застаріла структура; remote branch пізніше видалено, архівні теги залишено.
- `docs/EVA_SYNDICATE_SYSTEM_PASSPORT.pdf` (6,3 МБ) знято з відстеження, але блоб лишився
  в історії. Для повного очищення потрібен Git LFS або переписування історії.

### Наступне
1. **Людина завантажує `backup/full/` собі** — пісковиця може бути очищена після сесії.
2. Доробити пункти з `docs/BACKLOG.md` (рекомендації 2–5 див. нижче).
3. Коли Antigravity згенерує новий код — дати його гілку/PR на аудит.

### Ризики й спостереження
- ⚠️ **Робоча тека пісковиці двічі відкочувалася до базового коміту між сесіями.**
  Зникали незакомічені файли, `.venv`, одного разу — вже зроблений бекап.
  → **Усе важливе має лежати в git або в GitHub-тегах.** Дивись `AGENTS.md` §0.
- ⚠️ Локальний клон був **shallow (глибина 1)**. Перший зроблений bundle виявився
  неповним. Підсумковий створено з повного mirror-клону і перевірено
  (відновлення дало 758 комітів / 6 гілок / 6 тегів). Якщо робиш бекап сам —
  перевіряй `git rev-parse --is-shallow-repository` і `git rev-list --count main`.
- Легасі-сьюти (`test_10floors_architecture.py`, `sandbox_test.py`) **завжди завершуються
  з кодом 0**, навіть коли всередині помилки. Перевіряй банер `🏆`, а не `$?`.
  Це вже враховано в `tools/check.sh`.

---

## 2026-10-05 — Arena Agent (сесія 2): другий прохід аудиту

**Коміт:** `b4f443b` · **Ворота:** ✅

### Зроблено
- **Кореневу причину вигаданих балансів знайдено:** `integrations/banking.py` повертав
  портфель-заглушку (185400/42300/74200 UAH + 15000 USD) зі `status: "synced"`.
  Тепер пісочниця — лише за `EVA_BANKING_SANDBOX=1` і завжди з `synthetic: True`.
- Сфальшовані дані вичищено ще в 11 місцях: `publisher` (`mock_success` → `not_published`,
  `MOCK_YT_ID_1048` → `not_implemented`), `grok_writer` (захардкоджена canned-відповідь;
  різна обгортка в демо/бойовому режимі), `script_director` (шаблон завжди давав 21 с
  нарації незалежно від замовлення), `mockup_studio` (синтетичний артворк як «успіх»),
  `office_copilot` (демо-дані як реальні).
- 🔴 **Витік PII:** патерн IBAN покривав 27 символів, український — 29. Реальні IBAN
  доходили до зовнішнього LLM у відкритому вигляді.
- `negative_constraints(symbol=…)` приймав і ігнорував аргумент; `adr.py` — `TypeError`
  через `kind` у `**kwargs`; `caption_engine` — невалідні ASS-таймстампи й вихід за межі
  теки через `../`; `vault_client` — цикл поновлення токена вмирав від першої ж помилки мережі.
- **C901: 13 → 0.** Таблиці диспечеризації для marshal/sam/doc/architect/coordinator,
  винесені функції в `pii`, `flowlint`, `verifier`, `council`, `video_engine_v2`,
  `orchestrator.initialize`. Невідома дія тепер = явна помилка, а не тихий фолбек.
- Переглянуто вручну всі раніше не перевірені модулі.

### Наступне
- Реалізувати resumable-завантаження YouTube Data API v3 (зараз чесно `not_implemented`).
- Підняти PostgreSQL+pgvector у CI, щоб зняти `pragma: no cover` з SQL-гілок.

---

## 2026-10-05 — Arena Agent (сесія 1): перший аудит

**Коміти:** `3b31663`, `31082f9`, `7baa409` · **Ворота:** ✅

### Зроблено
- Повний аудит репозиторію: 74 помилки ruff → 0; 6 × `datetime.utcnow()` → 0.
- **Безпека:** самоапрув change request; Sam міг торгувати без людини; dev-фолбек auth
  пропускав публічні IP `172.32.x.x`.
- **HTTP 500:** `sensory_split_audio` (bytes у відповіді), `vault_reindex`, Edge-TTS валив
  Floor 2, несеріалізовувані результати `/execute`.
- **Логіка:** інвертований календар скринінгів; `morning_data_sam` мовчки зникав з брифінгу;
  ключі конфігурації Sam ігнорувалися; сесії Kira колізійно ключувалися.
- **Інфраструктура:** `src/data_paths.py` + `EVA_DATA_DIR` (read-only контейнер),
  втрачені моунти в compose, відсутній `Dockerfile.agent`, SIGTERM-обробник, що блокував
  `docker stop`, дедуплікація `init.sql` (18 таблиць / 39 індексів), три копії `cockpit.html`
  → симпосилання, `src/vault_paths.py` як єдине джерело шляхів секретів.
- Створено `tests/test_regressions.py` і `tests/test_all_task_types.py`.

---

## Домовленості між агентами

- **Antigravity** — будує: архітектура, нові агенти, нові поверхи.
- **Arena Agent** — перевіряє: аудит на сфальшовані дані, безпека, регресії,
  консолідація гілок, періодичні повні проходи.
- Ніколи не редагуємо `main` одночасно. Гілка → `tools/check.sh` → мердж → запис сюди.
- Правила для обох — у `AGENTS.md`. Що робити далі — у `docs/BACKLOG.md`.

## 2026-10-10 — KODEX, Док: нагадування, вправи, вендор, профіль

- **KODEX** (`src/agents/kodex.py`, `kodex_buttons.py`, `config/agents/kodex.profile.json`, `doc_core/KODEX_NOTES.md`): системний агент архівів; видалення двоетапне (лише Андрій); інтернет лише з його підтвердженням; `andrii_medical_vault` незмінний для всіх агентів (рішення KODEX — лише читання, потребує підтвердження Андрія). Профіль додано в `EXPECTED_IDS`.
- **Shared skill** `knowledge_base`: KODEX додано до читання й запису (файли без мітки).
- **Док**: нагадування о 13:10 і 19:10 (`doc_reminders.py`), показання цифрами, список добавок порожній — нічого не вигадується; вправи (`doc_exercises.py`, free-exercise-db, Unlicense).
- **Вендор**: `kodex_core/vendor/book-to-skill` (офіційний, MIT, 808 тестів пройдено), `doc_core/vendor/free-exercise-db` (Unlicense), `doc_core/vendor/open-exercisedb` (MIT). Кожен має `SOURCES.lock.yaml`.
- **Відкладено до деплою**: планувальник і доставка нагадувань, live-відео, голос, n8n моніторинг новин, транскрибація і переклад (рушій), Obsidian/NotebookLM/Drive/Sheets, Telegram-токен.
- **Відкрите**: підтвердити пороги харчування і зон; підтвердити «щоранку» з нагадуваннями; вирішити, чи вендорені набори вправ іти в базу зараз.

### Оновлення KODEX (рішення Андрія, 2026-10-10)

- Захист іде за **міткою файла** `andrii_protected`, а не за папкою. Попереднє правило «`andrii_medical_vault` незмінний» скасовано.
- Особисті завантаження Андрія мітяться автоматично: лише читання; видалення — лише через KODEX з підтвердженням Андрія.
- Файли без мітки: редагування, сортування, видалення — агентами й KODEX автоматично; усе йде у звіт Єві.
- Нагадування Доку: щодня о 13:10 і 19:10 (підтверджено).
- База знань (вправи, рецепти тощо) — вводиться при деплої. Вендоровані набори вправ лежать у репозиторії, але не завантажені в базу знань.
- Відкрите: Док (`DOC_KNOWLEDGE_PLAN.md`, `doc_knowledge.py`) досі має правило «лише читання» для `andrii_medical_vault` як роль Доку. Потрібне рішення: залишити чи прив'язати до мітки.

### Уточнення правил захисту (2026-10-10, остаточне)

- Медичний архів: **лише читання** для файлів з міткою `andrii_protected`; решта файлів архіву — за звичайними правилами.
- Мічені файли: переміщення дозволене (сортування); редагування і видалення — лише з дозволу Андрія.
- Особисте завантаження Андрія — мітка автоматично. Через KODEX — без мітки, з негайним попередженням (якщо не просили мітку); з такими файлами дозволені будь-які дії.
- Усі дії KODEX і агентів (редагування, переміщення, видалення) — у звіті для Єви.
- `doc_knowledge.py`: доступ Дока до медичного архіву прив'язано до мітки, а не до папки.
- Нагадування Доку — о 13:10 і 19:10, щодня (підтверджено).
- База знань при деплої.

### Пакет розгортання і злиття в main (2026-10-10)

- **Пакет розгортання:** `docs/DEPLOY_SYNDICATE.md` (що запускати, секрети, права, карта коду, відкрите). Серверні кроки — `DEPLOYMENT_RUNBOOK.md`.
- **Матриця прав:** `docs/PERMISSIONS_MATRIX.md` — генерується з `config/agents/*.profile.json` (`tools/export_permissions.py`), тест перевіряє відповідність.
- **KODEX:** завантаження через KODEX — без мітки за замовчуванням з попередженням; мітка — на прохання Андрія. Фото (jpg, png, webp, gif, bmp, tiff) — зберігаються; HEIC і аудіо (mp3, wav, m4a, flac, ogg, opus, aac, aiff…) — зберігаються, розпізнавання (OCR, транскрибація) — при деплої. Файли зберігаються в `KODEX_DATA_DIR` (не в git).
- **Єва:** YouTube (офіційний Data API) і YouTube Music оголошено в `external_sources` профілю, **не ввімкнено**. YouTube Music не має офіційного публічного API — рішення Андрія.
- **Сміття прибрано:** застарілі планові й аудитні записки перенесено в `docs/archive/`; кеші й `.venv` локальні, не в git.
- **Відкрите:** див. розділ 8 у `DEPLOY_SYNDICATE.md`.

### Стан на кінець сесії 2026-10-10 (для наступного чату)

- **`main`** — злито PR #7 (merge `b18c335`). Обидва джоби CI на `main` зелені: «Gates (no database)» і «PostgreSQL + pgvector».
- **Робоча копія:** `/home/user/syndicate`, гілка `arena/41a10104-syndicate` (вершина == `main` за змістом). Незакомічених змін немає, стешів немає. `.venv` і кеші видалено; для тестів створити заново: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt -r requirements-dev.txt -r requirements-fin.txt`.
- **Перевірка:** `bash tools/check.sh` — зелено (ruff, тести, контракт API, політики Vault, гігієна).
- **CI:** Gates ставить `requirements-fin.txt` (тести звітів Фіна потребують pptx/docx/xlsx); gates-джоб не піднімає pgserver (`EVA_SKIP_PGSERVER=1`), SQL-шляхи перевіряє джоб з pgvector.
- **Відома нестабільність:** `tests/test_postgres_paths.py::...durable_audit_decisions...` падав один раз у повному прогоні; у ізоляції 0/12. Причину червоного Gates на попередніх комітах не встановлено (журнали CI недоступні з пісочниці). Після змін Gates зелений у трьох прогонах з рядка.
- **Файли для розгортання:** `docs/DEPLOY_SYNDICATE.md`, `docs/PERMISSIONS_MATRIX.md`, `DEPLOYMENT_RUNBOOK.md`, `.env.example`.
- **Відкрите (Андрій):** YouTube для Єви (офіційний Data API) — вмикати чи ні; YouTube Music (офіційного API немає); пороги харчування Дока; журнал діалогу `EVA_SYNDICATE_FULL_DIALOGUE.txt` (1,8 МБ) — лишати чи архівувати; рушій транскрибації і OCR при деплої; Telegram-токени для Дока і KODEX.
- **Відкладено до деплою:** бази знань (вправи, рецепти, медичні протоколи), запуск runtime агентів, live-відео, голос, нагадування-планувальник Дока, n8n-моніторинг новин, Obsidian/NotebookLM/Drive/Sheets.
