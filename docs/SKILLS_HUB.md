# Хаб скілів SYNDICATE

Джерело правди: `config/skill_library.json` (451 скіл, кожен закріплений комітом і SHA-256).
Скіл лише довідка (`reference_only`): він не дає агенту жодних прав і нічого не запускає.
Агент отримує скіл тільки через `reference_skills` у своєму профілі `config/agents/<агент>.profile.json`.

Імпорт 03.11.2026 (`tools/import_skills.py`) пройшов автоматичну перевірку на ін'єкції, приховані символи,
віддалений запуск і обхід захисту. Це не ручна перевірка: перед призначенням агенту скіл читається повністю.
96 імпортованих скілів посилаються на свої додаткові файли, а в хаб узято лише `SKILL.md`.

Відсіяні перевіркою (не в хабі): `github-ops`, `story-lifecycle`, `tdd-workflow` (ECC).

## Призначено агентам зараз

- **Тренер:** `evidence-based-fitness-coach`, `hypertrophy-training`, `rep-max`, `i-have-adhd` (усі чотири прочитано повністю, довідкові файли перевірено автоматично), `scientific-critical-thinking`.
- **Сем:** 43 трейдерські скіли (імпорт 06.11.2026, розділ «Трейдинг» нижче).
- **Кіра:** `thesis-validation`, `evidence-gap-check`, `scenario-analyzer`.
- **Тайлер:** `data-quality-checker`. **Єва:** `dual-axis-skill-reviewer`, `skill-integration-tester`. **Маршал:** `dual-axis-skill-reviewer`.
- **Усі семеро:** `obsidian-markdown`, `obsidian-bases`, `json-canvas` (формат Obsidian, 10.11.2026).
- Решта профілів без змін, перелік у `docs/PERMISSIONS_MATRIX.md`.

## Obsidian Skills від Kepano (6, імпорт 10.11.2026)

Джерело: `kepano/obsidian-skills@3ccff53`, MIT, автор — CEO Obsidian. Перевірка: усі 6 чисті.

| Скіл | Кому | Чому |
|---|---|---|
| `obsidian-markdown` (+3 довідки) | усім сімом | властивості, [[посилання]], callout, вбудовування: нотатки не ламаються й знаходяться |
| `obsidian-bases` (+1) | усім сімом | таблиці й картки з властивостей нотаток (`.base`) |
| `json-canvas` (+1) | усім сімом | полотна й майндмапи (`.canvas`) |
| `defuddle` | нікому | CLI на Node.js; кандидат для `web_fetch` пізніше |
| `knap` | нікому | шаблони Markdown, потрібен Node.js |
| `obsidian-cli` | нікому | потрібен запущений настільний Obsidian; уміє запускати JavaScript у плагінах |

## Трейдинг (46, імпорт 06.11.2026)

Розбір десяти репозиторіїв Андрія, що взято й чому: `knowledge_pools/notebooklm_second_brain/08_Хаб_Скілів_Промтів_та_MCP/04_Огляд_репозиторіїв_2026-11-06.md`.
Реєстр усіх посилань Андрія: `05_Реєстр_посилань_Андрія.md` у тій самій теці. Скрипти не скопійовано, лише `SKILL.md` і `references/*.md`. Скіли, що ставлять ордери (`trader-broker`, `etoro`), не взято.

- marian2js/trading-skills (16): `catalyst-map`, `watchlist-review`, `macro-event-analysis`, `market-regime-analysis`, `position-management`, `journal-pattern-analyzer`, `post-trade-review`, `evidence-gap-check`, `thesis-validation`, `execution-plan-check`, `portfolio-concentration`, `position-sizing`, `risk-reward-sanity-check`, `portfolio-risk-review`, `post-trade-debrief`, `pre-trade-check`
- tradermonty/claude-trading-skills (22): `backtest-expert`, `crypto-regime-analyzer`, `cot-contrarian-detector`, `news-reaction-failure-analyzer`, `contrarian-setup-gate`, `macro-regime-detector`, `drawdown-circuit-breaker`, `pre-trade-discipline-gate`, `trader-memory-core`, `signal-postmortem`, `weekly-performance-digest`, `trade-performance-coach`, `futures-position-sizer`, `strategy-pivot-designer`, `scenario-analyzer`, `technical-analyst`, `market-news-analyst`, `mt5-robot-tester`, `us-market-bubble-detector`, `data-quality-checker`, `dual-axis-skill-reviewer`, `skill-integration-tester`
- Jakeschincariol/day-trader-skill (4): `trader-timemachine`, `trader-risk`, `trader-budget`, `trader-exit`
- Shubhamkumartrichy/claude-trading-skills-india (4): `fibonacci-trading`, `multi-timeframe-analysis`, `rsi-divergence`, `trailing-stops`

## Власні скіли холдингу (local)

- `tyler-price-compare` — порівняння цін
- `tyler-supplier-research` — пошук постачальників
- `tyler-listing-draft` — чернетка оголошення
- `kodex-prompt-catalog` — каталог промптів
- `kodex-skill-research` — пошук нових скілів
- `kodex-notebooklm` — робота з NotebookLM
- `kodex-obsidian` — робота з Obsidian
- `kodex-mcp-connector-scout` — пошук MCP-конекторів
- `marshal-skill-scout` — безпекова перевірка скілів
- `marshal-mcp-connector-review` — безпекова перевірка MCP

## Окремі джерела

- `grill-me`, `grilling` — допит ідеї питаннями (mattpocock)
- `handoff` — передача роботи іншому агенту (mattpocock)
- `api-and-interface-design` — проєктування API (addyosmani)
- `debugging-and-error-recovery` — пошук і виправлення помилок (addyosmani)
- `context-engineering` — економне наповнення контексту (addyosmani)
- `documentation-and-adrs` — документація й рішення (addyosmani)
- `source-driven-development` — робота від першоджерел (addyosmani)
- `test-driven-development` — спершу тест (addyosmani)
- `planning-breakdown` — розбиття задачі на кроки (addyosmani)
- `internal-comms` — внутрішні повідомлення (Anthropic)
- `frontend-design` — дизайн інтерфейсів (Anthropic)
- `scientific-critical-thinking` — перевірка наукових тверджень (K-Dense)
- `behavioral-finance` — поведінкові фінанси (Vibe-Trading)
- `tyler-store-legitimacy-review` — чи справжній інтернет-магазин (HinkoK)
- `replica-recon`, `replica-test` — розбір і перевірка копії продукту (replica-skill)
- `i-have-adhd` — відповідь з першої дії, без води

## Ponytail (менше коду)

- `ponytail` — писати мінімум коду
- `ponytail-audit` — аудит зайвого коду
- `ponytail-debt` — технічний борг
- `ponytail-gain` — що дасть спрощення
- `ponytail-help` — довідка Ponytail
- `ponytail-review` — рев'ю на зайву складність

## OpenDirectory (маркетинг і зростання)

- `app-store-review-arbitrage` — ідеї з відгуків App Store
- `blog-cover-image-cli` — обкладинки для блогу
- `brand-alchemy` — побудова бренду
- `claude-md-generator` — CLAUDE.md для репозиторію
- `cold-email-verifier` — перевірка холодних листів
- `company-radar` — моніторинг компаній
- `competitor-pr-finder` — PR конкурентів
- `cook-the-blog` — статті для блогу
- `dependency-update-bot` — оновлення залежностей
- `docs-from-code` — документація з коду
- `domain-expired-opportunity-finder` — прострочені домени
- `dx-roaster` — критика досвіду розробника
- `email-newsletter` — розсилка
- `explain-this-pr` — пояснення PR
- `geo-gap-fixer` — видимість у відповідях ШІ
- `gh-issue-to-demand-signal` — попит з GitHub issues
- `github-discussion-to-devrel-content` — контент з обговорень
- `graphic-case-study`, `graphic-chart`, `graphic-ebook`, `graphic-gif`, `graphic-slide-deck` — графіка: кейс, графік, e-book, GIF, слайди
- `hackernews-intel` — розвідка з Hacker News
- `human-tone` — живий тон тексту (ШІ-текст розкривати при публікації)
- `hyperframes-product-launch-video` — відео запуску продукту
- `kill-the-standup` — заміна щоденних мітингів
- `linkedin-job-post-to-buyer-pain-map` — болі клієнта з вакансій
- `linkedin-post-generator` — пости LinkedIn
- `llms-txt-generator` — файл llms.txt
- `map-your-market` — карта ринку
- `meeting-brief-generator` — бриф до зустрічі
- `meta-tribeV2-skill` — реклама Meta
- `newsletter-digest` — дайджест розсилок
- `noise-to-linkedin-carousel` — каруселі LinkedIn
- `noise2blog` — нотатки в статтю
- `npm-downloads-to-leads` — ліди з завантажень npm
- `openverse-sfx` — вільні звукові ефекти
- `oss-launch-kit` — запуск open source
- `outreach-sequence-builder` — серії листів
- `podcast-transcript-fetcher` — транскрипти подкастів
- `pr-description-writer` — опис PR
- `pricing-finder` — ціни конкурентів
- `pricing-page-psychology-audit` — аудит сторінки цін
- `product-update-logger` — журнал оновлень
- `producthunt-launch-kit` — запуск на Product Hunt
- `reddit-icp-monitor` — клієнти на Reddit
- `reddit-post-engine` — пости Reddit
- `schema-markup-generator` — розмітка Schema.org
- `sdk-adoption-tracker` — використання SDK
- `show-hn-writer` — пост Show HN
- `store-listing-optimizer` — сторінка в магазині застосунків
- `tweet-thread-from-blog` — треди з статей
- `vc-curated-match`, `vc-finder` — пошук інвесторів
- `vid-motion-graphics`, `vid-product-launch`, `vid-sizzle-reel` — відео: анімація, запуск, нарізка
- `where-your-customer-lives` — де шукати клієнтів
- `xquik-x-follower-scraper`, `xquik-x-tweet-scraper` — збір даних X через платний API Xquik

## ECC (311 скілів)

### Агенти й автоматизація
- `agent-architecture-audit` — аудит архітектури агента
- `agent-eval`, `eval-harness`, `gan-style-harness` — оцінка агентів
- `agent-harness-construction`, `autonomous-agent-harness` — побудова середовища агента
- `agent-introspection-debugging` — налагодження агента
- `agent-payment-x402` — платежі агентів x402
- `agent-runtime-gateway-smoke-test` — перевірка шлюзу агента
- `agent-security-hardening` — захист агента
- `agent-self-evaluation` — самооцінка відповіді
- `agent-sort` — сортування задач агентам
- `agentic-engineering`, `agentic-os`, `ai-first-engineering` — розробка з агентами
- `autonomous-loops`, `continuous-agent-loop`, `loop-design-check` — автономні цикли
- `claude-devfleet`, `dev-team`, `team-agent-orchestration`, `team-builder` — команди агентів
- `council`, `council-multi-model` — рада кількох моделей
- `deepseek-harness-setup` — налаштування DeepSeek
- `dmux-workflows`, `parallel-execution-optimizer` — паралельна робота
- `dynamic-workflow-mode` — гнучкий режим роботи
- `enterprise-agent-ops` — агенти в компанії
- `hermes-imports` — імпорт у Hermes
- `nanoclaw-repl`, `nasiko-control-plane`, `openclaw-persona-forge` — інструменти конкретних платформ
- `operator-approval-loop` — підтвердження оператором
- `orch-add-feature`, `orch-build-mvp`, `orch-change-feature`, `orch-fix-defect`, `orch-pipeline`, `orch-refine-code` — оркестрація розробки
- `plan-canvas`, `plan-orchestrate` — планування
- `ralphinho-rfc-pipeline` — конвеєр RFC
- `santa-method` — подвійна перевірка результату
- `skill-comply`, `skill-host-compat`, `skill-scout`, `skill-stocktake` — керування скілами
- `rules-distill` — витяг правил

### Економія токенів, пам'ять, пошук
- `context-budget` — бюджет контексту
- `cost-aware-llm-pipeline` — дешевий конвеєр LLM
- `cost-tracking`, `ecc-tools-cost-audit`, `token-card` — облік витрат
- `prompt-caching-strategy` — кешування промптів
- `prompt-optimizer` — стиснення промптів
- `strategic-compact` — стискання розмови вчасно
- `token-budget-advisor` — вибір глибини відповіді
- `iterative-retrieval` — пошук малими кроками
- `search-first` — спершу пошук готового
- `knowledge-ops`, `unified-memory` — знання й пам'ять
- `ck` — пам'ять проєкту між сесіями
- `continuous-learning`, `continuous-learning-v2` — навчання агента
- `context-and-decisions`, `recursive-decision-ledger` — журнал рішень
- `regex-vs-llm-structured-text` — регулярки замість LLM
- `content-hash-cache-pattern` — кеш за хешем
- `documentation-lookup`, `exa-search`, `deep-research`, `research-ops` — пошук і дослідження

### Якість, тести, безпека
- `ai-regression-testing`, `module-regression` — регресійні тести
- `benchmark`, `benchmark-methodology`, `benchmark-optimization-loop` — бенчмарки
- `browser-qa`, `click-path-audit`, `e2e-testing`, `windows-desktop-e2e`, `ui-demo` — перевірка інтерфейсу
- `canary-watch`, `delivery-gate`, `gateguard`, `verification-loop` — ворота перед здачею
- `change-impact` — вплив зміни
- `codehealth-mcp`, `plankton-code-quality`, `coding-standards` — якість коду
- `conventional-commit-review`, `issue-review` — рев'ю комітів і задач
- `error-handling` — обробка помилок
- `mcp-dependency-review` — перевірка MCP-залежностей
- `production-audit` — аудит продакшену
- `safety-guard` — запобіжники
- `security-bounty-hunter`, `security-review`, `security-scan` — безпека коду
- `test-collaboration` — тести разом
- `llm-trading-agent-security` — безпека торгового агента
- `defi-amm-security`, `evm-token-decimals`, `nodejs-keccak256` — блокчейн-безпека

### Архітектура й процес розробки
- `api-connector-builder`, `api-design`, `contract-first` — API
- `architecture-decision-records`, `blueprint`, `hexagonal-architecture` — архітектура
- `backend-patterns`, `data-throughput-accelerator`, `latency-critical-systems` — бекенд
- `brownfield-retrospective`, `inherit-legacy-style` — старий код
- `code-tour`, `codebase-onboarding`, `repo-scan` — знайомство з кодом
- `config-gc`, `configure-ecc`, `ecc-guide`, `ecc-recipes` — налаштування ECC
- `database-migrations` — міграції БД
- `deployment-patterns`, `docker-patterns`, `kubernetes-patterns`, `uncloud` — розгортання
- `docs-governance`, `living-docs-governance` — керування документацією
- `flox-environments`, `bun-runtime` — середовища
- `generating-python-installer` — інсталятор Python
- `git-workflow` — робота з git
- `hookify-rules` — хуки
- `i18n-sync` — переклади
- `intent-driven-development`, `product-capability` — розробка від мети
- `mcp-server-patterns` — MCP-сервери
- `module-governance` — межі модулів
- `opensource-pipeline` — випуск open source
- `project-flow-ops`, `jira-integration` — ведення проєкту
- `terminal-opener`, `terminal-ops` — термінал
- `tinystruct-patterns` — фреймворк tinystruct
- `workspace-surface-audit` — аудит робочого середовища

### Мови й фреймворки
- `android-clean-architecture`, `compose-multiplatform-patterns` — Android
- `angular-developer` — Angular
- `cpp-coding-standards`, `cpp-testing` — C++
- `csharp-testing`, `dotnet-patterns`, `fsharp-testing` — .NET
- `dart-flutter-patterns`, `flutter-dart-code-review` — Flutter
- `django-celery`, `django-patterns`, `django-security`, `django-tdd`, `django-verification` — Django
- `fastapi-patterns`, `python-patterns`, `python-testing`, `pytorch-patterns` — Python
- `frontend-a11y`, `accessibility` — доступність
- `frontend-design-direction`, `frontend-patterns`, `frontend-slides`, `design-system`, `liquid-glass-design`, `make-interfaces-feel-better`, `taste`, `taste-application`, `taste-distillation` — фронтенд і дизайн
- `golang-patterns`, `golang-testing` — Go
- `java-coding-standards`, `jpa-patterns`, `mybatis-patterns`, `springboot-patterns`, `springboot-security`, `springboot-tdd`, `springboot-verification`, `quarkus-patterns`, `quarkus-security`, `quarkus-tdd`, `quarkus-verification` — Java
- `kotlin-coroutines-flows`, `kotlin-exposed-patterns`, `kotlin-ktor-patterns`, `kotlin-patterns`, `kotlin-testing` — Kotlin
- `laravel-patterns`, `laravel-plugin-discovery`, `laravel-security`, `laravel-tdd`, `laravel-verification` — Laravel
- `nestjs-patterns`, `nextjs-turbopack`, `nuxt4-patterns`, `react-native-patterns`, `react-patterns`, `react-performance`, `react-testing`, `typescript-patterns`, `vite-patterns`, `vue-patterns`, `ui-to-vue` — JS/TS
- `perl-patterns`, `perl-security`, `perl-testing` — Perl
- `postgres-patterns`, `mysql-patterns`, `redis-patterns`, `clickhouse-io`, `prisma-patterns` — бази даних
- `rails-patterns` — Rails
- `rust-patterns`, `rust-testing` — Rust
- `swift-actor-persistence`, `swift-concurrency-6-2`, `swift-protocol-di-testing`, `swiftui-patterns`, `foundation-models-on-device`, `ios-icon-gen` — Apple
- `bengali-nlp` — бенгальська мова

### Мережі й домашній сервер
- `cisco-ios-patterns`, `netmiko-ssh-automation`, `network-bgp-diagnostics`, `network-config-validation`, `network-interface-health` — мережі
- `homelab-network-readiness`, `homelab-network-setup`, `homelab-pihole-dns`, `homelab-vlan-segmentation`, `homelab-wireguard-vpn` — домашня мережа

### Бізнес, продажі, контент
- `article-writing`, `content-engine`, `brand-voice`, `brand-discovery` — тексти й бренд
- `competitive-platform-analysis`, `competitive-report-structure`, `market-research`, `product-lens` — аналіз ринку
- `connections-optimizer`, `lead-intelligence`, `social-graph-ranker` — ліди й контакти
- `crosspost`, `social-publisher`, `x-api`, `seo`, `marketing-campaign`, `growth-log` — публікації й маркетинг
- `customer-billing-ops`, `finance-billing-ops` — рахунки
- `email-ops`, `mailtrap-email-integration`, `messages-ops`, `unified-notifications-ops` — пошта й повідомлення
- `google-workspace-ops` — Google Workspace
- `investor-materials`, `investor-outreach` — інвестори
- `master-agreement-generator`, `esign-field-placement`, `counterparty-channel-discipline` — договори
- `automation-audit-ops`, `dashboard-builder` — автоматизація й дашборди
- `data-scraper-agent` — збір даних з сайтів
- `osint-investigation` — розвідка з відкритих джерел
- `prediction-market-oracle-research`, `prediction-market-risk-review` — ринки прогнозів
- `visa-doc-translate` — переклад документів на візу
- `nutrient-document-processing` — обробка документів (Nutrient API)

### Логістика й виробництво
- `carrier-relationship-management`, `logistics-exception-management`, `returns-reverse-logistics` — логістика
- `customs-trade-compliance` — митниця
- `energy-procurement` — закупівля енергії
- `inventory-demand-planning`, `production-scheduling`, `quality-nonconformance` — склад і виробництво

### Медицина (розробка ПЗ, не лікування)
- `healthcare-cdss-patterns`, `healthcare-emr-patterns`, `healthcare-eval-harness`, `healthcare-phi-compliance`, `hipaa-compliance` — медичні системи й захист даних

### Відео, медіа, ML
- `blender-motion-state-inspection`, `manim-video`, `motion-advanced`, `motion-foundations`, `motion-patterns`, `remotion-video-creation`, `tasteforge-video`, `video-editing`, `videodb`, `fal-ai-media` — відео й анімація
- `ito-baskets`, `ito-compute`, `ito-inference`, `ito-training`, `ml-adoption-playbook`, `mle-workflow`, `recsys-pipeline-architect` — машинне навчання
- `scientific-db-pubmed-database`, `scientific-db-uspto-database`, `scientific-pkg-gget`, `scientific-thinking-literature-review`, `scientific-thinking-scholar-evaluation` — наукові бази й огляд літератури

## Тренування й харчування (46, імпорт 03.11.2026)

- `evidence-based-fitness-coach` — програма й харчування з доказовою базою, межі «не лікар» (Lancetnik) — **Тренер**
- `hypertrophy-training` — наука росту м'язів, 19 довідок з джерелами PubMed (disco-trooper) — **Тренер**
- `rep-max` — 1ПМ і робочі ваги за таблицею ACSM (Jeffallan) — **Тренер**
- `body-composition` — відсоток жиру за каліпером (Jeffallan)
- `meal-planner` — макроси за типом статури, слабка наукова основа (Jeffallan)
- `cycling-training` — велотренування, FTP, зони (disco-trooper)
- `intervals-icu` — дані з Intervals.icu (disco-trooper)
- `process-automation-audit` — аудит автоматизації процесів (disco-trooper)
- `trainer` — особистий коуч з цитованою базою (Yuvasee)
- `nutrition-coach` — щоденник їжі й макроси (NataMoroz)
- `fitness-coach` — тренування під профіль і журнал (neilberget)
- `hypertrophy-programme-designer` — програма на масу з історії тренувань (flaviusapop)
- `fitness-diet-planner` — тиждень тренувань і меню (Kyo-zmol)
- `adaptive-endurance-coach` — біг, плавання, вело, тріатлон (mprecilio20)
- `weekly-meal-planner` — меню на тиждень і список покупок (marklavine)
- `fitness-review-board` — рада експертів для перевірки плану (Rowan)
- `fitcoach-pro` — методика персонального тренера (FitCoach Pro)
- `edamam-barcode-lookup` — харчова цінність за штрихкодом, потрібен Edamam MCP
- `lzheng-fitness-plan`, `lzheng-strength-cycle-planner`, `lzheng-strength-training-review`, `lzheng-training-system`, `lzheng-training-return`, `lzheng-training-expert-library` — силові плани, цикли, розбір тренувань, повернення після перерви (китайською)
- `lzheng-nutrition-system` — харчування під тренування (китайською)
- `lzheng-fitness-workbench-builder`, `lzheng-knowledge-library`, `lzheng-video-learning`, `lzheng-video-lessons`, `douyin-question-distiller` — робочий простір, бібліотека знань, навчання з відео (китайською)
- `food-research`, `food-deep-research`, `food-review`, `food-paper`, `food-proposal`, `food-fetch`, `food-figure`, `food-ppt`, `food-pipeline` — наукова робота з харчування: пошук, огляд, статті (Pangenome)
- `agri-research`, `agri-deep-research`, `agri-review`, `agri-paper`, `agri-ppt`, `agri-pipeline` — те саме для агронауки (Pangenome)
- `journal-selector` — вибір журналу для статті (Pangenome)

## Кандидати, які не є скілами (не встановлено)

- **Graphify** (Graphify-Labs/graphify, Apache-2.0) — граф знань з коду й документів, щоб агент швидко знаходив потрібне. Це програма, а не текст: потребує встановлення на сервері, погодження Андрія й перевірки Маршалом.
- **headroom** (chopratejas/headroom) — стискання контексту перед моделлю. Теж програма: кандидат для шлюзу Hermes.
- **MOSS-TTS** (OpenMOSS, Apache-2.0) — синтез мовлення з клонуванням голосу. Модель, кандидат для голосового плану.
