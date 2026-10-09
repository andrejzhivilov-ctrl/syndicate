# Marshal — запропоновані межі доступу v0.2

**Статус:** чернетка. Це **не** активні grants.
**Профіль:** `prepared_not_enabled`, порожні `capabilities` / `resource_scopes` / `services_enabled`.
**Розбір досьє:** `MARSHAL_DOSSIER_REVIEW.md`.

Жоден рядок не записується в активний grant, доки Андрій не погодить точний id **і** маршрути Marshal не проходитимуть через `AgentDispatcher`.

## Запропоновані межі (не видані)

| Кандидат | Межа |
|---|---|
| `memory.read` / `memory.write` | лише `agents/marshal`; аудити не пишуться автоматично |
| cross-agent memory (Єва 03:00, rollback чужих фактів) | deny |
| `policy.veto` / скасування дій Єви | не пропонувати в профіль, доки немає окремого рішення Андрія |
| host control / `emergency_lockdown` / network sever | deny |
| Telegram `@marshal_security_bot` | не підключати; порожній allowlist = deny; bot_id не вигадувати |
| MCP / HoneyMCP / SkillSpector | не копіювати з Vault-мапи в `services_enabled` |
| Sentinel / Sentyr / Council / Tetragon | out of scope / Фаза 2 |
| читання секретів Vault, `.env`, робочих текстів агентів | deny |
| зміна `EVA_CORE_PERSONA.md` / власного коду Marshal | deny |

## Блокери

- `AgentDispatcher` не стоїть на `MarshalAgent` / LangGraph (`security_audit`, `emergency_lockdown`, …).
- Історичний `src/agents/sentinel.py` і task types `sentinel_*` лишаються в оркестраторі; це **не** профіль Marshal і не вмикати.
- Vault `marshal → mcp, telegram` — стара HCL-мапа, не platform grant.
- `_emergency_lockdown` у агенті все ще може повернути `LOCKDOWN_ACTIVE` при прямому `execute`; оркестраторний task `emergency_lockdown` fail-closed як `denied`.
