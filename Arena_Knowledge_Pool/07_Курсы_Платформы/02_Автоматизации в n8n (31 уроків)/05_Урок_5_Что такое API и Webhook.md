---
title: "Урок 5: Что такое API и Webhook"
course: "Автоматизация с n8n"
lesson_number: 5
module_number: 1
video_url: "https://vimeo.com/1169075896"
tags:
  - lesson
  - course_n8n
  - n8n_automation
  - ai_agents
  - module_1
---

# 🎬 Урок 5: Что такое API и Webhook

> **Курс:** [[07_Курсы_Платформы/02_Автоматизация с n8n (31 урок)/00_Оглавление_Курса_Автоматизация с n8n|Автоматизация с n8n]]  
> **Модуль:** `1` | **Урок:** `5`  
> **Ссылка на HD-видео:** [https://vimeo.com/1169075896](https://vimeo.com/1169075896)

---

### 🎯 Цель урока:
Освоить базовые протоколы взаимодействия современных интернет-сервисов: REST API и Webhooks.

### 🛠 Ключевые узлы n8n:
- `Webhook Trigger`
- `HTTP Request Node`
- `Respond to Webhook`

---

## 📖 Подробный конспект и теоретическая база:
API (Application Programming Interface) — метод активного опроса (*pull*), когда n8n делает запрос к внешнему сервису. Webhook — метод пассивного уведомления (*push*), когда внешний сервис сам мгновенно присылает HTTP POST запрос на URL n8n при наступлении события (например, оплата Stripe или новое сообщение в Telegram).

---

## ⚙️ Пошаговый сценарий настройки в n8n:
1. Создание вебхук-триггера в n8n (разница между Test URL и Production URL).
2. Тестирование вебхука через Postman или curl.
3. Возврат кастомного ответа клиенту через узел 'Respond to Webhook' (код 200 OK, JSON-тело).

---

## 💻 Примеры кода, JSON и конфигурации:
```json
curl -X POST https://n8n.yourdomain.com/webhook/test-endpoint \
  -H 'Content-Type: application/json' \
  -d '{"event":"payment_received", "amount": 99.00, "currency": "USD"}'
```

---

## 💡 Практические рекомендации и инсайты:
> [!TIP]
> В режиме разработки слушайте Test Webhook (он активен только когда открыта кнопка Listen for Test Event). Для фоновой работы обязательно активируйте workflow и используйте Production URL.

---
*Материал оцифрован и структурирован для интеграции в базу знаний и AI Arena Pool.*
