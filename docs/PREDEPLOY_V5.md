# Pre-deploy v5 — порядок розгортання та чесний перелік прогалин

Ціль: `SYNDICATE_HOLDING_ATOMIC_MANIFEST.pdf` v5.0. Сервер: Contabo 169.58.178.154, домен syndicateholding.com.

## Порядок (на сервері, від root)
1. `git clone` (токен лише через `GITHUB_TOKEN=… sudo -E bash deploy/server_bootstrap.sh`; після клону remote без токена).
2. `deploy/server_bootstrap.sh` — Docker, UFW (80/443, 7881/tcp, 7882/udp; Syncthing тільки через `tailscale0`), fail2ban,
   SSH-hardening (лише якщо є authorized_keys), самопідписаний сертифікат-заглушка.
3. `deploy/scripts/setup_ssl.sh` — справжній Let's Encrypt для apex, n8n., voice.
4. Підняти Vault → `deploy/scripts/vault_init.sh` (AppRole на агента, 90 діб SecretID, `operator.token`, `directors.env`)
   → зберегти unseal-ключі офлайн → `deploy/scripts/vault_finalize.sh` (шреддінг `vault-init.json`).
   Авто-unseal за замовчуванням ВИМКНЕНО (`AUTO_UNSEAL=1` + `deploy/systemd/syndicate-vault-unseal.service` — рішення людини).
5. Ключі/боти: `python scripts/syndicate_vault.py set-key|bulk-bots|set-owner|distribute-keys|verify-bots` (секрети через прихований ввід).
6. `docker compose -f docker-compose.yml [-f deploy/docker-compose.directors.yml] [-f deploy/docker-compose.voice.yml] up -d`.
7. Telegram: `POST /admin/telegram/register` (master key) → вебхук кожного з 18 ботів із власним секретом.
8. `python -m tools.check_models` — перевірка ID моделей. Далі `/health`, `/directors`, cockpit.
9. **Ротація:** ключ cockpit/master та токени, що засвітилися в PDF/чатах: `syndicate_vault.py rotate-master`, перевипустити боти/API-ключі.

## Рішення за замовчуванням (змінюються одним рядком)
- Syncthing GUI не публікується (SSH-тунель); синхронізація через Tailscale.
- Окремий Telegram-токен на кожного директора; вебхук-секрет виводиться HMAC-ом від майстер-секрету.
- Оператор — єдиний, хто схвалює CR/HITL; ідентичність фіксується на сервері, не з тіла запиту.
- Anti-detect-профілі відхиляються політикою; AI-контент публікується з розкриттям.

## Що НЕ перевірено в цій сесії
- `nginx -t` та `docker compose config` (немає Docker/nginx у середовищі розробки) — виконати на сервері до `up`.
- Реальні виклики Vault/Telegram/LLM (тести йдуть проти фейків і `httpx.MockTransport`).
- Фактичні назви моделей Gemini/Anthropic — `tools/check_models.py` на сервері з ключами.

## Розбіжності з маніфестом (відомі)
- Контейнеризовано 9 воркерів; решта директорів працюють in-process в `eva-agent`.
- Trifecta-guard — дорадчий, не блокуючий; circuit breaker / token guard / kill-switch у маніфесті — частково
  (lockdown і HITL реалізовані, глобальний бюджетний ліміт токенів — ні).
- Sonar/Atlas/Alice daemon/Pronunciation без живих клієнтів повертають `unavailable` (раніше вигадували дані).
- Kira: детермінований скринінг кризових фраз → фіксована відповідь + сигнал оператору (112). Лінії довіри не додано, бо номери не верифіковано.
- `tools/check.sh` ruff-ворота мають попередні зауваження (було 48/17/7, стало 41/11/7) — не з цієї гілки.
