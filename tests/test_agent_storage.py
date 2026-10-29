"""Directors' Garage storage: own bucket, read-only shared, honest when not configured."""
from __future__ import annotations

import asyncio
import io
from datetime import datetime, timezone
from pathlib import Path

from src.agent_storage import (
    MAX_OBJECT_BYTES,
    SHARED_BUCKET,
    AgentStorage,
    bucket_for,
    files_reply,
)

ROOT = Path(__file__).resolve().parents[1]


class _Vault:
    def __init__(self, secrets):
        self.secrets, self.paths = secrets, []

    async def get_secret(self, path):
        self.paths.append(path)
        return self.secrets.get(path, {})


class _S3:
    def __init__(self):
        self.objects = {}

    def put_object(self, Bucket, Key, Body, ContentType):
        self.objects[(Bucket, Key)] = (Body, ContentType)
        return {}

    def get_object(self, Bucket, Key):
        body, ctype = self.objects[(Bucket, Key)]
        return {"Body": io.BytesIO(body), "ContentType": ctype}

    def list_objects_v2(self, Bucket, Prefix, MaxKeys):
        keys = sorted(k for b, k in self.objects if b == Bucket and k.startswith(Prefix))
        return {"Contents": [{"Key": k, "Size": len(self.objects[(Bucket, k)][0]),
                              "LastModified": datetime(2026, 10, 29, tzinfo=timezone.utc)} for k in keys[:MaxKeys]],
                "IsTruncated": len(keys) > MaxKeys}


CREDS = {"access_key_id": "GK1", "secret_access_key": "s"}


def _storage(agent="fin", s3=None, secrets=None):
    s3 = s3 or _S3()
    vault = _Vault(secrets if secrets is not None else {f"secret/data/syndicate/agents/{agent}/storage": CREDS})
    return AgentStorage(agent, vault, client_factory=lambda creds: s3), s3, vault


def test_director_writes_and_reads_its_own_bucket_with_its_own_vault_key():
    storage, s3, vault = _storage("fin")
    saved = asyncio.run(storage.put("reports/2026-10-29.md", b"# day", "text/markdown"))
    assert saved == {"status": "ok", "bucket": "agent-fin", "key": "reports/2026-10-29.md", "bytes": 5}
    assert asyncio.run(storage.get("reports/2026-10-29.md"))["data"] == b"# day"
    assert vault.paths == ["secret/data/syndicate/agents/fin/storage"]
    assert ("agent-fin", "reports/2026-10-29.md") in s3.objects


def test_shared_folder_is_read_only_except_for_eva():
    s3 = _S3()
    fin, _, _ = _storage("fin", s3)
    eva, _, _ = _storage("eva", s3)
    assert asyncio.run(fin.put("brief.md", b"x", shared=True))["status"] == "denied"
    assert asyncio.run(eva.put("brief.md", b"x", shared=True))["status"] == "ok"
    assert asyncio.run(fin.get("brief.md", shared=True))["data"] == b"x"
    assert (SHARED_BUCKET, "brief.md") in s3.objects


def test_without_a_key_nothing_pretends_to_be_saved():
    storage, s3, _ = _storage("sam", secrets={})
    result = asyncio.run(storage.put("a.txt", b"x"))
    assert result["status"] == "unavailable" and result["reason"] == "storage_not_configured"
    assert s3.objects == {}
    unknown, _, _ = _storage("hacker")
    assert asyncio.run(unknown.list())["status"] == "unavailable"


def test_bad_keys_and_oversized_files_are_refused():
    storage, _, _ = _storage()
    for key in ("/etc/passwd", "../agent-sam/x", "a//b", "a\\b", "", "x" * 600):
        assert asyncio.run(storage.put(key, b"x"))["error"] == "invalid_key"
    assert asyncio.run(storage.put("big.bin", b"0" * (MAX_OBJECT_BYTES + 1)))["error"] == "too_large_or_not_bytes"


def test_storage_errors_are_honest_not_fatal():
    class Broken(_S3):
        def put_object(self, **kwargs):
            raise ConnectionError("garage down")

    storage, _, _ = _storage("fin", Broken())
    result = asyncio.run(storage.put("a.txt", b"x"))
    assert result == {"status": "unavailable", "reason": "storage_error", "code": "ConnectionError"}


def test_agents_get_no_delete():
    assert not hasattr(AgentStorage, "delete")


def test_files_command_lists_without_a_model():
    storage, _, _ = _storage("fin")
    asyncio.run(storage.put("reports/a.md", b"12345"))
    reply = asyncio.run(files_reply("fin", "reports/", storage))
    assert reply["status"] == "completed" and "reports/a.md — 5 Б" in reply["response"]
    empty = asyncio.run(files_reply("fin", "shared", storage))
    assert "спільній теці" in empty["response"]
    missing, _, _ = _storage("sam", secrets={})
    assert "ще не підключене" in asyncio.run(files_reply("sam", "", missing))["response"]


def test_compose_runs_garage_internal_only_and_identical_in_both_files():
    root = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert root == (ROOT / "deploy/docker-compose.yml").read_text(encoding="utf-8")
    block = root.split("\n  garage:\n", 1)[1].split("\n  nginx:", 1)[0]
    assert "dxflrs/garage:v2.4.1" in block and "ports:" not in block and "frontend" not in block
    assert "GARAGE_RPC_SECRET: ${GARAGE_RPC_SECRET:?" in block and "cap_drop" in block
    toml = (ROOT / "config/garage/garage.toml").read_text(encoding="utf-8")
    assert "rpc_secret" not in toml.replace("GARAGE_RPC_SECRET", "") and "admin_token" not in toml
    # No admin HTTP API at all: administration goes over the encrypted RPC (garage json-api).
    sections = [line.strip() for line in toml.splitlines() if line.strip().startswith("[")]
    assert "[admin]" not in sections and "3903" not in toml and "ADMIN_TOKEN" not in block
    assert "garage" not in (ROOT / "config/nginx/nginx.conf").read_text(encoding="utf-8").lower()


def test_client_construction_and_stream_failures_stay_honest():
    def bad_factory(creds):
        raise ValueError("invalid endpoint from Vault")

    vault = _Vault({"secret/data/syndicate/agents/fin/storage": CREDS})
    storage = AgentStorage("fin", vault, client_factory=bad_factory)
    assert asyncio.run(storage.list())["reason"] == "storage_error"

    closed = []

    class Body:
        def read(self, n):
            raise ConnectionResetError("stream cut")

        def close(self):
            closed.append(True)

    class S3(_S3):
        def get_object(self, Bucket, Key):
            return {"Body": Body(), "ContentType": "text/plain"}

    reader, _, _ = _storage("fin", S3())
    result = asyncio.run(reader.get("a.txt"))
    assert result["status"] == "unavailable" and result["code"] == "ConnectionResetError" and closed == [True]


def test_setup_revokes_what_an_agent_must_not_have(monkeypatch):
    import tools.garage_setup as setup

    calls = []
    monkeypatch.setattr(setup, "api", lambda endpoint, payload=None: calls.append((endpoint, payload)))
    setup.reconcile("shared", "GKfin", read=True, write=False, owner=False)
    assert calls == [("AllowBucketKey", {"bucketId": "shared", "accessKeyId": "GKfin", "permissions": {"read": True}}),
                     ("DenyBucketKey", {"bucketId": "shared", "accessKeyId": "GKfin",
                                        "permissions": {"write": True, "owner": True}})]
    assert any(rule["ID"] == "tmp-expiry" for rule in setup.LIFECYCLE)


def test_setup_dry_run_on_a_fresh_cluster_changes_nothing(monkeypatch, capsys):
    import tools.garage_setup as setup

    calls = []

    def fake_api(endpoint, payload=None):
        calls.append(endpoint)
        return {"GetClusterLayout": {"roles": [], "version": 0},
                "GetClusterStatus": {"nodes": [{"id": "abc123def456789"}]}}[endpoint]

    monkeypatch.setattr(setup, "api", fake_api)
    assert setup.main([]) == 0
    assert calls == ["GetClusterLayout", "GetClusterStatus"]  # read-only, no bucket queries
    out = capsys.readouterr().out
    assert "bucket agent-fin: create" in out and "dry run" in out


def test_bucket_names_are_per_director():
    assert bucket_for("jack") == "agent-jack"
