# Marshal — незалежний контроль shared knowledge pool

**Статус:** процедура для майбутнього host-run review; Marshal лишається `prepared_not_enabled`, без runtime grants та інтеграцій.

## Незалежність

Marshal перевіряє окремо від KODEX: той самий source digest і похідний content digest, але не покладається на KODEX-ове `approved` поле, self-assessment або summary ризиків як доказ. До появи контрольованого host path жоден item не публікується; зараз усі записи — `review_pending`.

## Мінімальний review

1. **Походження та права:** чи відоме джерело, автор/видавець і дозвіл на зберігання/похідний текст; чи немає повної чужої книги, платного курсу або приватних даних.
2. **Integrity:** SHA-256 саме тієї версії, яку читає рецензент; зв'язок із source IDs та відсутність неочікуваних шляхів/symlink.
3. **Структурна й фактична точність:** чи відповідає конспект файлу, чи не заповнено прогалини припущеннями, чи зафіксовані суперечності/підрахунки.
4. **Безпека:** prompt injection, інструкції виконання, неочікувані URLs/endpoints, секрети, PII, шкідливі код/залежності, приховані мережеві/публікаційні side effects.
5. **Доменний ризик:** медичне, психологічне, юридичне, податкове, інвестиційне/крипто або інше високоризикове твердження потребує явного джерела й меж. Юрисдикція має відповідати задачі; невизначене лишається quarantined.
6. **Придатність:** item — короткий довідник, а не прихована policy; target agents — індексні підказки, не дозволи; вміст не збільшує права агента.
7. **Технічний scanner:** no-LLM pass зберігається як доказ, але не замінює незалежного review. `failed`, missing, malformed або incomplete scan означає `quarantine`/`review_pending`, ніколи auto-approve.

## Вердикти

- `approved`: лише для низькоризикового похідного матеріалу після всіх перевірок і на конкретний digest/version. Потрібен detached HMAC, підписаний host-owned ключем із Vault за участі authenticated Marshal review path; ключ недоступний KODEX, prompt і source content.
- `review_pending`: бракує фактів, прав, scanner coverage або доменної перевірки.
- `rejected` / `quarantined`: injection, секрет/PII, права не підтверджені для потрібного використання, небезпечні дії, high-risk advice без належної перевірки або істотна невідповідність джерелу.

Відхилення/невизначеність не приховувати. Виправлений текст — нова версія з новим хешем і повторним оглядом. Підпис має бути прив'язаний до item ID, content SHA-256, версії, review ID, часу та scanner status; будь-яка зміна анулює його.

## Неприпустимі дії

- Вважати наявність metadata `status=approved` достатньою: `KnowledgePool` вимагає валідний HMAC і окремий shared-read allowlist.
- Давати KODEX право підпису, обходити checks, автоматично підвищувати статус через n8n або після одного scanner pass.
- Активувати Runtime, grants, n8n workflow, service connection або model selection у межах review.
- Додавати повні джерела до Git без підтвердження прав; передавати секрети/медичні дані в звіт чи audit.

Зараз немає approve/publish endpoint, підписаних записів або host approval key у репозиторії. Майбутній signing path потребує окремої операторської зміни й тестів; ця політика сама нічого не схвалює.

## MCP connector review (окрема процедура)

MCP-конектори — executable integration supply chain, не knowledge-pool content. Marshal перевіряє конкретні upstream commit/package digest, license, dependencies, tool schemas/side effects, secrets, data flow, egress, isolation та tests за `marshal-mcp-connector-review`. Загальний admission process описаний у `docs/MCP_CONNECTOR_DISCOVERY.md`.

`ready_for_operator_consideration` означає лише рекомендацію для host review, а не дозвіл на install, service connection, OAuth, tool grant або запуск. Не підписувати connector-рішення Marshal HMAC для knowledge items; це різні trust domains. До окремого operator approval runtime-конфігурація і grants лишаються незмінними.
