# SYNDICATE — пакет розгортання

Статус: **готовий до розгортання на сервері; агенти підготовлені, але не ввімкнені** (`prepared_not_enabled`).
Покрокові серверні команди — у `DEPLOYMENT_RUNBOOK.md` (Ubuntu 24.04, Docker Compose, Vault, nginx, TLS).
Цей файл — що саме розгортати, з якими правами, секретами і що ще відкрито.

## 1. Що запускаємо

| Компонент | Де | Примітки |
|---|---|---|
| Стек Docker Compose | `docker-compose.yml`, `deploy/docker-compose.yml` | postgres (pgvector), redis, vault, embeddings, whisper, eva-agent, nginx |
| Gates (CI) | `.github/workflows/ci.yml`, `tools/check.sh` | тести, ruff, контракт API; запускаються на кожному пуші в `main` |
| Профілі агентів | `config/agents/*.profile.json` | Єва, Архітектор, Маршал, Фін, Сем, Док, KODEX, Кіра |
| Матриця прав | `docs/PERMISSIONS_MATRIX.md` | генерується з профілів (`tools/export_permissions.py`) |
| Сховище KODEX | `KODEX_DATA_DIR` (за замовч. `/opt/eva/kodex_data`) | фото, аудіо, документи; поза git, з бекапом |

Агенти (Док, KODEX, Сем, Фін, Архітектор, Маршал) — **код і профілі готові, runtime не підключено**. Їх запуск — окремий крок після погодження Андрія (див. розділ 6).

## 2. Секрети і змінні

Усі секрети — у Vault або в `.env` на сервері. У репозиторій не потрапляють. Шаблон: `.env.example`.

Обов'язкові (базові): `APP_ENV`, `DOMAIN`, `POSTGRES_*`, `REDIS_PASSWORD`, `VAULT_ADDR`, `VAULT_ROLE_ID`, `VAULT_SECRET_ID`, `EVA_API_KEY`, `WEBHOOK_SECRET`, `EVA_DATA_DIR`.

Додані в цьому пакеті (значення не задані):
- `KODEX_DATA_DIR` — каталог сховища файлів KODEX.
- `TELEGRAM_BOT_TOKEN_DOC`, `TELEGRAM_BOT_TOKEN_KODEX` — окремі приватні боти, allowlist лише Андрій.
- `KODEX_TELEGRAM_ALLOWED_CHAT_IDS` — ID Андрія для бота KODEX. Порожньо = бот відмовляє всім.
- `YOUTUBE_API_KEY` — лише після погодження Андрія для Єви.

## 3. Права (коротко; повна матриця — `docs/PERMISSIONS_MATRIX.md`)

- За замовчуванням — відмова (default-deny). Єва, Док, KODEX, Кіра, Маршал без активних grants.
- **Мітка `andrii_protected`** (ваші файли): читання — всі; переміщення — KODEX і агенти; редагування і видалення — лише з дозволу Андрія; зняти мітку — лише Андрій.
- **Файли без мітки:** KODEX і агенти редагують, сортують, видаляють самі; видалене — у кошик на 30 днів; усе йде у звіт Єві.
- **Завантаження через KODEX** — без мітки за замовчуванням, з попередженням; мітку ставимо на прохання Андрія.
- **Інтернет** (у т.ч. YouTube і завантаження з нього) — лише з явного підтвердження Андрія.
- **Telegram** — лише Андрій (allowlist); порожній allowlist = відмова.
- Медичні файли Андрія — в тому ж сховищі, захист за міткою; Док має доступ лише на читання до файлів з міткою.

## 4. Код: карта модулів

- **KODEX:** `src/agents/kodex.py` (сховище, завантаження, мітки, дозволи, звіт), `src/agents/kodex_buttons.py` (кнопки), `src/agents/kodex_telegram.py` (обробники), `tools/kodex_bot.py` (запуск бота, long polling), `config/agents/kodex.profile.json`, `doc_core/KODEX_NOTES.md`.
- **Док:** `src/agents/doc_knowledge.py`, `doc_nutrition.py`, `doc_shopping.py`, `doc_buttons.py`, `doc_reminders.py` (13:10 і 19:10 Europe/Kyiv), `doc_exercises.py`.
- **Єва:** `src/agents/eva*.py`, `config/agents/eva.profile.json` (YouTube — лише оголошено, не ввімкнено).
- **Фін:** `src/agents/fin_*.py`, `eva_basket.py`.
- **Сем:** `src/agents/sam_*.py`, `sam_core/vendor/` (торгові скіли, неактивні).
- **Архітектор, Маршал, Кіра:** `src/agents/architect_*.py`, `marshal_*.py`, профілі.
- **Спільний skill:** `config/shared_skills/knowledge_base.json`.
- **Тести:** `tests/` (~660, усі зелені на `main` після злиття).

## 5. Вендоровані пакети (ліцензії — у `SOURCES.lock.yaml`)

- `kodex_core/vendor/book-to-skill` — офіційний репозиторій, MIT. Неактивний. Книги з захищеним авторським правом — лише приватно.
- `doc_core/vendor/free-exercise-db` — Unlicense, лише дані.
- `doc_core/vendor/open-exercisedb` — MIT, лише дані.
- `sam_core/vendor/tradermonty-claude-trading-skills` — неактивні скіли.

## 6. Не ввімкнено (потребує вашого рішення або деплою)

- **Запуск runtime агентів** (Hermes-профілі, n8n-воркфлоу) — після погодження.
- **Бази знань** (вправи, рецепти, медичні протоколи) — вводимо при деплої.
- **Транскрибація аудіо і відео, OCR фото, HEIC** — потрібен безкоштовний локальний рушій; вибір при деплої.
- **YouTube (Єва)** — офіційний Data API після погодження; завантаження відео з YouTube заборонено правилами.
- **YouTube Music** — офіційного публічного API немає. Неофіційний доступ через cookies акаунта може порушувати умови сервісу. Рішення Андрія: лише Data API для музичних відео, або неофіційний доступ з ризиком.
- **Live-відео, голос, планувальник нагадувань (Док), моніторинг новин n8n, Perplexity/Swarm-дослідження.**
- **Obsidian, NotebookLM, Google Drive, Sheets** — спосіб доступу при деплої.
- **Telegram-токени** для Дока і KODEX.
- **Фітнес-годинник** (Док) — пізніше.
- **Пороги харчування Дока** — чекають затвердження Андрія.
- **Брокери (Сем)** — шорт-ліст без вибору; офіційна перевірка реєстрами не виконана.
- **Ашан/Ashan (Фін)** — не досліджено; перевірка умов сайтів перед будь-яким замовленням.

## 7. Перевірка перед запуском

1. `bash tools/check.sh` — зелено.
2. `python tools/export_permissions.py` — матриця актуальна (тест її перевіряє).
3. Вручну: `scripts/verify_deployment.sh` після першого запуску стека (див. `DEPLOYMENT_RUNBOOK.md`, розділ 7).
4. Перевірити, що `KODEX_DATA_DIR` на сервері не в git і його бекапи зашифровані.
5. Перевірити, що `.env` не в git (`.gitignore` це покриває).

## 7a. Домашній ПК зараз, сервер пізніше

Інструкція: `docs/HOME_DEPLOYMENT.md` (LAN без домену, `DATA_ROOT`, перенесення на сервер крок за кроком).

## 8. Відкриті питання Андрію

1. Чи вмикаємо YouTube для Єви, і який шлях (офіційний Data API)?
2. YouTube Music: офіційно (лише Data API) чи неофіційний доступ з ризиком?
3. Пороги харчування Дока — затвердити.
4. Чи переносити журнал діалогу `EVA_SYNDICATE_FULL_DIALOGUE.txt` з репозиторію в архів?
5. Вибір безкоштовного рушія транскрибації (Whisper локально) — підтвердити при деплої.
