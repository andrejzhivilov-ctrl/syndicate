"""Stream quotes from a local IBKR paper terminal to Sam's market-data directory."""
import argparse
import asyncio
import json
import math
import os
import tempfile
import time
from collections import deque
from itertools import combinations

from src.data_paths import ensure_dir
from src.sam_fx_board import FILE, fresh

# Conventional base/quote order for G10 crosses. Qualify each contract at the broker.
G10 = ("EUR", "GBP", "AUD", "NZD", "USD", "CAD", "CHF", "NOK", "SEK", "JPY")
MAJORS = ("EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD")
PAIRS = tuple(dict.fromkeys((*MAJORS, *(a + b for a, b in combinations(G10, 2)))))


def update_ticks(tickers, quotes):
    for ticker in tickers:
        key = ticker.contract.symbol + ticker.contract.currency
        row = quotes.setdefault(key, {"pair": key, "bid": 0., "ask": 0., "bid_received": 0., "ask_received": 0.})
        row["data_type"] = ticker.marketDataType
        for tick in ticker.ticks:
            side = {1: "bid", 2: "ask"}.get(tick.tickType)
            if side:
                row[side] = tick.price
                row[side + "_received"] = tick.time.timestamp()


def metrics(row, history, now):
    mid = (row["bid"] + row["ask"]) / 2
    minute = int(now // 60)
    if history and history[-1][0] == minute:
        history.pop()
    history.append((minute, mid))
    vol = None
    if len(history) == 16 and history[-1][0] - history[0][0] == 15:
        prices = [p for _, p in history]
        vol = 1e4 * math.sqrt(sum(math.log(b / a) ** 2 for a, b in zip(prices[:-1], prices[1:], strict=True)))
    return {**row, "spread_bp": 1e4 * (row["ask"] - row["bid"]) / mid, "volatility_15m_bp": vol}


def publish(quotes, history, requested):
    now = time.time()
    rows = [metrics(row, history[pair], now) for pair, row in quotes.items() if fresh(row, now)]
    rows.sort(key=lambda r: (r["volatility_15m_bp"] is not None, r["volatility_15m_bp"] or 0), reverse=True)
    folder = ensure_dir("market_data")
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=folder, delete=False) as tmp:
            name = tmp.name
            json.dump({"provider": "IBKR Paper", "written_at": now, "requested_pairs": requested, "quotes": rows},
                      tmp, allow_nan=False)
        os.replace(name, folder / FILE)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


async def collect(port, limit):
    from ib_async import Forex, IB

    client = IB()
    try:
        await client.connectAsync("127.0.0.1", port, clientId=78, readonly=True, timeout=10)
        accounts = client.managedAccounts()
        if not accounts or not all(a.startswith("DU") for a in accounts):
            raise RuntimeError("The bridge requires an individual IBKR Paper session.")
        client.reqMarketDataType(1)
        pairs = PAIRS[:limit]
        contracts = await client.qualifyContractsAsync(*(Forex(pair) for pair in pairs))
        contracts = [c for c in contracts if c is not None and c.conId > 0]
        if not contracts:
            raise RuntimeError("No FX contract qualified.")
        quotes = {}
        history = {pair: deque(maxlen=16) for pair in pairs}
        client.pendingTickersEvent += lambda tickers: update_ticks(tickers, quotes)
        for contract in contracts:
            client.reqMktData(contract)
        while client.isConnected():
            await asyncio.sleep(2)
            publish(quotes, history, len(pairs))
        raise ConnectionError("Paper terminal disconnected.")
    finally:
        client.disconnect()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, choices=(7497, 4002), default=7497)
    parser.add_argument("--pairs", type=int, choices=range(1, len(PAIRS) + 1), default=28)
    args = parser.parse_args()
    asyncio.run(collect(args.port, args.pairs))


if __name__ == "__main__":
    main()
