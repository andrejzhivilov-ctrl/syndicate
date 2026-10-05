"""
SYNDIKAT Operations — Growth & Funnel Analyst.
Monitors organic impression velocity, click-through rates (CTR), and conversion funnels.
MANDATE: All financial balances, net profit, and ROI calculations are strictly
delegated and submitted directly to Fin (CFO).
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)


class GrowthAnalyst:
    """Tracks traffic channels and formats financial metrics strictly for Fin (CFO)."""

    #: Metrics we can derive from whatever the caller supplies.
    _DERIVED = ("ctr",)

    def aggregate_channel_performance(
        self, channels: Optional[Dict[str, Dict[str, Any]]] = None, period: str = "Last 7 Days"
    ) -> Dict[str, Any]:
        """Aggregate cross-channel metrics.

        ``channels`` maps a channel name to its raw counters, e.g.::

            {"x_twitter": {"impressions": 1200, "link_clicks": 30}}

        When no channel data is supplied we MUST NOT invent numbers. The
        previous implementation returned a hardcoded block (128.5k impressions,
        2 560 clicks, 48 conversions) that was logged as if it were measured
        and then shipped to Fin inside a RESTRICTED_EXECUTIVE_FINANCE dossier.
        """
        if not channels:
            logger.warning("channel_performance_aggregated", status="no_data")
            return {
                "status": "unavailable",
                "period": period,
                "channels": {},
                "total_outbound_clicks": 0,
                "estimated_referral_conversions": 0,
                "data_source": "not_collected",
                "synthetic": False,
                "warning": (
                    "No channel data supplied. Metrics are NOT estimated — pass "
                    "real channel counters or wire up the platform APIs."
                ),
            }

        total_clicks = 0
        normalised: Dict[str, Dict[str, Any]] = {}
        for name, metrics in channels.items():
            metrics = dict(metrics or {})
            clicks = int(metrics.get("link_clicks", 0) or 0)
            impressions = int(metrics.get("impressions", metrics.get("views", 0)) or 0)
            if "ctr" not in metrics:
                metrics["ctr"] = f"{(clicks / impressions * 100):.2f}%" if impressions else "n/a"
            normalised[name] = metrics
            total_clicks += clicks

        data = {
            "status": "ok",
            "period": period,
            "channels": normalised,
            "total_outbound_clicks": total_clicks,
            "data_source": "caller_supplied",
            "synthetic": False,
        }
        logger.info("channel_performance_aggregated", total_clicks=total_clicks)
        return data

    def formulate_cfo_dossier(
        self, revenue_generated: Optional[float], direct_costs: Optional[float]
    ) -> Dict[str, Any]:
        """
        Package traffic and revenue data strictly for Fin (CFO) audit.
        Only Fin is authorized to sign off on ROI and ledger state.

        ``revenue_generated``/``direct_costs`` are required: a dossier built on
        defaulted money is worse than no dossier, because it reads as audited
        fact (the old defaults were $210 / $35 — a fabricated 500% ROI).
        """
        if revenue_generated is None or direct_costs is None:
            logger.warning("growth_dossier_missing_inputs")
            return {
                "recipient": "Fin (CFO)",
                "classification": "RESTRICTED_EXECUTIVE_FINANCE",
                "status": "unavailable",
                "cfo_audit_required": True,
                "warning": (
                    "revenue_generated and direct_costs are required. ROI is NOT "
                    "estimated — supply the real ledger figures."
                ),
            }

        revenue_generated = float(revenue_generated)
        direct_costs = float(direct_costs)
        roi = ((revenue_generated - direct_costs) / direct_costs * 100) if direct_costs > 0 else 0.0
        dossier = {
            "recipient": "Fin (CFO)",
            "classification": "RESTRICTED_EXECUTIVE_FINANCE",
            "status": "ok",
            "period_revenue": f"${revenue_generated:,.2f}",
            "period_costs": f"${direct_costs:,.2f}",
            "net_margin": f"${(revenue_generated - direct_costs):,.2f}",
            "calculated_roi": f"{roi:.1f}%",
            "target_roi_threshold": "300% (3x)",
            "cfo_audit_required": True
        }
        logger.info("growth_dossier_submitted_to_fin", net_margin=dossier["net_margin"])
        return dossier
