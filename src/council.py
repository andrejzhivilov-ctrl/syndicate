"""
LLM Council — critical decisions are never trusted to a single model.

The question goes to several providers in parallel. Consensus is computed
deterministically (majority over explicit options, or answer-similarity
medoid) so the verdict stays auditable; an optional arbiter LLM only writes the
final synthesis. Weak agreement or a missing quorum forces human review.
"""

from __future__ import annotations

from src.model_registry import model_for
import asyncio
import os
import re
from dataclasses import dataclass, field
from itertools import combinations
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)

_WORD = re.compile(r"\w+", re.UNICODE)


@dataclass
class ModelVote:
    model: str
    answer: str = ""
    option: Optional[str] = None
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None and bool(self.answer.strip())


@dataclass
class CouncilVerdict:
    decision: str
    agreement: float
    quorum_met: bool
    requires_hitl: bool
    votes: List[ModelVote] = field(default_factory=list)
    dissent: List[str] = field(default_factory=list)
    synthesis: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "chosen": self.decision,
            "agreement": round(self.agreement, 3),
            "consensus_score": round(self.agreement, 3),
            "quorum": self.quorum_met,
            "quorum_met": self.quorum_met,
            "requires_hitl": self.requires_hitl,
            "dissent": self.dissent,
            "synthesis": self.synthesis,
            "votes": [{"model": v.model, "option": v.option, "error": v.error, "answer": v.answer[:400]} for v in self.votes],
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    def __contains__(self, key: str) -> bool:
        return key in self.to_dict()

    def get(self, key: str, default: Any = None) -> Any:
        return self.to_dict().get(key, default)

    def keys(self):
        return self.to_dict().keys()

    def values(self):
        return self.to_dict().values()

    def items(self):
        return self.to_dict().items()


def _tokens(text: str) -> set:
    return {w.lower() for w in _WORD.findall(text) if len(w) > 2}


def _jaccard(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb:
        return 1.0
    return len(ta & tb) / max(1, len(ta | tb))


def _extract_option(answer: str, options: List[str]) -> Optional[str]:
    low = answer.lower()
    first = [o for o in options if re.search(rf"\b{re.escape(o.lower())}\b", low)]
    if len(first) == 1:
        return first[0]
    # several options mentioned: take the one mentioned earliest
    positions = [(low.find(o.lower()), o) for o in first if low.find(o.lower()) >= 0]
    return min(positions)[1] if positions else None


class LLMCouncil:
    def __init__(
        self,
        members: Optional[Dict[str, Any]] = None,
        arbiter: Optional[Any] = None,
        min_quorum: int = 2,
        agreement_threshold: float = 0.6,
        default_threshold: Optional[float] = None,
        timeout_s: float = 30.0,
        llm: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        if members is not None:
            self._members = dict(members)
        elif llm is not None:
            self._members = {"member_1": llm, "member_2": llm}
        else:
            self._members = {}
        self._arbiter = arbiter
        self._quorum = min_quorum
        self._threshold = default_threshold if default_threshold is not None else agreement_threshold
        self._timeout = timeout_s

    @staticmethod
    def _text(resp: Any) -> str:
        return str(getattr(resp, "content", resp))

    async def _ask(self, name: str, llm: Any, prompt: str) -> ModelVote:
        try:
            resp = await asyncio.wait_for(llm.ainvoke(prompt), timeout=self._timeout)
            return ModelVote(name, answer=self._text(resp))
        except asyncio.TimeoutError:
            return ModelVote(name, error="timeout")
        except Exception as exc:  # noqa: BLE001
            return ModelVote(name, error=f"{type(exc).__name__}: {exc}")

    def _tally_options(self, good: List[ModelVote], options: List[str]) -> tuple:
        """Majority vote over explicit options."""
        for v in good:
            v.option = _extract_option(v.answer, options)
        tally: Dict[str, int] = {}
        for v in good:
            if v.option:
                tally[v.option] = tally.get(v.option, 0) + 1
        if not tally:
            return "no_consensus", 0.0, [v.model for v in good]
        decision, top = max(tally.items(), key=lambda kv: kv[1])
        return decision, top / len(good), [v.model for v in good if v.option != decision]

    def _decide_by_similarity(self, good: List[ModelVote]) -> tuple:
        """No explicit options — pick the medoid answer and measure agreement."""
        if len(good) == 1:
            return good[0].answer, 1.0, []
        sims = {v.model: 0.0 for v in good}
        pair_scores = []
        for a, b in combinations(good, 2):
            s = _jaccard(a.answer, b.answer)
            sims[a.model] += s
            sims[b.model] += s
            pair_scores.append(s)
        medoid = max(good, key=lambda v: sims[v.model])
        agreement = sum(pair_scores) / len(pair_scores)
        dissent = [
            v.model for v in good
            if _jaccard(v.answer, medoid.answer) < self._threshold / 2
        ]
        return medoid.answer, agreement, dissent

    async def _synthesize(self, question: str, good: List[ModelVote]) -> str:
        """Optional arbiter pass — never fatal, always returns a string."""
        if self._arbiter is None or not good:
            return ""
        joined = "\n\n".join(f"[{v.model}] {v.answer[:800]}" for v in good)
        try:
            resp = await asyncio.wait_for(
                self._arbiter.ainvoke(
                    f"Question: {question}\n\nModel answers:\n{joined}\n\n"
                    "Synthesize the consensus; explicitly flag disagreements and uncertain claims."
                ),
                timeout=self._timeout,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("council_arbiter_failed", error=str(exc))
            return ""
        return self._text(resp)

    async def deliberate(
        self,
        question: str,
        context: Optional[str] = "",
        options: Optional[List[str]] = None,
    ) -> CouncilVerdict:
        ctx = context or ""
        prompt = question if not ctx else f"{ctx}\n\n{question}"
        if options:
            prompt += f"\n\nAnswer with exactly one of: {', '.join(options)}, then justify briefly."
        votes = await asyncio.gather(*[self._ask(n, m, prompt) for n, m in self._members.items()])
        good = [v for v in votes if v.ok]
        quorum_met = len(good) >= self._quorum

        if options:
            decision, agreement, dissent = self._tally_options(good, options)
        elif good:
            decision, agreement, dissent = self._decide_by_similarity(good)
        else:
            decision, agreement, dissent = "no_consensus", 0.0, []

        synthesis = await self._synthesize(question, good)

        requires_hitl = (not quorum_met) or agreement < self._threshold or decision == "no_consensus"
        logger.info("council_verdict", decision=decision[:60], agreement=round(agreement, 3), quorum=quorum_met)
        return CouncilVerdict(decision, agreement, quorum_met, requires_hitl, list(votes), dissent, synthesis)


def build_council_members(llm_config: Dict[str, Any]) -> Dict[str, Any]:
    """Provider-agnostic member construction. Missing keys simply skip a provider.

    ``DEFAULT_LLM_PROVIDER`` (env) only influences ordering, never availability.
    """
    members: Dict[str, Any] = {}
    anthropic_key = llm_config.get("anthropic_api_key") or ""
    openai_key = llm_config.get("openai_api_key") or ""
    google_key = llm_config.get("google_api_key") or ""
    placeholder = "PLACEHOLDER_UPDATE_ME"
    try:
        if anthropic_key and anthropic_key != placeholder:
            from langchain_anthropic import ChatAnthropic
            members["anthropic"] = ChatAnthropic(api_key=anthropic_key, model=llm_config.get("anthropic_model") or model_for("ANTHROPIC_PRIMARY"), temperature=0)
        if openai_key and openai_key != placeholder:
            from langchain_openai import ChatOpenAI
            members["openai"] = ChatOpenAI(api_key=openai_key, model=llm_config.get("openai_model", "gpt-4o"), temperature=0)
        if google_key and google_key != placeholder:
            from langchain_google_genai import ChatGoogleGenerativeAI
            members["google"] = ChatGoogleGenerativeAI(google_api_key=google_key, model=llm_config.get("google_model") or model_for("COUNCIL_GOOGLE"), temperature=0)
    except Exception as exc:  # noqa: BLE001
        logger.warning("council_member_init_failed", error=str(exc))
    preferred = os.getenv("DEFAULT_LLM_PROVIDER", "")
    if preferred in members:
        members = {preferred: members[preferred], **{k: v for k, v in members.items() if k != preferred}}
    return members
