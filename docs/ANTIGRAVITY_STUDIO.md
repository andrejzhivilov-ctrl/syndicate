# Antigravity Studio — локальні handoff-інструменти

**Antigravity — технологія; Аліса — агентка.** Опис API-first runtime Аліси, ролі, профілю, grants, Vault та deployment prerequisites міститься в [`docs/ALICE_RUNTIME.md`](ALICE_RUNTIME.md).

Цей окремий Studio/CLI-каркас призначений лише для локальної, вручну контрольованої підготовки матеріалів. Він не є особистістю чи runtime Аліси, не є Gemini API adapter і не входить автоматично до orchestrator. Він не автентифікується через Google One, не читає browser cookies/session і не автоматизує desktop. Якщо оператор вручну використовує зовнішній Google/Antigravity продукт, це окрема дія поза SYNDICATE; Google One не є API credential.

## Поточні межі

- Конфігурація агентки й grants: `config/agents/alice.profile.json`; активні capabilities/grants порожні.
- API-first worker: `src/agents/alice.py`; окремий API runner і опційний Compose overlay — див. `docs/ALICE_RUNTIME.md`.
- `tools/antigravity_studio.py` — локальний handoff/helper, не онлайн-модель, не повний coding environment і не deployment agent.
- Немає автоматичного запуску коду, публікації, PR/merge, платежів або серверного deployment.
- Живі API, Vault, Docker build та сервер у цій задачі не перевірялися й не активувалися.

Будь-які зміни до особистої історії, workspace mount, приватних даних чи зовнішніх доступів потребують окремого погодження та збереження чинних ACL. Не читати й не передавати `EVA_SYNDICATE_FULL_DIALOGUE.txt`; особисті файли — лише в погодженому `EVA_DATA_DIR`/`KODEX_DATA_DIR`.
