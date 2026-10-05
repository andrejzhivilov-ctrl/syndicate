# DEPLOYMENT RUNBOOK — EVA SYNDICATE

Покроковий посібник із розгортання суверенної, автономної, security-first мультиагентної системи **EVA SYNDICATE** на Contabo VPS (Ubuntu 24.04 LTS).

> Усі команди виконуються на **чистому** сервері Ubuntu 24.04 LTS від імені користувача з правами `sudo`. Замініть `your-domain.com` на ваш реальний домен.

---

## 0. Архітектура (короткий огляд)

| Сервіс | Образ | Внутрішній порт | Публічний | UID |
|--------|-------|------------------|-----------|-----|
| nginx | nginx:1.25-alpine | 80/443 | ✅ 80, 443 | root+NET_BIND |
| eva-agent | build docker/Dockerfile.agent | 8000 | ❌ (через nginx) | 1001 |
| n8n | n8nio/n8n:latest | 5678 | ❌ (через nginx /n8n/) | 1000 |
| postgres | pgvector/pgvector:pg16 | 5432 | ❌ | 999 |
| redis | redis:7-alpine | 6379 | ❌ | 999 |
| vault | hashicorp/vault:1.15 | 8200 | лише 127.0.0.1 | 100 |

- Мережі: `backend` (`internal: true`) — усі сервіси; `frontend` — лише nginx та n8n. Тільки nginx мостить обидві.
- Принципи: Zero-Trust, Least Privilege, non-root, read-only rootfs, cap_drop ALL, без docker.sock, без хардкод-секретів.

---

## 1. Підготовка сервера (bootstrap)

### 1.1. Отримати код на сервер

```bash
sudo mkdir -p /opt/eva
sudo chown "$USER":"$USER" /opt/eva
cd /opt/eva
git clone https://github.com/andrejzhivilov-ctrl/eva-syndicate.git .
git checkout feature/complete-system-implementation
```

### 1.2. Запустити bootstrap-скрипт (від root)

Скрипт встановлює Docker, створює системного користувача `syndicate` (UID 1001), готує каталоги `/data/*` з коректними правами, налаштовує firewall (UFW), fail2ban, sysctl-зміцнення та автоматичні security-оновлення.

```bash
sudo bash deploy/scripts/server_bootstrap.sh
```

Перевірка після виконання:

```bash
docker --version
sudo ufw status verbose        # має бути deny 8200/5432/6379/5678, allow 22/80/443
ls -ld /data/postgres /data/redis /data/vault /data/n8n
```

---

## 2. Налаштування секретів (.env)

### 2.1. Створити `.env` із шаблону

```bash
cd /opt/eva
cp .env.example .env
chmod 600 .env
```

### 2.2. Згенерувати надійні паролі

```bash
# PostgreSQL
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d '/+=' | head -c 32)"
# Redis
echo "REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d '/+=' | head -c 32)"
# n8n basic auth
echo "N8N_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 24)"
# n8n encryption key (32 символи)
echo "N8N_ENCRYPTION_KEY=$(openssl rand -hex 16)"
```

Впишіть згенеровані значення у `.env` (`nano .env`). Також задайте `DOMAIN=your-domain.com` та `N8N_HOST=your-domain.com`.
Поля `VAULT_ROLE_ID` / `VAULT_SECRET_ID` заповняться пізніше (крок 4.4).

> ⚠️ Ніколи не комітьте `.env` у git — він уже у `.gitignore`.

### 2.3. Синхронізувати пароль Redis у конфіг

У `config/redis/redis.conf` рядок `requirepass REDIS_PASSWORD_PLACEHOLDER` потрібно замінити на реальний пароль з `.env`:

```bash
source .env
sed -i "s/^requirepass .*/requirepass ${REDIS_PASSWORD}/" config/redis/redis.conf
```

---

## 3. Перший запуск інфраструктури (без агента)

Спочатку піднімаємо базові сервіси, щоб ініціалізувати Vault до старту агента.

```bash
cd /opt/eva
docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env up -d postgres redis vault
docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env ps
```

> **Важливо щодо шляхів.** Файл `deploy/docker-compose.yml` посилається на шляхи відносно кореня репозиторію (`./config`, `./src`, `context: .`). Тому compose **завжди** запускається з кореня `/opt/eva` з прапорцем `--project-directory .`. Для зручності можна створити аліас:
>
> ```bash
> alias dc='docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env'
> ```

Перевірити стан:

```bash
docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env logs vault | tail -20
curl -s http://127.0.0.1:8200/v1/sys/health | jq   # initialized:false, sealed:true — очікувано
```

---

## 4. Ініціалізація Vault

### 4.1. Запустити ініціалізацію (Shamir 3-of-5 + AppRole)

```bash
cd /opt/eva
sudo VAULT_ADDR=http://127.0.0.1:8200 bash deploy/scripts/vault_init.sh
```

Скрипт виконає: init (5 ключів, поріг 3), автоматичний unseal для налаштування, увімкнення audit log, KV v2, завантаження політик, створення AppRole для eva/sentinel, збереження плейсхолдер-секретів.

### 4.2. Зберегти unseal-ключі та root-token

Файл `/opt/eva/vault-secrets/vault-init.json` містить 5 unseal-ключів і root-token.

```bash
sudo cat /opt/eva/vault-secrets/vault-init.json | jq
```

> 🔴 **КРИТИЧНО:**
> 1. Розподіліть 5 unseal-ключів між 5 довіреними особами.
> 2. Збережіть root-token у HSM або менеджері паролів.
> 3. Після цього **видаліть** файл: `sudo shred -u /opt/eva/vault-secrets/vault-init.json`.

### 4.3. Замінити плейсхолдери секретів на реальні

Використайте root-token (тимчасово) для запису реальних значень:

```bash
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN="<root-token>"
source /opt/eva/.env

> **Увага.** Усі секрети живуть в одному KV v2-mount `secret` з префіксом
> `eva-syndicate` — єдине джерело правди: `src/vault_paths.py`. Старі шляхи
> `eva/database`, `eva/config`, `eva/api-keys` більше не використовуються.

```bash
# Реальні креденшли БД
curl -s -X POST -H "X-Vault-Token: $VAULT_TOKEN" \
  -d "{\"data\":{\"host\":\"postgres\",\"port\":\"5432\",\"name\":\"eva_syndicate\",\"user\":\"eva\",\"password\":\"${POSTGRES_PASSWORD}\"}}" \
  "$VAULT_ADDR/v1/secret/data/eva-syndicate/database"

# Пароль Redis
curl -s -X POST -H "X-Vault-Token: $VAULT_TOKEN" \
  -d "{\"data\":{\"password\":\"${REDIS_PASSWORD}\"}}" \
  "$VAULT_ADDR/v1/secret/data/eva-syndicate/redis"

# Реальні LLM-ключі
curl -s -X POST -H "X-Vault-Token: $VAULT_TOKEN" \
  -d '{"data":{"openai_api_key":"sk-...","anthropic_api_key":"sk-ant-...","embedding_model":"text-embedding-3-small"}}' \
  "$VAULT_ADDR/v1/secret/data/eva-syndicate/api-keys"

# API-ключ агента та HMAC-секрет webhook'ів.
# Без цього /execute повертає 401 "API authentication key not configured".
API_KEY=$(openssl rand -hex 32)
WEBHOOK_SECRET=$(openssl rand -hex 32)
curl -s -X POST -H "X-Vault-Token: $VAULT_TOKEN" \
  -d "{\"data\":{\"api_key\":\"${API_KEY}\",\"webhook_secret\":\"${WEBHOOK_SECRET}\"}}" \
  "$VAULT_ADDR/v1/secret/data/eva-syndicate/auth"

unset VAULT_TOKEN
```

### 4.4. Записати AppRole-креденшли в `.env`

```bash
sudo cat /opt/eva/vault-secrets/eva-approle.env
# Скопіюйте VAULT_ROLE_ID та VAULT_SECRET_ID у /opt/eva/.env
nano /opt/eva/.env
# Після копіювання — видаліть файл:
sudo shred -u /opt/eva/vault-secrets/eva-approle.env
```

---

## 5. Видача TLS-сертифікатів (Let's Encrypt)

```bash
sudo apt-get install -y certbot
sudo systemctl stop nginx 2>/dev/null || true
sudo certbot certonly --standalone -d your-domain.com --agree-tos -m admin@your-domain.com --non-interactive
ls /etc/letsencrypt/live/your-domain.com/   # fullchain.pem, privkey.pem
```

> Nginx монтує `/etc/letsencrypt` у режимі read-only, тому сертифікати мають існувати на хості до запуску nginx.

---

## 6. Повний запуск стека

```bash
cd /opt/eva
docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env build eva-agent
docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env up -d
docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env ps
```

Перевірити healthcheck усіх сервісів:

```bash
docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env ps --format 'table {{.Name}}\t{{.Status}}'
```

Усі мають бути `healthy`.

---

## 7. Верифікація розгортання

### 7.1. Автоматична перевірка

```bash
cd /opt/eva
bash scripts/verify_deployment.sh
```

Скрипт перевіряє: синтаксис compose, відсутність хардкод-секретів, наявність усіх обов'язкових файлів, що `.env` не в git, non-root у Dockerfile.

### 7.2. Ручні перевірки

```bash
# Health-ендпоінт агента (через nginx)
curl -sk https://your-domain.com/health | jq

# Vault запечатано/розпечатано
curl -s http://127.0.0.1:8200/v1/sys/health | jq '.sealed'

# Внутрішні порти НЕ доступні ззовні (мають таймаутити/відхилятися)
nc -zv your-domain.com 5432 || echo "postgres closed — OK"
nc -zv your-domain.com 6379 || echo "redis closed — OK"
nc -zv your-domain.com 8200 || echo "vault closed — OK"
```

---

## 8. Операції з Vault (перезапуски)

Після кожного перезапуску Vault він запечатаний. Розпечатати (ключі — з менеджера секретів, НЕ з диска):

```bash
VAULT_ADDR=http://127.0.0.1:8200 \
VAULT_UNSEAL_KEY_1="<key1>" \
VAULT_UNSEAL_KEY_2="<key2>" \
VAULT_UNSEAL_KEY_3="<key3>" \
bash /opt/eva/deploy/scripts/vault_unseal.sh
```

Після unseal перезапустіть агента, якщо він стартував раніше за розпечатування:

```bash
cd /opt/eva && docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env restart eva-agent
```

---

## 9. Оновлення системи

```bash
cd /opt/eva
git pull origin feature/complete-system-implementation
docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env build eva-agent
docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env up -d
```

---

## 10. Резервне копіювання

```bash
# PostgreSQL dump (запускати з кореня /opt/eva)
docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env exec -T postgres \
  pg_dump -U eva eva_syndicate | gzip > /opt/eva/backups/pg_$(date +%F).sql.gz

# Дані Vault (Raft snapshot; потрібен root-token)
export VAULT_ADDR=http://127.0.0.1:8200
curl -s -H "X-Vault-Token: $VAULT_TOKEN" \
  "$VAULT_ADDR/v1/sys/storage/raft/snapshot" -o /opt/eva/backups/vault_$(date +%F).snap
```

Каталоги `/data/postgres`, `/data/redis`, `/data/vault`, `/data/n8n` також слід включати в офлайн-бекап.

---

## 11. Усунення несправностей

| Симптом | Причина | Дія |
|---------|---------|-----|
| eva-agent `unhealthy` | Vault запечатано або невірні AppRole-креденшли | Розпечатати Vault (крок 8), перевірити `VAULT_ROLE_ID/SECRET_ID` у `.env` |
| eva-agent не стартує: `POSTGRES_PASSWORD required` | Порожній `.env` | Заповнити `.env`, запускати compose з кореня з `--project-directory . --env-file .env` |
| nginx `unhealthy` | Відсутні TLS-сертифікати | Виконати крок 5, перевірити `/etc/letsencrypt/live/<domain>/` |
| redis healthcheck fail | Пароль у конфізі ≠ `.env` | Синхронізувати (крок 2.3), перезапустити redis |
| Vault `sealed:true` після рестарту | Очікувано | Розпечатати (крок 8) |
| 403 на внутрішніх портах ззовні | Очікувано (ізоляція) | Це коректна поведінка Zero-Trust |

---

## 12. Чеклист готовності до продакшн

- [ ] `server_bootstrap.sh` виконано; UFW/fail2ban активні
- [ ] `.env` заповнено надійними паролями, `chmod 600`, не в git
- [ ] `config/redis/redis.conf` містить реальний `requirepass`
- [ ] Vault ініціалізовано; 5 unseal-ключів розподілено; root-token у сейфі
- [ ] `vault-init.json` та `*-approle.env` видалено (`shred`)
- [ ] Реальні секрети записано у Vault (БД, Redis, LLM)
- [ ] `VAULT_ROLE_ID/SECRET_ID` вписано в `.env`
- [ ] TLS-сертифікати видано
- [ ] Усі сервіси `healthy`
- [ ] `verify_deployment.sh` — без критичних помилок
- [ ] Внутрішні порти недоступні ззовні
- [ ] Налаштовано резервне копіювання

---

Готово. Система EVA SYNDICATE розгорнута згідно з принципами Zero-Trust та Least Privilege.
