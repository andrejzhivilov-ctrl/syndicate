"""Per-agent tier routing: coverage, zero-token classification, failover."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from src.llm_router import AGENT_PROFILES, BASE, HEAVY, TieredLLM, classify_complexity
from src.model_registry import DEFAULTS, model_for
from src.vault_paths import DIRECTOR_IDS


class FakeChat:
    def __init__(self, name, fail=False):
        self.name, self.fail, self.calls = name, fail, 0

    async def ainvoke(self, messages, *args, **kwargs):
        self.calls += 1
        if self.fail:
            raise RuntimeError(f"{self.name} down")
        return SimpleNamespace(content=self.name)


def _factory(clients):
    return lambda transport, model_id: clients.get((transport, model_id))


PROFILE = {"agent": {BASE: (("openrouter", "OR_CLAUDE_HAIKU"),),
                     HEAVY: (("openrouter", "OR_CLAUDE_SONNET"), ("anthropic", "ANTHROPIC_PRIMARY"))}}


def test_every_director_has_a_profile_with_registered_models():
    assert set(DIRECTOR_IDS) <= set(AGENT_PROFILES)
    for agent, tiers in AGENT_PROFILES.items():
        assert set(tiers) == {BASE, HEAVY}, agent
        for tier, candidates in tiers.items():
            assert candidates, (agent, tier)
            for transport, key in candidates:
                assert transport in {"openrouter", "gemini", "anthropic"}, (agent, transport)
                assert key in DEFAULTS, (agent, key)


def test_routine_prompt_stays_on_base():
    assert classify_complexity([("system", "x"), ("human", "Привіт, що на сьогодні?")]).tier == BASE


def test_long_or_analytical_prompt_escalates():
    assert classify_complexity([("human", "a" * 7000)]).tier == HEAVY
    assert classify_complexity([("human", "Зроби аналіз ризиків і фінансовий прогноз")]).tier == HEAVY


def test_system_prompt_does_not_count_towards_complexity():
    system = "You are a strategy, security, finance and architecture analyst. " * 200
    assert classify_complexity([("system", system), ("human", "Дякую!")]).tier == BASE


def test_explicit_hint_wins_and_unknown_hint_is_an_error():
    assert classify_complexity([("human", "a" * 9000)], hint=BASE).tier == BASE
    with pytest.raises(ValueError, match="unknown_complexity_hint"):
        classify_complexity("hi", hint="medium")


def test_routes_to_the_tier_model_and_records_it():
    haiku, sonnet = FakeChat("haiku"), FakeChat("sonnet")
    llm = TieredLLM("agent", _factory({("openrouter", model_for("OR_CLAUDE_HAIKU")): haiku,
                                       ("openrouter", model_for("OR_CLAUDE_SONNET")): sonnet}), profiles=PROFILE)
    assert asyncio.run(llm.ainvoke([("human", "hi")])).content == "haiku"
    assert llm.last_route["tier"] == BASE and llm.last_route["model"] == model_for("OR_CLAUDE_HAIKU")
    assert asyncio.run(llm.ainvoke([("human", "hi")], complexity=HEAVY)).content == "sonnet"


def test_provider_failure_cascades_inside_the_tier_then_across_tiers():
    sonnet_or = FakeChat("sonnet-or", fail=True)
    sonnet_direct = FakeChat("sonnet-direct")
    llm = TieredLLM("agent", _factory({("openrouter", model_for("OR_CLAUDE_SONNET")): sonnet_or,
                                       ("anthropic", model_for("ANTHROPIC_PRIMARY")): sonnet_direct}), profiles=PROFILE)
    assert asyncio.run(llm.ainvoke("x", complexity=HEAVY)).content == "sonnet-direct"
    assert llm.last_route["attempts"] == 2
    # Base has no configured client here: it escalates to heavy instead of failing.
    assert asyncio.run(llm.ainvoke("x", complexity=BASE)).content == "sonnet-direct"


def test_fallback_then_real_error_never_a_made_up_answer():
    down = FakeChat("down", fail=True)
    llm = TieredLLM("agent", _factory({("openrouter", model_for("OR_CLAUDE_HAIKU")): down}),
                    profiles=PROFILE, fallback=FakeChat("primary"))
    assert asyncio.run(llm.ainvoke("x")).content == "primary"
    llm = TieredLLM("agent", _factory({("openrouter", model_for("OR_CLAUDE_HAIKU")): down}), profiles=PROFILE)
    with pytest.raises(RuntimeError, match="down"):
        asyncio.run(llm.ainvoke("x"))
    empty = TieredLLM("agent", _factory({}), profiles=PROFILE)
    assert not empty.is_configured
    with pytest.raises(RuntimeError, match="llm_unavailable"):
        asyncio.run(empty.ainvoke("x"))


def test_unknown_agent_has_no_silent_default_profile():
    with pytest.raises(ValueError, match="no_llm_profile"):
        TieredLLM("nobody", _factory({}))


def test_orchestrator_hands_each_agent_its_own_router():
    from src.orchestrator import EvaOrchestrator

    orch = EvaOrchestrator.__new__(EvaOrchestrator)
    orch._llm = FakeChat("primary")
    orch._provider_keys = {}
    assert orch._llm_for("eva") is orch._llm  # no keys: unchanged behaviour
    orch._provider_keys = {"openrouter": "k"}
    eva, fin = orch._llm_for("eva"), orch._llm_for("fin")
    assert isinstance(eva, TieredLLM) and eva.agent_id == "eva" and fin.agent_id == "fin"
    assert orch._llm_for("eva") is eva


def test_a_client_that_cannot_be_built_fails_over_instead_of_crashing():
    def factory(transport, model_id):
        if transport == "openrouter":
            raise ImportError("langchain provider missing")
        return FakeChat("direct")

    llm = TieredLLM("agent", factory, profiles=PROFILE)
    assert asyncio.run(llm.ainvoke("x", complexity=HEAVY)).content == "direct"


def test_architect_keeps_the_reasoning_model_as_its_last_resort():
    from src.orchestrator import EvaOrchestrator

    orch = EvaOrchestrator.__new__(EvaOrchestrator)
    orch._llm, reasoning = FakeChat("primary"), FakeChat("reasoning")
    orch._provider_keys = {}
    assert orch._llm_for("architect", default=reasoning) is reasoning
    orch._provider_keys = {"openrouter": "k"}
    assert orch._llm_for("architect", default=reasoning)._fallback is reasoning


def test_curator_reports_unavailable_when_the_model_did_not_answer():
    # Fallback text used to be returned with status "completed" (Zero-Faking).
    from src.agents.eva_curator import EvaCurator

    curator = EvaCurator(memory=None, llm=FakeChat("down", fail=True), config={})
    result = asyncio.run(curator.execute({"action": "weekly_review", "review_materials": ["note"]}))
    assert result["status"] == "unavailable"
    curator = EvaCurator(memory=None, llm=FakeChat("real review"), config={})
    result = asyncio.run(curator.execute({"action": "weekly_review", "review_materials": ["note"]}))
    assert result["status"] == "completed" and result["reflection"] == "real review"
