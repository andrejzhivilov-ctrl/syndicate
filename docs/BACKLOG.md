# BACKLOG — що робити далі

Пріоритети: 🔴 треба · 🟠 бажано · 🟡 коли буде час.
Оновлюй цей файл разом із `docs/HANDOFF.md`.

Легенда хто: **AG** = Antigravity (будує) · **AA** = Arena Agent (перевіряє/консолідує) ·
**👤** = тільки людина (потрібен секрет, гроші або рішення).

---

## 🔴 Пріоритет 1 — без цього функція не існує

| # | Задача | Де | Хто |
|---|---|---|---|
| 1 | **Resumable-завантаження YouTube Data API v3.** Зараз `schedule_youtube_short` чесно повертає `not_implemented` — публікація в YouTube неможлива. Потрібен OAuth-флоу, збереження refresh token у Vault, resumable upload | `content_factory/publisher.py` | AG → AA |
| 2 | **Завантажити бекап собі.** `backup/full/` (73 МБ) живе в пісковиці, яка вже двічі відкочувалася. Скачати mirror/bundle/zip локально | — | 👤 |
| 3 | **Ключі Pexels/Pixabay у Vault.** Без них `broll_scout` не може дістати B-roll, і рендер коротких відео деградує (порожній concat → `output_file_missing`) | `content_factory/broll_scout.py`, Vault | 👤 → AG |
| 4 | **Заповнити реальні секрети у Vault** за шляхами з `src/vault_paths.py`: `database`, `redis`, `auth`, `api-keys`, `agents`. Зараз багато шляхів працює через env-фолбек і логує warning | Vault | 👤 |

## 🟠 Пріоритет 2 — якість й довіра

| # | Задача | Де | Хто |
|---|---|---|---|
| 5 | **PostgreSQL + pgvector у CI.** Усі SQL-гілки мають `# pragma: no cover` і перевірені лише статично; у тестах працюють in-memory бекенди. Це найбільша «сліпа зона» репозиторію | `.github/workflows/`, `tests/` | AG → AA |
| 6 | **Розширити `Humanizer`** — словники `CLICHES` і `REPLACEMENTS` короткі для продакшен-копірайтингу (uk/ru/en) | `content_factory/humanizer.py` | AG |
| 7 | **Винести `base_url` у `GrokWriter` у конфігурацію.** Зараз `https://api.x.ai/v1` захардкоджений у двох модулях | `grok_writer.py`, `script_director.py` | AG |
| 8 | **Реальний матчер Word-шаблонів у `office_copilot`.** Пошук по `{{placeholder}}` працює спрощено; для складних шаблонів варто обробляти поля й таблиці окремо | `agents/office_copilot.py` | AG |
| 9 | **Метрики й алерти.** Жодного експорту в Prometheus; стан відділів видно тільки з логів | новий модуль | AG |
| 10 | **Документація розгортання з нуля.** `DEPLOYMENT_RUNBOOK.md` існує, але не перевірявся на чистому VPS після всіх правок (read-only корінь, `EVA_DATA_DIR`, новий Dockerfile) | `DEPLOYMENT_RUNBOOK.md` | AG → AA |

## 🟡 Пріоритет 3 — гігієна

| # | Задача | Де | Хто |
|---|---|---|---|
| 11 | **Git LFS для `docs/EVA_SYNDICATE_SYSTEM_PASSPORT.pdf`.** Файл знято з відстеження, але блоб 6,3 МБ лишився в історії. Або LFS, або регенерувати з Markdown-джерела | `docs/` | AG |
| 12 | **Видалити гілку `arena/01a10abd-eva-syndicate`**, коли сесія завершиться. Вона ідентична `main` — нічого не втратиться (є тег `archive/eva-syndicate-2026-10-05`) | GitHub | AA |
| 13 | **Вирішити долю `backup-stable-cockpit` (`7be2dda`).** Там 736 комітів, яких немає в `main` (стара розкладка cockpit v4.2). Варіанти: залишити архівом (зараз), винести в окремий read-only репозиторій, або перенести тільки потрібніAssets в `static/` | GitHub | 👤 |
| 14 | **Розширити `tools/check.sh`**: перевірка на незакомічені зміни як помилка в CI, `pip-audit` на вразливості, перевірка що `init.sql` і `migration_v4.sql` не розійшлися | `tools/check.sh` | AA |
| 15 | **Покрити тестами SQL-шляхи `TradeJournal`** — зараз перевірений тільки in-memory бекенд, а символ-фільтр у SQL-гілці додано без теста | `agents/sam/journal.py`, `tests/` | AA |

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
