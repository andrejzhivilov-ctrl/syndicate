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
| 6 | **PostgreSQL + pgvector у CI.** Усі SQL-гілки мають `# pragma: no cover` і перевірені лише статично; у тестах працюють in-memory бекенди. Це найбільша «сліпа зона» репозиторію | `.github/workflows/`, `tests/` | AG → AA |
| 7 | **Розширити `Humanizer`** — словники `CLICHES` і `REPLACEMENTS` короткі для продакшен-копірайтингу (uk/ru/en) | `content_factory/humanizer.py` | AG |
| 8 | **Винести `base_url` у `GrokWriter` у конфігурацію.** Зараз `https://api.x.ai/v1` захардкоджений у двох модулях | `grok_writer.py`, `script_director.py` | AG |
| 9 | **Реальний матчер Word-шаблонів у `office_copilot`.** Пошук по `{{placeholder}}` працює спрощено; для складних шаблонів варто обробляти поля й таблиці окремо | `agents/office_copilot.py` | AG |
| 10 | **Метрики й алерти.** Жодного експорту в Prometheus; стан відділів видно тільки з логів | новий модуль | AG |
| 11 | **Документація розгортання з нуля.** `DEPLOYMENT_RUNBOOK.md` існує, але не перевірявся на чистому VPS після всіх правок (read-only корінь, `EVA_DATA_DIR`, новий Dockerfile) | `DEPLOYMENT_RUNBOOK.md` | AG → AA |

## 🟡 Пріоритет 3 — гігієна

| # | Задача | Де | Хто |
|---|---|---|---|
| 12 | **Git LFS для `docs/EVA_SYNDICATE_SYSTEM_PASSPORT.pdf`.** Файл знято з відстеження, але блоб 6,3 МБ лишився в історії. Або LFS, або регенерувати з Markdown-джерела | `docs/` | AG |
| 13 | **Видалити гілку `arena/01a10abd-eva-syndicate`**, коли сесія завершиться. Вона ідентична `main` — нічого не втратиться (є тег `archive/eva-syndicate-2026-10-05`) | GitHub | AA |
| 14 | **Вирішити долю `backup-stable-cockpit` (`7be2dda`).** Там 736 комітів, яких немає в `main` (стара розкладка cockpit v4.2). Варіанти: залишити архівом (зараз), винести в окремий read-only репозиторій, або перенести тільки потрібніAssets в `static/` | GitHub | 👤 |
| 15 | **Розширити `tools/check.sh`**: `pip-audit` на вразливості, перевірка що `init.sql` і `migration_v4.sql` не розійшлися. (Перевірка `device_tokens` на ідентичність уже є в `tests/test_regressions.py::TestPostgresSchemaConsistency`.) **Головне:** CI як такий відсутній — див. 17 | `tools/check.sh` | AA |
| 16 | **Покрити тестами SQL-шляхи `TradeJournal`** — зараз перевірений тільки in-memory бекенд, а символ-фільтр у SQL-гілці додано без теста | `agents/sam/journal.py`, `tests/` | AA |
| 17 | 🔴 **Створити CI (`.github/workflows/check.yml`).** Його немає взагалі, хоч доки посилаються на «у CI» і `tools/check.sh` описаний як крок CI. Зараз «main завжди зелений» тримається лише на пам'яті людини: будь-який агент може запушити гілку з червоними воротами, і ніхто цього не помітить. Треба: `python -m venv`, `pip install -r requirements.txt pytest ruff`, `bash tools/check.sh` на push/PR. Без PostgreSQL-сервісу (SQL-гілки — 6) | `.github/workflows/` | AA |
| 18 | 🟠 **`python deploy/runtime/agent_runner.py` падає** — `ModuleNotFoundError: No module named 'src'`. Блок `if __name__ == "__main__"` не додає корінь репозиторію в `sys.path`, тому локальний запуск без `PYTHONPATH` неможливий (у контейнері все гаразд, тому ворота цього не ловлять) | `deploy/runtime/agent_runner.py` | AA |
| 19 | 🟡 **`VAULT_ADDR` без значення дає `KeyError: 'VAULT_ADDR'`** замість зрозумілого повідомлення; `python-dotenv` є в залежностях, але `.env` на старті не читається — оператор бачить криптичний трейсбек | `deploy/runtime/agent_runner.py` | AA |

---

## ✅ Закрито в сесії 8 (2026-10-05) — вигадані оцінки в confluence Sam

Знайдено й виправлено **п'ять** шарів, які перетворювали відсутність даних на числову
оцінку (порушення §1 `AGENTS.md`). Гірший — `news_shield` відмовляв **у бік дозволу**
(80/100 без veto) при невідомому економічному календарі. Деталі — у `docs/HANDOFF.md`
(сесія 8) і `tests/test_regressions.py::TestConfluenceAbsenceIsNotAnObservation`.

Тепер «не змогли прочитати» = `unavailable` (0 внеску, `missing: True`), а «перевірили
й нічого не знайшли» = справжній бал. Наслідок: сетап без реальних даних дає 0.0, а не ~40.

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
