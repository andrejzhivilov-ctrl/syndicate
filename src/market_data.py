"""Market data for Sam: candles from crypto exchanges and Yahoo Finance (19.11.2026).

Read-only public data, no keys: crypto through ccxt (Binance, Bybit, OKX, Kraken), forex, futures, metals,
indices and stocks through yfinance. Every answer says where the numbers came from and when; nothing
is filled in (AGENTS.md §1). The full series is kept on the server as a dataset the agent passes to
``run_python`` by id, so a long series never floods the conversation.
"""
from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx

from src.code_sandbox import dataset_dir

CRYPTO = ("binance", "bybit", "okx", "kraken")
YAHOO = "yahoo"
SOURCES = CRYPTO + (YAHOO,)
TIMEFRAMES = {"1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"}
YAHOO_INTERVAL = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "60m", "4h": "60m", "1d": "1d", "1w": "1wk"}
YAHOO_PERIOD = {"1m": "5d", "5m": "30d", "15m": "30d", "30m": "30d", "60m": "365d", "1d": "5y", "1wk": "10y"}
MAX_LIMIT = 2_000
PREVIEW_ROWS = 10
SYMBOL = re.compile(r"^[A-Za-z0-9=^./:_-]{1,30}$")


def _crypto(source: str, symbol: str, timeframe: str, limit: int) -> List[List[Any]]:
    if source == "binance" and re.fullmatch(r"[A-Z0-9]+/USDT", symbol):
        # Spot-only public host. Futures and other symbol conventions stay on CCXT.
        response = httpx.get("https://data-api.binance.vision/api/v3/klines",
                             params={"symbol": symbol.replace("/", ""), "interval": timeframe,
                                     "limit": min(limit, 1000)}, timeout=20)
        response.raise_for_status()
        return [[int(row[0]), *(float(n) for n in row[1:6])] for row in response.json()]

    import ccxt

    exchange = getattr(ccxt, source)({"timeout": 20_000, "enableRateLimit": True})
    return [[row[0], row[1], row[2], row[3], row[4], row[5]] for row in exchange.fetch_ohlcv(symbol, timeframe, limit=limit)]


def _yahoo(symbol: str, timeframe: str, limit: int) -> List[List[Any]]:
    import yfinance

    interval = YAHOO_INTERVAL[timeframe]
    frame = yfinance.Ticker(symbol).history(period=YAHOO_PERIOD[interval], interval=interval, auto_adjust=False)
    if timeframe == "4h" and not frame.empty:
        frame = frame.resample("4h").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last",
                                          "Volume": "sum"}).dropna()
    rows = [[int(index.timestamp() * 1000), float(row["Open"]), float(row["High"]), float(row["Low"]),
             float(row["Close"]), float(row["Volume"])] for index, row in frame.iterrows()]
    return rows[-limit:]


def _dataset_id(source: str, symbol: str, timeframe: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "-", f"{source}_{symbol}_{timeframe}")


def _iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M")


async def candles(source: str, symbol: str, timeframe: str = "1h", limit: int = 500) -> Dict[str, Any]:
    source, timeframe = source.lower().strip(), timeframe.lower().strip()
    if source not in SOURCES:
        return {"status": "error", "error": "unknown_source", "available_sources": list(SOURCES),
                "hint": "crypto: binance/bybit/okx/kraken with BTC/USDT; forex, metals, futures, stocks: yahoo with "
                        "EURUSD=X, GC=F, CL=F, ^GSPC, SPY"}
    if timeframe not in TIMEFRAMES:
        return {"status": "error", "error": "unknown_timeframe", "available_timeframes": sorted(TIMEFRAMES)}
    if not SYMBOL.match(symbol or ""):
        return {"status": "error", "error": "bad_symbol"}
    limit = max(1, min(int(limit or 500), MAX_LIMIT))
    try:
        rows = await asyncio.to_thread(_yahoo, symbol, timeframe, limit) if source == YAHOO \
            else await asyncio.to_thread(_crypto, source, symbol, timeframe, limit)
    except Exception as exc:  # noqa: BLE001 - a market source failing is reported, never guessed
        return {"status": "unavailable", "reason": f"{source}_{type(exc).__name__}", "detail": str(exc)[:160]}
    if not rows:
        return {"status": "unavailable", "reason": "no_data", "source": source, "symbol": symbol}
    dataset = _dataset_id(source, symbol, timeframe)
    lines = ["time_utc,open,high,low,close,volume"] + [f"{_iso(r[0])},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]}" for r in rows]
    (dataset_dir() / f"{dataset}.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    closes = [r[4] for r in rows]
    return {"status": "ok", "source": source, "symbol": symbol, "timeframe": timeframe, "rows": len(rows),
            "from": _iso(rows[0][0]), "to": _iso(rows[-1][0]), "last_close": closes[-1],
            "change_pct": round((closes[-1] / closes[0] - 1) * 100, 3) if closes[0] else None,
            "high": max(r[2] for r in rows), "low": min(r[3] for r in rows),
            "dataset": dataset, "preview": lines[:1] + lines[-PREVIEW_ROWS:],
            "note": "Повний ряд передай у run_python через datasets=[dataset]; файл там зветься <dataset>.csv."}
