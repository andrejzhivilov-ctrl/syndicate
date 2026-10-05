# EVA SYNDICATE — Звіт про виявлені та виправлені помилки

**Дата:** 2025-10-05 (сесія аудиту) · **Гілка:** `arena/01a10abd-eva-syndicate`
**Коміти:** `3b31663`, `31082f9` (база `5c85712`)

Методика: повний статичний перегляд `src/`, `deploy/`, `tests/`, Docker/compose-конфігу,
плюс динамічний зонд, який прогнав **усі 103 типи задач** з `TASK_ROUTING` через
справжній `EvaOrchestrator` із підміненими LLM і БД.

---

## 1. Підсумок

| Показник | Було | Стало |
|---|---|---|
| Типи задач, що виконуються без помилки | 94 / 103 | **103 / 103** |
| Тести (pytest) | 0 | **163** |
| Легасі-сьюти | 10/10 + 8/8 (писали в `scratch/`) | 10/10 + 8/8 (ізольовані, ідемпотентні) |
| Лінтер `ruff` (F, E9, B) | 74 помилки | **0** |
| `datetime.utcnow()` (deprecated) | 6 місць | **0** |

---

## 2. Критичні: сфальшовані дані 🔴

Найнебезпечніша категорія — агенти, які **вигадували числа** там, де даних не було.
Такі значення виглядають як виміряні й потрапляють у фінансові та медичні звіти.

### 2.1. FinAgent вигадував залишки на рахунках
`src/agents/fin.py` — `_sync_bank_data()`

При збої банківської інтеграції поверталося `185400 UAH + 74200 UAH + 15000 USD`.
На цих цифрах будувалися runway-звіт і CFO-досьє.

**Виправлено:** `status: "unavailable"`, нульові суми, явне поле `error` і
`warning: "Balances are NOT estimated"`. Шлях з явно переданими `accounts`
приводить баланси через `float()` і повертає `status: "ok"`.

### 2.2. FinAgent: фальшивий «нескінченний» runway
`src/agents/fin.py` — `_calculate_runway()`

При `monthly_burn <= 0` поверталося `runway_months = 999`, `runway_days = 9999`.

**Виправлено:** `runway_months = None`, `runway_days = None`, `status = "unknown"`
і пояснення в `alert`.

### 2.3. GrowthAnalyst: захардкоджені метрики каналів
`src/departments/operations/growth_analyst.py` — `aggregate_channel_performance()`

Повертав константи: 128 500 показів, 84 200, 44 300, 98 000; 2 560 кліків;
48 конверсій. Вони логувалися як реальні та йшли в CFO-досьє.

**Виправлено:** приймає реальні лічильники каналів від викликача, рахує CTR і
суми; без даних повертає `status: "unavailable"`, нулі та
`warning`. Жодного «оціненого» значення.

### 2.4. CFO-досьє з вигаданими грошима
`growth_analyst.formulate_cfo_dossier()` + `coordinator.py`

`payload.get("revenue", 210.0)` / `payload.get("costs", 35.0)` — досьє з міткою
`RESTRICTED_EXECUTIVE_FINANCE` і **зфабрикованим ROI 500 %**.

**Виправлено:** обидва параметри обов'язкові; без них — `status: "unavailable"`
без поля `calculated_roi`.

---

## 3. Безпека та права доступу 🔴

### 3.1. Самостійне схвалення change request
`src/change_requests.py` — `review()` / `apply()`

Обидва методи робили `self._approvers.add(reviewer)` **перед** перевіркою.
Будь-хто — включно з автором заявки — міг видати собі право апрувера,
схвалити і застосувати власну зміну в захищеній теці `statutes/`.

**Виправлено:** єдиний шлюз `_guard()`, який перевіряє
`author != actor` і `actor in self._approvers`. Права видаються лише конфігурацією.
Додано `_write_changes()`, що перевіряє наявність vault.

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
тоді як приватний лише `172.16.0.0/12` (наприклад, `172.32.x.x` — публічний).

**Виправлено:** `_is_private_client()` — loopback, `10/8`, `192.168/16`,
`172.16–172.31`, IPv6 `fc00::/7`.

### 3.4. Приватний метод і мертва гілка в `create()`
`self._vault._resolve()` (приватний API) і `if ...: pass`.

**Виправлено:** публічний `MarkdownVault.validate_path()`, мертву гілку видалено.

---

## 4. Збої під час виконання (HTTP 500) 🟠

### 4.1. `sensory_split_audio` повертав `bytes`
У результаті задачі лежали сирі байти → `TypeError: bytes is not JSON serializable`
**після** того, як задача вже виконалася.

**Виправлено:** чанки містять лише метадані
(`index`, `filename`, `start_s`, `end_s`, `size`, `bytes_included: False`).

### 4.2. `vault_reindex` — `TypeError`
`self._vault.reindex()` викликався без аргументів і ніколи не очікувався
(метод — корутина й вимагає `embed` + `upsert`).

**Виправлено:** новий `async Orchestrator._reindex_vault(payload)` — або викликає
передані `embed`/`upsert`, або повертає зрозумілу помилку зі списком файлів.

### 4.3. Edge-TTS «ронив» увесь Floor 2
`video_producer.generate_voiceover()` — `ClientConnectorError` від
`speech.platform.bing.com` поширювався назовні.

**Виправлено:** `try/except` → `{"status": "error", "message": "Edge-TTS synthesis unavailable: ..."}`;
окремо відсікається порожній сценарій (зайвий мережевий виклик).

### 4.4. Невалідні вхідні дані замість HTTP 500
`_change_requests_handler` тепер перехоплює `ChangeRequestError` / `VaultError` і
повертає `{"status": "error", ...}` замість винятку.

### 4.5. `/execute` і несеріалізовувані результати
`ExecuteResponse.result` розширено до `Optional[Any]`, значення проганяється через
новий `_json_safe()` (bytes → `<N bytes>`, NaN/inf → рядок, рядки > 20 000 символів
обрізаються, dataclass/`__dict__` — у словник, глибина ≤ 12).

---

## 5. Логіка та маршрутизація 🟠

| Модуль | Помилка | Виправлення |
|---|---|---|
| `orchestrator._doc_agent_handler` | ключі задач не збігалися з діями Doc → помилка / не та обробка | action-map `analyze_document→summarize`, `morning_data_doc→morning_data`, `swarm_research_doc→swarm_research` |
| `orchestrator._kira_agent_handler` | `mentor_code_review` відповідав як **`socratic_dialogue`** | action-map `mentor_code_review→code_review` |
| `agents/sam/agent.py` | `morning_data_sam` → `"Unknown action: morning_data"`: ринкова секція ранкового брифінгу Єви мовчки зникала | додано гілку `morning_data`/`briefing` → `build_digest` |
| `agents/kira.py` | невідома дія мовчки падала в `socratic_dialogue` — правдоподібна, але не та відповідь | явна помилка + список доступних дій |
| `agents/doc.py` | календар скринінгів **інвертовано**: виконані обстеження називалися `upcoming`, а ніколи не зроблені — `overdue` | `today = date.today()`; коректні `completed` / `due` / `overdue` |
| `agents/sam/journal.py` | при відхиленні сигналу обмеження не містило `symbol`/`direction`, тому `_match_constraint` нічого не блокував — повторна пропозиція проходила | у summary пишеться `"SYMBOL:direction — reason"`; додано `TradeJournal.get_signal()` |
| `agents/sam/agent.py` | ключі конфігурації не збігалися: `risk_per_trade`(0.01) / `daily_stop_out`(0.03) / `telegram_chat_id` ігнорувалися → ліміти ризику оператора не діяли | нормалізація в `risk_pct`/`daily_stop_pct` (відсотки) і `sam_chat_id` |
| `agents/kira_socratic.py` | сесії ключувалися `(student, topic)` — двоє учнів на одній задачі ділили драбину підказок; необмежене зростання словника | ключ `(session_id, student, topic)`, `MAX_SESSIONS = 1000` із FIFO-витісненням |
| `agents/office_copilot.py` | параметр `tool` зчитувався й **ігнорувався**: завжди поверталася вся база знань | реальна фільтрація `word` / `excel` / `macro` / all |
| `orchestrator._change_requests_handler` | автор заявки за замовчуванням `operator` == рев'юер за замовчуванням — увесь цикл за замовчуванням блокувався новим шлюзом | автор за замовчуванням — непривілейований `agent` |

---

## 6. Розгортання та інфраструктура 🟠

### 6.1. Контейнер не міг запуститися з read-only коренем
`MarkdownVault`, `VideoProducer`, `MockupStudio`, `AntiDetectProfileManager`
робили `mkdir` відносно CWD під час імпорту. У compose `eva-agent` має
`read_only: true` і лише tmpfs `/tmp` → `PermissionError` на старті.

**Виправлено:** новий модуль `src/data_paths.py` + змінна `EVA_DATA_DIR`
(`vault`, `videos`, `mockups`, `browser_profiles`, `reports`). Без змінної
зберігається стара поведінка відносно репозиторію.

### 6.2. `docker-compose.yml` — втрачені моунти
Сервіс `eva-agent` оголошував ключ `volumes:` **двічі**. Другий блок мовчки
замінював перший, тобто `./src` і `./deploy/runtime` у контейнер не потрапляли.

**Виправлено:** один блок `volumes` з усіма моунтами + новий том `eva_data:/data/eva`.

### 6.3. Неіснуючий Dockerfile
`dockerfile: docker/Dockerfile.agent` — файла в репозиторії не було, стек не
збирався.

**Виправлено:** створено `deploy/docker/Dockerfile.agent` (python:3.11-slim,
ffmpeg, UID 1001, `/data/eva`, healthcheck); посилання в compose оновлено,
додано `command` і `working_dir`.

### 6.4. `agent_runner` перехоплював SIGTERM
На рівні імпорту реєструвався обробник `SIGTERM`/`SIGINT`, який лише логував.
Він перекривав обробник uvicorn, тому `docker stop` не зупиняв процес —
через 10 с Docker надсилав SIGKILL, губилися запити, який працювали.

**Виправлено:** обидва обробники та імпорт `signal` видалені.

### 6.5. `/cockpit` шукав файли в `repo_code/`
Список кандидатів містив шляхи зі старої розкладки репозиторію.

**Виправлено:** порядок від упакованої розкладки (`/app/cockpit.html`,
`/app/runtime/cockpit.html`) до кореня репозиторію; `cockpit.html` змонтовано
read-only, шлях додано в Dockerfile.

### 6.6. Неочікувана фонова задача
`asyncio.create_task(...)` для поновлення токена Vault зберігав результат унікуди —
задача могла бути зібрана GC.

**Виправлено:** посилання в `AppState.vault_renewal_task`, скасування й очікування
в `lifespan` при завершенні.

### 6.7. Інше
- Дублікат compose: кореневий `docker-compose.yml` і `deploy/docker-compose.yml`
  були ідентичними — синхронізовано, додано тест на розходження.
- `EVA_DATA_DIR` додано в `.env.example` і `deploy/.env.example`.

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

### Тести як джерело брехні
Обидва легасі-сьюти:
1. сканували **10 184 файли** всередині `.venv` (і падали на синтаксисі `ccxt`)
   → додано `_SKIP_DIRS` + `discover_python_files()`;
2. писали в **відслідковувані** файли `scratch/` (`thoughts.md` щоразу додавав
   рядок — сьют не був ідемпотентним) → тепер усе в `tempfile.mkdtemp()`,
   `EVA_DATA_DIR` вказує туди ж;
3. містили кроки, які створювали об'єкти без жодної перевірки
   (`wf_error`, `scheduler`, `r_good_wh`) → додано реальні assert-и.

---

## 8. Що додано

| Файл | Призначення |
|---|---|
| `tests/test_regressions.py` | 58 тестів, кожен фіксує конкретний виправлений дефект |
| `tests/test_all_task_types.py` | 105 тестів: **усі** типи з `TASK_ROUTING` — без винятку, результат серіалізується, `status == "completed"` |
| `src/data_paths.py` | вирішення шляхів для записуваних даних (`EVA_DATA_DIR`) |
| `deploy/docker/Dockerfile.agent` | відсутній образ для сервісу `eva-agent` |
| `docs/FIX_REPORT.md` | цей звіт |

Як запускати:

```bash
.venv/bin/python -m pytest tests/ -q          # 163 тести
.venv/bin/python tests/test_10floors_architecture.py
.venv/bin/python tests/sandbox_test.py
.venv/bin/ruff check --select F,E9,B --ignore E501,B008,B904 src deploy tests
```

---

## 9. Залишилося (виявлено, не виправлено)

Відсортовано за пріоритетом. Нічого з цього не ламає тести, але варто знати.

| # | Проблема | Де | Ризик |
|---|---|---|---|
| 1 | **Різні шляхи секретів Vault.** `src/integrations/base.py` читає `secret/data/eva-syndicate/<SERVICE>`, а `agent_runner.py` — `eva/database`, `eva/config`, `eva/api-keys`. Хтось з них гарантовано не знайде секрет у продакшені. | `integrations/base.py`, `deploy/runtime/agent_runner.py` | 🔴 високий |
| 2 | **Дублікати DDL.** Таблиці `audit.decisions`, `audit.outbound_vetoes`, `memory.response_cache` створюються і в `config/postgres/init.sql`, і в `migration_v4.sql`. Друга міграція на свіжій БД впаде або призведе до розходження схем. | `config/postgres/*.sql` | 🔴 високий |
| 3 | **Три копії cockpit.html** по 2,7 МБ (`cockpit.html`, `syndikat_cockpit.html`, `static/cockpit.html` — байт-в-байт ідентичні) і дубль `assets/` ↔ `static/assets/`. ~8 МБ у репозиторії. | корінь, `static/` | 🟠 середній |
| 4 | **`create_viral_short` недосяжний** через `TASK_ROUTING`, хоча перелічений у доступних діях Floor 2. | `orchestrator.py`, `coordinator.py` | 🟠 середній |
| 5 | **C901 — складнощі.** Найбільші: `pii.redact` (15), `architect.verify_code_integrity` (18), `flowlint.lint_workflow` (15), `doc.execute` (15), `coordinator.execute` (14), `verifier.verify` (14), `architect.execute` (13). Лише читабельність/супровід. | `src/` | 🟡 низький |
| 6 | **Не переглянуто вручну:** `src/agents/office_copilot.py` (частково), `src/integrations/{google,telegram,mcp}.py`, `src/voice/*`, `src/departments/content_factory/{broll_scout,publisher,release_pack,humanizer,video_prompt_enhancer}.py`, `src/agents/architect/adr.py`, `src/vault_client.py`, документація в `docs/` і `*_core/*_SPEC.md`. | — | 🟡 |
| 7 | **`docs/EVA_SYNDICATE_SYSTEM_PASSPORT.pdf`** відслідковується, хоч `*.pdf` у `.gitignore`. | `docs/` | 🟡 низький |
