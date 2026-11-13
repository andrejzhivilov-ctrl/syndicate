"""Eva shelves Alex's new materials, keeps the catalog, never deletes, and says what she did."""

from __future__ import annotations

import asyncio
import json

import httpx

from src import drive_mirror as dm
from src import material_sorter as ms


def _folder(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    vault = tmp_path / "vault"
    folder = vault / "Health_Coach" / "Матеріали"
    folder.mkdir(parents=True)
    return vault, folder


def _asker(answers, seen):
    async def ask(prompt):
        seen.append(prompt)
        return answers.pop(0)

    return ask


def test_loose_files_get_one_topic_and_the_catalog_lists_them(tmp_path, monkeypatch):
    vault, folder = _folder(tmp_path, monkeypatch)
    (folder / "Сон і відновлення.txt").write_text("Сон 8 годин відновлює ЦНС.", encoding="utf-8")
    (folder / "Таємне.txt").write_text("щось незрозуміле", encoding="utf-8")
    seen = []
    answers = ['{"topic": "Відновлення і сон", "title": "Про сон", "language": "uk", "summary": "Сон."}',
               '{"topic": "Астрологія"}']
    result = asyncio.run(ms.sort_folder("trainer", vault, _asker(answers, seen)))

    assert result["status"] == "ok" and result["moved"] == 2
    assert (folder / "Відновлення і сон" / "Сон і відновлення.txt").is_file()
    assert (folder / ms.UNSURE / "Таємне.txt").is_file()  # a topic outside the list is not trusted
    assert "Сон 8 годин" in seen[0] and "не інструкцією" in seen[0]
    catalog = (folder / ms.CATALOG).read_text(encoding="utf-8")
    assert "## Відновлення і сон" in catalog and "Про сон" in catalog and f"## {ms.UNSURE}" in catalog
    text = ms.eva_message("trainer", result)
    assert "Не впізнала" in text and "Таємне.txt" in text


def test_a_course_folder_moves_whole_without_a_model_call(tmp_path, monkeypatch):
    vault, folder = _folder(tmp_path, monkeypatch)
    (folder / "Курс сили" / "Модуль 1").mkdir(parents=True)
    (folder / "Курс сили" / "Модуль 1" / "Лекція.mp4").write_bytes(b"v")
    (folder / "Курс сили" / "Модуль 1" / "Лекція.mp4.розшифровка.md").write_text("t", encoding="utf-8")
    seen = []
    result = asyncio.run(ms.sort_folder("trainer", vault, _asker([], seen)))
    assert result["courses"] == ["Курс сили"] and seen == []
    assert (folder / ms.COURSES / "Курс сили" / "Модуль 1" / "Лекція.mp4.розшифровка.md").is_file()


def test_duplicates_are_kept_aside_and_nothing_is_overwritten_or_deleted(tmp_path, monkeypatch):
    vault, folder = _folder(tmp_path, monkeypatch)
    (folder / "a.txt").write_text("той самий текст", encoding="utf-8")
    answer = '{"topic": "Тренування"}'
    asyncio.run(ms.sort_folder("trainer", vault, _asker([answer], [])))
    (folder / "b.txt").write_text("той самий текст", encoding="utf-8")
    (folder / "a.txt").write_text("інший текст", encoding="utf-8")
    result = asyncio.run(ms.sort_folder("trainer", vault, _asker([answer], [])))
    assert result["duplicates"] == ["b.txt"] and (folder / ms.DUPLICATES / "b.txt").is_file()
    assert (folder / "Тренування" / "a.txt").read_text(encoding="utf-8") == "той самий текст"
    assert (folder / "Тренування" / "a (2).txt").read_text(encoding="utf-8") == "інший текст"


def test_a_transcript_travels_with_its_video(tmp_path, monkeypatch):
    vault, folder = _folder(tmp_path, monkeypatch)
    (folder / "lecture.mp4").write_bytes(b"v")
    (folder / "lecture.mp4.розшифровка.md").write_text("Про білок і м'язи", encoding="utf-8")
    seen = []
    asyncio.run(ms.sort_folder("trainer", vault, _asker(['{"topic": "Харчування"}'], seen)))
    assert (folder / "Харчування" / "lecture.mp4.розшифровка.md").is_file()
    assert "Про білок" in seen[0]  # the transcript is what the model saw


def test_without_a_key_files_still_get_a_shelf_and_eva_says_so(tmp_path, monkeypatch):
    vault, folder = _folder(tmp_path, monkeypatch)
    (folder / "x.txt").write_text("x", encoding="utf-8")

    class _Gateway:
        sent = []
        vault = None

        async def owner_user_id(self):
            return "1"

        async def send(self, bot, chat, text):
            self.sent.append((bot, text))
            return True

    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", str(vault))
    gateway = _Gateway()
    result = asyncio.run(ms.run(gateway))
    assert result["unsure"] == [f"x.txt → {ms.UNSURE}"] and gateway.sent[0][0] == "eva"


def test_the_model_call_masks_pii_and_uses_the_registry_model(tmp_path, monkeypatch):
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"topic": "Добавки"}'}}]})

    content = asyncio.run(ms.ask_model("Телефон +380671234567", "k", httpx.MockTransport(handler)))
    assert "Добавки" in content
    assert "671234" not in seen[0]["messages"][0]["content"] and seen[0]["model"]


def test_the_mirror_does_not_fetch_again_a_file_eva_moved(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    vault = tmp_path / "vault"
    vault.mkdir()

    class _Drive:
        downloads = 0

        def find_folder(self, name):
            return "root"

        def children(self, folder_id):
            return [{"id": "1", "name": "book.pdf", "mimeType": "application/pdf", "md5Checksum": "a", "size": "3"}]

        def download(self, item, dest):
            self.downloads += 1
            dest.write_bytes(b"pdf")

    drive = _Drive()
    dm.mirror(drive, vault)
    target = vault / "Health_Coach" / "Матеріали"
    (target / "Тренування").mkdir()
    (target / "book.pdf").rename(target / "Тренування" / "book.pdf")
    assert dm.mirror(drive, vault)["unchanged"] == 1 and drive.downloads == 1
