"""Gateway tools of a Hermes agent: internet, archive, own notes and colleagues, all capped (06.11.2026)."""
import asyncio
import json
import re
from pathlib import Path

import httpx

from src import hermes_gateway as gateway
from src import hermes_tools as tools

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = {"example.org": ["93.184.216.34"], "pubmed.example": ["130.14.29.110"]}
INTERNAL = {"inside.example": ["10.0.0.5"], "metadata.example": ["169.254.169.254"],
            "mixed.example": ["93.184.216.34", "127.0.0.1"]}


def _resolver(host):
    known = {**PUBLIC, **INTERNAL}
    if host not in known:
        raise OSError("no such host")
    return known[host]


def test_only_granted_agents_get_the_tools_and_the_hermes_toolsets_stay_off():
    assert set(tools.granted("trainer")) == {"web_search", "web_fetch", "archive_search", "archive_read",
                                             "note_write", "ask_agent", "material_list", "material_read", "drive_save"}
    assert tools.granted("sam") == () and tools.granted("nobody") == ()
    config = (ROOT / "deploy" / "hermes" / "trainer" / "config.yaml").read_text(encoding="utf-8")
    off = re.search(r"disabled_toolsets: \[([^\]]*)\]", config)
    assert off and {"terminal", "file", "web", "browser", "code_execution", "delegation", "computer_use"} <= {
        name.strip() for name in off.group(1).split(",")}
    assert "api_server: [memory, skills, session_search, mcp-syndicate]" in config
    compose = (ROOT / "deploy" / "docker-compose.hermes.yml").read_text(encoding="utf-8")
    assert "privileged" not in compose and "docker.sock" not in compose and "- ALL" in compose


def test_web_search_masks_the_query_uses_sonar_and_returns_sources():
    seen = {}

    def provider(request):
        seen["body"] = json.loads(request.content)
        seen["key"] = request.headers["authorization"]
        return httpx.Response(200, json={"choices": [{"message": {"content": "Креатин 3-5 г на день.", "annotations": [
            {"type": "url_citation", "url_citation": {"url": "https://pubmed.example/2"}}]}}],
            "citations": ["https://pubmed.example/1"], "usage": {"cost": 0.006}})

    found = asyncio.run(tools.web_search("креатин доза, пиши на test@example.com", "real-key",
                                         transport=httpx.MockTransport(provider)))
    assert found["status"] == "ok" and found["answer"].startswith("Креатин")
    assert found["sources"] == ["https://pubmed.example/1", "https://pubmed.example/2"]
    assert seen["body"]["model"] == "perplexity/sonar" and seen["key"] == "Bearer real-key"
    assert "test@example.com" not in json.dumps(seen["body"], ensure_ascii=False)

    down = asyncio.run(tools.web_search("креатин", "real-key", transport=httpx.MockTransport(lambda r: httpx.Response(502))))
    assert down == {"status": "unavailable", "reason": "search_failed"}
    assert asyncio.run(tools.web_search("креатин", ""))["reason"] == "model_key_unavailable"
    assert asyncio.run(tools.web_search("  ", "real-key"))["error"] == "empty_query"


def test_only_public_http_addresses_may_be_fetched():
    assert tools.check_url("https://example.org/a", _resolver) is None
    assert tools.check_url("file:///etc/passwd", _resolver) == "only_http_urls"
    assert tools.check_url("ftp://example.org/x", _resolver) == "only_http_urls"
    assert tools.check_url("http://user:pw@example.org/", _resolver) == "credentials_in_url"
    assert tools.check_url("http://example.org/?mail=test@example.com", _resolver) == "personal_data_in_url"
    for url in ("http://inside.example/", "http://metadata.example/latest", "http://mixed.example/",
                "http://[::1]:8000/", "http://unknown.example/", "http://syndicate-agent:8000/health"):
        assert tools.check_url(url, _resolver) == "address_not_public", url


def test_fetch_reads_text_follows_only_public_redirects_and_refuses_the_rest():
    def site(request):
        if request.url.path == "/article":
            return httpx.Response(200, headers={"content-type": "text/html; charset=utf-8"},
                                  text="<html><head><title>t</title><script>steal()</script></head>"
                                       "<body><h1>Білок</h1><p>1,6 г/кг на день.</p></body></html>")
        if request.url.path == "/moved":
            return httpx.Response(301, headers={"location": "/article"})
        if request.url.path == "/inside":
            return httpx.Response(302, headers={"location": "http://inside.example/admin"})
        if request.url.path == "/pdf":
            return httpx.Response(200, headers={"content-type": "application/pdf"}, content=b"%PDF")
        if request.url.path == "/huge":
            return httpx.Response(200, headers={"content-type": "text/plain"}, content=b"a" * (tools.MAX_FETCH_BYTES * 2))
        return httpx.Response(404)

    def fetch(url):
        return asyncio.run(tools.web_fetch(url, resolver=_resolver, transport=httpx.MockTransport(site)))

    page = fetch("https://example.org/moved")
    assert page["status"] == "ok" and page["url"] == "https://example.org/article"
    assert "Білок" in page["text"] and "1,6 г/кг" in page["text"] and "steal" not in page["text"]
    assert page["note"] == tools.UNTRUSTED

    inside = fetch("https://example.org/inside")
    assert inside == {"status": "refused", "reason": "address_not_public", "url": "http://inside.example/admin"}
    assert fetch("https://example.org/pdf")["reason"] == "not_a_text_page"
    assert fetch("https://example.org/missing")["reason"] == "http_error"
    huge = fetch("https://example.org/huge")
    assert huge["status"] == "ok" and huge["truncated"] and len(huge["text"]) == tools.MAX_PAGE_CHARS


def test_the_archive_is_read_only_and_says_when_it_is_not_connected(tmp_path, monkeypatch):
    monkeypatch.delenv("KODEX_DATA_DIR", raising=False)
    assert tools.archive_search("аналіз") == {"status": "unavailable", "reason": "archive_not_connected"}

    from src.agents.eva_kodex import KodexStore

    store = KodexStore(tmp_path / "kodex.json", tmp_path / "blobs")
    text_id = store.ingest("Аналіз_крові_2026.md", "Гемоглобін 150".encode("utf-8"), origin="andrii_direct")["id"]
    pdf_id = store.ingest("Аналіз_крові_скан.pdf", b"%PDF-1.7", origin="agent")["id"]
    store.save()
    monkeypatch.setenv("KODEX_DATA_DIR", str(tmp_path))

    found = tools.archive_search("аналіз крові")
    assert found["status"] == "ok" and found["found"] == 2
    read = tools.archive_read(text_id)
    assert read["status"] == "ok" and read["text"] == "Гемоглобін 150" and read["protected"] is True
    assert tools.archive_read(pdf_id)["reason"] == "not_a_text_file"
    assert tools.archive_read("nope")["error"] == "not_found"
    assert not any(hasattr(tools, name) for name in ("archive_write", "archive_delete"))


def test_notes_go_only_to_the_own_folder_and_never_overwrite(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    (vault / "Health_Coach").mkdir(parents=True)
    (vault / "Finance").mkdir()
    (vault / "Health_Coach" / "Аналізи.md").write_text("---\nandrii_protected: true\n---\nмої аналізи", encoding="utf-8")
    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", str(vault))
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))

    made = tools.note_write("trainer", "Workouts/Тиждень_45.md", "Пн: присід 5×5", "create")
    assert made == {"status": "ok", "mode": "create", "path": "Health_Coach/Workouts/Тиждень_45.md"}
    added = tools.note_write("trainer", "Workouts/Тиждень_45.md", "Ср: жим 5×5", "append")
    assert added["status"] == "ok"
    note = (vault / "Health_Coach" / "Workouts" / "Тиждень_45.md").read_text(encoding="utf-8")
    assert "присід" in note and "жим" in note

    assert tools.note_write("trainer", "Workouts/Тиждень_45.md", "інше", "create")["reason"] == "note_exists"
    assert tools.note_write("trainer", "Аналізи.md", "зміна", "append")["reason"] == "protected"
    assert "зміна" not in (vault / "Health_Coach" / "Аналізи.md").read_text(encoding="utf-8")
    assert tools.note_write("trainer", "Нема.md", "x", "append")["reason"] == "note_not_found"
    for path in ("../Finance/x.md", "/etc/x.md", "x.txt"):
        assert tools.note_write("trainer", path, "x", "create")["reason"] == "outside_own_folder", path
    assert not (vault / "Finance" / "x.md").exists()
    assert tools.note_write("trainer", "x.md", "x", "overwrite")["error"] == "unknown_mode"
    assert tools.note_write("sam", "x.md", "x", "create")["reason"] == "vault_unavailable"

    log = (tmp_path / "data" / "obsidian_activity" / "activity.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["action"] for line in log] == ["create", "append"]


class _Llm:
    def __init__(self, reply="Бюджет на добавки: 1200 грн на місяць.", fail=False):
        self.reply, self.fail, self.seen = reply, fail, []

    async def ainvoke(self, messages):
        self.seen.append(messages)
        if self.fail:
            raise RuntimeError("provider down")
        return type("Reply", (), {"content": self.reply})()


class _Orchestrator:
    def __init__(self, llm):
        self.llm, self.asked = llm, []

    def _llm_for(self, agent):
        self.asked.append(agent)
        return self.llm

    def openrouter_key(self):
        return ""


def test_ask_agent_is_one_question_on_the_direct_path():
    orchestrator = _Orchestrator(_Llm())
    asked = asyncio.run(tools.ask_agent("trainer", "fin", "Який бюджет на добавки?", orchestrator))
    assert asked == {"status": "ok", "agent": "fin", "answer": "Бюджет на добавки: 1200 грн на місяць."}
    assert orchestrator.asked == ["fin"]
    sent = json.dumps(orchestrator.llm.seen[0], ensure_ascii=False, default=str)
    assert "не від Андрія" in sent and "нічого не виконуй" in sent

    wrong = asyncio.run(tools.ask_agent("trainer", "trainer", "сам собі", orchestrator))
    assert wrong["error"] == "unknown_agent" and "trainer" not in wrong["available_agents"]
    assert "eva" in wrong["available_agents"] and "alice" not in wrong["available_agents"]
    assert asyncio.run(tools.ask_agent("trainer", "eva", " ", orchestrator))["error"] == "empty_or_too_long"
    down = asyncio.run(tools.ask_agent("trainer", "eva", "Як справи?", _Orchestrator(_Llm(fail=True))))
    assert down["status"] == "unavailable" and down["agent"] == "eva"


def test_daily_limit_counts_per_agent_and_tool(tmp_path):
    limit = tools.DailyLimit(tmp_path / "use.json", {"web_search": 2})
    assert limit.take("trainer", "web_search") and limit.take("trainer", "web_search")
    assert not limit.take("trainer", "web_search") and limit.used("trainer", "web_search") == 2
    assert limit.take("sam", "web_search")
    assert not limit.take("trainer", "unknown_tool")  # no limit written means no calls


def _call(name, **arguments):
    return {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}


def test_the_gateway_routes_the_tools_and_stops_at_the_daily_limit(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(tools, "DAILY_LIMITS", {**tools.DAILY_LIMITS, "ask_agent": 1})
    orchestrator = _Orchestrator(_Llm())

    listed = asyncio.run(gateway.mcp_reply("trainer", {"id": 1, "method": "tools/list"}, orchestrator))
    ask = next(tool for tool in listed["result"]["tools"] if tool["name"] == "ask_agent")
    assert ask["inputSchema"]["properties"]["agent"]["enum"] == tools.ask_targets("trainer")

    first = asyncio.run(gateway.mcp_reply("trainer", _call("ask_agent", agent="eva", question="Привіт"), orchestrator))
    assert "1200 грн" in first["result"]["content"][0]["text"]
    second = asyncio.run(gateway.mcp_reply("trainer", _call("ask_agent", agent="eva", question="Ще"), orchestrator))
    assert "daily_limit_reached" in second["result"]["content"][0]["text"] and orchestrator.asked == ["eva"]

    no_key = asyncio.run(gateway.mcp_reply("trainer", _call("web_search", query="креатин"), orchestrator))
    assert "model_key_unavailable" in no_key["result"]["content"][0]["text"]
    local = asyncio.run(gateway.mcp_reply("trainer", _call("web_fetch", url="http://127.0.0.1:8000/admin"), orchestrator))
    assert "address_not_public" in local["result"]["content"][0]["text"]
