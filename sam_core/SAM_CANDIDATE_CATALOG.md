# Sam — каталог кандидатів (GitHub, 2026-10-10)

**Статус:** огляд. Нічого з цього не встановлено як grant, не pip у runtime, крім уже наявних `yfinance` і `ccxt` у `requirements.txt`.
Скіли в профілі — `activation=draft`. «Погодити» ≠ grant.
Брокер не вибраний.

Зірки — з GitHub API на дату огляду. Ліцензія перевіряти перед будь-яким vendor.

## Брати в чергу (окреме «так»)

| Кандидат | Stars / ліц. | Навіщо Сему | Не робити зараз |
|---|---|---|---|
| [ccxt/ccxt](https://github.com/ccxt/ccxt) | ~44k MIT | Уніфікований crypto API; уже в requirements | Не live ключі, не auto |
| [ranaroussi/yfinance](https://github.com/ranaroussi/yfinance) | ~25k Apache-2.0 | Котирування акцій/ETF; уже в requirements | Не як єдине джерело для live ордерів |
| [joshyattridge/smart-money-concepts](https://github.com/joshyattridge/smart-money-concepts) | ~2.1k MIT | FVG/OB/liquidity; skills.py уже probe | Не pip без HITL |
| [dcajasn/Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib) | ~4.5k BSD-3 | Kelly / CDaR для портфеля (інвест-контур) | Не auto-rebalance |
| [ib-api-reloaded/ib_async](https://github.com/ib-api-reloaded/ib_async) | ~1.8k BSD-2 | Живий наступник **архівного** `erdewit/ib_insync` | IBKR лише HITL invest |
| [NDelventhal/cot_reports](https://github.com/NDelventhal/cot_reports) | ~0.2k MIT | CFTC COT у pandas | Не вигадувати COT без файлу |
| [xgboosted/pandas-ta-classic](https://github.com/xgboosted/pandas-ta-classic) | ~0.5k MIT | Активний форк індикаторів; оригінал pandas-ta тихіший | Не 150 індикаторів як «сигнал» |
| [openbb-org/OpenBB](https://github.com/OpenBB-finance/OpenBB) | ~74k | Дослідницька data platform (акції, макро) | Не execution; велика поверхня |
| [nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader) | ~30k LGPL-3 | Серйозний event-driven backtest/live engine | Не ставити як бот; ліц. LGPL |
| [polakowo/vectorbt](https://github.com/polakowo/vectorbt) | ~9k | Швидкий backtest демо-стратегій | Дослідження, не live |
| [hummingbot/hummingbot](https://github.com/hummingbot/hummingbot) | ~20k Apache-2 | HFT crypto mm — **не наш стиль $100 SMC** | Не вендорити |
| [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) | ~55k GPL-3 | Dry-run crypto bot | GPL + чужі стратегії; не copypaste auto |

## Демо-лабораторія

Freqtrade dry-run / vectorbt / nautilus backtest — кандидати **після** вибору брокера. Журнал `venue=demo`.

## Не тягнути оптом

| Репо | Чому |
|---|---|
| `erdewit/ib_insync` | Archived 2024; брати `ib_async` |
| Збірки «AI trading bot» з ключами в репо | Секрети, неперевірені стратегії |
| `kaushikjadhav01/Stock-Market-Prediction-...` | У коді бувають API keys |
| Community «2000 strategies» | Невідомий edge, survivorship |
| Соц-скрапери Facebook/Instagram | TOS, шум, не авторитет; posting deny |

## Соцмережі (observe-only, не grant)

Офіційні API X/Twitter — платні. Telegram MTProto — ризик ToS. Поки `social_listen=false`. Новини: календар (ForexFactory-клас) і першоджерела (Fed, CFTC, SEC EDGAR) важливіші за Instagram.

## Cloudflare

Не квант-дані. Можливий **пізніше** Tunnel/WAF під webhook бота. Не вмикати.

## n8n

Календар + дайджест — креслення Архітектора (`n8n.workflow.mount` у нього). Сем n8n grant не має.
