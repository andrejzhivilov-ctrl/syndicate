# Sam — дозволи (підготовка)

**Чинні права в профілі:** порожні `capabilities` / `resource_scopes` / `services_enabled`.
Скіли — `activation=draft`, не Hermes install.

Перемикач auto і міст брокера **є в коді** і **вимкнені**.

## Дозволено зараз (хост-код, без capability)

| Дія | Код |
|---|---|
| Взяти задачу від Андрія | `sam_accepts_task` |
| Порахувати confluence fail-closed | `ConfluenceEngine` |
| Показати шлях HITL vs auto-eligible | `decide_execution` |
| Відмовити брокер без конектора | `submit_lot` → `broker_unavailable` |
| Звіт Єві payload | `build_eva_digest` |

## Не видано

trade.execute, broker_demo, broker_live, auto_fx_crypto (прапор false), auto_invest (код завжди false), Telegram, voice, cockpit, Drive, Obsidian, NotebookLM, social_listen, n8n, Hermes start, GPS.
