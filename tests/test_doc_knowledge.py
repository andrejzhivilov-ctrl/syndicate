from datetime import date
from decimal import Decimal as D

from src.agents import doc_buttons as DB
from src.agents import doc_knowledge as K
from src.agents import doc_nutrition as N


def test_no_medical_values_are_invented():
    out = N.energy_and_macros({"weight_kg": 80, "height_cm": None, "age": None,
                               "sex": None, "activity": None})
    assert out["status"] == "not_configured"
    assert set(out["missing"]) == {"height_cm", "age", "sex", "activity"}


def test_mifflin_bmr_and_tdee_worked_example():
    # 80 кг, 180 см, 30 років, чоловік: 10*80 + 6.25*180 − 5*30 + 5 = 1780
    assert N.bmr_mifflin_st_jeor(D("80"), D("180"), 30, "male") == D("1780")
    out = N.energy_and_macros({"weight_kg": 80, "height_cm": 180, "age": 30,
                               "sex": "male", "activity": "moderate"})
    assert out["status"] == "ok" and out["tdee_kcal"] == "2759"
    assert out["protein_g"] == "160" and out["fat_g"] == "80" and out["water_ml"] == "2800"
    # вуглеводи — залишок калорій: (2759 − 640 − 720) / 4 = 350
    assert out["carb_g"] == "350"


def test_bad_activity_and_sex_are_rejected_not_guessed():
    base = {"weight_kg": 80, "height_cm": 180, "age": 30, "sex": "male", "activity": "couch"}
    assert N.energy_and_macros(base)["status"] == "rejected"
    base.update(activity="light", sex="other")
    assert N.energy_and_macros(base)["status"] == "rejected"


def test_readiness_zones_match_dossier():
    assert N.readiness_zone(70) == "green" and N.readiness_zone(69.9) == "yellow"
    assert N.readiness_zone(45) == "yellow" and N.readiness_zone(44.9) == "red"
    assert N.readiness_zone(None) == "not_configured"


def test_pseudoscience_is_rejected():
    r = K.admit_fact({"domain": "nutrition_recipes", "claim": "Детокс-крапельниці чистять печінку",
                      "source_type": "blog"})
    assert r["status"] == "rejected" and r["reason"] == "pseudoscience_marker"


def test_medical_claim_needs_tier_ab_or_andrii():
    base = {"domain": "evidence_research", "claim": "Магній покращує сон у дорослих",
            "source_type": "youtube", "medical": True}
    assert K.admit_fact(base)["status"] == "pending_review"
    ok = dict(base, source_type="pubmed", evidence_level="1A", source_url="https://pubmed.ncbi.nlm.nih.gov/1")
    assert K.admit_fact(ok)["status"] == "admitted"
    assert K.admit_fact(dict(base, verified_by="andrii"))["status"] == "admitted"


def test_labeled_vault_file_is_read_only_for_doc_unlabeled_follows_medical_rules():
    labeled = K.admit_fact({"domain": "andrii_medical_vault", "claim": "аналіз", "source_type": "book",
                            "target_labeled": True})
    assert labeled["status"] == "rejected" and labeled["reason"] == "labeled_file_read_only_for_doc"
    unlabeled = K.admit_fact({"domain": "andrii_medical_vault", "claim": "аналіз", "source_type": "book"})
    assert unlabeled["status"] == "pending_review"  # медичний контекст: потрібна оцінка A/B або Андрій


def test_refresh_only_from_allowed_hosts_and_on_sunday():
    assert K.refresh_host_allowed("https://pubmed.ncbi.nlm.nih.gov/12345")
    assert not K.refresh_host_allowed("https://random-blog.example/diet")
    assert K.weekly_refresh_due(date(2026, 10, 11))  # неділя
    assert not K.weekly_refresh_due(date(2026, 10, 10))


def test_medical_card_is_not_configured_until_andrii_verifies():
    assert K.medical_card_status({"blood_type": "A+"}) == "not_configured"
    assert K.medical_card_status({"blood_type": "A+", "verified_by": "andrii"}) == "verified"


def test_doc_buttons_only_for_andrii_and_fit_telegram_limit():
    for menu in DB.MENUS:
        for row in DB.build_keyboard(menu, "andrii")["inline_keyboard"]:
            for b in row:
                assert len(b["callback_data"].encode()) <= 64
    assert DB.build_keyboard("main", "eva") == {"inline_keyboard": []}
    assert DB.handle_callback("rep:full", "andrii")["action"] == "report"
    assert DB.handle_callback("rep:full", "eva") is None
    assert DB.handle_callback("unknown", "andrii") is None
