# Інструменти й доступи Архітектора v0.1

**Профіль:** `config/agents/architect.profile.json`.
**Поточний стан:** жоден сервісний конектор не надано; `capabilities`, `resource_scopes`, `services_enabled` порожні.

## Базова взаємодія

Архітектор може обговорювати структуру неактивного n8n JSON і статичні правила якості. Це не право викликати n8n API, імпортувати workflow, тримати credentials або змінювати production.

Історичний код `src/agents/architect/` (генератор, FlowLint, gitops bundle) є репозиторним інструментом розробки. Він **не** є виданим Hermes-toolset і не вмикається цим профілем.

## Підключення сервісів

Кожне майбутнє підключення — окреме погодження: сервіс, мета, точна операція, мінімальний scope, відкликання.

- Не просити секрет у чаті.
- Не класти секрети в prompt, git, n8n JSON, execution data, логи.
- Не надавати n8n admin, credential CRUD, shell, довільний HTTP, browser-login, GitHub write, Docker.
- n8n не є органом управління агентами.

Старий рядок Vault `architect → mcp` стосується історичного спільного процесу; він **не** скопійований у `services_enabled` і не є platform grant.

## Режими

У профілі вимкнені: `n8n_editor`, `gitops_push`, `host_control`, `telegram_bot`, `geolocation`. Live n8n API вимкнений.
