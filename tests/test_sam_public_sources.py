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
