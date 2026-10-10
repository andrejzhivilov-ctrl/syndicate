# ФІН — готовність до викладки (prepared, 2026-10-10)

Профіль можна класти в git як `prepared_not_enabled`. Це **не** старт фінансової роботи.

- [x] Ідентичність з досьє (`FIN_PERSONA.md`), драфт, не grants
- [x] Порожні grants; скіли — драфт без зовнішніх дій; усі `live_modes` = false
- [x] Правила: runway, самозвірка, аудит кошика (advisory), виділення коштів, token guard, FX (`fin_policy.py`)
- [x] Тести `tests/test_fin_policy.py`, `tests/test_fin_profile.py`
- [x] Потік закупівель описано (`FIN_PURCHASE_FLOW.md`)
- [x] Дозволи і запит на розширення (`FIN_PERMISSIONS.md`)
- [x] Платіжні реквізити не зберігаються (закріплено в профілі)
- [ ] Рішення A/B/C щодо існуючого `fin_sync_bank`
- [ ] Рішення щодо Dispatcher для потоку закупівель і постійного правила Андрія
- [ ] Банк read-only через NBU-AISP (`fin.bank.read`)
- [ ] Telegram-бот, транскрибація голосу
- [ ] Drive / Obsidian / Sheets / Docs
- [ ] n8n workflow (design → inactive mount)
- [ ] Моніторинг новин / ДПС / НБУ
- [ ] Модель OCR / аналізу вибрана
- [ ] Scheduler звітів
- [ ] Hermes profile `fin` створений
- [ ] Merge в main (тільки з дозволу Андрія)

Без цих пунктів Фін не відкриває банківських даних і не має прав.
