# EVA SYNDICATE — Розрахунок потужностей для повної екосистеми
> **Сервер:** Contabo Cloud VPS 12 — 12 vCPU / 48 GB RAM / 400 GB SSD  
> **Режим розгортання:** Повна екосистема одразу (всі 5 агентів + повна інфраструктура)

---

## 1. ПОВНИЙ КАТАЛОГ КОНТЕЙНЕРІВ (23 процеси)

### Група A — Інфраструктура (6 контейнерів)
| Контейнер | Image | RAM типова | RAM пік | vCPU | SSD |
|:---|:---|---:|---:|---:|---:|
| `postgres` (+ pgvector) | `pgvector/pgvector:pg16` | 3.0 GB | 6.0 GB | 2.0 | 50 GB |
| `redis` | `redis:7.2-alpine` | 0.5 GB | 2.0 GB | 0.3 | 5 GB |
| `vault` (production) | `hashicorp/vault:1.17` | 0.5 GB | 0.5 GB | 0.3 | 2 GB |
| `n8n` | `n8nio/n8n:1.65.x` | 1.0 GB | 2.0 GB | 1.0 | 10 GB |
| `nginx` | `nginx:1.27-alpine` | 0.1 GB | 0.3 GB | 0.2 | 1 GB |
| OS + Docker daemon | — | 2.0 GB | 3.0 GB | 0.5 | 20 GB |
| **Підсумок A** | | **7.1 GB** | **13.8 GB** | **4.3** | **88 GB** |

### Група B — Агенти (5 контейнерів)
| Контейнер | Модель | RAM типова | RAM пік | vCPU |
|:---|:---|---:|---:|---:|
| `eva` | Claude Sonnet (API) + N8N orchestration | 2.0 GB | 4.0 GB | 2.0 |
| `marshal` | Claude Haiku (API) + ML inference | 2.0 GB | 3.0 GB | 1.5 |
| `architect` | Gemini Flash (API) + Claude Sonnet | 0.5 GB | 1.0 GB | 0.5 |
| `fin` | Gemini Flash (API) + LangGraph | 0.5 GB | 1.0 GB | 0.5 |
| `doc` | Gemini Flash (API) + Claude Sonnet | 0.5 GB | 1.0 GB | 0.5 |
| **Підсумок B** | | **5.5 GB** | **10.0 GB** | **5.0** |

> **Примітка:** Усі LLM-виклики — через зовнішні API (Anthropic/Google). Локально зберігається тільки Python-runtime + agent logic + черги задач. Тому RAM агентів відносно мала.

### Група C — Безпека (Маршал — окремі процеси)
| Сервіс | Тип | RAM типова | RAM пік | vCPU |
|:---|:---|---:|---:|---:|
| `falco` | Runtime syscall detector | 0.3 GB | 0.5 GB | 0.3 |
| `tetragon` | eBPF kernel enforcer (on host) | 0.3 GB | 0.5 GB | 0.3 |
| `suricata` | Network IDS | 0.3 GB | 0.5 GB | 0.3 |
| `clamav` | Antivirus daemon | 0.3 GB | 0.5 GB | 0.2 |
| `llm-guard` | Per-request LLM scanner (inside marshal) | 0.5 GB | 1.0 GB | 0.5 |
| `sentyr-ml` | Isolation Forest × 5 агентів | 0.5 GB | 1.0 GB | 0.5 |
| **Підсумок C** | | **2.2 GB** | **4.0 GB** | **2.1** |

### Група D — Compute-важкі компоненти ⚠️
| Компонент | Тип | RAM типова | RAM пік | vCPU | Примітка |
|:---|:---|---:|---:|---:|:---|
| `whisper` (STT) | `faster-whisper` + `large-v3-int8` | 2.5 GB | 3.5 GB | 3.0 | Найвагоміший локальний процес |
| `browser-use` (Playwright) | Headless Chromium × 2 instances | 1.0 GB | 2.5 GB | 2.0 | Пікова при Browser-Use сесії |
| **Підсумок D** | | **3.5 GB** | **6.0 GB** | **5.0** | Пікове навантаження не постійне |

---

## 2. ЗВЕДЕНИЙ БАЛАНС РЕСУРСІВ

```
┌──────────────────────────────────────────────────────────┐
│            CONTABO VPS 12 — БАЛАНС РЕСУРСІВ              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  RAM (48 GB total)                                       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━             │
│  Група A (Інфраструктура):   7.1 GB  ████░░░░░░         │
│  Група B (Агенти):           5.5 GB  ███░░░░░░░         │
│  Група C (Безпека):          2.2 GB  █░░░░░░░░░         │
│  Група D (Compute):          3.5 GB  ██░░░░░░░░         │
│  ─────────────────────────────────────                  │
│  ТИПОВЕ СПОЖИВАННЯ:         18.3 GB  ████████░░         │
│  ПІКОВЕ СПОЖИВАННЯ:         33.8 GB  ██████████████░░░  │
│  ВІЛЬНО (буфер):           ~14 GB    ░░░░░░░░░░░░░░░    │
│                                                          │
│  vCPU (12 total)                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━             │
│  Група A (Інфраструктура):   4.3 vCPU                   │
│  Група B (Агенти):           5.0 vCPU                   │
│  Група C (Безпека):          2.1 vCPU                   │
│  Groupe D (Compute) — пік:   5.0 vCPU (не постійно)    │
│  ─────────────────────────────────────                  │
│  ТИПОВЕ СПОЖИВАННЯ:          ~7 vCPU  ██████░░░░░░      │
│  ПІКОВЕ (Whisper + Browser):  12 vCPU ████████████      │
│  → Рекомендований throttle Whisper до 2 vCPU            │
│                                                          │
│  SSD (400 GB total)                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━             │
│  Docker images (~23 контейнери):    15 GB               │
│  OS + system:                       20 GB               │
│  PostgreSQL data (з ростом):        80 GB (рік)         │
│  Redis AOF + RDB:                    5 GB               │
│  Vault encrypted store:              2 GB               │
│  N8N workflows + logs:              10 GB               │
│  Whisper model (large-v3-int8):      3 GB               │
│  Agent workspaces:                  20 GB               │
│  Audit logs (append-only):          15 GB               │
│  Бекапи (щотижневі):                50 GB               │
│  ─────────────────────────────────────                  │
│  ВИКОРИСТАНО (рік):                220 GB               │
│  ВІЛЬНО:                          ~180 GB               │
└──────────────────────────────────────────────────────────┘
```

---

## 3. КРИТИЧНА ТОЧКА: WHISPER v3 БЕЗ GPU

> Це єдине вузьке місце в екосистемі. Вирішено.

| Варіант | RAM | Швидкість на CPU | Якість | Вартість |
|:---|---:|:---|:---|---:|
| `faster-whisper large-v3` (float16) | 6 GB | 0.5× realtime ❌ | Найкраща | \$0 |
| **`faster-whisper large-v3-int8`** ✅ | **2.5 GB** | **2-3× realtime ✅** | **Чудова** | **\$0** |
| `faster-whisper medium-int8` | 1.2 GB | 5× realtime | Добра | \$0 |
| Groq API Whisper | ~0 | миттєво | Відмінна | \$0.111/год аудіо |
| OpenAI Whisper API | ~0 | миттєво | Відмінна | \$0.006/хв |

**Рішення:** `faster-whisper large-v3-int8` локально. При пікових навантаженнях (одночасно Whisper + Browser-Use) — Whisper обмежений до 2 vCPU через `--threads 2` щоб не вичерпати CPU.

**Fallback:** якщо черга голосових >3 хв → автоматичний switch на Groq API (\$0.111/год).

---

## 4. MEMORY LIMITS ПО КОНТЕЙНЕРАХ (docker-compose)

```yaml
# Ліміти RAM та vCPU для production deployment
postgres:      memory: 6G,  cpus: "2.0"   # Найбільший споживач — page cache
redis:         memory: 2G,  cpus: "0.5"
vault:         memory: 512M, cpus: "0.3"
n8n:           memory: 2G,  cpus: "1.0"
nginx:         memory: 256M, cpus: "0.2"

eva:           memory: 4G,  cpus: "2.0"   # Основний агент
marshal:       memory: 3G,  cpus: "1.5"   # LLM-Guard + Isolation Forest
architect:     memory: 1G,  cpus: "0.5"
fin:           memory: 1G,  cpus: "0.5"
doc:           memory: 1G,  cpus: "0.5"

whisper:       memory: 3G,  cpus: "2.0"   # faster-whisper large-v3-int8
browser-use:   memory: 2G,  cpus: "1.5"   # Playwright headless Chromium × 1

falco:         memory: 512M, cpus: "0.3"
suricata:      memory: 512M, cpus: "0.3"
clamav:        memory: 512M, cpus: "0.2"

# ЗАГАЛОМ виділено: ~28 GB RAM / 12 vCPU
# ЗАПАС: ~20 GB RAM для page cache PostgreSQL та пікових сплесків
```

---

## 5. ВИСНОВОК: CONTABO VPS 12 ДОСТАТНІЙ

| Метрика | Факт | Оцінка |
|:---|:---|:---|
| RAM типова | 18 GB з 48 GB | ✅ Комфортно (залишається 30 GB буфер/page cache) |
| RAM пік | 34 GB з 48 GB | ✅ Достатньо (14 GB запас навіть при піку) |
| vCPU типова | 7 з 12 | ✅ Нормально |
| vCPU пік | 12 з 12 | ⚠️ Saturation при Whisper + Browser + всі агенти одночасно |
| SSD рік | 220 GB з 400 GB | ✅ Достатньо |
| **Вердикт** | **Запускаємо все одразу** | **✅ Сервер тягне** |

**Єдине застереження щодо CPU:** пікове насичення можливе при одночасному запуску: Whisper (3 vCPU) + Browser-Use (1.5 vCPU) + N8N active (1 vCPU) + всі агенти (5 vCPU) = ~11.5 vCPU. Вирішується throttle Whisper до 2 vCPU.

---

## 6. РЕКОМЕНДОВАНА ЧЕРГА ЗАПУСКУ (все одразу, але в правильному порядку)

```
Хвилина 0:    docker compose up -d postgres redis vault nginx
Хвилина 1:    vault_init.sh (Shamir unseal + AppRole + API keys)
Хвилина 5:    docker compose up -d n8n
Хвилина 6:    docker compose up -d whisper clamav suricata falco
Хвилина 8:    docker compose up -d marshal
Хвилина 9:    docker compose up -d eva architect fin doc browser-use
Хвилина 12:   docker compose ps (перевірка всіх healthy)
Хвилина 15:   Перший Telegram /start → ранковий брифінг тест
```

Порядок критичний: Vault → агенти (агенти при старті запитують AppRole token з Vault).
