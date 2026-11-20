"""Sam's strategy tournament on paper (Andrii, 19.11.2026: "not one strategy: test many, compare, choose").

Each strategy is a rule from the catalog (src/sam_catalog.py, src/sam_rules.py) over candles: no model,
no tokens, the same answer every time. Only strategies on ``paper`` run. They run
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

from src import sam_backtest, sam_catalog, sam_paper

MIN_RR = 2.5


@dataclass(frozen=True)
class Signal:
    side: str
    entry: float
    stop: float
    reason: str
    rr: float = MIN_RR

    def target(self) -> float:
        risk = abs(self.entry - self.stop)
        reward = max(self.rr, MIN_RR) * risk
        return self.entry + reward if self.side == "long" else self.entry - reward


def signal_now(spec: Dict[str, Any], frame: pd.DataFrame) -> Optional[Signal]:
    """The catalog rule on the last closed bar (the last row is still forming)."""
    if len(frame) < max(int(spec.get("min_bars") or 0), 3):
        return None
    marks = sam_backtest.signals(spec, frame)
    for side in ("long", "short"):
        if marks[side] is not None and bool(marks[side].iat[-2]):
            entry, stop = float(frame["close"].iat[-2]), float(marks[f"stop_{side}"].iat[-2])
            return Signal(side, entry, stop, f"{spec.get('title', spec['id'])} ({side})", float(spec.get("rr") or MIN_RR))
    return None


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


def instruments_for(spec: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """The instruments a strategy trades: its markets, and no Yahoo for one-minute bars (too thin)."""
    return [(account, source, symbol) for account, source, symbol in INSTRUMENTS
            if account in spec.get("markets", ()) and not (spec.get("timeframe") == "1m" and source == "yahoo")]


def run(ledger: Dict[str, Any], fetch: Fetch, names: Optional[List[str]] = None,
        now: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """One pass: every chosen catalog strategy (default: all on paper but scalping) over its instruments."""
    every = sam_catalog.specs()
    chosen = {n: every[n] for n in names if n in every} if names else sam_catalog.active(exclude=("1m",))
    opened, cache = [], {}
    for name, spec in chosen.items():
        timeframe = spec["timeframe"]
        for account, source, symbol in instruments_for(spec):
            if any(t["strategy"] == name and t["symbol"] == symbol for t in ledger["open"]):
                continue
            key = (source, symbol, timeframe)
            if key not in cache:
                try:
                    cache[key] = frame_of(fetch(source, symbol, timeframe, max(300, int(spec.get("min_bars") or 0) + 60)))
                except Exception:  # noqa: BLE001 - one dead source skips its instruments, never the tournament
                    cache[key] = None
            frame = cache[key]
            try:
                signal = signal_now(spec, frame) if frame is not None and len(frame) else None
            except Exception:  # noqa: BLE001 - a broken rule skips its own turn, never the others'
                signal = None
            if signal is None or not signal.entry > 0 or signal.stop <= 0:
                continue
            made = sam_paper.open_trade(ledger, account=account, strategy=name, source=source, symbol=symbol,
                                        side=signal.side, entry=signal.entry, stop=signal.stop, target=signal.target(),
                                        risk=float(spec["risk"]), timeframe=timeframe, reason=signal.reason, now=now)
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
