# Розгортання Oscar / Tyler / Jack

## Поточна готовність

Підготовлено окремі локальні backend workers, дев’ять власних скілів, профілі Hermes, Vault ACL та Docker Compose. Профілі залишаються `prepared_not_enabled`; production і зовнішні дії не активовані.

Ці worker-сервіси надають доменні інструменти через FastAPI. Вони **не є реалізацією Hermes runtime**. Живий Hermes runtime bridge і його policy/tool gateway залишаються окремим етапом загальної платформи. HTTP-міст LangGraph → worker реалізовано в `src/agent_platform/director_client.py`. У наявному LangGraph додано `oscar_task`, `tyler_task`, `jack_task`; за замовчуванням вони повертають `director_prepared_not_enabled`. Локальне виконання дозволяється тільки конфігурацією оператора `config[agent_id].enabled=true` та точним списком `config[agent_id].allowed_actions`.

## Реалізовані можливості

| Директор | Дії та результат |
|---|---|
| Oscar | Три персони; Grok/Gemini/Haiku router; джерельні транскрипти до 100 відео з лімітом контексту; імпорт коментарів із шести платформ, PII-маскування й дедуплікація; YouTube read adapter; чернетки, відповіді й newsletter через LLM; відкладена черга; типографічний thumbnail і SVG-схема; email-метрики з наданих лічильників |
| Tyler | Decimal net margin ≥35% з податками, доставкою та комісією; premium/ліцензійні/DPI/trademark gates; PNG 300 DPI та схематичний preview; збереження замовлень-концептів; вибір постачальника з наданих котирувань; Pinterest draft; фільтр негативних відгуків |
| Jack | Poisson/Dixon–Coles, possession/normal baseline, Markov set, independent map series, poker chip EV, ICM; EV≥4.5%, quarter Kelly та cap 1% за замовчуванням (не більше 2.5%); свіжість котирувань; пропорційне очищення маржі; The Odds API scout із явним coverage; транзакційний paper tracker, ROI, 24-годинний anti-tilt |

Точні вхідні поля й приклади — у `tests/test_directors.py`, процедури — у `<agent>_core/skills/`. `capabilities` повертає фактичний список дій із коду. Невідома дія — помилка; відсутнє поле — `unavailable` з `value:null`.

### Межі, які потрібно врахувати

- LLM-моделі обирає оператор у Vault. Заявлене у специфікації вікно Gemini 2M не гарантується. Поточний ліміт router — 200000 символів, генерація — до 4096 токенів; більший запит відхиляється.
- YouTube: до 100 top-level comments за запит, без повного дерева відповідей; для TikTok/Reddit/X/Threads/blog підтримано імпорт дозволених експортів. Автоматичних скраперів цих платформ немає.
- У worker немає LivePortrait, production-конвеєра VideoEngineV2, автоматичного створення персон чи бази email-підписників. Існуючий Content Factory залишається окремим сервісом; його мережевий рендер не запускається неявно.
- Tyler preview — схематична типографіка на футболці, не фотореалістична фотографія. SLA 10–15 секунд не виміряний. Ліцензію шрифту, CMYK, printable area, колір і розміщення підтверджує технолог перед друком.
- `trademark_reviewed` — надане оператором підтвердження, не результат USPTO-пошуку. USPTO TESS замінено новою системою; live adapter не налаштовано. Trend data, фабричні котирування й негативні відгуки надходять із дозволених джерел вручну.
- Платежі Stripe, підписані webhooks, живий storefront/chat віджет, Printify/Printful/Gelato/Prodigi submit і Pinterest publish не реалізовані як зовнішні виконувані операції. Усі концепти залишаються pending review.
- Jack моделі — явні математичні оцінки на наданих входах; вони не навчені та не відкалібровані. Tennis оцінює сет, esports використовує точний розрахунок незалежних карт, poker не є GTO solver. Backtesting і калібрування потрібні перед використанням сигналів.
- PariMatch/Vbet можуть бути відсутні в The Odds API або тарифі. Scout повертає `unavailable` для відсутніх букмекерів. Прямі приватні API букмекерів не вигадані; closing-line й live coverage не припускаються.
- Paper bankroll задається оператором у запиті; це симуляція, а не банківський баланс. Усі сигнали належать одній обліковій одиниці цього worker; multi-currency не підтримується. Подієвий cap враховує відкриті paper-позиції; void не скидає серію поразок. Anti-tilt рахує результати за UTC-часом settlement, який записує сервер.
- Telegram-картки готуються як чернетки; кнопки підтвердження і доставка потребують окремого підключення до наявного operator control plane. Автоматичного фінансового виконання немає.
- Локальні записи ізольовані за директором у SQLite; синхронізації з KODEX/центральною episodic memory ще немає. Будь-яке збереження в worker має локальний ID, час і стан; центральний audit gateway потрібно підключити до активації Hermes.

## Підготовка Vault

Для кожного директора створити **власний** AppRole з політикою `eva-oscar`, `eva-tyler` або `eva-jack` (генератор `tools/vault_policies.py --write`). Ці політики дозволяють читання лише власного `agents/<id>/*` і self-renewal токена; спільних ключів LLM, інших агентів і server auth немає.

Структура KV v2: mount `secret`, prefix `eva-syndicate`. Використовуються шляхи з `src/vault_paths.py`:

| Логічний шлях | Обов’язкові поля |
|---|---|
| `eva-syndicate/agents/<id>/auth` | `api_key`: окремий випадковий ASCII ключ, щонайменше 32 символи |
| `eva-syndicate/agents/oscar/grok` | `api_key`, `model` |
| `eva-syndicate/agents/oscar/gemini` | `api_key`, `model` |
| `eva-syndicate/agents/oscar/haiku` | `api_key`, `model` |
| `eva-syndicate/agents/oscar/youtube` | `api_key` із YouTube Data API read-доступом |
| `eva-syndicate/agents/jack/odds` | `api_key` The Odds API |

Тільки `auth` потрібен для локальних інструментів. Provider secrets читаються лише для явно ввімкнених провайдерів. Порожні й placeholder ключі блокують запуск; запит API не може вмикати провайдери чи замінювати URL. Не записувати ключі в Git, лог, shell history чи приклади. AppRole environment передавати із секретного сховища платформи розгортання.

## Збірка й локальний запуск

З кореня репозиторію:

```bash
docker build -f deploy/docker/Dockerfile.director -t syndicate-directors:local .
```

Налаштувати `VAULT_ADDR` (TLS URL доступного Vault), для кожного `OSCAR_`, `TYLER_`, `JACK_`: `VAULT_ROLE_ID`, `VAULT_SECRET_ID`. За потреби явно задати `OSCAR_PROVIDERS=grok,gemini,haiku,youtube`, `JACK_PROVIDERS=odds`. Для локальних операцій залишити provider lists порожніми. Задати `OSCAR_ACTIONS`, `TYLER_ACTIONS`, `JACK_ACTIONS` як точні comma-separated списки дозволених дій; за замовчуванням доступна тільки `capabilities`. Цей operator allowlist обмежує інструменти worker і не змінює Hermes grants.

```bash
docker compose -f deploy/docker-compose.directors.yml --profile directors config -q
docker compose -f deploy/docker-compose.directors.yml --profile directors up -d --build
```

Compose не публікує host ports. Кожен директор має власну bridge network, volume, AppRole і ключ API; спільної мережі між директорами немає. Vault має бути доступним за зовнішнім URL або через додану оператором мережу до кожного конкретного worker. Підключити координатор до потрібних control networks окремо, не з’єднувати директорів між собою. На координаторі явно задати `<ID>_WORKER_ENABLED=true`, `<ID>_WORKER_URL=http://<id>-agent:8000` та `<ID>_COORDINATOR_ACTIONS` — власний список дозволених дій. І координатор, і worker перевіряють allowlist; API key координатор читає з Vault лише для конкретного директора. Ці параметри не активують Hermes-профіль. Для першого запуску потрібен вихід до Vault; provider traffic — лише для обраних провайдерів.

Контейнери працюють як UID/GID 1001, read-only root, без capabilities, з `no-new-privileges`, writable volume `/data/director` і tmpfs. На bind mount оператор має забезпечити права UID 1001; named volume успадковує права каталогу з образу. Ліміти: 768 MiB, 1 CPU, 128 PID. Volume містить чернетки та замовлення: потрібні backup, шифрування диска й контроль доступу оператора.

`GET /health` повертає 200 лише після читання auth із Vault. `POST /execute` потребує `X-API-Key` свого worker. Формат:

```json
{"payload":{"action":"capabilities"}}
```

API `/execute` основного EVA runtime приймає `task_type=oscar_task|tyler_task|jack_task` із таким самим внутрішнім payload. За замовчуванням ці маршрути не активовані.

## Перевірки й активація

1. `PATH=<ffmpeg-with-libx264>:$PATH bash tools/check.sh` — усі тести, lint, API/Vault, жива PostgreSQL-схема та compose.
2. Побудувати образ і перевірити локальні math/draft/persistence операції на синтетичних даних.
3. Перевірити Vault AppRole renewal, ізоляцію мереж і allowed actions у цільовому deployment.
4. Підключити Hermes tool gateway і центральний audit/KODEX; додати точні capabilities/grants у профілі.
5. Підключати реальні акаунти, фінансові та публікаційні операції тільки через існуючий HITL control plane після реалізації відповідних adapters і webhook verification.

Перевірений каталог CodeRabbit emulate v0.0.1 не містить xAI/Gemini/Anthropic LLM, YouTube Data API, The Odds API або HashiCorp Vault. Google emulator покриває OAuth/Gmail/Calendar/Drive; він не заміняє YouTube. HTTP-контракти цих adapters перевіряються через `httpx.MockTransport`; це не підтверджує live-права або роботу реальних провайдерів. Stripe є в каталозі, але платіжний adapter у цьому етапі не реалізовано й emulator не запускається.

## Результати перевірки цього етапу

- Docker image збирається з мінімальними worker-залежностями; ownership COPY перевірено для UID 1001.
- У контейнері без мережі, з read-only root і tmpfs пройшли API/auth/capabilities усіх трьох директорів, створення реального PNG і SQLite-запису. Production AppRole startup не перевірено з реальним Vault.
- Sandbox має threaded cgroup: smoke запускався з `--cgroupns host --cgroup-parent /` без CPU/memory контролерів. Ліміти production Compose збережено; їх застосування потребує перевірки на цільовому хості.
- Усі Vault ACL перевірено незалежним HCL parser: виправлено старий генератор, який подвоював лапки capability tokens.
