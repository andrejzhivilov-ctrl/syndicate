"""One channel for all knowledge (18.11.2026): Drive or Eva's bot -> 00_Inbox/Вхідні -> each agent's folder."""

from __future__ import annotations

import asyncio
import json

from src import agent_folders, agent_schedule, drive_mirror, inbox_router, material_sorter, telegram_files


def _asker(answers):
    async def ask(prompt):
        for word, agent in answers.items():
            if word in prompt:
                return json.dumps({"agent": agent})
        return "не знаю"
    return ask


def test_each_item_goes_to_its_owner_and_the_rest_waits_for_andrii(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    inbox = tmp_path / "00_Inbox" / "Вхідні"
    inbox.mkdir(parents=True)
    (inbox / "Форекс для початківців.txt").write_text("Валютні пари, спред, кредитне плече", encoding="utf-8")
    (inbox / "Сніданки.txt").write_text("Рецепт вівсянки з білком", encoding="utf-8")
    (inbox / "лекція.mp3").write_bytes(b"ID3")
    (inbox / "лекція.mp3.розшифровка.md").write_text("Про тренування ніг", encoding="utf-8")
    course = inbox / "Курс Pinterest"
    course.mkdir()
    (course / "1.txt").write_text("Як вести Pinterest для мерчу", encoding="utf-8")
    (inbox / "щось.txt").write_text("незрозуміле", encoding="utf-8")
    asker = _asker({"Форекс": "sam", "вівсянки": "trainer", "тренування ніг": "trainer", "Pinterest": "tyler"})
    result = asyncio.run(inbox_router.route(tmp_path, asker))
    assert (tmp_path / "Сем/Матеріали/Форекс для початківців.txt").is_file()
    assert (tmp_path / "Health_Coach/Матеріали/Сніданки.txt").is_file()
    assert (tmp_path / "Health_Coach/Матеріали/лекція.mp3.розшифровка.md").is_file()  # travels with its recording
    assert (tmp_path / "Тайлер/Матеріали/Курс Pinterest/1.txt").is_file()  # a course moves whole
    assert (tmp_path / "00_Inbox/На перевірку/щось.txt").is_file() and result["unsure"] == ["щось.txt"]
    assert list(inbox.iterdir()) == []
    text = inbox_router.eva_message(result)
    assert "Сем" in text and "На перевірку" in text


def test_without_a_key_nothing_is_guessed_and_nothing_is_overwritten(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    inbox = tmp_path / "00_Inbox" / "Вхідні"
    inbox.mkdir(parents=True)
    (inbox / "a.txt").write_text("1", encoding="utf-8")
    (tmp_path / "00_Inbox/На перевірку").mkdir(parents=True)
    (tmp_path / "00_Inbox/На перевірку/a.txt").write_text("старий", encoding="utf-8")
    result = asyncio.run(inbox_router.route(tmp_path, None))
    assert result["unsure"] == ["a.txt"] and result["routed"] == []
    assert (tmp_path / "00_Inbox/На перевірку/a.txt").read_text(encoding="utf-8") == "старий"
    assert (tmp_path / "00_Inbox/На перевірку/a (2).txt").is_file()
    assert inbox_router.parse_owner('{"agent": "hacker"}') is None and inbox_router.parse_owner("") is None
    assert inbox_router.eva_message({"routed": [], "unsure": []}) is None


def test_every_route_has_a_shelf_and_a_folder_and_the_inbox_has_its_channels():
    for agent, (folder, _about) in inbox_router.ROUTES.items():
        assert material_sorter.SHELVES[agent][0] == folder, agent
        assert any(agent_folders.LAYOUT[key][0] == folder[0] for key in agent_folders.LAYOUT), agent
    assert drive_mirror.MIRRORS["eva"][1] == inbox_router.INBOX
    assert telegram_files.MATERIALS["eva"] == inbox_router.INBOX
    job = agent_schedule.JOBS["eva_drive_inbox"]
    assert job.kind == "drive_mirror" and job.agent == "eva"


def test_the_drive_inbox_mirrors_into_the_holding_inbox_with_its_own_state(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))

    class _Drive:
        downloads = 0

        def find_folder(self, name):
            return "root"

        def children(self, folder_id):
            return [{"id": "1", "name": "книга.pdf", "mimeType": "application/pdf", "md5Checksum": "a", "size": 3}]

        def download(self, item, dest):
            self.downloads += 1
            dest.write_bytes(b"pdf")

    drive = _Drive()
    vault = tmp_path / "vault"
    assert drive_mirror.mirror(drive, vault, "eva")["copied"] == 1
    assert (vault / "00_Inbox/Вхідні/книга.pdf").is_file()
    assert (tmp_path / "data/drive_mirror/eva.json").is_file()
    assert drive_mirror.mirror(drive, vault, "trainer")["copied"] == 1  # Alex's state is separate
