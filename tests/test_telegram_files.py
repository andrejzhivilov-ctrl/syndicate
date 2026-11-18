"""Files from the chat: documents, tables, slides and audio are kept, read or transcribed (16.11.2026)."""

from __future__ import annotations

import asyncio
import io

from src import material_reader, telegram_files, video_digest
from src.telegram_gateway import extract_message


def _xlsx() -> bytes:
    from openpyxl import Workbook

    book = Workbook()
    sheet = book.active
    sheet.title = "Харчування"
    sheet.append(["Продукт", "Ккал", "Білок"])
    sheet.append(["Гречка", 343, 13.3])
    sheet["D2"] = "=B2*2"
    out = io.BytesIO()
    book.save(out)
    return out.getvalue()


def _pptx() -> bytes:
    from pptx import Presentation

    deck = Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[1])
    slide.shapes.title.text = "Тренування А"
    slide.placeholders[1].text = "Присід 5x5"
    slide.notes_slide.notes_text_frame.text = "Темп 3-1-1"
    out = io.BytesIO()
    deck.save(out)
    return out.getvalue()


def _update(**message):
    return {"message": {"from": {"id": 1}, "chat": {"id": 1, "type": "private"}, "message_id": 7, **message}}


def test_tables_slides_and_csv_become_text_the_agent_can_read():
    table = material_reader.extract_text("xlsx", _xlsx())
    assert "[аркуш «Харчування»]" in table and "| Гречка | 343 | 13.3 |" in table
    slides = material_reader.extract_text("pptx", _pptx())
    assert "[слайд 1]" in slides and "Присід 5x5" in slides and "Темп 3-1-1" in slides
    rows = material_reader.extract_text("csv", "Продукт;Ккал\nРис;130\n".encode("cp1251"))
    assert "| Рис | 130 |" in rows
    assert {"xlsx", "csv", "pptx"} <= material_reader.EXTENSIONS


def test_a_document_or_audio_file_is_a_file_and_a_voice_note_stays_a_voice_note():
    pdf = extract_message(_update(document={"file_id": "d", "mime_type": "application/pdf",
                                            "file_name": "аналізи.pdf", "file_size": 1000}, caption="глянь"))
    assert pdf["kind"] == "file" and pdf["file_name"] == "аналізи.pdf" and pdf["text"] == "глянь"
    song = extract_message(_update(audio={"file_id": "a", "mime_type": "audio/mpeg", "file_name": "лекція.mp3",
                                          "duration": 3600, "file_size": 9_000_000}))
    assert song["kind"] == "file" and song["mime"] == "audio/mpeg"
    voice = extract_message(_update(voice={"file_id": "v", "duration": 5}))
    assert voice["kind"] == "voice"
    photo_doc = extract_message(_update(document={"file_id": "p", "mime_type": "image/png", "file_name": "x.png"}))
    assert photo_doc["kind"] == "media"


def test_a_file_is_refused_with_the_reason_and_never_cut():
    assert telegram_files.refusal("trainer", {"file_size": 30_000_000, "file_name": "x.pdf"}) == telegram_files.TOO_BIG
    assert "не читаю" in telegram_files.refusal("trainer", {"file_size": 10, "file_name": "x.exe"})
    assert telegram_files.refusal("sam", {"file_size": 10, "file_name": "x.pdf"}) is not None  # 18.11: Eva takes files now
    assert telegram_files.refusal("trainer", {"file_size": 10, "file_name": "x.pptx"}) is None


def test_a_table_is_kept_in_the_materials_folder_and_its_beginning_goes_to_the_agent(tmp_path):
    result = asyncio.run(telegram_files.take("trainer", tmp_path, "раціон.xlsx", "", _xlsx(), {}))
    assert result["status"] == "ok" and result["path"] == "Health_Coach/Матеріали/раціон.xlsx"
    again = asyncio.run(telegram_files.take("trainer", tmp_path, "раціон.xlsx", "", _xlsx(), {}))
    assert again["path"] == "Health_Coach/Матеріали/раціон (2).xlsx"  # nothing is overwritten
    turn = telegram_files.prompt(result, "раціон.xlsx", "")
    assert "Гречка" in turn and "material_read" in turn and "запитай, що з ним зробити" in turn


def test_audio_is_transcribed_next_to_the_file_or_the_reason_is_told(tmp_path, monkeypatch):
    no_key = asyncio.run(telegram_files.take("trainer", tmp_path, "лекція.mp3", "audio/mpeg", b"ID3", {}))
    assert no_key == {"status": "unavailable", "path": "Health_Coach/Матеріали/лекція.mp3", "kind": "audio",
                      "reason": "no_groq_key"}
    assert "не переказуй" in telegram_files.prompt(no_key, "лекція.mp3", "")

    monkeypatch.setattr(video_digest, "to_opus", lambda source, work: [source])

    async def groq(parts, key, transport=None):
        return "[00:00:01] Білок 1.6 г на кілограм."

    monkeypatch.setattr(video_digest, "groq_transcribe", groq)
    heard = asyncio.run(telegram_files.take("trainer", tmp_path, "лекція.mp3", "audio/mpeg", b"ID3",
                                            {"groq_api_key": "k"}))
    assert heard["status"] == "ok" and heard["transcript"].endswith("лекція (2).mp3.розшифровка.md")
    assert "Білок 1.6 г" in (tmp_path / heard["transcript"]).read_text(encoding="utf-8")
