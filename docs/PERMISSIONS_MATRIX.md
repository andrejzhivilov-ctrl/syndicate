# Матриця прав агентів (генерується)

> Не редагувати вручну. Джерело — `config/agents/*.profile.json`.
> Перегенерація: `python tools/export_permissions.py`. Тест `tests/test_permissions_matrix.py` перевіряє відповідність.

За замовчуванням — відмова (default-deny): усе, чого немає в колонках, заборонено.

| Агент | Активація | Роль | Capabilities | Resource scopes | Сервіси | Proposed grants (не застосовані) | Skills | Reference skills (read-only) | Telegram |
|---|---|---|---|---|---|---|---|---|---|
| alice | prepared_not_enabled | agreed_draft | — | — | — | alice.github.pull_request.create (proposed_not_applied), alice.github.repo.read (proposed_not_applied), alice.image.generate (proposed_not_applied), alice.memory.read (proposed_not_applied), alice.model.invoke (proposed_not_applied), alice.video.render (proposed_not_applied), alice.web.search (proposed_not_applied), alice.workspace.read (proposed_not_applied), alice.workspace.write (proposed_not_applied) | 0 (активних: 0) | api-and-interface-design, debugging-and-error-recovery, context-engineering, documentation-and-adrs, source-driven-development, test-driven-development, planning-breakdown, agent-security-hardening | not_connected |
| architect | prepared_not_enabled | identity_draft | n8n.workflow.design, n8n.workflow.mount | n8n/live | n8n | — | 3 (активних: 0) | grill-me, handoff, grilling, api-and-interface-design, debugging-and-error-recovery, context-engineering, documentation-and-adrs, source-driven-development, test-driven-development, planning-breakdown, ponytail, replica-recon, agent-security-hardening | — |
| doc | prepared_not_enabled | not_agreed | — | — | — | — | 0 (активних: 0) | scientific-critical-thinking | buttons_ready_bot_pending_token |
| eva | prepared_not_enabled | agreed_draft | — | — | — | — | 5 (активних: 0) | grill-me, handoff, grilling, context-engineering, planning-breakdown, internal-comms, market-research | — |
| fin | prepared_not_enabled | identity_draft | fin.dispatch.eva_basket, fin.funds_check, fin.reports.local, fin.docs.local_generate | fin/out | — | — | 14 (активних: 0) | internal-comms, scientific-critical-thinking, behavioral-finance, market-research | — |
| jack | prepared_not_enabled | agreed_draft | — | — | — | — | 3 (активних: 0) | scientific-critical-thinking, behavioral-finance | not_connected |
| kira | prepared_not_enabled | not_agreed | — | — | — | kira.learning.store_local (proposed_not_applied) | 0 (активних: 0) | scientific-critical-thinking | — |
| kodex | prepared_not_enabled | not_agreed | kodex.archive.read_all, kodex.archive.write_unlabeled, kodex.labeled.move, kodex.labeled.change_with_andrii_permission, kodex.report.eva | kodex/archive | — | — | 0 (активних: 0) | handoff, context-engineering, documentation-and-adrs, internal-comms | handlers_ready_bot_pending_token |
| marshal | prepared_not_enabled | identity_draft | — | — | — | — | 0 (активних: 0) | replica-test, agent-security-hardening | — |
| oscar | prepared_not_enabled | agreed_draft | — | — | — | — | 3 (активних: 0) | internal-comms, frontend-design, content-engine, market-research, brand-voice | not_connected |
| sam | prepared_not_enabled | identity_draft | — | — | — | — | 5 (активних: 0) | scientific-critical-thinking, behavioral-finance, market-research | — |
| tyler | prepared_not_enabled | agreed_draft | — | — | — | — | 3 (активних: 0) | frontend-design, replica-recon, content-engine, market-research, brand-voice | not_connected |

## Спільні правила доступу (поза профілями)

- Мітка `andrii_protected`: читання — всі; переміщення — KODEX і агенти; редагування/видалення — лише з дозволу Андрія.
- Файли без мітки: KODEX і агенти редагують, сортують, видаляють самі; усе йде у звіт Єві.
- Інтернет і будь-яке завантаження (включно з YouTube) — лише з підтвердження Андрія.
- Видалення — у кошик на 30 днів; остаточне видалення автоматичне.
- Telegram: лише Андрій (allowlist); порожній allowlist = відмова.
