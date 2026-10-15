# 🌐 SYNDICATE

> **A modular multi-agent AI platform with privacy-conscious memory and controlled integrations.**

**Стан:** розробка базової платформи; не production-ready. Репозиторій містить як нові платформні контракти, так і історичну реалізацію агентів. Наявність коду, Docker-сервісу чи опису інтеграції сама по собі не означає, що компонент підключений, дозволений або працює.

Актуальна архітектурна основа — [`docs/SYNDICATE_PLATFORM_BASE.md`](docs/SYNDICATE_PLATFORM_BASE.md). SYNDICATE — назва платформи; Єва — окремий агентський профіль, а не назва всієї системи. Профілі, ролі, моделі й права визначаються та погоджуються окремо.

## Архітектура

Цільовий потік запитів:

```text
Клієнт
  │
  ▼
FastAPI — API / транспорт
  │
  ▼
LangGraph — оркестрація та вибір наступного кроку
  │
  ▼
AgentRegistry + AgentPolicy + AgentDispatcher — профіль, capability, resource scope
  ├──► окремий Hermes runtime/profile на агента (ціль; runtime ще не підключений)
  ├──► обмежені service adapters (лише після окремого погодження)
  └──► ізольовані memory namespace та мінімізований audit

n8n — виконання workflow та інтеграцій; не control plane і не джерело дозволів
```

Це **цільова схема, а не твердження про готову інтеграцію**. Контракти та локальні policy-механізми платформи реалізовані й тестуються, але новий `AgentDispatcher` ще не з’єднаний із LangGraph і живим Hermes runtime. Детальні блокери та межі готовності описані в [`docs/SYNDICATE_PLATFORM_BASE.md`](docs/SYNDICATE_PLATFORM_BASE.md).

| Компонент | Призначення і поточний стан |
|---|---|
| **FastAPI** | API-поверхня наявної системи; API не надає агентам додаткових прав. |
| **LangGraph** | Оркестрація задач у наявному backend-коді; новий policy dispatcher ще не інтегрований у цей потік. |
| **Agent platform** | `AgentProfile`, immutable registry, default-deny policy, dispatcher та adapter-контракти в `src/agent_platform/`; локальні тести є, live runtime bridge — ні. |
| **Hermes** | Цільовий окремий когнітивний runtime/profile для кожного агента. Не встановлений і не запускався в межах цієї підготовки. |
| **n8n** | Workflow та інтеграції. Не control plane; workflow не може самостійно розширювати профілі чи scope. Профіль Архітектора — `prepared_not_enabled` без grants; права, модель і інтеграції ще не визначені. |
| **PostgreSQL + pgvector** | Наявне backend-сховище для структурованих даних, audit і семантичного пошуку. |
| **Redis** | Кеш/короткоживучий стан; не канонічний архів знань. |
| **HashiCorp Vault** | Інтерфейси та політики роботи із секретами; секрети не зберігаються в README, prompt чи profile manifest. |

## Пам’ять і зовнішні сервіси

Для різних типів даних передбачені різні межі; жоден сервіс не отримує автоматично доступ до всього архіву.

- **Obsidian** — канонічний архів погодженої пам’яті Єви за її політикою. Production-шлях, mount і connector ще не підтверджені.
- **Supabase** — платформа навколо PostgreSQL з Auth, Storage, Realtime та іншими сервісами ([огляд](https://supabase.com/docs/guides/database/overview)); зараз не підключений. Старі документи згадують його як можливу Phase 2, але це не чинне рішення про інтеграцію чи дзеркалювання даних. Перед використанням треба визначити єдине джерело істини, щоб не створити дві конкуруючі копії PostgreSQL.
- **Nextcloud** — open-source платформа для файлів і спільної роботи ([офіційний сайт](https://nextcloud.com/)); кандидат на окремий файловий простір, не на заміну базі даних чи канонічній пам’яті. Інтеграції немає; можливий доступ Єви до конкретно вибраних папок потребуватиме окремого погодження.

## Поточний статус

### Реалізовано та перевіряється локально

- Контракти профілів, registry, exact-scope policy, approval gates, PII-redaction та мінімізований audit у `src/agent_platform/`.
- Існуючий Python/FastAPI/LangGraph backend, PostgreSQL/pgvector, Redis та Vault-компоненти.
- Eva-специфічна політика пам’яті й підготовлений профіль без активних grants.

### Не підключено або не активовано

- Hermes runtime, його transport/API, sandbox і контрольований tool bridge.
- Зв’язок нового `AgentDispatcher` з LangGraph та живим агентським runtime.
- Production deployment, активні service credentials і нові інтеграції.
- Supabase та Nextcloud connectors.
- Психологічний корпус знань: реєстр джерел порожній, матеріали не завантажені.

### Межі профілю Єви

`config/agents/eva.profile.json` позначає Єву як `prepared_not_enabled`; `capabilities`, `resource_scopes` і `services_enabled` порожні. Пам’ять проєктується лише на `agents/eva` (cross-agent deny). Telegram inbound вимкнений, порожній allowlist = deny. Нічний контракт — 03:00 `Europe/Kyiv`, source provider не налаштований. `AgentDispatcher` ще не стоїть на історичних маршрутах Єви — активні grants не додавати. Деталі: [`eva_core/`](eva_core/).

### Межі профілю Архітектора

`config/agents/architect.profile.json` — завершений `prepared_not_enabled` пакет. Чернетки n8n з mermaid-прев’ю (`tools/architect_preview.py`). Задачі лише Андрій. Дозволи: [`ARCHITECT_PERMISSIONS.md`](architect_core/ARCHITECT_PERMISSIONS.md). Grants порожні; n8n не live; git push вимкнений.

### Межі профілю Marshal

`config/agents/marshal.profile.json` — `prepared_not_enabled`, порожні grants. CSO-архетип, observe+HITL лише на критичне; інтернет за командою Андрія не блокується. Ранбук: [`marshal_core/MARSHAL_DEPLOYMENT_RUNBOOK.md`](marshal_core/MARSHAL_DEPLOYMENT_RUNBOOK.md). Сканер пропозицій: `bash tools/install_skillspector.sh` (Python 3.12+, не в runtime image) і `python tools/marshal_skill_scan.py`. Telegram, veto, n8n, Drive, TTS вимкнені.

### Інші підготовлені маніфести (ще не сформовані)

`fin`, `doc`, `kira`, `sam` мають `prepared_not_enabled` файли в `config/agents/` з порожніми grants і `role_status=not_agreed`. Історичні специфікації в `*_core/` не є активними ролями. Sentinel і Council не включаються.

## Принципи безпеки

- Новий профіль починається без capability та resource grants; scope — точний, не wildcard.
- Модель, prompt, відповідь агента й вхідний payload не можуть самі надати дозвіл.
- Фінансові дії, видалення, зовнішні комунікації, security/production-зміни та розширення прав потребують людського підтвердження.
- PII редагується до передачі зовнішньому runtime; секрети не потрапляють у prompt, логи чи пам’ять.
- GPS, геолокація та геомітки вимкнені; місце не виводиться з IP, часової зони чи метаданих.
- Агентам не призначаються задачі одне одному без прямого прохання користувача.

## Структура репозиторію

```text
.
├── src/agent_platform/       # Профілі, policy, registry, dispatcher та adapters
├── src/orchestrator.py       # Наявна LangGraph-оркестрація
├── src/memory.py             # PostgreSQL/pgvector, cache та audit-шляхи
├── src/vault_md.py           # Markdown/Obsidian-політики пам’яті
├── config/agents/             # Маніфести агентських профілів
├── config/postgres/           # SQL-схема й міграції
├── eva_core/                  # Межі ролі Єви, пам’ять, workflow та readiness
├── architect_core/            # Gap analysis і default-deny контракт Архітектора (не activation)
├── docs/SYNDICATE_PLATFORM_BASE.md # Актуальний нейтральний платформний дизайн
├── deploy/                    # Наявні deployment-конфігурації; не доказ live deployment
├── apps/                      # Клієнтський застосунок, окрема зона
└── tests/                     # Unit, regression, routing і PostgreSQL-тести
```

У репозиторії також зберігаються історичні 10-поверхові й агентські специфікації. Вони не є автоматичним джерелом активних ролей, доступів чи стану сервісів; для нового цільового контуру орієнтуйтеся на `docs/SYNDICATE_PLATFORM_BASE.md` та актуальні профілі в `config/agents/`.

## Перевірка

Потрібні Python і залежності з `requirements.txt` та `requirements-dev.txt`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
bash tools/check.sh
```

Quality gate запускає тести, лінтери, перевірки API-контракту й Vault-політик, а також перевірку PostgreSQL-шляхів, якщо доступний `pgserver` або заданий `EVA_TEST_DATABASE_URL`. Зелений результат підтверджує лише локальні перевірки коду — **не** готовність Hermes, сервісних інтеграцій чи production deployment.

Production-запуск, активація Hermes і підключення сервісів потребують окремого технічного перегляду та явного погодження.

## Розгортання

Пакет розгортання, права і відкриті питання: [`docs/DEPLOY_SYNDICATE.md`](docs/DEPLOY_SYNDICATE.md). Матриця прав (генерується): [`docs/PERMISSIONS_MATRIX.md`](docs/PERMISSIONS_MATRIX.md). Серверні кроки: [`DEPLOYMENT_RUNBOOK.md`](DEPLOYMENT_RUNBOOK.md).

## Oscar, Tyler та Jack: backend workers

Додано локальні інструменти трьох директорів: медіа-драфти й дослідження Оскара, POD-маржа та персоналізація Тайлера, спортивні математичні моделі й paper-аудит Джека. Профілі та дев’ять власних скілів підготовлено без автоматичної активації.

- [Розгортання, доступні дії та межі інтеграцій](docs/DIRECTORS_DEPLOYMENT.md)
- [56 GitHub-кандидатів скілів із зафіксованими ревізіями](docs/DIRECTOR_SKILLS_CATALOG.md)
- [Матриця прав](docs/PERMISSIONS_MATRIX.md)

### Перевірена бібліотека скілів

[Розподіл між 12 агентами, аудит 26 GitHub-джерел та використання](docs/SKILL_LIBRARY.md).
Локальні матеріали перевіряються за pinned commit/SHA256; встановлення скіла не активує зовнішні сервіси.

## Паспорт системи та інтеграції

[Детальний паспорт усіх агентів](docs/SYSTEM_PASSPORT.md): можливості, скіли, обов’язкові й рекомендовані сервіси, розгортання та межі готовності. Integration worker: `deploy/docker-compose.integrations.yml`; приклади Vault/MCP: `config/integration_worker.example.json`, `config/integration_mcp.example.json`.
