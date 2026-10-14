# Матриця прав агентів (генерується)

> Не редагувати вручну. Джерело — `config/agents/*.profile.json`.
> Перегенерація: `python tools/export_permissions.py`. Тест `tests/test_permissions_matrix.py` перевіряє відповідність.

За замовчуванням — відмова (default-deny): усе, чого немає в колонках, заборонено.

| Агент | Активація | Роль | Capabilities | Resource scopes | Сервіси | Skills | Telegram |
|---|---|---|---|---|---|---|---|
| antigravity | prepared_not_enabled | identity_draft | — | — | — | 0 (активних: 0) | not_connected |
| architect | prepared_not_enabled | identity_draft | n8n.workflow.design, n8n.workflow.mount | n8n/live | n8n | 3 (активних: 0) | — |
| doc | prepared_not_enabled | not_agreed | — | — | — | 0 (активних: 0) | buttons_ready_bot_pending_token |
| eva | prepared_not_enabled | agreed_draft | — | — | — | 5 (активних: 0) | — |
| fin | prepared_not_enabled | identity_draft | fin.dispatch.eva_basket, fin.funds_check, fin.reports.local, fin.docs.local_generate | fin/out | — | 14 (активних: 0) | — |
| kira | prepared_not_enabled | not_agreed | — | — | — | 0 (активних: 0) | — |
| kodex | prepared_not_enabled | not_agreed | kodex.archive.read_all, kodex.archive.write_unlabeled, kodex.labeled.move, kodex.labeled.change_with_andrii_permission, kodex.report.eva | kodex/archive | — | 0 (активних: 0) | handlers_ready_bot_pending_token |
| marshal | prepared_not_enabled | identity_draft | — | — | — | 0 (активних: 0) | — |
| sam | prepared_not_enabled | identity_draft | — | — | — | 5 (активних: 0) | — |

## Спільні правила доступу (поза профілями)

- Мітка `andrii_protected`: читання — всі; переміщення — KODEX і агенти; редагування/видалення — лише з дозволу Андрія.
- Файли без мітки: KODEX і агенти редагують, сортують, видаляють самі; усе йде у звіт Єві.
- Інтернет і будь-яке завантаження (включно з YouTube) — лише з підтвердження Андрія.
- Видалення — у кошик на 30 днів; остаточне видалення автоматичне.
- Telegram: лише Андрій (allowlist); порожній allowlist = відмова.
