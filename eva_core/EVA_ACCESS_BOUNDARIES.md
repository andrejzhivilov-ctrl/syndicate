# Єва — запропоновані межі доступу v0.1

**Статус:** чернетка меж для підготовки. Це **не** активні grants.
**Профіль:** `config/agents/eva.profile.json` → `activation=prepared_not_enabled`, порожні `capabilities`, `resource_scopes`, `services_enabled`.

Жоден рядок нижче не записується в поле активного grant, доки Андрій окремо не погодить точний id **і** кожен маршрут Єви не проходитиме через `AgentDispatcher`.

## Запропоновані межі (не видані)

| Кандидат | Межа |
|---|---|
| `memory.read` | лише `agents/eva` |
| `memory.write` | лише `agents/eva`, явна команда, low-sensitivity |
| cross-agent memory | завжди deny |
| Telegram inbound | потенційний канал; `enabled=false`; порожній allowlist = deny; bot/chat id невідомі |
| `gmail.draft` | майбутній кандидат; акаунт невідомий; не інтегрувати зараз; send поза scope |
| nightly analysis | dormant; source provider не налаштований |
| psychology corpus | порожній manifest; без ingest |

## Обов’язковий блокер

`AgentDispatcher` ще не стоїть на історичних маршрутах `EvaAgent` / LangGraph (`chat`, `webhook_telegram`, curator, `parse_memory_command`). Поки його немає, **активну capability не додавати**. Підключення Dispatcher з порожніми grants fail-closed відхилить і розмову (`CAPABILITY_NOT_GRANTED`) — це окреме рішення, не зроблене в цій фазі.

Історичний `parse_memory_command` у оркестраторі все ще може маршрутизувати запис за `detect_agent()` до інших namespace. Це не маршрут профілю Єви; його не розширювати. З боку `EvaAgent` cross-agent write вже відхиляється.
