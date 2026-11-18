"""Calories and macros of real products from Open Food Facts (16.11.2026).

Andrii: the agent counts KBJU from a product base connected to the internet, not by eye. Open Food
Facts is open (ODbL), needs no key and has Ukrainian products with labels. One call: a name or a
barcode; the answer is per 100 g with the product's page as the source. A product without the four
numbers is listed as such, never filled in (AGENTS.md §1).
"""
from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, List, Optional

import httpx

SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"
PRODUCT_URL = "https://world.openfoodfacts.org/api/v2/product/{code}.json"
PAGE_URL = "https://world.openfoodfacts.org/product/{code}"
HEADERS = {"User-Agent": "SYNDICATE-health/1.0 (personal nutrition agent)"}
FIELDS = "code,product_name,product_name_uk,brands,quantity,nutriments"
TIMEOUT_S = 20
MAX_RESULTS = 5
BARCODE = re.compile(r"^\d{8,14}$")
SOURCE = "Open Food Facts (ODbL), дані з етикеток, внесені людьми; перевіряй з упаковкою."


def _number(nutriments: Dict[str, Any], key: str) -> Optional[float]:
    value = nutriments.get(f"{key}_100g")
    return round(float(value), 1) if isinstance(value, (int, float)) else None


def per_100g(product: Dict[str, Any]) -> Dict[str, Any]:
    nutriments = product.get("nutriments") or {}
    values = {"kcal": _number(nutriments, "energy-kcal"), "protein": _number(nutriments, "proteins"),
              "fat": _number(nutriments, "fat"), "carbs": _number(nutriments, "carbohydrates")}
    code = str(product.get("code") or "")
    return {"name": product.get("product_name_uk") or product.get("product_name") or "(без назви)",
            "brand": product.get("brands") or "", "quantity": product.get("quantity") or "", "code": code,
            "per_100g": values, "complete": all(v is not None for v in values.values()),
            "url": PAGE_URL.format(code=code) if code else ""}


#: Live 18.11.2026: the same search from the server answered 200 and 503 a second apart. Open Food
#: Facts sheds load with 503 and 429; a short wait and another try usually gets the answer.
RETRY_STATUSES = frozenset({429, 502, 503, 504})
ATTEMPTS = 3
RETRY_PAUSE_S = 1.5


async def _get(client: httpx.AsyncClient, url: str, params: Dict[str, Any]) -> httpx.Response:
    for attempt in range(1, ATTEMPTS + 1):
        response = await client.get(url, params=params)
        if response.status_code not in RETRY_STATUSES or attempt == ATTEMPTS:
            return response
        await asyncio.sleep(RETRY_PAUSE_S * attempt)
    return response  # unreachable; keeps type checkers calm


async def lookup(query: str, transport: Any = None) -> Dict[str, Any]:
    """Products matching a name, or the one product of a barcode; honest when nothing is found."""
    query = query.strip()
    if not query or len(query) > 200:
        return {"status": "error", "error": "empty_or_too_long"}
    barcode = bool(BARCODE.match(query))
    url = PRODUCT_URL.format(code=query) if barcode else SEARCH_URL
    params = {"fields": FIELDS} if barcode else {"search_terms": query, "search_simple": 1, "json": 1,
                                                 "page_size": MAX_RESULTS, "fields": FIELDS}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_S, headers=HEADERS, transport=transport) as client:
            response = await _get(client, url, params)
        if response.status_code != 200:
            return {"status": "unavailable", "reason": f"open_food_facts_http_{response.status_code}"}
        data = response.json()
        found: List[Dict[str, Any]] = ([data["product"]] if data.get("product") else []) if barcode \
            else (data.get("products") or [])
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        return {"status": "unavailable", "reason": f"open_food_facts_{type(exc).__name__}"}
    products = [per_100g(product) for product in found[:MAX_RESULTS]]
    if not products:
        return {"status": "unavailable", "reason": "not_found", "query": query}
    return {"status": "ok", "query": query, "products": products, "source": SOURCE}
