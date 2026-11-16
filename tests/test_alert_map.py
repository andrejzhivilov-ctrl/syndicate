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
    # 15.11: maps go without a caption, so the credits are printed inside the picture.
    png = alert_map.render(lambda _p: "N", "9", (), (), datetime(2026, 11, 15, 9, 37, tzinfo=timezone.utc),
                           "Дані: NEPTUN · neptun.in.ua")
    assert png and png.startswith(b"\x89PNG")


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

    png = alert_map.render(lambda _p: "R", "9", [], [Marker("kab", 35.0, 48.4), Marker("drone", 35.9, 48.5), Marker("jet", 34.6, 48.1),
                                                         Marker("missile", 33.4, 47.9)])
    assert png and png.startswith(b"\x89PNG")


def _docx(path, rows):
    """A minimal .docx with one table, like the TOT annexes on zakon.rada.gov.ua."""
    import zipfile

    w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    cells = "".join("<w:tr>" + "".join(f"<w:tc><w:p><w:r><w:t>{c}</w:t></w:r></w:p></w:tc>" for c in row) + "</w:tr>"
                    for row in rows)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", f'<w:document xmlns:w="{w}"><w:body><w:tbl>{cells}</w:tbl></w:body></w:document>')


def test_only_settlements_occupied_now_count_and_whole_communities_are_told_apart(tmp_path):
    # Operator, 15.11.2026: occupied areas from the official list; an end date means liberated.
    from tools import build_occupied as bo

    occ = "Тимчасово окупована Російською Федерацією територія України"
    _docx(tmp_path / "a.docx", [
        ["область", "район", "громада", "пункт", "код", "тип", "початок", "кінець", "так/ні"],
        ["Донецька", "Бахмутський", "Бахмутська", "с. Андріївка", "UA14020010030085322", occ, "30.11.2022", "14.09.2023", "Ні"],
        ["Донецька", "Бахмутський", "Бахмутська", "м. Бахмут", "UA14020010010012345", occ, "20.05.2023", "", "Ні"],
        ["Донецька", "Донецький", "Донецька", "м. Донецьк", "UA14060010010054321", occ, "07.04.2014", "", "Ні"],
        ["Дніпропетровська", "Криворізький", "Грушівська", "с. Грушівка", "UA12060090010097136",
         "Територія можливих бойових дій", "27.09.2024", "", "Так"],
    ])
    occupied = bo.occupied_now(bo.table_rows(tmp_path / "a.docx"))
    assert occupied == {"UA1402001001", "UA1406001001"}  # Андріївка was liberated; Грушівка never occupied
    settlements = [{"properties": {"adm3_pcode": code[:9], "adm4_pcode": code}}
                   for code in ("UA1402001001", "UA1402001003", "UA1406001001")]
    whole, partial = bo.split(settlements, occupied)
    assert whole == {"UA1406001"} and partial == {"UA1402001001"}


def test_occupied_areas_are_painted_dark_burgundy_over_any_level():
    from io import BytesIO

    from PIL import Image

    assert alert_map.occupied(), "src/alert_occupied.json is part of the repository"
    png = alert_map.render(lambda _p: "R", "28")
    image = Image.open(BytesIO(png)).convert("RGB")
    canvas = alert_map._Canvas(alert_map._view("28"))
    points = [(38.20, 47.50), (37.95, 47.75), (38.45, 47.80), (37.70, 47.45), (38.60, 48.10)]  # occupied since 2014
    hits = sum(image.getpixel((int(canvas.xy(*p)[0] / alert_map.SCALE), int(canvas.xy(*p)[1] / alert_map.SCALE)))
               == alert_map.OCCUPIED for p in points)
    assert hits >= 3  # a label or a border may cover a point, the area stays burgundy
