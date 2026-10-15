# Кожен агент — в окремому контейнері

**Рішення Андрія 2026-10-10** (`docs/DECISIONS_ANDRII.md`): при розгортанні кожен агент запускається у власному контейнері. LangGraph — зовнішній координатор.

**Статус:** основний `docker-compose.yml` містить `eva-agent`. Окремий `deploy/docker-compose.directors.yml` тепер готує Oscar/Tyler/Jack tool workers: ізольовані мережі, томи, Vault AppRole, API auth і operator action allowlists. Образ збирається; локальні сценарії перевірено в контейнері. Це не Hermes runtime і не активація директорів. Інструкція та точні межі — [DIRECTORS_DEPLOYMENT.md](DIRECTORS_DEPLOYMENT.md).

**Платформа агентів:** runtime — **Hermes Agent**, координація — **LangGraph** (підтверджено Андрієм). Що є в репозиторії:
- LangGraph: `src/orchestrator.py` (наявна оркестрація, `StateGraph`).
- Hermes: лише контракти й межа викликів (`src/agent_platform/contracts.py`, `dispatcher.py`, `RuntimeKind.HERMES`). Живого Hermes-клієнта, образу контейнера й сервісу **немає**: ці частини треба ще написати/встановити.

Жоден агент не активовано.

## Цільова схема

```text
LangGraph (координатор, окремий сервіс)
   │  внутрішня мережа, без публічних портів
   ├── eva-agent     (контейнер Єви)
   ├── doc-agent     (контейнер Дока)
   ├── fin-agent     (контейнер Фіна)
   ├── sam-agent     (контейнер Сема)
   ├── architect-agent / marshal-agent / kira-agent  (за погодженням Андрія)
   └── kodex-agent   (сховище й звіт Єві; Telegram-бот окремо, лише Андрій)
```

## Принципи

- **Один агент — один контейнер — один Vault-токен.** Політики вже розділені: `config/vault/policies/eva-*.hcl`. Агент бачить лише свої секрети (`AGENT_SERVICES` у `src/vault_paths.py`).
- **Окрема мережа на агента.** Агент не спілкується з агентом напряму. Лише через LangGraph або KODEX.
- **Права з профілю.** `config/agents/<id>.profile.json` → `tools/export_permissions.py` → `docs/PERMISSIONS_MATRIX.md`. Порожні `grants` = відмова.
- **Файли без мітки.** Усі зміни (ingest агентом, редагування, переміщення, видалення, автоочищення кошика) йдуть у звіт Єві (`KodexStore.report_for_eva`).
- **Кожен контейнер стартує окремо.** Жоден агент не запускається без окремого погодження Андрія.

## Що треба до реалізації

1. Реалізувати Hermes-клієнт (межа вже є в `src/agent_platform/`) і зібрати образ Hermes-runtime.
2. Додати по одному сервісу в `docker-compose.yml` з `profiles: ["agents"]`, щоб звичайний `up` їх не запускав.
3. Для кожного: окремий `Dockerfile`, мережа, Vault-токен, healthcheck.
4. Тест: агент без `grants` не може викликати інструмент; звіт KODEX містить усі його файлові дії.
