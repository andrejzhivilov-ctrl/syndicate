"""
SYNDIKAT Operations — Affiliate & SaaS Offer Scout.
Identifies high-converting B2B SaaS and CPA partner offers.
Formulates work orders for the Content Factory to generate organic campaigns.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class AffiliateScout:
    """Scouts and scores affiliate offers based on recurring MRR, EPC, and conversion potential."""

    CURATED_SAAS_BENCHMARKS = [
        {
            "name": "CloudVPS Infrastructure",
            "category": "DevOps / Hosting",
            "commission_type": "recurring_mrr",
            "payout": "25% lifetime",
            "avg_epc": 2.45,
            "cookie_days": 60,
            "target_niche": "developers, sysadmins, ai engineers",
            "priority": "HIGH"
        },
        {
            "name": "AI Automation Studio",
            "category": "Productivity AI",
            "commission_type": "recurring_mrr",
            "payout": "30% for 12 months",
            "avg_epc": 3.80,
            "cookie_days": 90,
            "target_niche": "marketers, freelancers, agency owners",
            "priority": "CRITICAL"
        },
        {
            "name": "Smart Ledger FinTech",
            "category": "Finance / Accounting",
            "commission_type": "cpa_fixed",
            "payout": "$85 per funded account",
            "avg_epc": 4.10,
            "cookie_days": 30,
            "target_niche": "crypto traders, solopreneurs",
            "priority": "HIGH"
        }
    ]

    def __init__(self, min_epc: float = 1.5):
        self.min_epc = min_epc

    def scout_top_offers(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Filter and rank partner programs."""
        offers = self.CURATED_SAAS_BENCHMARKS
        if category:
            offers = [o for o in offers if category.lower() in o["category"].lower()]

        # Sort by avg_epc descending
        ranked = sorted(offers, key=lambda x: x["avg_epc"], reverse=True)
        logger.info("scouted_affiliate_offers", count=len(ranked))
        return ranked

    def create_content_work_order(self, offer_name: str) -> Dict[str, Any]:
        """Convert an affiliate offer into an actionable Content Factory order."""
        offer = next((o for o in self.CURATED_SAAS_BENCHMARKS if o["name"].lower() == offer_name.lower()), self.CURATED_SAAS_BENCHMARKS[0])
        return {
            "order_id": f"wo_aff_{offer['name'].replace(' ', '_').lower()}",
            "target_offer": offer["name"],
            "target_audience": offer["target_niche"],
            "deliverables": [
                {"type": "short_video", "quantity": 2, "platform": "tiktok_youtube"},
                {"type": "x_thread", "quantity": 1, "platform": "x_threads"},
                {"type": "snipe_comment", "quantity": 5, "platform": "x"}
            ],
            "commission_potential": offer["payout"],
            "assigned_to": "content_factory"
        }
