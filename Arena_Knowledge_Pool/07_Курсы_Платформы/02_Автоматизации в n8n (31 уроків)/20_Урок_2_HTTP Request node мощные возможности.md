---
title: "Урок 20: HTTP Request node: работа с кастомными API"
course: "Автоматизация с n8n"
lesson_number: 20
module_number: 6
video_url: "https://vimeo.com/1167925426"
tags:
  - lesson
  - course_n8n
  - n8n_automation
  - ai_agents
  - module_6
---

# 🎬 Урок 20: HTTP Request node: работа с кастомными API

> **Курс:** [[07_Курсы_Платформы/02_Автоматизация с n8n (31 урок)/00_Оглавление_Курса_Автоматизация с n8n|Автоматизация с n8n]]  
> **Модуль:** `6` | **Урок:** `20`  
> **Ссылка на HD-видео:** [https://vimeo.com/1167925426](https://vimeo.com/1167925426)

---

### 🎯 Цель урока:
Подключение любого веб-сервиса мира, даже если для него нет нативного узла в каталоге n8n.

### 🛠 Ключевые узлы n8n:
- `HTTP Request`
- `Crypto Node`

---

## 📖 Подробный конспект и теоретическая база:
HTTP Request — самый универсальный узел n8n. Он поддерживает все методы (GET, POST, PUT, PATCH, DELETE), любые типы авторизации (Bearer, Basic, OAuth2, Custom Header, HMAC signature) и прямую передачу бинарных файлов (multipart/form-data).

---

## ⚙️ Пошаговый сценарий настройки в n8n:
1. Изучение документации любого стороннего сервиса (например, CRM или платежного шлюза).
2. Настройка заголовков авторизации: `Authorization: Bearer {{ $credentials.apiKey }}`.
3. Генерация HMAC SHA-256 подписи запроса через узел Crypto для защищенных банковских API.

---

## 💻 Примеры кода, JSON и конфигурации:
```json
Method: POST
URL: https://api.stripe.com/v1/payment_intents
Authentication: Generic Credential Type (Header Auth)
Body Parameters:
- amount: {{ $json.price * 100 }}
- currency: 'usd'
```

---

## 💡 Практические рекомендации и инсайты:
> [!TIP]
> Включайте флаг 'Ignore SSL Issues' только в тестовом окружении, на продакшене сертификаты должны быть валидными.

---
*Материал оцифрован и структурирован для интеграции в базу знаний и AI Arena Pool.*
