# Sam — перевірка скілів і репозиторіїв (2026-10-10)

**Статус:** перевірено ліцензії (LICENSE-файли) і код (grep на execution/secret/eval/subprocess, dependencies). Нічого не встановлено в runtime, не pip, не vendor у репо.
**Джерело правди:** `config/agents/sam.profile.json` → `skill_candidates` (activation = `candidate_not_installed`). Це **не** `skills[]` і **не** grants.
**Метод:** shallow clone в `/tmp` (поза репо), read-only огляд. Повного аудиту всіх файлів не робив; перед будь-яким install — окремий код-рев’ю з тестами.

## Вердикти

### Adopt candidate (MIT, без execution, без обов’язкового ключа)

| ID | Репо / шлях | Ліц. | Залежності | Для чого Сему |
|---|---|---|---|---|
| tm-position-sizer | tradermonty/claude-trading-skills `skills/position-sizer` | MIT | stdlib | sizing 1% / 0.5% |
| tm-pre-trade-discipline-gate | same `skills/pre-trade-discipline-gate` | MIT | PyYAML | чекліст перед HITL-карткою |
| tm-drawdown-circuit-breaker | same `skills/drawdown-circuit-breaker` | MIT | pandas-market-calendars, PyYAML | daily stop 3%, серія збитків |
| tm-weekly-performance-digest | same `skills/weekly-performance-digest` | MIT | PyYAML | понеділок 10:00 аналітика |
| tm-trade-performance-coach | same `skills/trade-performance-coach` | MIT | PyYAML | 1-ше число аналітика, помилки |
| tm-trader-memory-core | same `skills/trader-memory-core` | MIT | jsonschema, PyYAML; FMP optional | журнал/тезиси; FMP ключ вимкнено |
| riskkit | HasibVortex369/riskkit | MIT | 0 (pandas/backtesting optional) | PreTradeValidator, drawdown, stops, correlation caps; без мережі й без order-коду |
| cot_reports | NDelventhal/cot_reports | MIT | pandas | CFTC COT щотижня |

Умова для кожного: окремий install-permission Андрія + тести + HITL на будь-що, що торкається грошей.

### Defer (потрібна додаткова перевірка)

- **tm-signal-postmortem** — `requests`, FMP optional; перевірити всі HTTP-виклики.
- **tm-economic-calendar-fetcher** — stdlib `urllib`; перевірити хости перед використанням (потрібен calendar для news freeze).
- **tm-cot-contrarian-detector** — `requests`; спершу взяти `cot_reports`.
- **RKiding/Awesome-finance-skills** (Alphaear, Apache-2.0) — news/sentiment; не читав глибоко.

### Reference only (ідеї, без копіювання коду в репо)

- **saeid00065/trade-journal** (MIT) — UI-ідеї щоденника, P&L календар, prop-firm. Broker-sync виключити.
- **MobiusQuant/OpenMobius-skill** (Apache-2.0) — SMC-knowledge. **113 MB** knowledge base → тримати зовні, не в git.
- **LLMQuant/skills** (MIT) — формат скілів; залежить від LLMQuant Data (зовнішній API).
- **SilentFleetKK/riskguard** (MIT) — ідеї circuit breaker; broker-адаптери (Alpaca) виключити.

### Rejected

| Репо | Причина |
|---|---|
| aryan-cs/grok-trader | **Немає ліцензії.** Містить `place_ioc_order`, `create_order`. Auto-trader scaffold. |
| 13empty/trading-journal | `bridge-python/mt5_sync.py` містить `mt5.order_send`. Execution-шлях. |
| Mark-Mulli/Trade-Journal | Немає ліцензії. Ідея read-only MT5 — тільки як ідея. |
| lalit8786/Trading-Journal-Analytics | Немає ліцензії. |
| atirek-pro/ForexFactory-MCP | Немає ліцензії. |
| AtaCanYmc/forex-pytory | cloudscraper обходить Cloudflare challenge — TOS-ризик. |
| ghwmelite-dotcom/claude-skills | Немає ліцензії; MQL5 EA-орієнтовано. |
| marketcalls/vectorbt-backtesting-skills | Немає ліцензії. |
| SimpleFXcom / GMGNAI / okx onchainos / Superior-Trade | Execution / wallet / DEX. Поза межами Сема. |
| agiprolabs/claude-trading-skills | MIT, але DeFi/Solana-first. |
| JoelLewis/finance_skills | MIT, але 84 compliance/advisory-скіли — надто широко. |

## Що саме перевіряв

1. Наявність LICENSE-файлу і його тип.
2. grep по всьому коду: `order_send`, `place_order`, `create_order`, захардкоджені ключі (`sk-`, `AKIA`, `ghp_`), `eval(`, `exec(`, `pickle.load`, `curl | sh`, `os.system`, `subprocess`, `requests.post`, `urlopen`.
3. `requirements.txt` / `pyproject.toml` для кожного обраного скіла.

Знахідки, які не блокують, але важливі:
- `tradermonty/claude-trading-skills` містить `scripts/run_skill_generation_pipeline.py`, що робить git push і створює PR через `subprocess`. Це CI/генерація репо, **не** копіювати в Сема.
- `riskguard` має `brokers/alpaca.py` з реальними order-запитами — лише ядро без адаптера.

## Наступний крок

- Install обраних adopt-скілів — тільки з окремим «так» Андрія.
- Defer-позиції — окрема перевірка кожного HTTP-хоста.
- Брокери — далі в окремому документі.
