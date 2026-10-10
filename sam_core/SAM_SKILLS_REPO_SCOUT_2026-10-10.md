# Sam — розвідка скілів і репозиторіїв (2026-10-10)

**Статус:** лише список кандидатів. Нічого не встановлено, не pip, не vendor, не grant.
**Правило:** «знайдено в пошуку» ≠ перевірено. Перед будь-яким кодом: ліцензія, останній коміт, відсутність ключів у репо, код читається вручну.
**Брокери:** окремо, не вибрано (Андрій: почекати).

Легенда статусу: `snippet` = бачено в описі пошуку, не відкривав README повністю; `check` = потрібно відкрити репо і перевірити.

---

## A. Skills (SKILL.md-формат) — кандидати в драфт-скіли Сема

| Кандидат | Що дає | Зв’язок із Семом | Ризик / примітка | Статус |
|---|---|---|---|---|
| [tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills) | Велика бібліотека: position-sizer, pre-trade-discipline-gate, drawdown-circuit-breaker, trader-memory-core, signal-postmortem, technical-analyst, futures-position-sizer | **Найсильніший кандидат** для журналу, ризику й аналітики тижня/місяця | Багато скілів; брати вибірково; перевірити ліцензію і інтеграції (FMP/API) | snippet |
| [MobiusQuant/OpenMobius-skill](https://github.com/MobiusQuant/OpenMobius-skill) | ICT/SMC knowledge cards, chart rendering, RAG-retrieval | Зручно для SMC-знань Сема | Має real-time data і кеш KB; брати лише knowledge/render, не data-feeds без рішення | snippet |
| [ghwmelite-dotcom/claude-skills](https://github.com/ghwmelite-dotcom/claude-skills) (`ea-trading-skills/`) | ea-signal-engine (SMC/ICT), ea-risk-engine, ea-analytics-hub (журнал, equity, WR/PF/Sharpe), ea-backtest-lab, ea-market-regime | MQL5/EA-орієнтовано; як **довідка** для метрик і режимів | MQL5-специфіка; не EA-бот | snippet |
| [agiprolabs/claude-trading-skills](https://github.com/agiprolabs/claude-trading-skills) | 68 скілів: pandas-ta, TA-Lib, backtesting, position sizing, risk, trade journaling, Kelly, walk-forward | Велика карта для аналітики і ризику | **Крипто/DeFi-first**, Solana/PumpFun/MEV — не наш профіль; брати лише ta/risk/journal | snippet |
| [JoelLewis/finance_skills](https://github.com/JoelLewis/finance_skills) | 84 скіли: інвест-менеджмент, compliance, trading ops, reporting | Інвест-контур (IBKR/DCA) як довідка | Compliance/advisory — не для Сема без рішення; велика поверхня | snippet |
| [LLMQuant/skills](https://github.com/LLMQuant/skills) | Скіли для агентів (Claude Code, Hermes, OpenClaw, Codex) на LLMQuant Data | Формат і патерни для фінданих скілів | Залежить від LLMQuant Data (зовнішній API) | snippet |
| [RKiding/Awesome-finance-skills](https://github.com/RKiding/Awesome-finance-skills) (Alphaear) | News, sentiment, signal tracking, reporting | **Сентимент новин** для слоту «аналіз» | Перевірити ключі й джерела | snippet |
| [quant-sentiment-ai/claude-equity-research](https://github.com/quant-sentiment-ai/claude-equity-research) | Research buy/sell/hold | Інвест-дискусія (не auto) | Лише як шаблон звіту; не рекомендація | snippet |
| [xbtlin/ai-berkshire](https://github.com/xbtlin/ai-berkshire) | Value-investing, multi-investor playbook | Інвест-контур «обговорити» | Лише шаблон аргументації | snippet |
| [marketcalls/vectorbt-backtesting-skills](https://github.com/marketcalls/vectorbt-backtesting-skills) | Skill для vectorbt | Демо-лабораторія, backtest | Не live | snippet |
| [SimpleFXcom/simplefx-trading-skill](https://github.com/SimpleFXcom/simplefx-trading-skill) | Скіл для **торгівлі** через SimpleFX (ордери, позиції) | **Не брати** без брокерського рішення | Це execution-скіл; конфлікт з HITL-only і «брокер TBD» | snippet — **заборонено зараз** |
| [GMGNAI/gmgn-skills](https://github.com/GMGNAI/gmgn-skills), [okx/onchainos-skills](https://github.com/okx/onchainos-skills) | DEX/on-chain торгівля | **Не брати** | Execution / wallet — поза межами Сема | snippet — **заборонено** |
| [Superior-Trade/superior-skills](https://github.com/Superior-Trade/superior-skills) | Hyperliquid deploy | **Не брати** | Deploy стратегій, execution | snippet — **заборонено** |

---

## B. Репозиторії — дані, календар, COT

| Кандидат | Ліц. / зірки (з попереднього огляду) | Навіщо | Примітка | Статус |
|---|---|---|---|---|
| [NDelventhal/cot_reports](https://github.com/NDelventhal/cot_reports) | MIT, ~0.2k | CFTC COT (щотижня, неділя 18:00) | Вже в каталозі | check |
| [atirek-pro/ForexFactory-MCP](https://github.com/atirek-pro/ForexFactory-MCP) | не перевірено | Календар ForexFactory як MCP/JSON | Скрейпінг — перевірити TOS і стабільність | snippet |
| [AtaCanYmc/forex-pytory](https://github.com/AtaCanYmc/forex-pytory) | не перевірено | Календар forex/crypto/energy/metals, Pydantic, CLI, MCP; cloudscraper | Обходить Cloudflare challenge — **ризик TOS**, не вмикати без перевірки | snippet |
| [wilsonfreitas/awesome-quant](https://github.com/wilsonfreitas/awesome-quant) | каталог | Навігація по всьому quant | Лише індекс | check |
| [LLMQuant/awesome-trading-agents](https://github.com/LLMQuant/awesome-trading-agents) | CC0, ~0.9k | Огляд агентів/MCP/skills | Індекс | snippet |
| [ccxt/ccxt](https://github.com/ccxt/ccxt) | MIT | Уже в requirements | Без ключів у проді | in catalog |
| [ranaroussi/yfinance](https://github.com/ranaroussi/yfinance) | Apache-2 | Уже в requirements | — | in catalog |
| [joshyattridge/smart-money-concepts](https://github.com/joshyattridge/smart-money-concepts) | MIT | SMC-індикатори (FVG/OB/liquidity) | Тестувати на історії | in catalog |

---

## C. Journal / аналітика / звіти (щоденник, тиждень, місяць)

Це **обов’язкова** частина: щоденник щодня, аналітика щотижня (понеділок 10:00) і щомісяця (1-ше 10:00).

| Кандидат | Що дає | Примітка | Статус |
|---|---|---|---|
| [lalit8786/Trading-Journal-Analytics](https://github.com/lalit8786/Trading-Journal-Analytics) | MT5 Excel → WR, PF, expectancy, drawdown, сесії Лондон/NY | Маленький, навчальний; брати логіку метрик | snippet |
| [Mark-Mulli/Trade-Journal](https://github.com/Mark-Mulli/Trade-Journal) | SQLite system-of-record, read-only MT5, annotate, Excel/Power BI | Архітектурно близько до «архів угод» Сема; read-only ок | snippet |
| [saeid00065/trade-journal](https://github.com/saeid00065/trade-journal) (LuxAlgo, MIT) | P&L calendar, daily journal, analytics, prop-firm tracking, AI reflection (BYO key) | Велика функціональність; **broker sync = окремий grant**; AI reflection — не зараз | snippet |
| [13empty/trading-journal](https://github.com/13empty/trading-journal) (MIT) | Календар PnL, цілі/правила STOP, MT5 bridge, Windows desktop | Desktop/Windows-орієнтовано; ідеї для алертів «STOP» | snippet |
| [marketcalls/vectorbt-backtesting-skills](https://github.com/marketcalls/vectorbt-backtesting-skills) | backtest/оптимізація | Тижнева/місячна аналітика стратегій (demo) | snippet |
| [aryan-cs/grok-trader](https://github.com/aryan-cs/grok-trader) | Grok + X/Reddit/Reuters sentiment (хакатон 2025) | Ідея для Grok-слоту соцмереж; **не копіювати** auto-trader scaffolding; ключі — env | snippet |
| Skill «xai-sentiment» / «xai-stock-sentiment» (adaptationio, mcpmarket / agentskills.so) | Grok X-sentiment JSON | Лише observe-only; без постингу | snippet — **check** автора/ліцензії |

---

## D. Ризик / position sizing / prop-firm math

| Кандидат | Примітка | Статус |
|---|---|---|
| [dcajasn/Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib) | Інвест-портфель, Kelly/CDaR | in catalog |
| [riskkit (HasibVortex369)](https://github.com/HasibVortex369/riskkit) | Position sizing, drawdown, stops, correlation limits, pre-trade validator; адаптери backtesting.py/freqtrade/vectorbt | **Гарний кандидат** для ідей, перевірити ліцензію | snippet |
| [SilentFleetKK/riskguard](https://github.com/SilentFleetKK/riskguard) | Circuit breaker, Kelly/vol sizing, аудит | check | snippet |
| [leionion/dynamic-position-sizer-atr-calculator](https://github.com/leionion/dynamic-position-sizer-atr-calculator) | 1% risk + ATR lot size | Маленький, перевірити | snippet |
| [shootingallday/propfirm-calc](https://github.com/shootingallday/propfirm-calc) | Prop-firm drawdown, payout | Лише якщо буде prop-рахунок (не зараз) | snippet |
| [ChristianRene12/open-source-trading-bot](https://github.com/ChristianRene12/open-source-trading-bot) | Risk management XAUUSD + тести | Тести як зразок | snippet |

---

## E. Заборонено / не тягнути (поточні правила)

- `freqtrade`, `hummingbot`, `nautilus_trader` як live-бот — ліцензія/стиль (вже в каталозі).
- Будь-що з execution, wallet, DEX-swap, order_send (SimpleFX, GMGN, OKX onchainos, Superior, Alpaca MCP з ордерами) — лише після окремого рішення про брокера.
- Скрейпери з обходом Cloudflare (`forex-pytory` cloudscraper) — не вмикати без перевірки TOS.
- Соцмережі з постингом / Facebook / Instagram скрапери — заборонено (observe-only).
- Збірки «AI trading bot» з ключами в репо.
- `erdewit/ib_insync` (archived) — брати `ib_async`.

---

## F. Наступні кроки (лише з «так» Андрія)

1. Відкрити топ-5 (tradermonty, riskkit, lalit/Mark-Mulli journal, Alphaear, OpenMobius) і перевірити ліцензію + код вручну.
2. Вибрати **1–2** для скіл-драфтів Сема (journal/analytics і risk), не більше.
3. Брокери — пізніше, окремо від цього списку.
