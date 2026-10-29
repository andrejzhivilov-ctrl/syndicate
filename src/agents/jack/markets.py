"""One shape for markets from any bookmaker, exchange or odds API.

Lines from different sources are only comparable after they agree on the market
type, the line and the selection names. Anything that does not fit is rejected
with a reason instead of being guessed into shape.
"""
from __future__ import annotations

from datetime import datetime, timezone

from src.agents.director_base import number, text

MARKET_TYPES = {
    "1x2": ("home", "draw", "away"),
    "moneyline": ("home", "away"),
    "double_chance": ("1x", "x2", "12"),
    "handicap": ("home", "away"),
    "total": ("over", "under"),
    "btts": ("yes", "no"),
}
LINED = frozenset({"handicap", "total"})


def normalize(payload: dict) -> dict:
    market = text(payload.get("market"), "market", 40).lower()
    if market not in MARKET_TYPES:
        raise ValueError("unsupported_market")
    line = None
    if market in LINED:
        line = number(payload.get("line"), "line", -100, 1000)
        if (line * 4) % 1:
            raise ValueError("line_not_in_quarter_steps")
    elif payload.get("line") is not None:
        raise ValueError("line_not_expected")
    raw = payload.get("selections")
    if not isinstance(raw, dict):
        raise ValueError("invalid_selections")
    names = {str(k).strip().lower(): v for k, v in raw.items()}
    expected = MARKET_TYPES[market]
    if set(names) != set(expected):
        raise ValueError("selections_do_not_match_market")
    observed = datetime.fromisoformat(text(payload.get("observed_at"), "observed_at", 64))
    if observed.tzinfo is None:
        raise ValueError("odds_time_must_be_aware")
    return {"event_id": text(payload.get("event_id"), "event_id", 200),
            "sport": text(payload.get("sport"), "sport", 40).lower(),
            "bookmaker": text(payload.get("bookmaker"), "bookmaker", 80).lower(),
            "market": market, "line": line,
            "selections": [{"name": n, "odds": number(names[n], "odds", 1.000001, 10000)} for n in expected],
            "observed_at": observed.astimezone(timezone.utc).isoformat()}
