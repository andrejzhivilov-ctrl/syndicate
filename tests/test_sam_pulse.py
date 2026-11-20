"""Sam's market pulse from primary sources (Andrii, 20.11.2026)."""

from __future__ import annotations

import asyncio
import json

import httpx

from src import agent_schedule, hermes_tools, sam_pulse

RSS = (b'<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>'
       b'<item><title>Fed holds rates</title><link>https://example.org/a</link>'
       b'<pubDate>Fri, 20 Nov 2026 10:00:00 GMT</pubDate><description>text</description></item></channel></rss>')
TELEGRAM = (b'<div class="tgme_widget_message_text js-message_text" dir="auto">New listing: <b>ABC</b></div>'
            b'<time datetime="2026-11-20T11:01:19+00:00">')


def _payload(request: httpx.Request):  # noqa: C901 - one fake internet, one branch per host
    host, path = request.url.host, request.url.path
    if host == "api.bybit.com" and path.endswith("tickers"):
        return {"result": {"list": [{"lastPrice": "59257.7", "price24hPcnt": "-0.0613", "fundingRate": "-0.0000686",
                                     "openInterestValue": "4190816600"}]}}
    if host == "api.bybit.com":
        return {"result": {"list": [{"buyRatio": "0.7396"}] + [{"buyRatio": "0.70"}] * 24}}
    if host == "api.alternative.me":
        return {"data": [{"value": "12", "value_classification": "Extreme Fear", "timestamp": "1795132800"}]}
    if host == "stablecoins.llama.fi":
        return {"peggedAssets": [{"pegType": "peggedUSD", "circulating": {"peggedUSD": 300e9},
                                  "circulatingPrevDay": {"peggedUSD": 299e9}, "circulatingPrevWeek": {"peggedUSD": 295e9}}]}
    if host == "nfs.faireconomy.media":
        return [{"title": "CPI m/m", "country": "USD", "date": "2099-01-01T08:30:00-05:00", "impact": "High",
                 "forecast": "0.3%", "previous": "0.2%"},
                {"title": "Minor", "country": "NZD", "date": "2099-01-01T08:30:00-05:00", "impact": "Low"}]
    if host == "gamma-api.polymarket.com":
        return [{"question": "Fed cut in December?", "outcomes": '["Yes","No"]', "outcomePrices": '["0.31","0.69"]',
                 "volume24hr": 1200000, "endDate": "2026-12-09T23:59:00Z"},
                {"question": "Who wins a song contest?", "outcomes": '["A"]', "outcomePrices": '["1"]'}]
    if host == "publicreporting.cftc.gov":
        return [{"market_and_exchange_names": "GOLD", "report_date_as_yyyy_mm_dd": "2026-11-10T00:00:00.000",
                 "open_interest_all": "500000", "noncomm_positions_long_all": "300000",
                 "noncomm_positions_short_all": "100000", "comm_positions_long_all": "50000",
                 "comm_positions_short_all": "250000"}]
    if host == "site.api.espn.com":
        return {"injuries": [{"displayName": "Hawks", "injuries": [{"athlete": {"displayName": "X"}, "status": "Out"}]}]}
    return None


def _handler(blocked=()):
    def handle(request: httpx.Request) -> httpx.Response:
        host = request.url.host
        if host in blocked:
            return httpx.Response(403, content=b"forbidden")
        if host == "t.me":
            return httpx.Response(200, content=TELEGRAM)
        if host in {"news.google.com", "www.federalreserve.gov", "www.ecb.europa.eu", "www.bankofengland.co.uk",
                    "www.boj.or.jp"}:
            return httpx.Response(200, content=RSS)
        data = _payload(request)
        return httpx.Response(200, json=data) if data is not None else httpx.Response(404)
    return httpx.MockTransport(handle)


def _ctx(keys=None, blocked=()):
    return sam_pulse.Context(sam_pulse.config(), dict(keys or {}), _handler(blocked))


def test_every_free_source_answers_from_its_own_data_and_keeps_a_history(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    ctx = _ctx()
    free = [n for n, s in sam_pulse.SOURCES.items() if not s.keys]
    results = {n: asyncio.run(sam_pulse.collect(n, ctx)) for n in free}
    assert all(r["status"] == "ok" for r in results.values()), {n: r.get("reason") for n, r in results.items()}
    assert "у лонгах 74.0% акаунтів" in results["crypto_positioning"]["data"]["summary"][0]
    assert "великі спекулянти нетто +200,000" in results["cot"]["data"]["summary"][0]
    assert results["calendar"]["data"]["items"][0]["event"] == "CPI m/m" and len(results["calendar"]["data"]["items"]) == 1
    assert [i["question"] for i in results["polymarket"]["data"]["items"]] == ["Fed cut in December?"]
    assert results["telegram"]["data"]["items"][0]["text"] == "New listing: ABC"
    assert "+1,000 млн" in results["stablecoins"]["data"]["summary"][0]
    history = (tmp_path / "sam_pulse" / "history" / "fear_greed.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(history) == 1 and json.loads(history[0])["data"]["items"][0]["value"] == 12


def test_a_missing_key_or_a_blocked_site_is_named_never_filled_in(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    ctx = _ctx(blocked={"api.alternative.me"})
    for name, source in sam_pulse.SOURCES.items():
        if source.keys:
            result = asyncio.run(sam_pulse.collect(name, ctx))
            assert result["status"] == "unavailable" and result["key"] in source.keys, name
    blocked = asyncio.run(sam_pulse.collect("fear_greed", ctx))
    assert blocked == {**blocked, "status": "unavailable", "reason": "http_403"}
    assert not (tmp_path / "sam_pulse" / "history" / "fear_greed.jsonl").exists()  # a failure is no data point
    digest = sam_pulse.digest()
    assert digest["missing"]["fred"] == "fred_api_key" and digest["missing"]["fear_greed"] == "http_403"


def test_line_moves_are_measured_against_the_last_snapshot(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    prices = iter([2.0, 1.8])

    def handle(request: httpx.Request) -> httpx.Response:
        price = next(prices) if "soccer_epl" in request.url.path else 2.0
        return httpx.Response(200, json=[{"id": "e1", "home_team": "A", "away_team": "B", "commence_time": "2026-11-22",
                                          "bookmakers": [{"markets": [{"outcomes": [{"name": "A", "price": price}]}]}]}])

    ctx = sam_pulse.Context(sam_pulse.config(), {"odds_api_key": "k"}, httpx.MockTransport(handle))
    asyncio.run(sam_pulse.collect("sports_odds", ctx))
    second = asyncio.run(sam_pulse.collect("sports_odds", ctx))
    epl = next(i for i in second["data"]["items"] if i["sport"] == "soccer_epl")
    assert epl["move_pct"] == {"A": -10.0} and "рух коефіцієнтів" in second["data"]["summary"][0]


def test_x_is_paid_counted_and_stopped_at_the_monthly_cap(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SAM_X_MONTHLY_USD", "0.6")
    sent = []

    def handle(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        assert request.headers["Authorization"] == "Bearer xk"
        return httpx.Response(200, json={
            "output": [{"type": "message", "content": [{"type": "output_text", "text": "1. Fed: пауза",
                                                        "annotations": [{"url": "https://x.com/a/status/1"}]}]}],
            "usage": {"input_tokens": 1000, "output_tokens": 200,
                      "server_side_tool_usage_details": {"x_posts_fetched": 40, "x_users_fetched": 0}}})

    assert asyncio.run(sam_pulse.x_search(_ctx()))["key"] == "xai_api_key"
    ctx = sam_pulse.Context(sam_pulse.config(), {"grok_api_key": "xk"}, httpx.MockTransport(handle))
    first = asyncio.run(sam_pulse.x_search(ctx, handles=["@whale_alert", "bad handle!"]))
    assert first["status"] == "ok" and first["cost_usd"] == round(40 * 0.005 + 1000 * 1.25e-6 + 200 * 2.5e-6, 4)
    tool = sent[0]["tools"][0]
    assert tool["type"] == "x_search" and tool["allowed_x_handles"] == ["whale_alert"] and sent[0]["max_turns"] == 2
    asyncio.run(sam_pulse.x_search(ctx))
    refused = asyncio.run(sam_pulse.x_search(ctx))
    assert refused["reason"] == "monthly_x_budget_reached" and len(sent) == 2


def test_sam_has_the_tool_the_schedule_and_unknown_actions_are_errors(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    assert hermes_tools.PULSE in hermes_tools.granted("sam")
    assert agent_schedule.JOBS["sam_pulse"].cron == "40 7,14,20 * * *" and sam_pulse.X_HOUR == 7
    assert asyncio.run(sam_pulse.tool({"action": "buy"}, None))["available_actions"] == ["digest", "read", "sources", "x"]
    assert asyncio.run(sam_pulse.tool({"action": "read", "source": "nope"}, None))["error"] == "unknown_source"
    listed = asyncio.run(sam_pulse.tool({"action": "sources"}, None))["sources"]
    assert listed["fred"]["needs"] == ["fred_api_key"] and listed["cot"]["last"] == "not_collected_yet"
    assert len(sam_pulse.config()["x_handles"]) <= 20  # x_search takes at most 20 accounts
