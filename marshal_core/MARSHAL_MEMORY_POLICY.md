# Політика пам’яті Marshal v0.2

**Namespace (зарезервований):** `agents/marshal`.
**Статус:** `memory.read` / `memory.write` не видані.

## Правила

- Звичайні аудити й рапорти не стають довготривалою пам’яттю автоматично.
- Не архівувати секрети, payload сканування, GPS, canary-ключі, knock-послідовності.
- Чужі namespace (Єва, Fin, Doc, …) завжди deny — включно з «нічним аудитом Dreaming Loop».
- Маркер `[ANDRII_IMMUTABLE]` і прямі вказівки Андрія не перезаписуються. Без grant Marshal їх і не читає в чужих папках.
- Історичний recall у `MarshalAgent` — лише контекст, не security decision і не grant.
