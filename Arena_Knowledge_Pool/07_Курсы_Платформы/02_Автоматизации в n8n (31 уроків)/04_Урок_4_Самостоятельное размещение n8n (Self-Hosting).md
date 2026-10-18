---
title: "Урок 4: Самостоятельное развертывание n8n (Self-Hosting)"
course: "Автоматизация с n8n"
lesson_number: 4
module_number: 1
video_url: "https://vimeo.com/1169076001"
tags:
  - lesson
  - course_n8n
  - n8n_automation
  - ai_agents
  - module_1
---

# 🎬 Урок 4: Самостоятельное развертывание n8n (Self-Hosting)

> **Курс:** [[07_Курсы_Платформы/02_Автоматизация с n8n (31 урок)/00_Оглавление_Курса_Автоматизация с n8n|Автоматизация с n8n]]  
> **Модуль:** `1` | **Урок:** `4`  
> **Ссылка на HD-видео:** [https://vimeo.com/1169076001](https://vimeo.com/1169076001)

---

### 🎯 Цель урока:
Практическое пошаговое развертывание надежного production-кластера n8n с PostgreSQL.

### 🛠 Ключевые узлы n8n:
- `Docker Compose`
- `Postgres`
- `Redis / Queue Mode`

---

## 📖 Подробный конспект и теоретическая база:
По умолчанию n8n использует SQLite. Для промышленной эксплуатации SQLite не подходит из-за блокировок базы при параллельных вебхуках. Промышленный стек: n8n + PostgreSQL в качестве бэкенд-БД + Redis для масштабирования очередей (Queue Mode).

---

## ⚙️ Пошаговый сценарий настройки в n8n:
1. Подготовка файла docker-compose.yml с сервисами postgres и n8n.
2. Настройка переменных среды: `DB_TYPE=postgresdb`, `DB_POSTGRESDB_DATABASE=n8n`.
3. Настройка регулярного создания резервных копий (бэкап папки workflows и БД pg_dump).

---

## 💻 Примеры кода, JSON и конфигурации:
```json
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: n8n
      POSTGRES_USER: n8n_user
      POSTGRES_PASSWORD: SecretPassword123
    volumes:
      - pg_data:/var/lib/postgresql/data
  n8n:
    image: docker.n8n.io/n8nio/n8n
    depends_on: [postgres]
    environment:
      DB_TYPE: postgresdb
      DB_POSTGRESDB_HOST: postgres
      DB_POSTGRESDB_USER: n8n_user
      DB_POSTGRESDB_PASSWORD: SecretPassword123
```

---

## 💡 Практические рекомендации и инсайты:
> [!TIP]
> Используйте режим Queue Mode с несколькими воркерами (Workers), если ожидается наплыв более 50 вебхуков в секунду.

---
*Материал оцифрован и структурирован для интеграции в базу знаний и AI Arena Pool.*
