# Етап 5: `eva-agent` → `syndicate-agent` (команди для сервера)

Частина плану `docs/MIGRATION_7_AGENTS.md`. Команди запускає Андрій на `169.58.178.154` під `root`.
Кожен крок окремо, з перевіркою після нього. Простій ботів і cockpit — близько хвилини (кроки 1–4).

## Що змінюється

- Сервіс у `docker-compose.yml` тепер `syndicate-agent`, контейнер — `syndicate-syndicate-agent-1`.
- Стара назва `eva-agent` лишається **мережевим псевдонімом** у мережах `backend` і `hermes_net`.
  Сценарії, вже імпортовані в n8n, і Hermes зі старим конфігом далі ходять на `http://eva-agent:8000`.
  Псевдонім прибираємо разом з n8n на етапі 6.
- nginx: upstream `syndicate_agent` → `syndicate-agent:8000`.
- **Не змінюється:** роль і політика Vault `eva-agent` (той самий `VAULT_ROLE_ID/SECRET_ID` у `.env`),
  роль Postgres `eva_agent`, том `syndicate_eva_data` з даними Єви. Рішення Андрія від 04.11.2026.

## Крок 1. Зупинити старий контейнер

Спершу зупиняємо, а потім оновлюємо код. Після `git pull` у compose вже не буде сервісу `eva-agent`, і
`docker compose` не зможе його зупинити. А два контейнери одночасно не можна: обидва тягнули б Telegram.

```bash
cd /opt/syndicate && docker compose stop eva-agent && docker compose rm -f eva-agent
```

## Крок 2. Оновити код

```bash
sudo -u syndicate git pull --ff-only && sudo -u syndicate git log --oneline -1
```

## Крок 3. Підняти `syndicate-agent`

Образ той самий, що працював (код `src` монтується з диска), тому не збираємо, а лише даємо йому нову назву:

```bash
docker tag syndicate-eva-agent:latest syndicate-syndicate-agent:latest
docker compose up -d --no-deps syndicate-agent
```

Через 30–60 секунд:

```bash
docker compose ps syndicate-agent && docker compose logs --tail 40 syndicate-agent
```

Чекаємо `healthy`, `SYNDICATE agent ready` і жодного `Traceback`.

## Крок 4. Перезапустити nginx

nginx читає новий `nginx.conf` і нову адресу контейнера лише при старті:

```bash
docker compose restart nginx && docker compose ps nginx
docker compose exec nginx wget -qO- http://syndicate-agent:8000/health
```

## Крок 5. Перевірити старе ім'я і Hermes

```bash
docker compose exec n8n wget -qO- http://eva-agent:8000/health
docker compose logs --since 3m syndicate-agent | grep -E 'hermes/trainer|Traceback' | tail -5
```

Перше має відповісти так само, як `/health` у кроці 4. Hermes Алекса має давати `POST /hermes/trainer/mcp ... 200`.
Перезапускати Hermes не обов'язково: його новий конфіг уже вказує на `syndicate-agent`, а старий працює через псевдонім.

Після цього: відкрити cockpit і написати будь-якому боту, щоб переконатися, що відповідь приходить.

## Крок 6. Прибрати старий образ (за бажанням)

```bash
docker image rm syndicate-eva-agent:latest
```

Тег `syndicate-syndicate-agent:latest` вказує на ті самі шари, тож місце звільниться лише від назви. Але
після цього відкат нижче потребуватиме `docker tag syndicate-syndicate-agent:latest syndicate-eva-agent:latest`.

## Відкат

```bash
cd /opt/syndicate && docker compose stop syndicate-agent && docker compose rm -f syndicate-agent
sudo -u syndicate git checkout HEAD~1 -- docker-compose.yml config/nginx/nginx.conf
docker compose up -d --no-deps eva-agent && docker compose restart nginx
```

Після відкату `git status` покаже змінені файли. Повернути їх: `sudo -u syndicate git checkout HEAD -- docker-compose.yml config/nginx/nginx.conf`.
