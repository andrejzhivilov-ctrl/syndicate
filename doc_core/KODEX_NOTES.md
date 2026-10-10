# KODEX — K.O.D.E.K.S. (Knowledge Organization & Database Extraction System)

Системний агент архівів. Лише Telegram-інтерфейс (`src/agents/kodex_buttons.py`). Безкоштовний у роботі.

## Обов'язок
Приймати великі обсяги, структурувати, розподіляти по агентських і спільних базах, сортувати, редагувати, видаляти. Звітує Єві про завантаження, перетворення, видалення і всі дії.

## Правила
- Інтернет і будь-яке завантаження — лише з явного підтвердження Андрія (`request_download` → `approve_download`).
- Видалення двоетапне: запит → підтвердження Андрієм → кошик на 30 днів.
- `andrii_medical_vault` (ANDRII_IMMUTABLE): читання — так; запис і видалення — ніхто, KODEX також ні.
  Моє рішення (потребує підтвердження Андрія): KODEX має доступ лише для читання до цього сховища.
- Невідомий формат не відкидається: `needs_parser` → вивчення тільки після підтвердження.
- Класифікація детермінована (ключові слова), без платного LLM.

## Формати
| Статус | Формати |
|---|---|
| native | md, txt, csv, json |
| library_installed | docx, xlsx, pptx |
| vendored_parser | pdf, epub, html, rtf (через вендорений book-to-skill) |
| needs_engine | mp3, wav, m4a, mp4 — транскрибація локальним безкоштовним рушієм (ще не встановлено) |

## Відкладено до деплою
Транскрибація та переклад (рушій), Obsidian, NotebookLM, Google Drive, Sheets, парсери Office/PDF у середовищі деплою, Telegram-токен.

## Файли
- `src/agents/kodex.py` — сховище, ingest, rewrite, move, видалення, інтернет-гейт, звіт Єві
- `src/agents/kodex_buttons.py` — меню і callback
- `config/agents/kodex.profile.json` — профіль (prepared_not_enabled)
- `tests/test_kodex.py`
