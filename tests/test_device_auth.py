"""
SYNDICATE — per-device client tokens (backend blockers 0.2 / 0.3).

Motivation, so nobody "simplifies" this away:

  * The runtime has one shared ``EVA_API_KEY``. Compiling it into a mobile or
    desktop client would mean the key can be extracted from the binary, and it
    cannot be revoked per device. Device tokens are per-device, short-lived,
    scoped and individually revocable.
  * ``/execute`` blocks for the whole agent run. A streamed variant must keep
    the connection alive and must NOT invent progress events it does not have.

Run with:  .venv/bin/python -m pytest tests/test_device_auth.py -q
"""

from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "deploy" / "runtime"))


def _run(coro):
    return asyncio.run(coro)


MASTER = "sandbox-secret-api-key-2026"


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def store():
    """A fresh in-memory DeviceTokenStore (no DB pool -> memory backend)."""
    from src.device_auth import DeviceTokenStore

    return DeviceTokenStore(memory=None, default_ttl_seconds=3600)


@pytest.fixture()
def runtime():
    """A TestClient wired with a master key, a token store and stub services."""
    import agent_runner

    saved = {
        "api_key": agent_runner.app_state.api_key,
        "ready": agent_runner.app_state.ready,
        "device_tokens": agent_runner.app_state.device_tokens,
        "orchestrator": agent_runner.app_state.orchestrator,
        "sentinel": agent_runner.app_state.sentinel,
        "memory_manager": agent_runner.app_state.memory_manager,
    }

    from src.device_auth import DeviceTokenStore

    agent_runner.app_state.api_key = MASTER
    agent_runner.app_state.ready = True
    agent_runner.app_state.device_tokens = DeviceTokenStore(memory=None, default_ttl_seconds=3600)
    agent_runner.app_state.memory_manager = None
    agent_runner.app_state.orchestrator = _StubOrchestrator()
    agent_runner.app_state.sentinel = _StubSentinel()

    client = TestClient(agent_runner.app)
    try:
        yield client, agent_runner.app_state
    finally:
        for key, value in saved.items():
            setattr(agent_runner.app_state, key, value)


class _StubSentinel:
    async def validate_task(self, payload):  # noqa: ARG002
        class V:
            allowed = True
            reason = None

        return V()


class _StubOrchestrator:
    def __init__(self, delay: float = 0.0) -> None:
        self.delay = delay
        self.calls = []

    async def execute(self, task_type, payload, session_id=None):  # noqa: ARG002
        self.calls.append(task_type)
        if self.delay:
            await asyncio.sleep(self.delay)
        return {"task_id": "task-1", "status": "completed", "result": {"answer": "done"}}


# ─────────────────────────────────────────────────────────────────────────────
class TestTokenIssuance:
    """0.3 — a client must be able to hold a credential that is not the master key."""

    def test_enroll_returns_plaintext_once(self, store):
        issued = _run(store.enroll("pixel-8", label="Andrii phone"))
        assert issued["token"].count(".") == 1
        assert issued["device_id"] == "pixel-8"
        assert issued["status"] == "active"
        # The plaintext is never persisted — only its hash is.
        assert "token" not in store._mem_tokens[issued["token_id"]].public_dict()

    def test_secret_is_only_stored_hashed(self, store):
        issued = _run(store.enroll("pixel-8"))
        record = store._mem_tokens[issued["token_id"]]
        assert record.secret_hash != issued["token"]
        assert len(record.secret_hash) == 64  # sha256 hex

    def test_enroll_requires_device_id(self, store):
        with pytest.raises(ValueError):
            _run(store.enroll("   "))

    def test_enroll_rejects_unknown_scope(self, store):
        with pytest.raises(ValueError):
            _run(store.enroll("pixel-8", scopes=["root"]))

    def test_device_token_verifies(self, store):
        issued = _run(store.enroll("pixel-8"))
        record = _run(store.verify(issued["token"]))
        assert record is not None and record.device_id == "pixel-8"

    def test_tampered_secret_rejected(self, store):
        issued = _run(store.enroll("pixel-8"))
        token_id, _secret = issued["token"].split(".")
        assert _run(store.verify(f"{token_id}.wrongsecret")) is None

    def test_garbage_token_rejected(self, store):
        for bad in ("", None, "nodot", ".", "abc.", ".def"):
            assert _run(store.verify(bad)) is None

    def test_unknown_token_id_rejected(self, store):
        assert _run(store.verify("deadbeefdeadbeef.somesecret")) is None


class TestTokenLifetime:
    def test_expired_token_rejected(self, store):
        issued = _run(store.enroll("pixel-8", ttl_seconds=60))
        record = store._mem_tokens[issued["token_id"]]
        from datetime import datetime, timedelta, timezone

        record.expires_at = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        assert _run(store.verify(issued["token"])) is None

    def test_ttl_is_clamped(self, store):
        tiny = _run(store.enroll("a", ttl_seconds=1))
        huge = _run(store.enroll("b", ttl_seconds=10 ** 9))
        assert tiny["expires_in_seconds"] == 60          # MIN_TTL_SECONDS
        assert huge["expires_in_seconds"] == 365 * 24 * 3600  # MAX_TTL_SECONDS

    def test_unparsable_expiry_is_never_valid(self):
        from src.device_auth import DeviceToken

        record = DeviceToken(token_id="t", device_id="d", secret_hash="h", expires_at="not-a-date")
        assert record.expired is True and record.usable is False


class TestRevocationAndRotation:
    def test_revoke_kills_token(self, store):
        issued = _run(store.enroll("pixel-8"))
        assert _run(store.revoke(issued["token_id"])) is True
        assert _run(store.verify(issued["token"])) is None
        assert _run(store.list_devices())[0]["status"] == "revoked"

    def test_revoke_unknown_returns_false(self, store):
        assert _run(store.revoke("nosuch")) is False

    def test_refresh_rotates_old_token_dead(self, store):
        issued = _run(store.enroll("pixel-8", label="phone", scopes=["read"]))
        rotated = _run(store.refresh(issued["token"]))
        assert rotated is not None
        assert rotated["token"] != issued["token"]
        assert rotated["device_id"] == "pixel-8"
        assert rotated["scopes"] == ["read"]          # scopes survive rotation
        assert _run(store.verify(issued["token"])) is None   # old one is dead
        assert _run(store.verify(rotated["token"])) is not None

    def test_refresh_with_bad_token_returns_none(self, store):
        assert _run(store.refresh("garbage.token")) is None

    def test_per_device_cap(self, store):
        # 12 tokens, cap of 10 -> the two oldest must be evicted.
        for i in range(12):
            _run(store.enroll("pixel-8", label=f"t{i}"))
        active = [d for d in _run(store.list_devices()) if d["status"] == "active"]
        assert len(active) == 10


class TestScopes:
    def test_empty_scopes_satisfy_no_required_scope(self, store):
        """Least privilege: a token with no scopes cannot satisfy *any*
        required scope. The master key is the only credential that implicitly
        grants everything."""
        issued = _run(store.enroll("pixel-8"))
        assert _run(store.verify(issued["token"], required_scope="execute")) is None
        assert _run(store.verify(issued["token"], required_scope="hitl")) is None

    def test_explicit_scopes_satisfy_only_those(self, store):
        issued = _run(store.enroll("pixel-8", scopes=["read", "execute", "hitl"]))
        assert _run(store.verify(issued["token"], required_scope="read")) is not None
        assert _run(store.verify(issued["token"], required_scope="execute")) is not None
        assert _run(store.verify(issued["token"], required_scope="hitl")) is not None

    def test_scope_restricts(self, store):
        issued = _run(store.enroll("pixel-8", scopes=["read"]))
        assert _run(store.verify(issued["token"], required_scope="read")) is not None
        assert _run(store.verify(issued["token"], required_scope="execute")) is None
        assert _run(store.verify(issued["token"], required_scope="hitl")) is None


# ─────────────────────────────────────────────────────────────────────────────
class TestHttpAuth:
    """The wire behaviour a client actually depends on."""

    def test_master_key_still_works(self, runtime):
        client, _ = runtime
        assert client.get("/status").status_code == 401
        assert client.get("/status", headers={"X-API-Key": MASTER}).status_code == 200

    def test_bearer_master_key_works(self, runtime):
        client, _ = runtime
        r = client.get("/status", headers={"Authorization": f"Bearer {MASTER}"})
        assert r.status_code == 200

    def test_device_token_authenticates(self, runtime):
        client, state = runtime
        issued = _run(state.device_tokens.enroll("pixel-8", label="phone"))
        token = issued["token"]
        assert client.get("/status", headers={"X-API-Key": token}).status_code == 200
        assert client.get("/status", headers={"Authorization": f"Bearer {token}"}).status_code == 200

    def test_revoked_token_loses_access_immediately(self, runtime):
        client, state = runtime
        issued = _run(state.device_tokens.enroll("pixel-8"))
        assert client.get("/status", headers={"X-API-Key": issued["token"]}).status_code == 200
        _run(state.device_tokens.revoke(issued["token_id"]))
        assert client.get("/status", headers={"X-API-Key": issued["token"]}).status_code == 401

    def test_device_token_cannot_administer_other_devices(self, runtime):
        """A stolen phone must not be able to mint or revoke the fleet."""
        client, state = runtime
        issued = _run(state.device_tokens.enroll("pixel-8"))
        headers = {"X-API-Key": issued["token"]}
        assert client.get("/auth/devices", headers=headers).status_code == 403
        assert client.post("/auth/device/enroll", json={"device_id": "evil"}, headers=headers).status_code == 403
        assert client.post("/auth/device/revoke", json={"token_id": issued["token_id"]}, headers=headers).status_code == 403

    def test_enroll_requires_master_key(self, runtime):
        client, _ = runtime
        assert client.post("/auth/device/enroll", json={"device_id": "x"}).status_code == 401

    def test_enroll_and_use_roundtrip(self, runtime):
        client, state = runtime
        r = client.post(
            "/auth/device/enroll",
            json={"device_id": "macbook", "label": "Andrii MBP", "scopes": ["read"], "ttl_seconds": 600},
            headers={"X-API-Key": MASTER},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["device_id"] == "macbook" and body["scopes"] == ["read"]
        assert body["expires_in_seconds"] == 600
        assert "warning" in body  # client is told the token is shown once
        assert client.get("/status", headers={"X-API-Key": body["token"]}).status_code == 200

    def test_enroll_rejects_bad_scope_over_http(self, runtime):
        client, _ = runtime
        r = client.post("/auth/device/enroll", json={"device_id": "x", "scopes": ["root"]},
                        headers={"X-API-Key": MASTER})
        assert r.status_code == 422

    def test_whoami_distinguishes_credentials(self, runtime):
        client, state = runtime
        issued = _run(state.device_tokens.enroll("pixel-8", scopes=["read"]))
        me = client.get("/auth/device/whoami", headers={"X-API-Key": MASTER}).json()
        assert me["credential"] == "master_key"
        me = client.get("/auth/device/whoami", headers={"X-API-Key": issued["token"]}).json()
        assert me["credential"] == "device_token"
        assert me["device_id"] == "pixel-8" and me["scopes"] == ["read"]

    def test_refresh_endpoint_rotates(self, runtime):
        client, state = runtime
        issued = _run(state.device_tokens.enroll("pixel-8"))
        r = client.post("/auth/device/refresh", json={"token": issued["token"]})
        assert r.status_code == 200
        new_token = r.json()["token"]
        assert new_token != issued["token"]
        assert client.get("/status", headers={"X-API-Key": new_token}).status_code == 200
        assert client.get("/status", headers={"X-API-Key": issued["token"]}).status_code == 401

    def test_refresh_rejects_dead_token(self, runtime):
        client, _ = runtime
        r = client.post("/auth/device/refresh", json={"token": "deadbeef.nope"})
        assert r.status_code == 401

    def test_device_list_never_exposes_secrets(self, runtime):
        client, state = runtime
        issued = _run(state.device_tokens.enroll("pixel-8"))
        devices = client.get("/auth/devices", headers={"X-API-Key": MASTER}).json()["devices"]
        assert devices and devices[0]["device_id"] == "pixel-8"
        blob = str(devices)
        assert issued["token"] not in blob
        assert "secret_hash" not in blob


# ─────────────────────────────────────────────────────────────────────────────
class TestOpenApiAndCors:
    """0.1 / 0.2 — the contract must be exportable and CORS must be closed by default."""

    def test_openapi_is_served(self, runtime):
        client, _ = runtime
        r = client.get("/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        assert schema["info"]["title"] == "SYNDICATE Agent"
        assert "/execute/stream" in schema["paths"]
        assert "/auth/device/enroll" in schema["paths"]

    def test_docs_route_exists(self, runtime):
        client, _ = runtime
        assert client.get("/docs").status_code == 200

    def test_cors_closed_by_default(self, runtime):
        client, _ = runtime
        r = client.get("/status", headers={"Origin": "https://evil.example", "X-API-Key": MASTER})
        assert "access-control-allow-origin" not in {k.lower() for k in r.headers}

    def test_cors_allowlist_is_env_driven(self, monkeypatch):
        monkeypatch.setenv("EVAS_CORS_ORIGINS", "https://app.eva.local, http://localhost:5173")
        import agent_runner

        agent_runner = importlib.reload(agent_runner)
        try:
            origins = agent_runner._cors_origins()
            assert origins == ["https://app.eva.local", "http://localhost:5173"]
        finally:
            monkeypatch.delenv("EVAS_CORS_ORIGINS", raising=False)
            importlib.reload(agent_runner)


# ─────────────────────────────────────────────────────────────────────────────
class TestProtectedReadSurface:
    """Optional backlog item 0.6: protect the UI and floor registry."""

    @staticmethod
    def _basic_headers(token: str) -> dict:
        import base64

        credentials = base64.b64encode(f"device:{token}".encode("utf-8")).decode("ascii")
        return {"Authorization": f"Basic {credentials}"}

    def test_floor_registry_requires_explicit_read_scope(self, runtime):
        client, state = runtime
        assert client.get("/floors").status_code == 401

        execute_only = _run(state.device_tokens.enroll("worker", scopes=["execute"]))
        denied = client.get("/floors", headers={"X-API-Key": execute_only["token"]})
        assert denied.status_code == 401
        assert "read" in denied.json()["detail"].lower()

        # The fixture's orchestration stub is only for auth tests; use the
        # real static registry fallback for this protected read endpoint.
        state.orchestrator = None
        read_token = _run(state.device_tokens.enroll("reader", scopes=["read"]))
        allowed = client.get("/floors", headers={"Authorization": f"Bearer {read_token['token']}"})
        assert allowed.status_code == 200 and "floors" in allowed.json()
        assert client.get("/floors", headers={"X-API-Key": MASTER}).status_code == 200

    def test_cockpit_and_root_require_read_authentication(self, runtime):
        client, state = runtime
        for path in ("/cockpit", "/"):
            denied = client.get(path)
            assert denied.status_code == 401
            assert denied.headers["www-authenticate"].startswith("Basic realm=")

        read_token = _run(state.device_tokens.enroll("browser", scopes=["read"]))
        response = client.get("/cockpit", headers=self._basic_headers(read_token["token"]))
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert "SYNDIKAT" in response.text

    def test_basic_auth_is_limited_to_read_routes_and_read_scope(self, runtime):
        client, state = runtime
        execute_only = _run(state.device_tokens.enroll("worker", scopes=["execute"]))
        denied = client.get("/cockpit", headers=self._basic_headers(execute_only["token"]))
        assert denied.status_code == 401

        read_token = _run(state.device_tokens.enroll("browser", scopes=["read"]))
        assert client.get("/status", headers=self._basic_headers(read_token["token"])).status_code == 401

    def test_proxy_and_admin_routes_fail_closed_without_master_key(self, runtime, monkeypatch):
        client, state = runtime
        state.api_key = None
        monkeypatch.setenv("APP_ENV", "development")

        # The development fallback stays available for a direct private
        # connection, but a reverse-proxied public request must not inherit the
        # proxy container's private socket address as trusted identity.
        import agent_runner

        monkeypatch.setattr(agent_runner, "_client_host", lambda _request: "127.0.0.1")
        assert client.get("/status").status_code == 200
        monkeypatch.setattr(agent_runner, "_client_host", lambda _request: "172.20.0.2")
        proxy_headers = {"X-Real-IP": "203.0.113.5", "X-Forwarded-For": "203.0.113.5"}
        assert client.get("/status", headers=proxy_headers).status_code == 401
        assert client.get("/floors", headers=proxy_headers).status_code == 401
        assert client.get("/cr/pending", headers=proxy_headers).status_code == 401

        # Device-admin routes never rely on the private development fallback.
        enroll = client.post("/auth/device/enroll", json={"device_id": "attacker"})
        assert enroll.status_code == 401

    def test_nginx_proxies_protected_pages_instead_of_serving_a_static_bypass(self):
        config = (REPO_ROOT / "config" / "nginx" / "nginx.conf").read_text(encoding="utf-8")
        assert "location = /cockpit {\n            proxy_pass http://eva_agent/cockpit;" in config
        assert "location = /floors {\n            limit_req zone=api burst=10 nodelay;\n            proxy_pass http://eva_agent/floors;" in config
        assert "location /cockpit/ {\n            return 404;" in config
        assert "alias /usr/share/nginx/static/;" not in config


# ─────────────────────────────────────────────────────────────────────────────
class TestExecuteStream:
    """0.4 — a 10-60 s run must not look like a dead connection."""

    def _events(self, text: str):
        """Parse an SSE body into [(event, data_dict)] — tolerates blank lines."""
        import json

        out = []
        event, data = None, []
        for line in text.splitlines():
            if line.startswith("event: "):
                event = line[7:]
            elif line.startswith("data: "):
                data.append(line[6:])
            elif line == "" and event is not None:
                out.append((event, json.loads("".join(data))))
                event, data = None, []
        if event is not None and data:
            out.append((event, json.loads("".join(data))))
        return out

    def test_stream_emits_accepted_then_result_then_done(self, runtime):
        client, _ = runtime
        r = client.post("/execute/stream", json={"task_type": "document_qa", "payload": {}},
                        headers={"X-API-Key": MASTER})
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/event-stream")
        events = self._events(r.text)
        kinds = [e for e, _ in events]
        assert kinds[0] == "accepted"
        assert "result" in kinds and kinds[-1] == "done"
        result = [d for e, d in events if e == "result"][0]
        assert result["status"] == "completed"
        assert result["result"] == {"answer": "done"}

    def test_stream_requires_auth(self, runtime):
        client, _ = runtime
        assert client.post("/execute/stream", json={"task_type": "document_qa", "payload": {}}).status_code == 401

    def test_stream_rejects_no_buffering_headers(self, runtime):
        client, _ = runtime
        r = client.post("/execute/stream", json={"task_type": "document_qa", "payload": {}},
                        headers={"X-API-Key": MASTER})
        assert r.headers.get("x-accel-buffering") == "no"
        assert "no-cache" in r.headers.get("cache-control", "")

    def test_stream_heartbeats_during_long_run(self, runtime):
        client, state = runtime
        state.orchestrator = _StubOrchestrator(delay=2.0)
        import agent_runner

        agent_runner.os.environ["EVAS_SSE_HEARTBEAT"] = "1"
        try:
            r = client.post("/execute/stream", json={"task_type": "document_qa", "payload": {}},
                            headers={"X-API-Key": MASTER})
        finally:
            agent_runner.os.environ.pop("EVAS_SSE_HEARTBEAT", None)
        events = self._events(r.text)
        assert [e for e, _ in events].count("heartbeat") >= 1
        assert [e for e, _ in events][-1] == "done"

    def test_stream_never_invents_progress(self, runtime):
        """Honesty contract: no synthetic progress while the graph cannot stream."""
        client, _ = runtime
        r = client.post("/execute/stream", json={"task_type": "document_qa", "payload": {}},
                        headers={"X-API-Key": MASTER})
        assert "progress" not in [e for e, _ in self._events(r.text)]

    def test_stream_reports_error_not_crash(self, runtime):
        client, state = runtime

        class Boom(_StubOrchestrator):
            async def execute(self, task_type, payload, session_id=None):  # noqa: ARG002
                raise RuntimeError("agent exploded")

        state.orchestrator = Boom()
        r = client.post("/execute/stream", json={"task_type": "document_qa", "payload": {}},
                        headers={"X-API-Key": MASTER})
        events = self._events(r.text)
        kinds = [e for e, _ in events]
        assert "error" in kinds and kinds[-1] == "done"
        assert "exploded" not in r.text  # internals are not leaked to the client

    def test_sse_helper_escapes_newlines(self):
        import agent_runner

        frame = agent_runner._sse("result", {"note": "line1\nline2"})
        assert frame.count("\n\n") == 1  # exactly one frame terminator
        assert frame.startswith("event: result\n")

    def test_sse_helper_survives_bytes_and_datetimes(self):
        import datetime

        import agent_runner

        frame = agent_runner._sse("result", {"blob": b"\x00\x01", "when": datetime.datetime.now()})
        assert "data: {" in frame
