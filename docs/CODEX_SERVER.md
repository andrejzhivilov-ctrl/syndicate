# Codex на сервері (19.11.2026)

Codex потрібен сервер, щоб запускати ворота (`tools/check.sh`) і дивитися стан контейнерів. На ПК немає
Python-оточення проєкту, а на сервері є. Доступ будується за принципом найменших прав.

## Що Codex отримує

| Можна | Не можна |
|---|---|
| Окремий користувач `codex` без пароля, вхід лише своїм ключем | root, `sudo` для будь-чого, крім однієї команди нижче |
| Свій клон репозиторію `/home/codex/syndicate` і свій venv: ворота, тести, ruff | Запис у `/opt/syndicate`, `/opt/eva`, Vault, compose, `.env` |
| `sudo syndicate-ro status` — список контейнерів і їхній стан | Група `docker` (вона дорівнює root), `docker exec`, перезапуски |
| `sudo syndicate-ro logs <контейнер> [рядки]` — хвіст логів (без Vault і LiveKit) | Секрети, `vault-init.json`, `directors.env` |
| `sudo syndicate-ro version` — який коміт розгорнуто | Деплой: його робить Андрій |

Живі SQL-тести (`pgserver`) працюють саме від звичайного користувача: PostgreSQL не запускається від root.

## Команди для Андрія

**1. На ПК (PowerShell): окремий ключ для Codex.** Його можна відкликати, не чіпаючи ключ Андрія. На питання
про пароль ключа натисни Enter двічі.

```powershell
ssh-keygen -t ed25519 -f "$HOME\.ssh\codex_syndicate" -C codex-syndicate
```

```powershell
Get-Content "$HOME\.ssh\codex_syndicate.pub"
```

**2. На сервері (як root).** Встав публічний ключ (рядок `ssh-ed25519 …`) замість `<КЛЮЧ>`. Публічний ключ не є
секретом.

```bash
adduser --disabled-password --gecos "" codex
install -d -m 700 -o codex -g codex /home/codex/.ssh
echo '<КЛЮЧ>' > /home/codex/.ssh/authorized_keys
chown codex:codex /home/codex/.ssh/authorized_keys && chmod 600 /home/codex/.ssh/authorized_keys
sudo -u codex git clone https://github.com/andrejzhivilov-ctrl/syndicate.git /home/codex/syndicate
sudo -u codex python3 -m venv /home/codex/syndicate/.venv
sudo -u codex /home/codex/syndicate/.venv/bin/pip install -q -r /home/codex/syndicate/requirements.txt -r /home/codex/syndicate/requirements-dev.txt
```

**3. На сервері, після злиття цієї гілки й `git pull` у `/opt/syndicate`:** команда для читання стану.
Скрипт ставиться з копії root, а не з клону Codex, щоб Codex не міг його підмінити.

```bash
install -m 755 -o root -g root /opt/syndicate/tools/server/syndicate_ro.sh /usr/local/bin/syndicate-ro
echo 'codex ALL=(root) NOPASSWD: /usr/local/bin/syndicate-ro' > /etc/sudoers.d/codex
chmod 440 /etc/sudoers.d/codex && visudo -c
```

**4. На ПК: ярлик для Codex.** Допиши у `C:\Users\Admin\.ssh\config`:

```
Host syndicate-codex
    HostName 169.58.178.154
    User codex
    IdentityFile ~/.ssh/codex_syndicate
    IdentitiesOnly yes
```

Перевірка: `ssh syndicate-codex "cd syndicate && git pull -q && bash tools/check.sh"`.

## Як Codex цим користується

- Ворота для своєї гілки: `ssh syndicate-codex "cd syndicate && git fetch -q && git checkout -q codex/<що> && git pull -q && bash tools/check.sh"`.
- Стан: `ssh syndicate-codex "sudo syndicate-ro status"`, логи: `ssh syndicate-codex "sudo syndicate-ro logs syndicate-syndicate-agent-1 300"`.
- Логи можуть містити уривки повідомлень. Не копіюй їх у зовнішні сервіси й звіти більше, ніж потрібно задачі
  (`docs/OPERATOR_RULES.md`).

## Коли репозиторій стане приватним

`git clone`/`git pull` з `/home/codex/syndicate` потребуватимуть ключа. Додай на GitHub **deploy key лише на
читання** (Settings → Deploy keys): ключ генерується від користувача `codex` на сервері
(`sudo -u codex ssh-keygen -t ed25519 -f /home/codex/.ssh/github_ro -N ""`), публічна частина йде в GitHub, а
remote клону змінюється на `git@github.com:andrejzhivilov-ctrl/syndicate.git`. Push Codex робить з ПК, як і зараз.

## Чесна межа

Codex на ПК працює від того самого користувача Windows, що й Claude Code. Тож технічно він може прочитати і ключ
Андрія `~/.ssh/id_ed25519` з правами root. Окремий ключ і користувач `codex` задають правило й дають журнал (видно,
хто заходив), але справжня межа на ПК — пісочниця Codex і правило з `docs/OPERATOR_RULES.md`: **Codex заходить на
сервер лише як `syndicate-codex`.**

## Відкликати

`deluser --remove-home codex && rm /etc/sudoers.d/codex /usr/local/bin/syndicate-ro`, а на ПК видалити
`~/.ssh/codex_syndicate*`.
