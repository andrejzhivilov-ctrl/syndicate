"""Ray Agent — Chief of Physical Dropshipping, Supplier Audit & E-Commerce Operations for SYNDICATE Holding."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from src.agents.director_base import DirectorAgent, number, text

ALLOWED_SUPPLIER_PLATFORMS = {"aliexpress", "cj_dropshipping", "spocket", "zendrop", "1688_direct", "eu_warehouse", "us_warehouse"}


class RayAgent(DirectorAgent):
    AGENT_ID = "ray"
    ACTIONS = {
        "capabilities": "capabilities",
        "calculate_dropship_margin": "calculate_dropship_margin",
        "audit_supplier": "audit_supplier",
        "product_research": "product_research",
        "batch_plan": "batch_plan",
        "products": "products",
        "suppliers": "suppliers",
        "report": "report",
        "place_supplier_order": "blocked_external",
        "publish_store_listing": "blocked_external",
    }

    async def calculate_dropship_margin(self, payload: dict) -> dict:
        selling_price = Decimal(str(number(payload["selling_price_usd"], "selling_price_usd", 1.0, 50000)))
        supplier_cost = Decimal(str(number(payload["supplier_cost_usd"], "supplier_cost_usd", 0.1, 40000)))
        shipping_cost = Decimal(str(number(payload["shipping_cost_usd"], "shipping_cost_usd", 0.0, 5000)))
        customs_duty = Decimal(str(number(payload.get("customs_duty_usd", 0.0), "customs_duty_usd", 0.0, 5000)))
        refund_reserve_pct = Decimal(str(number(payload.get("refund_reserve_pct", 5.0), "refund_reserve_pct", 0.0, 50.0)))

        # Payment processor fee (2.9% + $0.30)
        processor_fee = (selling_price * Decimal("0.029") + Decimal("0.30")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        refund_reserve = (selling_price * (refund_reserve_pct / Decimal("100"))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total_landed_cost = supplier_cost + shipping_cost + customs_duty + processor_fee + refund_reserve
        net_profit = (selling_price - total_landed_cost).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        margin_pct = ((net_profit / selling_price) * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        viable = margin_pct >= Decimal("30.0") and net_profit >= Decimal("10.0")
        return {
            "status": "ok",
            "selling_price_usd": str(selling_price.quantize(Decimal("0.01"))),
            "total_landed_cost_usd": str(total_landed_cost.quantize(Decimal("0.01"))),
            "processor_fee_usd": str(processor_fee),
            "refund_reserve_usd": str(refund_reserve),
            "net_profit_usd": str(net_profit),
            "net_margin_pct": float(margin_pct),
            "viable_for_catalog": viable,
        }

    async def audit_supplier(self, payload: dict) -> dict:
        supplier_name = text(payload["supplier_name"], "supplier_name", 200)
        platform = text(payload["platform"], "platform", 40).lower()
        if platform not in ALLOWED_SUPPLIER_PLATFORMS:
            raise ValueError("unsupported_supplier_platform")

        rating_pct = number(payload["positive_rating_pct"], "positive_rating_pct", 0, 100)
        dispatch_days = number(payload["avg_dispatch_days"], "avg_dispatch_days", 0.5, 60)
        delivery_days = number(payload["avg_delivery_days"], "avg_delivery_days", 1, 90)
        has_tracking = bool(payload.get("verified_tracking", True))

        approved = rating_pct >= 94.0 and dispatch_days <= 3.0 and delivery_days <= 14.0 and has_tracking
        record = self.store.add(
            "supplier",
            {
                "supplier_name": supplier_name,
                "platform": platform,
                "positive_rating_pct": rating_pct,
                "avg_dispatch_days": dispatch_days,
                "avg_delivery_days": delivery_days,
                "verified_tracking": has_tracking,
                "approved": approved,
                "verdict": "approved_supplier" if approved else "rejected_sla_risk",
            },
        )
        return {"status": "ok", "supplier": record}

    async def product_research(self, payload: dict) -> dict:
        title = text(payload["title"], "title", 200)
        category = text(payload["category"], "category", 100)
        margin_calc = await self.calculate_dropship_margin(payload)

        record = self.store.add(
            "product",
            {
                "title": title,
                "category": category,
                "selling_price_usd": margin_calc["selling_price_usd"],
                "net_profit_usd": margin_calc["net_profit_usd"],
                "net_margin_pct": margin_calc["net_margin_pct"],
                "viable_for_catalog": margin_calc["viable_for_catalog"],
                "state": "draft_listing" if margin_calc["viable_for_catalog"] else "rejected_margin",
            },
        )
        return {"status": "ok", "product": record}

    async def batch_plan(self, payload: dict) -> dict:
        days = int(number(payload.get("horizon_days", 4), "horizon_days", 3, 7))
        products = payload["products"]
        if not isinstance(products, list) or not products or len(products) > 50:
            raise ValueError("invalid_batch_products")
        saved = []
        for item in products:
            res = await self.product_research(item)
            saved.append(res["product"])
        return {"status": "ok", "horizon_days": days, "planned_count": len(saved), "products": saved}

    async def products(self, payload: dict) -> dict:
        return {"status": "ok", "records": self.store.list("product")}

    async def suppliers(self, payload: dict) -> dict:
        return {"status": "ok", "records": self.store.list("supplier")}

    async def report(self, payload: dict) -> dict:
        products = self.store.list("product")
        suppliers = self.store.list("supplier")
        viable = [p for p in products if p.get("viable_for_catalog")]
        return {
            "status": "ok",
            "products_researched": len(products),
            "viable_products": len(viable),
            "suppliers_audited": len(suppliers),
            "external_actions": False,
        }
