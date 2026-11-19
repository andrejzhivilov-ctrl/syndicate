"""Use deterministic fixtures for the public, read-only research tool."""
import asyncio
import json

import httpx

from src import hermes_tools
from src.sam_public_sources import TREND_SCRIPT, read


def run(source, handler):
    return asyncio.run(read(source, httpx.MockTransport(handler)))


def test_public_book_and_failure():
    def book(request):
        assert request.url.host == "api.kraken.com"
        return httpx.Response(200, json={"error": [], "result": {"XXBTZUSD": {
            "asks": [["102", "2", 120]], "bids": [["100", "1", 121]]}}})
    result = run("btc_book", book)
    assert result["data"]["bid"] == 100
    assert result["data"]["ask_updated"] == 120
    assert run("usd_uah", lambda _: httpx.Response(429))["status"] == "unavailable"
    assert run("unknown", book)["status"] == "error"
    assert "public_research" in hermes_tools.granted("sam")
    assert "public_research" not in hermes_tools.granted("trainer")


def test_mcp_session_and_result():
    calls = []
    def provider(request):
        msg = json.loads(request.content)
        calls.append(msg["method"])
        if msg["method"] == "initialize":
            return httpx.Response(200, headers={"mcp-session-id": "demo"},
                                  json={"id": 1, "result": {"protocolVersion": "2025-03-26"}})
        assert request.headers["mcp-session-id"] == "demo"
        if msg["method"] == "notifications/initialized":
            return httpx.Response(202)
        assert msg["params"] == {"name": "execute", "arguments": {"code": TREND_SCRIPT}}
        return httpx.Response(200, headers={"Content-Type": "text/event-stream"},
                              text='data: {"id":2,"result":{"content":[{"type":"text","text":"SAM_COINS=test-coin"}]}}\n\n')
    assert run("crypto_trending", provider)["data"]["coin_ids"] == ["test-coin"]
    assert calls == ["initialize", "notifications/initialized", "tools/call"]


def test_empty_news_and_archive_not_live():
    assert run("fed_news", lambda _: httpx.Response(200, content=b"<rss><channel/></rss>"))["status"] == "unavailable"
    result = run("football_archive", lambda _: httpx.Response(200, json=[{
        "competition_id": 1, "season_id": 2, "competition_name": "Demo", "season_name": "Fixture"}]))
    assert result["research_only"] and result["data"][0]["season_id"] == 2


def test_spot_venues_preserve_clock_and_reject_bad_quotes():
    ticker = {"symbol": "BTCUSDT", "bidPrice": "100", "askPrice": "101", "bidQty": "2", "askQty": "3"}
    def binance(request):
        assert request.url.host == "data-api.binance.vision"
        return httpx.Response(200, json=ticker)
    quote = run("binance_btc_book", binance)["data"]
    assert quote["exchange_time_ms"] is None and quote["ask_size_btc"] == 3
    ticker["askPrice"] = "99"
    assert run("binance_btc_book", binance)["status"] == "unavailable"
    data = {"retCode": 0, "result": {"s": "BTCUSDT", "b": [["100", "2"]], "a": [["101", "3"]], "ts": 123000}}
    def bybit(request):
        assert request.url.params["category"] == "spot"
        return httpx.Response(200, json=data)
    assert run("bybit_btc_book", bybit)["data"]["exchange_time_ms"] == 123000
    data["retCode"] = 10006
    assert run("bybit_btc_book", bybit)["status"] == "unavailable"


def test_binance_public_spot_candles(monkeypatch):
    from src import market_data

    def get(url, *, params, timeout):
        assert url == "https://data-api.binance.vision/api/v3/klines"
        assert params == {"symbol": "BTCUSDT", "interval": "1m", "limit": 1000}
        return httpx.Response(200, request=httpx.Request("GET", url),
                              json=[[123000, "10", "12", "9", "11", "5", 182999]])
    monkeypatch.setattr(market_data.httpx, "get", get)
    assert market_data._crypto("binance", "BTC/USDT", "1m", 2000) == [[123000, 10, 12, 9, 11, 5]]
