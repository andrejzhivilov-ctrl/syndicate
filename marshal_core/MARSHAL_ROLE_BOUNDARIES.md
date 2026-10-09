# Marshal — межі підготовки v0.1

**Профіль:** `config/agents/marshal.profile.json` → `prepared_not_enabled`, `role_status=identity_draft`.
**Grants:** порожні. Модель не вибрана. Prompt — draft, не activation.

Історичний `MARSHAL_FULL_SPEC.md` не є джерелом прав. Sentinel виключений; Council не вмикати. Tetragon/eBPF — Фаза 2, не реалізовувати тут.

Ідентичність-чернетка: опис і статична перевірка меж. Це не автономний CSO, не 24/7 guarding, не kill switch.

Профіль не дає host control, emergency lockdown, Telegram-бота, MCP чи читання чужих секретів. Оркестраторний `emergency_lockdown` fail-closed як `denied`, доки немає окремого scope від Андрія. Історичний `MarshalAgent` лишається кодом, не грантом.

Будь-який capability — лише після точного id **і** окремого рішення про Dispatcher на маршрутах Marshal.
