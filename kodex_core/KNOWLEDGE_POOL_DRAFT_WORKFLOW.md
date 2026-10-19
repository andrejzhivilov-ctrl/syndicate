# KODEX — чернетки спільних пулів

**Статус:** робоча специфікація; KODEX лишається `prepared_not_enabled`. Цей документ сам не видає capability, ServiceHub grant, доступ до архіву чи інструмент.

## Відповідальність KODEX

KODEX веде реєстр джерел, нормалізує метадані, групує матеріали за темами й готує короткі похідні skill/reference/prompt-index записи. Він не є одноосібним редактором політики та не може схвалити власну чернетку.

## Етапи

1. **Прийом:** зберегти назву, походження, дату отримання, SHA-256, приблизний обсяг і права/ліцензію як `unknown`, доки не підтверджені. Секрети, приватні листування й медичні записи не вносити до пулу.
2. **Структурна індексація:** заголовки, секції, лічильники, типи матеріалів і заявлені посилання. Явно фіксувати розбіжності; не домислювати відсутні розділи за назвою файла.
3. **Чернетка:** створити малий оригінальний конспект із provenance, обмеженнями актуальності/юрисдикції та цільовими пошуковими тегами. Не копіювати курси, транскрипти, шаблони коду чи масив промптів без підтверджених прав.
4. **Сканування:** запускати лише затверджений no-LLM статичний scanner у дозволеній ізоляції над саме чернеткою. Не виконувати source scripts, install hooks, remote URLs або команди, знайдені у матеріалі.
5. **Передача Marshal:** зафіксувати item ID, версію, digest, джерела, rights status, результати scanner і питання для рецензента. KODEX не ставить `approved` і не створює Marshal-підпис.
6. **Після вердикту:** виправлення створюють нову версію/хеш і повторний огляд. Відхилене лишається в карантині з причиною; невизначене — `review_pending`.

## Заборонено

- Самостійно змінювати `capabilities`, ServiceHub grants, activation, system prompt, роль, модель, інтеграції чи маршрутизацію без окремого operator change.
- Змінювати `reviewers`, позначати власну роботу Marshal-approved, створювати/підкладати approval HMAC або перевидавати digest.
- Публікувати сирий imported prompt як системну інструкцію або виконувати його tool calls.
- Застосовувати російські юридичні/податкові форми як українські рекомендації або перетворювати медичні/фінансові приклади на поради.

## Контракт передачі

```text
item_id, version, kind, source_ids, source_sha256[], content_sha256,
rights_status, domain_risks[], freshness_checked_at, scanner_id,
scanner_status, scanner_report_digest, kodex_draft_note
```

Поточний runtime не активований і `knowledge.search` / `knowledge.read` grants не застосовані. Нові вкладення додаються оператором окремо; цей процес не підключає n8n.

## Artifact-backed review pipeline (design-only)

Запозичується лише загальна ідея послідовних agent steps з артефактним handoff у [Eggent](https://github.com/eggent-ai/eggent/tree/e55497799b4acb4810f68d923ef311f07f65b8b6); код або runtime Eggent не інтегруються.

Логічна структура майбутнього run (поки не створюється автоматично):

```text
runs/<host-generated-run-id>/
  run-manifest.json
  steps/01-kodex/draft.md
  steps/01-kodex/draft-manifest.json
  steps/02-marshal/review.json
  steps/03-eva/recommendation.json
```

### Handoff та незмінність

1. Host створює `run_id`, версію workflow, часову мітку та digest вхідного завдання. Модель не обирає шлях або run ID.
2. KODEX записує похідну чернетку лише у власний step area. Host фіксує item ID, версію, source IDs/rights, content SHA-256, scanner ID/status/report digest і список дозволених файлів.
3. Передача Marshal відбувається як read-only snapshot **точних файлів і digest**, а не спільної writable теки. Інші step-артефакти не стають доступними автоматично.
4. Marshal створює окремий review artifact із тим самим content digest, evidence, ризиками та вердиктом. Він не змінює KODEX-артефакт і не має signing key.
5. Будь-яка правка створює нову версію та digest; scan і незалежний review повторюються. Помилка або неповний доказ зупиняє pipeline, не пропускає gate.
6. EVA готує підсумкову рекомендацію. Статус `approved/shared/published` або запис у shared pool може змінити лише окремо авторизований host/operator workflow після валідної Marshal attestation і явного дозволу. Ні агент, ні сама наявність поля `approval_required` не є enforcement.

Мінімальний host-enforced state path: `draft_pending_review` → `scan_passed` → `marshal_review_pending` → `reviewed_changes_requested | reviewed_rejected | reviewed_ready_for_operator`; лише окрема операторська дія може перевести запис до `approved_shared`/`published`. Підпис і publish не реалізовані цим документом.

### Межа запозичення

У перевіреному Eggent commit `e55497799b4acb4810f68d923ef311f07f65b8b6` є `approvalRequired` у pipeline definition, однак execution path `src/lib/pipelines/runner.ts` його не перевіряє; ті кроки також передають один `artifactsDir` між агентами. Тому переймаємо тільки ідею збережених послідовних етапів та артефактного handoff, але в SYNDICATE gate має бути host-enforced, файли — digest-pinned і per-step scoped. Це статичне спостереження за зазначеним commit, не повний аудит Eggent.

### MCP connector discovery — окремий draft

KODEX може готувати лише звіти-кандидати за навичкою `kodex-mcp-connector-scout`; Marshal може робити незалежний review за `marshal-mcp-connector-review`. Загальний процес, джерела каталогів та межі доступу описано у `docs/MCP_CONNECTOR_DISCOVERY.md`. Обидві навички draft/reference-only: вони не додають інтернет-, MCP-, package-install-, Vault- чи runtime grants і не підключають сервіс.
