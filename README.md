# 🌐 EVA SYNDICATE

> **Sovereign Autonomous Multi-Agent AI Ecosystem**  
> **Засновник та Командир:** Андрій (Ветеран, Військовий)  
> **Генеральний Директор (CEO):** ЄВА (E.V.A.)  
> **Економічний Закон:** ROI x3+ | Стек: LangGraph + Hermes + N8N  
> **Інфраструктура:** Contabo Cloud VPS 12 (48 GB RAM / 12 vCPU / Франкфурт)

---

## 🏛️ Бойовий Склад Синдикату (6 Активних Агентів)

| Агент | Роль | Модель ШІ | Призначення |
| :--- | :--- | :--- | :--- |
| **👑 ЄВА (E.V.A.)** | CEO & Права рука | Claude 3.5 Sonnet + Haiku | Стратег, оркестратор, мобільний хаб, ранкові/вечірні брифінги. Бот: `@eva_syndicate_bot` |
| **🛡️ МАРШАЛ (MARSHAL)** | Head of Security | Claude 3.5 Haiku + Python Gate | 9 рівнів захисту, Vault, eBPF Tetragon, Soft Anomaly Protocol. Бот: `@marshal_security_bot` |
| **🏛️ АРХІТЕКТОР (ARCHITECT)** | CTO & Головний Інженер | Google Gemini Flash + Sonnet | Моніторинг заліза 24/7, воркфлоу N8N, Shadow Staging, Auto-Rollback. Бот: `@architect_infra_bot` |
| **💰 ФІН (FIN)** | CFO & Казначей | Gemini Flash + LangGraph | Бухгалтерія hledger, аудит кошиків, runway, банки Read-Only, скарбнички |
| **🩺 ДОК (DOC)** | Chief Health & Fitness | Gemini Flash + Claude Sonnet | Доказова медицина (Cochrane/PubMed), тренування, аналізи OCR. Бот: `@doc_health_bot` |
| **📈 СЕМ (SAM)** | Chief Investment & Trading (CIO) | Nous Hermes 3 + Groq / Gemini | Квант-трейдинг (MT5), інвестиції (IBKR), крипта (CCXT), HITL-контроль. Бот: `@sam_quant_bot` |

---

## 📁 Структура Репозиторію

```
eva-syndicate/
├── README.md                          # Головний опис системи
├── SYNDICATE_STRUCTURE_MANIFEST.md    # Повний архітектурний маніфест проекту
├── SYNDICATE_AIP.md                   # Кодекс ініціативності агентів
├── implementation_plan.md             # Технічний план реалізації та безпеки
├── PRE_LAUNCH_AUDIT.md                # Передстартовий аудит та лог виправлень
├── eva_core/                          # Ядро ЄВИ
│   ├── EVA_CORE_PERSONA.md            # Особистість, філософія, режими
│   ├── eva_runtime_prompt.md          # Системний промпт (v1.2)
│   ├── EVA_TOOLKIT_SPEC.md            # Інструменти (Telegram, Whisper, ElevenLabs)
│   └── EVA_DAILY_OPS_PROTOCOL.md      # Добовий операційний цикл
├── marshal_core/                      # Служба безпеки МАРШАЛ
│   └── MARSHAL_FULL_SPEC.md           # 9 рівнів захисту, eBPF, Vault, Kill Switch
├── architect_core/                    # Головний Архітектор & CTO
│   └── ARCHITECT_CTO_SPEC.md          # Моніторинг 24/7, воркфлоу N8N, прийомка
├── fin_core/                          # Фінансовий офіцер ФІН
│   └── FIN_CFO_SPEC.md                # Чеки OCR, hledger, Google Sheets, токени
├── doc_core/                          # Медик і тренер ДОК
│   └── DOC_HEALTH_SPEC.md             # Здоров'я, тренування, R&D Perplexity
├── sam_core/                          # Квантовий трейдер СЕМ (CIO)
│   ├── SAM_QUANT_SPEC.md              # 4 ринки, SMC, Confluence >95%, HITL, 15 скілів
│   └── sam_runtime_prompt.md          # Системний промпт Сема
└── deploy/                            # Інфраструктура та розгортання
    ├── docker-compose.yml             # Full Production Stack (всі 6 агентів + інфра)
    ├── .env.example                   # Шаблон конфігурації секретів
    ├── server_bootstrap.sh            # Скрипт налаштування Ubuntu 24.04
    ├── RESOURCE_CALCULATION.md        # Повний розрахунок RAM/CPU/SSD та 24/7 токенів
    └── scripts/
        └── vault_init.sh              # Shamir 3-of-5 ініціалізація Vault та AppRole
```
