"""Archives in the knowledge channel are opened safely, each file then carded (Andrii, 19.11.2026)."""

from __future__ import annotations

import asyncio
import json
import subprocess

from src import archive_unpack as au
from src import material_markdown as mm
from src import material_sorter


def _tools(monkeypatch, entries, *, encrypted=False, unpacked=None, rc=0):
    """Fake lsar/unar: lsar lists ``entries``; unar writes ``unpacked`` {relative: text} into -o."""
    monkeypatch.setattr(au.shutil, "which", lambda name: f"/usr/bin/{name}")
    calls = []

    def run(args, **_kwargs):
        calls.append(args)
        if args[0].endswith("lsar"):
            body = {"lsarEncrypted": encrypted, "lsarContents": [
                {"XADFileName": name, "XADFileSize": size} for name, size in entries]}
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps(body).encode(), stderr=b"")
        target = args[args.index("-o") + 1]
        for relative, text in (unpacked or {}).items():
            path = __import__("pathlib").Path(target) / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return subprocess.CompletedProcess(args, rc, stdout=b"", stderr=b"")

    monkeypatch.setattr(au.subprocess, "run", run)
    return calls


def _shelf(tmp_path, name):
    folder = tmp_path / "Сем" / "Матеріали"
    (folder / "Курси").mkdir(parents=True)
    path = folder / "Курси" / name
    path.write_bytes(b"Rar!\x1a\x07")
    return folder, path


def test_an_archive_opens_next_to_itself_and_every_file_inside_waits_for_its_own_card(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    folder, archive = _shelf(tmp_path, "трейдинг.rar")
    calls = _tools(monkeypatch, [("Рівні.pdf", 10), ("уроки/1.txt", 5)],
                   unpacked={"Рівні.pdf": "pdf", "уроки/1.txt": "рівні підтримки"})
    body = asyncio.run(mm.content(archive, {}))
    assert body["status"] == "ok" and body["kind"] == "archive" and body["files"] == 2
    assert "трейдинг (архів)" in body["text"] and "уроки/1.txt" in body["text"].replace("\\", "/")
    assert "-no-recursion" in calls[-1]  # a nested archive is opened on its own pass, with the depth guard
    inside = archive.parent / "трейдинг (архів)"
    assert (inside / "уроки" / "1.txt").is_file()
    mm.card_path(archive).write_text("card", encoding="utf-8")
    assert sorted(p.name for p in mm.pending(folder)) == ["1.txt", "Рівні.pdf"]
    assert "Рівні.pdf" in material_sorter.excerpt(archive)  # Eva routes an archive by what it holds


def test_dangerous_or_locked_archives_are_refused_never_guessed(tmp_path, monkeypatch):
    _folder, archive = _shelf(tmp_path, "x.zip")
    _tools(monkeypatch, [("../../etc/passwd", 1)])
    assert au.unpack(archive) == {"status": "unavailable", "reason": "unsafe_paths"}
    _tools(monkeypatch, [("C:/Windows/x.dll", 1)])
    assert au.unpack(archive)["reason"] == "unsafe_paths"
    _tools(monkeypatch, [("a.txt", 1)], encrypted=True)
    assert au.unpack(archive)["reason"] == "password_protected"
    _tools(monkeypatch, [("a.bin", au.MAX_UNPACKED_BYTES + 1)])
    assert au.unpack(archive)["reason"] == "archive_too_large"
    nested = archive.parent / "a (архів)" / "b (архів)" / "c.zip"
    nested.parent.mkdir(parents=True)
    nested.write_bytes(b"PK")
    assert au.unpack(nested)["reason"] == "nested_too_deep"
    assert not any(p.name.endswith(au.SUFFIX) for p in archive.parent.iterdir() if p.name != "a (архів)")


def test_without_the_tool_the_archive_waits_for_the_next_run_and_an_old_card_is_redone(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    folder, archive = _shelf(tmp_path, "курс.7z")
    monkeypatch.setattr(au.shutil, "which", lambda _name: None)
    done = asyncio.run(mm.convert_one(archive, {}, {}, {}, None, None))
    assert done["status"] == "later" and done["reason"] == "archive_tool_missing"
    assert not mm.card_path(archive).exists() and archive.is_file()
    mm.card_path(archive).write_text("Вміст не розпізнано: unsupported_format.", encoding="utf-8")
    assert mm.pending(folder) == [archive]
