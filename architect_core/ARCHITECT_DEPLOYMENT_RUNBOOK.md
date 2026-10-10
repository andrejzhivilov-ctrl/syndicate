# Architect — ранбук розгортання (завершений пакет)

**Гілка:** `arena/41a10104-syndicate`. Не зливати в main без окремого «так».

## Перед викладкою

```bash
bash tools/check.sh
python tools/architect_ready.py
python tools/architect_preview.py   # optional: JSON file path
```

Очікування `architect_ready.py`: `grants_empty=true`, `n8n_live=false`, `gitops_push=false`, `eva_cannot_assign=true`.

## Прев’ю зв’язки

```bash
python tools/architect_preview.py path/to/workflow.json
```

Вивід: mermaid + пояснення вузлів. Підтвердження Андрія → `deliver_after_confirm(..., approved=True)` здає **inactive** JSON. Live n8n не викликається.

## Права

Див. `ARCHITECT_PERMISSIONS.md`. Порожні grants — свідомий дозвіл на безпечну викладку, не дира в політиці.

## Не вмикати під час деплою

Hermes, n8n live, Telegram-бот, git push від агента, Dispatcher на порожніх grants (відхилить навіть lint, якщо повісити на модель).
