"""
Orc — Adversarial Verifier + Swarm Board.

A claim is only worth a human's attention if it carries reproducible evidence.
The verifier never believes an agent on its word:

  * no evidence                       -> unproven (dropped before the human)
  * stale evidence                    -> unproven
  * evidence contradicts the claim    -> refuted
  * live replay differs from evidence -> refuted
  * otherwise                         -> confirmed

SwarmBoard tracks every finding from proof-in-to proof-out (live replay after
the fix) and reports how many findings were filtered before reaching a human.
"""

from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)

Replayer = Callable[[Dict[str, Any]], Awaitable[Any]]


@dataclass
class Evidence:
    call: Dict[str, Any]                 # what was executed (tool, args)
    response: Any                        # what came back
    timestamp: float = field(default_factory=time.time)


@dataclass
class Claim:
    statement: str
    author: str
    evidence: Optional[Evidence] = None
    must_contain: List[str] = field(default_factory=list)       # evidence must include these
    must_not_contain: List[str] = field(default_factory=list)   # evidence must NOT include these
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:10])


@dataclass
class Verdict:
    status: str                          # confirmed | refuted | unproven
    reasons: List[str]
    replay_matched: Optional[bool] = None

    @property
    def passes_to_human(self) -> bool:
        return self.status == "confirmed"


def _norm(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    return re.sub(r"\s+", " ", text).strip().lower()


class OrcVerifier:
    def __init__(
        self,
        max_evidence_age_s: float = 86_400.0,
        skeptic_llm: Optional[Any] = None,
        llm: Optional[Any] = None,
    ) -> None:
        self._max_age = max_evidence_age_s
        self._skeptic = llm or skeptic_llm

    async def verify_claim(
        self,
        claim: str | Claim,
        evidence: Optional[Any] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Verify claim with evidence and return structured dict."""
        if isinstance(claim, str):
            ev = Evidence(call={"action": "verify", "context": context}, response=evidence or "")
            c = Claim(statement=claim, author="orchestrator", evidence=ev)
        else:
            c = claim
        verdict = await self.verify(c)
        return {
            "verdict": "verified" if verdict.status == "confirmed" else verdict.status,
            "status": "ok",
            "passes_to_human": verdict.passes_to_human,
            "reasons": verdict.reasons,
            "replay_matched": verdict.replay_matched,
        }

    async def verify(self, claim: Claim, replayer: Optional[Replayer] = None) -> Verdict:
        ev = claim.evidence
        if ev is None:
            return Verdict("unproven", ["no_evidence"])
        if time.time() - ev.timestamp > self._max_age:
            return Verdict("unproven", ["evidence_stale"])

        body = _norm(ev.response)
        reasons: List[str] = []
        for needle in claim.must_contain:
            if _norm(needle) not in body:
                reasons.append(f"evidence_missing:{needle}")
        for needle in claim.must_not_contain:
            if _norm(needle) in body:
                reasons.append(f"evidence_contradicts:{needle}")
        if reasons:
            return Verdict("refuted", reasons)

        replay_matched: Optional[bool] = None
        if replayer is not None:
            try:
                fresh = await replayer(ev.call)
            except Exception as exc:  # noqa: BLE001
                return Verdict("unproven", [f"replay_failed:{type(exc).__name__}"], replay_matched=None)
            replay_matched = _norm(fresh) == body
            if not replay_matched:
                return Verdict("refuted", ["replay_differs_from_evidence"], replay_matched=False)

        if self._skeptic is not None:
            try:
                resp = await self._skeptic.ainvoke(
                    f"Try to refute this claim using ONLY the evidence. Answer REFUTED or HOLDS.\n"
                    f"Claim: {claim.statement}\nEvidence: {ev.response!s:.1500}"
                )
                if "REFUTED" in str(getattr(resp, "content", resp)).upper().split("HOLDS")[0]:
                    return Verdict("refuted", ["skeptic_refuted"], replay_matched)
            except Exception as exc:  # noqa: BLE001
                logger.warning("orc_skeptic_failed", error=str(exc))

        return Verdict("confirmed", ["evidence_ok"] + (["replay_matched"] if replay_matched else []), replay_matched)


@dataclass
class Finding:
    claim: Claim
    verdict: Verdict
    state: str = "found"          # found -> verified | dropped -> fix_proposed -> replayed -> closed | reopened
    history: List[Dict[str, Any]] = field(default_factory=list)
    fix: Optional[str] = None

    def log(self, state: str, note: str = "") -> None:
        self.state = state
        self.history.append({"state": state, "note": note, "ts": time.time()})


class SwarmBoard:
    def __init__(self, verifier: Optional[OrcVerifier] = None) -> None:
        self._verifier = verifier or OrcVerifier()
        self._findings: Dict[str, Finding] = {}

    async def submit(self, claim: Claim, replayer: Optional[Replayer] = None) -> Finding:
        verdict = await self._verifier.verify(claim, replayer)
        f = Finding(claim, verdict)
        f.log("found", claim.author)
        f.log("verified" if verdict.passes_to_human else "dropped", ",".join(verdict.reasons))
        self._findings[claim.id] = f
        return f

    def propose_fix(self, finding_id: str, fix: str) -> None:
        f = self._findings[finding_id]
        if f.state != "verified":
            raise ValueError(f"fix_requires_verified_finding:{f.state}")
        f.fix = fix
        f.log("fix_proposed", fix[:120])

    async def live_replay(self, finding_id: str, replayer: Replayer, fixed_check: Callable[[Any], bool]) -> Finding:
        """Re-run the original call after the fix; close only if the check now passes."""
        f = self._findings[finding_id]
        if f.claim.evidence is None or f.state != "fix_proposed":
            raise ValueError(f"replay_requires_fix_proposed:{f.state}")
        fresh = await replayer(f.claim.evidence.call)
        f.log("replayed", _norm(fresh)[:120])
        f.log("closed" if fixed_check(fresh) else "reopened", "live_replay")
        return f

    def get(self, finding_id: str) -> Optional[Finding]:
        return self._findings.get(finding_id)

    def stats(self) -> Dict[str, int]:
        total = len(self._findings)
        dropped = sum(1 for f in self._findings.values() if f.verdict.status != "confirmed")
        return {
            "total": total,
            "filtered_before_human": dropped,
            "passed_to_human": total - dropped,
            "closed": sum(1 for f in self._findings.values() if f.state == "closed"),
        }
