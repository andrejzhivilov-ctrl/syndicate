"""Operator regulations for Eva, Fin, Sam and Jack (29.10): loaded, cheap, honest."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from src.agent_chat import chat_reply, pool_command, pool_reply
from src.agent_specs import SPEC_DIR, load_spec, spec_core, spec_reference, spec_reply

AGENTS = ("eva", "fin", "sam", "jack")


@pytest.mark.parametrize("agent", AGENTS)
def test_every_spec_is_complete_and_consistent(agent):
    spec = load_spec(agent)
    assert spec and spec["agent"] == agent and spec["source"]
    assert len(spec["core"]) <= 1300, "core goes into every chat turn: keep it short"
    ids = [s["id"] for s in spec["sections"]]
    assert len(ids) == len(set(ids)) and all(s["keywords"] and s["text"] for s in spec["sections"])
    assert {i["status"] for i in spec["integrations"]} <= {"connected", "not_connected"}
    for job in spec["schedule"]:
        assert len(job["cron"].split()) == 5 and job["name"].startswith(agent)


def test_malformed_spec_is_rejected_not_crashing(monkeypatch, tmp_path):
    import src.agent_specs as specs

    (tmp_path / "eva.json").write_text('{"agent": "eva"}', encoding="utf-8")
    monkeypatch.setattr(specs, "SPEC_DIR", tmp_path)
    specs.load_spec.cache_clear()
    try:
        assert specs.load_spec("eva") is None and specs.spec_core("eva") is None
        assert specs.spec_reply("eva", "")["status"] == "unavailable"
    finally:
        specs.load_spec.cache_clear()


def test_unknown_or_unsafe_agent_ids_have_no_spec():
    assert load_spec("kira") is None and load_spec("../eva") is None and spec_core("nobody") is None


def test_core_lists_what_is_not_connected_so_agents_do_not_claim_it():
    core = spec_core("sam")
    assert "Interactive Brokers" in core and "не стверджуй" in core
    assert "Telegram-бот Сема" not in core  # connected things are not listed as missing


def test_reference_adds_only_matching_sections_and_stays_bounded():
    assert spec_reference("fin", "Привіт, як справи?") is None
    ref = spec_reference("fin", "Коли нагадування про платежі і який дедлайн?")
    assert ref and "10:00" in ref and len(ref) <= 1500
    assert "Календар нагадувань" in spec_reference("fin", "нагадування")


def test_spec_command_lists_sections_schedule_and_integrations_without_a_model():
    assert pool_command({"text": "/spec розклад"}) == ("/spec", "розклад")
    listing = pool_reply("jack", "/spec", "", library=None)["response"]
    assert "markets" in listing and "розклад" in listing
    schedule = spec_reply("fin", "розклад")["response"]
    assert "0 10 * * *" in schedule and "ще не ввімкнено" in schedule
    assert "⛔" in spec_reply("eva", "інтеграції")["response"]
    assert "23:59" in spec_reply("fin", "reminders")["response"]
    assert spec_reply("kira", "")["status"] == "unavailable"


class _LLM:
    def __init__(self):
        self.calls = []

    async def ainvoke(self, messages):
        self.calls.append(messages)
        return "Ок."


def test_director_chat_carries_core_and_the_matching_section():
    llm = _LLM()
    asyncio.run(chat_reply("sam", "Який у тебе графік звітів по сесіях?", llm))
    system = "\n".join(text for role, text in llm.calls[0] if role == "system")
    assert "Регламент Сема" in system and "09:45" in system and "Довідка з твого регламенту" in system
    asyncio.run(chat_reply("kira", "Привіт", llm))
    assert not any("Регламент" in text for role, text in llm.calls[1] if role == "system")


def test_eva_prompt_includes_her_regulation():
    from src.agents.eva import EVA_SYSTEM_PROMPT

    assert "Регламент Єви" in EVA_SYSTEM_PROMPT and "21:30" in EVA_SYSTEM_PROMPT


def test_unknown_values_in_templates_are_null_not_zero():
    text = json.dumps([load_spec(a) for a in AGENTS], ensure_ascii=False)
    assert "0.0" not in text.replace("null, не 0.0", "") and text.count("null, не") >= 2


def test_image_ships_the_specs():
    dockerfile = (Path(__file__).resolve().parents[1] / "deploy/docker/Dockerfile.agent").read_text(encoding="utf-8")
    assert "COPY config/agent_specs /app/config/agent_specs" in dockerfile
    assert sorted(p.stem for p in SPEC_DIR.glob("*.json")) == sorted(AGENTS)
