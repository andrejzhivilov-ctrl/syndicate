"""Alex ready for daily work (16.11.2026): own tables, own folder, skills by buttons, real KBJU."""

from __future__ import annotations

import asyncio

import httpx
from openpyxl import load_workbook

from src import agent_folders, food_facts, hermes_tools, skill_approval


def test_alex_writes_his_own_table_with_formulas_and_a_markdown_copy(tmp_path, monkeypatch):
    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", str(tmp_path))
    sheets = [{"title": "Раціон", "rows": [["Продукт", "Ккал"], ["Гречка", 329], ["Разом", "=SUM(B2:B2)"]]}]
    made = hermes_tools.table_save("trainer", "Health_Coach/Таблиці/Раціон.xlsx", sheets)
    assert made["status"] == "ok" and made["path"] == "Health_Coach/Таблиці/Раціон.xlsx"  # no second Health_Coach
    book = load_workbook(tmp_path / "Health_Coach/Таблиці/Раціон.xlsx")
    assert book["Раціон"]["B2"].value == 329 and book["Раціон"]["B3"].value == "=SUM(B2:B2)"
    copy = (tmp_path / "Health_Coach/Таблиці/Раціон.md").read_text(encoding="utf-8")
    assert "| Гречка | 329 |" in copy and "summary:" in copy
    assert hermes_tools.table_save("trainer", "Таблиці/Раціон.xlsx", sheets)["action"] == "replaced"
    assert hermes_tools.table_save("trainer", "../Інше/x.xlsx", sheets)["status"] == "refused"
    assert hermes_tools.table_save("trainer", "Таблиці/x.xlsx", "не таблиця")["error"] == "bad_sheets"
    assert hermes_tools.TABLE_SAVE in hermes_tools.granted("trainer")


def test_a_note_path_with_the_folder_in_front_is_not_nested_twice(tmp_path, monkeypatch):
    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", str(tmp_path))
    done = hermes_tools.note_write("trainer", "Health_Coach/Щоденник/Рефлексія/2026-11-17.md", "Підсумок", "create")
    assert done["path"] == "Health_Coach/Щоденник/Рефлексія/2026-11-17.md"
    assert (tmp_path / "Health_Coach/Щоденник/Рефлексія/2026-11-17.md").is_file()


def test_the_own_folder_and_its_map_are_laid_out_once_and_nothing_existing_is_touched(tmp_path):
    (tmp_path / "Health_Coach").mkdir()
    (tmp_path / "Health_Coach/Карта.md").write_text("моя карта", encoding="utf-8")
    created = agent_folders.ensure("trainer", tmp_path)
    assert "Health_Coach/Щоденник/Заміри" in created and "Health_Coach/Харчування/Продукти" in created
    assert (tmp_path / "Health_Coach/Карта.md").read_text(encoding="utf-8") == "моя карта"
    assert agent_folders.ensure("trainer", tmp_path) == []
    fresh = tmp_path / "other"
    fresh.mkdir()
    agent_folders.ensure("trainer", fresh)
    assert "Щоденник/" in (fresh / "Health_Coach/Карта.md").read_text(encoding="utf-8")


def test_a_sensitive_skill_becomes_two_buttons_and_the_decision_is_kept_for_eva(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    reply, proposals = skill_approval.split(
        "trainer", "Зробив план.\n<<СКІЛ: Протокол креатину | дози щодня>>")
    assert reply == "Зробив план." and proposals[0]["name"] == "Протокол креатину"
    text, markup = skill_approval.question(proposals[0])
    buttons = markup["inline_keyboard"][0]
    assert "Протокол креатину" in text and [b["text"] for b in buttons] == ["✅ Погодити", "❌ Відхилити"]
    assert all(len(b["callback_data"].encode()) <= 64 for b in buttons)
    decided = skill_approval.decide("trainer", buttons[0]["callback_data"])
    assert decided["approved"] and "Створи його" in decided["turn"]
    assert skill_approval.decide("trainer", buttons[1]["callback_data"])["status"] == "already"
    assert skill_approval.decide("trainer", "region:9") is None  # not a skill button
    assert [e["event"] for e in skill_approval.entries()] == ["proposed", "decided"]
    assert skill_approval.split("trainer", "Без скілів.") == ("Без скілів.", [])


def test_kbju_comes_from_open_food_facts_with_the_source_and_gaps_stay_gaps():
    def answer(request):
        if "/product/" in request.url.path:
            return httpx.Response(200, json={"product": {"code": "4820000000001", "product_name": "Сир",
                                                          "nutriments": {"energy-kcal_100g": 120}}})
        return httpx.Response(200, json={"products": [{"code": "2999300019448", "product_name": "Гречка",
                                                       "brands": "Розумний вибір", "nutriments": {
                                                           "energy-kcal_100g": 329, "proteins_100g": 13,
                                                           "fat_100g": 2.6, "carbohydrates_100g": 68}}]})

    found = asyncio.run(food_facts.lookup("гречка", httpx.MockTransport(answer)))
    product = found["products"][0]
    assert found["status"] == "ok" and product["per_100g"] == {"kcal": 329.0, "protein": 13.0, "fat": 2.6, "carbs": 68.0}
    assert product["complete"] and product["url"].endswith("/2999300019448") and "Open Food Facts" in found["source"]
    cheese = asyncio.run(food_facts.lookup("4820000000001", httpx.MockTransport(answer)))["products"][0]
    assert cheese["per_100g"]["protein"] is None and not cheese["complete"]  # never filled in
    empty = httpx.MockTransport(lambda request: httpx.Response(200, json={"products": []}))
    assert asyncio.run(food_facts.lookup("щось", empty))["reason"] == "not_found"
    down = httpx.MockTransport(lambda request: httpx.Response(503, text="down"))
    assert asyncio.run(food_facts.lookup("гречка", down))["status"] == "unavailable"


def test_open_food_facts_is_asked_again_when_it_sheds_load(monkeypatch):
    # Live 18.11.2026: 200 and 503 a second apart from the same server.
    monkeypatch.setattr(food_facts, "RETRY_PAUSE_S", 0)
    answers = iter([httpx.Response(503, text="busy"), httpx.Response(200, json={"products": [
        {"code": "1", "product_name": "Рис", "nutriments": {"energy-kcal_100g": 130}}]})])
    found = asyncio.run(food_facts.lookup("рис", httpx.MockTransport(lambda request: next(answers))))
    assert found["status"] == "ok" and found["products"][0]["name"] == "Рис"
    always = httpx.MockTransport(lambda request: httpx.Response(503, text="busy"))
    assert asyncio.run(food_facts.lookup("рис", always))["reason"] == "open_food_facts_http_503"
