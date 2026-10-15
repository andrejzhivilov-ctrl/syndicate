---
name: jack-line-scout
description: Read authorized sportsbook odds with explicit coverage and source timestamps.
---

# jack-line-scout

Use scout with sport_key and h2h/spreads/totals only when the operator configured The Odds API credentials. Inspect coverage for parimatch, vbet, pinnacle and betfair. Missing coverage is unavailable, never a fabricated quote. Do not bypass bookmaker access restrictions or treat opening odds as closing-line evidence. Correlate event, market, point, selection and timestamps before comparing prices. Use alert only to format a draft; Telegram delivery is not enabled by this worker. Read docs/DIRECTOR_SKILLS_CATALOG.md for statistics and uncertainty candidates.
