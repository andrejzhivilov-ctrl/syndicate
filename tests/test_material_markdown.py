"""Materials become Markdown; the original leaves the server only once it is safe on Drive (18.11.2026)."""

from __future__ import annotations

import asyncio
import hashlib
import io

from src import material_markdown as mm
from src import material_sorter, media_vision


def _shelf(tmp_path, name, data):
    folder = tmp_path / "Сем" / "Матеріали"
    (folder / "Форекс").mkdir(parents=True)
    path = folder / "Форекс" / name
    path.write_bytes(data)
    state = {"files": {f"Форекс/{name}": {"path": f"Форекс/{name}", "topic": "Форекс", "title": "Основи форексу",
                                           "summary": "Що таке спред і плече", "language": "uk"}}}
    return folder, path, state


async def _yes(_file_id):
    return True


async def _no(_file_id):
    return False


def test_a_drive_file_becomes_a_card_and_leaves_the_server_once_drive_confirms(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    folder, path, state = _shelf(tmp_path, "форекс.txt", "Спред — різниця між bid і ask.".encode())
    mirrored = {"drive-1": {"path": "форекс.txt", "version": hashlib.md5(path.read_bytes()).hexdigest()}}
    done = asyncio.run(mm.convert_folder(folder, state, {}, mirrored, _yes, None))
    card = (folder / "Форекс" / "форекс.txt.md").read_text(encoding="utf-8")
    assert done[0]["removed_from_server"] and not path.exists()
    assert 'summary: "Що таке спред і плече"' in card and "drive.google.com/file/d/drive-1" in card
    assert "Спред — різниця між bid і ask." in card and "# Основи форексу" in card
    catalog = material_sorter.render_catalog(folder, state)
    assert "[[Форекс/форекс.txt.md]]" in catalog  # the catalog points at the card now


def test_an_original_stays_when_drive_does_not_confirm_it(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    folder, path, state = _shelf(tmp_path, "a.txt", b"text")
    mirrored = {"drive-1": {"path": "a.txt", "version": hashlib.md5(b"text").hexdigest()}}
    done = asyncio.run(mm.convert_folder(folder, state, {}, mirrored, _no, None))
    assert path.exists() and not done[0]["removed_from_server"]
    assert "не підтверджено" in (folder / "Форекс" / "a.txt.md").read_text(encoding="utf-8")


def test_a_chat_file_is_uploaded_first_and_kept_if_the_upload_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    folder, path, state = _shelf(tmp_path, "b.txt", b"from the chat")
    sent = []

    async def upload(name, data):
        sent.append((name, data))
        return {"id": "up-1"}

    asyncio.run(mm.convert_folder(folder, state, {}, {}, None, upload))
    assert sent == [("b.txt", b"from the chat")] and not path.exists()
    folder2, path2, state2 = _shelf(tmp_path / "x", "c.txt", b"x")

    async def broken(name, data):
        raise OSError("network")

    asyncio.run(mm.convert_folder(folder2, state2, {}, {}, None, broken))
    assert path2.exists() and "не вдалося" in (path2.parent / "c.txt.md").read_text(encoding="utf-8")


def test_an_unreadable_file_keeps_its_original_and_says_so(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    folder, path, state = _shelf(tmp_path, "tool.exe", b"MZ")

    async def upload(name, data):
        raise AssertionError("nothing unreadable is moved")

    asyncio.run(mm.convert_folder(folder, state, {}, {}, None, upload))
    assert path.exists() and "Вміст не розпізнано: unsupported_format" in (path.parent / "tool.exe.md").read_text("utf-8")


def test_images_are_described_and_read_and_png_is_packed_without_loss(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    from PIL import Image

    raw = io.BytesIO()
    Image.new("RGB", (64, 64), (200, 10, 10)).save(raw, "PNG", compress_level=0)
    folder, path, state = _shelf(tmp_path, "графік.png", raw.getvalue())

    async def describe(agent, data, mime, caption, key, **_):
        assert agent == "library" and mime == "image/png"
        return {"status": "ok", "description": "## Опис\nЧервоний квадрат.\n\n## Текст\nнемає"}

    monkeypatch.setattr(media_vision, "describe", describe)
    sent = []

    async def upload(name, data):
        sent.append(data)
        return {"id": "img"}

    asyncio.run(mm.convert_folder(folder, state, {"openrouter_api_key": "k"}, {}, None, upload))
    assert "Червоний квадрат" in (folder / "Форекс" / "графік.png.md").read_text(encoding="utf-8")
    packed = Image.open(io.BytesIO(sent[0]))
    assert len(sent[0]) < len(raw.getvalue()) and packed.getpixel((5, 5)) == (200, 10, 10)  # smaller, same pixels
    assert "library" in media_vision.PROMPTS


def test_a_recording_takes_its_transcript_into_the_card_and_unshelved_files_wait(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    folder, path, state = _shelf(tmp_path, "лекція.mp3", b"ID3")
    transcript = path.with_name("лекція.mp3.розшифровка.md")
    transcript.write_text("---\nsource: x\n---\n\n**[0:00:01]** Ризик на угоду 1%.", encoding="utf-8")
    (folder / "новий.pdf").write_bytes(b"%PDF")  # not shelved yet
    asyncio.run(mm.convert_folder(folder, state, {}, {}, None, None))
    card = (folder / "Форекс" / "лекція.mp3.md").read_text(encoding="utf-8")
    assert "Ризик на угоду 1%." in card and "source: x" not in card and not transcript.exists()
    assert path.exists()  # no way to Drive: the original stays
    assert not (folder / "новий.pdf.md").exists()


def test_an_old_word_book_is_read_through_antiword_and_its_old_card_is_redone(tmp_path, monkeypatch):
    """19.11.2026: Bradbury and Yalom came as Word 97 .doc and were «not supported»."""
    import shutil
    import subprocess

    from src import material_reader

    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    folder, book, _state = _shelf(tmp_path, "Ялом.doc", b"\xd0\xcf\x11\xe0 old word")
    mm.card_path(book).write_text("---\n---\n\nВміст не розпізнано: unsupported_format. Оригінал: сервер.",
                                  encoding="utf-8")
    silent = book.with_name("екран.mp4")
    silent.write_bytes(b"\x00")
    mm.card_path(silent).write_text("Вміст не розпізнано: no_speech_heard.", encoding="utf-8")
    assert mm.pending(folder) == [book]  # the book is retried, a silent recording is not

    monkeypatch.setattr(shutil, "which", lambda _name: None)
    with __import__("pytest").raises(material_reader.MaterialError, match="doc_reader_missing"):
        material_reader.extract_text("doc", book.read_bytes())

    def antiword(args, **_kwargs):
        assert args[1:3] == ["-m", "UTF-8.txt"]
        return subprocess.CompletedProcess(args, 0, stdout="Екзистенційна психотерапія".encode(), stderr=b"")

    monkeypatch.setattr(shutil, "which", lambda _name: "/usr/bin/antiword")
    monkeypatch.setattr(subprocess, "run", antiword)
    assert material_reader.extract_text("doc", book.read_bytes()) == "Екзистенційна психотерапія"
