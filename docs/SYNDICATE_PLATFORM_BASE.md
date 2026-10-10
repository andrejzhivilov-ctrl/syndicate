# SYNDICATE — базова платформа

**Дата:** 2026-10-06
**Фаза:** спільний каркас перед опрацюванням агентів по одному.
**Статус:** контракти й локальні policy-механізми реалізовані та протестовані; Hermes runtime, його service API та production-запуск тут **не підключені**.

## 1. Межі цієї фази

На цьому етапі створюється лише платформа, спільна для майбутніх профілів:

- кожен майбутній агент працює на окремому Hermes runtime/profile;
- **кожен агент — у окремому контейнері** (рішення Андрія 2026-10-10, див. `docs/DECISIONS_ANDRII.md`);
- LangGraph залишається зовнішнім координатором SYNDICATE;
- доступи описуються явними capability/resource scope, без wildcard і без успадкованих прав;
- пам’ять і сервіси підключаються через адаптери, а не прямі секрети в prompt/config;
- зовнішні виклики мають спільну policy-перевірку й мінімізований audit;
- небезпечні дії не виконуються цим dispatcher без окремого human-approval флоу.

**Не входить:** ролі, системні промпти, моделі, інструменти й конкретні права окремих агентів; реальне підключення NotebookLM, Obsidian чи Google Drive; нові credentials; production deployment. Ці рішення приймаються окремо для кожного агента. Маніфести `prepared_not_enabled` у `config/agents/` з порожніми grants **не** є активацією runtime. Сформовані ідентичності зараз: Єва; Архітектор (чернетки n8n). Інші — лише слоти без погодженої ролі.

`SYNDICATE` — назва системи; Єва є майбутнім агентом-координатором, а не назвою всієї платформи. Цей нейтральний каркас не призначає Єві чи будь-якому іншому профілю окрему бізнес-роль або привілей.

## 2. Цільовий потік

```text
вхідна задача
    │
    ▼
LangGraph (маршрутизація та координація)
    │
    ▼
AgentDispatcher ── AgentRegistry ── AgentPolicy
    │                                  ├─ exact capability/resource check
    │                                  └─ allow / deny / approval_required
    ├─ PII-redaction перед runtime
    ├─ AgentRuntime protocol ── майбутній Hermes adapter/profile
    └─ privacy-minimized event ── MemoryManagerAuditSink ── audit.decisions

Hermes tool call (майбутній шлях)
    └─ лише через ToolRegistry / scoped service adapter + ту саму policy
```

LangGraph має вирішувати, **який** профіль викликати; control plane перевіряє, **чи можна** його викликати; Hermes виконує обмежений turn. Класифікатор дії, capability та scope формує довірений host/tool catalog — не Hermes, не prompt і не відповідь моделі.

## 3. Реалізовані контракти

Пакет `src/agent_platform/` наразі містить:

- `AgentProfile`: обов’язковий Hermes runtime/profile, унікальний `memory_namespace`, порожні grants за замовчуванням; ролі й credentials відсутні.
- `AgentRegistry`: immutable registry; дублікати agent ID, Hermes profile або memory namespace відхиляються. Відсутній ID не підміняється default-агентом.
- `AgentPolicy`: fail-closed перевірка capability, точного resource scope та класу дії. `memory.*`, `service.*` і `location.*` вимагають явного scope; wildcard не підтримується.
- `AgentDispatcher`: лише за дозволу маскує PII і викликає інжектований runtime. Для deny/approval-required Hermes не запускається. Prompt, output і текст exception не пишуться в audit/log.
- `MemoryManagerAdapter`: прив’язаний до одного `AgentProfile` і task session; namespace не можна передати іншим аргументом. `memory.read`/`memory.write` — окремі grants; текст редагується від PII, а metadata обмежена allowlist коротких ідентифікаторів.
- `ServiceAdapter`: інтерфейс для майбутнього сервісного backend. Реалізація має звіряти кожну операцію з host-owned tool catalog, `AgentPolicy` і точним scope до побічного ефекту. Наявний `ToolRegistry` ще не підключений до цієї нової policy автоматично; зв’язувальний wrapper треба реалізувати й перевірити до видачі tools.
- `MemoryManagerAuditSink`: адаптує dispatch-статуси до наявного append-only `audit.decisions`; передає тільки контрольовані labels/status/details.

Це **не означає**, що Hermes tools уже проходять через цю політику: живого Hermes tool bridge немає. Реалізація Hermes runtime має блокувати його неузгоджені вбудовані інструменти й передавати кожен дозволений tool call через SYNDICATE gateway. Без цього live adapter не вмикати.

## 4. Обов’язкові межі доступу та погоджень

### Доступи

- Новий profile починається без capability та resource grants.
- Memory namespace ізольований і унікальний; додаткові namespace/resource доступи — лише точними явними grants.
- Секрети не зберігаються у profile manifest, prompt, audit чи в цій платформі; майбутня видача секретів іде через Vault/scoped connector.
- Автоматичне навчання можливе лише в межах уже наданих компетенцій/прав. Registry не має API самозміни; агент не може сам додати собі capability, сервіс або ресурс.
- Навички та пропозиції про зміну прав/політик/підключень збираються Євою в окремий розділ вечірнього звіту. Єва не схвалює такі зміни замість Андрія.

### Дії, які потребують людського підтвердження

`AgentPolicy` повертає `approval_required` і не викликає Hermes для фінансових операцій (зокрема ордерів/торгівлі/переказів), видалення даних чи пам’яті, security-змін, production-деплою, зовнішніх комунікацій, зміни повноважень/політик, підключення сервісу, розширення resource scope та location access. Реальний шлях «створити proposal → Андрій переглянув → схвалив/відхилив → контрольований виконавець» ще треба зв’язати з наявним HITL/Change Request флоу; цього коду тут немає.

Окремі заборони/налаштування за замовчуванням:

- `communication.email.send` — не видавати; для пошти допускаються лише чернетки.
- Автоматизований вхід AI до Дії, Армія+ чи BankID — поза межами системи.
- Підміна browser fingerprints і ротація residential proxies для обходу захистів сервісів — поза межами архітектури.
- GPS, геолокація й геомітки вимкнені за замовчуванням; немає прихованого виведення місця з IP/таймзони/метаданих. Location access відсутній у профілях і policy-обмежений; підтримку можна додати лише з окремою явною згодою користувача.

## 5. Hermes — інтеграційний блокер, а не заявлена працездатність

Офіційний Hermes має окремі шляхи інтеграції (ACP, TUI gateway, HTTP API server і Python in-process API); профілі ізолюють конфігурацію, сесії, skills і пам’ять. Перелік API та їх семантика змінюються разом із Hermes. Офіційний `pyproject.toml` на дату перевірки пояснює, що Python 3.11–3.13 допускаються для перехідного updater-шляху, тоді як актуальні залежності runtime прив’язані до Python 3.14. Поточний SYNDICATE agent image базується на Python 3.11.

Тому в цій фазі **не імпортуємо** Hermes у процес SYNDICATE, не додаємо неперевірену залежність, не запускаємо інсталяційний скрипт і не додаємо Hermes service до Compose. Транспорт/API, версію/commit, окремий runtime image, toolsets, storage і sandbox спершу треба зафіксувати й протестувати. HTTP API не вважати безпечним лише тому, що він внутрішній: профіль не має отримати shell/filesystem/browser/messaging чи credentials без окремого перегляду й контрольованого tool bridge.

Довідка, перевірена 2026-10-06:

- [Hermes Agent — programmatic integration](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/programmatic-integration.md)
- [Hermes Agent — API server](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/api-server.md)
- [Hermes Agent — pyproject.toml](https://github.com/NousResearch/hermes-agent/blob/main/pyproject.toml)

Ці посилання описують upstream, не доводять, що інтеграція працює в цьому репозиторії.

## 6. Перевірка й межа готовності

Додані unit-тести в `tests/test_agent_platform.py` перевіряють: відсутність default grants, унікальність профілів/namespaces, exact scopes, критичні HITL-зупинки, неприпустимі capabilities, PII-redaction, відсутність payload у audit, деградацію runtime/audit і прив’язку memory adapter до одного namespace.

Зелений `bash tools/check.sh` означає лише, що репозиторний код/контракти пройшли наявні локальні ворота. Він **не** означає, що встановлено Hermes, працює його API, готові сервісні адаптери або дозволено production deployment.

## 7. Наступні кроки — тільки після окремого рішення

1. Перевірити й закріпити Hermes upstream tag/commit, спосіб інсталяції та transport; зробити окремий безпечний smoke-test із порожнім профілем.
2. Перевірити, як у конкретній версії вимкнути або проксіювати кожен Hermes built-in tool; випробувати неавторизований/зовнішній tool call і approval pause.
3. Спроєктувати маніфест без секретів та окремі Vault grants/runtime homes; не створювати production профілі до обговорення ролей.
4. З’єднати tool/service gateway, memory namespaces, поточний HITL і audit; перевірити точні ресурси на негативних і позитивних тестах.
5. Лише потім опрацьовувати одного агента за раз: роль, модель, prompt, пам’ять, skills, сервіси, allowlist і red lines — із погодженням Андрія. Для Архітектора зараз є лише default-deny контракт (`config/agents/architect.profile.json`); конкретні права ще не визначені, профіль не активований, n8n workflow не запускалися.
6. Production deployment лишається окремою фазою та потребує прямого підтвердження.
