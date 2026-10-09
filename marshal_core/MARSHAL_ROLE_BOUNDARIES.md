# Marshal — межі підготовки v0.2

**Профіль:** `config/agents/marshal.profile.json` → `prepared_not_enabled`, `role_status=identity_draft`.
**Grants:** порожні. Модель не вибрана. Prompt — draft, не activation.
**Ідентичність:** `MARSHAL_CORE_PERSONA.md`. **Розбір досьє:** `MARSHAL_DOSSIER_REVIEW.md`.

Історичний `MARSHAL_FULL_SPEC.md` не є джерелом прав. Sentinel / Sentyr виключені; Council не вмикати. Tetragon/eBPF — Фаза 2.

Ідентичність-чернетка: CSO-архетип, сталевий голос, Zero Trust, кредо v4.0, підпорядкування лише Андрію. Це **не** live enforcement, не 24/7 guarding, не kill switch, не абсолютне вето.

Профіль не дає host control, emergency lockdown, Telegram-бота, MCP, читання чужих секретів чи пам’яті Єви. Оркестраторний `emergency_lockdown` fail-closed як `denied`. Історичний `MarshalAgent` лишається кодом, не грантом.

Дев’ять рівнів Defense-in-Depth і добовий цикл 02:00–21:00 — backlog інфри, не cron Маршала.

Будь-який capability (включно з майбутнім `policy.veto`) — лише після точного id **і** окремого рішення про Dispatcher на маршрутах Marshal.
