# Уточнення до pinned upstream скілів

Upstream-файли в `skills/vendor/` збережено без змін для відтворюваності commit SHA/SHA256. Під час використання враховуйте три редакційні помилки, виявлені перевіркою PR13:

1. `skills/vendor/addyosmani/agent-skills/references/accessibility-checklist.md`: React-приклади з `onClick` та `htmlFor` — це JSX; мітку fence `html` читати як `jsx`.
2. `skills/vendor/addyosmani/agent-skills/references/performance-checklist.md`: приклади INP не слід об’єднувати з двома однойменними imports. Для attribution-прикладу використати `import { onINP as onINPWithAttribution } from 'web-vitals/attribution'` та `onINPWithAttribution(...)`.
3. `skills/vendor/anthropics/skills/skills/internal-comms/examples/3p-updates.md`: розділ Progress описує виконану роботу за **минулий** період; “next time period” у вступі — помилка. Плани на наступний період належать у Plans.

Ці уточнення не запускають код і не змінюють grants агентів. При оновленні upstream перевірити, чи помилки усунуто, та видалити неактуальні уточнення. Не видавати ці приклади за протестований production-код.
