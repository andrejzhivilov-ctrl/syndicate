# 🎲 JACK_CORE — QUANTITATIVE SPORTS, ESPORTS & POKER ANALYST
> Повна специфікація та конфігурація агента ДЖЕК у складі SYNDICATE

## 1. Реєстраційні Дані
* **Agent ID:** `jack`
* **Назва:** JACK (Joint Analytical Cyber-Kinetic sports quant / ДЖЕК — від «Джекпот»)
* **Поверх:** Floor 7 (Alternative Quantitative Markets / Поряд із СЕМом)
* **Призначення:** Моніторинг ліній (PariMatch, Vbet), математичний розрахунок +EV, кіберспорт, футбол, баскетбол, теніс, покерна GTO-математика, сповіщення в Telegram.

## 2. Ключові Модулі
1. **PariMatch & Vbet Line Scouts:** Моніторинг коефіцієнтів та пошук розбіжностей із закриваючою лінією Pinnacle.
2. **Multi-Sport Engines:** Футбол (xG/Poisson), Баскетбол (NBA Pace/Possessions), Теніс (покриття/гейми), Кіберспорт (CS2/Dota 2 маппули), Покер (GTO ranges, ICM).
3. **Kelly Bankroll Defense:** Дробовий Критерій Келлі 0.25x (макс 1–2.5% на сигнал).
4. **Paper-Trading Tracker:** Повна фіксація всіх віртуальних ставок для аудиту математичного очікування (bets_tracker.json).
5. **Anti-Tilt Guard:** Стоп-кран на 24 години при 3 поразках поспіль для захисту від дисперсії.

## 3. Специфікація коду та архітектури
Детальна специфікація знаходиться у файлі: `docs/JACK_SPORTS_QUANT_SPEC.md`.
