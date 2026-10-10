# Sam — вендоровані скіли (INACTIVE)

Статус: **vendored_inactive**. Код у репо для рев’ю і тестів. Нічого не запущено в runtime, не підключено до Hermes, без прав (`capabilities=[]`, `live_modes` = false).

Джерела й SHA — у `SOURCES.lock.yaml`. Ліцензії збережені.

Змінено відносно upstream:
- `trader-memory-core/scripts/fmp_price_adapter.py` і його тест **видалено** (мережевий адаптер FMP з API key). `thesis_review` отримує адаптер ззовні; Сем передає `None`, MAE/MFE недоступні.

Не вендорено: git-pipeline, CI-скрипти, `skill-designer`, screeners та інші скіли tradermonty; broker-модулі riskkit (їх немає); `cot_reports` тягне CFTC лише для завантаження даних.

Залежності — тільки з `requirements-sam.txt`.
