"""Sam's quant skill modules.

Each function turns raw market features into a :class:`~src.agents.sam.confluence.LayerScore`.
Where the optional institutional libraries named in ``SAM_QUANT_SPEC.md`` §6 are
installed (``smartmoneyconcepts``, ``pandas-ta``, ``cot-reports``, ``ccxt``,
``Riskfolio-Lib``, ``yfinance``) they are used to compute features from live
data; otherwise the caller may pass a pre-computed ``features`` dict and the
skill degrades gracefully.  **Every third-party import is optional** so this
module is always import-safe.

The skills never place orders and never contact a broker.  They only produce
scores + rationale for the confluence engine.  Execution is exclusively via
Human-in-the-Loop (see ``signal.py`` / ``agent.py``).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from .confluence import LayerScore

logger = structlog.get_logger(__name__)


# --------------------------------------------------------------------------- #
# Optional dependency probing (import-safe).
# --------------------------------------------------------------------------- #
def _has_module(name: str) -> bool:
    import importlib.util

    return importlib.util.find_spec(name) is not None


HAS_SMC = _has_module("smartmoneyconcepts")
HAS_PANDAS_TA = _has_module("pandas_ta")
HAS_COT = _has_module("cot_reports")
HAS_CCXT = _has_module("ccxt")
HAS_RISKFOLIO = _has_module("riskfolio")
HAS_YFINANCE = _has_module("yfinance")


# --------------------------------------------------------------------------- #
# Layer 1 — Smart Money Concepts technical structure.
# --------------------------------------------------------------------------- #
def smc_layer(features: Dict[str, Any]) -> LayerScore:
    """Score SMC confluence: FVG test, order-block, liquidity sweep, BOS/CHoCH.

    ``features`` may contain booleans / floats already computed upstream:
        - ``fvg_test`` (bool), ``order_block`` (bool),
          ``liquidity_sweep`` (bool), ``bos`` (bool), ``choch`` (bool)
        - ``trend_aligned`` (bool)
    When ``smartmoneyconcepts`` and a ``candles`` DataFrame are available the
    structural flags are derived instead of trusted blindly.

    If candles are supplied but cannot be analysed (library missing, or any
    individual probe raising), the layer is returned as ``unavailable`` rather
    than scored 0.0. Scoring it would report "no structural confluence
    detected", which is indistinguishable from a genuine analysis result.
    """
    f = dict(features or {})

    if f.get("candles") is not None:
        if not HAS_SMC:
            return LayerScore(
                name="smc",
                score=0.0,
                rationale="SMC: smartmoneyconcepts not installed — candles were not analysed",
                unavailable=True,
            )
        try:  # pragma: no cover - requires optional dep + data
            derived, failed = _derive_smc_features(f["candles"])
            f.update(derived)
        except Exception as exc:  # noqa: BLE001
            return LayerScore(
                name="smc",
                score=0.0,
                rationale=f"SMC: candle analysis failed ({type(exc).__name__}: {exc})",
                unavailable=True,
            )
        if failed:
            return LayerScore(
                name="smc",
                score=0.0,
                rationale="SMC: could not derive " + ", ".join(failed),
                detail={"failed": failed},
                unavailable=True,
            )

    checks = {
        "liquidity_sweep": 25.0,
        "order_block": 25.0,
        "fvg_test": 20.0,
        "bos": 15.0,
        "trend_aligned": 15.0,
    }

    # Nothing to read: no candles were supplied and the caller provided none of
    # the structural flags. Reporting "no structural confluence detected" here
    # would invent a market observation out of a missing input.
    if not any(key in f for key in checks):
        return LayerScore(
            name="smc",
            score=0.0,
            rationale="SMC: no candles and no structural flags supplied — layer skipped",
            unavailable=True,
        )

    score = 0.0
    hit: List[str] = []
    for key, pts in checks.items():
        if f.get(key):
            score += pts
            hit.append(key)

    # CHoCH against the intended direction is a caution flag, not a full veto.
    if f.get("choch") and not f.get("bos"):
        score *= 0.7

    rationale = (
        "SMC: " + ", ".join(hit) if hit else "SMC: no structural confluence detected"
    )
    return LayerScore(name="smc", score=score, rationale=rationale, detail={"hits": hit})


def _derive_smc_features(candles: Any) -> "tuple[Dict[str, Any], List[str]]":  # pragma: no cover
    """Derive structural flags from OHLC candles via smartmoneyconcepts.

    Returns ``(features, failed_flags)``. A library call that raises must be
    *reported*, never swallowed: silently dropping one flag turns "we could not
    compute this" into "this structure is absent", and an absent FVG/order-block
    is itself a bearish/neutral finding that feeds the confluence score.
    """
    from smartmoneyconcepts import smc  # type: ignore

    out: Dict[str, Any] = {}
    failed: List[str] = []

    probes = (
        ("fvg_test", lambda: smc.fvg(candles)),
        ("order_block", lambda: smc.ob(candles)),
        ("liquidity_sweep", lambda: smc.liquidity(candles)),
    )
    for flag, probe in probes:
        try:
            result = probe()
            out[flag] = bool(
                result is not None and len(result) and result.iloc[-1].notna().any()
            )
        except Exception as exc:  # noqa: BLE001
            failed.append(f"{flag} ({type(exc).__name__})")

    return out, failed


# --------------------------------------------------------------------------- #
# Layer 2 — Macro context.
# --------------------------------------------------------------------------- #
def macro_layer(features: Dict[str, Any]) -> LayerScore:
    """Score macro alignment for the intended direction.

    ``features``:
        - ``direction`` ('long'/'short')
        - ``real_yield_delta`` (float, %, negative is metals-bullish)
        - ``dxy_delta`` (float, %, negative is risk/metals-bullish)
        - ``regime`` (str: expansion/inflation/recession/recovery)

    With neither macro input supplied the layer is ``unavailable`` — the old
    "neutral baseline 40" was a numeric score derived from an empty payload and
    was described in its own rationale as "insufficient data".
    """
    f = dict(features or {})
    direction = (f.get("direction") or "long").lower()

    if f.get("real_yield_delta") is None and f.get("dxy_delta") is None:
        return LayerScore(
            name="macro",
            score=0.0,
            rationale="Macro: no real-yield or DXY data — layer skipped",
            detail={"regime": f.get("regime")},
            unavailable=True,
        )

    score = 40.0  # neutral baseline, only reachable with at least one input
    notes: List[str] = []

    ry = f.get("real_yield_delta")
    if ry is not None:
        if direction == "long" and ry < 0:
            score += 20
            notes.append(f"real yields down {ry:+.2f}%")
        elif direction == "short" and ry > 0:
            score += 20
            notes.append(f"real yields up {ry:+.2f}%")
        else:
            score -= 10

    dxy = f.get("dxy_delta")
    if dxy is not None:
        if direction == "long" and dxy < 0:
            score += 20
            notes.append(f"DXY {dxy:+.2f}%")
        elif direction == "short" and dxy > 0:
            score += 20
            notes.append(f"DXY {dxy:+.2f}%")
        else:
            score -= 10

    regime = f.get("regime")
    if regime:
        notes.append(f"regime={regime}")

    rationale = "Macro: " + ("; ".join(notes) if notes else "neutral / insufficient data")
    return LayerScore(name="macro", score=score, rationale=rationale, detail={"regime": regime})


# --------------------------------------------------------------------------- #
# Layer 3 — COT institutional positioning.
# --------------------------------------------------------------------------- #
def cot_layer(features: Dict[str, Any]) -> LayerScore:
    """Score CFTC COT non-commercial net-position flow.

    ``features``:
        - ``direction``
        - ``noncommercial_net_change`` (int, weekly change in net contracts)
        - ``noncommercial_net`` (int, absolute net)

    Without a net-change figure the layer is ``unavailable``: "no fresh COT
    flow" is a statement about missing data, and it used to be reported as a
    45/100 score.
    """
    f = dict(features or {})
    direction = (f.get("direction") or "long").lower()
    change = f.get("noncommercial_net_change")

    if change is None:
        return LayerScore(
            name="cot",
            score=0.0,
            rationale="COT: no net-change figure supplied — layer skipped",
            unavailable=True,
        )

    score = 45.0
    notes: List[str] = []

    if direction == "long" and change > 0:
        score += min(45.0, abs(change) / 200.0)
        notes.append(f"funds added +{change} net longs")
    elif direction == "short" and change < 0:
        score += min(45.0, abs(change) / 200.0)
        notes.append(f"funds added {change} net shorts")
    else:
        score -= 15
        notes.append(f"COT flow against direction ({change:+})")

    rationale = "COT: " + ("; ".join(notes) if notes else "no fresh COT flow")
    return LayerScore(name="cot", score=score, rationale=rationale)


# --------------------------------------------------------------------------- #
# Layer 4 — Crypto derivatives / on-chain microstructure.
# --------------------------------------------------------------------------- #
def derivatives_layer(features: Dict[str, Any]) -> LayerScore:
    """Score derivative/on-chain microstructure.

    ``features``:
        - ``direction``
        - ``funding_rate`` (float, per-8h; extreme positive = crowded longs)
        - ``oi_change_pct`` (float)
        - ``stablecoin_inflow`` (bool)
    For non-crypto assets pass an empty dict → the layer is ``unavailable``
    (it does not apply, so it must contribute nothing rather than a fabricated
    neutral score). A payload that carries no ``funding_rate`` is likewise
    ``unavailable``: without the primary microstructure input there is nothing
    to score, and a manufactured "neutral 45" would quietly add weight to a
    trade that the data never supported.
    """
    f = dict(features or {})
    if not f:
        return LayerScore(
            name="derivatives",
            score=0.0,
            rationale="Derivatives: n/a for this asset — layer skipped",
            unavailable=True,
        )

    funding = f.get("funding_rate")
    if funding is None:
        return LayerScore(
            name="derivatives",
            score=0.0,
            rationale="Derivatives: no funding-rate data — layer skipped",
            unavailable=True,
        )

    direction = (f.get("direction") or "long").lower()
    score = 45.0
    notes: List[str] = []

    # Contrarian: very positive funding favours shorts (long squeeze risk).
    if direction == "long" and funding <= 0.01:
        score += 20
        notes.append(f"funding benign {funding:.4f}")
    elif direction == "short" and funding >= 0.03:
        score += 20
        notes.append(f"funding hot {funding:.4f} (squeeze risk)")
    else:
        score -= 5

    if f.get("stablecoin_inflow"):
        score += 15
        notes.append("stablecoin inflow +")

    oi = f.get("oi_change_pct")
    if oi is not None:
        notes.append(f"OI {oi:+.1f}%")

    rationale = "Derivatives: " + ("; ".join(notes) if notes else "neutral")
    return LayerScore(name="derivatives", score=score, rationale=rationale)


# --------------------------------------------------------------------------- #
# Layer 5 — Black-swan / news shield (can VETO).
# --------------------------------------------------------------------------- #
def news_shield_layer(features: Dict[str, Any], freeze_minutes: int = 30) -> LayerScore:
    """Gate trading around high-impact events.

    ``features``:
        - ``minutes_to_high_impact`` (int|None): minutes until next High-impact
          event. If within ``freeze_minutes`` → hard VETO.
        - ``news_calendar_checked`` (bool): the caller must set this to assert
          that an economic calendar was actually consulted and holds no
          high-impact event in the window. Without it, ``minutes_to_high_impact
          is None`` is treated as "unknown", not as "clear" (see below).
        - ``black_swan`` (bool): manual/automatic kill switch.

    Why the explicit ``news_calendar_checked`` flag: ``None`` is ambiguous — it
    can mean "checked, nothing scheduled" *or* "we have no calendar wired up".
    Collapsing the two made this layer fail **open**: an unknown calendar scored
    80/100 and never vetoed, while an FOMC/NFP/CPI release could be minutes
    away. A shield whose whole job is to fail closed must not award points for
    data it never read.
    """
    f = dict(features or {})
    if f.get("black_swan"):
        return LayerScore(
            name="news_shield",
            score=0.0,
            rationale="Black-swan shield ACTIVE — trading frozen",
            veto=True,
        )

    mins = f.get("minutes_to_high_impact")
    if mins is not None:
        if mins <= freeze_minutes:
            return LayerScore(
                name="news_shield",
                score=0.0,
                rationale=f"High-impact event in {mins} min (< {freeze_minutes}m freeze) — VETO",
                veto=True,
            )
        # Farther the event, the safer.
        score = min(100.0, 60.0 + mins / 10.0)
        return LayerScore(
            name="news_shield",
            score=score,
            rationale=f"News: next high-impact in {mins} min",
        )

    if f.get("news_calendar_checked"):
        return LayerScore(
            name="news_shield",
            score=80.0,
            rationale="News: calendar checked, no high-impact event in window",
            detail={"calendar_checked": True},
        )

    # No calendar and no explicit claim that one was read → fail closed.
    return LayerScore(
        name="news_shield",
        score=0.0,
        rationale="News: economic calendar unavailable — cannot rule out a high-impact event",
        unavailable=True,
    )


# --------------------------------------------------------------------------- #
# Risk guard — position sizing & capital protection (spec §4 / skill #5, #16).
# --------------------------------------------------------------------------- #
def compute_risk_plan(
    *,
    balance: float,
    entry: float,
    stop_loss: float,
    take_profit: Optional[float] = None,
    risk_pct: float = 1.0,
    contract_size: float = 100.0,
    min_lot: float = 0.01,
    lot_step: float = 0.01,
    daily_loss_used_pct: float = 0.0,
    daily_stop_pct: float = 3.0,
) -> Dict[str, Any]:
    """Deterministic risk sizing with hard capital-protection rules.

    Enforces:
      * risk per trade capped at ``risk_pct`` of ``balance`` (spec: 1% on $100);
      * mandatory Hard Stop-Loss (raises if missing / on wrong side);
      * daily stop-out — refuses new risk once ``daily_stop_pct`` (default 3%)
        of the day's loss budget is consumed.
    Returns a plan dict; ``blocked`` is True when a protection rule fires.
    """
    result: Dict[str, Any] = {"blocked": False, "reasons": []}

    if stop_loss is None or entry is None:
        result["blocked"] = True
        result["reasons"].append("missing entry or hard stop-loss")
        return result

    direction = "long" if stop_loss < entry else "short"
    stop_distance = abs(entry - stop_loss)
    if stop_distance <= 0:
        result["blocked"] = True
        result["reasons"].append("stop-loss equals entry (zero risk distance)")
        return result

    # Daily stop-out guard.
    if daily_loss_used_pct >= daily_stop_pct:
        result["blocked"] = True
        result["reasons"].append(
            f"daily stop-out hit ({daily_loss_used_pct:.2f}% >= {daily_stop_pct:.2f}%)"
        )

    risk_amount = balance * (risk_pct / 100.0)
    # Value per 1.0 lot per unit of price move.
    per_lot_risk = stop_distance * contract_size
    raw_lots = risk_amount / per_lot_risk if per_lot_risk else 0.0

    # Round DOWN to lot step, floor at min_lot only if it doesn't exceed budget.
    steps = int(raw_lots / lot_step) if lot_step else 0
    lots = round(steps * lot_step, 8)
    if lots < min_lot:
        # Using min_lot would risk more than allowed → flag it explicitly.
        min_lot_risk = min_lot * per_lot_risk
        if min_lot_risk > risk_amount * 1.0001:
            result["reasons"].append(
                f"min lot {min_lot} risks ${min_lot_risk:.2f} > budget ${risk_amount:.2f}"
            )
        lots = min_lot

    rr = None
    if take_profit is not None:
        reward = abs(take_profit - entry)
        rr = round(reward / stop_distance, 2) if stop_distance else None

    result.update(
        {
            "direction": direction,
            "risk_amount": round(risk_amount, 2),
            "risk_pct": risk_pct,
            "stop_distance": round(stop_distance, 8),
            "position_size_lots": lots,
            "per_lot_risk": round(per_lot_risk, 4),
            "rr_ratio": rr,
            "hard_stop_loss": stop_loss,
            "take_profit": take_profit,
        }
    )
    return result


# Registry of the confluence layer producers for convenient iteration.
LAYER_PRODUCERS = {
    "smc": smc_layer,
    "macro": macro_layer,
    "cot": cot_layer,
    "derivatives": derivatives_layer,
    "news_shield": news_shield_layer,
}


def capability_report() -> Dict[str, bool]:
    """Report which optional quant libraries are actually available at runtime."""
    return {
        "smartmoneyconcepts": HAS_SMC,
        "pandas_ta": HAS_PANDAS_TA,
        "cot_reports": HAS_COT,
        "ccxt": HAS_CCXT,
        "riskfolio": HAS_RISKFOLIO,
        "yfinance": HAS_YFINANCE,
    }
