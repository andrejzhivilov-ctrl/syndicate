# Architect — каталог кандидатів (GitHub)

**Статус:** огляд 2026-10-09. Нічого не встановлено, не ingest, не live n8n.
Скіли в профілі — `activation=draft`. «Погодити» ≠ grant.

## Брати як чергу (окреме «так»)

| Кандидат | Навіщо | Не робити зараз |
|---|---|---|
| Власний mermaid з JSON (уже в `architect_preview.py`) | Наочна схема зв’язки без n8n API | Не піднімати live editor |
| [jwa91/n8nmermaid](https://github.com/jwa91/n8nmermaid) (MIT) | Зрілий JSON→mermaid CLI/UI | Не вендорити WebUI/API; не сканувати чужий хост n8n |
| [nedeadinside/likec4-skill](https://github.com/nedeadinside/likec4-skill) | C4/LikeC4 з валідацією CLI | Не ставити як Hermes skill без HITL |
| [ythalorossy/architecture-skills](https://github.com/ythalorossy/architecture-skills) | C4 з локального репо | Лише локальний код, не прод-скан секретів |
| [muthub-ai/c4-skills](https://github.com/muthub-ai/c4-skills) | C4 + ADR (MADR) | Не git write |
| Існуючі `flowlint` + `n8n_builder` у репо | Core nodes, `active=false` | Не вмикати golden Telegram-ноду як live бот |

## Не тягнути оптом

| Репо | Чому |
|---|---|
| Збірки «2000 n8n workflows» | Community nodes, невідомі credentials, active workflows |
| n8n templates, що читають **live API** інстанса | Потрібен n8n grant, якого немає |
| MCP/community nodes | Політика: `N8N_COMMUNITY_PACKAGES` не вмикати |

## Контроль системи (доктрина, не host_control)

Архітектор **наглядає за кресленнями**: чернетки JSON, схеми, lint, Blueprint HITL. Він не root хоста, не GitOps-push, не live n8n, доки Андрій не видасть точний id.
