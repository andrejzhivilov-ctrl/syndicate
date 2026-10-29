"""Bull / bear committee with a deterministic arbiter (pattern of TauricResearch/TradingAgents).

Two model roles argue opposite theses; neither decides. Each must back its case
with evidence that names a source. The arbiter here is code, not a third model:

* evidence without a source does not count (a claim is not data);
* a side with no sourced evidence contributes nothing, so one loud model cannot
  win by assertion; a committee where either side is missing is ``incomplete``;
* the output is a normalised signal in [-1, +1] plus a 0-100 confidence that
  ``risk.position_size`` and Andrii's approval consume. No order size here.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping

BULL_PROMPT = (
    "Ти — бичачий дослідник комітету Сема. Обстоюй тезу на зростання активу. Кожен аргумент підкріплюй "
    "конкретними даними з джерелом (звіт, ряд, дата). Без джерела аргумент не рахується. Не вказуй розмір позиції."
)
BEAR_PROMPT = (
    "Ти — ведмежий дослідник комітету Сема. Обстоюй тезу на падіння активу. Кожен аргумент підкріплюй "
    "конкретними даними з джерелом (звіт, ряд, дата). Без джерела аргумент не рахується. Не вказуй розмір позиції."
)
MAX_EVIDENCE = 8
MIN_CONFIDENCE = 60


def _sourced(side: Mapping[str, Any]) -> List[Dict[str, Any]]:
    items = side.get("evidence") if isinstance(side, Mapping) else None
    if not isinstance(items, list):
        return []
    kept = []
    for item in items[:MAX_EVIDENCE]:
        if not isinstance(item, Mapping):
            continue
        claim, source = item.get("claim"), item.get("source")
        weight = item.get("weight", 1.0)
        if (isinstance(claim, str) and claim.strip() and isinstance(source, str) and source.strip()
                and isinstance(weight, (int, float)) and not isinstance(weight, bool) and 0 < weight <= 1):
            kept.append({"claim": claim.strip()[:500], "source": source.strip()[:300], "weight": float(weight)})
    return kept


def arbitrate(bull: Mapping[str, Any] | None, bear: Mapping[str, Any] | None) -> Dict[str, Any]:
    """Weigh both sides' sourced evidence into a signal and a confidence."""
    if not isinstance(bull, Mapping) or not isinstance(bear, Mapping):
        return {"status": "incomplete", "reason": "both_sides_required", "strength": 0.0, "confidence": 0}
    pro, con = _sourced(bull), _sourced(bear)
    dropped = {"bull": len(bull.get("evidence") or []) - len(pro), "bear": len(bear.get("evidence") or []) - len(con)}
    w_pro, w_con = sum(e["weight"] for e in pro), sum(e["weight"] for e in con)
    total = w_pro + w_con
    if total == 0:
        return {"status": "incomplete", "reason": "no_sourced_evidence", "strength": 0.0, "confidence": 0,
                "unsourced_dropped": dropped}
    strength = (w_pro - w_con) / total            # -1 .. +1: who has the better-sourced case
    depth = min(1.0, total / MAX_EVIDENCE)        # little evidence -> little confidence
    confidence = round(100 * abs(strength) * depth)
    return {"status": "ok", "strength": round(strength, 4), "confidence": confidence,
            "actionable": confidence >= MIN_CONFIDENCE,
            "bull": {"thesis": str(bull.get("thesis") or "")[:500], "evidence": pro},
            "bear": {"thesis": str(bear.get("thesis") or "")[:500], "evidence": con},
            "unsourced_dropped": dropped, "requires_hitl": True}
