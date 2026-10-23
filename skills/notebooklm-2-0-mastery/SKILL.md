---
name: notebooklm-2-0-mastery
description: End-to-end architecture and operational protocol for Google NotebookLM 2.0 (Gemini Notebook) + Obsidian Second Brain + pgvector 3-Tier Hybrid Memory across SYNDICATE Holding (syndicateholding.com).
---

# SYNDICATE Skill: Google NotebookLM 2.0 Mastery & 3-Tier Hybrid Memory

## 1. Консолідований Майстер-Блокнот (Single Source of Truth)
- **Master Notebook ID:** `0a882755-acbf-468c-be37-21e40395dd50`
- **Назва:** *"Google NotebookLM: Екосистема, Практика та Майстер-Гайд"* (129 верифікованих джерел, 0 помилок).
- **Мовна директива Андрія (Обов'язкова):** Усі артефакти в NotebookLM Studio (подкасти Audio Overview, інтерактивні Mind Maps, звіти Study Guide, презентації Slide Decks, інфографіка) **ЗАВЖДИ генеруються українською мовою (`--language uk`)**, за винятком спеціалізованих англомовних тренажерів вимови Кіри.

## 2. Інформаційна Алхімія (`Compress & Convert to Source`)
- **Проблема:** Ліміт 300 джерел (Free) / 500 джерел (Pro/Ultra) та деградація уваги («Index Tax») при великій кількості сирих файлів.
- **Рішення:** Агент `kodex` або `alice` групує 5–10 тематичних джерел, генерує концентрований аналітичний звіт у Нотатках, виконує дію **`Convert to Source`**, а початкові сирі джерела видаляє або архівує. Це розширює реальну місткість блокнота до **1 500–3 000 документів** без втрати фактів.

## 3. Обхід ліміту 500 символів (`00_MASTER_INSTRUCTIONS.md`)
- Вікно кастомних інструкцій чату NotebookLM обмежене 500 символами.
- Замість нього створюється закріплене джерело `00_MASTER_INSTRUCTIONS.md`, яке містить повну конституцію форматування, тон звертання до Андрія, матрицю агентів та правила цитування `[1]`, `[2]`.

## 4. Late Chunking та 3-Рівнева Гібридна Пам'ять (Боротьба з «Index Tax»)
Щоб уникнути затримки 5–15 секунд при кожному запиті до 500 джерел у NotebookLM:
1. **Tier 1 — Obsidian Second Brain (`C:\Second Brain` / `/data/obsidian_vault`):** миттєвий локальний граф Markdown-нотаток із `[[двосторонніми зв'язками]]` та `.canvas` (0 мс мережі, `$0`).
2. **Tier 2 — PostgreSQL 16 + `pgvector` + `BAAI/bge-m3`:** швидкий векторний кеш (`<20 мс`, `$0`) з використанням **Late Chunking** (кожен чанк зберігає глобальний контекст документа).
3. **Tier 3 — Google NotebookLM (`Gemini 3.1 + Deep Research`):** глибокий мультимодальний синтез та генерація Studio-артефактів (`$0` API токенів).

## 5. Безпека та Ізоляція Токенів (`syndicateholding.com`)
- Для серверної автоматизації через `nlm` CLI (`jacob-bd/notebooklm-mcp-cli`) та `notebooklm-py` використовується **виключно ізольований технічний акаунт** на корпоративному домені **`syndicateholding.com`** (наприклад, `kodex-bot@syndicateholding.com`), якому надано доступ Editor до спільних блокнотів.
- Особистий `--master-token` власника ніколи не зберігається у відкритому вигляді на публічних вузлах.
