"""Andrii's Google Drive folder reaches Alex's vault: copy new, never delete, report the rest."""

from __future__ import annotations

import asyncio
from pathlib import Path

from src import agent_schedule as sched
from src import drive_mirror as dm


class _FakeDrive:
    def __init__(self, tree, shared=True):
        self.tree = tree  # folder id -> list of items
        self.shared = shared
        self.downloads = []
        self.broken = set()

    def find_folder(self, name):
        assert name == dm.FOLDER_NAME
        return "root" if self.shared else None

    def children(self, folder_id):
        return list(self.tree.get(folder_id, []))

    def download(self, item, dest: Path):
        if item["id"] in self.broken:
            raise OSError("network")
        self.downloads.append(item["id"])
        dest.write_bytes(f"{item['id']}:{item.get('md5Checksum', '')}".encode())


def _file(fid, name, md5="a", mime="application/pdf", size=10):
    return {"id": fid, "name": name, "mimeType": mime, "md5Checksum": md5, "size": str(size)}


def _setup(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    vault = tmp_path / "vault"
    vault.mkdir()
    return vault, vault / "Health_Coach" / "Матеріали"


def test_new_and_changed_files_are_copied_with_their_folders(tmp_path, monkeypatch):
    vault, target = _setup(tmp_path, monkeypatch)
    drive = _FakeDrive({
        "root": [_file("1", "Книга.pdf"), {"id": "f", "name": "Курс 1", "mimeType": dm.FOLDER_MIME},
                 _file("2", "Нотатки", mime=dm.DOC_MIME, size=0), _file("3", "Таблиця", mime="application/vnd.google-apps.spreadsheet")],
        "f": [_file("4", "Лекція 1.mp4", mime="video/mp4")],
    })
    first = dm.mirror(drive, vault)
    assert first["status"] == "ok" and first["copied"] == 3 and first["skipped_native"] == 1
    assert (target / "Книга.pdf").is_file() and (target / "Курс 1" / "Лекція 1.mp4").is_file()
    assert (target / "Нотатки.docx").is_file()  # a Google Doc arrives as DOCX

    again = dm.mirror(drive, vault)
    assert again["copied"] == 0 and again["unchanged"] == 3

    drive.tree["root"][0] = _file("1", "Книга.pdf", md5="b")
    changed = dm.mirror(drive, vault)
    assert changed["copied"] == 1 and (target / "Книга.pdf").read_bytes() == b"1:b"


def test_nothing_is_deleted_when_a_file_leaves_drive(tmp_path, monkeypatch):
    vault, target = _setup(tmp_path, monkeypatch)
    drive = _FakeDrive({"root": [_file("1", "Книга.pdf")]})
    dm.mirror(drive, vault)
    drive.tree["root"] = []
    result = dm.mirror(drive, vault)
    assert result["removed_in_drive_kept"] == 1 and (target / "Книга.pdf").is_file()


def test_unsafe_names_stay_inside_the_target_folder(tmp_path, monkeypatch):
    vault, target = _setup(tmp_path, monkeypatch)
    drive = _FakeDrive({"root": [_file("1", "../../evil.pdf"), _file("2", "..")]})
    dm.mirror(drive, vault)
    written = [p for p in vault.rglob("*") if p.is_file()]
    assert written and all(target in p.parents for p in written)


def test_failures_large_files_and_limits_are_counted_not_hidden(tmp_path, monkeypatch):
    vault, target = _setup(tmp_path, monkeypatch)
    items = [_file(str(i), f"{i}.pdf") for i in range(dm.MAX_FILES_PER_RUN + 3)]
    items.append(_file("big", "big.mp4", size=dm.MAX_FILE_BYTES + 1))
    drive = _FakeDrive({"root": items})
    drive.broken.add("0")
    result = dm.mirror(drive, vault)
    assert result["status"] == "partial" and result["failed"] == 1 and result["too_large"] == 1
    assert result["copied"] + result["failed"] == dm.MAX_FILES_PER_RUN and result["deferred"] == 3
    assert not list(target.rglob("*.part")), "a failed download leaves no half file"


def test_an_unshared_folder_or_missing_key_is_unavailable(tmp_path, monkeypatch):
    vault, _ = _setup(tmp_path, monkeypatch)
    assert dm.mirror(_FakeDrive({}, shared=False), vault)["reason"] == "drive_folder_not_shared"

    class _Vault:
        async def get_secret(self, path):
            return {}

    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", str(vault))
    assert asyncio.run(dm.run(_Vault()))["reason"] == "no_service_account_json_in_vault"


def test_the_same_failure_alarms_once_until_the_reason_changes(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    reasons = iter(["drive_folder_not_shared", "drive_folder_not_shared", "ok", "drive_folder_not_shared"])

    async def job(job, gateway):
        reason = next(reasons)
        return {"status": "ok"} if reason == "ok" else {"status": "unavailable", "reason": reason}

    class _Gateway:
        sent = []

        async def owner_user_id(self):
            return "1"

        async def send(self, bot, chat, text):
            self.sent.append(text)
            return True

    gateway = _Gateway()
    monkeypatch.setattr(sched, "run_job", job)
    schedule = sched.AgentSchedule(gateway, [])
    for _ in range(4):
        asyncio.run(schedule.run(sched.JOBS["alex_drive_mirror"]))
    assert len(gateway.sent) == 2  # first failure, then again after a success
