# Політика пам’яті Marshal v0.1

**Namespace (зарезервований):** `agents/marshal`.
**Статус:** `memory.read` / `memory.write` не видані.

## Правила

- Звичайні аудити не стають довготривалою пам’яттю автоматично.
- Не архівувати секрети, payload сканування, GPS.
- Чужі namespace завжди deny.
- Історичний recall у `MarshalAgent` — лише контекст, не security decision і не grant.
