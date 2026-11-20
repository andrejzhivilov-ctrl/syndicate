"""Sam's pulse: what big players, officials and crowds do across every market Sam follows (Andrii, 20.11.2026).

Primary sources first, free first: CFTC positions of large traders, central banks, FRED and EIA, SEC insider
filings, the economic calendar, crypto futures positioning, stablecoin supply, the fear index, Polymarket,
news headlines, injuries and bookmaker line moves in sport, Reddit and public Telegram channels. X is read
through Grok's x_search (Andrii's xAI key), paid per post, so it runs once a day under a monthly cap.

Every source answers ``ok`` with what it fetched or ``unavailable`` with a reason (AGENTS.md §1): a missing
key says which key, a blocked site says its HTTP code. Each answer is kept twice: the latest one for the
morning report and an append-only history, so later an event study can test "this happened → the price
moved" before any of it becomes a signal. Headlines and moods are context, never a trade by themselves.
"""
from __future__ import annotations

import asyncio
import base64
import html
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Mapping, Optional, Tuple
from urllib.parse import quote_plus

import httpx

from src.data_paths import ensure_dir
from src.integrations import macro_data
from src.learning_feeds import parse_feed

CONFIG_PATH = Path(__file__).resolve().parent.parent / "sam_core" / "pulse_sources.json"
MAX_BYTES = 3_000_000
TIMEOUT_S = 20
#: A plain agent string: some public APIs refuse bot-like names, ESPN refuses browser-like ones.
AGENT = "syndicate-research/1.0"
#: xAI x_search: $5 per 1000 posts fetched (docs.x.ai, checked 20.11.2026) plus tokens.
X_PRICE_PER_POST = 0.005
X_TOKEN_PRICE = {"input": 1.25 / 1e6, "output": 2.50 / 1e6}
DEFAULT_X_MONTHLY_USD = 4.0


class NeedKey(Exception):
    """A source that needs a key Andrii has not put in Vault yet."""


@dataclass(frozen=True)
class Source:
    market: str
    fetch: Callable[[httpx.AsyncClient, "Context"], Awaitable[Dict[str, Any]]]
    keys: Tuple[str, ...] = ()
    note: str = ""


@dataclass
class Context:
    config: Dict[str, Any]
    keys: Dict[str, str]
    transport: Any = None  # tests pass a mock; production lets httpx open its own

    def key(self, *names: str) -> str:
        for name in names:
            if self.keys.get(name):
                return self.keys[name]
        raise NeedKey(names[0])


def config() -> Dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _get(client: httpx.AsyncClient, url: str, **kwargs: Any) -> bytes:
    headers = {"User-Agent": AGENT, **kwargs.pop("headers", {})}
    async with client.stream("GET", url, headers=headers, **kwargs) as response:
        response.raise_for_status()
        body = bytearray()
        async for chunk in response.aiter_bytes():
            body.extend(chunk)
            if len(body) > MAX_BYTES:
                raise ValueError("response_too_large")
        return bytes(body)


async def _json(client: httpx.AsyncClient, url: str, **kwargs: Any) -> Any:
    return json.loads(await _get(client, url, **kwargs))


def _pct(new: float, old: float) -> Optional[float]:
    return round((new / old - 1) * 100, 2) if old else None


# ─── Crypto ──────────────────────────────────────────────────────────────────

async def _crypto_positioning(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    """Bybit USDT perpetuals: funding, open interest, the share of accounts long now and a day ago."""
    items, lines = [], []
    for symbol in ctx.config["crypto_symbols"]:
        ticker = (await _json(client, "https://api.bybit.com/v5/market/tickers",
                              params={"category": "linear", "symbol": symbol}))["result"]["list"][0]
        ratio = (await _json(client, "https://api.bybit.com/v5/market/account-ratio",
                             params={"category": "linear", "symbol": symbol, "period": "1h", "limit": 25}))["result"]["list"]
        long_now, long_day = float(ratio[0]["buyRatio"]), float(ratio[-1]["buyRatio"])
        row = {"symbol": symbol, "price": float(ticker["lastPrice"]),
               "change_24h_pct": round(float(ticker["price24hPcnt"]) * 100, 2),
               "funding_pct": round(float(ticker["fundingRate"]) * 100, 4),
               "open_interest_usd": round(float(ticker["openInterestValue"])),
               "accounts_long_pct": round(long_now * 100, 1), "accounts_long_day_ago_pct": round(long_day * 100, 1)}
        items.append(row)
        lines.append(f"{symbol}: {row['change_24h_pct']:+}% за добу, funding {row['funding_pct']}%, "
                     f"OI ${row['open_interest_usd'] / 1e9:.2f} млрд, у лонгах {row['accounts_long_pct']}% акаунтів "
                     f"(добу тому {row['accounts_long_day_ago_pct']}%)")
    return {"summary": lines, "items": items}


async def _fear_greed(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    rows = (await _json(client, "https://api.alternative.me/fng/", params={"limit": 7}))["data"]
    items = [{"value": int(r["value"]), "label": r["value_classification"],
              "date": datetime.fromtimestamp(int(r["timestamp"]), timezone.utc).strftime("%Y-%m-%d")} for r in rows]
    week = ", ".join(str(i["value"]) for i in reversed(items))
    return {"summary": [f"Страх і жадібність (крипта): {items[0]['value']} — {items[0]['label']}; тиждень: {week}"],
            "items": items}


async def _stablecoins(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    """New dollars entering crypto: USD stablecoin supply now, a day and a week ago."""
    assets = (await _json(client, "https://stablecoins.llama.fi/stablecoins", params={"includePrices": "false"}))["peggedAssets"]

    def total(field: str) -> float:
        return sum(float((a.get(field) or {}).get("peggedUSD") or 0) for a in assets if a.get("pegType") == "peggedUSD")

    now, day, week = total("circulating"), total("circulatingPrevDay"), total("circulatingPrevWeek")
    if not now:
        raise ValueError("no_supply")
    item = {"supply_usd": round(now), "day_change_usd": round(now - day), "week_change_usd": round(now - week)}
    return {"summary": [f"Стейблкоїни в USD: ${now / 1e9:.1f} млрд; за добу {(now - day) / 1e6:+,.0f} млн, "
                        f"за тиждень {(now - week) / 1e6:+,.0f} млн"], "items": [item]}


async def _telegram(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    """Public channels through their web preview: no account, nothing about Andrii leaves the server."""
    items, lines = [], []
    for channel in ctx.config["telegram_channels"]:
        page = (await _get(client, f"https://t.me/s/{quote_plus(channel)}")).decode("utf-8", "replace")
        texts = re.findall(r'tgme_widget_message_text[^>]*>(.*?)</div>', page, flags=re.S)
        times = re.findall(r'<time datetime="([^"]+)"', page)
        # A service post may have a time and no text, so the two lists are not assumed equal.
        for raw, when in list(zip(texts, times, strict=False))[-5:]:
            text = html.unescape(re.sub(r"<[^>]+>", " ", raw)).strip()
            text = re.sub(r"\s+", " ", text)[:280]
            if text:
                items.append({"channel": channel, "time": when, "text": text})
        if items:
            lines.append(f"t.me/{channel}: {items[-1]['text'][:160]}")
    if not items:
        raise ValueError("no_messages")
    return {"summary": lines, "items": items}


# ─── Macro, rates, currencies, commodities ──────────────────────────────────

async def _cot(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    """CFTC: net positions of large speculators (non-commercial) and hedgers, each Tuesday, out on Friday."""
    items, lines = [], []
    for code, name in ctx.config["cot_markets"].items():
        row = await macro_data.cot_positioning(code, transport=ctx.transport)
        if row.get("status") != "ok":
            continue
        items.append({"code": code, "name": name, **{k: row[k] for k in ("report_date", "open_interest",
                                                                         "noncommercial_net", "commercial_net")}})
        lines.append(f"{name}: великі спекулянти нетто {row['noncommercial_net']:+,}, хеджери {row['commercial_net']:+,} "
                     f"(звіт {row['report_date']})")
    if not items:
        raise ValueError("no_reports")
    return {"summary": lines, "items": items}


async def _fred(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    key = ctx.key("fred_api_key")
    items, lines = [], []
    for series, name in ctx.config["fred_series"].items():
        row = await macro_data.fred_latest(series, key, transport=ctx.transport)
        if row.get("status") == "ok" and row["value"] is not None:
            items.append({"series": series, "name": name, "date": row["date"], "value": row["value"]})
            lines.append(f"{name}: {row['value']} ({row['date']})")
    if not items:
        raise ValueError("no_observations")
    return {"summary": lines, "items": items}


async def _eia(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    row = await macro_data.eia_latest("petroleum/stoc/wstk", "WCESTUS1", ctx.key("eia_api_key"),
                                      transport=ctx.transport)
    if row.get("status") != "ok":
        raise ValueError(row.get("reason", "no_observation"))
    return {"summary": [f"Комерційні запаси нафти США: {row['value']} {row.get('units') or ''} (тиждень {row['period']})"],
            "items": [row]}


async def _feeds(client: httpx.AsyncClient, feeds: Mapping[str, str], per_feed: int) -> Dict[str, Any]:
    items, lines, failed = [], [], []
    for name, url in feeds.items():
        try:
            entries = parse_feed(await _get(client, url, follow_redirects=True))[:per_feed]
        except (httpx.HTTPError, ValueError):
            failed.append(name)
            continue
        for entry in entries:
            when = entry["when"].isoformat() if entry["when"] else None
            items.append({"feed": name, "title": entry["title"], "url": entry["url"], "published": when})
        if entries:
            lines.append(f"{name}: {entries[0]['title'][:160]}")
    if not items:
        raise ValueError("feeds_unreachable")
    return {"summary": lines, "items": items, **({"failed": failed} if failed else {})}


async def _central_banks(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    return await _feeds(client, ctx.config["central_banks"], 5)


async def _news(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    feeds = {market: f"https://news.google.com/rss/search?q={quote_plus(query + ' when:1d')}&hl=en-US&gl=US&ceid=US:en"
             for market, query in ctx.config["news_queries"].items()}
    return await _feeds(client, feeds, 6)


async def _calendar(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    """This week's high-impact releases: windows when Sam does not open new trades on that currency."""
    rows = await _json(client, "https://nfs.faireconomy.media/ff_calendar_thisweek.json")
    now, wanted = _now(), set(ctx.config["calendar_currencies"])
    items = []
    for row in rows:
        when = datetime.fromisoformat(row["date"]).astimezone(timezone.utc)
        if row.get("impact") == "High" and row.get("country") in wanted and when >= now - timedelta(hours=2):
            items.append({"time_utc": when.strftime("%Y-%m-%d %H:%M"), "currency": row["country"], "event": row["title"],
                          "forecast": row.get("forecast") or None, "previous": row.get("previous") or None})
    lines = [f"{i['time_utc']} UTC {i['currency']}: {i['event']} (прогноз {i['forecast']}, було {i['previous']})"
             for i in items[:12]]
    return {"summary": lines or ["Важливих релізів до кінця тижня немає"], "items": items}


# ─── Stocks ─────────────────────────────────────────────────────────────────

async def _insiders(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    """SEC EDGAR: the newest insider trades (Form 4) and fund holdings (13F); the SEC wants a named contact."""
    agent = ctx.key("sec_user_agent")
    feeds = {form: f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type={form}&output=atom&count=40"
             for form in ("4", "13F-HR")}
    items, lines = [], []
    for form, url in feeds.items():
        entries = parse_feed(await _get(client, url, headers={"User-Agent": agent}))
        for entry in entries[:20]:
            items.append({"form": form, "title": entry["title"], "url": entry["url"],
                          "filed": entry["when"].isoformat() if entry["when"] else None})
        lines.append(f"SEC {form}: {len(entries)} нових; останнє — {entries[0]['title'][:120]}" if entries else
                     f"SEC {form}: нових немає")
    return {"summary": lines, "items": items}


async def _polymarket(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    """Money-weighted odds on rates, inflation, elections, crypto and sport: the busiest open markets."""
    rows = await _json(client, "https://gamma-api.polymarket.com/markets",
                       params={"active": "true", "closed": "false", "order": "volume24hr", "ascending": "false", "limit": 200})
    words = [w.lower() for w in ctx.config["polymarket_keywords"]]
    items = []
    for row in rows:
        question = str(row.get("question") or "")
        if not any(w in question.lower() for w in words):
            continue
        outcomes, prices = json.loads(row.get("outcomes") or "[]"), json.loads(row.get("outcomePrices") or "[]")
        odds = {o: round(float(p) * 100, 1) for o, p in zip(outcomes, prices, strict=False)}
        items.append({"question": question, "odds_pct": odds, "volume_24h_usd": round(float(row.get("volume24hr") or 0)),
                      "ends": str(row.get("endDate") or "")[:10]})
    lines = [f"{i['question']} — {', '.join(f'{k} {v}%' for k, v in i['odds_pct'].items())} "
             f"(обсяг за добу ${i['volume_24h_usd']:,})" for i in items[:10]]
    if not items:
        raise ValueError("no_matching_markets")
    return {"summary": lines, "items": items[:40]}


# ─── Sport ──────────────────────────────────────────────────────────────────

async def _injuries(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    data = await _json(client, "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries")
    items = []
    for team in data.get("injuries", []):
        for row in team.get("injuries", []):
            athlete = (row.get("athlete") or {}).get("displayName")
            items.append({"league": "NBA", "team": team.get("displayName"), "player": athlete,
                          "status": row.get("status"), "comment": str(row.get("shortComment") or "")[:200]})
    out = [i for i in items if i["status"] == "Out"]
    return {"summary": [f"NBA: травмованих {len(items)}, точно не грають {len(out)}"], "items": items}


def _fair_odds(event: Mapping[str, Any]) -> Dict[str, float]:
    """The average decimal price of each outcome over all bookmakers in the answer."""
    prices: Dict[str, List[float]] = {}
    for book in event.get("bookmakers", []):
        for market in book.get("markets", []):
            for outcome in market.get("outcomes", []):
                prices.setdefault(outcome["name"], []).append(float(outcome["price"]))
    return {name: round(sum(p) / len(p), 3) for name, p in prices.items() if p}


async def _odds(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    """Bookmaker prices now and their move since the last snapshot: big money shortens a price."""
    key = ctx.key("odds_api_key")
    before = {i["event_id"]: i for i in (latest("sports_odds") or {}).get("data", {}).get("items", [])}
    items, lines = [], []
    for sport in ctx.config["odds_sports"]:
        events = await _json(client, f"https://api.the-odds-api.com/v4/sports/{sport}/odds",
                             params={"apiKey": key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"})
        for event in events[:30]:
            odds = _fair_odds(event)
            old = before.get(event["id"], {}).get("odds", {})
            moves = {k: _pct(v, old[k]) for k, v in odds.items() if k in old}
            items.append({"event_id": event["id"], "sport": sport, "event": f"{event['home_team']} — {event['away_team']}",
                          "starts": event["commence_time"], "odds": odds, "move_pct": moves})
    for item in items:
        big = {k: v for k, v in item["move_pct"].items() if v is not None and abs(v) >= 5}
        if big:
            lines.append(f"{item['event']}: рух коефіцієнтів {big} з минулого знімка")
    return {"summary": lines or [f"Подій у знімку: {len(items)}; різких рухів ліній (≥5%) немає"], "items": items}


# ─── Crowds ─────────────────────────────────────────────────────────────────

async def _reddit(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    """Reddit's app-only OAuth (Andrii's approved non-commercial app); the hottest threads of each forum."""
    pair = f"{ctx.key('reddit_client_id')}:{ctx.key('reddit_client_secret')}".encode()
    token_response = await client.post("https://www.reddit.com/api/v1/access_token", data={"grant_type": "client_credentials"},
                                       headers={"Authorization": "Basic " + base64.b64encode(pair).decode(),
                                                "User-Agent": AGENT})
    token_response.raise_for_status()
    auth = {"Authorization": f"Bearer {token_response.json()['access_token']}"}
    items, lines = [], []
    for sub in ctx.config["subreddits"]:
        data = await _json(client, f"https://oauth.reddit.com/r/{quote_plus(sub)}/hot", params={"limit": 8}, headers=auth)
        posts = [c["data"] for c in data["data"]["children"] if not c["data"].get("stickied")][:5]
        for post in posts:
            items.append({"subreddit": sub, "title": post["title"][:200], "score": post["score"],
                          "comments": post["num_comments"], "url": "https://www.reddit.com" + post["permalink"]})
        if posts:
            lines.append(f"r/{sub}: {posts[0]['title'][:140]} ({posts[0]['score']} голосів)")
    return {"summary": lines, "items": items}


async def _cryptopanic(client: httpx.AsyncClient, ctx: Context) -> Dict[str, Any]:
    data = await _json(client, "https://cryptopanic.com/api/developer/v2/posts/",
                       params={"auth_token": ctx.key("cryptopanic_api_key"), "public": "true"})
    items = [{"title": r.get("title"), "published": r.get("published_at"),
              "coins": [c.get("code") for c in r.get("instruments") or r.get("currencies") or []]}
             for r in data.get("results", [])[:30]]
    if not items:
        raise ValueError("no_posts")
    return {"summary": [f"{i['title'][:150]} {i['coins']}" for i in items[:6]], "items": items}


SOURCES: Dict[str, Source] = {
    "crypto_positioning": Source("crypto", _crypto_positioning, note="Bybit: funding, OI, частка лонгів"),
    "fear_greed": Source("crypto", _fear_greed, note="alternative.me"),
    "stablecoins": Source("crypto", _stablecoins, note="DefiLlama: нові долари в крипті"),
    "telegram": Source("crypto", _telegram, note="публічні канали t.me/s"),
    "cryptopanic": Source("crypto", _cryptopanic, ("cryptopanic_api_key",), "крипто-новини"),
    "cot": Source("macro", _cot, note="CFTC: позиції великих гравців"),
    "fred": Source("macro", _fred, ("fred_api_key",), "ставки, долар, VIX, інфляція"),
    "eia": Source("commodities", _eia, ("eia_api_key",), "запаси нафти США"),
    "central_banks": Source("macro", _central_banks, note="ФРС, ЄЦБ, Банк Англії, Банк Японії"),
    "calendar": Source("macro", _calendar, note="важливі релізи тижня"),
    "news": Source("all", _news, note="Google News за ринками"),
    "insiders": Source("stocks", _insiders, ("sec_user_agent",), "SEC: інсайдери і фонди"),
    "polymarket": Source("all", _polymarket, note="ринки прогнозів"),
    "sports_injuries": Source("sports", _injuries, note="ESPN: травми NBA"),
    "sports_odds": Source("sports", _odds, ("odds_api_key",), "рух ліній букмекерів"),
    "reddit": Source("all", _reddit, ("reddit_client_id", "reddit_client_secret"), "гарячі теми форумів"),
}
#: Every collection run takes these; X (paid) runs on its own once a day.
SCHEDULED = tuple(SOURCES)


# ─── Storage ────────────────────────────────────────────────────────────────

def _store() -> Path:
    return ensure_dir("sam_pulse")


def latest(name: str) -> Optional[Dict[str, Any]]:
    path = _store() / "latest" / f"{name}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _keep(name: str, result: Dict[str, Any]) -> None:
    folder = _store() / "latest"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.json").write_text(json.dumps(result, ensure_ascii=False, default=str), encoding="utf-8")
    if result.get("status") == "ok":  # the history feeds the event study; failures are in latest only
        history = _store() / "history"
        history.mkdir(parents=True, exist_ok=True)
        with (history / f"{name}.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, default=str) + "\n")


async def collect(name: str, ctx: Context) -> Dict[str, Any]:
    """One source, fetched now and kept; an exception becomes an honest ``unavailable``."""
    source = SOURCES[name]
    base = {"source": name, "market": source.market, "retrieved_at": _now().isoformat()}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_S, transport=ctx.transport, follow_redirects=False) as client:
            data = await source.fetch(client, ctx)
        result = {"status": "ok", **base, "data": data}
    except NeedKey as missing:
        result = {"status": "unavailable", **base, "reason": "key_not_configured", "key": str(missing)}
    except httpx.HTTPStatusError as exc:
        result = {"status": "unavailable", **base, "reason": f"http_{exc.response.status_code}"}
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
        result = {"status": "unavailable", **base, "reason": type(exc).__name__, "detail": str(exc)[:120]}
    _keep(name, result)
    return result


KEY_NAMES = ("fred_api_key", "eia_api_key", "sec_user_agent", "odds_api_key", "reddit_client_id",
             "reddit_client_secret", "cryptopanic_api_key", "xai_api_key", "grok_api_key")


async def keys_from(vault: Any) -> Dict[str, str]:
    """Only the keys this module uses, from Vault's api-keys; none of them is ever logged or returned."""
    from src.vault_paths import secret_path

    if vault is None:
        return {}
    try:
        pool = await vault.get_secret(secret_path("api-keys")) or {}
    except Exception:  # noqa: BLE001 - no Vault means every keyed source says which key is missing
        pool = {}
    return {k: str(pool[k]) for k in KEY_NAMES if isinstance(pool.get(k), str) and pool.get(k)}


# ─── X through Grok ─────────────────────────────────────────────────────────

def x_budget() -> float:
    try:
        return float(os.getenv("SAM_X_MONTHLY_USD", DEFAULT_X_MONTHLY_USD))
    except ValueError:
        return DEFAULT_X_MONTHLY_USD


def x_spent(month: Optional[str] = None) -> float:
    month = month or _now().strftime("%Y-%m")
    path = _store() / "x_spend.json"
    try:
        return float(json.loads(path.read_text(encoding="utf-8")).get(month, 0.0))
    except (OSError, ValueError):
        return 0.0


def _x_charge(cost: float) -> None:
    path = _store() / "x_spend.json"
    try:
        book = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        book = {}
    month = _now().strftime("%Y-%m")
    book[month] = round(float(book.get(month, 0.0)) + cost, 4)
    path.write_text(json.dumps(book), encoding="utf-8")


def _x_cost(usage: Mapping[str, Any]) -> float:
    tools = usage.get("server_side_tool_usage_details") or {}
    posts = int(tools.get("x_posts_fetched") or 0) + 2 * int(tools.get("x_users_fetched") or 0)
    tokens = (int(usage.get("input_tokens") or 0) * X_TOKEN_PRICE["input"]
              + int(usage.get("output_tokens") or 0) * X_TOKEN_PRICE["output"])
    return round(posts * X_PRICE_PER_POST + tokens, 4)


def _x_text(body: Mapping[str, Any]) -> Tuple[str, List[str]]:
    texts, urls = [], []
    for item in body.get("output") or []:
        for part in item.get("content") or [] if isinstance(item, dict) else []:
            if part.get("type") == "output_text":
                texts.append(part.get("text") or "")
                urls += [a.get("url") for a in part.get("annotations") or [] if a.get("url")]
    urls += [c for c in body.get("citations") or [] if isinstance(c, str)]
    return "\n".join(texts).strip(), list(dict.fromkeys(urls))


X_PROMPT = ("Ти — дослідник для трейдера. Знайди на X пости за останню добу від цих акаунтів про ринки: "
            "валюти, ставки, метали, нафту, акції, крипту, великі угоди й перекази, спорт і ставки. {question} "
            "Дай до 12 пунктів українською: хто, що сказав або зробив, коли, на який ринок впливає. "
            "Лише те, що є в постах, з посиланням на кожен; нічого не домислюй. Якщо нічого суттєвого — так і скажи.")


async def x_search(ctx: Context, question: str = "", handles: Optional[List[str]] = None) -> Dict[str, Any]:
    """One paid x_search turn over Andrii's chosen accounts, refused before it would pass the monthly cap."""
    from src.model_registry import model_for

    base = {"source": "x", "market": "all", "retrieved_at": _now().isoformat()}
    try:
        key = ctx.key("xai_api_key", "grok_api_key")
    except NeedKey:
        return {"status": "unavailable", **base, "reason": "key_not_configured", "key": "xai_api_key"}
    spent, cap = x_spent(), x_budget()
    if spent >= cap - 0.25:  # one run costs at most ~$0.25 with max_turns 2
        return {"status": "unavailable", **base, "reason": "monthly_x_budget_reached", "spent_usd": spent, "cap_usd": cap}
    chosen = [h.lstrip("@") for h in (handles or ctx.config["x_handles"]) if re.fullmatch(r"@?\w{1,15}", h)][:20]
    day = _now().date()
    body = {"model": model_for("XAI_X_SEARCH"), "max_turns": 2,
            "input": X_PROMPT.format(question=question[:300]),
            "tools": [{"type": "x_search", "allowed_x_handles": chosen,
                       "from_date": (day - timedelta(days=1)).isoformat(), "to_date": (day + timedelta(days=1)).isoformat()}]}
    try:
        async with httpx.AsyncClient(timeout=180, transport=ctx.transport) as client:
            response = await client.post("https://api.x.ai/v1/responses", json=body,
                                         headers={"Authorization": f"Bearer {key}"})
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as exc:
        return {"status": "unavailable", **base, "reason": f"http_{exc.response.status_code}"}
    except (httpx.HTTPError, ValueError) as exc:
        return {"status": "unavailable", **base, "reason": type(exc).__name__}
    cost = _x_cost(data.get("usage") or {})
    _x_charge(cost)
    text, urls = _x_text(data)
    usage = (data.get("usage") or {}).get("server_side_tool_usage_details") or {}
    result = {"status": "ok" if text else "unavailable", **base, "cost_usd": cost, "spent_month_usd": x_spent(),
              "cap_usd": cap, "posts_fetched": usage.get("x_posts_fetched"), "handles": chosen,
              "data": {"summary": [line for line in text.splitlines() if line.strip()][:14], "items": [{"url": u} for u in urls]}}
    if not text:
        result["reason"] = "empty_answer"
    _keep("x", result)
    return result


# ─── Digest, the job and Sam's tool ─────────────────────────────────────────

MARKET_TITLES = {"macro": "Макро, ставки, валюти", "commodities": "Сировина", "crypto": "Крипта",
                 "stocks": "Акції", "sports": "Спорт", "all": "Усі ринки"}


def digest(market: str = "") -> Dict[str, Any]:
    """What the latest snapshots say, grouped by market, with every missing source named."""
    sections: Dict[str, List[str]] = {}
    missing: Dict[str, str] = {}
    for name in (*SOURCES, "x"):
        row = latest(name)
        source_market = SOURCES[name].market if name in SOURCES else "all"
        if market and source_market not in (market, "all"):
            continue
        if not row or row.get("status") != "ok":
            missing[name] = (row or {}).get("key") or (row or {}).get("reason") or "not_collected_yet"
            continue
        stamp = str(row.get("retrieved_at", ""))[:16].replace("T", " ")
        sections.setdefault(source_market, []).append(f"**{name}** ({stamp} UTC)")
        sections[source_market] += [f"- {line}" for line in row["data"].get("summary", [])[:10]]
    return {"status": "ok" if sections else "unavailable", "sections": sections, "missing": missing,
            "note": "Контекст, не сигнал: кожна залежність «подія → ціна» спершу перевіряється на історії."}


def render(result: Mapping[str, Any]) -> str:
    lines = [f"# Пульс ринків {_now().strftime('%Y-%m-%d %H:%M')} UTC", "", f"_{result.get('note', '')}_", ""]
    for market, rows in result.get("sections", {}).items():
        lines += [f"## {MARKET_TITLES.get(market, market)}", *rows, ""]
    if result.get("missing"):
        lines += ["## Недоступно", *[f"- {k}: {v}" for k, v in result["missing"].items()]]
    return "\n".join(lines) + "\n"


def write_note(text: str) -> Optional[Path]:
    from src.obsidian_notes import vault_dir_from_env

    root = vault_dir_from_env()
    if root is None:
        return None
    folder = root / "Сем" / "Пульс"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{_now().strftime('%Y-%m-%d_%H%M')}.md"
    path.write_text(text, encoding="utf-8")
    return path


#: Kyiv hour of the run that also reads X (once a day, before the morning report).
X_HOUR = 7


async def run_job(vault: Any, with_x: bool, transport: Any = None) -> Dict[str, Any]:
    ctx = Context(config(), await keys_from(vault), transport)
    results = await asyncio.gather(*(collect(name, ctx) for name in SCHEDULED))
    states = {r["source"]: r["status"] if r["status"] == "ok" else r.get("key") or r.get("reason") for r in results}
    if with_x:
        states["x"] = (await x_search(ctx)).get("status")
    note = await asyncio.to_thread(write_note, render(digest()))
    ok = sum(1 for s in states.values() if s == "ok")
    return {"status": "ok" if ok else "unavailable", "sources_ok": ok, "sources": states,
            "note": str(note) if note else None}


ACTIONS = ("digest", "read", "sources", "x")


async def tool(args: Mapping[str, Any], vault: Any, transport: Any = None) -> Dict[str, Any]:
    action = str(args.get("action") or "")
    ctx = Context(config(), await keys_from(vault), transport) if action in ("read", "x") else None
    if action == "sources":
        return {"status": "ok", "sources": {n: {"market": s.market, "needs": list(s.keys), "about": s.note,
                                                "last": (latest(n) or {}).get("status", "not_collected_yet")}
                                            for n, s in SOURCES.items()},
                "x": {"spent_usd": x_spent(), "cap_usd": x_budget()}}
    if action == "digest":
        return digest(str(args.get("market") or ""))
    if action == "read":
        name = str(args.get("source") or "")
        if name not in SOURCES:
            return {"status": "error", "error": "unknown_source", "available_sources": sorted(SOURCES)}
        return await collect(name, ctx)
    if action == "x":
        handles = [str(h) for h in args.get("handles") or []] or None
        return await x_search(ctx, str(args.get("question") or ""), handles)
    return {"status": "error", "error": "unknown_action", "available_actions": sorted(ACTIONS)}
