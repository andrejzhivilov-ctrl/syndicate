"""Telegram conversation mode for every director."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace

from src.agent_chat import PERSONAS, SECRET_REFUSAL, chat_reply, chat_text, system_prompt
from src.vault_paths import DIRECTOR_IDS

OWNER = "523"


class FakeLLM:
    def __init__(self, reply="Привіт, Андрію!", fail=False):
        self.reply, self.fail, self.calls = reply, fail, []

    async def ainvoke(self, messages, *args, **kwargs):
        self.calls.append(messages)
        if self.fail:
            raise RuntimeError("provider down")
        return SimpleNamespace(content=self.reply)


def _orch(llm):
    from src.orchestrator import EvaOrchestrator

    orch = EvaOrchestrator.__new__(EvaOrchestrator)

    async def owner():
        return OWNER

    async def must_not_route(**kwargs):
        raise AssertionError(f"chat text must not reach task routing: {kwargs.get('task_type')}")

    orch._telegram_owner_id = owner
    orch._llm_for = lambda agent_id, default=None: llm
    orch.execute = must_not_route
    return orch


def _payload(text, chat=OWNER):
    return {"text": text, "chat_id": chat, "message": {"chat": {"id": chat}, "text": text}}


def test_every_director_has_a_ukrainian_persona_with_the_no_action_rule():
    assert set(DIRECTOR_IDS) <= set(PERSONAS)
    for agent_id in DIRECTOR_IDS:
        prompt = system_prompt(agent_id)
        assert PERSONAS[agent_id][0] in prompt
        assert "українською" in prompt and "не вигадуй" in prompt.lower()
        assert "нічого не публікуєш" in prompt


def test_commands_keep_their_handlers_but_start_and_text_are_chat():
    assert chat_text({"text": "/status"}) is None
    assert chat_text({"text": "/start"}) == "/start"
    assert chat_text({"text": "  Привіт  "}) == "Привіт"
    assert chat_text({"text": ""}) is None


def test_sam_chat_is_a_conversation_not_a_trade_or_hitl_item():
    llm = FakeLLM("Привіт! Я Сем.")
    out = asyncio.run(_orch(llm).handle_webhook(source="telegram_sam", payload=_payload("Привіт")))
    assert out["result"] == {"agent": "sam", "status": "completed", "mode": "chat", "response": "Привіт! Я Сем."}
    system, human = llm.calls[0]
    assert system[0] == "system" and "Сем" in system[1]
    assert human == ("human", "Привіт")


def test_prepared_director_can_talk_without_gaining_actions():
    out = asyncio.run(_orch(FakeLLM("Я Оскар.")).handle_webhook(source="telegram_oscar", payload=_payload("Привіт")))
    assert out["result"]["status"] == "completed" and out["result"]["mode"] == "chat"


def test_non_owner_chat_is_denied_before_any_model_call():
    llm = FakeLLM()
    out = asyncio.run(_orch(llm).handle_webhook(source="telegram_fin", payload=_payload("Привіт", chat="999")))
    assert out["result"]["status"] == "denied" and llm.calls == []


def test_kira_crisis_screen_runs_before_the_model():
    llm = FakeLLM()
    out = asyncio.run(chat_reply("kira", "я не хочу жити", llm))
    assert out["crisis_support"] is True and "112" in out["response"] and llm.calls == []


def test_secret_like_text_never_reaches_the_model():
    llm = FakeLLM()
    out = asyncio.run(chat_reply("fin", "мій ключ sk-ant-api03-" + "x" * 40, llm))
    assert out["response"] == SECRET_REFUSAL and llm.calls == []


def test_model_failure_is_unavailable_not_an_invented_reply():
    out = asyncio.run(chat_reply("dex", "Привіт", FakeLLM(fail=True)))
    assert out == {"agent": "dex", "status": "unavailable", "mode": "chat", "reason": "llm_unavailable"}


def test_eva_and_commands_still_use_task_routing():
    from src.orchestrator import EvaOrchestrator

    orch = EvaOrchestrator.__new__(EvaOrchestrator)
    routed = []

    async def execute(**kwargs):
        routed.append(kwargs["task_type"])
        return {"status": "completed", "result": {}}

    orch.execute = execute
    asyncio.run(orch.handle_webhook(source="telegram_eva", payload=_payload("Привіт")))
    asyncio.run(orch.handle_webhook(source="telegram_doc", payload=_payload("/status")))
    assert routed == ["webhook_telegram_eva", "webhook_telegram_doc"]


def test_feminine_personas_are_told_their_grammatical_gender():
    assert "жіночому роді" in system_prompt("kira")
    assert "жіночому роді" in system_prompt("alice")
    assert "чоловічому роді" in system_prompt("oscar")
