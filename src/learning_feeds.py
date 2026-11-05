"""Weekly learning from RSS/Atom feeds, read by the schedule (replaces the n8n RSS workflow).

Each feed is fetched once, parsed with the standard library and reduced to the items of the
last seven days. The items then pass ``agent_jobs.accept_learning``, which keeps only links on
hosts Andrii connected. A feed that cannot be read is counted and named, never replaced with
anything. Documents with a DOCTYPE are refused, so no entity is ever expanded.
"""
from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
import structlog

logger = structlog.get_logger(__name__)

FEEDS_PATH = Path(__file__).with_name("learning_feeds.json")
MAX_FEED_BYTES = 2_000_000
FETCH_TIMEOUT_S = 20.0
MAX_ITEMS = 50
MAX_TEXT = 4000
WINDOW = timedelta(days=7)
_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


def feeds_for(agent: str, path: Path = FEEDS_PATH) -> List[str]:
    try:
        feeds = json.loads(path.read_text(encoding="utf-8")).get(agent, [])
    except (OSError, ValueError):
        return []
    return [url for url in feeds if isinstance(url, str) and url.startswith("https://")]


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child(node: ET.Element, *names: str) -> Optional[ET.Element]:
    for child in node:
        if _local(child.tag) in names:
            return child
    return None


def _text(node: Optional[ET.Element]) -> str:
    return "".join(node.itertext()).strip() if node is not None else ""


def _plain(raw: str) -> str:
    return _SPACE.sub(" ", html.unescape(_TAG.sub(" ", raw))).strip()


def _when(raw: str) -> Optional[datetime]:
    if not raw:
        return None
    try:
        stamp = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        try:
            stamp = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
    return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)


def _link(entry: ET.Element) -> str:
    node = _child(entry, "link")
    if node is None:
        return ""
    return (node.get("href") or _text(node)).strip()


def _entry(entry: ET.Element) -> Dict[str, Any]:
    body = _child(entry, "description", "summary", "content")
    date = _child(entry, "pubDate", "published", "updated", "date")
    return {"url": _link(entry), "title": _plain(_text(_child(entry, "title")))[:200],
            "text": _plain(_text(body))[:MAX_TEXT], "when": _when(_text(date))}


def parse_feed(raw: bytes) -> List[Dict[str, Any]]:
    """Items of an RSS 2.0 or Atom document; raises ``ValueError`` on anything else."""
    if len(raw) > MAX_FEED_BYTES:
        raise ValueError("feed_too_large")
    if b"<!DOCTYPE" in raw[:4096].upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("doctype_refused")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("not_xml") from exc
    if _local(root.tag) not in ("rss", "feed", "RDF"):
        raise ValueError("not_a_feed")
    return [_entry(node) for node in root.iter() if _local(node.tag) in ("item", "entry")]


def fresh_items(entries: List[Dict[str, Any]], now: datetime) -> List[Dict[str, str]]:
    """Last week's items with a link and text, each link once. An undated item is kept, as n8n did."""
    seen, out = set(), []
    for item in entries:
        url, when = item["url"], item["when"]
        if not url or not item["text"] or url in seen or (when is not None and when < now - WINDOW):
            continue
        seen.add(url)
        out.append({"url": url, "title": item["title"], "text": item["text"]})
    return out[:MAX_ITEMS]


async def _fetch(client: httpx.AsyncClient, url: str) -> bytes:
    response = await client.get(url, follow_redirects=True)
    response.raise_for_status()
    return response.content


async def collect(agent: str, *, now: Optional[datetime] = None, client: Optional[httpx.AsyncClient] = None,
                  feeds_path: Path = FEEDS_PATH) -> Tuple[List[Dict[str, str]], List[str]]:
    """Last week's items from the agent's feeds, plus the feeds that failed."""
    feeds = feeds_for(agent, feeds_path)
    moment = now or datetime.now(timezone.utc)
    entries: List[Dict[str, Any]] = []
    failed: List[str] = []
    owned = client is None
    http = client or httpx.AsyncClient(timeout=FETCH_TIMEOUT_S, headers={"User-Agent": "syndicate-learning/1.0"})
    try:
        for url in feeds:
            try:
                entries.extend(parse_feed(await _fetch(http, url)))
            except (httpx.HTTPError, ValueError) as exc:
                logger.warning("learning_feed_failed", agent=agent, url=url, error=type(exc).__name__)
                failed.append(url)
    finally:
        if owned:
            await http.aclose()
    return fresh_items(entries, moment), failed
