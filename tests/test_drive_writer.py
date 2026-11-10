"""Alex writes only his own files into Andrii's Drive (drive.file); nothing is deleted."""

from __future__ import annotations

import asyncio
import json
import sys

import httpx
import pytest

from src import drive_writer as dw

CREDS = {"client_id": "cid", "client_secret": "cs", "refresh_token": "rt"}


class _FakeDrive:
    def __init__(self):
        self.files = {}  # id -> {name, parents, data}
        self.calls = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.calls.append((request.method, request.url.path))
        if request.url.host == "oauth2.googleapis.com":
            return httpx.Response(200, json={"access_token": "at"})
        assert request.headers["Authorization"] == "Bearer at"
        path = request.url.path
        if request.method == "GET" and path == "/drive/v3/files":
            query = request.url.params["q"]
            hits = [dict(id=i, name=f["name"], webViewLink=f"https://drive/{i}") for i, f in self.files.items()
                    if f"name = '{f['name']}'" in query and ("in parents" not in query or
                                                              any(f"'{p}' in parents" in query for p in f["parents"]))]
            return httpx.Response(200, json={"files": hits[:1]})
        if request.method == "GET" and path.startswith("/drive/v3/files/"):
            file_id = path.rsplit("/", 1)[1]
            return httpx.Response(200 if file_id in self.files else 404, json={"id": file_id, "trashed": False})
        if request.method == "POST" and path == "/drive/v3/files":
            body = json.loads(request.content)
            new_id = f"f{len(self.files) + 1}"
            self.files[new_id] = {"name": body["name"], "parents": [], "data": b""}
            return httpx.Response(200, json={"id": new_id})
        if request.method == "POST" and path == "/upload/drive/v3/files":
            raw = request.content.decode("utf-8", "replace")
            meta = json.loads(raw[raw.index("{"):raw.index("}") + 1])
            new_id = f"f{len(self.files) + 1}"
            self.files[new_id] = {"name": meta["name"], "parents": meta["parents"], "data": request.content}
            return httpx.Response(200, json={"id": new_id, "name": meta["name"], "webViewLink": f"https://drive/{new_id}"})
        if request.method == "PATCH":
            file_id = path.rsplit("/", 1)[1]
            self.files[file_id]["data"] = request.content
            return httpx.Response(200, json={"id": file_id, "name": self.files[file_id]["name"]})
        raise AssertionError(f"unexpected call {request.method} {path}")


class _Vault:
    def __init__(self, secret):
        self.secret = secret

    async def get_secret(self, path):
        assert path == "secret/data/syndicate/agents/trainer/google_oauth"
        return self.secret


def test_a_note_creates_the_own_folder_then_updates_the_same_file(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    drive = _FakeDrive()
    transport = httpx.MockTransport(drive.handler)
    first = asyncio.run(dw.save("trainer", _Vault(CREDS), None, name="План тижня", text="Пн: присід",
                                transport=transport))
    assert first["status"] == "ok" and first["action"] == "created" and first["name"] == "План тижня.md"
    folders = [f for f in drive.files.values() if f["name"] == dw.FOLDERS["trainer"]]
    assert len(folders) == 1
    second = asyncio.run(dw.save("trainer", _Vault(CREDS), None, name="План тижня", text="Пн: жим",
                                 transport=transport))
    assert second["action"] == "updated" and len(drive.files) == 2  # folder + one note, no duplicate
    assert all(method != "DELETE" for method, _ in drive.calls)


def test_files_come_only_from_alexs_own_obsidian_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    vault = tmp_path / "vault"
    (vault / "Health_Coach").mkdir(parents=True)
    (vault / "Health_Coach" / "Програма.pdf").write_bytes(b"%PDF-1.4")
    (vault / "Finance.md").write_text("гроші", encoding="utf-8")
    (vault / "Health_Coach" / "run.sh").write_text("x", encoding="utf-8")
    transport = httpx.MockTransport(_FakeDrive().handler)
    ok = asyncio.run(dw.save("trainer", _Vault(CREDS), vault, path="Health_Coach/Програма.pdf", transport=transport))
    assert ok["status"] == "ok" and ok["name"] == "Програма.pdf"
    outside = asyncio.run(dw.save("trainer", _Vault(CREDS), vault, path="Finance.md", transport=transport))
    assert outside["reason"] == "outside_own_folder_or_missing"
    script = asyncio.run(dw.save("trainer", _Vault(CREDS), vault, path="Health_Coach/run.sh", transport=transport))
    assert script["reason"] == "unsupported_type"


def test_without_a_grant_or_with_a_revoked_one_it_says_so(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    missing = asyncio.run(dw.save("trainer", _Vault({"client_id": "cid"}), None, name="x", text="y"))
    assert missing["reason"] == "drive_not_authorized"

    def revoked(request):
        return httpx.Response(400, json={"error": "invalid_grant"})

    result = asyncio.run(dw.save("trainer", _Vault(CREDS), None, name="x", text="y",
                                 transport=httpx.MockTransport(revoked)))
    assert result["reason"] == "grant_revoked"


def test_device_login_asks_only_drive_file_and_stores_the_refresh_token(tmp_path, monkeypatch, capsys):
    from tests.test_regressions import REPO_ROOT

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import syndicate_vault as tool

    store = {"agents/trainer/google_oauth": {"client_id": "cid", "client_secret": "cs"}}
    monkeypatch.setattr(tool, "get_secret", lambda path: dict(store.get(path, {})))
    monkeypatch.setattr(tool, "put_secret", lambda path, data: store.__setitem__(path, data))
    replies = [{"device_code": "dc", "user_code": "ABCD-EFGH", "verification_url": "https://www.google.com/device",
                "interval": 1, "expires_in": 60},
               {"error": "authorization_pending"},
               {"access_token": "at", "refresh_token": "REFRESH-SECRET-9", "scope": tool.DRIVE_FILE_SCOPE}]
    sent = []

    def fake_post(url, fields):
        sent.append((url, fields))
        return replies.pop(0)

    monkeypatch.setattr(tool, "_post_form", fake_post)
    tool.cmd_google_device_login("trainer", sleep=lambda seconds: None)
    assert sent[0][1]["scope"] == "https://www.googleapis.com/auth/drive.file"
    assert store["agents/trainer/google_oauth"]["refresh_token"] == "REFRESH-SECRET-9"
    out = capsys.readouterr().out
    assert "ABCD-EFGH" in out and "REFRESH-SECRET-9" not in out  # the token is never printed
    with pytest.raises(SystemExit):
        tool.cmd_google_device_login("nobody")
