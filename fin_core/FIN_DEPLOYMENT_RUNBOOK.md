# ФІН — ранбук підготовки (prepared)

**Статус:** `prepared_not_enabled`. Не запускати. Не класти ключі в JSON, промпт чи лог.

## Перед будь-яким мерджем
1. `bash tools/check.sh` — зелено.
2. `tests/test_fin_policy.py`, `tests/test_fin_profile.py` — зелено.
3. Рішення A/B/C щодо `fin_sync_bank` зафіксовано.
4. Профіль: `capabilities=[]`, усі `live_modes` = false, `banking.status=not_granted`, `payment_data_stored=false`.
5. Гілка `arena/41a10104-syndicate` — **без push** до рішення Андрія. Merge в main — лише з його дозволу.

## Окремі кроки (кожен — окремий дозвіл)
1. Рішення A/B/C щодо банківського шляху; NBU-AISP для read-only.
2. Telegram-бот Фіна (окремий токен у Vault).
3. Drive / Obsidian / Sheets / Docs (окремі папки і таблиці).
4. n8n workflow Фіна — design, потім inactive mount (як Architect).
5. Моніторинг новин / ДПС / НБУ — observe-only.
6. Вибір моделі OCR і аналізу (слоти).
7. Потік закупівель — після рішення про Dispatcher.
8. Scheduler звітів — останнім.

## Заборони
- Не запускати Hermes profile `fin` без дозволу.
- Не чіпати `apps/`.
- Не активувати сервіси й інтеграції.
- Не ставити задач іншим агентам.
- Не зберігати платіжні реквізити.
