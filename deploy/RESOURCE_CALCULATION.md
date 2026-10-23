# SYNDICATE — Розрахунок потужностей та Чек-лист купівлі Contabo Cloud VPS 12
> **Сервер:** Contabo Cloud VPS 12 — 12 vCPU / 48 GB RAM / 400 GB NVMe SSD / 800 Mbit/s (24 €/міс)  
> **Корпоративний домен холдингу (КРОК №1 ПЕРЕД РОЗГОРТАННЯМ):** `syndicateholding.com`  
> **Режим розгортання:** Повна екосистема одразу (всі 18 агентів + стек `LiveKit + Silero VAD + Kokoro-82M` + `Obsidian Second Brain`)

---

## 0. НАГАДУВАННЯ ПЕРЕД РОЗГОРТАННЯМ ТА ПАКЕТ CONTABO VPS 12

> [!IMPORTANT]
> **Крок 0 (До запуску `server_bootstrap.sh`):** Першим кроком необхідно придбати домен **`syndicateholding.com`** (на Cloudflare Registrar або Namecheap). На нього підв'язуються:
> - Субдомен **`voice.syndicateholding.com`** (обов'язковий SSL/TLS сертифікат для роботи мікрофона через браузер/телефон у `LiveKit WebRTC`).
> - Корпоративні пошти та ізольований технічний Google-акаунт (`kodex-bot@syndicateholding.com`) для безпечної ротації токенів `Google NotebookLM` (`--master-token`).

### Що обрати в кошику Contabo для Cloud VPS 12 (24 €/міс):
1. **Регіон:** `European Union (Germany)` (мінімальний пінг `25–35 мс` з України для живого голосу WebRTC без затримок).
2. **Сховище:** `400 GB SSD (Free)` — повністю вистачає на роки вперед (база Obsidian у 100 000+ нотаток займає лише ~5–15 ГБ).
3. **Образ ОС:** `Ubuntu 24.04 LTS` (чиста система, без платних панелей Plesk/cPanel).
4. **Мережа:** 1× IPv4 (включено безкоштовно), Private Networking — не потрібно (`0 €`), Add-ons / Backups — не потрібно (`0 €`, бекапи робить наш скрипт + 3 вбудовані Snapshots безкоштовно).

---

## 1. ПОВНИЙ КАТАЛОГ КОНТЕЙНЕРІВ (Інфраструктура + Агенти + Голос + Second Brain)

### Група A — Базова Інфраструктура та Сховище Знань (7 контейнерів)
| Контейнер | Image | RAM типова | RAM пік | vCPU | SSD |
|:---|:---|---:|---:|---:|---:|
| `postgres` (+ pgvector HNSW) | `pgvector/pgvector:pg16` | 3.0 GB | 6.0 GB | 2.0 | 50 GB |
| `redis` | `redis:7-alpine` | 0.5 GB | 2.0 GB | 0.3 | 5 GB |
| `vault` (production) | `hashicorp/vault:1.15` | 0.5 GB | 0.5 GB | 0.3 | 2 GB |
| `n8n` | `n8nio/n8n:1.68.0` | 1.0 GB | 2.0 GB | 1.0 | 10 GB |
| `obsidian-syncthing` | `lscr.io/linuxserver/syncthing` | 0.2 GB | 0.5 GB | 0.3 | 15 GB |
| `nginx` | `nginx:1.25-alpine` | 0.1 GB | 0.3 GB | 0.2 | 1 GB |
| OS + Docker daemon | — | 2.0 GB | 3.0 GB | 0.5 | 20 GB |
| **Підсумок A** | | **7.3 GB** | **14.3 GB** | **4.6** | **103 GB** |

### Група B — Агенти Холдингу (18 агентів: Ядро + Директори)
| Контейнер / Кластер | Модель | RAM типова | RAM пік | vCPU |
|:---|:---|---:|---:|---:|
| `eva` (Chief of Staff) | Claude Sonnet / Gemini Pro + Orchestrator | 2.0 GB | 4.0 GB | 1.5 |
| `kira` (Academy, Psychotherapist & English Coach) | Gemini 2.5 Flash / Pro + LiveKit Bridge | 0.8 GB | 1.5 GB | 1.0 |
| `marshal` (Zero-Trust Security) | Claude Haiku + ML inference | 2.0 GB | 3.0 GB | 1.0 |
| `architect`, `fin`, `doc`, `sam`, `kodex`, `alice` | API + LangGraph / SDK Workers | 2.5 GB | 4.5 GB | 2.0 |
| Комерційне крило (`oscar`, `tyler`, `jack`, `ray`, `dex`, `atlas`, `trainer`, `scout`, `sonar`) | Event-driven Workers | 1.5 GB | 3.0 GB | 1.5 |
| **Підсумок B** | | **8.8 GB** | **16.0 GB** | **7.0** |

### Група C — Безпека (Маршал — окремі процеси)
| Сервіс | Тип | RAM типова | RAM пік | vCPU |
|:---|:---|---:|---:|---:|
| `falco` + `tetragon` + `suricata` + `clamav` | Runtime eBPF + IDS + AV | 1.2 GB | 2.0 GB | 1.0 |
| `llm-guard` + `sentyr-ml` | LLM scanner + Isolation Forest | 1.0 GB | 2.0 GB | 1.0 |
| **Підсумок C** | | **2.2 GB** | **4.0 GB** | **2.0** |

### Група D — Локальний Голосовий Стек ($0.00 токенів) та AI-Compute 🎙️
| Компонент | Технологія | RAM типова | RAM пік | vCPU | Примітка |
|:---|:---|---:|---:|---:|:---|
| `livekit-server` | WebRTC SFU (`7880-7882`) + `Silero VAD v5` | 0.2 GB | 0.5 GB | 0.5 | Миттєвий Barge-in `<30 мс` |
| `whisper` (STT) | `faster-whisper large-v3-int8` | 2.5 GB | 3.5 GB | 2.0 | Розпізнавання UA/EN на CPU |
| `kokoro-tts` (18 голосів) | `Kokoro-82M` ONNX + Voice Blending | 0.6 GB | 1.2 GB | 1.5 | 5–10x швидше реального часу на CPU |
| `voice-cloner` (On-demand) | `F5-TTS` / `XTTS-v2` Zero-Shot Clone | 0.5 GB | 2.5 GB | 1.5 | Клонування голосу Андрія та референсів |
| `pronunciation-coach` | `Wav2Vec2-GOP` / IPA Phoneme Scorer | 0.8 GB | 1.5 GB | 1.0 | Акустична оцінка вимови для Кіри |
| `embeddings` + `browser-use` | `BAAI/bge-m3` + Headless Chromium | 2.5 GB | 4.0 GB | 2.0 | 3-Tier Hybrid Memory (Late Chunking) |
| **Підсумок D** | | **7.1 GB** | **13.2 GB** | **8.5** | Голосові моделі працюють лише під час розмови |

---

## 2. ЗВЕДЕНИЙ БАЛАНС РЕСУРСІВ CONTABO CLOUD VPS 12 (12 vCPU / 48 GB RAM / 400 GB SSD)

| Метрика | Фактичне споживання | Доступно на VPS 12 | Оцінка та Запас |
|:---|:---|:---|:---|
| **RAM (типова 24/7)** | **~25.4 GB** | **48.0 GB** | ✅ **+22.6 GB вільно** (під кеш БД та миттєвий відгук) |
| **RAM (пікова — всі системи + голос)** | **~37.5 GB** | **48.0 GB** | ✅ **+10.5 GB запас** (жодних OOM-падінь) |
| **vCPU (типова / голосова сесія)** | **6–9 ядер** | **12 ядер** | ✅ Затримка голосу Кіри/Єви `<300 мс` без GPU |
| **SSD (400 GB NVMe/SSD)** | **~235 GB за рік** | **400.0 GB** | ✅ **~165 GB вільно** (включаючи 100 000+ нотаток Obsidian та всі голосові моделі) |
