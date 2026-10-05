"""Sam's multi-layer confluence engine.

Implements the 5-layer synthesis described in ``SAM_QUANT_SPEC.md`` §4:

    1. SMC technique        (structure, FVG, order-block, liquidity sweep)
    2. Macro context        (yields, DXY, rate regime)
    3. COT positioning      (non-commercial net flow)
    4. On-chain/derivatives (funding, open-interest, stablecoin flow)
    5. Black-swan/news shield (event proximity gating)

Each layer returns a normalised score in ``[0, 100]`` together with a
human-readable rationale.  The engine combines them into a single weighted
*confluence score* and gates the decision behind a configurable threshold.

HONESTY NOTE
------------
No trading system can guarantee a fixed win-rate.  Markets are stochastic.
This engine does **not** hardcode or fabricate any "99%" or "95%" accuracy
figure.  The ``threshold`` is a *decision gate on the confluence score* — i.e.
"how many independent factors must agree before Sam is even allowed to propose
a trade to the human" — not a promise of outcome probability.  The default of
95 mirrors the spec's stated ``Точність > 95%`` gate; it is fully configurable
and every proposed signal still passes through mandatory Human-in-the-Loop
approval before any execution.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


# Default relative weights of each confluence layer. They are normalised at
# runtime so callers may override a subset without having to keep them summing
# to 1.0 themselves.
DEFAULT_LAYER_WEIGHTS: Dict[str, float] = {
    "smc": 0.30,
    "macro": 0.20,
    "cot": 0.20,
    "derivatives": 0.20,
    "news_shield": 0.10,
}

# Default gate on the *confluence score* (NOT a win-rate promise). See module
# docstring. Mirrors the spec's ">95%" phrasing; override via config.
DEFAULT_CONFLUENCE_THRESHOLD = 95.0


@dataclass
class LayerScore:
    """Score contributed by a single confluence layer."""

    name: str
    score: float                       # 0-100
    rationale: str = ""
    detail: Dict[str, Any] = field(default_factory=dict)
    # ``veto`` short-circuits the whole signal regardless of the weighted sum
    # (e.g. a high-impact news event inside the freeze window).
    veto: bool = False
    # ``unavailable`` marks a layer whose inputs were absent or unreadable, so no
    # honest score could be produced. The engine treats it exactly like a layer
    # that was never evaluated: it contributes 0 and is reported as ``missing``.
    # This exists because "we could not read the data" and "we read the data and
    # found nothing" are different findings — collapsing them lets an unreadable
    # layer silently count as a real market observation (see AGENTS.md §1).
    unavailable: bool = False

    def clamped(self) -> float:
        return max(0.0, min(100.0, float(self.score)))


@dataclass
class ConfluenceResult:
    """Aggregated result of the confluence synthesis."""

    score: float
    threshold: float
    passes: bool
    vetoed: bool
    layers: Dict[str, Dict[str, Any]]
    direction: Optional[str] = None
    rationale_lines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "confluence_score": round(self.score, 2),
            "threshold": round(self.threshold, 2),
            "passes": self.passes,
            "vetoed": self.vetoed,
            "direction": self.direction,
            "layers": self.layers,
            "rationale": self.rationale_lines,
        }


class ConfluenceEngine:
    """Combine per-layer scores into a gated confluence decision.

    The engine is deliberately *pure* — it does not fetch market data itself.
    Skill modules produce :class:`LayerScore` objects (from live data when the
    optional quant libraries are installed, or from supplied features), and the
    engine synthesises them.  This keeps it fully unit-testable and import-safe.
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        threshold: float = DEFAULT_CONFLUENCE_THRESHOLD,
    ) -> None:
        raw = dict(DEFAULT_LAYER_WEIGHTS)
        if weights:
            raw.update({k: float(v) for k, v in weights.items()})
        total = sum(raw.values()) or 1.0
        self._weights = {k: v / total for k, v in raw.items()}
        self._threshold = float(threshold)

    @property
    def threshold(self) -> float:
        return self._threshold

    @property
    def weights(self) -> Dict[str, float]:
        return dict(self._weights)

    def synthesize(
        self,
        layers: List[LayerScore],
        direction: Optional[str] = None,
    ) -> ConfluenceResult:
        """Combine ``layers`` into a single gated :class:`ConfluenceResult`."""

        by_name: Dict[str, LayerScore] = {ls.name: ls for ls in layers}
        vetoed = any(ls.veto for ls in layers)

        weighted_sum = 0.0
        weight_used = 0.0
        layer_dump: Dict[str, Dict[str, Any]] = {}
        rationale_lines: List[str] = []

        for name, weight in self._weights.items():
            ls = by_name.get(name)
            if ls is None or ls.unavailable:
                # Missing/unavailable layer contributes a neutral-conservative 0
                # so that an incomplete picture cannot accidentally clear a high
                # gate. An unreadable layer must never be scored as though its
                # input had been observed (e.g. "news calendar unknown" is not
                # "no news", and an unscored SMC layer is not "no structure").
                layer_dump[name] = {
                    "score": None,
                    "weight": round(weight, 4),
                    "rationale": ls.rationale if ls is not None else "layer not evaluated",
                    "missing": True,
                }
                continue
            score = ls.clamped()
            weighted_sum += score * weight
            weight_used += weight
            layer_dump[name] = {
                "score": round(score, 2),
                "weight": round(weight, 4),
                "rationale": ls.rationale,
                "veto": ls.veto,
                **({"detail": ls.detail} if ls.detail else {}),
            }
            if ls.rationale:
                rationale_lines.append(f"[{name}] {ls.rationale}")

        # Include any extra layers not present in the weight map for full audit.
        for name, ls in by_name.items():
            if name not in layer_dump:
                layer_dump[name] = {
                    "score": None if ls.unavailable else round(ls.clamped(), 2),
                    "weight": 0.0,
                    "rationale": ls.rationale,
                    "veto": ls.veto,
                    "unweighted": True,
                    **({"missing": True} if ls.unavailable else {}),
                }

        # If some weighted layers were missing, the achievable maximum shrinks;
        # we do NOT rescale upward (that would inflate a partial picture).
        final_score = weighted_sum if weight_used else 0.0

        passes = (not vetoed) and final_score >= self._threshold
        if vetoed:
            rationale_lines.insert(0, "VETO active — signal blocked regardless of score")

        return ConfluenceResult(
            score=final_score,
            threshold=self._threshold,
            passes=passes,
            vetoed=vetoed,
            layers=layer_dump,
            direction=direction,
            rationale_lines=rationale_lines,
        )

    @staticmethod
    def logistic_confidence(score: float, midpoint: float = 50.0, steepness: float = 0.08) -> float:
        """Map a confluence score to a soft 0-1 confidence for reporting only.

        This is a monotonic transform for display/telemetry — never presented to
        the user as a probability of profit.
        """
        try:
            return 1.0 / (1.0 + math.exp(-steepness * (score - midpoint)))
        except OverflowError:
            return 0.0 if score < midpoint else 1.0
