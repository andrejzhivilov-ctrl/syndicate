# Marshal — запропоновані межі доступу v0.3

**Статус:** чернетка. Це **не** активні grants.
**Профіль:** `prepared_not_enabled`, порожні `capabilities` / `resource_scopes` / `services_enabled`.
**Модель роботи:** `MARSHAL_OPERATING_MODEL.md`. HITL: `MARSHAL_HITL_CONTRACT.md`.

Жоден рядок не записується в активний grant, доки Андрій не погодить точний id **і** маршрути Marshal не проходитимуть через `AgentDispatcher`.

## Запропоновані межі (не видані)

| Кандидат | Межа |
|---|---|
| `memory.read` / `memory.write` | лише `agents/marshal`; briefs/HITL audit, не сирі payload |
| cross-agent memory | deny; Єва не читає namespace Маршала, Маршал не читає Єву |
| щоденний brief → Єва | лише як поле `agent_data.marshal` у payload брифу; не виклик агента |
| `policy.veto` | кандидат після шару Observe + Dispatcher; не Andrii; таймаут = deny |
| host control / lockdown / network sever | deny |
| Telegram inbound / alert send | окремий бот; `enabled=false`; bot_id і allowlist не вигадувати |
| n8n aggregator | не control plane; `activation=not_enabled`; не джерело прав |
| Cloudflare | не для внутрішніх метрик; пізніше лише публічний ingress |
| Drive workspace | `folder_id=null`; не джерело прав |
| knowledge/security | `sources: []`; read-only після ingest, ingest немає |
| MCP / HoneyMCP / SkillSpector | не копіювати з Vault у `services_enabled` |
| Sentinel / Sentyr / Council / Tetragon | out of scope / Фаза 2 |
| TTS / voice | deny |
| секрети Vault, `.env`, тексти інших агентів | deny |
| зміна `EVA_CORE_PERSONA.md` / коду Marshal / само-grant | deny |

## Блокери

- `AgentDispatcher` не стоїть на `MarshalAgent` / LangGraph.
- Історичний `sentinel_*` в оркестраторі — не профіль Marshal.
- Vault `marshal → mcp, telegram` — стара HCL-мапа, не grant.
- Оркестраторний `emergency_lockdown` fail-closed як `denied`.
