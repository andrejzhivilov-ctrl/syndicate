---
name: jack-paper-risk
description: Evaluate +EV signals and maintain an auditable paper-only bankroll log.
---

# jack-paper-risk

evaluate requires probability, decimal_odds, bankroll, observed_at and model_source. Reject stale/future odds; threshold is EV >= 0.045. Quarter Kelly is capped at 1 percent per event by default, configurable up to 2.5 percent by the operator. record_paper additionally requires event_id, market and selection; open event exposure is capped and duplicate selections rejected. settle_paper is single-use with win/loss/void. Three consecutive losses settled on one UTC day halt new recommendations for 24 hours. Report paper ROI with sample size; fewer than 1000 settled bets is preliminary. Never place a real bet.
