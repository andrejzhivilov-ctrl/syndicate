"""Keyless public research feeds for Sam. No account, order or wallet methods."""
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone

import httpx

from src.learning_feeds import parse_feed

TREND_SCRIPT = ("async function run(client) { const data = await client.search.trending.get(); "
                "return 'SAM_COINS=' + data.coins.slice(0, 15).map(x => x.item.id).join(','); }")
MCP = "https://mcp.api.coingecko.com/mcp"
URLS = {
    "ibkr_fx": "local:ibkr-paper-fx",
    "crypto_trending": MCP,
    "binance_btc_book": "https://data-api.binance.vision/api/v3/ticker/bookTicker?symbol=BTCUSDT",
    "bybit_btc_book": "https://api.bybit.com/v5/market/orderbook?category=spot&symbol=BTCUSDT&limit=1",
    "btc_book": "https://api.kraken.com/0/public/Depth?pair=XBTUSD&count=1",
    "usd_uah": "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=USD&json",
    "fed_news": "https://www.federalreserve.gov/feeds/press_all.xml",
    "ecb_news": "https://www.ecb.europa.eu/rss/press.html",
    "cme_video": "https://www.youtube.com/feeds/videos.xml?channel_id=UCLC4PuFlyKwK03Sc29YLEGQ",
    "nba_games": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    "atp_events": "https://site.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard",
    "epl_events": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard",
    "dota_results": "https://api.opendota.com/api/proMatches",
    "football_archive": "https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json",
}
LIMIT = 2_000_000


async def _read(client, method, url, **kwargs):
    async with client.stream(method, url, **kwargs) as response:
        response.raise_for_status()
        body = bytearray()
        async for chunk in response.aiter_bytes():
            if len(body) + len(chunk) > LIMIT:
                raise ValueError("response_too_large")
            body.extend(chunk)
        return bytes(body), response.headers


def _rpc_result(body, request_id):
    packets = [x[5:].strip() for x in body.splitlines() if x.startswith(b"data:")]
    for raw in packets or [body]:
        msg = json.loads(raw)
        if isinstance(msg, dict) and msg.get("id") == request_id and "result" in msg:
            return msg["result"]
    raise ValueError("mcp_missing_result")


async def _post_rpc(client, headers, packet, request_id):
    async with client.stream("POST", MCP, json=packet, headers=headers) as response:
        response.raise_for_status()
        if response.headers.get("mcp-session-id"):
            headers["mcp-session-id"] = response.headers["mcp-session-id"]
        if request_id is None:
            return None
        body = bytearray()
        streaming = "text/event-stream" in response.headers.get("content-type", "")
        async for chunk in response.aiter_bytes():
            body.extend(chunk)
            if len(body) > LIMIT:
                raise ValueError("response_too_large")
            if streaming and b"\n\n" in body.replace(b"\r\n", b"\n"):
                try:
                    return _rpc_result(bytes(body), request_id)
                except ValueError:
                    pass  # A notification or an incomplete response may precede the reply.
        return _rpc_result(bytes(body), request_id)


async def _trending(client):
    headers = {"Accept": "application/json, text/event-stream"}
    async def send(method, params, request_id=None):
        packet = {"jsonrpc": "2.0", "method": method, "params": params}
        if request_id is not None:
            packet["id"] = request_id
        return await _post_rpc(client, headers, packet, request_id)
    hello = await send("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                     "clientInfo": {"name": "syndicate-paper", "version": "1"}}, 1)
    headers["MCP-Protocol-Version"] = hello["protocolVersion"]
    await send("notifications/initialized", {})
    result = await send("tools/call", {"name": "execute", "arguments": {"code": TREND_SCRIPT}}, 2)
    if result.get("isError") or not result.get("content"):
        raise ValueError("mcp_trending_unavailable")
    text = "\n".join(c.get("text", "") for c in result["content"] if c.get("type") == "text")
    match = re.search(r"SAM_COINS=([a-z0-9-]+(?:,[a-z0-9-]+)*)", text)
    if not match:
        raise ValueError("empty_trending")
    return {"coin_ids": match.group(1).split(",")}


def _book(data, now):
    if data.get("error"):
        raise ValueError("exchange_error")
    book = next(iter(data["result"].values()), {})
    bid, ask = book["bids"][0], book["asks"][0]
    bp, ap = float(bid[0]), float(ask[0])
    if not all(map(math.isfinite, (bp, ap))) or not 0 < bp <= ap:
        raise ValueError("invalid_book")
    return {"pair": "BTC/USD", "bid": bp, "ask": ap, "bid_updated": bid[2],
            "ask_updated": ask[2], "oldest_level_age_s": now.timestamp() - min(int(bid[2]), int(ask[2]))}


def _spot_top(source, data):
    if source == "bybit_btc_book":
        if data["retCode"] != 0:
            raise ValueError("exchange_error")
        book = data["result"]
        symbol = book["s"]
        bid, bid_size = book["b"][0]
        ask, ask_size = book["a"][0]
        timestamp_ms = int(book["ts"])
        if timestamp_ms <= 0:
            raise ValueError("invalid_timestamp")
    else:
        symbol = data["symbol"]
        bid, bid_size = data["bidPrice"], data["bidQty"]
        ask, ask_size = data["askPrice"], data["askQty"]
        timestamp_ms = None  # REST bookTicker has no exchange timestamp.
    prices = [float(n) for n in (bid, ask, bid_size, ask_size)]
    if symbol != "BTCUSDT" or not all(math.isfinite(n) and n > 0 for n in prices) or prices[0] > prices[1]:
        raise ValueError("invalid_spot_quote")
    return {"pair": "BTC/USDT", "bid": prices[0], "ask": prices[1], "bid_size_btc": prices[2],
            "ask_size_btc": prices[3], "exchange_time_ms": timestamp_ms}


def _scoreboard(data):
    return {"events": [{"id": e["id"], "name": e["name"], "scheduled_at": e["date"],
                        "status": e.get("status", {}).get("type", {}).get("name")}
                       for e in data["events"][:30]]}


def _digest(key, body, now):
    if key in {"fed_news", "ecb_news", "cme_video"}:
        return [{"title": e["title"], "url": e["url"],
                 "published": e["when"].isoformat() if e["when"] else None}
                for e in parse_feed(body)[:8] if e["title"] and e["url"]]
    data = json.loads(body)
    if key in {"binance_btc_book", "bybit_btc_book"}:
        return _spot_top(key, data)
    if key in {"nba_games", "atp_events", "epl_events"}:
        return _scoreboard(data)
    if key == "btc_book":
        return _book(data, now)
    if key == "usd_uah":
        return [{"currency": r["cc"], "rate": r["rate"], "effective_date": r["exchangedate"]}
                for r in data if r["cc"] == "USD" and float(r["rate"]) > 0]
    fields = (("match_id", "start_time", "league_name", "radiant_win") if key == "dota_results"
              else ("competition_id", "season_id", "competition_name", "season_name"))
    return [{k: row[k] for k in fields} for row in data[:10]]


async def read(source, transport=None):
    if source == "ibkr_fx":
        from src.sam_fx_board import snapshot
        return snapshot()
    url = URLS.get(source)
    if not url:
        return {"status": "error", "reason": "unknown_source", "sources": sorted(URLS)}
    try:
        async with httpx.AsyncClient(timeout=12, transport=transport, follow_redirects=False) as client:
            if source == "crypto_trending":
                result = await _trending(client)
            else:
                body, _ = await _read(client, "GET", url)
                result = _digest(source, body, datetime.now(timezone.utc))
        if not result:
            raise ValueError("empty_result")
    except (httpx.HTTPError, ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        reason = (f"http_{exc.response.status_code}" if isinstance(exc, httpx.HTTPStatusError) else type(exc).__name__)
        return {"status": "unavailable", "source": source, "url": url, "reason": reason}
    return {"status": "ok", "source": source, "url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "research_only": True, "data": result}
