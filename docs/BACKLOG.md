# BACKLOG — що робити далі

Пріоритети: 🔴 треба · 🟠 бажано · 🟡 коли буде час.
Оновлюй цей файл разом із `docs/HANDOFF.md`.

Легенда хто: **AG** = Antigravity (будує) · **AA** = Arena Agent (перевіряє/консолідує) ·
**👤** = тільки людина (потрібен секрет, гроші або рішення).

---

## 🔴 Пріоритет 0 — підготовка бекенду під клієнтський додаток

Це блокери для додатка (ПК + смартфон). Виявлено аудитом `deploy/runtime/agent_runner.py`.
Деталі — у `docs/ANTIGRAVITY_BRIEF.md`. **Пункти 0.1–0.6 зроблені** (див. бриф і журнал
у `docs/HANDOFF.md`); реальний OS-push FCM/APNs залишається окремою клієнтською інтеграцією.

| # | Задача | Статус |
|---|---|---|
| 0.1 | **OpenAPI увімкнено** + `apps/shared/api-contract.yaml` генерується з коду (`tools/export_openapi.py`, перевіряється `--check` у CI) | ✅ зроблено |
| 0.2 | **CORS** — env-керований allowlist `EVAS_CORS_ORIGINS` (за замовчуванням закрито) | ✅ зроблено |
| 0.3 | **Per-device токени** — `src/device_auth.py`: логін мастер-ключем → короткоживучий
скопований токен, ротація, відкликання поштучно. Мастер-ключ **не** потрапляє в клієнт | ✅ зроблено |
| 0.4 | **Стрімінг `/execute/stream`** (SSE). Чесно: поки лише heartbeat — реальний прогрес
агента з'явиться, коли граф перейде на `astream_events`; вигаданих подій прогресу немає | ✅ зроблено |
| 0.5 | **HITL у додатку як першокласна поверхня.** Зараз підтвердження живе в Telegram.
Зроблено: inbox (`GET /cr/pending`, `/cr/list`, `/cr/{cr_id}`), скоуп `hitl`
(окремий device-токен може тільки підтверджувати), SSE-пуш (`GET /cr/stream`).
Чесно: SSE — in-process; реальний OS-пуш (FCM/APNs) — окрема клієнтська інтеграція | ✅ зроблено (бекенд) |
| 0.6 | **Закрити `/cockpit` і `/floors`** за reverse proxy: FastAPI перевіряє `read`-скоуп, Nginx більше не віддає HTML напряму | ✅ зроблено (бекенд + proxy) |

**Початок для Antigravity:** гілка `app/client`, усе в `apps/`. Контракт — `apps/shared/api-contract.yaml`.
Перша задача — каркас Flutter + екран «реєстр поверхів» із `/floors`; для запитів потрібен
короткоживучий device-токен зі скоупом `read` (майстер-ключ у клієнт не передавати).

## 🔴 Пріоритет 1 — без цього функція не існує

| # | Задача | Де | Хто |
|---|---|---|---|
| 1 | **Resumable-завантаження YouTube Data API v3.** Зараз `schedule_youtube_short` чесно повертає `not_implemented` — публікація в YouTube неможлива. Потрібен OAuth-флоу, збереження refresh token у Vault, resumable upload | `content_factory/publisher.py` | AG → AA |
| 2 | **Завантажити бекап собі.** `backup/full/` (73 МБ) живе в пісковиці, яка вже двічі відкочувалася. Скачати mirror/bundle/zip локально | — | 👤 |
| 3 | **Ключі Pexels/Pixabay у Vault.** Без них `broll_scout` не може дістати B-roll, і рендер коротких відео деградує (порожній concat → `output_file_missing`) | `content_factory/broll_scout.py`, Vault | 👤 → AG |
| 4 | **Заповнити реальні секрети у Vault** за шляхами з `src/vault_paths.py`: `database`, `redis`, `auth`, `api-keys`, `agents`. Зараз багато шляхів працює через env-фолбек і логує warning | Vault | 👤 |
| 5 | **Клієнтський додаток (ПК + смартфон).** Каркас + перший екран (реєстр поверхів із `/floors`). Гілка `app/client`, усе в `apps/` | `apps/` | AG → AA |

## 🟠 Пріоритет 2 — якість й довіра

| # | Задача | Де | Хто |
|---|---|---|---|
| 6 | **PostgreSQL + pgvector у CI.** SQL-гілки більше не «сліпа зона»: `tests/live_pg.py` + `tests/test_postgres_paths.py` (25 тестів), job `postgres` у `.github/workflows/ci.yml`, крок у `tools/check.sh` | ✅ зроблено (сесія 8) | AA |
| 7 | **Розширити `Humanizer`** — словники `CLICHES` і `REPLACEMENTS` короткі для продакшен-копірайтингу (uk/ru/en) | `content_factory/humanizer.py` | AG |
| 8 | **Винести `base_url` у `GrokWriter` у конфігурацію.** Зараз `https://api.x.ai/v1` захардкоджений у двох модулях | `grok_writer.py`, `script_director.py` | AG |
| 9 | **Реальний матчер Word-шаблонів у `office_copilot`.** Пошук по `{{placeholder}}` працює спрощено; для складних шаблонів варто обробляти поля й таблиці окремо | `agents/office_copilot.py` | AG |
| 10 | **Метрики й алерти.** Жодного експорту в Prometheus; стан відділів видно тільки з логів | новий модуль | AG |
| 11 | **Документація розгортання з нуля.** `DEPLOYMENT_RUNBOOK.md` існує, але не перевірявся на чистому VPS після всіх правок (read-only корінь, `EVA_DATA_DIR`, новий Dockerfile) | `DEPLOYMENT_RUNBOOK.md` | AG → AA |

## 🟡 Пріоритет 3 — гігієна

| # | Задача | Де | Хто |
|---|---|---|---|
| 12 | **Git LFS для `docs/EVA_SYNDICATE_SYSTEM_PASSPORT.pdf`.** Файл знято з відстеження, але блоб 6,3 МБ лишився в історії. Або LFS, або регенерувати з Markdown-джерела | `docs/` | AG |
| 13 | **Видалити гілку `arena/01a10abd-eva-syndicate`** | ✅ гілки вже немає на GitHub (сесія 9 перевірила `git ls-remote --heads`). Пункт закрито | — |
| 14 | **Доля `backup-stable-cockpit` (`7be2dda`)** | ✅ remote-гілку видалено ще в сесії 7. Важливе уточнення: оцінка «736 комітів, яких немає в `main`» була **помилковою** (наслідок shallow-клону) — `7be2dda` давно в історії `main`. Вміст збережено тегами `archive/cockpit-stable-7be2dda` і `v4.2-cockpit-halo-stable` | — |
| 15 | **Розширити `tools/check.sh`** — частково: крок живої БД і перевірка «робоче дерево чисте» в CI вже є (сесія 8); лишилося `pip-audit` на вразливості | `tools/check.sh` | AA |
| 16 | **Покрити тестами SQL-шляхи `TradeJournal`** (разом із символ-фільтром) | ✅ зроблено (сесія 8, `tests/test_postgres_paths.py`) | AA |
| 17 | **Durable audit trail у `audit.decisions` / `audit.outbound_vetoes`** | ✅ **зроблено:** `MemoryManager` append-only записує рішення й outbound gate; оркестратор фіксує outcome (`pending` для HITL), risk/escalation і veto. У записах лише allowlist-ідентифікатори та агрегати — без payload; вільні reason-тексти відкидаються. Збій audit DB не змінює результат задачі. Перевірено unit + живим PostgreSQL і INSERT-only правами | AA |
| 18 | **Один пул з'єднань замість двох.** `MemoryManager` тепер тримає SQLAlchemy-двигун і `asyncpg`-пул для `$1`-SQL компонентів (`TradeJournal`, `DeviceTokenStore`). Працює, але два пули до однієї БД — зайве; варто уніфікувати на SQLAlchemy-сесії | `src/memory.py`, `agents/sam/journal.py`, `src/device_auth.py` | AG → AA |
| 19 | **Сумісність розширень у тестовій БД.** Вбудований `pgserver` має лише `vector`; CI — повний набір. Поки що harness чесно пропускає `pg_trgm` із причиною; якщо з'явиться код, що реально використовує `pg_trgm`/`uuid-ossp`, знадобиться образ із contrib і для локальних прогонів | `tests/live_pg.py` | AA |
| 20 | 🟠 **`python deploy/runtime/agent_runner.py` падає** — `ModuleNotFoundError: No module named 'src'` | ✅ зроблено (сесія 10): `sys.path` bootstrap за тим самим патерном, що в `tools/export_openapi.py`; регресійний тест запускає файл у підпроцесі без кореня репо в `sys.path` | AA |
| 21 | 🟡 **`VAULT_ADDR` без значення дає `KeyError: 'VAULT_ADDR'`**; `python-dotenv` у залежностях, але `.env` не читався | ✅ зроблено (сесія 10): `.env` вантажиться з `override=False` (значення Compose/systemd завжди перемагають), `_vault_env()` називає **всі** відсутні змінні й вказує на runbook; порожнє значення = відсутнє | AA |
| 22 | 🔴 **Секрет у публічному репозиторії** — `EVA_SYNDICATE_FULL_DIALOGUE.txt` (коміт `35b7926`) містить справжній GitHub PAT (рядки 5670, 5756 = репліка #69). **Дія людини:** відкликати токен; вирішити долю файлу (вирізати репліку / повернути приватність). У нові файли повне значення **не копіювати** | `EVA_SYNDICATE_FULL_DIALOGUE.txt` | Андрій |
| 23 | 🔴 **Пам'ять для всіх агентів** — спочатку лише Єва читала власні епізоди; ціль — контекстна, bounded recall і корисне збереження без вигаданих «поточних» фактів | ✅ **зроблено:** `MemoryManager.build_memory_context` має бюджет і звітує `dropped`/`truncated`; Eva зберігає обидві репліки, Doc/Kira/Fin/Sam/Marshal мають agent-scoped recall і збереження з PII-redaction. Історичні медичні/фінансові/ринкові/безпекові дані не підміняють поточні виміри чи рішення. Orchestrator передає caller `session_id`; недоступність пам'яті не валить задачу. Перевірено повним `tools/check.sh` і цільовими регресіями | AA |
| 24 | 🔴 **Redis блокує деплой** — немає `requirepass` у `config/redis/redis.conf`; `DEPLOYMENT_RUNBOOK.md` §2.3 робить `sed` по неіснуючому рядку (мовчки нічого не робить); чек-ліст (рядок 320) недосяжний; `initialize()` кличе `ping()` без try/except → фатальний старт, хоч Redis задумано опційним | ✅ **зроблено (сесія 11):** пароль передається з `.env` через `--requirepass` (у файлі секрету немає — нема чого «синхронізувати»); healthcheck автентифікується так само; `rename-command` вимикає FLUSHALL/FLUSHDB/CONFIG/DEBUG/EVAL; `_connect_redis` деградує до «кеш вимкнено» замість фатального старту, кеш-операції мають circuit-breaker; паролі в DSN маскуються в логах (`_redact_dsn`). Runbook §2.3 і чек-ліст переписані. Тести: `TestRedisIsOptional` (2, живий PG), `test_redis_is_password_protected_and_lockdown_commands_are_disabled`, `test_every_service_drops_all_capabilities`, `test_dsn_passwords_never_reach_the_logs` | AA |
| 25 | 🔴 **Системи бекапів немає взагалі** — 0 рядків коду, хоч це прямий пункт задуму (репл. #33) | ✅ **зроблено (сесія 11):** `tools/backup.py` — набір із трьох артефактів (дамп PostgreSQL `--format=custom`, Raft-знімок Vault, `.env` з `chmod 600`), `manifest.json` з sha256, **верифікація дампу через `pg_restore --list`**, retention, опційний `restic`. Крок, який не відбувся, — це `unavailable` з причиною, ніколи не «ok». Runbook §10 переписано (cron/systemd, окрема політика Vault для знімків), додано §10.1 «Відновлення» з обов'язковою репетицією. Тести: 16 регресійних на заглушках (`TestBackupTool`) | AA |
| 26 | 🟠 **N8N-будівник без гейта схвалення** — задум вимагав «пропонує архітектуру і стартує лише після схвалення» | ✅ **гейт реалізовано й протестовано:** пропозиція створює Markdown Change Request; `gitops_sync` fail-closed без CR у стані `applied`, перевіряє точний fingerprint workflow, FlowLint і `active=false`. Pending/approved-not-applied/rejected/mismatch/active workflow не формують bundle. N8N не активується автоматично — потрібні операторське застосування CR і окрема ручна активація | AA |
| 27 | 🟡 **SKILL.md-шар, Mem0 і token-budget** — Mem0 окремо не впроваджувався; токен-бюджет пам'яті вже є в `MemoryManager.build_memory_context` | 🟠 **SKILL.md реалізовано:** `src/skill_store.py` зберігає лише явні кандидати з успішних задач у MarkdownVault, маскує PII, підвищує до `verified` після двох різних успішних task ID і віддає лише релевантні перевірені нотатки; caller-injected skills відкидаються, нотатки не переважають поточні інструкції. Mem0 лишається окремим відкритим рішенням/роботою | AA |
| 28 | 🟡 **Tetragon/eBPF — рішення потрібне** — описано в `marshal_core/MARSHAL_FULL_SPEC.md`, коду немає; робота з ядром суперечить поточним обмеженням compose (`read_only`, `cap_drop`, `no-new-privileges`) | ✅ **вирішено (Андрій, 06.10): Фаза 2.** Лишається у специфікації як запланована Фаза 2, у Фазі 1 не реалізується (і не обіцяється як наявне) | Андрій |
| 29 | 🟡 **YAML-аудит Compose не завершено** — попередні цифри були отримані awk'ом | ✅ **зроблено (сесія 11):** повний аудит через `yaml.safe_load`. Точні факти: `cap_drop: ALL` тепер на **всіх 7** сервісах (було відсутнє на `vault` і `n8n` — виправлено); `read_only` лише на `eva-agent`; `nginx` справді без `user:`, але має `cap_add: NET_BIND_SERVICE,DAC_OVERRIDE,CHOWN` (потребує root-мастера для 80/443 — окремий пункт 33); Vault на `127.0.0.1:8200`; дубльованих ключів немає | AA |
| 30 | 🟡 **Геолокація/геотеги відсутні** — 0 входжень у `src/`, хоч у діалозі описано One-shot/Live до 8 год | ✅ **вирішено (Андрій, 06.10): абсолютний контроль.** Геолокація працює **лише** за особистим підтвердженням Андрія; у всіх інших випадках — **завжди вимкнена** (default-deny, не «вимкнена за замовчуванням, але вмикається»). Реалізація — окремою сесією | Андрій + AA |
| 31 | 🔴 **Генератора ембеддингів немає** — `semantic_search` фізично недосяжний: `save_episode` ніколи не передає `embedding=`, тому `content_vector` завжди NULL. Те саме в `src/lessons.py` | ✅ **зроблено (сесія 11):** рішення Андрія — **BGE-M3 локально** (1024 вим., пам'ять не виходить за межі сервера) + індексуємо **епізоди й уроки**. Новий `src/embeddings.py` (провайдер + жорстка валідація: чужий розмір, NaN, нульовий вектор → `EmbeddingUnavailable`, а не «схоже на вектор»), `deploy/runtime/embeddings_server.py` + `deploy/docker/embeddings.Dockerfile` + сервіс `embeddings` у compose (тільки `backend`, без публікації портів, не в `depends_on` агента), міграція `migration_v5_embeddings_1024.sql` (ідемпотентна, відмовляється конвертувати непорожні колонки), розмірність у коді й схемі зшита тестом. Тести: 15 регресійних + 8 живих (схема, наскрізний векторний пошук, урок за дією, деградація без втрати даних) | AA |
| 32 | 🟠 **Vault: політики й ізоляція** — замість одного wildcard-токена `eva-agent` на всі секрети; `vault_init.sh` клав `CHANGE_ME_BEFORE_PRODUCTION` / `PLACEHOLDER_UPDATE_ME`; прав за агентами не було | ✅ **зроблено (сесія 11):** політики **генеруються з коду** (`tools/vault_policies.py` ← `src/vault_paths.py`) у `config/vault/policies/*.hcl` — ані wildcard-а, ані heredoc-а в скрипті; на кожен поверх своя least-privilege політика (default deny, без чужої гілки, без `auth` сервера) + AppRole на кожну політику. `vault_init.sh` більше не вигадує секретів: пароль БД/Redis береться з `.env` (скрипт **відмовляється** працювати з плейсхолдером), LLM-ключі — лише передані змінними, `api_key`/`webhook_secret` генеруються, root-token відкликається наприкінці. Плейсхолдери тепер відсікає і клієнт (`VaultClient.get_secret`) — єдине місце замість восьми ad-hoc перевірок, — а `/health` показує їхні назви (`vault_placeholder_secrets`). Скрипт **уперше виконується** в тестах: `tests/live_vault.py` — мок Vault API, 40 тестів. Ворота: `tools/vault_policies.py --check` + `bash -n` у `tools/check.sh` | AA |
| 37 | 🟠 **Секрети повз Vault** — частина коду читає ключі напряму з env, тому політики Vault їх не захищають і ротація вимагає перезапуску: `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `XAI_API_KEY` (content factory), `TELEGRAM_BOT_TOKEN` (publisher), `MONOBANK_API_TOKEN`, `PRIVATBANK_PASSWORD` (banking), `EMBEDDINGS_TOKEN`. Сам `agent_runner` має правильний порядок (Vault → env), тож проблема не в базовому шляху, а в модулях, які пішли повз `BaseConnector`/`read_vault_secret` | `src/departments/content_factory/*`, `src/integrations/banking.py` | AA |
| 33 | 🟡 **`nginx` працює root-мастером** (без `user:`) — свідомо: потрібні `NET_BIND_SERVICE`, `CHOWN`, `DAC_OVERRIDE` для 80/443 і `/var/cache/nginx`. Альтернатива — `nginxinc/nginx-unprivileged` + `NET_BIND_SERVICE`; зміна ризикована без `docker` у пісковиці, тому лишається як усвідомлений компроміс | `docker-compose.yml` | AA |
| 35 | 🟠 **Бекапи: репетиція відновлення і розклад від Архітектора** — `tools/backup.py` готовий, але (а) відновлення жодного разу не виконувалось (див. §10.1 рунбуку), (б) розклад поки через cron/systemd, а за задумом його має ініціювати Архітектор (CTO) і звітувати Єві | `tools/backup.py`, `src/agents/architect/` | AA |
| 36 | 🔴 **Вигадані метрики організму й брифу** — `_morning_readiness` підставляла `hrv_ms` 50, `sleep_hours` 7.5, `resting_hr` 65, кроки 8000, а `_compose_briefing` — «готовність 85/100, зона green, ранвей 12 міс.»; `_nutrition_plan` брала 80 кг / 180 см / 35 р., `_nervous_system` «вимірювала» стрес 60 у порожньому payload, а нічний джоб передавав Доку HRV 62 / стрес 35 / сон 85 як справжні показники | ✅ **зроблено (сесія 11):** жодне число не підставляється — відсутній показник лишається `None`, а результат стає `status: unavailable` з переліком `missing_inputs`; часткові дані рахуються з перенормованими вагами й позначаються `partial: true`; Док без метрик пропонує **неперсоналізований** протокол (`personalised: false`), а не «стрес 60». Додано 16 регресійних тестів (`TestDocNeverInventsMetrics`, `TestEvaBriefingReportsAbsence`, `TestScheduledJobsDoNotInventBiometrics`) | AA |
| 34 | 🟡 **Клієнтський додаток (`apps/`)** — зараз лише 2 файли API-контракту | ✅ **вирішено (Андрій, 06.10): після того, як Синдикат буде повністю готовий до розгортання на сервері.** Не починати раніше | Андрій |

> **Нумерація:** пункти 17–19 прийшли від сесії 8 (PostgreSQL + CI), 20–21 — від сесії 9
> (вигадані оцінки в confluence Sam). Сесії виконувались паралельно, тому номери
> довелося перерозподілити під час злиття. Спершу сесія 9 пропонувала CI як пункт 17 —
> його закрила сесія 8, тому пункт зник, а 20–21 зсунулись.

---

## ✅ Закрито в сесії 9 (2026-10-05) — вигадані оцінки в confluence Sam

Знайдено й виправлено **п'ять** шарів, які перетворювали відсутність даних на числову
оцінку (порушення §1 `AGENTS.md`). Гірший — `news_shield` відмовляв **у бік дозволу**
(80/100 без veto) при невідомому економічному календарі. Деталі — у `docs/HANDOFF.md`
(сесія 9) і `tests/test_regressions.py::TestConfluenceAbsenceIsNotAnObservation`.

Тепер «не змогли прочитати» = `unavailable` (0 внеску, `missing: True`), а «перевірили
й нічого не знайшли» = справжній бал. Наслідок: сетап без реальних даних дає 0.0, а не ~40.

---

## ✅ Закрито в сесії 8 (2026-10-05) — CI та живі SQL-шляхи

`.github/workflows/ci.yml` (два job'и: ворота без БД + PostgreSQL 16 із pgvector),
`tests/live_pg.py` + `tests/test_postgres_paths.py` (25 живих SQL-тестів),
`EVA_REQUIRE_LIVE_DB=1` не дає skip'ам перетворитись на «зелений» прогін. Пункти 6 і 16
закриті, 15 — частково. Деталі — у `docs/HANDOFF.md` (сесія 8).

---

## Архітектурні ідеї (не планувались, просто помічено під час аудиту)

- **`src/agents/*` дублюють один і той самий патерн** `execute()` → таблиця дій.
  Варто винести спільний базовий клас `ActionDispatchAgent`, який будує `_ACTION_MAP`,
  повертає `available_actions` і сам обробляє невідомі дії. Зараз цей код скопійовано
  в 5 агентів.
- **Два наскрізні suite'и (`test_10floors_architecture.py`, `sandbox_test.py`) не є pytest.**
  Вони завжди завершуються з кодом 0 — CI їх не помітить, якщо зламаються.
  Переписати наpytest або додати явні `assert` + ненульовий exit code.
- **Немає єдиного контракту відповіді агента.** Різні агенти повертають
  `status` / `error` / `warning` / `synthetic` по-різному. Варто зафіксувати
  тип `AgentResult` (TypedDict) і валідувати його на виході з `execute()`.
- **Жодного retry/timeout-бюджету на рівні поверху.** Окремі конектори мають
  ретраї, алеtask не має загального дедлайну — повільний LLM може тримати
  воркера нескінченно.
