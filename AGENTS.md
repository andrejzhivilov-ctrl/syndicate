# AGENTS.md — правила для будь-якого AI-агента в цьому репозиторії

Цей файл читають усі AI-інструменти, що працюють з кодом (Arena Agent, Google Antigravity,
Codex, Claude Code тощо). Якщо ти агент — почни звідси, перш ніж щось змінювати.

**Проєкт:** EVA SYNDICATE — автономний AI-холдинг, 10 поверхів (Floor 1 інфраструктура →
Floor 10 Marshal/безпека). Python 3.11, FastAPI, LangGraph, PostgreSQL+pgvector, Redis,
HashiCorp Vault, n8n. Оператор-людина — Andrii.

---

## 0. Перед початком роботи

```bash
git pull --ff-only
cat docs/HANDOFF.md     # що зроблено й що не дороблено попереднім агентом
bash tools/check.sh     # усі ворота мають бути зеленими ДО твоїх змін
```

Якщо ти Google Antigravity — додатково прочитай **`docs/ANTIGRAVITY_BRIEF.md`**: там межі
твоєї зони, правила співпраці з Arena Agent і підготовлений промпт для старту.

Якщо ворота червоні до твоїх змін — не починай, а спочатку скажи про це людині.

---

## 1. Найголовніше правило: НІКОЛИ НЕ ВИГАДУЙ ДАНІ

Це причина, чому в репозиторії є розгалужене покриття регресійними тестами. Агент, який повертає
«правдоподібну цифру» замість реальної, — це не дрібна помилка, це отруєння всієї системи:
такі значення потрапляють у фінансові, медичні й маркетингові звіти людини.

**Правило:** якщо реального значення немає — повертай структуровану відсутність.
Ніколи не підставляй дефолт, який виглядає як виміряний.

```python
# ✅ ПРАВИЛЬНО
return {"status": "unavailable", "value": None, "warning": "no data from <source>"}
return {"status": "ok", "value": 42.0, "synthetic": False}
return {"status": "ok", "value": 42.0, "synthetic": True,   # демонстраційні дані
        "warning": "DEMO data — not measured"}

# ❌ НЕПРАВИЛЬНО — це саме те, що ми вичищали місяць
return {"status": "ok", "revenue": 210.0, "costs": 35.0}     # вигадані гроші
return {"status": "synced", "balance": 185400.0}             # заглушка як «реальна»
return {"status": "mock_success", "video_id": "MOCK_YT_ID"}  # «успіх» без дії
return {"runway_months": 999}                                # безкінечність замість None
```

Якщо тобі потрібні демонстраційні/шаблонні дані для dry-run — **позначай їх**:
`synthetic: True` (або `sample_data: True`) + `warning`, і бажано роби їх opt-in через
змінну оточення (приклади: `EVA_BANKING_SANDBOX`, `EVA_GROK_MOCK`).

Відсутність даних — це `unavailable`, а не `ok`.

---

## 2. Інші жорсткі правила

| Правило | Де |
|---|---|
| Людина затверджує будь-яку дію з грошима, торгівлею, видаленням і публікацією | `src/confidence.py` → `NEVER_AUTO_ACT` |
| Секрети — тільки через Vault, шляхи — тільки з `src/vault_paths.py`. Не вигадуй своїх шляхів | `src/vault_paths.py`, `src/integrations/base.py` |
| Записувані файли — тільки через `src/data_paths.py` (`EVA_DATA_DIR`). Контейнер має read-only корінь | `src/data_paths.py` |
| PII маскується до відправки в зовнішній LLM | `src/pii.py` |
| Пошта ніколи не надсилається автоматично — тільки чернетки | `src/integrations/google_workspace.py` |
| Мережеві виклики (Edge-TTS, Pexels, LLM) не повинні «ронити» весь поверх — завжди `try/except` + чесний статус | `content_factory/*` |
| `datetime.utcnow()` заборонено — лише `datetime.now(timezone.utc)` | весь код |

---

## 3. Ворота (обов'язково перед будь-яким комітом)

```bash
bash tools/check.sh
```

Це те саме, що:

```bash
.venv/bin/python -m pytest tests/ -q                      # усі pytest-тести
.venv/bin/python tests/test_10floors_architecture.py      # 10/10 suite'ів
.venv/bin/python tests/sandbox_test.py                    # 8/8 suite'ів
.venv/bin/ruff check --select F,E9,B --ignore E501,B008,B904 src deploy tests tools
.venv/bin/ruff check --select C901 src deploy tests tools
.venv/bin/python -m pytest tests/test_postgres_paths.py -q   # живі SQL-шляхи (потрібна БД)
```

**SQL-гілки не приймаються «за кодом».** Усе, що виконується в PostgreSQL, перевіряється на
справжньому сервері: `tests/live_pg.py` піднімає `pgserver` (вбудований PostgreSQL 16 + pgvector,
`requirements-dev.txt`) або бере `EVA_TEST_DATABASE_URL` (у CI — сервіс `pgvector/pgvector:pg16`).
Без бази тести друкують явний skip; у CI `EVA_REQUIRE_LIVE_DB=1` робить skip помилкою, тож
зелений прогін без БД неможливий. Ставити інструменти: `pip install -r requirements-dev.txt`.

Схема `config/postgres/*.sql` мусить бути **ідемпотентною**: `init.sql` застосовується повторно, а
`migration_v4.sql` — поверх нього (саме тому тригери створюються через `DROP TRIGGER IF EXISTS`).

Усі мають бути зеленими. **Заборонено** «лагодити» тест під себе — тест фіксує реальний
дефект, який уже виправлено. Якщо тест заважає — значить ти відновлюєш стару помилку.

Якщо додаєш нову функцію — додай регресійний тест у `tests/test_regressions.py`.

---

## 4. Гілки й коміти

- Основна гілка — **`main`**. Вона завжди має бути зеленою.
- Кожна зміна — **окрема гілка**: `feat/<що>`, `fix/<що>`, `audit/<дата>`.
- У `main` потрапляє тільки те, що пройшло `tools/check.sh`.
- Два агенти **ніколи не редагують `main` одночасно**.

**Клієнтський додаток** (ПК + смартфон) — окрема довгоживуча гілка `app/client` від `main`,
але з обов'язковим регулярним злиттям (раз на тиждень або як тільки щось працює).
Сувора межа каталогів:

```
apps/       ← ТІЛЬКИ клієнтський додаток. Зона Antigravity.
src/ deploy/ tests/ config/   ← бекенд. Зона Arena Agent.
apps/shared/api-contract.yaml  ← генерується З БЕКЕНДУ. Власник — Arena Agent,
                                 споживач — Antigravity. Спершу змінюється контракт,
                                 потім код з обох боків.
```

Якщо додатку потрібна нова можливість бекенду — не пиши її сам, а опиши в `docs/HANDOFF.md`
у розділі «Запит до бекенду»: який endpoint, які поля, яка семантика порожнього стану.
- Коміт-повідомлення англійською: `fix:`, `feat:`, `chore:`, `docs:`, `refactor:`.
- Документація й звіти — українською. Код, коментарі, ідентифікатори — англійською.

---

## 5. Після роботи — обов'язково

Допиши в **`docs/HANDOFF.md`**: що зробив, що **не** встиг/не доробив, що робити наступним,
які ризики побачив. Наступний агент не має пам'яті про твою сесію — тільки цей файл.

---

## 6. Пастки, які вже ловили (не повторюй)

Це реальні дефекти, знайдені аудитом 2026-10-05. Кожен має регресійний тест.

1. **Заглушка як «успіх»** — портфель-заглушка з `status: "synced"`; `mock_success` у публікаторі;
   вигаданий `video_id`. → §1 цього файлу.
2. **Параметр прийнятий і проігнорований** — `negative_constraints(symbol=…)` не фільтрував;
   `office_copilot(tool=…)` не фільтрував. Якщо підписуєш параметр — використовуй його.
3. **Невідома дія мовчки робить щось інше** — Marshal запускав повний security audit,
   Kira падала в `socratic_dialogue`. Невідома дія = явна помилка + `available_actions`.
4. **Ручний список доступних дій** — розходиться з кодом. Виводь його з `sorted(self._ACTION_MAP)`.
5. **Фіксовані діапазони/довжини** — `merge_cells("A1:F1")` ламався на 3 колонках;
   патерн IBAN на 27 символів не покривав українські 29 → **витік PII в зовнішній LLM**.
6. **Таймстампи, що округлюються за межі поля** — ASS-субтитри з `.100` соті.
7. **`status: "ok"` без перевірки результату** — FFmpeg повернув 0, а файла немає.
8. **Порожній `except`, що гасить конвеєр** — мережева помилка Edge-TTS валила весь Floor 2.
9. **Фонова задача без посилання** — `asyncio.create_task(...)` без збереження в змінну
   збирається GC; цикл поновлення токена Vault вмирав від першої ж помилки мережі.
10. **Складність (C901 > 10)** — розбивай винесенням функцій або таблицею диспечеризації,
    а не `# noqa: C901`.

---

## 7. Коротко про структуру

```
src/agents/              агенти поверхів (eva, fin, sam, kira, doc, marshal, architect, office_copilot)
src/departments/         content_factory, operations, compliance, coordinator (Floor 2)
src/integrations/        зовнішні сервіси (telegram, google_workspace, banking, mcp_gateway)
src/verifier.py          Orc — адверсаріальний верифікатор тверджень
src/council.py           LLM Council — критичні рішення кількома моделями
src/confidence.py        бюджет довіри + HITL-гейт
src/pii.py               маскування PII перед зовнішнім LLM
src/data_paths.py        ЄДИНЕ джерело шляхів для записуваних даних
src/vault_paths.py       ЄДИНЕ джерело шляхів секретів Vault
src/embeddings.py        ЄДИНЕ джерело векторів для пам'яті (BGE-M3, 1024 вим.)
deploy/runtime/embeddings_server.py  локальний сервіс ембеддингів (окремий контейнер)
tests/                   pytest-тести + 2 наскрізні suite'и
tests/live_pg.py         підйом справжнього PostgreSQL+pgvector для тестів
tests/test_postgres_paths.py  живі SQL-шляхи (схема, pgvector, журнал, device-токени)
requirements-dev.txt     pytest/ruff/pgserver — тільки для розробки й CI
tools/check.sh           всі ворота однією командою
.github/workflows/ci.yml CI: ворота + job із сервісом pgvector
docs/HANDOFF.md          журнал передачі між агентами ← починай звідси
docs/BACKLOG.md          що робити далі
docs/FIX_REPORT.md       звіт про аудит 2026-10-05 (українською)
```
