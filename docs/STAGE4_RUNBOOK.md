# Етап 4: прибрати старі контейнери агентів (команди для сервера)

Частина плану `docs/MIGRATION_7_AGENTS.md`. Команди запускає Андрій на `169.58.178.154` під `root`.
Кожен крок окремо, з перевіркою після нього. Значення секретів ніде не друкуються.

## Що вже перевірено (04.11.2026, лише читання)

- 9 контейнерів `deploy-{atlas,dex,jack,oscar,ray,scout,sonar,trainer,tyler}-agent-1` дозволяють лише
  дію `capabilities` і не мають постачальників (`SYNDICATE_DIRECTOR_PROVIDERS` порожній).
- `eva-agent` їх не викликає: у нього немає жодного `*_WORKER_URL`, крім вимкненого `ALICE_WORKER_URL`.
- Hermes Алекса (`deploy-trainer-hermes-1`) звертається до `eva-agent`, а не до `trainer-agent`.
  Його не чіпаємо.
- Усі 9 томів `deploy_*_data` порожні (4 КБ, жодного файлу). Переносити нічого.
- Контейнера Аліси на сервері немає.

## Крок 0. Оновити код і перезапустити eva-agent

Потрібно, щоб злитий етап 4 (і етапи 1–3) запрацював.

```bash
cd /opt/syndicate && sudo -u syndicate git pull --ff-only && docker compose restart eva-agent
docker compose ps eva-agent && docker compose logs --tail 40 eva-agent
```

Чекаємо `healthy` і жодного `Traceback`.

## Крок 1. Зупинити й видалити 9 контейнерів

```bash
for a in atlas dex jack oscar ray scout sonar trainer tyler; do docker stop deploy-$a-agent-1 && docker rm deploy-$a-agent-1; done
docker ps -a --format '{{.Names}}' | grep -E 'deploy-.*-agent-1' || echo "старих контейнерів немає"
```

Hermes (`deploy-trainer-hermes-1`) має лишитися в `docker ps`.

## Крок 2. Мережі, томи, образи

Мережі `deploy_*_control` використовували лише ці контейнери:

```bash
for a in atlas dex jack oscar ray scout sonar trainer tyler; do docker network rm deploy_${a}_control; done
```

Томи порожні, але перед видаленням ще раз перевіряємо, що в них нічого немає:

```bash
for a in atlas dex jack oscar ray scout sonar trainer tyler; do printf "%s: " $a; find "$(docker volume inspect deploy_${a}_data --format '{{.Mountpoint}}')" -type f | wc -l; done
```

Скрізь має бути `0`. Тоді:

```bash
for a in atlas dex jack oscar ray scout sonar trainer tyler; do docker volume rm deploy_${a}_data; done
for a in atlas dex jack oscar ray scout sonar trainer tyler; do docker image rm deploy-$a-agent:latest; done
```

Образи звільнять близько 5 ГБ.

## Крок 3. Ролі й політики Vault видалених агентів

Ролі AppRole створені з файлів політик, тому видалення файлів із репозиторію їх не прибирає.
Видаляємо 11 ролей і політик: `alice antigravity architect atlas dex doc jack oscar ray scout sonar`.
Ролі `tyler` і `trainer` лишаються: це агенти з ростера, вони отримають свої контейнери пізніше.

Потрібен токен адміністратора Vault. Андрій вводить його сам у запит `vault login`, токен не потрапляє
в командний рядок і в історію:

```bash
docker exec -it syndicate-vault-1 sh
vault login
for a in alice antigravity architect atlas dex doc jack oscar ray scout sonar; do vault delete auth/approle/role/eva-$a; vault policy delete eva-$a; done
vault list auth/approle/role
vault token revoke -self
exit
```

У списку ролей мають лишитися `eva-agent`, `eva-fin`, `eva-kira`, `eva-kodex`, `eva-marshal`, `eva-sam`,
`eva-trainer`, `eva-tyler`.

Токени ботів (`telegram/*`, `agents/<id>/telegram`) і ключі постачальників у Vault **не видаляються**.
Це окреме рішення Андрія.

## Крок 4. Облікові дані ролей у файлах

Після кроку 3 вони вже недійсні, але прибрати їх варто.

- `/opt/eva/vault-secrets/eva-{alice,antigravity,architect,atlas,dex,doc,jack,oscar,ray,scout,sonar}.approle.env`.
  Видалити або перенести в бекап на розсуд Андрія.
- У `/opt/syndicate/.env` рядки `<ID>_VAULT_ROLE_ID` і `<ID>_VAULT_SECRET_ID` для цих 11 id. Ось як побачити
  лише назви, без значень:

```bash
grep -oE '^(ALICE|ANTIGRAVITY|ARCHITECT|ATLAS|DEX|DOC|JACK|OSCAR|RAY|SCOUT|SONAR|TYLER|TRAINER)_VAULT_(ROLE|SECRET)_ID' /opt/syndicate/.env
```

`TYLER_*` і `TRAINER_*` лишаються.

## Перевірка після всього

```bash
docker ps --format '{{.Names}} {{.Status}}'
docker compose ps eva-agent
```

У cockpit (розділ директорів) має бути 9 записів: 7 агентів і боти Аліси та Кодекса.

## Відкат

- Кроки 1–2: контейнери можна підняти зі старого коміту (`git show e9d39d4:deploy/docker-compose.directors.yml`),
  але вони нічого не робили.
- Крок 3: ролі відновлює `deploy/scripts/vault_init.sh` зі старих файлів політик. Видалені SecretID при цьому
  не повертаються, видаються нові.
