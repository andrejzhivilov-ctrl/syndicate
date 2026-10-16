# Аліса — API-first інженерний runtime

**Стан на 2026-10-16: підготовлено в коді, не активовано, не розгорнуто.** Аліса — ім’я агентки; Antigravity SDK — технологічний runtime. Єва залишається єдиною CEO.

Усе default-off: `config/agents/alice.profile.json` має `prepared_not_enabled`, порожні активні `capabilities`/`grants`/`resource_scopes`/`services_enabled`; у `.env.example` worker вимкнений, дозволена лише дія `capabilities`, API та egress-підтвердження вимкнені, добові ліміти дорівнюють нулю. Vault policy описана, але не застосовувалась. Секрети не створювались і не переносились. API, Compose build, контейнер та сервер наживо не перевірялися.

## Роль і межі

- Роль: **керівниця інженерного відділу (Head of Engineering)**, звітує Єві. Промпт в `src/agents/alice_runtime_prompt.md` задає теплий, проактивний, стратегічний та доказовий стиль.
- Початкові задачі після окремої активації: інженерна робота й code review у власному workspace.
- Єва — єдина CEO. Аліса не змінює права, не затверджує власні grants, не зливає PR і не розгортає production.
- Не надаються shell, browser/desktop automation, вебпошук, читання URL, MCP, subagents, workflows, GitHub, image generation, відеогенерація, платежі, Telegram або глобальний доступ до пам’яті.
- SDK-файлові інструменти обмежені workspace. Код не виконується в контейнері з Vault-секретами; цей runtime не має `run_command`.

## API та перевірка SDK

Підготовлений adapter використовує `google-antigravity==0.1.22` із PyPI та `LocalAgentConfig`/`GeminiAPIEndpoint` SDK. Метадані PyPI вимагають Python ≥3.10 та `uvicorn>=0.46`; окремий образ використовує Python 3.11 і сумісний за оголошеними залежностями. Версія перевірена за метаданими пакета й upstream source; ізольований temporary venv успішно розв’язав pinned dependencies (`pip check` без помилок). `tests/test_alice_sdk.py` побудував реальний SDK config із фальшивим локальним Agent, без мережі та provider credentials. Зовнішній API transport/model invocation не перевіряли.

У `src/agents/alice.py` модель API отримує явний список лише file tools: `LIST_DIR`, `FIND_FILE`, `SEARCH_DIR`, `VIEW_FILE`; для інженерної дії додатково `CREATE_FILE`, `EDIT_FILE`. SDK `CapabilitiesConfig.enabled_tools` задається явно, `workspaces` містить лише власний workspace, а `policy.workspace_only([workspace])` увімкнений разом із `deny_all()` та точковим allow лише для цього списку. `allow_all()` не використовується (SDK документує його як спосіб вимкнути workspace containment); у конфігурації лишається лише один workspace. Це не покладається на назву `nondestructive` чи default capabilities SDK. Vertex/Enterprise вимкнені; API key не передається в env або prompt.

Ключ Gemini API **не є** підпискою Google One. Модель не обрана. Актуальна ціна, квота та оплачувані умови не верифіковані; вважати API безкоштовним не можна. Код має per-request caps (до 3 model calls, 8 tool calls, 12 000 input і 2 048 output tokens) та локальний SQLite ledger, який зберігає лише UTC-лічильники/резерв токенів, не prompt і не output. Добові request/token caps за замовчуванням `0`, тож API-виклики блокуються. Токенний ліміт **не є** гарантією грошового ліміту: до активації потрібне окреме provider-side billing limit і перевірка тарифу.

## Профіль і grants

Джерело прав — `config/agents/alice.profile.json`; `tools/export_permissions.py` показує proposed grants окремо від активних. Для каталогу додані підібрані reference-only інженерні матеріали (API/interface design, debugging, context engineering, ADR/docs, source/TDD, planning, security hardening). KODEX лишається власником prompt/skill engineering і каталогу; Alice не отримує повноважень редагувати/активувати скіли. SDK передає `skills_paths=[]` та `inline_skills=[]`, отже ці references не інжектуються в runtime і не надають прав. Усі proposed коди мають `proposed_not_applied`:

| Grant code | Призначення | Стан |
|---|---|---|
| `alice.model.invoke` | Виклик лише обраного Gemini Developer API | Не застосований |
| `alice.workspace.read` | Читання `alice/workspace` | Не застосований |
| `alice.workspace.write` | Запис лише в `alice/workspace` | Не застосований |
| `alice.web.search` | Майбутній пошук із domain allowlist | Не застосований; runtime не надає інструмент |
| `alice.github.repo.read` | Майбутнє читання allowlisted репозиторіїв | Не застосований |
| `alice.github.pull_request.create` | Майбутній PR, без auto-merge/force-push | Не застосований |
| `alice.image.generate` | Майбутня image API інтеграція | Не застосований |
| `alice.video.render` | Майбутня локальна обробка в окремому sandbox | Не застосований |
| `alice.memory.read` | Майбутнє читання лише погоджених ACL-матеріалів | Не застосований |

Browser, cookies, saved sessions і Google login не мають і не матимуть запропонованого grant у цьому API-first плані.
Активний профіль зараз не має жодного з цих grants. Зміна payload-запиту не може активувати права: worker перевіряє host-owned profile, окремі action allowlist, API enable, egress/billing gates, Vault credential та scope.

## Vault references і HCL

Ключові значення не входять до Git. Профіль посилається на:

- `secret/syndicate/agents/alice/auth` — випадковий внутрішній worker API key; `deploy/scripts/vault_init.sh` створюватиме його лише коли адміністратор окремо запустить цей скрипт.
- `secret/syndicate/agents/alice/gemini` — поля `api_key` і `model`; Gemini ключ треба внести в Vault окремим захищеним процесом після вибору моделі.
- `secret/syndicate/agents/alice/anthropic` та `/github` — лише майбутні reference paths, не granted і не читані поточним кодом. Їх не додають до Alice policy, доки не буде окремої реалізації та рішення.

`config/vault/policies/eva-alice.hcl` дозволяє тільки точкові `read` для `agents/alice/auth` і `agents/alice/gemini` та їхніх KV metadata paths, плюс Vault token self-renewal/lookup. Немає wildcard на власну subtree, shared `api-keys`, database, Redis, інші агенти чи server auth. Код `vault_init.sh` формує окремий `eva-alice.approle.env` із `ALICE_VAULT_ROLE_ID`/`ALICE_VAULT_SECRET_ID`, а не Eva runtime credentials. Генератор — `tools/vault_policies.py`; перевірка — `python tools/vault_policies.py --check`. Policy/скрипт ініціалізації не застосовувалися до live Vault. Зауваження: чинна `eva-agent` runtime policy має широку wildcard-доступність до agent secrets через монолітний процес; це існуючий дизайн, окремий Alice AppRole її не успадковує. Eva coordinator читає worker auth для внутрішнього bridge; Alice provider key не потрібен coordinator, але broad runtime wildcard усе ще може охопити його.

## Deployment prerequisites (не виконано)

- Окремий образ: `deploy/docker/Dockerfile.alice`; окремий FastAPI entrypoint: `deploy/runtime/alice_runner.py`; pin SDK/dependencies: `deploy/requirements-alice.txt`.
- Compose overlay: `deploy/docker-compose.alice.yml`. Він не входить у звичайний compose stack автоматично, не публікує host port і не приєднує Alice до `backend`. Єдина зовнішня мережа — зовнішньо створений `ALICE_PROVIDER_EGRESS_NETWORK`; Compose її не створює. Без неї сервіс не стартує.
- Оверлей з’єднує Eva й Alice через окрему internal control network, Alice з Vault через окрему internal network, а зовнішній виклик — лише через заздалегідь налаштований provider-egress network. Потрібен перевірений зовнішній firewall/allowlist для точних Gemini Developer API endpoint(s), перевірених за закріпленою версією SDK, та DNS, з outbound limits. Vault доступний лише через internal network. Сам факт Docker network або env прапорець не доводить наявність firewall; підтвердження залишається operator-owned.
- Дані та workspace: `${DATA_ROOT}/eva/data/alice`, змонтований як `/data/eva/data/alice`; підкаталог `workspace` має належати UID/GID `1001:1001`, мати mode `0700` і бути окремим від репозиторію, `andrii_protected` та особистих/медичних матеріалів.
- На сервері окремо потрібно створити/перевірити Alice AppRole credentials, внести лише обраний Gemini key/model у Vault, налаштувати зовнішній egress firewall та provider-side billing limit. Не додавати секрети до `.env`, Git, prompt, чатів чи логів.

Активація вимагає всіх gate-ів разом: profile `activation=active`, модель і service у профілі, потрібні capabilities та `alice/workspace` scope, billing/egress verification, `ALICE_API_ENABLED=true`, `ALICE_PROVIDERS=gemini`, позитивні добові request/token ліміти, `ALICE_ACTIONS` allowlist, `ALICE_WORKER_ENABLED=true` та URL клієнта в Eva. Це **не інструкція застосувати їх зараз**: жоден gate не змінено і жодного сервера не запускали.

## Невирішено / наступна перевірка

1. Андрій має обрати модель та прийняти її актуальні тарифи/квоти й provider-side billing limit; Google One не використовується як API credential.
2. Потрібно узгодити конкретну зовнішню egress allowlist і межі доступу до Vault/DNS. Не створювати необмежений egress.
3. Після окремого дозволу на live Vault/deployment — застосувати generated policy, видати server-side AppRole і тільки тоді налаштовувати активні gates.
4. Кодові тести й `bash tools/check.sh` пройшли без живої PostgreSQL; Compose render/build та security scan не виконувалися. Їх запускати лише після окремого погодження. Живі API-виклики, Vault і deployment потребують окремої явної згоди.
