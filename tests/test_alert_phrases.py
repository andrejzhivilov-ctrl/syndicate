"""Eva's air-raid notifications from the operator's phrase bank (29.10)."""
from __future__ import annotations

import random

from src.alert_phrases import (
    CLEAR_AFTER_RED,
    CLEAR_AFTER_YELLOW,
    EASE_TO_YELLOW,
    ESCALATE_TO_RED,
    PARTIAL_NOTE,
    POOLS,
    RED,
    YELLOW,
    AlertTracker,
    PhraseBag,
)


def _tracker(seed: int = 7) -> AlertTracker:
    return AlertTracker(PhraseBag(POOLS, rng=random.Random(seed)))


def test_each_phrase_once_before_repeats_and_never_twice_in_a_row():
    bag = PhraseBag({"red": RED}, rng=random.Random(1))
    drawn = [bag.draw("red") for _ in range(len(RED) * 5)]
    for start in range(0, len(drawn), len(RED)):
        assert sorted(drawn[start:start + len(RED)]) == sorted(RED)
    assert all(a != b for a, b in zip(drawn[:-1], drawn[1:], strict=True))


def test_yellow_then_all_clear_is_calm():
    t = _tracker()
    assert t.update("N") is None  # baseline after a restart: no message
    yellow = t.update("Y")
    assert yellow.startswith("🟡 ") and yellow[2:] in YELLOW
    clear = t.update("N")
    assert clear.startswith("🟢 ") and clear[2:] in CLEAR_AFTER_YELLOW


def test_every_level_change_is_announced_with_its_own_phrases():
    t = _tracker()
    t.update("N")
    straight_red = t.update("R")
    assert straight_red.startswith("🔴 ") and straight_red[2:] in RED  # no yellow first
    eased = t.update("Y")
    assert eased.startswith("🟡 ") and eased[2:] in EASE_TO_YELLOW
    escalated = t.update("R")
    assert escalated.startswith("🔴 ") and escalated[2:] in ESCALATE_TO_RED
    t.update("Y")
    clear = t.update("N")
    assert clear[2:] in CLEAR_AFTER_RED  # the alert reached red: "shot down" all-clear


def test_transition_pools_have_ten_to_fifteen_phrases():
    for pool in (ESCALATE_TO_RED, EASE_TO_YELLOW):
        assert 10 <= len(pool) <= 15 and len(set(pool)) == len(pool)


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
