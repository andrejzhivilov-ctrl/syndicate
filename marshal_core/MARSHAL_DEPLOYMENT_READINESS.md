# Підготовка Marshal — контрольний список v0.4

**Стан:** ідентичність + операційна чернетка; не activation.

## Зроблено

- Досьє розібране; операційна модель v0.4: observe; HITL лише критичне; інтернет за командою Андрія не блокувати.
- HITL-контракт кнопок без live бота.
- Knowledge `sources: []`. Drive `folder_id=null`. n8n не control plane.
- Grants порожні. Telegram/host_control/voice = false.
- Оркестраторний lockdown — deny.

## Не готово

- Шар Observe, бот, Dispatcher, veto grant, n8n aggregator, Drive folder, ingest.
- Tetragon, Sentinel, lockdown.

## Go/no-go

1. `bash tools/check.sh` зелений.
2. Жоден кандидат не в полі `capabilities` без точного «так».
