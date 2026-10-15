"""POD economics, concierge drafts, supplier routing and Pinterest preparation."""
from __future__ import annotations

import asyncio
from decimal import Decimal
from urllib.parse import urlsplit

from src.agents.director_base import DirectorAgent, number, text
from .finance import PREMIUM_BLANKS, calculate_margin, money
from .studio import render_personalization

SUPPLIERS = {"printify", "printful", "gelato", "prodigi"}


def public_https(value) -> str:
    value = text(value, "https_url", 2000)
    parts = urlsplit(value)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        raise ValueError("invalid_https_url")
    return value


def quality_check(payload: dict) -> dict:
    checks = {"premium_blank": payload["blank_id"] in PREMIUM_BLANKS,
              "commercial_art_license": payload["art_license_confirmed"] is True,
              "commercial_font_license": payload["font_license_confirmed"] is True,
              "print_resolution": number(payload["dpi"], "dpi", 1, 2400) >= 300,
              "trademark_review": payload["trademark_reviewed"] is True}
    return {"status": "ok" if all(checks.values()) else "blocked", "checks": checks,
            "eligible": all(checks.values()), "evidence": "operator_supplied_not_registry_verified"}


class TylerAgent(DirectorAgent):
    AGENT_ID = "tyler"
    ACTIONS = {"capabilities": "capabilities", "quote": "quote", "quality_check": "quality",
               "concierge": "concierge", "orders": "orders", "route_order": "route_order",
               "pinterest_draft": "pinterest_draft", "review_analysis": "review_analysis",
               "report": "report", "fulfill": "blocked_external", "publish": "blocked_external",
               "charge": "blocked_external", "trademark_search": "unavailable_trademarks"}

    async def quote(self, payload: dict) -> dict:
        return calculate_margin(payload)

    async def quality(self, payload: dict) -> dict:
        return quality_check(payload)

    async def concierge(self, payload: dict) -> dict:
        caption = text(payload["caption"], "caption", 120)
        if "\n" in caption or any(ord(char) < 32 for char in caption):
            raise ValueError("single_line_caption_required")
        quote = calculate_margin(payload["quote"])
        quality = quality_check(payload["quality"])
        if not quote["eligible"] or not quality["eligible"]:
            return {"status": "blocked", "quote": quote, "quality": quality, "payment_created": False}
        assets = await asyncio.to_thread(render_personalization, caption)
        record = self.store.add("order", {"caption": caption, "quote": quote, "quality": quality,
                                         "assets": assets, "state": "preview_pending_approval"})
        return {"status": "approval_required", "requires_hitl": True, "record": record,
                "payment_created": False, "manufacturing_submitted": False}

    async def orders(self, payload: dict) -> dict:
        return {"status": "ok", "orders": self.store.list("order")}

    async def route_order(self, payload: dict) -> dict:
        destination = text(payload["country"], "country", 2).upper()
        offers = payload["offers"]
        if not isinstance(offers, list) or not offers or len(offers) > 200:
            raise ValueError("invalid_offers")
        eligible = []
        for offer in offers:
            if offer["supplier"] not in SUPPLIERS:
                raise ValueError("unknown_supplier")
            if offer["currency"] != "USD":
                raise ValueError("currency_mismatch")
            cost = money(offer["production"], "production") + money(offer["shipping"], "shipping")
            days = number(offer["delivery_days"], "delivery_days", 1, 180)
            if destination in offer["ships_to"] and offer["premium_verified"] is True:
                eligible.append((cost, days, offer))
        if not eligible:
            return {"status": "unavailable", "value": None, "warning": "no_eligible_supplier_offer"}
        selected = min(eligible, key=lambda item: (item[0], item[1]))
        return {"status": "ok", "selected": selected[2], "landed_cost": str(selected[0]),
                "source_mode": "supplied_quotes", "submitted": False, "requires_hitl": True}

    async def pinterest_draft(self, payload: dict) -> dict:
        pin = {"title": text(payload["title"], "title", 100),
               "description": text(payload["description"], "description", 800),
               "link": public_https(payload["product_url"]),
               "media_source": {"source_type": "image_url", "url": public_https(payload["image_url"])},
               "board_id": text(payload["board_id"], "board_id", 100)}
        return {"status": "approval_required", "requires_hitl": True, "pin": pin,
                "published": False, "rich_pin_verified": False,
                "warning": "Rich Pins require website metadata and Pinterest validation"}

    async def review_analysis(self, payload: dict) -> dict:
        reviews = payload["reviews"]
        if not isinstance(reviews, list) or len(reviews) > 1000:
            raise ValueError("invalid_reviews")
        selected = [{"rating": number(r["rating"], "rating", 1, 5),
                     "text": text(r["text"], "review")} for r in reviews]
        return {"status": "ok", "low_rated_reviews": [r for r in selected if r["rating"] <= 3],
                "analysis_type": "rating_filter", "source_mode": "supplied_reviews"}

    async def unavailable_trademarks(self, payload: dict) -> dict:
        return {"status": "unavailable", "value": None,
                "warning": "live_trademark_registry_adapter_not_configured"}

    async def report(self, payload: dict) -> dict:
        orders = self.store.list("order")
        quoted = sum((Decimal(o["quote"]["price"]) for o in orders), Decimal(0))
        return {"status": "ok", "preview_orders": len(orders), "quoted_value_usd": str(quoted),
                "recognized_revenue": {"status": "unavailable", "value": None},
                "fulfilled_orders": {"status": "unavailable", "value": None}}
