import asyncio
from decimal import Decimal as D

from src.agents import doc_shopping as S


def test_nutrition_owner_is_doc_and_eva_uses_same_criteria():
    from src.agents import eva_basket as B

    assert S.NUTRITION_OWNER == "doc"
    assert B.nutrition_score is S.nutrition_score
    assert B.within_limits is S.within_limits


def test_shopping_list_ready_for_eva_and_never_orders():
    out = S.build_shopping_list([
        {"name": "Куряче філе", "qty": 1, "unit": "кг", "category": "meat",
         "nutrition": {"sugar_g": 0, "fat_g": 2, "carbs_g": 0}},
        {"name": "Овсянка", "qty": 2, "unit": "пачка", "category": "grains"},
    ], meal_plan_ref="plan-2026-10-12")
    assert out["status"] == "ready_for_eva" and out["to"] == "eva"
    assert out["order_allowed"] is False and out["meal_plan_ref"] == "plan-2026-10-12"
    assert out["items"][0]["nutrition_check"] is True
    assert out["items"][1]["nutrition_check"] is None  # даних немає — не вигадуємо


def test_shopping_list_rejects_bad_rows():
    assert S.build_shopping_list([{"name": " ", "qty": 1}])["reason"] == "empty_name"
    assert S.build_shopping_list([{"name": "x", "qty": 0}])["reason"] == "bad_qty"
    assert S.build_shopping_list([{"name": "x", "category": "electronics"}])["reason"] == "unknown_category"
    assert S.build_shopping_list([])["reason"] == "empty_list"


def test_doc_agent_shopping_list_action():
    from src.agents.doc import DocAgent

    agent = DocAgent(memory=None)
    out = asyncio.run(agent.execute({"action": "shopping_list",
                                     "items": [{"name": "Яйця", "qty": 10, "category": "eggs"}]}))
    assert out["agent"] == "doc" and out["status"] == "ready_for_eva"
    assert D(out["items"][0]["qty"]) == D(10)
