"""Sam's HITL signal formatting.

Builds the Telegram signal message + inline keyboard exactly in the shape shown
in ``SAM_QUANT_SPEC.md`` §4, plus the compact internal digest handed to Eva
(spec §3 Б) for the shared morning/evening briefing.

Pure formatting only — no network calls.  The connectors in ``src/integrations``
do the actual sending; this keeps the message layout unit-testable.
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

DIRECTION_EMOJI = {"long": "🟢", "buy": "🟢", "short": "🔴", "sell": "🔴"}


def new_proposal_id() -> str:
    return uuid.uuid4().hex[:12]


def build_signal_message(
    *,
    symbol: str,
    direction: str,
    confluence_score: float,
    platform: str,
    timeframe: str,
    rationale_layers: List[str],
    entry: float,
    stop_loss: float,
    take_profit: float,
    rr_ratio: Optional[float],
    risk_amount: float,
    risk_pct: float,
    position_size: float,
    balance: float,
    ttl_minutes: int = 10,
) -> str:
    """Render the professional 5-layer HITL signal text (Ukrainian)."""
    dir_key = (direction or "").lower()
    emoji = DIRECTION_EMOJI.get(dir_key, "⚪")
    dir_label = "BUY" if dir_key in ("long", "buy") else "SELL"

    layers_block = "\n".join(
        f"{i}. {line}" for i, line in enumerate(rationale_layers[:5], start=1)
    ) or "1. (деталі шарів недоступні)"

    stop_pts = abs(entry - stop_loss)
    tp_pts = abs(take_profit - entry)
    rr_txt = f"1 : {rr_ratio}" if rr_ratio else "—"

    return (
        f"🚨 [СИГНАЛ СЕМА] Знайдено сетап високої впевненості "
        f"(Confluence: {confluence_score:.0f}%)!\n\n"
        f"📊 АКТИВ: {symbol} | НАПРЯМОК: {dir_label} {emoji}\n"
        f"🏛️ ПЛАТФОРМА: {platform}\n"
        f"⏱️ ТАЙМФРЕЙМ: {timeframe}\n\n"
        f"🧠 АРГУМЕНТАЦІЯ (ШАРИ СИНТЕЗУ):\n{layers_block}\n\n"
        f"🛡️ ПАРАМЕТРИ РИЗИКУ (Депозит ${balance:.2f}):\n"
        f"• Вхід: {entry}\n"
        f"• Hard Stop-Loss: {stop_loss} ({stop_pts:.2f} пункт.)\n"
        f"• Take-Profit: {take_profit} ({tp_pts:.2f} пункт.)\n"
        f"• Співвідношення R:R: {rr_txt}\n"
        f"• Ризик на угоду: ${risk_amount:.2f} ({risk_pct:.1f}% від депозиту)\n"
        f"• Об'єм: {position_size} лота\n\n"
        f"⏳ Пропозиція активна {ttl_minutes} хвилин.\n"
        f"⚠️ Рішення за вами — Сем ніколи не відкриває угоду самостійно."
    )


def build_signal_keyboard(proposal_id: str) -> List[List[Dict[str, str]]]:
    """Inline keyboard matching the spec's approve / reject / half-risk buttons.

    Returns rows compatible with ``TelegramConnector.build_inline_keyboard`` /
    Telegram's ``inline_keyboard`` schema (callback_data carries the action).
    """
    return [
        [
            {"text": "✅ СХВАЛИТИ ТА ВІДКРИТИ", "callback_data": f"approve_{proposal_id}"},
        ],
        [
            {"text": "❌ ВІДХИЛИТИ", "callback_data": f"reject_{proposal_id}"},
            {"text": "✏️ ВХІД З 0.5% РИЗИКОМ", "callback_data": f"halfrisk_{proposal_id}"},
        ],
    ]


def parse_callback(callback_data: str) -> Dict[str, str]:
    """Parse ``approve_<id>`` / ``reject_<id>`` / ``halfrisk_<id>`` callbacks."""
    for action in ("approve", "reject", "halfrisk"):
        prefix = f"{action}_"
        if callback_data.startswith(prefix):
            return {"action": action, "proposal_id": callback_data[len(prefix):]}
    return {"action": "unknown", "proposal_id": ""}


def build_eva_digest(
    *,
    market_status: str,
    sentiment: str,
    pnl_24h_usd: float,
    pnl_24h_percent: float,
    active_trades_count: int,
    key_event_today: str,
) -> Dict[str, Any]:
    """Compact digest for Eva's shared briefing (spec §3 Б JSON shape)."""
    from datetime import datetime, timezone

    briefing_line = (
        f"📊 Фінанси (Сем): За добу {pnl_24h_usd:+.2f}$ ({pnl_24h_percent:+.1f}%). "
        + (f"Сьогодні: {key_event_today}." if key_event_today else "Ключових подій немає.")
    )
    return {
        "agent": "sam",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "market_status": market_status,
        "sentiment": sentiment,
        "pnl_24h_usd": round(pnl_24h_usd, 2),
        "pnl_24h_percent": round(pnl_24h_percent, 2),
        "active_trades_count": active_trades_count,
        "key_event_today": key_event_today,
        "briefing_line": briefing_line,
    }
