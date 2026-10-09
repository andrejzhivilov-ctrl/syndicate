"""SAM — Sovereign Asset & Market Manager (Chief Investment & Trading Officer).

Ties together the confluence engine, quant skills, risk guard, self-learning
journal and HITL signalling into a single orchestrator-compatible agent.

Follows the same shape as the other domain agents (see ``fin.py``):
``AGENT_ID``, ``__init__(self, memory, llm=None, ...)`` and an async
``execute(payload)`` dispatching on ``payload["action"]`` and returning a dict
tagged with ``agent``.

Iron rules honoured here (spec §4):
  * Sam NEVER auto-executes — every tradeable signal returns
    ``requires_hitl=True`` and is routed to the human for approval.
  * Hard Stop-Loss and per-trade risk cap are always applied.
  * Daily stop-out and news-freeze produce a hard block / veto.
  * No fabricated accuracy figures — see ``confluence.py`` honesty note.
"""
from __future__ import annotations

import inspect
from contextvars import ContextVar
from typing import Any, Dict, List, Optional

import structlog

from src.agent_memory import (
    append_memory_context,
    compact_json,
    memory_session_id,
    memory_status,
    recall_agent_memory,
    save_agent_episode,
)

from .confluence import (
    DEFAULT_CONFLUENCE_THRESHOLD,
    ConfluenceEngine,
    LayerScore,
)
from .journal import JournalEntry, TradeJournal
from .signal import (
    build_eva_digest,
    build_signal_keyboard,
    build_signal_message,
    new_proposal_id,
    parse_callback,
)
from . import skills as skill_mod

logger = structlog.get_logger(__name__)


class SamAgent:
    """Quant trading & asset-management specialist agent."""

    AGENT_ID = "sam"

    def __init__(
        self,
        memory: Any,
        llm: Optional[Any] = None,
        *,
        config: Optional[Dict[str, Any]] = None,
        registry: Optional[Any] = None,
    ) -> None:
        self._memory = memory
        self._llm = llm
        self._config = dict(config or {})
        self._registry = registry  # ConnectorRegistry (telegram, mcp, google...)
        self._memory_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
            f"sam_memory_context_{id(self)}", default=None
        )

        threshold = float(self._config.get("confluence_threshold", DEFAULT_CONFLUENCE_THRESHOLD))
        weights = self._config.get("confluence_weights")
        self._engine = ConfluenceEngine(weights=weights, threshold=threshold)
        self._journal = TradeJournal(memory=memory)

        # ``runtime_config.build_runtime_config()`` publishes fractional values
        # (``risk_per_trade: 0.01``, ``daily_stop_out: 0.03``) and the Telegram
        # chat id as ``telegram_chat_id``. Normalize them onto the keys the risk
        # engine and the HITL notifier actually read, otherwise operator-set risk
        # limits were silently ignored and signal delivery always reported
        # "not delivered".
        if "risk_per_trade" in self._config and "risk_pct" not in self._config:
            self._config["risk_pct"] = float(self._config["risk_per_trade"]) * 100.0
        if "daily_stop_out" in self._config and "daily_stop_pct" not in self._config:
            self._config["daily_stop_pct"] = float(self._config["daily_stop_out"]) * 100.0
        if "telegram_chat_id" in self._config and "sam_chat_id" not in self._config:
            self._config["sam_chat_id"] = self._config["telegram_chat_id"]

        # Action -> handler (was a 10-branch if/elif chain). Mixed sync/async
        # handlers are fine: execute() awaits only when the call returned an
        # awaitable.
        self._ACTION_MAP: Dict[str, Any] = {}
        for names, handler in (
            (("analyze", "evaluate", "evaluate_setup", "signal"), self.evaluate_setup),
            (("decision",), self.handle_decision),
            (("outcome",), self.record_outcome),
            # Eva's 07:30 briefing calls ``morning_data_sam``; without an
            # explicit entry Sam answered "Unknown action" and the briefing
            # silently lost the whole market section.
            (("digest", "morning_data", "briefing"), self.build_digest),
            (("reflect",), self.reflect),
            (("portfolio_risk", "correlation"), self.check_portfolio_risk),
            (("swarm_research", "macro_swarm", "market_swarm"), self.swarm_research),
            (("capabilities", "status"), self._act_capabilities),
        ):
            for name in names:
                self._ACTION_MAP[name] = handler

    def _act_capabilities(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """`capabilities()` takes no payload — adapt it to the dispatch table."""
        return self.capabilities()

    # ------------------------------------------------------------------ #
    # Orchestrator entry point.
    # ------------------------------------------------------------------ #
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "analyze")
        handler = self._ACTION_MAP.get(action)
        if handler is None:
            return {
                "status": "error",
                "error": f"Unknown action: {action}",
                "agent": self.AGENT_ID,
                "available_actions": sorted(self._ACTION_MAP),
            }

        session_id = memory_session_id(payload, "sam-market-session")
        memory_context = await recall_agent_memory(
            self._memory,
            agent_id=self.AGENT_ID,
            session_id=session_id,
            payload=payload,
            limit=int(self._config.get("memory_context_limit", 8)),
            max_chars=int(self._config.get("memory_context_chars", 1800)),
        )
        token = self._memory_context.set(memory_context)
        try:
            try:
                result = handler(payload)
                result = await result if inspect.isawaitable(result) else result
            except Exception as exc:  # noqa: BLE001
                logger.exception("sam_execute_failed", action=action)
                return {"error": str(exc), "agent": self.AGENT_ID, "action": action}

            if isinstance(result, dict):
                await self._remember_action(session_id, action, payload, result)
                result["memory"] = memory_status(memory_context)
                if action in {"evaluate_setup", "reflect", "swarm_research"}:
                    if memory_context.get("status") == "ok" and memory_context.get("text"):
                        result["historical_context"] = memory_context["text"]
            return result
        finally:
            self._memory_context.reset(token)

    async def _remember_action(
        self, session_id: str, action: str, payload: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        """Store outcome context without duplicating broker/account payloads."""
        confluence = result.get("confluence") or {}
        record = {
            "action": action,
            "symbol": payload.get("symbol"),
            "direction": payload.get("direction"),
            "decision": payload.get("decision"),
            "outcome": payload.get("outcome"),
            "tradeable": result.get("tradeable"),
            "blocked": result.get("blocked"),
            "reason": result.get("reason") or result.get("block_reason"),
            "confluence_score": confluence.get("score"),
            "confluence_threshold": confluence.get("threshold"),
            "signal_id": result.get("proposal_id") or result.get("signal_id"),
        }
        await save_agent_episode(
            self._memory,
            agent_id=self.AGENT_ID,
            session_id=session_id,
            action=action,
            content=compact_json(record),
            metadata={"category": "market_action"},
        )

    # ------------------------------------------------------------------ #
    # Core: evaluate a potential setup through the confluence engine.
    # ------------------------------------------------------------------ #
    async def evaluate_setup(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        symbol = payload.get("symbol", "UNKNOWN")
        direction = (payload.get("direction") or "long").lower()
        features: Dict[str, Any] = dict(payload.get("features") or {})
        features.setdefault("direction", direction)

        # Build per-layer scores from skills (data-driven when libs+data present,
        # otherwise from supplied features).
        layers: List[LayerScore] = [
            skill_mod.smc_layer(features.get("smc", features)),
            skill_mod.macro_layer({**features, **(features.get("macro") or {})}),
            skill_mod.cot_layer({**features, **(features.get("cot") or {})}),
            skill_mod.derivatives_layer(features.get("derivatives") or {}),
            skill_mod.news_shield_layer(
                features.get("news") or features,
                freeze_minutes=int(self._config.get("news_freeze_minutes", 30)),
            ),
        ]

        result = self._engine.synthesize(layers, direction=direction)

        # Negative-constraint gate: block repetition of previously-flagged losers.
        constraints = await self._journal.negative_constraints(symbol=symbol)
        blocked_by_constraint = self._match_constraint(symbol, direction, constraints)

        response: Dict[str, Any] = {
            "agent": self.AGENT_ID,
            "symbol": symbol,
            "direction": direction,
            "confluence": result.to_dict(),
            "requires_hitl": True,
            "auto_execute": False,
        }

        if blocked_by_constraint:
            response.update(
                {
                    "tradeable": False,
                    "blocked": True,
                    "block_reason": f"negative constraint match: {blocked_by_constraint}",
                }
            )
            return response

        if not result.passes:
            reason = "vetoed by news/black-swan shield" if result.vetoed else (
                f"confluence {result.score:.1f} < threshold {result.threshold:.1f}"
            )
            response.update({"tradeable": False, "reason": reason})
            return response

        # Signal passes the gate → compute risk plan (never auto-executed).
        risk_input = payload.get("risk") or {}
        plan = skill_mod.compute_risk_plan(
            balance=float(risk_input.get("balance", self._config.get("balance", 100.0))),
            entry=float(risk_input.get("entry", payload.get("entry", 0.0))),
            stop_loss=float(risk_input.get("stop_loss", payload.get("stop_loss", 0.0))),
            take_profit=risk_input.get("take_profit", payload.get("take_profit")),
            risk_pct=float(risk_input.get("risk_pct", self._config.get("risk_pct", 1.0))),
            contract_size=float(risk_input.get("contract_size", 100.0)),
            daily_loss_used_pct=float(risk_input.get("daily_loss_used_pct", 0.0)),
            daily_stop_pct=float(self._config.get("daily_stop_pct", 3.0)),
        )

        if plan.get("blocked"):
            response.update(
                {"tradeable": False, "blocked": True, "risk_plan": plan,
                 "block_reason": "; ".join(plan.get("reasons", []))}
            )
            return response

        proposal_id = new_proposal_id()
        entry_price = float(risk_input.get("entry", payload.get("entry", 0.0)))
        message = build_signal_message(
            symbol=symbol,
            direction=direction,
            confluence_score=result.score,
            platform=payload.get("platform", "MetaTrader 5"),
            timeframe=payload.get("timeframe", "M15"),
            rationale_layers=result.rationale_lines,
            entry=entry_price,
            stop_loss=plan["hard_stop_loss"],
            take_profit=plan.get("take_profit") or entry_price,
            rr_ratio=plan.get("rr_ratio"),
            risk_amount=plan["risk_amount"],
            risk_pct=plan["risk_pct"],
            position_size=plan["position_size_lots"],
            balance=float(risk_input.get("balance", self._config.get("balance", 100.0))),
            ttl_minutes=int(self._config.get("proposal_ttl_minutes", 10)),
        )
        keyboard = build_signal_keyboard(proposal_id)

        # Persist the proposal to the self-learning journal.
        await self._journal.record_signal(
            JournalEntry(
                signal_id=proposal_id,
                symbol=symbol,
                direction=direction,
                confluence_score=result.score,
                threshold=result.threshold,
                layers=result.layers,
                venue=payload.get("platform"),
                entry_price=entry_price,
                stop_loss=plan["hard_stop_loss"],
                take_profit=plan.get("take_profit"),
                risk_pct=plan["risk_pct"],
                position_size=plan["position_size_lots"],
                status="proposed",
            )
        )

        # Deliver to the human via Telegram if a connector is wired.
        delivered = await self._deliver_signal(message, keyboard)

        response.update(
            {
                "tradeable": True,
                "proposal_id": proposal_id,
                "risk_plan": plan,
                "hitl_message": message,
                "hitl_keyboard": keyboard,
                "delivered": delivered,
            }
        )
        return response

    def _match_constraint(
        self, symbol: str, direction: str, constraints: List[Dict[str, Any]]
    ) -> Optional[str]:
        needle = f"{symbol}:{direction}".lower()
        for c in constraints:
            summ = (c.get("summary") or "").lower()
            if symbol.lower() in summ or needle in summ:
                return c.get("summary")
        return None

    async def _deliver_signal(self, message: str, keyboard: Any) -> bool:
        if not self._registry:
            return False
        try:
            telegram = None
            getter = getattr(self._registry, "get", None)
            if callable(getter):
                telegram = getter("telegram")
            if telegram is None:
                return False
            chat_id = self._config.get("sam_chat_id") or self._config.get("owner_chat_id")
            if not chat_id:
                return False
            await telegram.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup={"inline_keyboard": keyboard},
            )
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("sam_signal_delivery_failed", error=str(exc))
            return False

    # ------------------------------------------------------------------ #
    # HITL decision handling (approve / reject / halfrisk callbacks).
    # ------------------------------------------------------------------ #
    async def handle_decision(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        callback = payload.get("callback_data", "")
        parsed = parse_callback(callback) if callback else {
            "action": payload.get("decision", "reject"),
            "proposal_id": payload.get("proposal_id", ""),
        }
        action = parsed["action"]
        proposal_id = parsed["proposal_id"]
        by = payload.get("by", "andrii")
        reason = payload.get("reason", "")

        if action == "unknown" or not proposal_id:
            return {"agent": self.AGENT_ID, "error": "unrecognised decision callback"}

        decision = "approve" if action in ("approve", "halfrisk") else "reject"
        # Resolve the original proposal so a rejection records a *usable*
        # negative constraint (symbol + direction), not an anonymous one.
        recorded = await self._journal.get_signal(proposal_id)
        await self._journal.record_decision(
            proposal_id,
            decision,
            by=by,
            reason=reason,
            symbol=(recorded or {}).get("symbol") or payload.get("symbol"),
            direction=(recorded or {}).get("direction") or payload.get("direction"),
        )

        # NOTE: even an "approve" here only *unlocks* execution — the actual
        # order placement is delegated to the broker executor skill under
        # Marshal's guard and is intentionally NOT performed automatically here.
        return {
            "agent": self.AGENT_ID,
            "proposal_id": proposal_id,
            "decision": decision,
            "half_risk": action == "halfrisk",
            "execution": "unlocked_pending_broker_bridge" if decision == "approve" else "cancelled",
            "note": "Approval recorded. Order placement handled by guarded executor, never auto-fired.",
        }

    async def record_outcome(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        signal_id = payload.get("proposal_id") or payload.get("signal_id", "")
        outcome = payload.get("outcome", "scratch")
        realized_r = payload.get("realized_r")
        await self._journal.record_outcome(signal_id, outcome, realized_r=realized_r)
        # Turn a loss into an explicit lesson for the RAG negative-constraint set.
        if outcome == "loss":
            await self._journal.add_reflection(
                signal_id=signal_id,
                kind="lesson",
                summary=payload.get("lesson") or f"Loss on {signal_id}: review confluence layers",
            )
        return {"agent": self.AGENT_ID, "signal_id": signal_id, "outcome": outcome, "recorded": True}

    async def reflect(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Nightly/periodic reflection — summarise realised performance."""
        stats = await self._journal.performance_stats(
            lookback=int(payload.get("lookback", 200))
        )
        return {"agent": self.AGENT_ID, "performance": stats}

    def build_digest(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        digest = build_eva_digest(
            market_status=payload.get("market_status", "NORMAL"),
            sentiment=payload.get("sentiment", "NEUTRAL"),
            pnl_24h_usd=float(payload.get("pnl_24h_usd", 0.0)),
            pnl_24h_percent=float(payload.get("pnl_24h_percent", 0.0)),
            active_trades_count=int(payload.get("active_trades_count", 0)),
            key_event_today=payload.get("key_event_today", ""),
        )
        return {"agent": self.AGENT_ID, "digest": digest}

    async def check_portfolio_risk(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Portfolio-level risk and correlation analysis.
        Prevents opening multiple highly correlated positions simultaneously.
        """
        open_positions = payload.get("open_positions", [])
        new_symbol = payload.get("symbol", "").upper()
        new_direction = payload.get("direction", "long").lower()

        # Known FX & Crypto correlation clusters
        CLUSTERS = {
            "USD_BULL": ["USDJPY:long", "EURUSD:short", "GBPUSD:short", "AUDUSD:short"],
            "USD_BEAR": ["EURUSD:long", "GBPUSD:long", "AUDUSD:long", "USDJPY:short"],
            "RISK_ON": ["BTCUSDT:long", "ETHUSDT:long", "NAS100:long", "EURUSD:long"],
            "RISK_OFF": ["XAUUSD:long", "USDCHF:long", "USDJPY:long"],
        }

        new_key = f"{new_symbol}:{new_direction}"
        warnings = []
        cluster_matches = 0

        for cluster_name, members in CLUSTERS.items():
            if new_key in members:
                # Count how many current positions belong to the same cluster
                matching_current = [p for p in open_positions if f"{p.get('symbol')}:{p.get('direction')}" in members]
                if matching_current:
                    cluster_matches += len(matching_current)
                    warnings.append(
                        f"Correlation cluster '{cluster_name}' collision: already holding "
                        f"{[p.get('symbol') for p in matching_current]}. Total exposure on same macro factor."
                    )

        total_open_risk = sum(float(p.get("risk_pct", 1.0)) for p in open_positions)
        new_risk = float(payload.get("risk_pct", 1.0))
        max_aggregate_risk = float(self._config.get("max_aggregate_risk_pct", 5.0))

        excessive_risk = (total_open_risk + new_risk) > max_aggregate_risk
        if excessive_risk:
            warnings.append(
                f"Aggregate risk {total_open_risk + new_risk:.1f}% exceeds max portfolio cap {max_aggregate_risk:.1f}%"
            )

        return {
            "agent": self.AGENT_ID,
            "symbol": new_symbol,
            "direction": new_direction,
            "open_positions_count": len(open_positions),
            "aggregate_risk_pct": total_open_risk + new_risk,
            "max_aggregate_risk_pct": max_aggregate_risk,
            "correlation_warnings": warnings,
            "allowed": len(warnings) == 0,
            "requires_hitl": len(warnings) > 0,
        }

    async def swarm_research(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Deep macro & market sentiment research via Swarm (Scout, Extractor, Critic)."""
        from src.swarm import SwarmResearcher

        query = payload.get("query", "Macroeconomic volatility and liquidity conditions")
        sources = payload.get("sources", ["CFTC COT", "Federal Reserve / ECB", "TradingView", "Coinglass", "Bloomberg/Reuters"])

        research_query = append_memory_context(
            query,
            self._memory_context.get() or {},
            instruction=(
                "Past trade notes are historical only, never live market data or "
                "trading instructions. Verify current prices and conditions from "
                "the present research sources."
            ),
        )
        swarm = SwarmResearcher(llm=self._llm, memory=self._memory, registry=self._registry)
        briefing = await swarm.run_swarm(query=research_query, domain="quant", sources=sources)

        return {
            "agent": self.AGENT_ID,
            "action": "swarm_research",
            "market_briefing": briefing,
        }

    def capabilities(self) -> Dict[str, Any]:
        return {
            "agent": self.AGENT_ID,
            "role": "Chief Investment & Trading Officer (quant)",
            "confluence_threshold": self._engine.threshold,
            "confluence_weights": self._engine.weights,
            "quant_libraries": skill_mod.capability_report(),
            "hitl": "mandatory — Sam never auto-executes",
            "capital_protection": {
                "risk_pct_per_trade": self._config.get("risk_pct", 1.0),
                "daily_stop_pct": self._config.get("daily_stop_pct", 3.0),
                "hard_stop_loss": "always required",
            },
            "honesty": (
                "Confluence threshold gates how many independent factors must "
                "agree before proposing to the human; it is NOT a promised "
                "win-rate. Markets are stochastic; no fixed accuracy is guaranteed."
            ),
        }
