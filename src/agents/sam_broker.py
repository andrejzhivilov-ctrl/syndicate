"""Broker bridge. No network. Broker is TBD. Demo and live are separate."""

from __future__ import annotations

from typing import Any, Mapping

from src.agent_platform.contracts import AccessRequest, ActionClass, DecisionStatus
from src.agent_platform.policy import AgentPolicy
from src.agents.sam_access import load_sam_manifest, sam_agent_profile
from src.agents.sam_policy import classify_venue, decide_execution


def submit_lot(
    *,
    symbol: str,
    venue: str | None = None,
    account_mode: str = "demo",
    approved: bool = False,
    confluence: Mapping[str, Any] | None = None,
    risk_blocked: bool = False,
    timeframe: str | None = None,
    env: Mapping[str, str] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Attempt to place a lot. Always fail-closed until broker+grant exist."""
    del env  # credentials would come from env later; never from profile
    data = dict(manifest or load_sam_manifest())
    live = data.get("live_modes") if isinstance(data.get("live_modes"), dict) else {}
    classified = classify_venue(symbol, venue)
    path = decide_execution(
        symbol=symbol,
        venue=classified,
        confluence=confluence,
        risk_blocked=risk_blocked,
        timeframe=timeframe,
        manifest=data,
    )
    base = {
        "agent": "sam",
        "symbol": symbol,
        "venue": classified,
        "account_mode": account_mode,
        "calls_broker": False,
        "filled": False,
        "grants_capability": False,
        "execution_path": path["path"],
        "broker": (data.get("execution") or {}).get("broker", "tbd"),
    }
    if classified == "investment" and not approved:
        return {**base, "status": "invest_discuss_required", "reason": "investments_need_andrii"}
    if path["path"] in {"blocked", "no_trade"}:
        return {**base, "status": path["path"], "reason": path.get("reason")}
    if path["path"] in {"hitl_signal", "invest_discuss"} and not approved:
        return {**base, "status": "hitl_required", "reason": path.get("reason")}

    if account_mode == "live" and live.get("broker_live") is not True:
        return {**base, "status": "broker_unavailable", "reason": "broker_live_not_granted"}
    if account_mode == "demo" and live.get("broker_demo") is not True:
        return {**base, "status": "broker_unavailable", "reason": "broker_demo_not_granted"}

    decision = AgentPolicy().evaluate(
        sam_agent_profile(data),
        AccessRequest(
            agent_id="sam",
            capability="trade.execute",
            action_class=ActionClass.FINANCIAL_OPERATION,
            resource_scope=f"broker/{account_mode}",
        ),
    )
    if decision.status is DecisionStatus.DENIED:
        return {**base, "status": "broker_unavailable", "reason": "trade_execute_not_granted"}
    return {**base, "status": "broker_unavailable", "reason": "broker_tbd_no_connector"}
