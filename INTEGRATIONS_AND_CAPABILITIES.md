# 🔌 SYNDICATE — Інтеграції, Голос та Розширені можливості агентів

> Цей документ описує **нові канали підключення сторонніх сервісів**, **голосову
> підсистему** та **розширені можливості агентів Сем (квант) і Архітектор
> (CTO / N8N-інженер)**, додані у цьому оновленні архітектури.

---

## 1. Чесне застереження щодо «99% точності»

Андрій просив, щоб Сем давав «99% точних входів у ринок». Треба бути чесним:
**жодна торгова система у світі не може гарантувати фіксований відсоток
прибуткових угод** — ринки стохастичні. Тому у код **не «зашито» фейкове число
99%**.

Замість цього побудовано **багатошаровий движок конфлюенсу (confluence engine)**:
- сигнал формується лише коли **кілька незалежних факторів збігаються** (SMC,
  макро, COT-позиціонування, деривативи/ончейн, щит новин);
- є **жорсткий поріг-гейт** (за замовчуванням 95, як у специфікації Сема —
  налаштовується) на *ступінь узгодженості факторів*, а не на «ймовірність
  прибутку»;
- **обов'язковий Human-in-the-Loop** — Сем ніколи не відкриває угоду сам;
- **самонавчання** через журнал рефлексій та «негативні правила», що блокують
  повторення програшних патернів;
- **залізний захист капіталу** (ризик 1% на угоду, Hard Stop-Loss, денний
  стоп-аут 3%).

Це — реальний шлях підвищити якість входів. Поріг можна підняти, але штучне
«99%» лишиться маркетингом, а не інженерією.

---

## 2. Канали підключення сторонніх сервісів (`src/integrations/`)

Уніфікований шар конекторів. **Усі секрети — лише через Vault**
(`secret/data/syndicate/<service>`); змінні середовища — резервний варіант
тільки для локальної розробки (з гучним попередженням у логах).

| Модуль | Що дає | Ключові можливості |
|:---|:---|:---|
| `base.py` | Базовий клас `BaseConnector` | Читання секретів із Vault (KV-v2), HTTP через `httpx` з ретраями (tenacity) на 429/5xx, rate-limiter (token bucket), `health_check()` |
| `google_workspace.py` | **Google-сервіси** | Gmail (список / читання / **створення чернеток — DRAFT-ONLY**), Calendar (події), Drive (список / вивантаження / завантаження). Service Account **або** OAuth refresh-token |
| `telegram.py` | Telegram-боти | Надсилання повідомлень/документів, inline-кнопки для HITL, `answer_callback_query`, `set_webhook` |
| `mcp_gateway.py` | **Model Context Protocol** | JSON-RPC 2.0 до MCP-серверів, підпис `X-Marshal-Signature` (HMAC-SHA256), `list_tools` / `call_tool`, реєстр серверів |
| `registry.py` | Реєстр конекторів | `build_default_registry()` — вмикає потрібні конектори за конфігом |

### Google-сервіси — політика безпеки
- Пошта **ніколи не надсилається автоматично** — створюються **лише чернетки**
  (DRAFT), рішення про відправку — за людиною.
- Області доступу (SCOPES) обмежені мінімально необхідними.
- Підтримка domain-wide delegation через `GOOGLE_WORKSPACE_SUBJECT`.

### MCP-шлюз
Дає агентам доступ до зовнішніх інструментів через стандарт **Model Context
Protocol**: кожен виклик підписується HMAC-ключем із Vault, сервери
реєструються через `MCP_SERVERS` (`name=url,name=url` або JSON).

---

## 3. Голосова підсистема (`src/voice/`)

Провайдер-незалежний шар **TTS (синтез) / STT (розпізнавання)** з
**ланцюжком резервування**: перший «здоровий» провайдер виконує запит.

| Провайдер | Тип | Модуль | Джерело ключа (Vault) |
|:---|:---|:---|:---|
| **ElevenLabs** | TTS | `elevenlabs.py` | `elevenlabs` |
| **xAI / Grok voice** | TTS | `xai_grok.py` | `xai` (endpoint налаштовується) |
| **OpenAI TTS** | TTS (резерв) | `openai_tts.py` | `openai` |
| **Whisper (локальний)** | STT | `whisper_stt.py` | — (сервіс у docker-compose) |
| **Groq Whisper** | STT (резерв) | `whisper_stt.py` | `groq` |

Керування — через `VoiceManager` (`build_voice_manager`). Пріоритети задаються
`TTS_PRIORITY` / `STT_PRIORITY`. Будь-який агент може «отримати голос», не знаючи
деталей конкретного провайдера.

```python
from src.voice import build_voice_manager
vm = build_voice_manager(vault_client=vault, config=cfg)
result = await vm.speak("Доброго ранку, Андрію!")   # → audio_bytes
text   = await vm.listen(audio_bytes)               # → транскрипт
```

---

## 4. Сем (SAM) — квант-трейдер (`src/agents/sam/`)

Побудований суворо за `SAM_QUANT_SPEC.md`.

| Файл | Призначення |
|:---|:---|
| `confluence.py` | Движок 5-шарового синтезу + зважений бал + поріг-гейт |
| `skills.py` | Скіл-модулі: SMC, макро, COT, деривативи, щит новин, розрахунок ризику (import-safe: `smartmoneyconcepts`, `pandas-ta`, `ccxt`, `Riskfolio-Lib`, `cot-reports`, `yfinance` — опційні) |
| `journal.py` | Самонавчальний журнал угод + рефлексії + «негативні правила» (PostgreSQL, з fallback у пам'ять) |
| `signal.py` | Формування HITL-сигналу для Telegram (кнопки ✅/❌/✏️) + дайджест для Єви |
| `agent.py` | `SamAgent` — оркестрація всього, сумісний з графом |

**Дії агента:** `evaluate_setup`, `decision` (обробка callback), `outcome`
(запис результату + урок), `reflect` (нічна рефлексія), `digest`, `capabilities`.

**Гарантії:**
- `auto_execute = False`, `requires_hitl = True` для кожного сигналу;
- Hard Stop-Loss обов'язковий, інакше сигнал блокується;
- денний стоп-аут і щит новин дають жорсткий veto;
- поріг конфлюенсу налаштовується (`confluence_threshold`).

---

## 5. Архітектор (ARCHITECT) — CTO / N8N-інженер (`src/agents/architect/`)

Побудований за `ARCHITECT_CTO_SPEC.md` та `ARCHITECT_N8N_SPEC.md`.

| Файл | Призначення |
|:---|:---|
| `n8n_builder.py` | Генератор чистих N8N-воркфлоу (**тільки core nodes**, гілка OnError, idempotency-guard) + **Golden Templates Vault** (4 еталони) |
| `flowlint.py` | **FlowLint** — статичний аналіз JSON: core-only, обов'язковий OnError, заборона хардкод-секретів, ідемпотентність |
| `adr.py` | Генерація ADR (`/docs/adr/ADR-XXXX.md`) + conventional-commit повідомлень для GitOps |
| `agent.py` | `ArchitectAgent` — проектування, лінтинг, шаблони, ADR, code review |

**Дії агента:** `design_workflow`, `lint_workflow`, `golden_template`, `adr`,
`review_code`, `capabilities`.

Golden Templates згенеровано у `docs/patterns/`:
`golden_error_handler.json`, `golden_idempotent_webhook.json`,
`golden_retry_policy.json`, `golden_vault_jwt_bridge.json` — усі проходять
FlowLint без помилок.

---

## 6. Інтеграція в оркестратор (`src/orchestrator.py`)

Додано маршрутизацію та вузли графа для нових агентів:

| task_type | Агент | Дія |
|:---|:---|:---|
| `quant_signal`, `evaluate_setup` | sam | оцінка сетапу |
| `trade_decision` | sam | обробка рішення HITL |
| `portfolio_review` | sam | рефлексія |
| `design_workflow`, `lint_workflow` | architect | N8N |
| `golden_template`, `generate_adr`, `review_code` | architect | інструменти |

`EvaOrchestrator.__init__` тепер приймає опційні `config` та `registry`
(реєстр конекторів) — агенти отримують доступ до Telegram / Google / MCP.

---

## 7. База даних (`config/postgres/init.sql`)

Додано таблиці:
- `audit.integration_audit_log` — аудит викликів конекторів;
- `audit.voice_events` — облік TTS/STT;
- `agents.sam_trade_journal` — журнал сигналів/угод Сема;
- `agents.sam_reflections` — уроки та «негативні правила» (з `vector(1536)` для RAG).

---

## 8. Змінні середовища (`.env.example`)

Додано секції: Google Workspace, Telegram, MCP, а також голосові провайдери
(`TTS_PRIORITY`, `STT_PRIORITY`, ElevenLabs, xAI, OpenAI, Groq, Whisper).
**У проді всі значення читаються з Vault** — порожні поля в `.env` це нормально.

---

## 9. Що перевірено, а що ні

**Перевірено локально (статично / юніт-рівень):**
- ✅ Синтаксис усіх модулів (`ast.parse`), import-safe без опційних залежностей.
- ✅ Движок конфлюенсу Сема: проходження/непроходження порогу, veto новин,
  розрахунок ризику (0.01 лота на $100, R:R).
- ✅ Наскрізний потік `SamAgent`: сигнал → журнал → рішення (reject → урок).
- ✅ Генерація N8N-воркфлоу + FlowLint (усі Golden Templates чисті; «поганий»
  воркфлоу з community-нодою та секретом коректно відхиляється).
- ✅ Реєстр конекторів і `VoiceManager` будуються без помилок.

**НЕ перевірено в цьому середовищі (потрібен повний стек):**
- ⚠️ Реальні виклики Google / ElevenLabs / xAI / Telegram (потрібні ключі + Vault).
- ⚠️ Повний запуск контейнерів docker-compose та підключення до PostgreSQL/Redis.
- ⚠️ Живе виконання N8N-воркфлоу на n8n-інстансі.

Ці кроки виконуються під час розгортання (див. `DEPLOYMENT_RUNBOOK.md`).
