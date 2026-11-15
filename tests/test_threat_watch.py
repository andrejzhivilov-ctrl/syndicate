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


def test_a_sign_only_where_the_message_names_a_settlement_and_no_direction():
    # Operator, 15.11.2026: «напрямки прибрати, оті стрілочки взагалі».
    assert tw.marker(KABS, "9") is None  # an oblast alone is no place for a pin
    kozelets = tw.marker(KOZELETS, "25")
    assert kozelets.kind == "jet" and abs(kozelets.lon - 31.11) < 0.05
    assert not hasattr(kozelets, "origin")
    assert tw.marker(BEREZNA, "25") and tw.marker(KHARKIV, "22") and tw.marker(KOROSTEN, "10")
    assert tw.kind_of(KABS) == "kab" and tw.kind_of("🚀 Київ: Бандероль в напрямку міста") == "missile"
    assert tw.kind_of("🛵 БпЛА в напрямку м.Запоріжжя з півдня") == "drone"  # a Shahed
    assert tw.kind_of(KHARKIV) == "jet" and tw.kind_of("Реактивний БпЛА на Сумщину") == "jet"


def test_country_wide_warnings_go_at_once_as_an_urgent_notice_whatever_the_choice(tmp_path, monkeypatch):
    # Operator, 15.11.2026: «очікувану масовану атаку … окремим повідомленням … НЕГАЙНЕ ПОВІДОМЛЕННЯ».
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    warning = "⚠ Увага! Зліт МіГ-31К! Загроза застосування ракет по всій території України!"
    assert tw.is_urgent(warning) and tw.is_urgent("Загроза масованої атаки сьогодні вночі")
    assert tw.is_urgent("Фіксуємо пуски крилатих ракет з Ту-95МС")
    assert not tw.is_urgent(KABS) and not tw.is_urgent(KOZELETS)
    for chosen in (None, ["332"]):
        gateway = _Gateway()
        watch = tw.ThreatWatch(gateway, "alice", _Alerts(), transport=_page((1, KABS)))
        tw._save_last(1)
        watch._transport = _page((1, KABS), (2, warning))
        asyncio.run(watch.run_once(chosen, now=5000.0))
        assert gateway.sent[0] == f"❗❗❗ НЕГАЙНЕ ПОВІДОМЛЕННЯ ❗❗❗\n{warning}"  # no link (15.11)
        assert all("НЕГАЙНЕ" not in text for text in gateway.sent[1:])  # never repeated as an ordinary quote


def test_first_read_sets_the_mark_then_new_posts_are_quoted_with_a_map(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    tw._markers.clear()
    tw._live.update(at=0.0, data=None)  # no NEPTUN snapshot left from another test
    gateway = _Gateway()
    watch = tw.ThreatWatch(gateway, "alice", _Alerts(), transport=_page((10, KABS)))
    assert asyncio.run(watch.run_once(["332"], now=1000.0)) == 0 and gateway.sent == []  # old posts stay old

    watch._transport = _page((10, KABS), (11, KOZELETS), (12, "🛵 БпЛА на Дніпро з півночі"))
    assert asyncio.run(watch.run_once(["332"], now=1060.0)) == 1
    card = gateway.sent[0].split("\n")  # 15.11: a card, then its picture with no caption
    assert card[0] == "⚠️ УВАГА! ЗАГРОЗА" and card[1].startswith("📍 м. Дніпро")
    assert card[2] == "🛵 БпЛА на Дніпро з півночі" and card[3].startswith("💬 ") and len(gateway.sent) == 1
    png, caption = gateway.photos[0]
    assert png.startswith(b"\x89PNG") and caption == ""
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
    assert "🏍 Чернігівська, Харківська, Житомирська, Київська" in text and "💣 Донецька" in text
    assert "/regions" in text and gateway.photos == []
    watch._transport = _page((6, "💣 КАБи на Сумщину"))
    asyncio.run(watch.run_once(None, now=1120.0))
    assert len(gateway.sent) == 1  # gathered, not sent yet
    asyncio.run(watch.run_once(None, now=1060.0 + tw.SUMMARY_GAP_S))
    assert len(gateway.sent) == 2 and "💣 Сумська" in gateway.sent[1]
    assert tw.watched_oblasts(None) == [] and tw.watched_oblasts(["332", "1293"]) == ["22", "9"]
    assert tw.summary([(1, "⚠ Увага! Загроза для прифронтових областей")]) is None  # no place: nothing to list
