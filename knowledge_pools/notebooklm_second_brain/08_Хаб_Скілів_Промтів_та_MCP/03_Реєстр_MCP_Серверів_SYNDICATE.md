---
title: "03_Реєстр_MCP_Серверів_SYNDICATE"
category: "obsidian_mcp_hub"
access: "READ_ALL_18_AGENTS | WRITE_VIA_KODEX_AND_ANDRII_APPROVAL"
tags: ["syndicate", "mcp-hub", "obsidian-mirror", "omnichannel-bridges", "whatsapp", "signal", "threema", "matrix"]
---

# 🔌 Загальний Хаб MCP-Серверів та Резервних Шлюзів Зв'язку SYNDICATE (18,789 серверів у пулі)

> **Принцип роботи:** Усі 18 агентів мають доступ до каталогу MCP-серверів у Markdown-форматі в Obsidian та на сервері (`mcp_servers/`).
> Підключення будь-якого нового зовнішнього MCP-сервера чи сервісу в бойовий контейнер `Hermes` відбувається **виключно через погодження Андрія** (разом із Євою або після особистої Live-розмови з агентом) та перевірку `Маршала`.

---

## 📡 Мульти-Месенджерні MCP-Шлюзи та Антиблокувальний Каскад Дзвінків Єви (`EvaResilientCallCascade`)

На випадок, коли **мобільна мережа (GSM) вимкнена**, а **Telegram заблокований або глушиться**, у системі прописані резервні інтернет-шлюзи та 5-рівневий каскад дозвону Єви до Андрія:

1. **Рівень 1 — Telegram (`mcp-telegram-mtproto-and-bot`):**
   - Текстові чати 18 ботів, звуковий будильник та VoIP-дзвінок у Telegram (через MTProto-акаунт Єви).
2. **Рівень 2 — Мобільний GSM-дзвінок (`livekit-sip -> Twilio / Zadarma`):**
   - Якщо мобільна мережа активна, Єва телефонує на звичайний мобільний номер Андрія.
3. **Рівень 3 — Суверенний Інтернет-Дзвінок SIP-over-TLS:443 (`Linphone / Groundwire -> sip.syndicateholding.com:443`):**
   - **Головний резервний канал, який неможливо заблокувати!** На смартфоні Андрія стоїть додаток `Linphone` або `Groundwire`, підключений напряму до нашого сервера `sip.syndicateholding.com` через порт `443` (трафік виглядає як звичайний HTTPS-сайт).
   - Коли немає мобільної мережі і лежить Telegram, Єва дзвонить через Wi-Fi / Starlink прямо в `Linphone` — телефон прокидається через Apple/Google Push і дзвонить як звичайний телефон!
4. **Рівень 4 — Суверенний Matrix / Element Call + Власний PWA-додаток (`chat.syndicateholding.com`):**
   - Власний закритий месенджер і голосовий сервер на нашому домені `syndicateholding.com`. Оскільки це наш приватний домен, жодні блокування публічних месенджерів на нього не діють.
5. **Рівень 5 — Шлюзи WhatsApp, Signal та Threema (`mcp-whatsapp`, `mcp-signal-cli`, `mcp-threema-gateway`):**
   - **WhatsApp (`mcp-whatsapp-baileys-cloud-api`):** інтернет-дзвінки та повідомлення через WhatsApp.
   - **Signal (`mcp-signal-cli-rest-api`):** офіційний Docker-шлюз для наскрізно шифрованих повідомлень і голосових файлів у Signal.
   - **Threema (`mcp-threema-gateway-e2ee`):** офіційний API-шлюз `Threema Gateway` (`gateway.threema.ch`) з повним E2EE-шифруванням.
