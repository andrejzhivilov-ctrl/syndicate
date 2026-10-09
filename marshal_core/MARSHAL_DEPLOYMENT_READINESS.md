# Підготовка Marshal — контрольний список v0.2

**Стан пакета:** ідентичність-чернетка (CSO-архетип) і default-deny профіль; не activation.

## Зроблено

- Окремий профіль `marshal`.
- Досьє розібране: `MARSHAL_DOSSIER_REVIEW.md` — ідентичність vs амбіція vs deny.
- Persona/prompt: голос, кредо, підпорядкування Андрію; без live CSO.
- Grants порожні; модель не вибрана.
- Telegram inbound вимкнений; host_control вимкнений.
- Оркестраторний `emergency_lockdown` — deny без grant.

## Не готово

- Dispatcher на маршрутах Marshal.
- Hermes, модель, credentials.
- Реальний lockdown/мережа/host/Tetragon.
- Sentinel/Sentyr (виключені).
- Вeto, бот, cron 02:00–21:00.

## Умови go/no-go

1. Зелений `bash tools/check.sh`.
2. Окремий точний capability, якщо взагалі потрібен runtime.
3. Не копіювати історичний spec і «✅ Закрито» в grants.
