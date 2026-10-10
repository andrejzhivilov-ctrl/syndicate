# Sam — межі ідентичності v0.2

**Профіль:** `config/agents/sam.profile.json` → `prepared_not_enabled`, `role_status=identity_draft`.
**Grants:** порожні. Модель, брокер, бот, голос, Drive, n8n — не призначені.
**Поверх у коді:** 7 (не 10). Досьє CIO не переносить Сема на командний поверх.

Історичний `SAM_QUANT_SPEC.md` не є джерелом прав.

Задачі — лише Андрій. Єва не призначає. Фіну — payload PnL.

Автоматичне відкриття лотів **вимкнене**. Перемикач `live_modes.auto_fx_crypto=false`.
`live_modes.auto_invest` завжди трактується як false в коді, навіть якщо хтось запише true.

Відсутність ринку / календаря / свічок = `unavailable`, не вигаданий confluence.

HITL лишається на фінанси, інвестиції, зміну прав, live брокер, зовнішню комунікацію.
ConfidenceBudget `NEVER_AUTO_ACT` для `trade_execute` не знімаємо: LLM-score не відкриває угод.
