# SYNDICATE — Pre-Launch Audit & Fix Log
> **Аудит:** 25 вересня 2026 (внутрішній)  
> **Зовнішній аудит:** 27 вересня 2026 (критичний зовнішній огляд)  
> **Статус:** Всі критичні та важливі пункти виправлені

---

## ЗОВНІШНІЙ АУДИТ — РЕЗУЛЬТАТИ ВИПРАВЛЕНЬ

### 🔴 КРИТИЧНІ (блокери для запуску) — всі закриті

| # | Проблема | Статус | Виправлення |
|:--|:---|:---|:---|
| 1 | **Vault в dev-режимі** — незашифрована пам'ять, перезапуск = втрата секретів | ✅ FIXED | `docker-compose.yml v2.0`: dev mode видалено, production mode + Shamir 3-of-5. `deploy/scripts/vault_init.sh` — повний скрипт ініціалізації |
| 2 | **Docker socket у агентах** — container escape через `/var/run/docker.sock` | ✅ FIXED | Socket прибрано з усіх контейнерів. Eva не монтує Docker socket. Управління через Docker API over TLS планується у Phase 2 через окремий sidecar |
| 3 | **Конфлікт номенклатури** — ВЕКТОР vs АРХІТЕКТОР, ШЕРИФ vs МАРШАЛ | ✅ FIXED | `vector_core/VECTOR_CTO_SPEC.md` видалено (через sync скрипт). Єдина номенклатура: МАРШАЛ + АРХІТЕКТОР у всіх файлах |
| 4 | **"Amigo" суперечність** у runtime prompt vs persona | ✅ FIXED | `eva_runtime_prompt.md v1.2`: Amigo видалено, правильні ADDRESS RULES додано |

### 🟠 ВАЖЛИВІ (до першого deploy) — всі закриті

| # | Проблема | Статус | Виправлення |
|:--|:---|:---|:---|
| 5 | **N8N порт 5678 відкритий напряму** (`ports:` замість `expose:`) | ✅ FIXED | `docker-compose.yml v2.0`: `ports:` → `expose:`. N8N тільки через Nginx |
| 6 | **UFW без NTP** — дрейф годинника → JWT відхилення | ✅ FIXED | `MARSHAL_FULL_SPEC.md`: додано `ufw allow out 123/udp comment "NTP"` з поясненням ризику |
| 7 | **AOF ≠ шифрування Redis** — технічна неточність | ✅ FIXED | `implementation_plan.md`: AOF описано як формат персистентності. Шифрування at-rest = LUKS на volume хоста |
| 8 | **pg_crypto ≠ full-disk шифрування PostgreSQL** — технічна неточність | ✅ FIXED | `implementation_plan.md`: pg_crypto = шифрування окремих полів. Full at-rest = LUKS на `/data/postgres` volume |
| 8b | **Signal Protocol** у Telegram ботів — неможливо | ✅ FIXED | `implementation_plan.md`: MTProto + TLS. Боти не підтримують e2e. Signal CLI як опція Phase 3 |

### 🟡 СИСТЕМНІ — всі закриті або прийняті рішення

| # | Проблема | Статус | Рішення |
|:--|:---|:---|:---|
| 9 | **Supabase vs PostgreSQL** — дублювання або хаос | ✅ FIXED | `SYNDICATE_STRUCTURE_MANIFEST.md`: чітке розділення. Phase 1 = тільки self-hosted Postgres. Supabase = опціональне дзеркало у Phase 2 |
| 10 | **Dreaming loop** — вектор отруєння пам'яті | ✅ FIXED | `MARSHAL_FULL_SPEC.md` + `implementation_plan.md`: `TIER_2_DREAMING` сегмент пам'яті з провенанс-тегами, конфліктною перевіркою vs TIER_1, 30-денним expire, забороною auto-promote |
| 11 | **Бюджет $100-150 vs 20+ контейнерів** | ✅ FIXED | `docker-compose.yml v2.0`: Phase 1 = 3 активних агенти (EVA + MARSHAL sidecar + ARCHITECT on-demand). FIN та DOC = N8N workflows у Phase 1 |
| 12 | **eva_runtime_prompt.md занадто мінімальний** | ✅ FIXED | `eva_runtime_prompt.md v1.2`: розширено до повного production-ready промпту: HITL gates, delegation rules, memory protocol, Phase 1 scope, context slots |
| 13 | **Confreimation: Sherif vs Marshal** | ✅ FIXED | Номенклатура уніфікована: тільки МАРШАЛ. Конфлікт файлів вирішено |

---

## ПОТОЧНА ГОТОВНІСТЬ СИСТЕМИ (після виправлень)

| Компонент | Специфікація | Deployment-файли | Готовність |
|:---|:---|:---|:---|
| 👑 ЄВА | ✅ 100% | ✅ docker-compose.yml | **80%** |
| 🛡️ МАРШАЛ | ✅ 100% | ✅ docker-compose (sidecar) | **75%** |
| 🏛️ АРХІТЕКТОР | ✅ 100% | ✅ on-demand через N8N | **70%** |
| 💰 ФІН | ✅ 100% | N8N workflow Phase 1 | **60%** |
| 🩺 ДОК | ✅ 100% | N8N workflow Phase 1 | **60%** |
| 🐳 Інфраструктура | ✅ 100% | ✅ docker-compose + bootstrap + vault_init | **85%** |

> **Що залишається до першого запуску:**  
> 1. IP-адреса Contabo VPS від Андрія  
> 2. Telegram Bot Token для `@syndicate_bot`<br>
> 3. API ключі (Anthropic, Gemini, Nova Poshta)  
> 4. SSH підключення → `server_bootstrap.sh` → `vault_init.sh`  
> 5. Перший N8N workflow (ранковий брифінг)

---

## НОВІ ФАЙЛИ СТВОРЕНІ В ЦІЙ СЕСІЇ

| Файл | Що робить |
|:---|:---|
| `deploy/docker-compose.yml` v2.0 | Production-ready stack: Postgres+pgvector, Redis, Vault (prod mode), N8N (expose, не ports), Nginx, Eva |
| `deploy/.env.example` | Шаблон всіх секретів з чіткими інструкціями що йде у Vault |
| `deploy/server_bootstrap.sh` | Підготовка Ubuntu 24.04 LTS: Docker, UFW, Fail2ban, SSH hardening, директорії |
| `deploy/scripts/vault_init.sh` | Shamir 3-of-5 unsealing, AppRole для кожного агента, завантаження API ключів |
| `eva_core/eva_runtime_prompt.md` v1.2 | Повний production system prompt з HITL, delegation, memory protocol |

---

## ЗАЛІЗНІ ПРАВИЛА (незмінні)

| Правило | Деталь |
|:---|:---|
| Vault: тільки production mode | Shamir 3-of-5. Unseal keys = USB Андрія офлайн |
| Жодного Docker socket у агентів | container escape = миттєвий root на хості |
| N8N: тільки через Nginx | Жодних відкритих портів напряму |
| NTP: завжди відкритий 123/udp | JWT TTL 15хв = критична залежність від точного часу |
| Dreaming: TIER_2 не замінює TIER_1 | Провенанс-тегування + 30-денний expire |
| Оплата: тільки ручний клік Андрія | Нуль автоплатежів |
| Email: тільки DRAFT | Жодного автовідправлення |
| Дія/Армія+: Zero Trust | Авто-вхід ШІ заборонено |
