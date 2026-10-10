"""Fin: джерела коштів, фонди, витрати, планувальник, маршрутизація, кнопки, звіти."""
from datetime import date
from decimal import Decimal as D

import pytest

from src.agents import fin_buttons as B
from src.agents import fin_ledger as L
from src.agents import fin_policy as fp
from src.agents import fin_reports as R
from src.agents.fin_bank_gate import bank_read_allowed

TODAY = date(2026, 10, 10)  # субота


def test_withdraw_options_orders_simplest_first_and_needs_balance():
    balances = {"monobank": (D("5000"), "UAH"), "payoneer": (D("200"), "USD"),
                "cash_wallet": (D("1000"), "UAH")}
    opts = L.withdraw_options(D("800"), "UAH", balances)
    ids = [o["source"] for o in opts]
    assert ids[:2] == ["cash_wallet", "monobank"]  # готівка, потім картка з ATM
    assert "a_bank" not in ids  # без балансу не вигадуємо
    pay = next(o for o in opts if o["source"] == "payoneer")
    assert pay["status"] == "needs_conversion" and pay["intl"] is True


def test_no_source_is_fop_and_no_payment_fields():
    assert "fop" not in L.SOURCES
    for meta in L.SOURCES.values():
        assert not ({"iban", "card", "pan", "cvv", "login", "password"} & set(meta))


def test_safety_fund_cannot_be_expense_source():
    with pytest.raises(ValueError):
        L.Expense(TODAY, D("10"), "UAH", "safety", "food", "x")


def test_period_bounds_week_is_monday_to_sunday():
    assert L.period_bounds(TODAY, "week") == (date(2026, 10, 5), date(2026, 10, 11))
    assert L.period_bounds(TODAY, "month") == (date(2026, 10, 1), date(2026, 10, 31))


def test_planner_cadences_and_month_end_clamp():
    pays = [
        L.PlannedPayment("d", "Підписка", D("10"), "UAH", "day"),
        L.PlannedPayment("w", "ЄСВ-огляд", D("100"), "UAH", "week", weekday=0),
        L.PlannedPayment("m", "Комуналка", D("2000"), "UAH", "month", day_of_month=31),
        L.PlannedPayment("o", "Contabo", D("20"), "USD", "once", on=date(2026, 10, 12)),
    ]
    h = L.plan_header(pays, TODAY)
    assert h["day"]["totals"] == {"UAH": "10.00"}
    # тиждень 5–11 жовтня: 7×10 підписка + понеділок 5-го 100 (USD 12-го — наступного тижня)
    assert h["week"]["totals"] == {"UAH": "170.00"}
    # місяць: 31×10 + понеділки 5,12,19,26 по 100 + 31-го 2000 ; USD 20 за 12-те
    assert h["month"]["totals"] == {"UAH": "2710.00", "USD": "20.00"}
    # 31 жовтня існує; у листопаді клампиться до 30-го
    nov = L.plan_items(pays, date(2026, 11, 1), date(2026, 11, 30))
    assert [r["date"] for r in nov if r["payment_id"] == "m"] == ["2026-11-30"]


def test_plan_header_always_has_four_periods_with_totals():
    h = L.plan_header([], TODAY)
    assert set(h) == {"day", "week", "month", "next_30_days"}
    assert all("totals" in v for v in h.values())


def test_spend_by_fund_and_expense_in_period():
    exp = [L.Expense(TODAY, D("420"), "UAH", "groceries", "food", "молоко", store="АТБ", source="monobank"),
           L.Expense(date(2026, 9, 1), D("999"), "UAH", "leisure", "fun", "old")]
    totals = L.spend_by_fund(exp, *L.period_bounds(TODAY, "month"))
    assert totals["groceries"] == D("420") and totals["leisure"] == D("0")


def test_route_only_eva_and_andrii():
    assert L.route_allowed("eva", "funds_check")
    assert not L.route_allowed("eva", "bank_read")
    assert not L.route_allowed("doc", "funds_check")  # Док не говорить з Фіном напряму
    assert L.route_allowed("andrii", "anything")


def test_bank_gate_default_deny():
    assert bank_read_allowed("monobank", []) is False
    assert bank_read_allowed("monobank", ["monobank"]) is True
    assert bank_read_allowed("unknown_bank", ["unknown_bank"]) is False


def test_allocate_food_uses_groceries_and_fund_required_for_other():
    funds = {"groceries": D("800"), "leisure": D("300"), "goals": D("0"), "safety": D("9000")}
    ok = fp.allocate_purchase(D("500"), "food", funds, "продукти")
    assert ok["status"] == "funds_allocated" and ok["source_fund"] == "groceries"
    assert fp.allocate_purchase(D("900"), "food", funds, "продукти")["status"] == "next_period"
    assert fp.allocate_purchase(D("100"), "other", funds, "гаджет")["status"] == "fund_required"
    assert fp.allocate_purchase(D("100"), "other", funds, "гаджет", fund="leisure")["source_fund"] == "leisure"
    assert fp.allocate_purchase(D("100"), "other", funds, "x", fund="safety")["status"] == "reserve_blocked"


def test_buttons_fit_telegram_limit_and_permissions():
    for menu in B.MENUS:
        for sender in ("andrii", "eva"):
            kb = B.build_keyboard(menu, sender)
            for row in kb["inline_keyboard"]:
                for btn in row:
                    assert len(btn["callback_data"].encode()) <= 64
    eva_main = B.build_keyboard("main", "eva")["inline_keyboard"]
    texts = [b["text"] for row in eva_main for b in row]
    assert not any("ЗВІТ — повний" in t for t in texts)  # повний звіт — лише Андрію


def test_full_report_button_only_for_andrii():
    assert B.handle_callback("rep:full", "andrii")["action"] == "report"
    assert B.handle_callback("rep:full", "eva") is None
    assert B.handle_callback("funds:basket", "eva")["action"] == "funds_check"
    assert B.handle_callback("nope", "andrii") is None


def _sample_report(kind="full"):
    pays = [L.PlannedPayment("m", "Комуналка", D("2000"), "UAH", "month", fund="goals", day_of_month=15),
            L.PlannedPayment("d", "Підписка", D("10"), "UAH", "day", fund="leisure")]
    exp = [L.Expense(TODAY, D("420"), "UAH", "groceries", "food", "молоко", store="АТБ", source="monobank")]
    bal = {"groceries": D("800"), "leisure": D("300"), "goals": D("500"), "safety": D("9000")}
    return R.build_report(kind, TODAY, pays, exp, bal)


def test_report_always_contains_planned_block_and_totals():
    r = _sample_report()
    md = R.to_markdown(r)
    assert "## Заплановано (завжди)" in md
    assert "Наступні 30 днів" in md
    eva = _sample_report("eva")
    assert "planned_header" in eva and "## Заплановано (завжди)" in R.to_markdown(eva)
    assert eva["sources"] == []  # Єві — без списку джерел


def test_report_has_no_safety_as_source_and_notes_say_observer_only():
    r = _sample_report()
    assert any("не є джерелом" in n for n in r["notes"])
    assert all(f["id"] != "x" for f in r["funds"])


@pytest.mark.parametrize("fmt", ["md", "xlsx", "docx", "pdf", "pptx"])
def test_every_export_format_writes_a_file(tmp_path, fmt):
    p = R.export(_sample_report(), fmt, tmp_path)
    assert p.exists() and p.stat().st_size > 500
    assert p.suffix == f".{fmt}"


def test_obsidian_requires_configured_vault(tmp_path):
    with pytest.raises(PermissionError):
        R.export(_sample_report(), "obsidian", tmp_path, vault_dir=None)
    p = R.export(_sample_report(), "obsidian", tmp_path, vault_dir=tmp_path / "vault")
    assert p.is_file() and "Fin" in p.parts


def test_external_sinks_blocked_without_grant():
    for sink in ("google_sheets", "google_docs", "google_drive"):
        assert R.external_sink_status(sink)["status"] == "blocked_not_granted"
