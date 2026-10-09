# Підготовка Marshal — контрольний список v0.1

**Стан пакета:** ідентичність-чернетка і default-deny профіль; не activation.

## Зроблено

- Підтверджено окремий профіль `marshal`.
- Ідентичність обмежена описом/статичними межами; CSO-спека не є роллю.
- Grants порожні; модель не вибрана.
- Telegram inbound вимкнений; host_control вимкнений.
- Оркестраторний `emergency_lockdown` — deny без grant.

## Не готово

- Dispatcher на маршрутах Marshal.
- Hermes, модель, credentials.
- Реальний lockdown/мережа/host.
- Sentinel (виключений), Tetragon (Фаза 2).

## Умови go/no-go

1. Зелений `bash tools/check.sh`.
2. Окремий точний capability, якщо взагалі потрібен runtime.
3. Не копіювати історичний spec у grants.
