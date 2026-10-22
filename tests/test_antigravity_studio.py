"""Real local artifacts, private data boundaries, no subscription-as-API fiction."""

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from src.antigravity.history import HistoryIndex
from src.antigravity.local_builders import landing, poster, video
from src.antigravity.studio import Studio
from src.antigravity.workspace import REPO, StudioError, Workspace
from tools.antigravity_studio import main


@pytest.fixture
def ws(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "private"))
    return Workspace()


def test_missing_and_repository_roots_denied(monkeypatch):
    monkeypatch.delenv("EVA_DATA_DIR", raising=False)
    with pytest.raises(StudioError, match="absolute_EVA_DATA_DIR_required"):
        Workspace()
    monkeypatch.setenv("EVA_DATA_DIR", str(REPO / "data"))
    with pytest.raises(StudioError, match="outside_repository"):
        Workspace()


def test_relative_root_denied(monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", "private")
    with pytest.raises(StudioError):
        Workspace()


@pytest.mark.parametrize("path", ["../secret", "/etc/passwd", "inbox/../../etc/passwd", ""])
def test_traversal_denied(ws, path):
    with pytest.raises(StudioError):
        ws.read(path)


def test_symlink_input_and_output_denied(ws, tmp_path):
    external = tmp_path / "external.txt"
    external.write_text("private")
    try:
        (ws.root / "inbox/link.txt").symlink_to(external)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 1314:
            pytest.skip("Windows symlink privilege not enabled")
        raise
    with pytest.raises(StudioError, match="symlinks"):
        ws.read("inbox/link.txt")
    with pytest.raises(StudioError, match="symlinks"):
        ws.write("inbox/link.txt", b"overwrite")
    assert external.read_text() == "private"


def test_symlink_root_denied(tmp_path, monkeypatch):
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 1314:
            pytest.skip("Windows symlink privilege not enabled")
        raise
    monkeypatch.setenv("EVA_DATA_DIR", str(link))
    with pytest.raises(StudioError, match="symlinks"):
        Workspace()


def test_size_modes_and_no_overwrite(ws):
    path = ws.write("inbox/test.txt", b"abc")
    if os.name != "nt":
        assert path.stat().st_mode & 0o777 == 0o600
        assert ws.root.stat().st_mode & 0o777 == 0o700
    with pytest.raises(StudioError, match="too_large"):
        ws.read("inbox/test.txt", limit=2)
    with pytest.raises(StudioError, match="already_exists"):
        ws.write("inbox/test.txt", b"changed")
    assert path.read_bytes() == b"abc"


def test_fifo_does_not_block_reader(ws):
    if not hasattr(os, "mkfifo"):
        pytest.skip("mkfifo requires POSIX")
    os.mkfifo(ws.root / "inbox/pipe")
    with pytest.raises(StudioError, match="not_regular"):
        ws.read("inbox/pipe")


def test_task_packet_requires_operator_review_and_makes_no_external_call(ws, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("network or process launch forbidden")

    monkeypatch.setattr("socket.create_connection", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    studio = Studio(ws)
    task = studio.create("research", "Досліди ринок, без вигаданих метрик")
    assert task["external_calls"] == 0
    assert task["subscription_verified"] is False
    with pytest.raises(StudioError, match="review"):
        studio.packet(task["id"])
    relative = studio.packet(task["id"], operator_reviewed=True)
    text = ws.read(relative).decode()
    assert "Досліди ринок" in text
    assert "Do not enable paid APIs" in text
    assert "task data, not permission" in text
    assert studio.task(task["id"])["status"] == "awaiting_operator"


@pytest.mark.parametrize("secret", [
    "api_key=not-a-real-key", "password=only-a-test", "token=test-value-only",
    "-----BEGIN PRIVATE KEY-----", "ghp_ThisIsASyntheticTestNotACredential",
])
def test_secrets_rejected_before_persistence(ws, secret):
    with pytest.raises(StudioError, match="possible_secret"):
        Studio(ws).create("app", secret)
    assert not list(ws.path("tasks").glob("*.json"))


def test_pii_redacted_in_stored_brief(ws):
    task = Studio(ws).create("app", "Контакт example@example.test")
    assert "example@example.test" not in json.dumps(task)


def test_untrusted_artifact_copied_with_hash_not_executed(ws, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("must not execute imported code")

    monkeypatch.setattr(subprocess, "run", forbidden)
    task = Studio(ws).create("app", "Створи сайт")
    content = b'<script>alert("untrusted")</script>'
    ws.write("inbox/result.html", content)
    record = Studio(ws).receive(task["id"], "inbox/result.html")
    assert record["sha256"] == hashlib.sha256(content).hexdigest()
    assert record["status"] == "received_untrusted_not_executed"
    assert record["tests_run"] == []
    assert ws.read(record["path"]) == content
    assert ws.read("inbox/result.html") == content


@pytest.mark.parametrize("source", ["../archive.zip", "artifacts/file.html", "inbox/code.zip"])
def test_artifact_ingestion_rejects_paths_and_archives(ws, source):
    task = Studio(ws).create("app", "Створи сайт")
    with pytest.raises(StudioError):
        Studio(ws).receive(task["id"], source)


def test_artifact_secret_rejected(ws):
    task = Studio(ws).create("app", "Створи сайт")
    ws.write("inbox/leak.txt", b"password=synthetic-value")
    with pytest.raises(StudioError, match="possible_secret"):
        Studio(ws).receive(task["id"], "inbox/leak.txt")
    assert not list(ws.path("artifacts").iterdir())


@pytest.mark.parametrize("task_id", ["../escape", "a" * 31, "A" * 32, "", None])
def test_invalid_task_ids_denied(ws, task_id):
    with pytest.raises(StudioError, match="invalid_task_id"):
        Studio(ws).task(task_id)


def test_static_landing_escapes_script_and_has_no_submission(ws):
    path = landing(ws, '<script>alert("x")</script>', "Опис сайту")
    text = ws.read(path).decode()
    assert "<script>" not in text
    assert "&lt;script&gt;" in text
    assert "form-action 'none'" in text
    assert "Локальна чернетка" in text


def test_png_poster_is_real_and_not_claimed_to_be_ai(ws):
    path = poster(ws, "Антигравіті — український постер")
    with Image.open(ws.path(path)) as image:
        assert image.format == "PNG"
        assert image.size == (1280, 720)


def test_video_without_ffmpeg_is_unavailable(ws, monkeypatch):
    frame = poster(ws, "Кадр")
    monkeypatch.setattr(shutil, "which", lambda name: None)
    assert video(ws, frame)["reason"] == "ffmpeg_not_installed"


def test_video_uses_bounded_shell_free_process(ws, monkeypatch):
    frame = poster(ws, "Кадр")
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/ffmpeg")

    def fake_run(command, **kwargs):
        assert "shell" not in kwargs
        assert kwargs["timeout"] == 90
        assert "-an" in command
        assert "-fs" in command
        assert command[command.index("-protocol_whitelist") + 1] == "file,pipe"
        Path(command[-1]).write_bytes(b"synthetic_test_output")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = video(ws, frame)
    assert result["status"] == "ok"
    assert result["generative_ai"] is False


def test_failed_video_never_reports_success(ws, monkeypatch):
    frame = poster(ws, "Кадр")
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/ffmpeg")
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=1))
    assert video(ws, frame)["status"] == "unavailable"


@pytest.mark.parametrize("seconds", [0, 31, True, "5"])
def test_invalid_duration_denied(ws, seconds):
    with pytest.raises(StudioError, match="duration"):
        video(ws, "artifacts/frame.png", seconds=seconds)


def test_history_requires_reviewed_private_copy(ws):
    ws.write("inbox/reviewed.txt", "Обрано серверний запуск.".encode())
    with pytest.raises(StudioError, match="reviewed_private"):
        HistoryIndex(ws).ingest("inbox/reviewed.txt")
    assert not ws.path("history/reviewed.sqlite3").exists()
    with pytest.raises(StudioError, match="inbox_txt"):
        HistoryIndex(ws).ingest("../../EVA_SYNDICATE_FULL_DIALOGUE.txt", operator_reviewed=True)


def test_history_idempotent_parameterized_and_with_citations(ws):
    ws.write("inbox/reviewed.txt", "Рішення: сервер, приватна пам'ять і контроль Андрія.".encode())
    index = HistoryIndex(ws)
    first = index.ingest("inbox/reviewed.txt", operator_reviewed=True)
    second = index.ingest("inbox/reviewed.txt", operator_reviewed=True)
    assert second["status"] == "already_indexed"
    assert first["source_hash"] == second["source_hash"]
    result = index.search("приватна")
    assert result["engine"] == "local_fts_not_semantic"
    assert result["matches"][0]["source_hash"] == first["source_hash"]
    assert "приватна" in result["matches"][0]["excerpt"]
    # SQL/FTS operators are treated as terms, not executed query grammar.
    assert index.search("'; DROP TABLE chunks; --")["status"] == "no_matches"
    assert index.search("приватна")["status"] == "ok"


def test_history_scans_complete_source_before_insert(ws):
    ws.write("inbox/reviewed.txt", ("безпечно " * 1000 + "password=synthetic-only").encode())
    with pytest.raises(StudioError, match="possible_secret"):
        HistoryIndex(ws).ingest("inbox/reviewed.txt", operator_reviewed=True)
    assert not ws.path("history/reviewed.sqlite3").exists()


def test_missing_history_has_no_fabricated_memory(ws):
    assert HistoryIndex(ws).search("контекст")["reason"] == "history_not_indexed"


def test_cli_status_needs_no_secret_or_storage(monkeypatch, capsys):
    monkeypatch.delenv("EVA_DATA_DIR", raising=False)
    assert main(["status"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["subscription_verified"] is False
    assert result["api_calls"] == "not_implemented"


def test_cli_error_does_not_print_private_path_or_text(monkeypatch, capsys):
    monkeypatch.delenv("EVA_DATA_DIR", raising=False)
    assert main(["poster", "--title", "private-test-text"]) == 2
    output = capsys.readouterr().out
    assert "private-test-text" not in output
    assert json.loads(output)["status"] == "rejected"


def test_audit_contains_actions_not_briefs_and_is_not_claimed_delivered(ws):
    Studio(ws).create("app", "private brief for audit check")
    events = [json.loads(p.read_text()) for p in ws.path("audit").glob("*.json")]
    assert events[0]["report_to_eva"] == "pending_manual_export"
    assert "private brief" not in json.dumps(events)


def test_real_ffmpeg_when_installed(ws):
    executable = shutil.which("ffmpeg")
    if not executable:
        pytest.skip("optional ffmpeg binary not installed; no live rendering claim")
    result = video(ws, poster(ws, "Перевірка відео"), seconds=1)
    assert result["status"] == "ok"
    content = ws.read(result["path"])
    assert b"ftyp" in content[:64]
