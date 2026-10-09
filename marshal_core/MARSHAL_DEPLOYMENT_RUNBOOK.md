# Marshal — ранбук розгортання v0.5

**Стан:** максимально підготовлений профіль. **Не** live Hermes, **не** production enforcement.
**Права:** `capabilities` / `resource_scopes` / `services_enabled` / `skills` = `[]`. Це свідомо.

Цей файл — щоб не забути, що вже є в репо і що ще потребує «так» Андрія.

## Що вже в коді (можна класти на сервер як prepared)

| Шар | Код | Права |
|---|---|---|
| Профіль default-deny | `config/agents/marshal.profile.json` | порожні grants; Telegram/host/voice = false |
| Ідентичність / голос | `MARSHAL_CORE_PERSONA.md`, `src/agents/marshal_runtime_prompt.md` | не activation |
| Observe (метадані) | `src/agents/marshal_observe.py` | не читає тіла, не блокує web-пошук Андрія |
| HITL-картки | `src/agents/marshal_hitl.py` | **не** шле в Telegram |
| Brief для Єви | `src/agents/marshal_brief.py` | лише payload, Єва не викликає Маршала |
| Скан пропозицій | `src/agents/marshal_skill_scan.py` | не ставить скіли; LLM-pass заборонений |
| Установка бінарника | `tools/install_skillspector.sh` → `.tools/skillspector/` (gitignore) | не в runtime image |
| Знімок готовності | `python tools/marshal_ready.py` | падає, якщо grants не порожні |
| Lockdown | оркестратор `emergency_lockdown` | `denied` / `host_control_not_granted` |

## Установка SkillSpector (сканер, не грант)

Потрібен **Python 3.12+** (NVIDIA SkillSpector). На 3.11 скрипт вийде з кодом 2, обгортка лишається `scan_unavailable`.

```bash
bash tools/install_skillspector.sh
python tools/marshal_skill_scan.py /path/to/local-skill
python tools/marshal_ready.py
```

- Джерело за замовчуванням: `git+https://github.com/NVIDIA/skillspector.git`
- Завжди `--no-llm`. Ключі з env дочірнього процесу здираються.
- Remote GitHub URL через обгортку — deny. Клонує Андрій, потім локальний скан.
- `pip` у `requirements.txt` **не** додавати (не production-залежність Синдикату).

## Права, які навмисно НЕ видані

Не записувати в `capabilities` без нового «так»:

- `policy.veto`
- `memory.read` / `memory.write` (навіть `agents/marshal`)
- `service.telegram.call`
- host control / lockdown
- n8n live
- Drive

Dispatcher на маршрути Marshal не підключений: порожній grant + Dispatcher відхилить і скан, якщо його повісити на агента. Скан зараз — **хост CLI**, не capability моделі.

## Що ще не live (і не вдавати, що є)

1. Telegram-бот (немає bot_id).
2. n8n-агрегатор брифу.
3. Drive folder.
4. Knowledge ingest (`sources: []`).
5. Tetragon / Falco / Sentinel.
6. Hermes / модель.
7. Вeto enforce.

## Порядок увімкнення пізніше (по одному «так»)

1. Python 3.12 + `bash tools/install_skillspector.sh` на хості.
2. Реальний bot_id + allowlist, якщо потрібен червоний пуш.
3. Dispatcher, потім точний capability.
4. Drive / n8n / knowledge — окремо.

## Перевірка перед комітом / викладкою

```bash
bash tools/check.sh
python tools/marshal_ready.py
```

`deployable_as_prepared_profile: true` означає «профіль можна класти в git/сервер вимкненим», не «Маршал уже шериф».
