"""Sam's strategy tournament on paper (Andrii, 19.11.2026: "not one strategy: test many, compare, choose").

Each strategy is plain code over candles: no model, no tokens, the same answer every time. They run
side by side on the same instruments, each tagged, and ``sam_paper.stats`` compares them honestly.
Sam (the agent) adds his own discretionary and fundamental trades with their own tags through the
paper tools; those enter the same tournament.

Every signal obeys Andrii's rules: a stop always, reward at least 2.5 times the risk, one open trade
per strategy and instrument, sizes from sam_paper (risk per trade, leverage cap, loss limits).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd

from src import sam_paper

MIN_RR = 2.5


@dataclass(frozen=True)
class Signal:
    side: str
    entry: float
    stop: float
    reason: str

    def target(self) -> float:
        risk = abs(self.entry - self.stop)
        return self.entry + MIN_RR * risk if self.side == "long" else self.entry - MIN_RR * risk


def atr(frame: pd.DataFrame, n: int = 14) -> pd.Series:
    prev = frame["close"].shift()
    true_range = pd.concat([frame["high"] - frame["low"], (frame["high"] - prev).abs(), (frame["low"] - prev).abs()], axis=1)
    return true_range.max(axis=1).rolling(n).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + gain / loss.replace(0, float("nan")))


def _cross(fast: pd.Series, slow: pd.Series) -> int:
    """+1 fast crossed above slow on the last closed bar, -1 below, 0 none."""
    if len(fast) < 3:
        return 0
    before, now = fast.iloc[-3] - slow.iloc[-3], fast.iloc[-2] - slow.iloc[-2]
    return 1 if before <= 0 < now else -1 if before >= 0 > now else 0


def levels(frame: pd.DataFrame) -> Optional[Signal]:
    """Andrii's way: yesterday's high and low as levels; a close through one is the trade."""
    if len(frame) < 40:
        return None
    days = frame.groupby(frame.index.date)
    if len(days) < 2:
        return None
    yesterday = list(days)[-2][1]
    high, low = float(yesterday["high"].max()), float(yesterday["low"].min())
    a = float(atr(frame).iloc[-2])
    prev, last = float(frame["close"].iloc[-3]), float(frame["close"].iloc[-2])
    if prev <= high < last:
        return Signal("long", last, high - a, f"закриття вище вчорашнього максимуму {high:.5g}")
    if prev >= low > last:
        return Signal("short", last, low + a, f"закриття нижче вчорашнього мінімуму {low:.5g}")
    return None


def trend_ema(frame: pd.DataFrame) -> Optional[Signal]:
    if len(frame) < 60:
        return None
    cross = _cross(frame["close"].ewm(span=20).mean(), frame["close"].ewm(span=50).mean())
    if not cross:
        return None
    last, a = float(frame["close"].iloc[-2]), float(atr(frame).iloc[-2])
    side = "long" if cross > 0 else "short"
    return Signal(side, last, last - 1.5 * a if side == "long" else last + 1.5 * a, f"EMA20 перетнула EMA50 ({side})")


def mean_reversion(frame: pd.DataFrame) -> Optional[Signal]:
    if len(frame) < 210:
        return None
    r, last = float(rsi(frame["close"]).iloc[-2]), float(frame["close"].iloc[-2])
    trend = float(frame["close"].ewm(span=200).mean().iloc[-2])
    a = float(atr(frame).iloc[-2])
    if r < 30 and last > trend:
        return Signal("long", last, last - a, f"RSI {r:.0f} у висхідному тренді")
    if r > 70 and last < trend:
        return Signal("short", last, last + a, f"RSI {r:.0f} у низхідному тренді")
    return None


def breakout(frame: pd.DataFrame) -> Optional[Signal]:
    if len(frame) < 30:
        return None
    window = frame.iloc[-22:-2]
    last, a = float(frame["close"].iloc[-2]), float(atr(frame).iloc[-2])
    if last > float(window["high"].max()):
        return Signal("long", last, last - 1.5 * a, "пробій 20-барного максимуму")
    if last < float(window["low"].min()):
        return Signal("short", last, last + 1.5 * a, "пробій 20-барного мінімуму")
    return None


def scalp(frame: pd.DataFrame) -> Optional[Signal]:
    if len(frame) < 40:
        return None
    cross = _cross(frame["close"].ewm(span=9).mean(), frame["close"].ewm(span=21).mean())
    if not cross:
        return None
    last, a = float(frame["close"].iloc[-2]), float(atr(frame).iloc[-2])
    side = "long" if cross > 0 else "short"
    return Signal(side, last, last - a if side == "long" else last + a, f"скальп EMA9/21 ({side})")


Rule = Callable[[pd.DataFrame], Optional[Signal]]
#: name -> (rule, timeframe, risk per trade, style). Andrii's style mix: scalp 10 / day 30 / mid 40 / long 20.
STRATEGIES: Dict[str, Tuple[Rule, str, float, str]] = {
    "levels_15m": (levels, "15m", 0.01, "day"),
    "breakout_1h": (breakout, "1h", 0.01, "mid"),
    "trend_ema_1h": (trend_ema, "1h", 0.01, "mid"),
    "mean_reversion_15m": (mean_reversion, "15m", 0.0075, "day"),
    "scalp_1m": (scalp, "1m", 0.005, "scalp"),
}
#: (account, source, symbol). Yahoo's 1-minute bars are too thin for scalping, so scalping is crypto only.
INSTRUMENTS: List[Tuple[str, str, str]] = [
    ("crypto", "binance", "BTC/USDT"), ("crypto", "binance", "ETH/USDT"), ("crypto", "binance", "SOL/USDT"),
    ("trading", "yahoo", "EURUSD=X"), ("trading", "yahoo", "GBPUSD=X"), ("trading", "yahoo", "USDJPY=X"),
    ("trading", "yahoo", "GC=F"), ("trading", "yahoo", "SI=F"), ("trading", "yahoo", "^GSPC"), ("trading", "yahoo", "CL=F"),
]


def frame_of(rows: List[List[Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])
    frame.index = pd.to_datetime(frame["time"], unit="ms", utc=True)
    return frame


Fetch = Callable[[str, str, str, int], List[List[Any]]]


def run(ledger: Dict[str, Any], fetch: Fetch, names: Optional[List[str]] = None,
        now: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """One pass: every chosen strategy over every instrument; new paper trades come back."""
    opened, cache = [], {}
    for name in names or list(STRATEGIES):
        rule, timeframe, risk, _style = STRATEGIES[name]
        for account, source, symbol in INSTRUMENTS:
            if timeframe == "1m" and source == "yahoo":
                continue
            if any(t["strategy"] == name and t["symbol"] == symbol for t in ledger["open"]):
                continue
            key = (source, symbol, timeframe)
            if key not in cache:
                try:
                    cache[key] = frame_of(fetch(source, symbol, timeframe, 300))
                except Exception:  # noqa: BLE001 - one dead source skips its instruments, never the tournament
                    cache[key] = None
            frame = cache[key]
            signal = rule(frame) if frame is not None and len(frame) else None
            if signal is None or not signal.entry > 0 or signal.stop <= 0:
                continue
            made = sam_paper.open_trade(ledger, account=account, strategy=name, source=source, symbol=symbol,
                                        side=signal.side, entry=signal.entry, stop=signal.stop, target=signal.target(),
                                        risk=risk, timeframe=timeframe, reason=signal.reason, now=now)
            if made["status"] == "ok":
                opened.append(made["trade"])
    return opened


def mark_open(ledger: Dict[str, Any], fetch: Fetch, now: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """Check every open trade's stop and target against fresh short candles."""
    closed = []
    for source, symbol in {(t["source"], t["symbol"]) for t in ledger["open"]}:
        try:
            rows = fetch(source, symbol, "1m" if source != "yahoo" else "5m", 120)
        except Exception:  # noqa: BLE001 - try again next minute
            continue
        candles = [{"time": datetime.fromtimestamp(r[0] / 1000, timezone.utc), "high": r[2], "low": r[3]} for r in rows]
        closed += sam_paper.mark(ledger, source, symbol, candles, now)
    return closed
