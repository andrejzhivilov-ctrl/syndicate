# Підготовка Marshal — контрольний список v0.5

**Стан:** prepared профіль + хост-код observe/HITL/scan. Не live runtime.
**Ранбук:** `MARSHAL_DEPLOYMENT_RUNBOOK.md`.

## Зроблено

- Ідентичність CSO, observe-only на інтернет за командою Андрія, HITL лише критичне.
- Порожні grants. Telegram/host/voice/n8n/Drive вимкнені.
- Код: `marshal_observe`, `marshal_hitl`, `marshal_brief`, `marshal_skill_scan`, `marshal_ready`.
- Скрипт бінарника: `tools/install_skillspector.sh` (Python 3.12+; не в `requirements.txt`).
- Оркестраторний lockdown — deny.

## Не готово до live

- Бінарник SkillSpector на хості (3.12).
- Бот, Dispatcher, veto grant, n8n, Drive, ingest, Tetragon, модель.

## Go/no-go

1. `bash tools/check.sh`
2. `python tools/marshal_ready.py` → `grants_empty: true`
3. Жоден capability без точного «так».
