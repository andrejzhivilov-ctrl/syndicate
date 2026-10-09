# Політика пам’яті Marshal v0.3

**Namespace (зарезервований):** `agents/marshal`.
**Статус:** `memory.read` / `memory.write` не видані.
**Корпус:** `marshal_core/knowledge/security/SOURCES.yaml` — `sources: []`, не пам’ять.
**Drive:** не налаштований; не підмішувати до memory.

## Правила

- У пам’ять (коли з’явиться grant): briefs, HITL-рішення, пропозиції скілів — з датою і без секретів.
- Не архівувати payload сканування, тіла HTTP, ключі, GPS, canary, knock-послідовності.
- Чужі namespace завжди deny. Єва не читає `agents/marshal`; Маршал не читає `agents/eva`.
- Brief для Єви не пишеться в її пам’ять; лише копія в payload брифу, якщо scheduler це зробить.
- `[ANDRII_IMMUTABLE]` не перезаписується. Без grant Маршал чужі файли не читає.
- Knowledge corpus read-only після майбутнього ingest; ingest зараз заборонений.
