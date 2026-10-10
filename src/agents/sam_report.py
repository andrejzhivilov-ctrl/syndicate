"""Eva/Fin payloads. Sam does not assign them work."""

from __future__ import annotations

from typing import Any

from src.agents.sam.signal import build_eva_digest


def build_eva_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    digest = build_eva_digest(
        market_status=str(snapshot.get("market_status", "UNKNOWN")),
        sentiment=str(snapshot.get("sentiment", "NEUTRAL")),
        pnl_24h_usd=float(snapshot.get("pnl_24h_usd", 0.0)),
        pnl_24h_percent=float(snapshot.get("pnl_24h_percent", 0.0)),
        active_trades_count=int(snapshot.get("active_trades_count", 0)),
        key_event_today=str(snapshot.get("key_event_today", "")),
    )
    return {
        "agent": "sam",
        "for_eva_payload": True,
        "eva_cannot_assign": True,
        "eva_must_not_fetch": True,
        "digest": digest,
    }


def build_fin_pnl_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent": "sam",
        "for_fin_payload": True,
        "fin_cannot_assign": True,
        "realized_pnl_usd": float(snapshot.get("realized_pnl_usd", 0.0)),
        "fees_usd": float(snapshot.get("fees_usd", 0.0)),
        "note": "Запис у hledger — рішення Фіна після payload, не доручення Сема.",
    }
