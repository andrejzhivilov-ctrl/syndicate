"""Shared skill / prompt / MCP pools: every director reads, nobody installs from chat."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.agent_chat import chat_reply, pool_command, pool_reference, pool_reply
from src.pool_library import PoolError, PoolLibrary
from src.vault_paths import DIRECTOR_IDS

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture()
def pools(tmp_path: Path) -> PoolLibrary:
    _write(tmp_path / "config/pool_access.json", json.dumps({"read": {"agents": "all_directors"}}))
    _write(tmp_path / ".agents/skills/seo-audit/SKILL.md",
           "---\nname: seo-audit\ndescription: Audit a site for SEO and marketing gaps.\n---\nSteps...")
    _write(tmp_path / "Arena_Knowledge_Pool/01_Промпты_по_категориям/09_Маркетинг/00_Категорія_Маркетинг.md", "index")
    _write(tmp_path / "Arena_Knowledge_Pool/01_Промпты_по_категориям/09_Маркетинг/01_Контент-план.md",
           "---\ntitle: \"Контент-план для блогу\"\ncategory: \"Маркетинг\"\n---\n# Контент-план\nСклади план постів.")
    _write(tmp_path / "Arena_Knowledge_Pool/06_Шаблоны_и_Сервисы/landing.md", "# Маркетинг лендинг шаблон")
    _write(tmp_path / "mcp_servers/mcp_servers_registry.json", json.dumps({"servers": [
        {"name": "acme/telegram-mcp", "url": "https://github.com/acme/telegram-mcp",
         "category": "Communication", "description": "Send Telegram messages from an agent."}]}))
    return PoolLibrary(tmp_path)


def test_every_director_can_search_all_three_kinds(pools):
    assert pools.readers() == frozenset(DIRECTOR_IDS)
    assert pools.counts() == {"skill": 0, "prompt": 0, "mcp": 0}  # lazy until first use
    for agent in DIRECTOR_IDS:
        assert pools.search(agent, "маркетинг контент", kind="prompt")[0]["title"] == "Контент-план для блогу"
    assert pools.search("dex", "seo marketing", kind="skill")[0]["title"] == "seo-audit"
    assert pools.search("eva", "telegram", kind="mcp")[0]["url"] == "https://github.com/acme/telegram-mcp"
    assert pools.counts() == {"skill": 1, "prompt": 1, "mcp": 1}


def test_courses_templates_and_category_index_pages_are_not_pools(pools):
    titles = {hit["title"] for hit in pools.search("eva", "маркетинг шаблон лендинг категорія", limit=5)}
    assert titles == {"Контент-план для блогу"}


def test_unknown_agent_and_missing_access_file_are_denied(pools, tmp_path):
    with pytest.raises(PoolError, match="pool_read_not_granted"):
        pools.search("intruder", "маркетинг")
    (tmp_path / "config/pool_access.json").unlink()
    with pytest.raises(PoolError, match="pool_read_not_granted"):
        PoolLibrary(tmp_path).search("eva", "маркетинг")


def test_reading_mcp_returns_catalog_metadata_never_an_install(pools):
    item_id = pools.search("architect", "telegram", kind="mcp")[0]["id"]
    item = pools.read("architect", item_id)
    assert item["note"] == "catalog_entry_only_install_requires_operator_approval"
    assert "text" not in item and item["untrusted_reference"] is True


def test_reading_a_prompt_is_bounded_text(pools, tmp_path):
    _write(tmp_path / "knowledge_pools/prompts/long.md", "---\ntitle: Довгий\n---\n" + "слово " * 2000)
    lib = PoolLibrary(tmp_path)
    item = lib.read("oscar", lib.search("oscar", "довгий", kind="prompt")[0]["id"])
    assert item["truncated"] is True and len(item["text"]) <= 3500


def test_telegram_pool_commands_answer_without_a_model(pools):
    assert pool_command({"text": "/skills seo"}) == ("/skills", "seo")
    assert pool_command({"text": "/prompts@syndicate_bot контент"}) == ("/prompts", "контент")
    assert pool_command({"text": "/status"}) is None
    listing = pool_reply("tyler", "/prompts", "контент маркетинг", pools)
    assert listing["status"] == "completed" and "Контент-план для блогу" in listing["response"]
    item_id = pools.search("tyler", "контент", kind="prompt")[0]["id"]
    opened = pool_reply("tyler", "/pool", item_id, pools)
    assert "Склади план постів" in opened["response"]
    assert pool_reply("tyler", "/pool", "p-0000000000", pools)["reason"] == "unknown_pool_item"


def test_chat_gets_pool_reference_only_when_the_pools_are_mentioned(pools):
    assert pool_reference("ray", "Привіт, як справи?", pools) is None
    reference = pool_reference("ray", "Є скіл для seo аудиту?", pools)
    assert "seo-audit" in reference and len(reference) <= 1200

    class LLM:
        calls = []

        async def ainvoke(self, messages):
            self.calls.append(messages)
            return SimpleNamespace(content="Так, є seo-audit.")

    llm = LLM()
    asyncio.run(chat_reply("ray", "Є скіл для seo аудиту?", llm, reference=reference))
    system_notes = [text for role, text in llm.calls[0] if role == "system"]
    assert len(system_notes) == 2 and "недовірений довідковий матеріал" in system_notes[1]


def _orch(pools):
    from src.orchestrator import EvaOrchestrator

    orch = EvaOrchestrator.__new__(EvaOrchestrator)

    async def owner():
        return "523"

    async def must_not_route(**kwargs):
        raise AssertionError("pool commands must not reach task routing")

    orch._telegram_owner_id = owner
    orch._pools = lambda: pools
    orch.execute = must_not_route
    return orch


def _payload(text, chat="523"):
    return {"text": text, "chat_id": chat, "message": {"chat": {"id": chat}, "text": text}}


def test_pool_commands_work_in_every_bot_including_eva_and_only_for_the_owner(pools):
    out = asyncio.run(_orch(pools).handle_webhook(source="telegram_eva", payload=_payload("/mcp telegram")))
    assert out["result"]["mode"] == "pool" and "acme/telegram-mcp" in out["result"]["response"]
    denied = asyncio.run(_orch(pools).handle_webhook(source="telegram_sam", payload=_payload("/skills seo", chat="9")))
    assert denied["result"]["status"] == "denied"


def test_real_repository_pools_are_indexed_and_shipped_in_the_image():
    lib = PoolLibrary(REPO_ROOT)
    counts = (lib.items, lib.counts())[1]
    assert counts["skill"] >= 100 and counts["prompt"] >= 3000 and counts["mcp"] >= 15000
    access = json.loads((REPO_ROOT / "config/pool_access.json").read_text(encoding="utf-8"))
    assert "mcp.call" in access["requires_operator_approval"]
    dockerfile = (REPO_ROOT / "deploy/docker/Dockerfile.agent").read_text(encoding="utf-8")
    for path in ("config/pool_access.json", "knowledge_pools", "mcp_servers/mcp_servers_registry.json",
                 "Arena_Knowledge_Pool/01_Промпты_по_категориям"):
        assert path in dockerfile
    assert "06_Шаблоны_и_Сервисы" not in dockerfile and "07_Курсы_Платформы" not in dockerfile
