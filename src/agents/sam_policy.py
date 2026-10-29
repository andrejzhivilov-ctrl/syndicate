"""Sam execution path: every tradeable signal goes to Andrii (no automatic path, 29.10)."""

from __future__ import annotations

from typing import Any, Mapping

from src.agents.sam_access import (
    load_sam_manifest,
    sam_auto_invest_allowed,
)

PROPOSE_THRESHOLD = 95.0
AUTO_THRESHOLD = 99.0
AUTO_VENUES = frozenset({"forex", "crypto"})  # venue classes only; nothing executes automatically
INVEST_VENUES = frozenset({"investment", "equities", "ibkr"})
ALL_TIMEFRAMES = ("M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN")
_INVEST_SYMBOLS = frozenset({"VOO", "QQQM", "QQQ", "AAPL", "NVDA", "MSFT", "SPY", "IVV"})


def classify_venue(symbol: str | None, venue: str | None = None) -> str:
    if venue:
        key = venue.strip().lower()
        if key in INVEST_VENUES:
            return "investment"
        if key in AUTO_VENUES:
            return key
        if key in {"mt5", "fx", "xau", "gold"}:
            return "forex"
    text = (symbol or "").upper().replace("/", "")
    if text in _INVEST_SYMBOLS or text.endswith(".US"):
        return "investment"
    if any(token in text for token in ("USDT", "USDC", "BTC", "ETH", "SOL")):
        return "crypto"
    if len(text) == 6 and text.isalpha():
        return "forex"
    return "unknown"


def layers_complete(confluence: Mapping[str, Any] | None) -> bool:
    layers = (confluence or {}).get("layers") or {}
    if not layers:
        return False
    for meta in layers.values():
        if not isinstance(meta, dict):
            return False
        if meta.get("missing") or meta.get("veto"):
            return False
        if meta.get("score") is None:
            return False
    return True


def _score(confluence: Mapping[str, Any] | None) -> float:
    raw = (confluence or {}).get("confluence_score")
    if raw is None:
        raw = (confluence or {}).get("score")
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def decide_execution(
    *,
    symbol: str | None = None,
    venue: str | None = None,
    confluence: Mapping[str, Any] | None = None,
    risk_blocked: bool = False,
    timeframe: str | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the lot path. Never sets auto_execute under empty grants."""
    data = dict(manifest or load_sam_manifest())
    classified = classify_venue(symbol, venue)
    score = _score(confluence)
    complete = layers_complete(confluence)
    tf = timeframe if timeframe in ALL_TIMEFRAMES else None
    base = {
        "venue": classified,
        "timeframe": tf,
        "analyze_all_timeframes": True,
        "confluence_score": score,
        "layers_complete": complete,
        "auto_execute": False,
        "auto_invest_allowed": sam_auto_invest_allowed(data),
        "notification": "WATCH",
    }

    if classified == "investment" or classified in INVEST_VENUES:
        return {
            **base,
            "path": "invest_discuss",
            "requires_hitl": True,
            "notification": "SIGNAL",
            "reason": "investments_always_andrii_hitl",
        }
    if risk_blocked:
        return {**base, "path": "blocked", "requires_hitl": True, "notification": "RISK", "reason": "risk_block"}
    if not complete or score < PROPOSE_THRESHOLD:
        return {**base, "path": "no_trade", "requires_hitl": True, "reason": "below_propose_or_incomplete"}
    # Operator decision 29.10: every tradeable signal, at any score, on any venue,
    # goes to Andrii. There is no automatic path left to arm.
    return {
        **base,
        "path": "hitl_signal",
        "requires_hitl": True,
        "notification": "SIGNAL",
        "reason": "propose_gate" if score < AUTO_THRESHOLD else "trading_always_andrii_hitl",
    }
