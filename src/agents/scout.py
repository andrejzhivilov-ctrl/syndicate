"""Scout Agent — Chief Marketing Strategist & Trend Scout for SYNDICATE Holding."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from src.agents.director_base import DirectorAgent, number, text
from src.pii import PIIRedactor

VALID_DEPARTMENTS = {"oscar", "dex", "tyler", "ray"}
VALID_CHANNELS = {"youtube", "tiktok", "reddit", "x", "threads", "blog", "quora"}


class ScoutAgent(DirectorAgent):
    AGENT_ID = "scout"
    ACTIONS = {
        "capabilities": "capabilities",
        "analyze_niche": "analyze_niche",
        "extract_pains": "extract_pains",
        "generate_hooks": "generate_hooks",
        "marketing_brief": "marketing_brief",
        "batch_plan": "batch_plan",
        "briefs": "briefs",
        "report": "report",
        "launch_campaign": "blocked_external",
    }

    async def analyze_niche(self, payload: dict) -> dict:
        niche_name = text(payload["niche"], "niche", 200)
        search_volume = number(payload["monthly_search_volume"], "monthly_search_volume", 0, 1e9)
        competition_index = number(payload["competition_index"], "competition_index", 0, 100)
        avg_cpc = Decimal(str(number(payload.get("avg_cpc_usd", 1.0), "avg_cpc_usd", 0, 1000)))

        # Opportunity score (0..100): high volume & moderate/low competition yields strong score
        vol_factor = min(50.0, (search_volume / 10000.0) * 10.0)
        comp_penalty = (competition_index / 100.0) * 35.0
        cpc_bonus = float(min(Decimal("25.0"), avg_cpc * Decimal("5.0")))
        raw_score = max(0.0, min(100.0, 40.0 + vol_factor - comp_penalty + cpc_bonus))
        score = float(Decimal(str(raw_score)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

        recommended_wings = []
        if score >= 50:
            recommended_wings.append("oscar")
            recommended_wings.append("dex")
        if competition_index <= 65:
            recommended_wings.append("tyler")
            recommended_wings.append("ray")

        record = self.store.add(
            "niche_analysis",
            {
                "niche": niche_name,
                "monthly_search_volume": int(search_volume),
                "competition_index": competition_index,
                "avg_cpc_usd": str(avg_cpc.quantize(Decimal("0.01"))),
                "opportunity_score": score,
                "verdict": "high_priority" if score >= 70 else ("viable" if score >= 45 else "saturated_or_low_demand"),
                "recommended_wings": recommended_wings,
            },
        )
        return {"status": "ok", "analysis": record}

    async def extract_pains(self, payload: dict) -> dict:
        comments = payload["comments"]
        if not isinstance(comments, list) or not comments or len(comments) > 5000:
            raise ValueError("invalid_comment_batch")
        redactor = PIIRedactor()
        extracted = []
        for item in comments:
            channel = text(item["channel"], "channel", 20).lower()
            if channel not in VALID_CHANNELS:
                raise ValueError("unsupported_channel")
            cid = text(item["id"], "id", 100)
            clean_body, _ = redactor.redact(text(item["text"], "text", 5000))
            lower = clean_body.lower()
            is_pain = any(
                kw in lower
                for kw in (
                    "how", "why", "problem", "issue", "struggle", "expensive", "help", "broken",
                    "як", "чому", "проблема", "болить", "дорого", "не працює", "порадьте", "важко",
                )
            )
            extracted.append(
                {
                    "id": cid,
                    "channel": channel,
                    "text": clean_body,
                    "signal_type": "pain_or_question" if is_pain else "general_feedback",
                }
            )
        pains = [row for row in extracted if row["signal_type"] == "pain_or_question"]
        return {
            "status": "ok",
            "total_processed": len(extracted),
            "pain_points_count": len(pains),
            "pain_points": pains,
            "redacted_pii": True,
        }

    async def generate_hooks(self, payload: dict) -> dict:
        pain_point = text(payload["pain_point"], "pain_point", 500)
        target_wing = text(payload.get("target_wing", "oscar"), "target_wing", 30).lower()
        if target_wing not in VALID_DEPARTMENTS:
            raise ValueError("unsupported_target_wing")

        hooks = [
            {
                "angle": "contrarian_truth",
                "retention_window": "0-3s",
                "hook_ua": f"Чому 90% помиляються, коли намагаються вирішити: {pain_point}",
                "hook_en": f"Why 90% fail when trying to solve: {pain_point}",
            },
            {
                "angle": "inception_diagnostic",
                "retention_window": "0-3s",
                "hook_ua": f"Прихований корінь проблеми «{pain_point}», про який мовчать експерти",
                "hook_en": f"The hidden root cause behind '{pain_point}' that experts ignore",
            },
            {
                "angle": "systemic_protocol",
                "retention_window": "0-3s",
                "hook_ua": f"Покроковий протокол усунення «{pain_point}» без зайвих витрат",
                "hook_en": f"Step-by-step protocol to eliminate '{pain_point}' without wasted budget",
            },
        ]
        return {"status": "ok", "pain_point": pain_point, "target_wing": target_wing, "hooks": hooks}

    async def marketing_brief(self, payload: dict) -> dict:
        niche = text(payload["niche"], "niche", 200)
        pain_point = text(payload["pain_point"], "pain_point", 500)
        target_wing = text(payload.get("target_wing", "oscar"), "target_wing", 30).lower()
        if target_wing not in VALID_DEPARTMENTS:
            raise ValueError("unsupported_target_wing")

        brief = self.store.add(
            "brief",
            {
                "niche": niche,
                "pain_point": pain_point,
                "target_wing": target_wing,
                "inception_angle": text(payload.get("inception_angle", "Solve pain via educational insight first"), "inception_angle", 500),
                "state": "ready_for_wing",
            },
        )
        return {"status": "ok", "brief": brief}

    async def batch_plan(self, payload: dict) -> dict:
        days = int(number(payload.get("horizon_days", 4), "horizon_days", 3, 7))
        items = payload["items"]
        if not isinstance(items, list) or not items or len(items) > 50:
            raise ValueError("invalid_batch_items")
        saved = []
        for item in items:
            res = await self.marketing_brief(item)
            saved.append(res["brief"])
        return {"status": "ok", "horizon_days": days, "planned_count": len(saved), "briefs": saved}

    async def briefs(self, payload: dict) -> dict:
        return {"status": "ok", "records": self.store.list("brief")}

    async def report(self, payload: dict) -> dict:
        niches = self.store.list("niche_analysis")
        briefs = self.store.list("brief")
        return {
            "status": "ok",
            "niches_analyzed": len(niches),
            "marketing_briefs_prepared": len(briefs),
            "external_actions": False,
        }
