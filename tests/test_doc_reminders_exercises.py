from datetime import datetime

from src.agents import doc_exercises
from src.agents.doc_reminders import KYIV, due_slots, format_metric, reminder_text, validate_supplement

ALLOWED = {"13:10", "19:10"}


def test_slots_fire_at_1310_and_1910_kyiv_once_each() -> None:
    assert due_slots(datetime(2026, 10, 10, 12, 0, tzinfo=KYIV), []) == []
    assert due_slots(datetime(2026, 10, 10, 13, 10, tzinfo=KYIV), []) == ["13:10"]
    assert due_slots(datetime(2026, 10, 10, 20, 0, tzinfo=KYIV), ["13:10"]) == ["19:10"]
    assert due_slots(datetime(2026, 10, 10, 20, 0, tzinfo=KYIV), ["13:10", "19:10"]) == []


def test_no_supplements_means_no_invented_reminder() -> None:
    assert reminder_text([], "13:10")["status"] == "not_configured"


def test_reminder_lists_only_matching_slot() -> None:
    sups = [{"name": "Вітамін D", "dose": "2000 IU", "slots": ["13:10"], "timing": "з їжею",
             "interaction_check": "done"}]
    r = reminder_text(sups, "13:10")
    assert r["status"] == "ok" and "Вітамін D" in r["text"]
    assert reminder_text(sups, "19:10")["status"] == "nothing_scheduled"


def test_supplement_needs_interaction_check() -> None:
    s = {"name": "X", "dose": "1", "slots": ["13:10"], "interaction_check": "pending"}
    assert validate_supplement(s, set(ALLOWED)) == "interaction_check_pending"
    s["interaction_check"] = "done"
    assert validate_supplement(s, set(ALLOWED)) is None


def test_metric_shown_as_number_zone_is_extra() -> None:
    assert format_metric("HRV", 58, "мс", zone="зелена") == "HRV: 58 мс (зелена)"
    assert format_metric("HRV", None, "мс") == "HRV: немає даних"


def test_exercise_library_search_on_vendored_data() -> None:
    db = doc_exercises.load_exercises()
    assert len(db) == 876
    assert all("images" not in e for e in db)
    hits = doc_exercises.search(db, muscle="abdominals", level="beginner", limit=3)
    assert 0 < len(hits) <= 3 and all(h["level"] == "beginner" for h in hits)
