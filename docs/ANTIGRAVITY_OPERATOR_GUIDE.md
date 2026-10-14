# Antigravity: операторська інструкція Google One

Дата: 2026-10-14. Рішення Андрія: працювати на його підписці Google One.
Точний тариф/регіональні права/квоти акаунта не перевірені. Це **керований
handoff**, а не unattended Google API агент. Автоматичні API-витрати = не підключені.
Профіль `prepared_not_enabled`, grants порожні; CLI — локальний інструмент власника,
не обхід host policy і не Telegram endpoint для сторонніх користувачів.

## 1. Офіційні джерела та межі

Перевірено 2026-10-14 через публічні офіційні сторінки:

- [1](https://support.google.com/googleone/answer/16286513?hl=en) — опис AI Ultra,
  Antigravity і окремих квот/AI credits. Звичайна назва Google One не визначає AI-tier.
- [2](https://gemini.google/subscriptions/) — сторінка Google AI-планів і функцій.
- [3](https://ai.google.dev/gemini-api/docs/billing) — Gemini API використовує
  project/Cloud Billing, free/paid tiers, власні обмеження й оплату.

Ми не читаємо платіжну інформацію акаунта, не встановлюємо вартість за назвою
моделі з повідомлення і не підключаємо AI Studio/Vertex/API key замість підписки.
Андрій сам входить у свій акаунт в офіційному Antigravity/Gemini/Flow та перевіряє
план, доступність і квоти. Не купувати top-up credits і не вмикати автоматичні
витрати без окремого рішення. Мови/функції можуть залежати від продукту.

## 2. Встановлення локальних інструментів

На довіреному хості з Python 3.11:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt -r requirements-fin.txt
export EVA_DATA_DIR=/data/eva
.venv/bin/python tools/antigravity_studio.py status
```

Створіть `/data/eva` заздалегідь із власником того користувача, який запускає CLI;
не використовуйте `chmod 777`. Workspace автоматично створює підкаталоги з 0700,
а файли з 0600. EVA_DATA_DIR обов'язково абсолютний, **поза репозиторієм**.
Symlink-шляхи заборонено. Батьківські каталоги не мають бути writable сторонніми.
Код — не multi-user сервіс, не захист від root і не sandbox для виконання проєктів.

Для відео встановіть системний FFmpeg; для українських зображень — DejaVu:

```bash
sudo apt-get install ffmpeg fonts-dejavu-core
```

Agent Dockerfile вже містить FFmpeg і додані шрифти, але CLI запускається з checkout
(каталог tools не копіюється в runtime image). Docker build у цій сесії не виконувався.
Не додавайте реальні ключі, cookies або приватний архів до working directory IDE.

## 3. Завдання для Google-підписки

Спочатку ініціалізуйте сховище:

```bash
.venv/bin/python tools/antigravity_studio.py init
```

Потім покладіть очищений UTF-8 brief у
`$EVA_DATA_DIR/antigravity-studio/inbox/brief.txt`. Не пишіть секрети в CLI arguments.

```bash
.venv/bin/python tools/antigravity_studio.py task app --brief-file inbox/brief.txt
```

Результат містить `task_id` — скопіюйте його в локальну змінну TASK_ID. Підтримані
типи: app, img, video, research, github. Статус `awaiting_operator` означає, що
нічого ще не згенеровано у Google і жодного мережевого виклику не відбулося.

```bash
.venv/bin/python tools/antigravity_studio.py packet "$TASK_ID" --operator-reviewed
```

Прапорець означає: **ви власноруч перевірили brief на особисті дані й таємниці**.
Автоматична евристика відхиляє схожі на ключі рядки й маскує поширені PII, але не
гарантує очищення всіх медичних/особистих даних. Пакет зберігається в artifacts/.
Перевірте його ще раз і лише тоді вручну передайте у свій Google-продукт.

Код/сайти — Antigravity; дослідження — доступна вам функція Gemini; зображення
й відео — доступні вам засоби Gemini/Flow. Це маршрути для людини, а не реалізовані
API endpoints. Не використовувати всю репозиторну папку/чат як безумовний контекст.
Зовнішній продукт не підпорядковується host policy SYNDICATE: оператор має
вимкнути auto-run/auto-deploy і перевіряти його запити на доступ.

## 4. Повернення результату без виконання

Збережіть завантажений файл у приватний inbox. Архіви ZIP, виконувані файли,
symlink і завантаження за URL не підтримуються. Максимум — 64 MiB на файл.
Копіювання не означає безпечність файлу або проходження тестів.

```bash
.venv/bin/python tools/antigravity_studio.py receive "$TASK_ID" inbox/result.html
```

Зберігаються окрема копія та manifest: SHA-256, bytes, task ID і статус
`received_untrusted_not_executed`. Текстові результати перевіряються евристикою
секретів. Код не запускається, HTML не відкривається, залежності не встановлюються,
PR/merge/deployment автоматично не створюються. Для складних проєктів — окремий
ізольований checkout/sandbox без секретів, ручний code review і тести, потім PR.
Небезпечний HTML/JS не відкривайте в основному браузері з авторизованими акаунтами.

## 5. Локальні артефакти без Google і без оплати

```bash
.venv/bin/python tools/antigravity_studio.py landing --title 'Мій проєкт' --description 'Опис пропозиції'
.venv/bin/python tools/antigravity_studio.py poster --title 'Мій проєкт'
.venv/bin/python tools/antigravity_studio.py video artifacts/ІМЯ_ПОСТЕРА.png --seconds 5
```

- landing: реальна статична HTML-чернетка, escaped текст, немає збору лідів,
  авторизації, backend або платежів; не «згенерований повний SaaS».
- poster: реальний PNG 1280x720 із текстом, **детермінований**, не AI-зображення.
- video: PNG перетворюється в MP4 H.264, 24 fps, без звуку; 1–30 секунд,
  1 thread, timeout 90 с, вихідний cap 16 MiB; без мережі/shell/музики/озвучення.
  При відсутності FFmpeg — unavailable, не вигаданий шлях готового ролика.

Ці команди створюють лише локальні файли з унікальними назвами. Нічого не
перезаписують із файлів оператора. FFmpeg пише лише в щойно створений файл відео.

## 6. Приватна історія: локальний пошук, не повний RAG

Не копіюйте автоматично `EVA_SYNDICATE_FULL_DIALOGUE.txt`. Спочатку Андрій відбирає
безпечні немедичні фрагменти в **нову приватну UTF-8 копію**. Не змінювати оригінал.
Покладіть її у workspace `inbox/reviewed-history.txt` із правами 0600.

```bash
.venv/bin/python tools/antigravity_studio.py history-ingest inbox/reviewed-history.txt --operator-reviewed
.venv/bin/python tools/antigravity_studio.py history-search 'контейнери'
```

Індекс — SQLite FTS5, лише локально, до 5 MiB на джерело, фрагменти по 1600
символів із кроком 1400. SHA-256 очищеного джерела забезпечує ідемпотентність:
повторна індексація повертає already_indexed без дублікатів. Кожен результат має
source_hash і номер chunk. Це лексичний пошук, не embedding, не pgvector,
не гарантія повного розуміння і не багатокористувацький ACL. Зовнішніх викликів немає.
Історія не додається автоматично до Google-пакетів. Старий запис про дозвіл у
діалозі не надає актуальних grants. При збігу евристики секретів імпорт відхиляється
**до** запису будь-яких фрагментів; помилковий збіг потрібно перевірити вручну.

## 7. Звітність, резервні копії, видалення

```bash
.venv/bin/python tools/antigravity_studio.py audit-report
```

Журнал містить операції, object IDs і UTC timestamp, але не brief/секрети. Статус
`local_report_not_delivered_to_eva` чесно означає ручну передачу звіту Єві о 21:00.
Автоматичний канал до Єви ще не підключено. Звіти можуть бути великими; переглядати
локально, не публікувати весь stdout. Історія/артефакти не видаляються цим CLI.

Бекап workspace включати **окремо** в зашифрований backup; tools/backup.py не
гарантує копію цього дерева. Для consistent SQLite backup зупинити CLI на час
копіювання або використати SQLite backup API. Restore спочатку в приватний тестовий
каталог і перевірити hash/пошук/права. Без підтвердження власника purge не робити.
