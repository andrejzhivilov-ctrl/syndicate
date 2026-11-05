# Етап 6б: прибрати n8n і псевдонім `eva-agent` (команди для сервера)

Частина плану `docs/MIGRATION_7_AGENTS.md`. Команди запускає Андрій на `169.58.178.154` під `root`.
Кожен крок окремо, з перевіркою після нього. Значення секретів ніде не друкуються.

## Що вже перевірено (05.11.2026, лише читання)

- Усі 5 сценаріїв у n8n вимкнені (`active = f`), запускались лише вручну 03.11. Розклад Алекса вже
  в `syndicate-agent` (етап 6а, `SYNDICATE_SCHEDULE`), тож n8n нічого не робить.
- Псевдонім `eva-agent` досі потрібен одному споживачу: **Hermes Алекса**. Його конфіг на диску вже вказує на
  `syndicate-agent`, але контейнер ще бачить старий файл (конфіг примонтований окремим файлом, а `git pull`
  замінив файл новим). Тому крок 1 — перезапуск Hermes, і лише потім прибираємо псевдонім.
- Дані n8n: база `n8n` у Postgres, тека `/data/n8n` (88 КБ, том `syndicate_n8n_data`), порожній старий том
  `deploy_n8n_data`. Щоденний бекап за 05.11 уже містить `n8n.dump` і `n8n_home.tar.gz`.

## Крок 0. Окрема копія даних n8n

Щоденні бекапи видаляються через 7 днів, тому кладемо копію окремо:

```bash
mkdir -p /root/backup-stage6 && chmod 700 /root/backup-stage6
cd /opt/syndicate && docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -Fc n8n' > /root/backup-stage6/n8n.dump
tar czf /root/backup-stage6/n8n_home.tar.gz -C /data n8n
ls -la /root/backup-stage6
```

Обидва файли мають бути не порожні.

## Крок 1. Перезапустити Hermes Алекса

```bash
cd /opt/syndicate/deploy && docker compose -f docker-compose.hermes.yml restart trainer-hermes
docker exec deploy-trainer-hermes-1 grep -c "eva-agent" /opt/data/config.yaml
```

Друге має показати `0`. Потім написати Алексу в Telegram будь-що і перевірити:

```bash
cd /opt/syndicate && docker compose logs --since 3m syndicate-agent | grep "hermes/trainer" | tail -3
```

Має бути `POST /hermes/trainer/... 200`.

## Крок 2. Зупинити n8n

Спершу зупиняємо, потім оновлюємо код: після `git pull` у compose вже не буде сервісу `n8n`.

```bash
cd /opt/syndicate && docker compose stop n8n && docker compose rm -f n8n
```

## Крок 3. Оновити код, перестворити `syndicate-agent` і nginx

```bash
sudo -u syndicate git pull --ff-only && sudo -u syndicate git log --oneline -1
docker compose run --rm --no-deps nginx nginx -t
```

Має бути `syntax is ok` і `test is successful`. Тоді:

```bash
docker compose up -d --no-deps syndicate-agent
docker compose restart nginx
docker compose ps syndicate-agent nginx
curl -s -o /dev/null -w "%{http_code}\n" https://syndicateholding.com/health
```

Чекаємо `healthy` для обох і `200`. `syndicate-agent` перестворюється, бо з мереж прибрано псевдонім.
Знову написати Алексу і перевірити `hermes/trainer ... 200`, як у кроці 1.

## Крок 4. Видалити дані n8n (лише після кроків 0–3)

```bash
cd /opt/syndicate && docker compose exec -T postgres sh -c 'dropdb -U "$POSTGRES_USER" n8n'
docker volume rm syndicate_n8n_data deploy_n8n_data
rm -rf /data/n8n
docker image rm n8nio/n8n:2.45.6
```

## Крок 5. Прибрати залишки (на розсуд Андрія)

- У `/opt/syndicate/.env` рядки `N8N_*` більше нічим не читаються. Побачити лише назви:
  `grep -oE '^N8N_[A-Z_]+' /opt/syndicate/.env`.
- DNS-запис `n8n.syndicateholding.com` у Cloudflare: nginx тепер відповідає на нього як на невідомий хост (444).
- Ключ `n8n_api_key` у Vault ніхто не читає. Видаляти чи ні — окреме рішення Андрія.
- `deploy/server_bootstrap.sh` і `deploy/scripts/server_bootstrap.sh` (захищені) досі створюють `/data/n8n` і
  правило UFW `deny 5678`. Це нешкідливо; прибрати разом з іншими змінами bootstrap за згодою Андрія.

## Відкат

- До кроку 4: `sudo -u syndicate git checkout <попередній коміт> -- docker-compose.yml config/nginx/nginx.conf`,
  потім `docker compose up -d n8n syndicate-agent && docker compose restart nginx`.
- Після кроку 4: спершу відновити базу й теку з `/root/backup-stage6`
  (`createdb` + `pg_restore -d n8n`, `tar xzf ... -C /data`), потім як вище.
