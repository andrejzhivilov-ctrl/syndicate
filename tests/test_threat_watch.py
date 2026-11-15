"""Air Force messages about the chosen oblast, quoted, with signs on the map (15.11.2026)."""

from __future__ import annotations

import asyncio

import httpx

from src import threat_watch as tw

# Real posts of @kpszsu, 15.11.2026.
KOZELETS = "🏍 Чернігівщина: Реактивний БпЛА курсом на Олишівку/Козелець."
BEREZNA = "🏍 Чернігівщина: Реактивний БпЛА повз н.п.Березна курсом на південь"
KABS = "💣 КАБи на Дніпропетровщину"
KHARKIV = "🏍 Харків: Ударний БпЛА курсом на місто з півночі"
KOROSTEN = "🏍 Реактивний БпЛА з Київщини на Житомирщину (Коростень)"


def _page(*posts):
    body = "".join(f'<div data-post="kpszsu/{n}"><div class="tgme_widget_message_text js-message_text" '
                   f'dir="auto">{text}</div></div>' for n, text in posts)
    return httpx.MockTransport(lambda _request: httpx.Response(200, text=f"<html>{body}</html>"))


class _Gateway:
    def __init__(self):
        self.sent, self.photos = [], []

    async def owner_user_id(self):
        return "1"

    async def send(self, bot, chat, text):
        self.sent.append(text)
        return True

    async def send_photo(self, bot, chat, png, caption=""):
        self.photos.append((png, caption))
        return True


class _Alerts:
    @staticmethod
    def level_of(_place):
        return "N"


def test_posts_are_matched_to_oblasts_by_name_or_settlement():
    assert tw.concerns(KABS, "9") and not tw.concerns(KABS, "22")
    assert tw.concerns(KHARKIV, "22")  # a city of the oblast, no oblast named
    assert tw.concerns(KOROSTEN, "10") and tw.concerns(KOROSTEN, "14")  # from Київщина to Житомирщина
    assert not tw.concerns(KOZELETS, "9")  # another oblast is named: its villages are not ours


def test_a_sign_only_where_the_message_names_a_settlement_with_its_direction():
    assert tw.marker(KABS, "9") is None  # an oblast alone is no place for a pin
    kozelets = tw.marker(KOZELETS, "25")
    assert kozelets.kind == "drone" and abs(kozelets.lon - 31.11) < 0.05 and kozelets.origin is None
    berezna = tw.marker(BEREZNA, "25")
    assert berezna.origin[1] > berezna.lat  # heading south: it comes from the north
    kharkiv = tw.marker(KHARKIV, "22")
    assert kharkiv.origin[1] > kharkiv.lat  # «з півночі»
    korosten = tw.marker(KOROSTEN, "10")
    assert korosten.origin[0] > korosten.lon  # from Київщина, east of Коростень
    assert tw.kind_of(KABS) == "kab" and tw.kind_of("🚀 Київ: Бандероль в напрямку міста") == "missile"


def test_first_read_sets_the_mark_then_new_posts_are_quoted_with_a_map(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    tw._markers.clear()
    gateway = _Gateway()
    watch = tw.ThreatWatch(gateway, "alice", _Alerts(), transport=_page((10, KABS)))
    assert asyncio.run(watch.run_once(["332"], now=1000.0)) == 0 and gateway.sent == []  # old posts stay old

    watch._transport = _page((10, KABS), (11, KOZELETS), (12, "🛵 БпЛА на Дніпро з півночі"))
    assert asyncio.run(watch.run_once(["332"], now=1060.0)) == 1
    assert gateway.sent == ["🛰️ Повітряні сили:\n🛵 БпЛА на Дніпро з півночі\nhttps://t.me/kpszsu/12"]
    png, caption = gateway.photos[0]
    assert png.startswith(b"\x89PNG") and caption.endswith(tw.NOTE)
    assert len(tw.recent_markers("9", now=1060.0)) == 1 and tw.recent_markers("9", now=1060.0 + tw.MARKER_TTL_S) == []

    # Busy night: the quotes keep coming, the map at most every MAP_GAP_S.
    watch._transport = _page((13, KABS))
    asyncio.run(watch.run_once(["332"], now=1100.0))
    assert len(gateway.sent) == 2 and len(gateway.photos) == 1


def test_no_choice_gives_a_short_list_of_oblasts_at_most_every_five_minutes(tmp_path, monkeypatch):
    # Operator, 15.11.2026: «коли не вибраний регіон, вона може просто давати список областей».
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    gateway = _Gateway()
    watch = tw.ThreatWatch(gateway, "alice", _Alerts(), transport=_page((1, KABS)))
    assert asyncio.run(watch.run_once(None, now=1000.0)) == 0 and gateway.sent == []  # first read: the mark only
    watch._transport = _page((1, KABS), (2, KOZELETS), (3, KHARKIV), (4, KOROSTEN), (5, "💣 КАБи на Донеччину"))
    assert asyncio.run(watch.run_once(None, now=1060.0)) == 4
    text = gateway.sent[0]
    assert "🛵 Чернігівська, Харківська, Житомирська, Київська" in text and "💣 Донецька" in text
    assert "/regions" in text and gateway.photos == []
    watch._transport = _page((6, "💣 КАБи на Сумщину"))
    asyncio.run(watch.run_once(None, now=1120.0))
    assert len(gateway.sent) == 1  # gathered, not sent yet
    asyncio.run(watch.run_once(None, now=1060.0 + tw.SUMMARY_GAP_S))
    assert len(gateway.sent) == 2 and "💣 Сумська" in gateway.sent[1]
    assert tw.watched_oblasts(None) == [] and tw.watched_oblasts(["332", "1293"]) == ["22", "9"]
    assert tw.summary([(1, "⚠ Увага! Загроза для прифронтових областей")]) is None  # no place: nothing to list
