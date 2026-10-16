# 🔄 EVA N8N WORKFLOW SPECS — Архітектура воркфлоу Єви (v1.0)

> **Контекст:** Всі воркфлоу SYNDICATE живуть у N8N v1.65+ (self-hosted, контейнер `n8n` у docker-compose).
> N8N — це оркестратор, не розум. Розум — це Claude Sonnet/Haiku в HTTP Request нодах.
> Усі секрети зберігаються у Vault та передаються в N8N через env-змінні.

---

## АРХІТЕКТУРА: ЯК N8N ВЗАЄМОДІЄ З АГЕНТАМИ

```
ЗОВНІШНІЙ ТРИГЕР (Telegram / Cron / Webhook)
            │
            ▼
    ┌──────────────┐
    │  N8N Workflow │  ← Оркестрація, routing, retry, logging
    └──────┬───────┘
           │ HTTP POST /process
           ▼
    ┌──────────────────────────────────────────┐
    │  Agent FastAPI (eva:8001 / doc:8005 ...)  │  ← Власний розум агента
    │  Runtime: agent_runner.py                 │
    │  LLM: Claude via Vault-ключ              │
    └──────────────────────────────────────────┘
           │
           ▼
    Telegram API (відповідь Андрію) / ARCHIVE / Google Workspace
```

---

## ВОРКФЛОУ 1: EVA-GATEWAY-INBOUND
**Тригер:** Telegram Webhook (будь-яке повідомлення в @syndicate_bot)
**Призначення:** Розпізнати тип вхідного запиту і направити в потрібний воркфлоу або обробити безпосередньо.

```
[Telegram Trigger]
        │
        ▼
[Switch Node — Тип повідомлення]
    ├── voice_message  → [HTTP: Whisper STT] → [HTTP: Eva /process] → [Telegram: Відповідь]
    ├── photo          → [HTTP: Eva /scan_doc] → [Telegram: Відповідь + PDF посилання]
    ├── video/audio    → [HTTP: Eva /media_process] → [Telegram: Конспект]
    ├── document (PDF) → [HTTP: Eva /analyze_doc] → [Telegram: Аналіз]
    ├── location       → [HTTP: Eva /geo_lookup] → [Telegram: Карта + опції]
    └── text           → [HTTP: Eva /process] → [Telegram: Відповідь]
```

**N8N Ноди (13 штук):**
1. `Telegram Trigger` — Polling або Webhook (HTTPS через Nginx)
2. `Function: Extract Content` — JS-нода: розпакувати тип, текст, file_id
3. `Switch: Message Type` — 6 гілок за типом
4. `HTTP Request: Whisper STT` → `http://whisper:9000/transcribe`
5. `HTTP Request: Eva /process` → `http://eva:8001/process`
6. `HTTP Request: Eva /scan_doc` → `http://eva:8001/scan_document`
7. `HTTP Request: Eva /media_process` → `http://eva:8001/media_process`
8. `HTTP Request: Eva /analyze_doc` → `http://eva:8001/analyze_document`
9. `HTTP Request: Eva /geo_lookup` → `http://eva:8001/geo_lookup`
10. `Error Trigger` — перехват помилок будь-якої гілки
11. `Telegram: Send Message` — уніфікований вихідний нод (підтримує markdown)
12. `Telegram: Send Document` — для PDF/файлів у відповідь
13. `Postgres: Log Request` — кожен запит логується в таблицю `agent_request_log`

---

## ВОРКФЛОУ 2: EVA-DAILY-BRIEFING-ORCHESTRATOR
**Тригер:** Cron `0 7 * * *` (7:00 ранку щоденно, Kyiv UTC+3)
**Призначення:** Зібрати ранковий брифінг для Андрія від усіх агентів і надіслати структурованим повідомленням у Telegram.

```
[Cron 07:00]
        │
        ▼
[Parallel HTTP Requests — всі агенти одночасно]
    ├── HTTP POST eva:8001/morning_data     → {schedule, tasks, alerts}
    ├── HTTP POST fin:8004/morning_data     → {balance, runway, alerts}
    ├── HTTP POST sam:8006/morning_data     → {market_snapshot, positions}
    ├── HTTP POST doc:8005/morning_data     → {health_metrics, plan}
    └── HTTP POST marshal:8002/morning_data → {security_status, incidents}
        │
        ▼
[Merge Node — зібрати всі відповіді]
        │
        ▼
[HTTP POST eva:8001/compose_briefing] ← Єва синтезує в читаємий брифінг
        │
        ▼
[OpenWeatherMap API] → Погода Дніпра (поточна + прогноз на день)
        │
        ▼
[Merge] → Єдиний payload
        │
        ▼
[Telegram: Send Rich Message] → Форматований брифінг до 07:05
```

**Структура брифінгу (приклад):**
```
☀️ ДОБРОГО РАНКУ, АНДРІЮ!
━━━━━━━━━━━━━━━━━━━━━━
🌤️ Дніпро: +18°C, ясно
━━━━━━━━━━━━━━━━━━━━━━
📅 СЬОГОДНІ: 3 зустрічі, дедлайн по проекту X о 17:00
💰 ФІН: Рахунок ПриватБанк — 24,300 грн | Runway: 47 днів
📈 СЕМ: EURUSD 1.0872 (+0.12%) | BTC 58,400 (+2.1%)
🩺 ДОК: Тренування о 18:30 (спина + ноги) | Вода сьогодні: 2.1л
🛡️ МАРШАЛ: Все чисто, 0 інцидентів
━━━━━━━━━━━━━━━━━━━━━━
[🔍 Детальний звіт] [📋 Задачі дня]
```

---

## ВОРКФЛОУ 3: EVA-HITL-ACTION-GATE
**Тригер:** Internal Webhook від будь-якого агента (POST `/hitl/request`)
**Призначення:** Будь-яка дія Синдикату, що вимагає підтвердження Андрія (HITL = Human-in-the-Loop), проходить через цей воркфлоу.

```
[Internal Webhook: /hitl/request]
        │
        ├── payload: {agent, action_type, details, risk_level}
        │
        ▼
[Switch: Risk Level]
    ├── LOW    → Telegram inline кнопки [✅ Дозволити] [❌ Скасувати]
    ├── MEDIUM → Telegram повідомлення + 30-хвилинний таймаут
    └── HIGH   → Telegram + GSM дзвінок (через EVA-VOICE-CALL-DISPATCHER)
        │
        ▼
[Wait for Telegram Callback] ← Андрій натискає кнопку
        │
        ├── APPROVED → [HTTP POST: Agent /execute_action {action_id}]
        └── REJECTED → [HTTP POST: Agent /cancel_action {action_id}]
        │
        ▼
[Telegram: Підтвердження виконання]
[Postgres: Audit Log запис]
```

---

## ВОРКФЛОУ 4: EVA-NOTEBOOKLM-ARCHIVE-SYNC
**Тригер:** Cron `0 2 * * *` (02:00 нічний синк) + ручний тригер
**Призначення:** Автоматична синхронізація нових даних з усіх агентів у відповідні блокноти АРХІВУ (NotebookLM / Gemini Notebook).

```
[Cron 02:00]
        │
        ▼
[HTTP GET: Eva /archive_queue] ← Черга нових матеріалів для завантаження
        │
        ▼
[Loop Over Items]
    ├── [Switch: Notebook Target]
    │       ├── EVA_STRATEGIC_HQ  → Eva content
    │       ├── TAX_BILLS_ARCHIVE → Fin content (PDF чеки/виписки)
    │       ├── ANDRII_MEDICAL_VAULT → Doc content (аналізи, протоколи)
    │       ├── MACRO_COT_RESEARCH → Sam content (звіти COT/macro)
    │       ├── SYSTEM_ARCHITECTURE → Architect content (design docs)
    │       └── CVE_RADAR → Marshal content (логи безпеки)
    │
    ├── [HTTP POST: Google Drive Upload] ← Завантажити джерело на Drive
    │
    ├── [Browser-Use: NotebookLM Add Source] ← Автоматично додати у блокнот
    │
    └── [Postgres: Sync Log запис]
        │
        ▼
[Telegram: Звіт синку в 02:10] → "📚 АРХІВ: +12 документів, всі блокноти актуальні"
```

---

## ВОРКФЛОУ 5: EVA-VOICE-CALL-DISPATCHER
**Тригер:** Internal Webhook від Єви або HITL Gate (HIGH risk)
**Призначення:** Ініціювати голосовий дзвінок Андрію через найдоступніший канал.

```
[Internal Webhook: /call/initiate]
        │
        ├── payload: {reason, priority, message_tts}
        │
        ▼
[HTTP POST: ElevenLabs TTS] ← Генерація голосового повідомлення Єви
        │
        ▼
[Switch: Call Priority]
    ├── CRITICAL → Twilio/Telnyx GSM Call → Read TTS message
    ├── HIGH     → Telegram VoIP (Pyrogram) → Voice note
    └── MEDIUM   → WhatsApp Cloud API → Voice note
        │
        ▼
[Wait 30s: Did Andrii answer?]
    ├── YES → [Postgres: Call Log — answered]
    └── NO  → [Telegram: Text fallback message] → [Postgres: Call Log — missed]
```

---

## ВОРКФЛОУ 6: EVA-NAVIGATOR-AND-HOTELS
**Тригер:** Telegram — запит на навігацію або бронювання
**Призначення:** Побудова маршруту, пошук готелів/ресторанів/аптек поблизу.

```
[EVA-GATEWAY-INBOUND → geo_lookup гілка]
        │
        ├── [Telegram: Request Live Location] ← Якщо немає локації
        │
        ▼
[HTTP POST: Eva /geo_lookup]
    ├── Google Maps MCP → Пошук поруч (POI, маршрут, час у дорозі)
    ├── EasyWay API → Громадський транспорт (якщо потрібно)
    ├── Uklon API → Вартість таксі
    └── Booking.com RapidAPI → Готелі (якщо запит на нічліг)
        │
        ▼
[Switch: Request Type]
    ├── transport → Telegram: розклад + час прибуття
    ├── taxi      → Telegram: кнопка [Відкрити Uklon] + орієнтовна ціна
    ├── hotel     → Telegram: 3 кращих варіанти + [Відкрити Booking]
    └── map       → Telegram: Organic Maps deeplink + Google Maps link
```

---

## ВОРКФЛОУ 7: EVA-SMART-SCANNER
**Тригер:** Photo у Telegram (тип photo або document з PDF розширенням)
**Призначення:** Автоматична обробка фото документів у стерильний архівний PDF.

```
[EVA-GATEWAY-INBOUND → photo гілка]
        │
        ▼
[Telegram: Download File] ← Завантажити фото з Telegram CDN
        │
        ▼
[HTTP POST: Eva /scan_document]
    │
    ├── OpenCV: Detect contours → Perspective correction → Denoise
    ├── Tesseract OCR: Extract text (uk + ru + en)
    ├── ReportLab: Create searchable PDF
    └── Optional: GPT-4o Vision → Document type detection
        │
        ▼
[Switch: Document Type] ← Авто-розпізнавання
    ├── passport     → [ARCHIVE: ANDRII_PERSONAL_DOCS] + [Telegram: Passport_Andrii.pdf]
    ├── invoice      → [HTTP POST: fin:8004/record_invoice] + [Telegram: PDF]
    ├── medical      → [HTTP POST: doc:8005/process_medical] + [ARCHIVE: ANDRII_MEDICAL_VAULT]
    ├── receipt      → [HTTP POST: fin:8004/record_receipt] + [Telegram: Підтвердження]
    └── other        → [ARCHIVE: MISC_DOCS] + [Telegram: PDF + OCR текст]
```

---

## ВОРКФЛОУ 8: EVA-CANVA-CREATIVE-SUITE
**Тригер:** Команда Андрія: "зроби презентацію", "намалюй майндмеп", "підготуй інфографіку"
**Призначення:** Генерація візуального контенту через Canva або Mermaid.js.

```
[EVA-GATEWAY-INBOUND → creative request]
        │
        ▼
[HTTP POST: Eva /creative_request]
    │
    ├── NLP: Визначити тип контенту
    │       ├── mindmap       → Mermaid.js mindmap → Markmap HTML → PNG Export
    │       ├── presentation  → [Canva API: Шаблон + Data] → PDF посилання
    │       ├── infographic   → [Canva API: Дизайн] → PNG/PDF
    │       └── brainstorm    → [Eva LLM: Генерація ідей] → Mermaid mindmap
    │
    ├── [If Canva]: Browser-Use → Авторизація → Шаблон → Наповнення → Publish
    │
    └── [If Mermaid]: Render → Convert PNG → Upload to Drive
        │
        ▼
[Telegram: Send Image/PDF + Посилання на Canva для редагування]
[ARCHIVE: Зберегти у EVA_STRATEGIC_HQ з міткою [CREATIVE]]
```

---

## ПІДСУМКОВА ТАБЛИЦЯ ВОРКФЛОУ ЄВИ

| # | Назва | Тригер | Час виконання | Агенти |
| :-- | :--- | :--- | :--- | :--- |
| 1 | EVA-GATEWAY-INBOUND | Telegram Webhook (будь-яке повідомлення) | < 3 сек | Eva |
| 2 | EVA-DAILY-BRIEFING-ORCHESTRATOR | Cron 07:00 | < 60 сек | Eva + Fin + Sam + Doc + Marshal |
| 3 | EVA-HITL-ACTION-GATE | Internal Webhook | < 5 сек | Eva + будь-який агент |
| 4 | EVA-NOTEBOOKLM-ARCHIVE-SYNC | Cron 02:00 | < 10 хв | Eva + всі агенти |
| 5 | EVA-VOICE-CALL-DISPATCHER | Internal Webhook | < 10 сек | Eva + ElevenLabs + Twilio |
| 6 | EVA-NAVIGATOR-AND-HOTELS | Telegram (geo запит) | < 5 сек | Eva + Google Maps + Uklon |
| 7 | EVA-SMART-SCANNER | Telegram (photo) | < 15 сек | Eva + OpenCV + Tesseract |
| 8 | EVA-CANVA-CREATIVE-SUITE | Telegram (creative request) | < 30 сек | Eva + Canva/Mermaid |
