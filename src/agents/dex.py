"""Dex Agent — Chief of Affiliate Marketing, CPA Networks & Conversion Funnels for SYNDICATE Holding."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urlencode
from src.agents.director_base import DirectorAgent, number, text

ALLOWED_NETWORKS = {"clickbank", "cj_affiliate", "shareasale", "digistore24", "impact", "saas_direct", "amazon_associates"}
ALLOWED_CLUSTERS = {"health_fitness", "ai_tech", "finance_ecommerce"}


class DexAgent(DirectorAgent):
    AGENT_ID = "dex"
    ACTIONS = {
        "capabilities": "capabilities",
        "score_offer": "score_offer",
        "build_funnel": "build_funnel",
        "package_links": "package_links",
        "batch_plan": "batch_plan",
        "offers": "offers",
        "funnels": "funnels",
        "report": "report",
        "activate_paid_traffic": "blocked_external",
        "withdraw_payout": "blocked_external",
    }

    async def score_offer(self, payload: dict) -> dict:
        offer_name = text(payload["offer_name"], "offer_name", 200)
        network = text(payload["network"], "network", 40).lower()
        if network not in ALLOWED_NETWORKS:
            raise ValueError("unsupported_affiliate_network")

        payout = Decimal(str(number(payload["payout_usd"], "payout_usd", 0.01, 50000)))
        conversion_rate = Decimal(str(number(payload["conversion_rate_pct"], "conversion_rate_pct", 0.01, 100)))
        refund_rate = Decimal(str(number(payload.get("refund_rate_pct", 5.0), "refund_rate_pct", 0, 95)))

        # Expected Earnings Per Click (EPC) = Payout * (CR / 100) * (1 - Refund / 100)
        net_multiplier = (Decimal("100") - refund_rate) / Decimal("100")
        epc = (payout * (conversion_rate / Decimal("100")) * net_multiplier).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        approved_for_funnels = epc >= Decimal("0.50") and refund_rate <= Decimal("15.0")

        record = self.store.add(
            "offer",
            {
                "offer_name": offer_name,
                "network": network,
                "payout_usd": str(payout.quantize(Decimal("0.01"))),
                "conversion_rate_pct": str(conversion_rate.quantize(Decimal("0.01"))),
                "refund_rate_pct": str(refund_rate.quantize(Decimal("0.01"))),
                "expected_epc_usd": str(epc),
                "approved": approved_for_funnels,
                "state": "approved_draft" if approved_for_funnels else "rejected_low_epc",
            },
        )
        return {"status": "ok", "offer": record}

    async def build_funnel(self, payload: dict) -> dict:
        funnel_name = text(payload["funnel_name"], "funnel_name", 200)
        offer_name = text(payload["offer_name"], "offer_name", 200)
        cluster = text(payload.get("cluster", "finance_ecommerce"), "cluster", 40).lower()
        if cluster not in ALLOWED_CLUSTERS:
            raise ValueError("unsupported_cluster")

        lead_magnet = text(payload["lead_magnet"], "lead_magnet", 300)
        bridge_page = text(payload.get("bridge_page", "Educational case study + comparison table"), "bridge_page", 300)

        record = self.store.add(
            "funnel",
            {
                "funnel_name": funnel_name,
                "offer_name": offer_name,
                "cluster": cluster,
                "steps": [
                    {"step": 1, "stage": "traffic_source", "actor": "oscar_blog_or_shorts"},
                    {"step": 2, "stage": "lead_magnet", "asset": lead_magnet},
                    {"step": 3, "stage": "bridge_prelanding", "asset": bridge_page},
                    {"step": 4, "stage": "affiliate_offer_redirect", "offer": offer_name},
                ],
                "state": "draft_only",
            },
        )
        return {"status": "ok", "funnel": record}

    async def package_links(self, payload: dict) -> dict:
        base_url = text(payload["base_url"], "base_url", 1000)
        if not (base_url.startswith("https://") or base_url.startswith("http://")):
            raise ValueError("invalid_base_url")
        cluster = text(payload["cluster"], "cluster", 40).lower()
        if cluster not in ALLOWED_CLUSTERS:
            raise ValueError("unsupported_cluster")
        campaign = text(payload["campaign"], "campaign", 100)
        sub_id = text(payload.get("sub_id", "oscar_blog"), "sub_id", 100)

        sep = "&" if "?" in base_url else "?"
        tracked_url = f"{base_url}{sep}{urlencode({'utm_source': 'syndicate', 'utm_medium': cluster, 'utm_campaign': campaign, 'sub_id': sub_id})}"
        return {
            "status": "ok",
            "cluster": cluster,
            "target_agent": "oscar",
            "tracked_url": tracked_url,
            "disclosure_required": True,
        }

    async def batch_plan(self, payload: dict) -> dict:
        days = int(number(payload.get("horizon_days", 4), "horizon_days", 3, 7))
        offers = payload["offers"]
        if not isinstance(offers, list) or not offers or len(offers) > 50:
            raise ValueError("invalid_batch_offers")
        results = []
        for item in offers:
            scored = await self.score_offer(item)
            results.append(scored["offer"])
        return {"status": "ok", "horizon_days": days, "scored_count": len(results), "offers": results}

    async def offers(self, payload: dict) -> dict:
        return {"status": "ok", "records": self.store.list("offer")}

    async def funnels(self, payload: dict) -> dict:
        return {"status": "ok", "records": self.store.list("funnel")}

    async def report(self, payload: dict) -> dict:
        offers = self.store.list("offer")
        funnels = self.store.list("funnel")
        approved = [o for o in offers if o.get("approved")]
        return {
            "status": "ok",
            "offers_evaluated": len(offers),
            "offers_approved": len(approved),
            "funnels_drafted": len(funnels),
            "external_actions": False,
        }
