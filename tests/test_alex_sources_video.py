"""Alex's sources and videos, Eva's analysis and Drive tidying (19.11.2026)."""

from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import datetime, timezone

import httpx

from src import learning_feeds, material_markdown as mm, video_digest

YOUTUBE_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">
 <entry><title>How To Build Muscle</title><link rel="alternate" href="https://www.youtube.com/watch?v=abc"/>
  <published>2026-11-18T10:00:00+00:00</published>
  <media:group><media:description>Training volume explained</media:description></media:group></entry>
 <entry><title>Quick tip #shorts</title><link rel="alternate" href="https://www.youtube.com/shorts/xyz"/>
  <published>2026-11-18T10:00:00+00:00</published>
  <media:group><media:description>clip</media:description></media:group></entry>
</feed>"""


def test_a_youtube_feed_gives_its_videos_with_descriptions_and_drops_shorts():
    items = learning_feeds.fresh_items(learning_feeds.parse_feed(YOUTUBE_FEED), datetime(2026, 11, 19, tzinfo=timezone.utc))
    assert items == [{"url": "https://www.youtube.com/watch?v=abc", "title": "How To Build Muscle",
                      "text": "Training volume explained"}]


def test_gemini_watches_a_youtube_link_itself_and_the_note_has_its_moments(tmp_path):
    asked = {}

    def answer(request):
        if "oembed" in request.url.path:
            return httpx.Response(200, json={"title": "Volume 101", "author_name": "Jeff Nippard"})
        body = json.loads(request.content)
        asked["uri"] = body["contents"][0]["parts"][0]["file_data"]["file_uri"]
        asked["model"] = request.url.path
        text = "## Про що\nОб'єм тренувань.\n=== МОМЕНТИ ===\n[00:01:10] 10-20 підходів на тиждень"
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": text}]}}]})

    def no_download(*_args, **_kwargs):
        raise AssertionError("YouTube is watched by Gemini, not downloaded by the server")

    result = asyncio.run(video_digest.digest("https://www.youtube.com/watch?v=abc", "trainer",
                                             {"gemini_api_key": "g", "openrouter_api_key": "o"}, tmp_path,
                                             fetcher=no_download, transport=httpx.MockTransport(answer)))
    assert result["status"] == "ok" and result["text_from"] == "gemini" and "gemini-4-hydrogen" in asked["model"]
    assert asked["uri"] == "https://www.youtube.com/watch?v=abc"
    note = (tmp_path / result["note"]).read_text(encoding="utf-8")
    assert "Об'єм тренувань" in note and '"channel": "Jeff Nippard"' in note
    moments = next(tmp_path.rglob("*.розшифровка.md")).read_text(encoding="utf-8")
    assert "10-20 підходів" in moments


def test_long_material_gets_an_analysis_on_top_and_a_failure_keeps_the_card(tmp_path):
    reply = {"choices": [{"message": {"content": "## Про що\nСпред і плече."}}]}
    ok = httpx.MockTransport(lambda request: httpx.Response(200, json=reply))
    body = {"status": "ok", "kind": "document", "text": "x" * 3000, "by": "text"}
    analysed = asyncio.run(mm.with_analysis(body, "k", ok))
    assert analysed["analysis"].startswith("## Про що")
    short = {"status": "ok", "kind": "document", "text": "коротко", "by": "text"}
    assert "analysis" not in asyncio.run(mm.with_analysis(short, "k", ok))
    down = httpx.MockTransport(lambda request: httpx.Response(500))
    assert "analysis" not in asyncio.run(mm.with_analysis(body, "k", down))
    path = tmp_path / "a.txt"
    path.write_text("x", encoding="utf-8")
    card = mm.render(path, analysed, {"title": "Форекс"}, "drive")
    assert card.index("## Про що") < card.index("## Повний текст")


def test_a_confirmed_drive_original_is_moved_into_syndicate_by_the_obsidian_path(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    folder = tmp_path / "Сем" / "Матеріали"
    (folder / "Форекс").mkdir(parents=True)
    path = folder / "Форекс" / "a.txt"
    path.write_bytes(b"text")
    mirrored = {"d1": {"path": "a.txt", "version": hashlib.md5(b"text").hexdigest()}}
    moved = []

    async def yes(_file_id):
        return True

    async def mover(file_id, parts):
        moved.append((file_id, parts))
        return True

    state = {"files": {"Форекс/a.txt": {"path": "Форекс/a.txt", "topic": "Форекс"}}}
    asyncio.run(mm.convert_folder(folder, state, {}, mirrored, yes, None, mover, ("Сем", "Матеріали")))
    assert moved == [("d1", ("Сем", "Матеріали", "Форекс"))] and not path.exists()
