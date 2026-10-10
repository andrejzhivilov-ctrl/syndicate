# Етап 0 — підготовка репозиторію (стан на 2026-10-10)

Перевірено на гілці `arena/ce93afb9-syndicate` (база `origin/main` = `0165aa4`).

## Ворота

- `bash tools/check.sh` — **зелені, exit 0** (після `pip install -r requirements.txt -r requirements-dev.txt -r requirements-fin.txt` у `.venv`).
- Робоче дерево чисте. `.venv/` ігнорується git.

## Файли KODEX-бота

Перевірено по git (`origin/main`), а не за описом у промпті:

| Файл | Наявність |
|---|---|
| `src/agents/kodex_telegram.py` | є |
| `src/agents/kodex_buttons.py` | є |
| `src/agents/kodex.py` | є |
| `tools/kodex_bot.py` | є |
| `tests/test_kodex_telegram.py` | є (43 тестові функції) |
| `tests/test_kodex.py` | є |

KODEX **не** підключено до `docker-compose.yml` (сервісу немає). Токен Telegram не задано, пряма перевірка з живим ботом не виконана.

## Агенти (`config/agents/*.profile.json`)

Усі 8 профілів: `activation: prepared_not_enabled`, `runtime: hermes`, `model_status: not_selected`. Жодного агента, крім Єви, не запущено.

| Агент | role_status |
|---|---|
| architect | identity_draft |
| doc | not_agreed |
| eva | agreed_draft |
| fin | identity_draft |
| kira | not_agreed |
| kodex | not_agreed |
| marshal | identity_draft |
| sam | identity_draft |

## Сервіси `docker-compose.yml`

`postgres`, `redis`, `vault`, `embeddings`, `eva-agent`, `whisper`, `nginx`, `n8n`.
Окремого контейнера для KODEX, Дока, Фіна, Сема, Архітектора, Маршала, Кіри немає.

## Розбіжності з промптом «новий чат»

1. Промпт каже «origin/main = 30828c8». Фактично `origin/main` = `0165aa4`.
2. Промпт каже, що файлів KODEX-Telegram на `main` немає. Вони є (див. таблицю вище).
3. Промпт каже, що Runtime Hermes не реалізовано. Це відповідає дійсності: у коді є лише посилання в профілях.

## Не зроблено (свідомо)

- Жодного агента не активовано, права (`grants`) не змінювались.
- Жодного секрету або токена в репозиторії.
- Етап 1 (базовий стек на сервері) не запускався: це серверна дія, потребує погодження Андрія.
