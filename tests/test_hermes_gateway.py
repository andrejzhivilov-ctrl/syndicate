"""The door of Hermes containers: identity, masking, budget, tool rights, honest failure."""
import asyncio
import json

import httpx

from src import hermes_gateway as gateway


def _token(monkeypatch):
    monkeypatch.setattr(gateway, "_MASTER", {"key": "master-for-tests"})
    return gateway.agent_token("trainer")


def test_a_token_works_for_one_agent_only(monkeypatch):
    token = _token(monkeypatch)
    assert gateway.token_ok("trainer", f"Bearer {token}")
    assert not gateway.token_ok("trainer", "Bearer wrong")
    assert not gateway.token_ok("trainer", None)
    assert not gateway.token_ok("sam", f"Bearer {token}")  # not on Hermes yet
    monkeypatch.setattr(gateway, "_MASTER", {"key": None})
    assert not gateway.token_ok("trainer", f"Bearer {token}")  # no master, no entry


def test_enabled_agents_come_from_the_server_and_only_known_ones(monkeypatch):
    monkeypatch.delenv("EVA_HERMES_AGENTS", raising=False)
    assert gateway.enabled_agents() == []
    monkeypatch.setenv("EVA_HERMES_AGENTS", "trainer, sam")
    assert gateway.enabled_agents() == ["trainer"]


def test_everything_heading_for_a_provider_is_masked_and_uses_a_registry_model():
    body = {"model": "anything-the-container-says", "messages": [
        {"role": "system", "content": "Пошта test@example.com"},
        {"role": "tool", "content": "результат: test@example.com"},
        {"role": "user", "content": [{"type": "text", "text": "пиши на test@example.com"}]},
    ]}
    out = gateway.provider_body("trainer", gateway.CHAT, body)
    assert "test@example.com" not in json.dumps(out, ensure_ascii=False)
    assert out["model"] != "anything-the-container-says" and "haiku" in out["model"]
    assert "deepseek" in gateway.provider_body("trainer", gateway.LEARNING, body)["model"]
    assert out["usage"] == {"include": True}


def test_learning_stops_at_the_monthly_budget(tmp_path):
    budget = gateway.LearningBudget(tmp_path / "spend.json", limit=1.0)
    assert budget.allowed() and budget.spent() == 0.0
    budget.add(0.6)
    budget.add(0.5)
    assert round(budget.spent(), 2) == 1.1 and not budget.allowed()


def test_relay_keeps_the_key_counts_learning_and_returns_the_stream(tmp_path):
    seen = {}

    def provider(request):
        seen["key"] = request.headers["authorization"]
        data = b'data: {"choices":[]}\n\ndata: {"usage":{"cost":0.25}}\n\ndata: [DONE]\n\n'
        return httpx.Response(200, content=data)

    budget = gateway.LearningBudget(tmp_path / "spend.json", limit=10.0)

    async def scenario():
        status, chunks = await gateway.relay("trainer", gateway.LEARNING, {"messages": []}, "real-key", budget,
                                             transport=httpx.MockTransport(provider))
        return status, b"".join([chunk async for chunk in chunks])

    status, data = asyncio.run(scenario())
    assert status == 200 and b"[DONE]" in data
    assert seen["key"] == "Bearer real-key" and "real-key" not in data.decode()
    assert budget.spent() == 0.25


class _Orchestrator:
    def __init__(self):
        self.calls = []

    async def execute(self, action, payload):
        self.calls.append((action, payload))
        return {"status": "ok", "note": "test@example.com"}


def _call(name, **arguments):
    return {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}


def test_tools_refuse_what_was_not_granted_and_mask_results():
    orchestrator = _Orchestrator()
    listed = asyncio.run(gateway.mcp_reply("trainer", {"id": 1, "method": "tools/list"}, orchestrator))
    names = {tool["name"] for tool in listed["result"]["tools"]}
    assert names == {"agent_action", "hub_search", "hub_read", "obsidian_search", "obsidian_read", "learning_inbox",
                     "web_search", "web_fetch", "archive_search", "archive_read", "note_write", "ask_agent",
                     "material_list", "material_read", "video_digest", "drive_save"}

    denied = asyncio.run(gateway.mcp_reply("trainer", _call("agent_action", action="place_trade"), orchestrator))
    text = denied["result"]["content"][0]["text"]
    assert "action_not_granted" in text and "workout_plan" in text and orchestrator.calls == []

    done = asyncio.run(gateway.mcp_reply("trainer", _call("agent_action", action="workout_plan"), orchestrator))
    assert orchestrator.calls == [("workout_plan", {})]
    assert "test@example.com" not in done["result"]["content"][0]["text"]

    unknown = asyncio.run(gateway.mcp_reply("trainer", _call("terminal", command="id"), orchestrator))
    assert "available_tools" in unknown["result"]["content"][0]["text"]
    assert asyncio.run(gateway.mcp_reply("trainer", {"method": "notifications/initialized"}, orchestrator)) is None
    assert "error" in asyncio.run(gateway.mcp_reply("trainer", {"id": 2, "method": "resources/list"}, orchestrator))


def test_obsidian_is_read_only_inside_the_vault(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "note.md").write_text("текст", encoding="utf-8")
    (tmp_path / "secret.md").write_text("чуже", encoding="utf-8")
    (vault / "data.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", str(vault))
    assert gateway._read_note("note.md") == "текст"
    assert gateway._read_note("../secret.md") == "Такої нотатки немає."
    assert gateway._read_note("data.json") == "Такої нотатки немає."
    monkeypatch.delenv("OBSIDIAN_VAULT_DIR")
    assert gateway._read_note("note.md") == "Сховище Obsidian недоступне."


def test_hermes_chat_screens_masks_and_fails_honestly(monkeypatch):
    _token(monkeypatch)
    seen = {}

    def hermes(request):
        seen["body"] = json.loads(request.content)
        seen["session"] = request.headers["x-hermes-session-key"]
        return httpx.Response(200, json={"choices": [{"message": {"content": "Готово"}}]})

    ok = asyncio.run(gateway.hermes_chat("trainer", "пиши на test@example.com", "42", "Урок",
                                         transport=httpx.MockTransport(hermes)))
    assert ok["response"] == "Готово" and ok["runtime"] == "hermes" and seen["session"] == "telegram-42"
    assert "test@example.com" not in json.dumps(seen["body"], ensure_ascii=False)
    assert seen["body"]["messages"][0] == {"role": "system", "content": "Урок"}

    secret = asyncio.run(gateway.hermes_chat("trainer", "ключ sk-ant-api03-" + "x" * 40, "42",
                                             transport=httpx.MockTransport(hermes)))
    assert secret["status"] == "refused"

    down = asyncio.run(gateway.hermes_chat("trainer", "Привіт", "42",
                                           transport=httpx.MockTransport(lambda r: httpx.Response(502))))
    assert down["status"] == "unavailable" and down["reason"] == "hermes_unavailable"


def test_the_token_tool_prints_nothing_but_the_env_file(monkeypatch, capsys):
    import structlog

    from src import hermes_token

    async def master():
        structlog.get_logger("test").info("Vault authenticated", lease_duration_seconds=3600)
        return "master-for-tests"

    saved = structlog.get_config()
    monkeypatch.setattr(hermes_token, "_master", master)
    monkeypatch.setattr(hermes_token.sys, "argv", ["hermes_token", "trainer"])
    try:
        assert hermes_token.main() == 0
    finally:
        structlog.configure(**saved)
    lines = capsys.readouterr().out.splitlines()
    assert [line.split("=", 1)[0] for line in lines] == ["API_SERVER_KEY", "SYNDICATE_TOKEN"]


def test_trainer_tools_reach_the_model_without_the_search_bridge():
    """The tool_search bridge cost ~9 model calls per turn in the first live run (2026-11-03)."""
    from pathlib import Path

    import yaml

    config = yaml.safe_load((Path(__file__).resolve().parent.parent / "deploy/hermes/trainer/config.yaml")
                            .read_text(encoding="utf-8"))
    assert config["tools"]["tool_search"]["enabled"] == "off"


def test_trainer_hermes_mounts_exactly_its_profile_skills():
    """A skill assigned in the profile but not mounted would silently never reach the Trainer."""
    import json
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    profile = json.loads((root / "config/agents/trainer.profile.json").read_text(encoding="utf-8"))
    catalog = {item["id"]: item for item in json.loads(
        (root / "config/skill_library.json").read_text(encoding="utf-8"))["skills"]}
    compose = (root / "deploy/docker-compose.hermes.yml").read_text(encoding="utf-8")
    mounts = dict((name, source) for source, name in re.findall(r"- \.\./(\S+):/opt/syndicate-skills/([\w-]+):ro", compose))
    assert set(mounts) == set(profile["reference_skills"])
    for name, source in mounts.items():
        assert catalog[name]["resources"]["SKILL.md"] == f"{source}/SKILL.md"
        assert (root / source / "SKILL.md").is_file()
