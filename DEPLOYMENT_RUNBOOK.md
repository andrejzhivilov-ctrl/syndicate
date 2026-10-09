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

> ⚠️ `POSTGRES_PASSWORD` і `REDIS_PASSWORD` мають бути **справжніми вже тут**: контейнери стартують із ними (крок 3), і саме ці самі значення `vault_init.sh` покладе у Vault (крок 4). Скрипт відмовиться працювати, якщо побачить `CHANGE_ME`/`PLACEHOLDER` — щоб не розійтися з тим, з чим реально піднято БД.

> ⚠️ Ніколи не комітьте `.env` у git — він уже у `.gitignore`.

### 2.3. Пароль Redis

**Нічого синхронізувати не треба — і не можна.** `config/redis/redis.conf` навмисно
не містить `requirepass`: пароль передається процесу при старті контейнера
(`docker compose` бере `${REDIS_PASSWORD}` з `.env` і додає `--requirepass`).

Команда `sed` тут більше не потрібна: раніше вона редагувала рядок, якого у файлі
не існувало, тому мовчки нічого не робила, а Redis піднімався **без пароля**.

Що потрібно зробити — лише переконатися, що `.env` містить `REDIS_PASSWORD`
(порожнє або відсутнє значення зупинить запуск, це навмисно).

```bash
grep -q '^REDIS_PASSWORD=.\+' .env && echo "OK: пароль задано" || echo "СТОП: задайте REDIS_PASSWORD"
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

### 4.1. Що змінилось (прочитати перед першим запуском)

Раніша версія скрипта клала в Vault **плейсхолдери** — `CHANGE_ME_BEFORE_PRODUCTION`
для пароля БД і Redis та `PLACEHOLDER_UPDATE_ME` для LLM-ключів. Значення, яке *виглядає*
заповненим, небезпечніше за відсутнє: воно не кидається в очі при перевірці `vault kv get`,
а помилка виринає пізніше й далеко від причини. Тепер:

* пароль БД і Redis **беруться з `.env`** (ті самі, з якими стартували контейнери) —
  скрипт не вигадує своїх і **відмовляється працювати**, якщо `POSTGRES_PASSWORD` /
  `REDIS_PASSWORD` порожні або містять `CHANGE_ME`/`PLACEHOLDER`;
* LLM-ключі передаються змінними середовища; чого немає — того **немає в Vault**
  (це чесно, і агент так і звітує: LLM `unavailable`). Щоб додати пізніше:
  `vault kv put secret/eva-syndicate/<service> key=value`;
* `api_key` + `webhook_secret` генеруються випадково самим скриптом;
* політики **не** пишуться heredoc-ом, а завантажуються з `config/vault/policies/*.hcl`,
  які генеруються з коду: `python tools/vault_policies.py --write`;
* AppRole створюється **на кожну політику** (не лише eva/sentinel), щоб поверх міг
  отримати власний токен, коли переїде в окремий контейнер;
* root-token **відкликається** наприкінці (`KEEP_ROOT_TOKEN=1` — щоб лишити).

### 4.2. Ключі для запуску

Скрипт бере секрети зі змінних середовища. Найпростіше — підвантажити `.env`:

```bash
cd /opt/eva
set -a; source .env; set +a          # POSTGRES_PASSWORD, REDIS_PASSWORD уже там
export ANTHROPIC_API_KEY="sk-ant-..."   # опційно; що не задано — те не потрапить у Vault
sudo -E VAULT_ADDR=http://127.0.0.1:8200 bash deploy/scripts/vault_init.sh
```

`sudo -E` потрібен, щоб змінні дійшли до скрипта (і `SUDO` не зʼїв `VAULT_ADDR`).

Скрипт виконує: init (5 ключів, поріг 3) → автounseal для налаштування → audit log →
KV v2 `secret` → завантаження політик → запис секретів → AppRole на кожну політику →
ревокація root-token. Наприкінці він друкує, у якому файлі лежать AppRole-креденшли.

### 4.3. Зберегти unseal-ключі

```bash
sudo cat /opt/eva/vault-secrets/vault-init.json | jq
```

> 🔴 **КРИТИЧНО:**
> 1. Розподіліть 5 unseal-ключів між 5 довіреними особами (не в одному місці).
> 2. Збережіть root-token у HSM або менеджері паролів — він знадобиться для
>    аварійного доступу (`vault operator generate-root` з 3 ключами, якщо root
>    втрачено, теж працює).
> 3. Після цього **видаліть** файл: `sudo shred -u /opt/eva/vault-secrets/vault-init.json`.

### 4.4. Записати AppRole-креденшли в `.env`

```bash
sudo cat /opt/eva/vault-secrets/eva-agent.approle.env
# Скопіюйте VAULT_ROLE_ID та VAULT_SECRET_ID у /opt/eva/.env
nano /opt/eva/.env
# Після копіювання — видаліть усі файли *.approle.env:
sudo shred -u /opt/eva/vault-secrets/*.approle.env
```

### 4.5. Перевірити, що політики відповідають коду

```bash
python tools/vault_policies.py --check     # виконується і в tools/check.sh
```

Перевірка ловить три класи помилок: політику, що відстала від коду (агент отримав би
403 на секреті, який читає на старті); сервіс, який код читає, але `src/vault_paths.py`
не оголошує; і grant, що покриває весь префікс (`secret/data/eva-syndicate/*`), тобто
доступ до чужих ключів.

### 4.6. Хто які секрети бачить

| Політика | Призначення | Доступ |
| :--- | :--- | :--- |
| `eva-agent` | **рантайм** (усі поверхи в одному процесі) | `database`, `redis`, `api-keys`, `auth`, конектори, голос, `agents/*` |
| `eva-eva` | Єва в окремому контейнері (на майбутнє) | інфраструктура + конектори + голос + `agents/eva/*` |
| `eva-marshal` | Маршал | інфраструктура + `mcp`, `telegram` + `agents/marshal/*` |
| `eva-fin` | Фін | інфраструктура + `google_workspace` + `agents/fin/*` |
| `eva-architect` | Архітектор | інфраструктура + `mcp` + `agents/architect/*` |
| `eva-sam`, `eva-doc`, `eva-kira` | Сем, Док, Кіра | інфраструктура + власна гілка (default deny) |

Жодна агентська політика не дає `auth` (ключ API самого сервера) і не дає доступу до
гілки іншого агента. **Причина, чому рантайм поки бачить усе:** сьогодні всі поверхи
живуть в одному процесі (`eva-agent`). Щойно поверх переїде в окремий контейнер, його
`VAULT_ROLE_ID/SECRET_ID` беруться з `vault-secrets/eva-<id>.approle.env`, і жодних
змін у коді це не потребує.

### 4.7. Як додати секрет для сервісу

```bash
export VAULT_ADDR=http://127.0.0.1:8200
vault login                     # будь-який метод з правом на запис
vault kv put secret/eva-syndicate/telegram bot_token=... chat_id=...
vault kv put secret/eva-syndicate/agents/sam/broker api_key=... api_secret=...
```

Далі перевірте, що сервіс оголошено в `src/vault_paths.py` (інакше `--check` попередить),
і за потреби додайте його агенту в `AGENT_SERVICES`.

> **Плейсхолдери заборонені.** `VaultClient.get_secret()` відкидає значення з
> `CHANGE_ME` / `PLACEHOLDER` / `REPLACE_ME` / `UPDATE_ME` і пише в лог
> `vault_placeholder_secret_ignored`. `/health` показує
> `vault_placeholder_secrets: ["secret/data/...:<key>"]` — саме **назви** ключів, не
> значення. Так само поводиться й порожній рядок.

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

Бекапи робить `tools/backup.py` — не одноразові команди з цього документа (раніше тут були
три рядки, які неможливо було запустити надійно). Інструмент створює **набір** з трьох
артефактів і сам їх перевіряє:

| Артефакт | Навіщо |
| :--- | :--- |
| `postgres.dump` (`pg_dump --format=custom`) | Єдині невідтворювані дані: пам'ять, журнали, історія |
| `vault.snap` (Raft snapshot) | Без нього не буде паролів до БД, Redis і всіх API-ключів |
| `env.bootstrap` (копія `.env`, `chmod 600`) | Без нього відновлення неможливе: unseal-матеріал і AppRole |

Плюс `manifest.json` із `sha256`, розмірами та **чесним статусом кожного кроку**:
`ok` або `unavailable` із причиною. Дамп **верифікується** (`pg_restore --list`) до того, як
набір уважається придатним — саме ця перевірка ловить пошкоджений дамп, який інакше
виявився б у день відновлення.

### Запуск

```bash
cd /opt/eva
# покласти поруч із бекапом (потрібен libpq: apt-get install -y postgresql-client)
export EVA_BACKUP_DIR=/data/backups
export DATABASE_URL="postgresql://eva:${POSTGRES_PASSWORD}@127.0.0.1:5432/eva_syndicate"  # або POSTGRES_PASSWORD

# токен Vault ІЗ ПРАВОМ ЛИШЕ НА ЗНІМОК (не root!) — див. нижче
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN="$(cat /root/.vault-backup-token)"

python3 tools/backup.py --dest "$EVA_BACKUP_DIR" --keep-days 14 --offsite
python3 tools/backup.py --list          # що лежить на диску
```

`--offsite` штовхає набір у `restic` (`RESTIC_REPOSITORY`, `RESTIC_PASSWORD`). Якщо restic
не встановлено або репозиторій не задано — це буде `unavailable` з причиною, **не** «ok».

`DB_PASSWORD` передається через DSN, тому не друкуйте вивід у публічні логи.

### Розклад (cron)

```bash
# /etc/cron.d/eva-backup — щодня о 03:30
30 3 * * * root cd /opt/eva && set -a && . ./.backup.env && set +a && \
  /usr/bin/python3 tools/backup.py --offsite >> /var/log/eva-backup.log 2>&1
```

`/opt/eva/.backup.env` (chmod 600, у git не потрапляє) містить `EVA_BACKUP_DIR`,
`DATABASE_URL`, `VAULT_ADDR`, `VAULT_TOKEN`, `RESTIC_*`. Cron повертає ненульовий код, якщо
дампу немає — тобто тишу в логах можна відрізнити від відсутності бекапу.

Альтернатива cron — systemd timer:

```ini
# /etc/systemd/system/eva-backup.service
[Service]
Type=oneshot
WorkingDirectory=/opt/eva
EnvironmentFile=/opt/eva/.backup.env
ExecStart=/usr/bin/python3 tools/backup.py --offsite
```
```ini
# /etc/systemd/system/eva-backup.timer
[Timer]
OnCalendar=*-*-* 03:30:00
Persistent=true
[Install]
WantedBy=timers.target
```

### Токен Vault лише для знімків

Не використовуйте root-token у cron. Створіть окрему політику й токен:

```bash
vault policy write eva-backup - <<'EOF'
path "sys/storage/raft/snapshot" { capabilities = ["read"] }
EOF
vault token create -policy=eva-backup -period=768h -field=token > /root/.vault-backup-token
chmod 600 /root/.vault-backup-token
```

---

## 10.1. Відновлення з бекапу

> Порядок важливий: **спершу Vault, потім БД, потім `.env`, і тільки потім піднімаємо стек.**
> Агент стартує, лише коли має і Vault, і БД — інакше він просто не підніметься.

```bash
cd /opt/eva
export SNAP=/data/backups/2026-10-06T03-30-00Z     # потрібен набір зі статусом "ok"
python3 -c "import json;print(json.load(open('$SNAP/manifest.json'))['status'])"   # має бути ok
sha256sum -c <(cd "$SNAP" && python3 -c "
import json,hashlib,pathlib
m=json.load(open('manifest.json'))
for a in m['artifacts']:
    if a['status']=='ok' and a['sha256']: print(a['sha256'], a['path'])")
```

1. **Секрети.** Розгорнути Vault, розпечатати (крок 8), потім:
   ```bash
   vault operator raft snapshot restore "$SNAP/vault.snap"
   ```
2. **Bootstrap-файл.** Відновити `.env` зі знімка (`cp "$SNAP/env.bootstrap" .env && chmod 600 .env`),
   звірити `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `VAULT_ROLE_ID/SECRET_ID`.
3. **Інфраструктура.** `docker compose ... up -d postgres redis vault` і дочекатися `healthy`.
4. **База.**
   ```bash
   docker compose -f deploy/docker-compose.yml --project-directory . --env-file .env exec -T postgres \
     pg_restore --clean --if-exists --no-owner -U eva -d eva_syndicate < "$SNAP/postgres.dump"
   ```
5. **Решта стека** (крок 6) і перевірка (крок 7), окремо — `/health` має показати
   `semantic_search_enabled: true`, а `embedding_failures: 0`.

**Обов'язкова репетиція.** Бекап, який жодного разу не відновлювали, — це не бекап:
раз на квартал розгортайте набір на тестовій машині за цими п'ятьма кроками й фіксуйте час.

Каталоги `/data/postgres`, `/data/vault`, `/data/n8n` (bind-mounts) варто додатково включати
в офлайн-бекап хоста: знімок Vault і дамп БД цілком замінюють їхній вміст, але копія не завадить.

---

## 11. Усунення несправностей

| Симптом | Причина | Дія |
|---------|---------|-----|
| eva-agent `unhealthy` | Vault запечатано або невірні AppRole-креденшли | Розпечатати Vault (крок 8), перевірити `VAULT_ROLE_ID/SECRET_ID` у `.env` |
| eva-agent не стартує: `POSTGRES_PASSWORD required` | Порожній `.env` | Заповнити `.env`, запускати compose з кореня з `--project-directory . --env-file .env` |
| nginx `unhealthy` | Відсутні TLS-сертифікати | Виконати крок 5, перевірити `/etc/letsencrypt/live/<domain>/` |
| redis healthcheck fail | Пароль у конфізі ≠ `.env` | Синхронізувати (крок 2.3), перезапустити redis |
| Vault `sealed:true` після рестарту | Очікувано | Розпечатати (крок 8) |
| Агент падає з 403 на `/v1/secret/data/...` | політика відстала від коду | `python tools/vault_policies.py --check`, далі `--write` і повторно завантажити політики (крок 4) |
| `/health` показує `vault_placeholder_secrets` | у Vault лежить `CHANGE_ME*`/`PLACEHOLDER*` | записати справжнє значення: `vault kv put secret/eva-syndicate/<service> <key>=<value>` |
| `vault_init.sh` відмовляється стартувати | `POSTGRES_PASSWORD`/`REDIS_PASSWORD` порожні або плейсхолдер | задати справжній пароль у `.env` і повторити |
| 403 на внутрішніх портах ззовні | Очікувано (ізоляція) | Це коректна поведінка Zero-Trust |

---

## 12. Чеклист готовності до продакшн

- [ ] `server_bootstrap.sh` виконано; UFW/fail2ban активні
- [ ] `.env` заповнено надійними паролями, `chmod 600`, не в git
- [ ] Redis відповідає лише з паролем: `redis-cli -a "$REDIS_PASSWORD" --no-auth-warning ping` → `PONG`, а `redis-cli ping` → `NOAUTH` (порожній `REDIS_PASSWORD` у `.env` не дає запустити compose)
- [ ] `POSTGRES_PASSWORD` / `REDIS_PASSWORD` — справжні (не `CHANGE_ME`), ті самі, з якими стартували контейнери
- [ ] Vault ініціалізовано (`vault_init.sh`); 5 unseal-ключів розподілено; root-token у сейфі
- [ ] `python tools/vault_policies.py --check` — політики відповідають коду
- [ ] `vault-init.json` і `*.approle.env` видалено з диска після розповсюдження ключів
- [ ] `vault-init.json` та `*-approle.env` видалено (`shred`)
- [ ] Реальні секрети записано у Vault (БД, Redis, LLM); перевірено, що плейсхолдерів немає
      (`curl -s localhost:8000/health | jq .vault_placeholder_secrets` → `[]`)
- [ ] `VAULT_ROLE_ID/SECRET_ID` вписано в `.env`
- [ ] TLS-сертифікати видано
- [ ] Усі сервіси `healthy`
- [ ] `verify_deployment.sh` — без критичних помилок
- [ ] Внутрішні порти недоступні ззовні
- [ ] `tools/backup.py` виконано на сервері: набір має `status: ok` у `manifest.json`, дамп **верифіковано** `pg_restore --list`, а cron/systemd timer щодня створює новий
- [ ] Бекап **відновлено** на тестовій машині за §10.1 (бекап без репетиції не рахується)

---

Готово. Система EVA SYNDICATE розгорнута згідно з принципами Zero-Trust та Least Privilege.
