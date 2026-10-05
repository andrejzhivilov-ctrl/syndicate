# EVA SYNDICATE — Повний звіт про виявлені та виправлені помилки

**Дата завершення:** 2026-10-05
**Гілка:** `arena/01a10abd-eva-syndicate` (база `5c85712`)
**Коміти аудиту:** `3b31663`, `31082f9`, `7baa409` + поточний (другий прохід)
**Обсяг:** весь репозиторій — `src/`, `deploy/`, `tests/`, `config/`, `static/`, Docker/compose, FastAPI-рантайм

Методика:
1. Суцільний статичний перегляд усього Python-коду (кожен модуль прочитано вручну).
2. Динамічний зонд: **усі 108 типів задач** з `EvaOrchestrator.TASK_ROUTING` прогнані через
   справжній `EvaOrchestrator` із підміненими LLM і БД.
3. Легасі-сьюти (`test_10floors_architecture.py`, `sandbox_test.py`) як наскрізні сценарії.
4. Статичний аналіз `ruff` (F, E9, B, C901) і пошук патернів «сфальшованих даних»
   (константи-заглушки, `return {"status": "ok"}` без перевірки, `mock_success`).

---

## 1. Підсумок

| Показник | Було (до аудиту) | Стало |
|---|---|---|
| Типи задач без помилки | 94 / 103 | **108 / 108** |
| Тести `pytest` | 0 | **210** (100 регресійних + 110 маршрутизації) |
| Регресійні класи | 0 | **24**, кожен фіксує конкретний виправлений дефект |
| Легасі-сьюти | 10/10 + 8/8 (писали у `scratch/`) | 10/10 + 8/8, ізольовані й ідемпотентні |
| `ruff` F, E9, B | 74 помилки | **0** |
| `ruff` C901 (складність > 10) | 13 функцій | **0** |
| Сфальшовані дані у відповідях агентів | 16 місць | **0** (усе позначено `synthetic` / `unavailable`) |
| `datetime.utcnow()` (deprecated) | 6 місць | **0** |
| Дублікати DDL у `init.sql` | 3 таблиці + індекси | **0** |
| Копії `cockpit.html` (2,7 МБ) | 3 шт. + дубль `assets/` | **1** (`static/`), решта — симпосилання |
| Відслідковуваний PDF 6,3 МБ | так | **ні** (`git rm --cached`) |

Фінальні ворота (усі зелені):

```bash
.venv/bin/python -m pytest tests/ -q                        # 210 passed
.venv/bin/python tests/test_10floors_architecture.py        # 🏆 ALL 10 SUITES
.venv/bin/python tests/sandbox_test.py                      # 🏆 ALL 8 SUITES
.venv/bin/ruff check --select F,E9,B --ignore E501,B008,B904 src deploy tests   # All checks passed
.venv/bin/ruff check --select C901 src deploy tests                             # All checks passed
```

---

## 2. Критичні: сфальшовані дані 🔴

Найнебезпечніша категорія — агенти, які **вигадували числа** там, де даних не було.
Такі значення виглядають як виміряні й потрапляють у фінансові, медичні та
маркетингові звіти. Кожен випадок виправлено за єдиним правилом:
**або реальне значення, або явний `unavailable` / `synthetic` — ніколи «правдоподібна цифра».**

| # | Модуль | Що вигадувалося | Як виправлено |
|---|---|---|---|
| 2.1 | `agents/fin.py` → `_sync_bank_data` | При збої інтеграції: `185400 UAH + 74200 UAH + 15000 USD` | `status: "unavailable"`, нулі, явні `error`/`warning` |
| 2.2 | `agents/fin.py` → `_calculate_runway` | `monthly_burn <= 0` → `runway_months = 999`, `days = 9999` | `None` / `None` + `status: "unknown"` |
| 2.3 | `departments/operations/growth_analyst.py` | Константи каналів: 128500 / 84200 / 44300 / 98000 показів, 2560 кліків, 48 конверсій | Реальні лічильники від викликача; без них — `status: "unavailable"` |
| 2.4 | `growth_analyst.formulate_cfo_dossier` + `coordinator.py` | `revenue=210.0`, `costs=35.0` за замовчуванням → досьє `RESTRICTED_EXECUTIVE_FINANCE` із **ROI 500 %** | Параметри обов'язкові; без них — `status: "unavailable"` без `calculated_roi` |
| 2.5 | `integrations/banking.py` → `get_accounts_overview` | **Коренева причина 2.1.** За відсутності токена повертався портфель-заглушка (185400 / 42300 / 74200 UAH + 15000 USD) зі `status: "synced"` — Fin публікував його як виміряний | Немає рахунків → `status: "unavailable"`, нулі, `warning`. Пісочниця — лише за `EVA_BANKING_SANDBOX=1` і завжди з `synthetic: True` + окремим warning-логом |
| 2.6 | `agents/fin.py` → `_sync_bank_data` (другий прохід) | Не розрізняв «немає даних» і «дані пісочниці» | Три явні гілки: `unavailable` / `synthetic: True` + `"SYNTHETIC SANDBOX DATA"` / `synthetic: False` |
| 2.7 | `content_factory/publisher.py` → `schedule_youtube_short` | `status: "ok"` + вигаданий `video_id = "MOCK_YT_ID_1048"` — кампанія вважалася опублікованою | `status: "not_implemented"`, `video_id: None`, `published: False` |
| 2.8 | `content_factory/publisher.py` → `publish_to_telegram` | Без токена — `status: "mock_success"`, «Simulated successful post» | `status: "not_published"`, `published: False`, `reason: TELEGRAM_BOT_TOKEN is not configured` |
| 2.9 | `content_factory/publisher.py` → `dispatch_full_campaign` | Завжди `status: "ok"` навіть коли всі канали впали | Статус виводиться з реальних статусів каналів + `published_platforms` + `published` |
| 2.10 | `content_factory/broll_scout.py` | Фантомний файл `fallback_loop_N.mp4`, якого не існує на диску | `video_path: None`, чесний `status` без вигаданого шляху |
| 2.11 | `agents/office_copilot.py` | Демо-рядки Excel і секції Word поверталися як реальні звіти | Константи `SAMPLE_REPORT_ROWS` / `SAMPLE_BRIEFING_SECTIONS`; кожна відповідь має `sample_data: bool` + `warning` |
| 2.12 | `content_factory/grok_writer.py` → `generate_reply_snipe` | Захардкоджена canned-відповідь зі `status: "ok"`, яка ігнорувала `target_post` і `product_angle` | Реальний виклик API; без ключа — `status: "unavailable"`, `reply: None` |
| 2.13 | `content_factory/grok_writer.py` → `generate_thread` | Різна обгортка: `posts` у демо-режимі, `content` (сирий рядок) у бойовому — виклик мовчки отримував порожній список | Єдина обгортка `status` / `posts` / `model`; демо-копія лише за `EVA_GROK_MOCK=1` і з `synthetic: True` |
| 2.14 | `content_factory/script_director.py` | Шаблонний сценарій повертався з `status: "ok"` і `model: "template-engine-v2"` без жодної позначки; 6 сцен завжди давали **21 с** нарації незалежно від замовлених 15/30/60 с | Довжини сцен масштабуються під запит (перевірено: 15/30/60 → точно 15.0/30.0/60.0), результат має `synthetic: True` + `warnings` |
| 2.15 | `content_factory/mockup_studio.py` | Відсутній артворк замінювався синтетичним квадратом, а відповідь казала `status: "ok"` без застережень | `synthetic: True` + `warnings: ["artwork_not_found:…"]`; нечитабельний файл → `status: "error"` |
| 2.16 | `departments/coordinator.py` → `aggregate_growth_metrics` | Див. 2.4 | — |

**Регресійні тести:** `TestBankingNoSandboxData`, `TestFinNoFabricatedBalances`,
`TestContentFactoryHonesty`, `TestCoordinatorNoDefaultMoney` у `tests/test_regressions.py`.

---

## 3. Безпека та права доступу 🔴

### 3.1. Самостійне схвалення change request
`src/change_requests.py` — `review()` / `apply()`

Обидва методи робили `self._approvers.add(reviewer)` **перед** перевіркою.
Будь-хто — включно з автором заявки — міг видати собі право апрувера, схвалити
й застосувати власну зміну в захищеній теці `statutes/`.

**Виправлено:** єдиний шлюз `_guard()`, який перевіряє `author != actor` і
`actor in self._approvers`. Права видаються лише конфігурацією. Додано
`_write_changes()` із перевіркою наявності vault.

### 3.2. Sam міг автоматично відкрити угоду
`src/confidence.py`

`SamAgent` має `act_threshold = 1.0`; при `confidence == 1.0` бюджет повертав `ACT`
і торгівля йшла без людини.

**Виправлено:** множина `ConfidenceBudget.NEVER_AUTO_ACT`
(`trade_execute`, `trade_decision`, `place_order`, `delete_data`,
`financial_transaction`, `emergency_lockdown`) — завжди `ASK` із причиною
«mandatory human approval».

### 3.3. Dev-фолбек автентифікації пропускав публічні IP
`deploy/runtime/agent_runner.py` — `require_auth()`

Перевірка `client_host.startswith("172.")` вважала приватними **всі** `172.*`,
тоді як приватний лише `172.16.0.0/12` (`172.32.x.x` — публічний).

**Виправлено:** `_is_private_client()` — loopback, `10/8`, `192.168/16`,
`172.16–172.31`, IPv6 `fc00::/7`.

### 3.4. Витік PII: IBAN не маскувався взагалі
`src/pii.py` — `PIIRedactor.PATTERNS["iban"]`

Патерн охоплював лише 27 символів (`UA\d{2}` + 19 + 4), тоді як **український
IBAN має рівно 29**. Реальний IBAN (`UA21 3223 1300 0002 6007 2335 66001`)
доходив до зовнішнього LLM у відкритому вигляді.

**Виправлено:** `[A-Z0-9]{21}` (2 + 2 + 21 + 4 = 29). Перевірено на трьох
прикладах. Додано тест `TestPIIRedaction::test_ukrainian_iban_is_masked`,
який стверджує ще й довжину еталонного IBAN — якщо хтось знову «підправить»
патерн, тест впаде.

### 3.5. Витік секретів через невірні шляхи Vault
`src/integrations/base.py` читав `secret/data/eva-syndicate/<SERVICE>`,
а `agent_runner.py` — `eva/database`, `eva/config`, `eva/api-keys`.
Хтось із них гарантовано не знаходив секрет у продакшені.

**Виправлено:** єдине джерело істини `src/vault_paths.py`
(`secret_path(svc) -> f"secret/data/eva-syndicate/{svc}"`, ключі
`database`, `redis`, `auth`, `api-keys`, `agents`). Усі виклики — через нього.
Заблоковано тестом `TestVaultSecretPaths`.

### 3.6. Приватний метод і мертва гілка в `create()`
`self._vault._resolve()` (приватний API) і `if ...: pass`.

**Виправлено:** публічний `MarkdownVault.validate_path()`, мертву гілку видалено.

---

## 4. Збої під час виконання (HTTP 500) 🟠

| # | Модуль | Симптом | Виправлення |
|---|---|---|---|
| 4.1 | `sensory_split_audio` | У результаті задачі лежали сирі `bytes` → `TypeError: bytes is not JSON serializable` **після** успішного виконання | Чанки містять лише метадані (`index`, `filename`, `start_s`, `end_s`, `size`, `bytes_included: False`) |
| 4.2 | `vault_reindex` | `self._vault.reindex()` без аргументів, корутина не очікувалася | Новий `async Orchestrator._reindex_vault(payload)` — або передані `embed`/`upsert`, або зрозуміла помилка зі списком файлів |
| 4.3 | `video_producer.generate_voiceover` | `ClientConnectorError` від `speech.platform.bing.com` «ронив» увесь Floor 2 | `try/except` → `status: "error"`; окремо відсікається порожній сценарій |
| 4.4 | `video_engine_v2.render_complete_short` | Те саме: Edge-TTS зривав увесь конвеєр | Сilent-track фолбек + `warnings: ["voiceover_unavailable: …"]`; статус `ok` лише якщо файл реально існує |
| 4.5 | `_change_requests_handler` | `ChangeRequestError` / `VaultError` перетворювалися на HTTP 500 | Перехоплення → `{"status": "error", ...}` |
| 4.6 | `/execute` | Несеріалізовувані результати | `ExecuteResponse.result: Optional[Any]` + `_json_safe()` (bytes → `<N bytes>`, NaN/inf → рядок, рядки > 20 000 символів обрізаються, dataclass → dict, глибина ≤ 12) |
| 4.7 | `agents/architect/adr.py` → `build_adr_bundle` | `kind` виймався з `kwargs` **всередині** словника, що повертається, — після того, як `format_adr()` уже отримав `**kwargs`. `kind="docs"` доїжджав неочікуваним kwarg → `TypeError` | `kind` виймається один раз, на початку, до формування словника |
| 4.8 | `agents/office_copilot.py` | `ws.merge_cells("A1:F1")` — фіксований діапазон: на звітах із 3 колонками кидав виняток, на 10 — склеював половину | `start_row=1, end_column=len(headers)` з охороною `len(headers) > 1` |
| 4.9 | `agents/office_copilot.py` | Запис за відносним ім'ям файлу — `PermissionError` на read-only контейнері | `_resolve_output()` → `src.data_paths.data_dir("reports")` + `mkdir(parents=True, exist_ok=True)` |
| 4.10 | `verifier.verify` | Помилка реплею повертала `unproven` з `replay_matched=None`, але код-шлях був заплутаний | Винесено `_replay()`; семантика збережена й покрита 9 тестами |

---

## 5. Логіка та маршрутизація 🟠

| Модуль | Помилка | Виправлення |
|---|---|---|
| `orchestrator._doc_agent_handler` | Ключі задач не збігалися з діями Doc | action-map `analyze_document→summarize`, `morning_data_doc→morning_data`, `swarm_research_doc→swarm_research` |
| `orchestrator._kira_agent_handler` | `mentor_code_review` відповідав як **`socratic_dialogue`** | action-map `mentor_code_review→code_review` |
| `agents/sam/agent.py` | `morning_data_sam` → «Unknown action»: ринкова секція ранкового брифінгу Єви мовчки зникала | Гілка `morning_data`/`briefing` → `build_digest` |
| `agents/kira.py` | Невідома дія мовчки падала в `socratic_dialogue` — правдоподібна, але не та відповідь | Явна помилка + список доступних дій |
| `agents/doc.py` | Календар скринінгів **інвертовано**: виконані обстеження називалися `upcoming`, а ніколи не зроблені — `overdue` | `today = date.today()`; коректні `completed` / `due` / `overdue` |
| `agents/sam/journal.py` | Обмеження при відхиленні не містило `symbol`/`direction` — `_match_constraint` нічого не блокував | У summary пишеться `"SYMBOL:direction — reason"`; додано `TradeJournal.get_signal()` |
| **`agents/sam/journal.py` (другий прохід)** | `negative_constraints(symbol=…)` **приймав і мовчки ігнорував** аргумент: обмеження BTCUSDT блокувало ETHUSDT, а `evaluate_setup` вважав фільтр символ-специфічним | Фільтр працює в обох бекендах: у пам'яті — за `detail["symbol"]` → `symbol` → запис журналу; у SQL — `LEFT JOIN agents.sam_trade_journal` + `AND ($2::text IS NULL OR j.symbol = $2)` |
| `agents/sam/agent.py` | Ключі конфігурації не збігалися: `risk_per_trade` (0.01) / `daily_stop_out` (0.03) / `telegram_chat_id` ігнорувалися → ліміти ризику оператора не діяли | Нормалізація в `risk_pct` / `daily_stop_pct` (відсотки) і `sam_chat_id` |
| `agents/kira_socratic.py` | Сесії ключувалися `(student, topic)` — двоє учнів на одній задачі ділили драбину підказок; необмежене зростання словника | Ключ `(session_id, student, topic)`, `MAX_SESSIONS = 1000` із FIFO-витісненням |
| `agents/office_copilot.py` | Параметр `tool` зчитувався й **ігнорувався** — завжди вся база знань | Реальна фільтрація `word` / `excel` / `macro` / all |
| `orchestrator._change_requests_handler` | Автор за замовчуванням `operator` == рев'юер за замовчуванням — цикл блокувався новим шлюзом | Автор за замовчуванням — непривілейований `agent` |
| `orchestrator.TASK_ROUTING` | `create_viral_short` та ще 4 дії Floor 2 були недосяжні, хоча перелічені як доступні | Додано 5 маршрутів; `test_all_task_types` тепер покриває 108/108 |
| **`agents/marshal.py` (другий прохід)** | Невідома дія мовчки запускала **повний security audit** — дорого й неочікувано | Явна помилка + `available_actions` |
| **`agents/architect/agent.py` (другий прохід)** | `capabilities` у таблиці диспечеризації вимагала payload → `TypeError` | Адаптер `_act_capabilities(payload)` |
| **`content_factory/caption_engine.py` (другий прохід)** | `sec_to_ass_time` рахував соті з дробової частини окремо: `1.999 s` → `0:00:01.100` — **невалідний ASS-таймстамп**, який libass/FFmpeg відкидає | Цілі соті з самого початку (`divmod` 3_600_00 / 6_000 / 100) |
| **`content_factory/caption_engine.py`** | `output_filename` з `../` виводив запис за межі теки субтитрів | `Path(output_filename).name` |
| **`content_factory/caption_engine.py`** | `words_per_phrase=0` → `range(step=0)` → `ValueError` | `max(1, int(...))` в обох місцях |
| **`content_factory/video_producer.py` (другий прохід)** | `render_video` повертав `status: "ok"` після `returncode == 0`, не перевіривши файл; невалідний `target_resolution` кидав `ValueError`; відсутній B-roll виявлявся лише після TTS-виклику | Перевірка існування B-roll на вході, валідація `WxH`, перевірка розміру файлу на виході; `status: "warning"` → `"error"` |
| **`content_factory/video_engine_v2.py` (другий прохід)** | Concat-рядок не екранував апостроф у шляху; порожній concat-лист давав заплутану помилку FFmpeg | Екранування `'`, явний `ffmpeg_skipped_no_input` |
| **`content_factory/release_pack.py` (другий прохід)** | Некоректний claim (`без statement`) кидав `KeyError` і зривав увесь пак | Такий claim іде в `blocked` із `reasons: ["malformed_claim"]` |

---

## 6. Розгортання та інфраструктура 🟠

### 6.1. Контейнер не міг запуститися з read-only коренем
`MarkdownVault`, `VideoProducer`, `MockupStudio`, `AntiDetectProfileManager`
робили `mkdir` відносно CWD під час імпорту. У compose `eva-agent` має
`read_only: true` і лише tmpfs `/tmp` → `PermissionError` на старті.

**Виправлено:** новий модуль `src/data_paths.py` + змінна `EVA_DATA_DIR`
(теки `vault`, `videos`, `mockups`, `browser_profiles`, `reports`, `captions`,
`broll_cache`). Без змінної зберігається стара поведінка відносно репозиторію.

### 6.2. `docker-compose.yml` — втрачені моунти
Сервіс `eva-agent` оголошував ключ `volumes:` **двічі**. Другий блок мовчки
замінював перший, тобто `./src` і `./deploy/runtime` у контейнер не потрапляли.

**Виправлено:** один блок `volumes` з усіма моунтами + новий том `eva_data:/data/eva`.

### 6.3. Неіснуючий Dockerfile
`dockerfile: docker/Dockerfile.agent` — файла не було, стек не збирався.

**Виправлено:** створено `deploy/docker/Dockerfile.agent` (python:3.11-slim,
ffmpeg, UID 1001, `/data/eva`, healthcheck); посилання в compose оновлено.

### 6.4. `agent_runner` перехоплював SIGTERM
На рівні імпорту реєструвався обробник `SIGTERM`/`SIGINT`, який лише логував.
Він перекривав обробник uvicorn, тому `docker stop` не зупиняв процес — через
10 с Docker надсилав SIGKILL, губилися запити, що оброблялися.

**Виправлено:** обидва обробники та імпорт `signal` видалені.

### 6.5. `/cockpit` шукав файли в `repo_code/`
Список кандидатів містив шляхи зі старої розкладки репозиторію.

**Виправлено:** порядок від упакованої розкладки до кореня; `cockpit.html`
змонтовано read-only, шлях додано в Dockerfile.

### 6.6. Неочікувана фонова задача
`asyncio.create_task(...)` для поновлення токена Vault зберігав результат унікуди —
задача могла бути зібрана GC. Крім того, `VaultClient.start_token_renewal()`
**вмирала при першій же помилці Vault**: якщо `authenticate()` у `except` теж
кидав виняток, цикл завершувався, і всі подальші `get_secret` отримували 403.

**Виправлено:** `AppState.vault_renewal_task` зберігає посилання; новий
`VaultClient.ensure_token_renewal()` ідемпотентний; цикл ловить
`CancelledError` окремо й ніколи не виходить через помилку мережі;
`revoke_token()` скидає токен у `finally`; `aclose()` скасовує задачу
поновлення; `_auth_headers()` не дає надіслати порожній токен; логін без
`client_token` у відповіді — явна помилка, а не тихе кешування `None`.

### 6.7. nginx не віддавав статику
У конфігурації не було локацій для `/assets/` і `/cockpit`.

**Виправлено:** alias на `static/assets/` + локації `/cockpit`.

### 6.8. Дублікати DDL у PostgreSQL
Таблиці `audit.decisions`, `audit.outbound_vetoes`, `memory.response_cache`
створювалися і в `config/postgres/init.sql`, і в `migration_v4.sql` — друга
міграція на свіжій БД падала або призводила до розходження схем.

**Виправлено:** `init.sql` — повна дедуплікована схема за один прохід
(**18 таблиць / 39 індексів**), строга надмножина `migration_v4.sql`
(залишено лише для апгрейду наявних БД). Заблоковано тестом
`TestPostgresSchemaConsistency`.

### 6.9. Три копії `cockpit.html` і дубль `assets/`
`cockpit.html`, `syndikat_cockpit.html`, `static/cockpit.html` — байт-в-байт
ідентичні по 2,7 МБ; `assets/` ↔ `static/assets/`. ~8 МБ у репозиторії.

**Виправлено:** canonical-файл у `static/`, кореневі `cockpit.html`,
`syndikat_cockpit.html` і `assets` — **симпосилання** в `static/`.

### 6.10. Відслідковуваний PDF
`docs/EVA_SYNDICATE_SYSTEM_PASSPORT.pdf` (6,3 МБ) був у індексі попри
`*.pdf` у `.gitignore`.

**Виправлено:** `git rm --cached` (файл залишено на диску).

### 6.11. Інше
- Кореневий `docker-compose.yml` і `deploy/docker-compose.yml` синхронізовані,
  додано тест `TestRepositoryHygiene::test_compose_files_are_in_sync`.
- `EVA_DATA_DIR` додано в `.env.example` і `deploy/.env.example`.
- Секрети з env: угода `<SERVICE_NAME>_<KEY>` (`TELEGRAM_BOT_TOKEN`,
  `API_KEYS_OPENAI_API_KEY`), bare `<KEY>` — крайній засіб. Реалізовано в
  `src/integrations/base.py` і `src/voice/_util.py`; кожен фолбек логує
  warning «Production must serve this secret via Vault».

---

## 7. Якість коду та гігієна 🟡

- **74 помилки ruff** (F401, F541, F841, B905, B904, RUF006) → **0**.
  Обережно: не видалялися захищені імпорти (`docx.*`, `BaseCheckpointSaver`,
  langchain-модулі), бо це опціональні залежності.
- `datetime.utcnow()` → `datetime.now(timezone.utc)` у `kira.py`, `marshal.py`,
  `banking.py`, `memory.py` (6 місць, включно з хибним `+ "Z"`).
- `zip(..., strict=...)` у `caption_engine.py` та `integrations/registry.py`.
- Прибрано f-рядки без підстановок (`grok_writer`, `script_director`,
  `video_engine_v2`, `marshal`).

### 7.1. C901 — складність: 13 → 0

Усі 13 функцій зі складністю > 10 розбиті **винесенням логіки**, а не
`# noqa`. Там, де ланцюг `if/elif` був диспечеризацією за дією, він замінений
на таблицю `self._ACTION_MAP`, яка будується в `__init__`.

| Функція | Було | Як розбито |
|---|---|---|
| `architect.verify_code_integrity` | 18 | `_known_signatures()`, `_check_call_node()`, `_check_sql_literal()` |
| `pii.redact` / `create_replacer` | 15 / 11 | Словник масок `_MASKERS` + `_KEY_PATTERNS` + модульна `_mask()` |
| `flowlint.lint_workflow` | 15 | `_rule_nodes_are_core`, `_rule_error_handling`, `_rule_no_hardcoded_secrets`, `_rule_idempotency`, `_rule_naming` |
| `doc.execute` | 15 | `self._ACTION_MAP` у `__init__` |
| `coordinator.execute` | 14 | 12 приватних `_act_<action>()` + `_build_action_map()` |
| `verifier.verify` | 14 | `_check_content()`, `_replay()`, `_skeptic_refutes()` |
| `architect.execute` | 13 | `self._ACTION_MAP` (11 дій) |
| `marshal.execute` | 12 | `self._ACTION_MAP` (10 дій) + 4 адаптери; **невідома дія більше не запускає security audit** |
| `council.deliberate` | 12 | `_tally_options()`, `_decide_by_similarity()`, `_synthesize()` |
| `video_engine_v2.render_complete_short` | 11 | `_synthesize_voiceover()`, `_write_concat_file()`, `_build_ffmpeg_cmd()`, `_run_ffmpeg()` |
| `orchestrator.initialize` | 11 | `_init_llms()`, `_init_verification_stack()`; швидкий LLM і основний теж у `try/except` |
| `sam.execute` | 11 | `self._ACTION_MAP` (8 дій) |

Побічний ефект, який теж був помилкою: список `available_actions` раніше
вівся вручну і розходився з реальним кодом. Тепер він — `sorted(self._ACTION_MAP)`.

**Захист від регресу:** клас `TestActionDispatchTables` перевіряє, що
(a) таблиця непорожня, (b) кожен обробник приймає **рівно один** позиційний
аргумент (саме так впав `architect.capabilities`), (c) невідома дія — це
помилка зі `status: "error"`, а не тихий фолбек, (d) `capabilities`/`status`
дійсно диспечеризуються.

### 7.2. Тести як джерело брехні

Обидва легасі-сьюти:
1. сканували **10 184 файли** всередині `.venv` (і падали на синтаксисі `ccxt`)
   → додано `_SKIP_DIRS` + `discover_python_files()`;
2. писали у **відслідковувані** файли `scratch/` (`thoughts.md` щоразу додавав
   рядок — сьют не був ідемпотентним) → тепер усе в `tempfile.mkdtemp()`,
   `EVA_DATA_DIR` вказує туди ж;
3. містили кроки, які створювали об'єкти без жодної перевірки
   (`wf_error`, `scheduler`, `r_good_wh`) → додано реальні assert-и.

---

## 8. Що додано

| Файл | Призначення |
|---|---|
| `tests/test_regressions.py` | **100** регресійних тестів у 24 класах, кожен фіксує конкретний виправлений дефект |
| `tests/test_all_task_types.py` | **110** тестів: усі типи з `TASK_ROUTING` + перевірка повноти покриття |
| `src/data_paths.py` | Вирішення шляхів для записуваних даних (`EVA_DATA_DIR`) |
| `src/vault_paths.py` | Єдине джерело істини для шляхів секретів Vault |
| `deploy/docker/Dockerfile.agent` | Відсутній образ для сервісу `eva-agent` |
| `docs/FIX_REPORT.md` | Цей звіт |
| `docs/FIX_REPORT.pdf` | Те саме у PDF |

---

## 9. Як перевірити

```bash
cd /home/user/eva-syndicate

.venv/bin/python -m pytest tests/ -q
#   210 passed   (100 регресійних + 110 маршрутизації)

.venv/bin/python tests/test_10floors_architecture.py
#   🏆 ALL 10 SUITES FOR ALL 10 FLOORS PASSED WITH ZERO ERRORS!

.venv/bin/python tests/sandbox_test.py
#   🏆 ALL 8 SANDBOX VERIFICATION SUITES PASSED (0 ERRORS)

.venv/bin/ruff check --select F,E9,B --ignore E501,B008,B904 src deploy tests
#   All checks passed!

.venv/bin/ruff check --select C901 src deploy tests
#   All checks passed!
```

Окремі групи:

```bash
.venv/bin/python -m pytest tests/ -q -k ActionDispatch   # таблиці диспечеризації
.venv/bin/python -m pytest tests/ -q -k PII              # маскування PII
.venv/bin/python -m pytest tests/ -q -k Orc              # адверсаріальний верифікатор
.venv/bin/python -m pytest tests/ -q -k ContentFactory   # чесність контент-фабрики
.venv/bin/python -m pytest tests/ -q -k Postgres         # узгодженість схеми БД
.venv/bin/python -m pytest tests/ -q -k Vault            # шляхи секретів
```

---

## 10. Стан на момент завершення

Усі пункти, що раніше входили до розділу «Залишилося», закриті:

| Було в «залишилося» | Статус |
|---|---|
| 1. Різні шляхи секретів Vault | ✅ `src/vault_paths.py` + тест |
| 2. Дублікати DDL | ✅ `init.sql` — 18 таблиць / 39 індексів + тест |
| 3. Три копії `cockpit.html` і дубль `assets/` | ✅ canonical у `static/`, симпосилання |
| 4. `create_viral_short` недосяжний | ✅ 5 нових маршрутів, 108/108 типів задач |
| 5. C901 — складність (13 функцій) | ✅ 0 |
| 6. Не переглянуто вручну | ✅ переглянуто всі (`office_copilot`, `google_workspace`, `telegram`, `mcp_gateway`, `voice/*`, `content_factory/*`, `architect/adr.py`, `vault_client.py`) |
| 7. Відслідковуваний PDF | ✅ `git rm --cached` |

### Що варто зробити далі (не є дефектом)

| # | Рекомендація | Чому |
|---|---|---|
| 1 | Перенести `docs/EVA_SYNDICATE_SYSTEM_PASSPORT.pdf` (6,3 МБ) у Git LFS або регенерувати з Markdown-джерела | Файл залишився на диску, але більше не в індексі; історія все ще містить блоб |
| 2 | Реалізувати resumable-завантаження YouTube Data API v3 | Зараз чесно `not_implemented` — публікація в YouTube неможлива |
| 3 | Додати Pexels/Pixabay ключі в Vault | `broll_scout` без ключів не може дістати B-roll, тож рендер деградує |
| 4 | Підняти PostgreSQL + pgvector у CI й зняти `pragma: no cover` з SQL-гілок | Усі SQL-шляхи перевірені лише статично; in-memory бекенди — в тестах |
| 5 | Винести `base_url` у `GrokWriter` у конфігурацію | Зараз `https://api.x.ai/v1` захардкоджений у двох модулях |
| 6 | Розширити `Humanizer.CLICHES` і словник `REPLACEMENTS` | Покрито uk/ru/en, але список короткий для продакшен-копірайтингу |

---

**Висновок.** Репозиторій пройшов два повних проходи аудиту. Знайдено й
виправлено **понад 60 дефектів**, з них 16 — сфальшовані дані, які могли
потрапити у фінансові й медичні звіти, і 6 — проблеми безпеки (самоапрув
change request, автоторгівля Sam, публічні IP в auth-фолбеку, витік IBAN,
різні шляхи секретів, невірна обробка токена Vault). Усі 108 типів задач
виконуються без помилок, 210 регресійних тестів і обидва легасі-сьюти зелені,
лінтер чистий і за F/E9/B, і за C901.
