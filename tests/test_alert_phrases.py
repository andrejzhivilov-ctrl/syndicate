"""Eva's air-raid notifications from the operator's phrase bank (29.10)."""
from __future__ import annotations

import random

from src.alert_phrases import (
    CLEAR_AFTER_RED,
    CLEAR_AFTER_YELLOW,
    PARTIAL_NOTE,
    RED,
    YELLOW,
    AlertTracker,
    PhraseBag,
)


def _tracker(seed: int = 7) -> AlertTracker:
    bag = PhraseBag({"yellow": YELLOW, "red": RED, "clear_after_red": CLEAR_AFTER_RED,
                     "clear_after_yellow": CLEAR_AFTER_YELLOW}, rng=random.Random(seed))
    return AlertTracker(bag)


def test_each_phrase_once_before_repeats_and_never_twice_in_a_row():
    bag = PhraseBag({"red": RED}, rng=random.Random(1))
    drawn = [bag.draw("red") for _ in range(len(RED) * 5)]
    for start in range(0, len(drawn), len(RED)):
        assert sorted(drawn[start:start + len(RED)]) == sorted(RED)
    assert all(a != b for a, b in zip(drawn, drawn[1:]))


def test_yellow_then_all_clear_is_calm():
    t = _tracker()
    assert t.update("N") is None  # baseline after a restart: no message
    yellow = t.update("Y")
    assert yellow.startswith("🟡 ") and yellow[2:] in YELLOW
    clear = t.update("N")
    assert clear.startswith("🟢 ") and clear[2:] in CLEAR_AFTER_YELLOW


def test_red_alert_ends_with_shot_down_all_clear_even_after_easing_to_yellow():
    t = _tracker()
    t.update("N")
    assert t.update("Y").startswith("🟡 ")
    red = t.update("R")
    assert red.startswith("🔴 ") and red[2:] in RED
    assert t.update("Y") is None  # red eased to yellow: no new alarm
    clear = t.update("N")
    assert clear[2:] in CLEAR_AFTER_RED


def test_partial_alert_is_marked_and_same_level_is_not_repeated():
    t = _tracker()
    t.update("N")
    partial = t.update("P")
    assert partial.startswith("🟡 ") and partial.endswith(PARTIAL_NOTE)
    assert t.update("Y") is None and t.update("P") is None


def test_unknown_or_missing_readings_never_announce_anything():
    t = _tracker()
    assert t.update("R") is None  # first reading only sets the baseline
    for junk in (None, "", "A", "?", " "):
        assert t.update(junk) is None
    assert t.update("N").startswith("🟢 ")  # the alert seen before the junk still ends properly
