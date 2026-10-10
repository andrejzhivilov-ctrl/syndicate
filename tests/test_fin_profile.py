"""Fin prepared profile: no grants, no money movement, no payment data."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "agents" / "fin.profile.json"


def _p():
    return json.loads(PROFILE.read_text(encoding="utf-8"))


def test_fin_has_no_grants():
    p = _p()
    assert p["capabilities"] == []
    assert p["resource_scopes"] == []
    assert p["services_enabled"] == []


def test_fin_skills_are_drafts_only():
    skills = _p()["skills"]
    assert len(skills) == 14
    assert all(s["activation"] == "draft" for s in skills)


def test_fin_live_modes_all_off():
    assert all(v is False for v in _p()["live_modes"].values())


def test_fin_money_movement_forbidden_and_no_payment_data():
    p = _p()
    assert p["execution"]["money_movement"] == "forbidden"
    assert p["execution"]["payments"] == "forbidden"
    assert p["execution"]["basket_audit"] == "advisory_only"
    assert p["banking"]["status"] == "not_granted"
    assert p["banking"]["write_allowed"] is False
    assert p["banking"]["payment_data_stored"] is False
    assert p["banking"]["bank_read_grants"] == []  # рішення A: за замовчуванням закрито


def test_fin_token_budget_matches_dossier():
    b = _p()["budgets"]
    assert b["token_daily_limit_usd"] == 5.0
    assert b["warn_ratio"] == 0.8
    assert b["circuit_spike_usd_15m"] == 0.5


def test_fin_proposed_expansions_pending_and_never_items_present():
    pe = _p()["proposed_expansions"]
    assert pe["status"] == "requires_andrii_approval"
    assert len(pe["items"]) == 12
    never_ids = {i["id"] for i in pe["never"]}
    assert never_ids == {"fin.payment_data", "fin.money_write"}


def test_fin_routing_only_eva_and_andrii():
    r = _p()["purchase_flow"]["routing"]
    assert set(r["eva"]) == {"funds_check", "basket_status", "expense_note", "report_request"}
    assert r["andrii"] == ["*"]
    assert r["doc"] == "no_direct_contact_with_fin"


def test_fin_full_report_and_skills_have_code():
    assert all("code" in s for s in _p()["skills"])
    assert "full" in _p()["reports"] and "planned_block" in _p()["reports"]
    assert _p()["funds"]["safety"].startswith("Фонд безпеки")


def test_fin_docs_and_prompt_exist():
    assert (ROOT / _p()["prompt_file"]).is_file()
    for name in ("FIN_PERSONA.md", "FIN_PERMISSIONS.md", "FIN_OPERATING_MODEL.md",
                 "FIN_PURCHASE_FLOW.md", "FIN_DEPLOYMENT_RUNBOOK.md", "FIN_DEPLOYMENT_READINESS.md"):
        assert (ROOT / "fin_core" / name).is_file(), name
