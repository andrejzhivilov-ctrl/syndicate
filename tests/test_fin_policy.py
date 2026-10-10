from decimal import Decimal as D

from src.agents import fin_policy as fp


def test_runway_needs_three_months_and_positive_burn():
    assert fp.runway_months(D("100"), [D("10"), D("10")]) is None
    assert fp.runway_months(D("100"), [D("0"), D("0"), D("0")]) is None


def test_runway_value_and_zones():
    months = fp.runway_months(D("72"), [D("10"), D("10"), D("10")])
    assert months == D("7.2")
    assert fp.runway_zone(months) == "green"
    assert fp.runway_zone(D("6")) == "yellow"
    assert fp.runway_zone(D("3")) == "yellow"
    assert fp.runway_zone(D("2.9")) == "red"
    assert fp.runway_zone(None) == "undefined"


def test_reconcile_any_difference_is_unreconciled():
    assert fp.reconcile_receipt([D("10.00"), D("5.50")], D("15.50"))["status"] == "bank_pending"
    assert fp.reconcile_receipt([D("10.00"), D("5.50")], D("15.51"))["status"] == "unreconciled"
    assert fp.reconcile_receipt([D("10.00")], D("10.00"), bank_amount=D("10.00"))["status"] == "reconciled"
    assert fp.reconcile_receipt([D("10.00")], D("10.00"), bank_amount=D("10.01"))["status"] == "unreconciled"


def test_basket_audit_is_advisory_only():
    assert fp.basket_audit(D("300"), None)["decision"] == "hold"
    assert fp.basket_audit(D("300"), D("500"))["decision"] == "within_budget"
    over = fp.basket_audit(D("600"), D("500"))
    assert over["decision"] == "over_budget" and over["shortfall"] == "100"
    assert fp.basket_audit(D("1"), D("5"))["advisory_only"] is True


def test_allocate_food_from_groceries_only():
    funds = {"groceries": D("800"), "leisure": D("300"), "goals": D("0"), "safety": D("9000")}
    ok = fp.allocate_purchase(D("500"), "food", funds, "groceries")
    assert ok["status"] == "funds_allocated" and ok["source_fund"] == "groceries"
    assert fp.allocate_purchase(D("900"), "food", funds, "groceries")["status"] == "next_period"


def test_allocate_never_uses_safety_fund():
    funds = {"groceries": D("0"), "leisure": D("0"), "goals": D("0"), "safety": D("9000")}
    res = fp.allocate_purchase(D("100"), "other", funds, "gadget", fund="safety")
    assert res["status"] == "reserve_blocked"
    assert "source_fund" not in res


def test_allocate_is_always_advisory():
    funds = {"groceries": D("800"), "leisure": D("0"), "goals": D("0"), "safety": D("0")}
    assert fp.allocate_purchase(D("100"), "food", funds, "x")["advisory_only"] is True


def test_token_guard_levels_and_marshal_signal():
    assert fp.token_guard(D("1.00"))["level"] == "ok"
    assert fp.token_guard(D("4.00"))["level"] == "warn"
    assert fp.token_guard(D("4.00"))["switch_to_cheap_models"] is True
    assert fp.token_guard(D("5.00"))["level"] == "over"
    spike = fp.token_guard(D("1.00"), D("0.60"))
    assert spike["level"] == "circuit_signal" and spike["notify_marshal"] is True


def test_fx_alert_threshold():
    assert fp.fx_move_alert(D("40.00"), D("40.50"))["alert"] is False  # 1.25%
    assert fp.fx_move_alert(D("40.00"), D("40.70"))["alert"] is True   # 1.75%
    assert fp.fx_move_alert(D("0"), D("40"))["alert"] is False
