# Бібліотека скілів SYNDICATE — 2026-10-15

GitHub доступ відновлено й перевірено для `andrejzhivilov-ctrl`. Переглянуто 12 профілів і 26 наданих репозиторіїв (усі активні на час перевірки). Це перевірка призначення, ліцензій, залежностей та вибраних інструкцій, не аудит кожного рядка всіх репозиторіїв.

## Що встановлено

21 скіл з 8 оригінальних джерел у `skills/vendor/`, із супровідними файлами та ліцензіями. Повні commit SHA і SHA256 усіх файлів — `config/skill_library.json`. `reference_skills` у кожному з 12 профілів визначає доступні матеріали. Власні draft skills збережено.

Це встановлена **бібліотека інструкцій**, а не активовані зовнішні сервіси. `SkillLibrary` читає лише явно призначений ресурс, перевіряє SHA256, обмежує розмір, відхиляє symlinks і вихід за межі каталогу. Читання не запускає код і не надає permissions. Ідентичність агента має визначати довірений runtime; CLI не є HTTP authorization boundary.

```bash
.venv/bin/python tools/skill_library.py --verify
.venv/bin/python tools/skill_library.py --agent oscar
.venv/bin/python tools/skill_library.py --agent oscar --skill content-engine
.venv/bin/python tools/skill_library.py --agent oscar --skill brand-voice --resource references/voice-profile-schema.md
```

Runtime може викликати `SkillLibrary().read(authenticated_agent_id, skill_id, resource)` та завантажувати лише потрібний матеріал як reference context. Автоматичне підмішування всіх скілів у кожен prompt погіршує контекст. Наявні Hermes профілі ще prepared_not_enabled; цей етап не додає Hermes Skill tool і не змінює образи workers. Для контейнерної інтеграції потрібен read-only mount `skills/`, каталогу і профілів, та перевірка gateway. Пара `grill-me`/`grilling` доступна як матеріал; Claude Skill-tool alias автоматично не емулюється.

Пріоритет мають запит оператора, `AGENTS.md`, policy gateway, Vault і PII. Сторонні `allowed-tools`, інструкції делегування, install/update команди та persistent session modes не є grants. Зовнішні source calls, browser, financial actions і publishing потребують чинного дозволу відповідного інструмента. Шаблони й приклади не є виміряними даними. `scientific-critical-thinking` можна читати offline; optional scientific-schematics не встановлено. `behavioral-finance` — guidance, його Python-приклади не є перевіреною торговою моделлю.

## Розподіл між агентами

**Актуалізація 2026-10-16:** попередню технічну мітку `antigravity` замінено на агентку `alice`; переліки звірені з профілями. Antigravity — технологія, а не ім’я агентки. KODEX залишається власником prompt/skill engineering і каталогу. Усі записи нижче — reference-only, не активація runtime.

| Агент | Додані матеріали |
|---|---|
| alice | api-and-interface-design, debugging-and-error-recovery, context-engineering, documentation-and-adrs, source-driven-development, test-driven-development, planning-breakdown, agent-security-hardening |
| architect | grill-me, handoff, grilling, api-and-interface-design, debugging-and-error-recovery, context-engineering, documentation-and-adrs, source-driven-development, test-driven-development, planning-breakdown, ponytail, replica-recon, agent-security-hardening |
| doc | scientific-critical-thinking |
| eva | grill-me, handoff, grilling, context-engineering, planning-breakdown, internal-comms, market-research |
| fin | internal-comms, scientific-critical-thinking, behavioral-finance, market-research |
| jack | scientific-critical-thinking, behavioral-finance |
| kira | scientific-critical-thinking |
| kodex | handoff, context-engineering, documentation-and-adrs, internal-comms |
| marshal | replica-test, agent-security-hardening |
| oscar | internal-comms, frontend-design, content-engine, market-research, brand-voice |
| sam | scientific-critical-thinking, behavioral-finance, market-research |
| tyler | frontend-design, replica-recon, content-engine, market-research, brand-voice |

## Рішення щодо всіх джерел

| Джерело | Стан | Причина / наступний крок |
|---|---|---|
| [Lum1104/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything/tree/f2d0164f72fe678805c34245a6df36acededfebd) | integration_candidate | GitHub перенаправляє на Egonex-AI. Плагін має граф, dashboard та власні залежності; потрібен окремий запуск і адаптер, копія SKILL.md не створить карту коду. |
| [nexu-io/open-design](https://github.com/nexu-io/open-design/tree/7abd6fc2b11987c3940eb4ffc461478ff37c0b33) | integration_candidate | Окремий collaborative workspace/daemon; не замінюємо наявний apps/. Потрібні preview/export smoke tests та окрема конфігурація. |
| [mattpocock/skills](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336) | installed_reference | Встановлено grill-me разом із залежністю grilling та handoff. Інтерв’ю лише коли потрібне користувачу; інструкції делегування не є дозволом запускати агентів. |
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman/tree/d262ab3882952a59312ff3537cd86d894523c5ab) | not_selected | Стиль може втрачати пояснення та змінювати поведінку всієї сесії. CLI також змінює налаштування/проксі. Стислість забезпечується без глобального переписування інструкцій. |
| [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers/tree/5b5d8dfca263fa76e6daae9f292890b311ef36aa) | integration_candidate | SKILL.md очікує MCP із 40 інструментами; він тут не налаштований. Генерацію знань слід запускати окремо з перевіркою джерел, ліцензій та PII. |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes/tree/cea8aa8a7dee9d669e47e4b488213008bbe305cd) | integration_candidate | Переглянуто hyperframes-core та pr-to-video: залежності на sibling skills, CLI/render та frame workers. Потрібен цілісний окремий відеоконвеєр; два файли не дадуть робочий рендер. |
| [leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill/tree/f624f37a8c650b9cc550253104925efe4c8de246) | integration_candidate | Поточний v2 містить Node scripts, завантаження зображень і browser inspector. Потребує окремої перевірки JS та браузерного середовища; базовий дизайн покрито frontend-design. |
| [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser/tree/dac13bb87468fe9d74a040d862720f6cc17a9565) | integration_candidate | SKILL.md тепер є bootstrap для CLI skills get core. Для цієї пісочниці використовується coderabbit-agent-browser; production browser isolation і tool gateway ще не підключені. |
| [mksglu/context-mode](https://github.com/mksglu/context-mode/tree/40813fe886798bad07c69a43d2ae00a52b4b934d) | integration_candidate | MCP та hooks із Node >=22.5; LICENSE — Elastic License 2.0, не MIT. Потрібна окрема інтеграція, збереження помилок і аудит routing hooks. |
| [ddavv1d/compact-guard-plugin](https://github.com/ddavv1d/compact-guard-plugin/tree/7dcda79f97957e9c8ad2ab02e25a14d5be4c8cbb) | integration_candidate | Claude Code hooks, Node >=20; не універсальний Hermes skill. Наявний validation record зберігає помилки; production hooks ще не інтегровані. |
| [malishomen/bdc-bridge-passport](https://github.com/malishomen/bdc-bridge-passport/tree/fdf684b54688c6c937984183b010e85ef49d0757) | integration_candidate | Starter kit для зовнішнього BDC verdict API, не набір скілів. Потрібні account/token та окреме рішення щодо надсилання workflow evidence. |
| [actualbudget/actual](https://github.com/actualbudget/actual/tree/d5d6035a8f5867717a80635d270fbe64e370ea08) | integration_candidate | Повноцінний бюджетний застосунок, Node і сховище/sync. Його .claude skills призначені для розробки Actual. Наступна інтеграція: read-only імпорт транзакцій із reconciliation; баланс не вигадувати. |
| [oriveo/oriveo](https://github.com/oriveo/oriveo/tree/284505910591ccaa2cbf81d352138db9afb9cb4a) | not_selected | Окремий BYOK клієнт, AGPL-3.0. Не дублюємо наявний клієнт та не переносимо код без плану ліцензій і синхронізації. |
| [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight/tree/9a499b1759084a86598eff8af30ed59f7354e76c) | integration_candidate | Сервіс retain/recall/reflect; потрібні isolated banks, PII redaction, retention та перевірка provider costs. Наявну пам’ять автоматично не мігрували. |
| [Oldcircle/geo-sleuth](https://github.com/Oldcircle/geo-sleuth/tree/836d70eea196b194391017e6e018e04ccc85aaa4) | integration_candidate | Скіл містить OCR, reverse image search, OSM, CLIP/DINO та мережеві скрипти. Потрібні окремі залежності й дозволи на передавання фото; геолокація в профілі лишається вимкненою. |
| [Jakeschincariol/replica-skill](https://github.com/Jakeschincariol/replica-skill/tree/77c9436fb3d18c3d58169efb8caf4fe906b0dc51) | installed_reference | Встановлено replica-recon та replica-test з шаблонами. Лише дослідження функцій і перевірка власного застосунку; браузерні тести не запускались цим встановленням. |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail/tree/84740e3d344b69b4a133201fa519eb37a62a2b2a) | installed_reference | Встановлено основну інструкцію мінімальних повних змін, без CLI та session hooks. |
| [diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute/tree/c4d1f3edabdcc7e3e51c2c90e1d36859bbc560a1) | integration_candidate | Gateway потребує окремого сервісу, provider accounts, allowlist та перевірки fallback/PII. Безкоштовний код не означає безкоштовні моделі або гарантовані квоти. |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills/tree/aeac41d4d005999432bb7312f7ff06383a91d59d) | installed_reference | Сім engineering skills із shared references; API, debugging, контекст, ADR, джерела, TDD, планування. |
| [anthropics/skills](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44) | installed_reference | internal-comms та frontend-design мають локальні Apache-2.0 LICENSE. Office document skills мають інші source-available умови; їх не вендорили. |
| [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps/tree/4bf51ab704fb2c5b3803cd5191b30d7dcdb51dc2) | reference_catalog | Каталог прикладів і окремих skills. Не переносимо демонстраційні оркестратори, їхні провайдери та гаманці в production; інженерні функції вже покриті вибраними skills. |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills/tree/a1043ef544e3a100c28e70a736b6cf32554d0677) | installed_reference | Встановлено scientific-critical-thinking та всі його references. Statistical-analysis потребує Python >=3.12 й ізольованого наукового оточення; clinical claims не стають діагнозами. |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills/tree/3cd17ca9f40796a5dc564ebc6d76b4aa1303ff07) | reference_catalog | Індекс посилань, не первинний автор усіх скілів. Встановлюємо з оригінальних джерел, не весь каталог. |
| [HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading/tree/29aa084fb7866087c612ddd55ef5449824374e22) | installed_reference | Встановлено behavioral-finance як методичний матеріал. Backtest-diagnose прив’язаний до чужого SignalEngine/artifacts; live trading не підключено, твердження про прибутковість не перевірені. |
| [affaan-m/ECC](https://github.com/affaan-m/ECC/tree/b92f181b3b748d1abbc2afd94af6aa7d8c8fca29) | installed_reference | content-engine, залежність brand-voice, market-research та agent-security-hardening. Hooks, автопублікація та автонавчання політик не встановлювались. |
| [morluto/rea](https://github.com/morluto/rea/tree/08a897b2cd7b359fcb0674c82baec3f1a74af632) | integration_candidate | MCP для reverse engineering з Node і native engines. Потрібен конкретний дозволений об’єкт аналізу та окреме середовище; для поточної системи не обов’язковий. |

## Оновлення і розгортання

Оновлення — окремий перегляд нового commit, ліцензій, інструкцій та залежностей; після нього заміна файлів і hashes, regression tests та `tools/check.sh`. Не оновлювати з рухомого `main` під час роботи агента. SHA256 виявляє зміну файла відносно довіреного каталогу, але не захищає від одночасної підміни каталогу і файла: обидва мають постачатись із довіреного read-only deployment artifact.

Перші практичні інтеграції після бібліотеки: Fin → Actual read-only transactions; KODEX → Hindsight із розділенням banks та PII; Oscar → HyperFrames renderer; browser → окремий sandbox/tool gateway. Для кожної потрібні власні contract/smoke tests, секрети Vault за потреби та перевірка production readiness. Це заплановані інтеграції, не вже запущені сервіси.

## Сканування SkillSpector

SkillSpector 2.12.0, commit `240421219409dc0bafef9f618a10d80c2d7e83a3`, ізольований Python 3.12.15, `--no-llm`. Початкова обгортка Маршала не читала `risk_assessment.score`/`issues`; виправлено парсер, unknown/failed report тепер scan_unavailable. Вилучено `security-and-hardening`: score 100, YARA match та неповний static analysis references. Це не доказ шкідливості; матеріал не включено до схваленого набору. Скіл `agent-security-hardening` з ECC пройшов скан із score 7; description trigger попередження розглянуто.

Фінальні 21 скан завершилися з exit 0: 21 знахідка, 11 complete / 10 incomplete reports. Це переважно збіги в прикладах, заборонах і обмеження parser; оцінки та рішення збережено в `config/skill_scan_report.json`. Неповне покриття не приховується й не вважається сертифікацією. Повний `tools/check.sh` пройшов, включно з живим PostgreSQL; CI-only перевірка optional extensions локально skipped.

## Уточнення до прикладів

Див. [SKILL_LIBRARY_ERRATA.md](SKILL_LIBRARY_ERRATA.md): три редакційні помилки pinned upstream. Оригінальні файли та їх SHA256 збережені.
