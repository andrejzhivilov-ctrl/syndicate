"""Water notices from verified Telegram channels, through Alice, marked 🚰."""

from __future__ import annotations

import asyncio

import httpx

from src import water_outages as wo


def _page(*posts):
    blocks = []
    for number, text in posts:
        body = f'<div class="tgme_widget_message_text js-message_text" dir="auto">{text}</div>' if text else ""
        blocks.append(f'<div class="tgme_widget_message" data-post="vinvoda_info/{number}">{body}'
                      f'<time datetime="2026-11-14T10:00:00+00:00"></time></div>')
    return "<html>" + "".join(blocks) + "</html>"


def test_posts_keep_each_text_with_its_own_post():
    page = _page((10, "Добрий день"), (11, ""), (12, "Без води<br>залишиться вул. Келецька"))
    assert wo.posts(page) == [("vinvoda_info", 10, "Добрий день"), ("vinvoda_info", 11, ""),
                              ("vinvoda_info", 12, "Без води\nзалишиться вул. Келецька")]


def test_only_water_outages_pass_the_filter():
    assert wo.about_water("Через аварію буде припинено водопостачання на вул. Пирогова")
    assert wo.about_water("Низький тиск води у мікрорайоні Вишенька")
    assert not wo.about_water("Голова ОВА провів нараду щодо опалювального сезону")
    assert not wo.about_water("Вода — джерело життя")  # water, but no outage


def test_first_read_sets_the_mark_then_only_new_water_posts_are_sent_once(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    asyncio.run(wo.reply("Вінницька"))
    pages = {"vinvoda_info": _page((10, "Аварія, немає води на Замостю")), "VinnytsiaODA": _page()}

    def handler(request):
        return httpx.Response(200, text=pages[request.url.path.rsplit("/", 1)[1]])

    transport = httpx.MockTransport(handler)
    assert asyncio.run(wo.new_notices("Вінницька", transport)) == []  # old posts are not news
    pages["vinvoda_info"] = _page((10, "Аварія, немає води на Замостю"), (11, "Новини підприємства"),
                                  (12, "Припинено водопостачання на вул. Келецька до 18:00"))
    sent = asyncio.run(wo.new_notices("Вінницька", transport))
    assert len(sent) == 1 and sent[0].startswith("🚰 ") and "📍 Вінницька\n" in sent[0]
    assert "t.me" not in sent[0] and "@vinvoda_info" not in sent[0]  # 15.11: no channel, no link
    assert asyncio.run(wo.new_notices("Вінницька", transport)) == []


def test_water_is_news_only_when_its_state_changes(tmp_path, monkeypatch):
    # Operator, 15.11.2026: «навіть якщо зміни написали, але статус не змінився, то присилати не потрібно».
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    asyncio.run(wo.reply("Вінницька"))
    pages = {"vinvoda_info": _page((1, "Новини підприємства")), "VinnytsiaODA": _page()}
    transport = httpx.MockTransport(lambda r: httpx.Response(200, text=pages[r.url.path.rsplit("/", 1)[1]]))
    asyncio.run(wo.new_notices("Вінницька", transport))
    pages["vinvoda_info"] = _page((2, "Аварія, немає води на Замостю"), (3, "Оновлення: аварія на Замостю, води немає"))
    assert len(asyncio.run(wo.new_notices("Вінницька", transport))) == 1  # the update says the same: one message
    pages["vinvoda_info"] = _page((4, "Подачу води на Замостю відновлено"))
    assert "відновлено" in asyncio.run(wo.new_notices("Вінницька", transport))[0]
    pages["vinvoda_info"] = _page((5, "Водопостачання відновлено повністю"))
    assert asyncio.run(wo.new_notices("Вінницька", transport)) == []  # still on: no news
    assert wo.status_of("Припинено водопостачання до 18:00") == "off"


def test_missing_regions_and_lookalikes_are_never_guessed(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    assert asyncio.run(wo.reply("Сумська"))["status"] == "unavailable"
    every = {channel.lower() for channels in wo.CHANNELS.values() for channel in channels}
    assert "sumy_oda" not in every  # a Russian-named lookalike found on 14.11.2026
    assert "Не знайшов" in asyncio.run(wo.reply("Атлантида"))["reply"]
    assert "Чернівецька" in asyncio.run(wo.reply("список"))["reply"]


def test_a_chosen_place_filters_administration_posts_but_not_the_water_utility(tmp_path, monkeypatch):
    """14.11.2026: /voda <region> <city or community>; the utility's own posts always count."""
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    asyncio.run(wo.reply("Вінницька Жмеринка"))
    assert wo.relevant("VinnytsiaODA", "У Жмеринці аварія: немає води до вечора")
    assert not wo.relevant("VinnytsiaODA", "У Тульчині аварія: немає води до вечора")
    assert wo.relevant("vinvoda_info", "Аварія, немає води на вул. Келецькій")
    assert wo.stems("Вінниця") == ["вінни"]
