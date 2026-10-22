"""Atlas Agent — Chief of Global Geography, Travel Routes & Logistics for SYNDICATE Holding."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from src.agents.director_base import DirectorAgent, number, text


class AtlasAgent(DirectorAgent):
    AGENT_ID = "atlas"
    ACTIONS = {
        "capabilities": "capabilities",
        "plan_route": "plan_route",
        "evaluate_destination": "evaluate_destination",
        "accommodation_options": "accommodation_options",
        "routes": "routes",
        "report": "report",
        "book_ticket": "blocked_external",
        "book_accommodation": "blocked_external",
    }

    async def plan_route(self, payload: dict) -> dict:
        origin = text(payload["origin"], "origin", 150)
        destination = text(payload["destination"], "destination", 150)
        duration_days = int(number(payload["duration_days"], "duration_days", 1, 365))
        transport_mode = text(payload.get("transport_mode", "mixed_flight_rail"), "transport_mode", 50)
        budget_usd = Decimal(str(number(payload.get("estimated_budget_usd", 1000.0), "estimated_budget_usd", 10, 500000)))

        daily_budget = (budget_usd / Decimal(str(duration_days))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        record = self.store.add(
            "route",
            {
                "origin": origin,
                "destination": destination,
                "duration_days": duration_days,
                "transport_mode": transport_mode,
                "estimated_budget_usd": str(budget_usd.quantize(Decimal("0.01"))),
                "daily_budget_usd": str(daily_budget),
                "state": "planned_draft",
            },
        )
        return {"status": "ok", "route": record}

    async def evaluate_destination(self, payload: dict) -> dict:
        city = text(payload["city"], "city", 150)
        country = text(payload["country"], "country", 150)
        safety_index = number(payload.get("safety_index", 75.0), "safety_index", 0, 100)
        visa_required = bool(payload.get("visa_required", False))
        timezone_utc = text(payload.get("timezone_utc", "UTC+2"), "timezone_utc", 20)

        record = self.store.add(
            "destination",
            {
                "city": city,
                "country": country,
                "safety_index": safety_index,
                "visa_required": visa_required,
                "timezone_utc": timezone_utc,
                "recommendation": "recommended" if safety_index >= 60.0 else "caution_advised",
            },
        )
        return {"status": "ok", "destination": record}

    async def accommodation_options(self, payload: dict) -> dict:
        city = text(payload["city"], "city", 150)
        nights = int(number(payload["nights"], "nights", 1, 365))
        options = payload["options"]
        if not isinstance(options, list) or not options or len(options) > 30:
            raise ValueError("invalid_accommodation_options")

        compared = []
        for opt in options:
            name = text(opt["name"], "name", 200)
            nightly = Decimal(str(number(opt["nightly_usd"], "nightly_usd", 5, 25000)))
            rating = number(opt.get("rating", 8.5), "rating", 0, 10)
            total = (nightly * Decimal(str(nights))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            compared.append(
                {
                    "name": name,
                    "type": text(opt.get("type", "apartment"), "type", 50),
                    "nightly_usd": str(nightly.quantize(Decimal("0.01"))),
                    "total_usd": str(total),
                    "rating": rating,
                }
            )
        compared.sort(key=lambda r: (-r["rating"], float(r["total_usd"])))
        return {"status": "ok", "city": city, "nights": nights, "options": compared}

    async def routes(self, payload: dict) -> dict:
        return {"status": "ok", "records": self.store.list("route")}

    async def report(self, payload: dict) -> dict:
        routes = self.store.list("route")
        destinations = self.store.list("destination")
        return {
            "status": "ok",
            "routes_planned": len(routes),
            "destinations_evaluated": len(destinations),
            "external_actions": False,
        }
