"""Per-agent LLM routing by task complexity (manifest §3.3 tier routing).

Every in-process director gets two tiers:

* ``base``  — cheap/fast model for routine work (chat, tags, short summaries);
* ``heavy`` — escalation model for long or analytical work (architecture, code,
  finance, legal, strategy, deep research).

The tier is chosen **without an LLM call** (zero-token): an explicit
``complexity=`` hint wins, otherwise a deterministic heuristic over the prompt.
Each tier is an ordered list of candidates; on a provider error (429/5xx,
timeout, auth) the next candidate is tried, then the other tier, then the
holding-wide fallback. Nothing is invented on failure: the last error is raised
so the caller reports ``unavailable`` as before.

Model IDs live in ``src/model_registry.py`` only; this module references
registry keys, so ``python -m tools.check_models`` verifies every ID used here.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import structlog

from src.model_registry import model_for

logger = structlog.get_logger(__name__)

BASE = "base"
HEAVY = "heavy"
TIERS = (BASE, HEAVY)

#: (transport, registry key). Transports: ``openrouter`` (one key, every model),
#: ``gemini`` (direct Google AI Studio), ``anthropic`` (direct Anthropic API).
Candidate = Tuple[str, str]

_CLAUDE_HAIKU: Sequence[Candidate] = (("openrouter", "OR_CLAUDE_HAIKU"), ("anthropic", "ANTHROPIC_DIRECTOR"))
_CLAUDE_SONNET: Sequence[Candidate] = (("openrouter", "OR_CLAUDE_SONNET"), ("anthropic", "ANTHROPIC_PRIMARY"))
_DEEPSEEK_FLASH: Sequence[Candidate] = (("openrouter", "OR_DEEPSEEK_FLASH"),)
# OpenRouter first: on 27.10 the direct Gemini key answered 503/timeout for
# gemini-3.8-flash, while OpenRouter served it; direct 3.5-flash is the backup.
_GEMINI_FLASH: Sequence[Candidate] = (("openrouter", "OR_GEMINI_FLASH"), ("gemini", "GEMINI_FLASH_LATEST"))
_GEMINI_ARGON: Sequence[Candidate] = (("openrouter", "OR_GEMINI_ARGON"),)

#: agent_id -> {tier: candidates in order}. Covers all 18 directors plus the
#: office copilot; tests assert the coverage.
AGENT_PROFILES: Dict[str, Dict[str, Sequence[Candidate]]] = {
    # Core wing
    "eva": {BASE: _CLAUDE_HAIKU, HEAVY: _CLAUDE_SONNET},
    "alice": {BASE: _CLAUDE_SONNET, HEAVY: _CLAUDE_SONNET},  # day-to-day runs on Antigravity, not this API
    "architect": {BASE: _DEEPSEEK_FLASH, HEAVY: (("openrouter", "OR_QWEN_MAX"),) + tuple(_CLAUDE_SONNET)},
    "kodex": {BASE: _CLAUDE_HAIKU, HEAVY: tuple(_GEMINI_ARGON) + tuple(_CLAUDE_SONNET)},
    "marshal": {BASE: (("openrouter", "OR_GPT_LUNA"),), HEAVY: (("openrouter", "OR_GPT_SOL"),) + tuple(_CLAUDE_SONNET)},
    # Intelligence & finance wing
    "sonar": {BASE: _GEMINI_FLASH, HEAVY: (("openrouter", "OR_SONAR_DEEP_RESEARCH"),)},
    "fin": {BASE: _DEEPSEEK_FLASH, HEAVY: _GEMINI_ARGON},
    "sam": {BASE: _DEEPSEEK_FLASH, HEAVY: (("openrouter", "OR_DEEPSEEK_PRO"),)},
    "jack": {BASE: _DEEPSEEK_FLASH, HEAVY: _CLAUDE_HAIKU},
    "scout": {BASE: _GEMINI_FLASH, HEAVY: (("openrouter", "OR_GROK"),)},
    # Commerce & media wing
    "oscar": {BASE: _CLAUDE_HAIKU, HEAVY: _CLAUDE_SONNET},
    "tyler": {BASE: _CLAUDE_HAIKU, HEAVY: _CLAUDE_SONNET},
    "ray": {BASE: _DEEPSEEK_FLASH, HEAVY: _CLAUDE_SONNET},
    "dex": {BASE: _DEEPSEEK_FLASH, HEAVY: _CLAUDE_SONNET},
    # LifeOps & academy wing
    "doc": {BASE: _CLAUDE_HAIKU, HEAVY: _CLAUDE_SONNET},
    "trainer": {BASE: _CLAUDE_HAIKU, HEAVY: _CLAUDE_SONNET},
    "kira": {BASE: _CLAUDE_HAIKU, HEAVY: _CLAUDE_SONNET},
    "atlas": {BASE: _GEMINI_FLASH, HEAVY: (("openrouter", "OR_SONAR_PRO"),)},
    # Not a director, but shares Eva's desk.
    "office_copilot": {BASE: _CLAUDE_HAIKU, HEAVY: _CLAUDE_SONNET},
}

# ─── Complexity classification (zero-token) ─────────────────────────────────

#: A prompt this long is heavy regardless of wording.
HEAVY_LENGTH = 6000
#: A prompt this long is heavy if it also names one heavy signal.
MEDIUM_LENGTH = 1500

_HEAVY_SIGNALS = re.compile(
    r"архітект|architect|стратег|strateg|аналіз|analy[sz]|дослідж|research|"
    r"рефактор|refactor|код\b|code|debug|налагод|юрид|legal|договір|contract|"
    r"фінанс|financ|p&l|бюджет|budget|ризик|risk|безпек|security|аудит|audit|"
    r"порівн|compar|прогноз|forecast|план|plan|звіт|report|модел|model|"
    r"обґрунт|justif|доказ|proof|розрахун|calculat",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class TierDecision:
    tier: str
    reason: str


def _message_text(messages: Any) -> str:
    """The task text of LangChain-style messages, *without* system prompts.

    Agents' system prompts are long and full of words like "strategy" or
    "analysis"; counting them would send every call to the heavy tier.
    """
    if isinstance(messages, str):
        return messages
    parts: List[str] = []
    for item in messages or []:
        if isinstance(item, (tuple, list)) and len(item) == 2:
            role, content = item
        else:
            role, content = getattr(item, "type", ""), getattr(item, "content", item)
        if str(role).lower() != "system":
            parts.append(str(content))
    return "\n".join(parts)


def classify_complexity(messages: Any, hint: Optional[str] = None) -> TierDecision:
    """Pick a tier without calling a model. An explicit valid hint always wins."""
    if hint is not None:
        if hint not in TIERS:
            raise ValueError(f"unknown_complexity_hint: {hint!r} (expected one of {TIERS})")
        return TierDecision(hint, "explicit_hint")
    text = _message_text(messages)
    signals = len(set(m.group(0).lower() for m in _HEAVY_SIGNALS.finditer(text)))
    if len(text) >= HEAVY_LENGTH:
        return TierDecision(HEAVY, "long_prompt")
    if signals >= 2:
        return TierDecision(HEAVY, "analytical_signals")
    if signals >= 1 and len(text) >= MEDIUM_LENGTH:
        return TierDecision(HEAVY, "medium_prompt_with_signal")
    return TierDecision(BASE, "routine")


# ─── Routed client ──────────────────────────────────────────────────────────

#: Builds a LangChain chat model for (transport, model_id); returns None when
#: that transport has no key, so the candidate is skipped instead of faked.
ClientFactory = Callable[[str, str], Optional[Any]]


class TieredLLM:
    """Drop-in replacement for a chat model: agents only call ``ainvoke``."""

    def __init__(
        self,
        agent_id: str,
        factory: ClientFactory,
        *,
        fallback: Optional[Any] = None,
        profiles: Optional[Dict[str, Dict[str, Sequence[Candidate]]]] = None,
    ) -> None:
        table = profiles if profiles is not None else AGENT_PROFILES
        if agent_id not in table:
            raise ValueError(f"no_llm_profile: {agent_id}")
        self.agent_id = agent_id
        self._profile = table[agent_id]
        self._factory = factory
        self._fallback = fallback
        self._clients: Dict[Tuple[str, str], Optional[Any]] = {}
        self.last_route: Optional[Dict[str, Any]] = None

    def _client(self, transport: str, key: str) -> Optional[Any]:
        model_id = model_for(key)
        cache_key = (transport, model_id)
        if cache_key not in self._clients:
            self._clients[cache_key] = self._factory(transport, model_id)
        return self._clients[cache_key]

    def candidates(self, tier: str) -> Iterable[Tuple[str, str]]:
        """Chosen tier first, then the other tier — escalation and de-escalation."""
        other = HEAVY if tier == BASE else BASE
        seen = set()
        for transport, key in list(self._profile[tier]) + list(self._profile[other]):
            if (transport, key) not in seen:
                seen.add((transport, key))
                yield transport, key

    @property
    def is_configured(self) -> bool:
        return any(self._client(t, k) is not None for tier in TIERS for t, k in self._profile[tier]) or (
            self._fallback is not None
        )

    async def ainvoke(self, messages: Any, *args: Any, complexity: Optional[str] = None, **kwargs: Any) -> Any:
        decision = classify_complexity(messages, complexity)
        last_exc: Optional[BaseException] = None
        attempts = 0
        for transport, key in self.candidates(decision.tier):
            try:
                client = self._client(transport, key)
            except Exception as exc:  # noqa: BLE001 - a client that cannot be built is a failover trigger
                last_exc = exc
                logger.warning("llm_route_candidate_unavailable", agent=self.agent_id, tier=decision.tier,
                               transport=transport, error=type(exc).__name__)
                continue
            if client is None:
                continue
            attempts += 1
            try:
                result = await client.ainvoke(messages, *args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - provider errors are failover triggers
                last_exc = exc
                logger.warning("llm_route_candidate_failed", agent=self.agent_id, tier=decision.tier,
                               transport=transport, model=model_for(key), error=type(exc).__name__)
                continue
            self._record(decision, transport, model_for(key), attempts)
            return result
        if self._fallback is not None:
            result = await self._fallback.ainvoke(messages, *args, **kwargs)
            self._record(decision, "fallback", getattr(self._fallback, "model_name", None)
                         or getattr(self._fallback, "model", "unknown"), attempts + 1)
            return result
        if last_exc is not None:
            raise last_exc
        raise RuntimeError(f"llm_unavailable: no configured model for agent {self.agent_id}")

    def _record(self, decision: TierDecision, transport: str, model: str, attempts: int) -> None:
        self.last_route = {"agent": self.agent_id, "tier": decision.tier, "reason": decision.reason,
                           "transport": transport, "model": model, "attempts": attempts}
        logger.info("llm_routed", **self.last_route)
