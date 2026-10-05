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

## 2026-10-05 — Arena Agent (сесія 8): живий PostgreSQL+pgvector замість статичної перевірки схеми

**Гілка:** `arena/01a10d46-eva-syndicate` · **Ворота:** ✅ (`tools/check.sh`, включно з новим кроком «жива схема + SQL-шляхи»)

| | |
|---|---|
| Тести | **309** (284 без БД + **25 живих SQL**) |
| Наскрізні suite'и | 🏆 10/10 floors · 🏆 8/8 sandbox |
| Лінтер | `ruff F,E9,B,C901,E,W` — чисто |
| Жива БД у воротах | ✅ PostgreSQL 16 + pgvector 0.6.2 (локально `pgserver`, у CI — `pgvector/pgvector:pg16`) |

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
- **GitHub Actions у пісковиці запустити неможливо** — workflow написаний і вичитаний, але не
  виконаний. Локально прогнано той самий набір кроків; у CI лишається неперевіреним, що образ
  `pgvector/pgvector:pg16` має `uuid-ossp`/`pg_trgm` (тест вимагає нуль пропусків у повному
  кластері — якщо ні, job упаде й це буде видно).
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
