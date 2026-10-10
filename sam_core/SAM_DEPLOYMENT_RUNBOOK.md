# Sam — ранбук викладки (prepared)

**Статус:** готово до викладки як `prepared_not_enabled`. Не запускати.

## Перед будь-яким мерджем
1. `bash tools/check.sh` — зелено.
2. Вендорені скіли: `sam_core/vendor/` — тести пройдено (див. `vendor/README.md`).
3. `tools/sam_ready.py` — `grants_empty=true`, `auto_fx_crypto=false`, `auto_invest=false`, `broker=tbd`.
4. Гілка `arena/41a10104-syndicate` — **без push** до рішення Андрія.
5. Merge в main — лише з явного дозволу Андрія (PR #7 не мерджимо).

## Окремі кроки (кожен — окремий дозвіл)
1. Вибір брокера і demo-рахунку (окрема сесія; шорт-ліст у `SAM_BROKER_SHORTLIST_2026-10-10.md`).
2. Встановлення `requirements-sam.txt` в окремий venv Сема (не в основний `requirements.txt`).
3. Ввімкнення скілів у Hermes profile `sam` (`vendored_inactive` → `active` після рев’ю).
4. Allowlist мережі для скілів (зараз нічого; COT — лише якщо Андрій дасть хост).
5. Telegram-бот, голос, cockpit — окремо.
6. Flip `auto_fx_crypto` — окремий HITL + capability + demo-журнал.

## Заборони
- Не класти ключі в JSON, промпт або лог.
- Не стартувати Hermes без дозволу.
- Не чіпати `apps/`.
- Інвестиції ніколи не перемикаються в auto.
