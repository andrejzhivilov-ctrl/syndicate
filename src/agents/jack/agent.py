"""Mathematical research and paper accounting; no real betting execution."""
from __future__ import annotations

from src.agents.director_base import DirectorAgent
from .engines import ENGINES
from .quant import evaluate, fair_probabilities
from .tracker import anti_tilt, record_paper, report, settle


class JackAgent(DirectorAgent):
    AGENT_ID = "jack"
    ACTIONS = {"capabilities": "capabilities", "model": "model", "evaluate": "evaluate",
               "benchmark": "benchmark", "record_paper": "record_paper", "settle_paper": "settle_paper",
               "report": "report", "scout": "scout", "place_bet": "blocked_external", "alert": "alert"}

    def __init__(self, *args, scout=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.scout_client = scout

    async def model(self, payload: dict) -> dict:
        engine = ENGINES.get(payload["sport"])
        if engine is None:
            raise ValueError("unsupported_sport")
        return {"status": "ok", "source_mode": "supplied_inputs", "calibrated": False,
                "estimate": engine(payload["inputs"])}

    async def evaluate(self, payload: dict) -> dict:
        guard = anti_tilt(self.store.list("paper"))
        if guard["blocked"]:
            return {"status": "blocked", "eligible": False, "reason": "anti_tilt", **guard}
        return evaluate(payload, risk_cap=self.config.get("event_risk_cap", 0.01))

    async def benchmark(self, payload: dict) -> dict:
        return {"status": "ok", "fair_probabilities": fair_probabilities(payload["odds"]),
                "method": "proportional_vig_removal", "source_mode": "supplied_market"}

    async def record_paper(self, payload: dict) -> dict:
        signal = await self.evaluate(payload)
        if not signal.get("eligible"):
            return signal
        if signal["stake"] <= 0:
            raise ValueError("stake_below_minor_unit")
        return {"status": "ok", "record": record_paper(self.store, payload, signal), "mode": "paper"}

    async def settle_paper(self, payload: dict) -> dict:
        return {"status": "ok", "record": settle(self.store, payload), "mode": "paper"}

    async def report(self, payload: dict) -> dict:
        return report(self.store)

    async def scout(self, payload: dict) -> dict:
        if self.scout_client is None:
            return {"status": "unavailable", "value": None, "warning": "odds_provider_not_configured",
                    "requested_bookmakers": ["parimatch", "vbet", "pinnacle", "betfair"]}
        return await self.scout_client.fetch(payload)

    async def alert(self, payload: dict) -> dict:
        signal = await self.evaluate(payload)
        if not signal.get("eligible"):
            return signal
        return {"status": "approval_required", "requires_hitl": True, "delivered": False,
                "message": f"JACK +EV {signal['ev']:.2%}; stake {signal['stake_fraction']:.2%} of bankroll. "
                           "Paper analysis; verify source and current odds.",
                "signal": signal, "warning": "Telegram delivery adapter not enabled"}
