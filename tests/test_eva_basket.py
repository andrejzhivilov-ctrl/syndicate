from decimal import Decimal as D

from src.agents import eva_basket as B


def _n(sugar, fat, carbs):
    return {"sugar_g": sugar, "fat_g": fat, "carbs_g": carbs}


def test_no_retailer_is_connected_by_default():
    assert all(r["status"] == "not_connected" for r in B.RETAILERS.values())
    assert {"silpo", "atb", "varus", "auchan"} <= set(B.RETAILERS)


def test_nutrition_score_needs_all_three_values():
    assert B.nutrition_score(_n(1, 2, 10)) == D("1.5") * 1 + D("2") + D("0.5") * 10
    assert B.nutrition_score({"sugar_g": 1, "fat_g": 2}) is None  # не вигадуємо
    assert B.nutrition_score(None) is None


def test_limits_none_when_data_missing():
    assert B.within_limits(_n(1, 2, 10)) is True
    assert B.within_limits(_n(9, 2, 10)) is False
    assert B.within_limits({"sugar_g": 1}) is None


def test_cheaper_alternative_must_not_be_worse_in_composition():
    item = {"name": "Йогурт A", "category": "dairy", "price": "40", "retailer": "silpo",
            "nutrition": _n(4, 2, 6)}
    candidates = [
        {"name": "Йогурт B", "category": "dairy", "price": "30", "retailer": "atb",
         "nutrition": _n(3, 1, 5)},          # дешевший і кращий склад
        {"name": "Йогурт C", "category": "dairy", "price": "25", "retailer": "atb",
         "nutrition": _n(12, 3, 8)},         # дешевший, але цукру вдвічі більше — відкинути
        {"name": "Йогурт D", "category": "dairy", "price": "35", "retailer": "atb"},  # без даних
        {"name": "Молоко", "category": "milk", "price": "20", "retailer": "atb",
         "nutrition": _n(4, 2, 6)},          # інша категорія
    ]
    res = B.cheaper_alternatives(item, candidates)
    names = [r["name"] for r in res]
    assert names[0] == "Йогурт B"
    assert "Йогурт C" not in names and "Молоко" not in names
    assert names[-1] == "Йогурт D" and res[-1]["nutrition_check"] == "unknown"


def test_basket_is_only_a_proposal_and_order_is_never_allowed():
    items = [{"name": "Овсянка", "qty": 2, "price": "35.50", "nutrition": _n(1, 6, 60)},
             {"name": "Куряче філе", "qty": 1, "price": "120", "nutrition": _n(0, 2, 0)}]
    p = B.build_basket_proposal("silpo", items)
    assert p["status"] == "awaiting_andrii_confirmation"
    assert p["order_allowed"] is False
    assert p["total"] == "191.00"
    assert p["items"][1]["nutrition_check"] is True


def test_rejects_unknown_retailer_empty_and_bad_qty():
    assert B.build_basket_proposal("unknown", [{"name": "x", "price": "1"}])["reason"] == "unknown_retailer"
    assert B.build_basket_proposal("atb", [])["reason"] == "empty_basket"
    assert B.build_basket_proposal("atb", [{"name": "x", "price": "1", "qty": 0}])["reason"] == "bad_qty"


def test_evidence_is_attached_without_changing_status():
    p = B.build_basket_proposal("atb", [{"name": "x", "price": "10"}])
    e = B.attach_evidence(p, screenshot_path="fin/out/cart.png", cart_url="https://example.invalid/cart")
    assert e["evidence"]["screenshot"] == "fin/out/cart.png"
    assert e["status"] == "awaiting_andrii_confirmation" and e["order_allowed"] is False
