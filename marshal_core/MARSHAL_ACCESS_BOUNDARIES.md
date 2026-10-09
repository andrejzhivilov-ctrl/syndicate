# Marshal — запропоновані межі доступу v0.1

**Статус:** чернетка. Це **не** активні grants.
**Профіль:** `prepared_not_enabled`, порожні `capabilities` / `resource_scopes` / `services_enabled`.

Жоден рядок не записується в активний grant, доки Андрій не погодить точний id **і** маршрути Marshal не проходитимуть через `AgentDispatcher`.

## Запропоновані межі (не видані)

| Кандидат | Межа |
|---|---|
| `memory.read` / `memory.write` | лише `agents/marshal` |
| cross-agent memory | deny |
| host control / `emergency_lockdown` | deny, доки немає окремого scope |
| Telegram `@marshal_security_bot` | не підключати; порожній allowlist = deny |
| MCP | не копіювати з Vault-мапи в `services_enabled` |
| Sentinel / Council / Tetragon | out of scope |

## Блокери

- `AgentDispatcher` не стоїть на `MarshalAgent` / LangGraph (`security_audit`, `emergency_lockdown`, …).
- Історичний `src/agents/sentinel.py` і task types `sentinel_*` лишаються в оркестраторі; це **не** профіль Marshal і не вмикати.
- Vault `marshal → mcp, telegram` — стара HCL-мапа, не platform grant.
- `_emergency_lockdown` у агенті все ще може повернути `LOCKDOWN_ACTIVE` при прямому `execute`; оркестраторний task `emergency_lockdown` fail-closed як `denied`.
