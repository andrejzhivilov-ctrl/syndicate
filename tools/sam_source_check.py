"""Report actual public provider availability from the machine running this command."""
import asyncio
import json

from src.market_data import _crypto
from src.sam_public_sources import URLS, read


async def probe(key):
    try:
        result = await asyncio.wait_for(read(key), timeout=25)
    except asyncio.TimeoutError:
        result = {"status": "unavailable", "reason": "timeout"}
    return {"source": key, "status": result["status"], "reason": result.get("reason"),
            "retrieved_at": result.get("retrieved_at")}


async def spot_candles(venue):
    """Exercise the same public exchange call as market_data without replacing Sam's saved dataset."""
    try:
        rows = await asyncio.wait_for(asyncio.to_thread(_crypto, venue, "BTC/USDT", "1m", 2), timeout=30)
        if not rows:
            raise ValueError("no_candles")
        return {"source": venue + "_candles", "status": "ok", "rows": len(rows), "last_open_ms": rows[-1][0]}
    except Exception as exc:  # Report each venue independently, including regional/network failures.
        return {"source": venue + "_candles", "status": "unavailable", "reason": type(exc).__name__}


async def main():
    for row in await asyncio.gather(*(probe(key) for key, url in URLS.items() if url.startswith("https://")), spot_candles("binance"), spot_candles("bybit")):
        print(json.dumps(row, ensure_ascii=True))


if __name__ == "__main__":
    asyncio.run(main())
