"""Regression tests for Eva's explicit-save and secret-refusal rules."""

from __future__ import annotations

from src.agents.eva_memory_policy import EvaMemoryPolicy, MemoryDisposition


def test_ordinary_chat_is_not_long_term_memory() -> None:
    decision = EvaMemoryPolicy().evaluate("Сьогодні обговорили кілька ідей.", explicit_save_request=False)
    assert decision.disposition is MemoryDisposition.IGNORE
    assert decision.reason_code == "no_explicit_save_request"


def test_explicit_low_sensitivity_memory_request_can_be_archived() -> None:
    decision = EvaMemoryPolicy().evaluate(
        "Для звітів Obsidian є канонічним архівом.", explicit_save_request=True
    )
    assert decision.disposition is MemoryDisposition.ARCHIVE


def test_health_or_psychology_memory_is_a_review_draft() -> None:
    decision = EvaMemoryPolicy().evaluate(
        "Запам'ятай: я проходжу психологічну терапію.", explicit_save_request=True
    )
    assert decision.disposition is MemoryDisposition.DRAFT
    assert decision.reason_code == "sensitive_topic_review_required"


def test_personal_identifiers_are_not_written_automatically() -> None:
    decision = EvaMemoryPolicy().evaluate(
        "Запам'ятай мою пошту: andrii@example.com", explicit_save_request=True
    )
    assert decision.disposition is MemoryDisposition.DRAFT
    assert decision.reason_code == "personal_identifier_review_required"


def test_secret_like_input_is_rejected_without_returning_the_value() -> None:
    secret = "ghp_abcdefghijklmnopqrstuvwxyz0123456789"
    policy = EvaMemoryPolicy()
    decision = policy.evaluate(f"Запам'ятай token={secret}", explicit_save_request=True)
    assert decision.disposition is MemoryDisposition.REJECT
    assert decision.reason_code == "secret_like_content"
    assert secret not in decision.reason_code


def test_secret_detector_covers_bearer_and_password_assignments() -> None:
    policy = EvaMemoryPolicy()
    assert policy.contains_secret_like_value("Authorization: Bearer abcdef0123456789abcdef")
    assert policy.contains_secret_like_value("password=hunter2-with-enough-length")
    assert not policy.contains_secret_like_value("Як зберегти API key безпечно?")


def test_unrequested_or_generated_candidate_cannot_be_archived() -> None:
    decision = EvaMemoryPolicy().evaluate("Єва припускає, що зустріч о десятій.", explicit_save_request=False)
    assert decision.disposition is MemoryDisposition.DRAFT
    assert decision.reason_code == "uncertain_sensitive_or_policy_review_required"


def test_gps_and_geolocation_content_is_never_stored() -> None:
    policy = EvaMemoryPolicy()
    decision = policy.evaluate("Запам'ятай GPS координати: 48.45, 35.05", explicit_save_request=True)
    assert decision.disposition is MemoryDisposition.REJECT
    assert decision.reason_code == "location_data_not_stored"


def test_coordinates_and_addresses_are_detected_without_location_labels() -> None:
    policy = EvaMemoryPolicy()
    assert policy.contains_location_data("48.45123, 35.04123")
    assert policy.contains_location_data("домашня адреса: вулиця Прикладна, 10")
    assert policy.contains_location_data("Я живу в Дніпрі.")


def test_third_party_and_advice_content_requires_review() -> None:
    decision = EvaMemoryPolicy().evaluate(
        "Запам'ятай: my friend should call the clinic.", explicit_save_request=True
    )
    assert decision.disposition is MemoryDisposition.DRAFT
    assert decision.reason_code == "uncertain_sensitive_or_policy_review_required"


def test_low_sensitivity_nightly_summary_is_allowed_only_in_nightly_mode() -> None:
    policy = EvaMemoryPolicy()
    summary = "The user explicitly chose Obsidian as the canonical project archive."
    assert policy.evaluate(summary, explicit_save_request=False).disposition is MemoryDisposition.IGNORE
    decision = policy.evaluate(summary, explicit_save_request=False, nightly_summary=True)
    assert decision.disposition is MemoryDisposition.ARCHIVE
    assert decision.reason_code == "low_sensitivity_nightly_summary"
