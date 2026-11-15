"""The alert map: borders matched to the Ukraine Alarm tree, and honest gaps (15.11.2026)."""

from __future__ import annotations

from src import alert_map
from tools.build_alert_map import key, simplify


def test_every_oblast_and_top_city_has_a_border_and_the_cities_know_their_oblast():
    shapes = alert_map.shapes()
    assert all(ident in shapes for ident in alert_map.children(None))
    assert alert_map.oblast_of("1293") == "22" and alert_map.oblast_of("564") == "12"  # Харків, Запоріжжя
    assert alert_map.oblast_of("332") == "9"  # м. Дніпро → Дніпропетровська
    assert alert_map.oblast_of("no-such-region") is None


def test_render_draws_a_png_or_nothing_never_a_guessed_shape():
    png = alert_map.render(lambda place: "R" if place == "332" else "N", "9", ["332"])
    assert png and png.startswith(b"\x89PNG")
    assert alert_map.render(lambda _place: "N", "no-such-oblast") is None
    assert alert_map.render(lambda _place: "Y", None).startswith(b"\x89PNG")  # all of Ukraine


def test_caption_says_where_when_in_kyiv_time_and_whose_borders():
    from datetime import datetime, timezone

    text = alert_map.caption("9", datetime(2026, 11, 15, 9, 37, tzinfo=timezone.utc))
    assert text.startswith("🗺️ Дніпропетровська область · стан на 11:37")
    assert text.endswith(alert_map.ATTRIBUTION)


def test_builder_names_and_simplification():
    # Live 15.11.2026: city communities and two renamed districts did not match at first.
    assert key("м. Вінниця та Вінницька територіальна громада") == "вінницька"
    assert key("Вінницька територіальна громада") == "вінницька"
    assert key("Берестинський") == key("Красноградський район")
    assert key("Кам’янська") == key("Кам'янська територіальна громада")
    ring = [[0, 0], [1, 0.0001], [2, 0], [2, 2], [0, 2], [0, 0]]
    assert simplify(ring, 0.01) == [[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]


def test_cities_are_named_on_the_map_largest_first():
    # Operator, 15.11.2026: «щоб населені пункти також прописувались … Дніпро, Павлоград, Самар».
    names = [name for name, _lon, _lat in alert_map.cities("9")]
    assert names[0] in ("Дніпро", "Кривий Ріг") and {"Павлоград", "Самар"} <= set(names)
    assert "Тульчин" in [name for name, _lon, _lat in alert_map.cities("4")]
    assert alert_map.short_name("9") == "Дніпропетровська" and alert_map.short_name("9999") == "А. Р. Крим"


def test_a_guided_bomb_has_its_own_sign():
    from src.alert_map import Marker

    png = alert_map.render(lambda _p: "R", "9", [], [Marker("kab", 35.0, 48.4), Marker("drone", 35.9, 48.5, (35.9, 48.9))])
    assert png and png.startswith(b"\x89PNG")
