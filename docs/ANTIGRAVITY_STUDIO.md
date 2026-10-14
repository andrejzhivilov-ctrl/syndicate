# Antigravity — Venture & Media Factory

Стан на 2026-10-14: **каркас підготовлено, не активовано**. Це агент SYNDICATE,
не інтеграція з підпискою Google Antigravity IDE. Старий `ANTIGRAVITY_BRIEF.md`
описує співпрацю із зовнішнім coding-інструментом, а не цей runtime.

## Що реально є

- `config/agents/antigravity.profile.json`: default-deny, порожні grants, proposed_grants
  лише для обговорення, жодного доступу до GitHub/інтернету/платежів/історії.
- `src/agents/antigravity.py`: внутрішній offline-контракт `execute`, `status` і сім
  запланованих операцій. Всі операції повертають denied, невідомі — rejected.
- Чернетка prompt і тести. Немає Telegram handlers, FastAPI server, порту 8007,
  фонового завдання, live Hermes adapter або реєстрації в orchestrator.

## Етапи після рішень Андрія

| Напрям / майбутня команда | Наступна реалізація | Обов'язковий gate |
|---|---|---|
| `/app` | Генератор проєкту + isolated build/test/preview | Repo/domain scopes; sandbox без Docker socket та production-секретів; deployment окремо через HITL |
| `/img` | Image-provider adapter + приватні артефакти | Актуальні API, ліцензія, ціна, бюджет і явний дозвіл |
| `/video` | Зв'язок з Floor 2, FFmpeg/Remotion, дозволені візуальні матеріали й TTS | Обмеження CPU/RAM/часу, права на медіа, погоджені провайдери; 16 vCPU не підтверджено |
| `/research` | Пошук/браузер із джерелами, датами, PDF/таблицями | Domain allowlist, egress policy, ліміти, SSRF-захист (localhost/metadata/private IP), захист від prompt injection |
| GitHub | GitHub App/обмежена авторизація, branches/PR | Repo allowlist, least privilege, без admin/force push/auto-merge; секрети лише через існуючі Vault paths |
| `/billing_status` | Read-only статистика обраного провайдера | Реальні метрики або unavailable, не вигаданий дохід |
| `/history` | Приватний ACL-aware пошук з цитатами | Наданий/перевірений архів, очищення PII, дозволений embedding-provider, немає глобального доступу до медичних даних |

Billing продуктів — окремий етап: вибір Stripe/Monobank/WayForPay, доступність
для юридичного статусу Андрія, тестовий режим, підпис і захист webhook від replay,
ідемпотентна обробка event ID, перевірені entitlements, скасування/повернення,
ротація й хешування API keys. Живі списання та зміна цін тільки через HITL.
Підписка на IDE/chat зазвичай не означає API-квоту: потрібно перевірити умови
конкретного сервісу. Жодну модель чи тариф із запропонованої архітектури не
позначено як актуальний/обраний без перевірки.

## Історія: безпечні вимоги, не виконаний імпорт

`EVA_SYNDICATE_FULL_DIALOGUE.txt` є серед tracked files поточного checkout.
Його не читали і не індексували в цій задачі. Не дублювати його в Git чи логи;
попереднє рішення лишити файл у репозиторії не є дозволом передавати його
зовнішнім embedding API. Перенесення/видалення tracked архіву — окреме рішення Андрія.

Використовувати приватну копію у `EVA_DATA_DIR`, не `/data/repo` і не credentials
у default DATABASE_URL. Перед ingest: інвентаризація, маскування секретів/PII,
ACL та категорії даних, рішення щодо зовнішнього або локального embedding.
RAG не тримає весь діалог у контексті й не гарантує згадування кожного слова.

Вимоги до майбутнього importer: schema/extension migrations та роль з мінімальними
правами; розмір vector відповідно до обраної моделі; token-aware chunking;
source hash + chunk ID + дата + версія embedding для ідемпотентності; batch/retry;
параметризований SQL, закриття connection у finally; ACL до retrieval; цитати
джерела; політика retention/видалення лише з актуальним дозволом.
Приклад скрипта з повідомлення користувача **не запускався**: він не забезпечує
ці властивості й надсилає весь текст зовнішньому провайдеру.

## Дані та deployment

Майбутній workspace: підкаталог `EVA_DATA_DIR/antigravity-studio/` з `apps/`,
`media/`, `reports/`; не репозиторний `apps/`. Контейнерні mount/resources/port
лише після погодження варіанта контейнеризації. Не монтувати GitHub SSH-ключ
із широкими правами або весь Vault у build sandbox.

Перед сервером: `DEPLOYMENT_RUNBOOK.md`, `docs/DEPLOY_SYNDICATE.md` та
`docs/DEPLOY_CHECKLIST.md`. Останній у цьому checkout **відсутній**: він є частиною
недоступного локального коміта `5e96a86`. Не вважати розгортання готовим.

## Потрібні рішення

1. Підписка — оплата інструмента, SaaS-білінг продуктів чи обидва?
2. Перший напрям, provider/model + бюджет; фактичні API і ціни перевірити перед вибором.
3. Конкретні grants/resource scopes, repo/domain allowlists і ліміти; запропоновані
   можливості не вмикаються автоматично.
4. Приватна історія: доступні джерела, категорії/ACL та локальні чи зовнішні embeddings.
5. Контейнери, сервер/TLS, автентифікований Telegram allowlist (порожній = deny).
