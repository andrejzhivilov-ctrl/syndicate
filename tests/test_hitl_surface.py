"""
SYNDICATE — HITL client surface (backend blocker 0.5).

Motivation, so nobody "simplifies" this away:

  * Change Requests (protected changes that need a human) used to be approvable
    only from Telegram. The PC/mobile app must be a first-class approval surface:
    list the pending inbox, open a change, approve/reject, and be *pushed* the
    moment an agent proposes something.
  * Approving is sensitive, so a general device token ("read"/"execute") must NOT
    be able to do it. Only a token minted with scope "hitl" (or the master key).
  * The SSE push is in-process only — real OS push (FCM/APNs) is a separate
    client integration. We never invent a push event we cannot deliver.

Run with:  .venv/bin/python -m pytest tests/test_hitl_surface.py -q
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.change_requests import ChangeRequestError

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "deploy" / "runtime"))

MASTER = "sandbox-secret-api-key-2026"


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture()
def runtime(tmp_path):
    import agent_runner

    saved = {
        "api_key": agent_runner.app_state.api_key,
        "ready": agent_runner.app_state.ready,
        "device_tokens": agent_runner.app_state.device_tokens,
        "change_request_store": agent_runner.app_state.change_request_store,
        "change_request_notifier": agent_runner.app_state.change_request_notifier,
        "orchestrator": agent_runner.app_state.orchestrator,
        "sentinel": agent_runner.app_state.sentinel,
        "memory_manager": agent_runner.app_state.memory_manager,
    }

    from src.change_requests import ChangeRequestNotifier, ChangeRequestStore
    from src.device_auth import DeviceTokenStore
    from src.vault_md import MarkdownVault

    vault = MarkdownVault(root=tmp_path)
    notifier = ChangeRequestNotifier()
    cr_store = ChangeRequestStore(vault=vault, notifier=notifier)
    device_store = DeviceTokenStore(memory=None, default_ttl_seconds=3600)

    agent_runner.app_state.api_key = MASTER
    agent_runner.app_state.ready = True
    agent_runner.app_state.device_tokens = device_store
    agent_runner.app_state.change_request_store = cr_store
    agent_runner.app_state.change_request_notifier = notifier
    agent_runner.app_state.memory_manager = None
    agent_runner.app_state.orchestrator = _StubCrOrchestrator(cr_store)
    agent_runner.app_state.sentinel = _StubSentinel()

    client = TestClient(agent_runner.app)
    try:
        yield client, agent_runner.app_state, cr_store
    finally:
        for key, value in saved.items():
            setattr(agent_runner.app_state, key, value)


class _StubSentinel:
    async def validate_task(self, payload):  # noqa: ARG002
        class V:
            allowed = True
            reason = None

        return V()


class _StubCrOrchestrator:
    """Mirrors orchestrator._change_requests_handler so the HTTP layer is real."""

    def __init__(self, store) -> None:
        self.store = store

    async def execute(self, task_type, payload, session_id=None, *, operator_verified=False):  # noqa: ARG002
        try:
            if task_type == "submit_change_request":
                inner = self.store.submit(
                    title=payload.get("title", "Untitled"),
                    description=payload.get("description", ""),
                    target_path=payload.get("target_path", "statutes/test.md"),
                    proposed_content=payload.get("proposed_content", ""),
                    author=payload.get("author", "agent"),
                )
            elif task_type == "review_change_request":
                if not operator_verified:
                    inner = {"status": "error", "error": "operator_verification_required"}
                else:
                    inner = self.store.review(
                        cr_id=payload.get("cr_id", ""),
                        decision=payload.get("decision", "approve"),
                        reviewer="operator",
                        comment=payload.get("comment", ""),
                    )
            elif task_type == "apply_change_request":
                if not operator_verified:
                    inner = {"status": "error", "error": "operator_verification_required"}
                else:
                    inner = self.store.apply(cr_id=payload.get("cr_id", ""))
            else:
                inner = {"status": "error", "error": f"unknown:{task_type}"}
        except ChangeRequestError as exc:
            # Mirror the real handler: a missing / already-decided / self-approval
            # CR is an expected condition, not a crash.
            inner = {"status": "error", "error": str(exc)}
        # Mirror the real EvaOrchestrator.execute wrapper so the HTTP layer is
        # exercised against the same contract the client will see.
        return {"task_id": "t", "status": "completed", "result": inner}


# ─────────────────────────────────────────────────────────────────────────────
class TestInboxRead:
    def test_pending_starts_empty(self, runtime):
        client, _, store = runtime
        assert store is not None
        r = client.get("/cr/pending", headers={"X-API-Key": MASTER})
        assert r.status_code == 200 and r.json()["count"] == 0

    def test_submit_appears_in_pending(self, runtime):
        client, _, store = runtime
        submit = client.post(
            "/cr/submit",
            json={"title": "Tighten risk threshold", "target_path": "statutes/risk.md",
                  "proposed_content": "# risk\n"},
            headers={"X-API-Key": MASTER},
        )
        assert submit.status_code == 200
        cr_id = submit.json()["result"]["cr_id"]
        pend = client.get("/cr/pending", headers={"X-API-Key": MASTER}).json()
        assert pend["count"] == 1
        assert pend["pending"][0]["id"] == cr_id
        # Summary must NOT leak full proposed content into the inbox list.
        assert "proposed_content" not in pend["pending"][0]
        assert pend["pending"][0]["paths"] == ["statutes/risk.md"]

    def test_list_filters_by_status(self, runtime):
        client, _, store = runtime
        r = client.post(
            "/cr/submit",
            json={"title": "A", "target_path": "statutes/a.md", "proposed_content": "# a"},
            headers={"X-API-Key": MASTER},
        )
        cr_id = r.json()["result"]["cr_id"]
        client.post("/cr/review", json={"cr_id": cr_id, "decision": "approve"},
                    headers={"X-API-Key": MASTER})
        all_items = client.get("/cr/list", headers={"X-API-Key": MASTER}).json()
        pending = client.get("/cr/list?status=pending", headers={"X-API-Key": MASTER}).json()
        approved = client.get("/cr/list?status=approved", headers={"X-API-Key": MASTER}).json()
        assert all_items["count"] == 1 and pending["count"] == 0 and approved["count"] == 1

    def test_detail_includes_full_content(self, runtime):
        client, _, store = runtime
        r = client.post(
            "/cr/submit",
            json={"title": "B", "target_path": "statutes/b.md", "proposed_content": "# full body"},
            headers={"X-API-Key": MASTER},
        )
        cr_id = r.json()["result"]["cr_id"]
        detail = client.get(f"/cr/{cr_id}", headers={"X-API-Key": MASTER}).json()
        assert detail["changes"][0]["content"] == "# full body"
        assert detail["created_at_iso"] is not None  # unix float surfaced as ISO

    def test_detail_404_for_unknown(self, runtime):
        client, _, store = runtime
        r = client.get("/cr/CR-deadbeef", headers={"X-API-Key": MASTER})
        assert r.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
class TestHitlScopeEnforcement:
    def _token(self, runtime, scopes):
        client, state, _ = runtime
        issued = _run(state.device_tokens.enroll("phone", scopes=scopes))
        return issued["token"]

    def test_master_key_can_read_inbox(self, runtime):
        client, _, _ = runtime
        assert client.get("/cr/pending", headers={"X-API-Key": MASTER}).status_code == 200

    def test_hitl_scoped_token_can_read_inbox(self, runtime):
        client, _, _ = runtime
        token = self._token(runtime, ["hitl"])
        assert client.get("/cr/pending", headers={"X-API-Key": token}).status_code == 200

    def test_general_device_token_cannot_read_inbox(self, runtime):
        client, _, _ = runtime
        token = self._token(runtime, ["read"])
        assert client.get("/cr/pending", headers={"X-API-Key": token}).status_code == 401

    def test_token_without_any_scope_cannot_read_inbox(self, runtime):
        client, _, _ = runtime
        token = self._token(runtime, [])
        assert client.get("/cr/pending", headers={"X-API-Key": token}).status_code == 401

    def test_general_token_cannot_review(self, runtime):
        client, _, _ = runtime
        # create a CR with master key
        r = client.post(
            "/cr/submit",
            json={"title": "C", "target_path": "statutes/c.md", "proposed_content": "# c"},
            headers={"X-API-Key": MASTER},
        )
        cr_id = r.json()["result"]["cr_id"]
        read_token = self._token(runtime, ["read"])
        review = client.post("/cr/review", json={"cr_id": cr_id, "decision": "approve"},
                            headers={"X-API-Key": read_token})
        assert review.status_code == 401

    def test_hitl_token_can_review_and_apply(self, runtime):
        client, _, _ = runtime
        r = client.post(
            "/cr/submit",
            json={"title": "D", "target_path": "statutes/d.md", "proposed_content": "# d"},
            headers={"X-API-Key": MASTER},
        )
        cr_id = r.json()["result"]["cr_id"]
        hitl_token = self._token(runtime, ["hitl"])
        review = client.post("/cr/review", json={"cr_id": cr_id, "decision": "approve"},
                            headers={"X-API-Key": hitl_token})
        assert review.status_code == 200 and review.json()["result"]["status"] == "approved"
        apply = client.post("/cr/apply", json={"cr_id": cr_id}, headers={"X-API-Key": hitl_token})
        assert apply.status_code == 200 and apply.json()["result"]["status"] == "applied"
        # The protected change was actually written to the vault.
        detail = client.get(f"/cr/{cr_id}", headers={"X-API-Key": MASTER}).json()
        assert detail["status"] == "applied"

    def test_review_rejects_self_approval_author_is_operator(self, runtime):
        client, _, _ = runtime
        r = client.post(
            "/cr/submit",
            json={"title": "E", "target_path": "statutes/e.md", "proposed_content": "# e",
                  "author": "operator"},
            headers={"X-API-Key": MASTER},
        )
        cr_id = r.json()["result"]["cr_id"]
        hitl_token = self._token(runtime, ["hitl"])
        review = client.post(
            "/cr/review", json={"cr_id": cr_id, "decision": "approve", "reviewer": "operator"},
            headers={"X-API-Key": hitl_token},
        )
        # operator submitted and operator reviews -> self-approval must be refused.
        assert review.status_code == 200
        assert review.json()["result"]["status"] == "error"
        assert "author_cannot_approve_own_request" in review.json()["result"]["error"]

    def test_no_credential_is_rejected(self, runtime):
        client, _, _ = runtime
        assert client.get("/cr/pending").status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
class TestSsePush:
    def test_stream_requires_auth(self, runtime):
        client, _, _ = runtime
        # Without auth the SSE endpoint must refuse (401), not silently stream.
        with client.stream("GET", "/cr/stream") as r:
            assert r.status_code == 401

    def test_stream_rejects_non_hitl_token(self, runtime):
        client, state, _ = runtime
        issued = _run(state.device_tokens.enroll("phone", scopes=["read"]))
        with client.stream("GET", "/cr/stream", headers={"X-API-Key": issued["token"]}) as r:
            assert r.status_code == 401

    def test_event_stream_emits_connected_then_pending_cr(self, runtime):
        """Drive the SSE generator directly — deterministic, no live socket.

        Proves the app is pushed a ``pending_cr`` frame the moment an agent
        submits a change request, and that the frame carries the CR id. The
        generator subscribes to its own queue, so we publish through the
        notifier (as the store does) to fan out to it.
        """
        import agent_runner

        notifier = agent_runner.app_state.change_request_notifier

        async def _collect():
            gen = agent_runner._cr_event_stream(notifier)
            frames = []
            frames.append(await gen.__anext__())          # connected
            notifier.publish({
                "type": "pending_cr", "cr_id": "CR-abc12345", "risk": "high",
                "title": "Tighten threshold", "author": "agent", "created_at": 1.0,
            })
            frames.append(await gen.__anext__())          # pending_cr
            await gen.aclose()                            # unsubscribes, no hang
            return frames

        frames = _run(_collect())
        assert frames[0].startswith("event: connected")
        assert frames[1].startswith("event: pending_cr")
        assert "CR-abc12345" in frames[1]

    def test_event_stream_never_invents_progress(self, runtime):
        """The only frame emitted with no event is the initial 'connected'.

        No fabricated 'progress' frame for an agent that is not actually running.
        """
        import agent_runner

        notifier = agent_runner.app_state.change_request_notifier

        async def _collect():
            gen = agent_runner._cr_event_stream(notifier)
            frames = []
            frames.append(await gen.__anext__())          # connected
            # No event arrives; stop the generator immediately to avoid the
            # 30s heartbeat wait — the point is that nothing else was emitted.
            await gen.aclose()
            return frames

        frames = _run(_collect())
        assert len(frames) == 1
        assert frames[0].startswith("event: connected")
        assert "progress" not in frames[0]

    def test_openapi_lists_hitl_endpoints(self, runtime):
        client, _, _ = runtime
        schema = client.get("/openapi.json").json()
        for path in ("/cr/pending", "/cr/list", "/cr/stream", "/cr/{cr_id}"):
            assert path in schema["paths"]
        # /cr/review and /cr/apply are now HITL-protected, not general auth.
        assert "/cr/review" in schema["paths"]


# ─────────────────────────────────────────────────────────────────────────────
class TestNotifierUnit:
    def test_notifier_publishes_to_subscriber(self, tmp_path):
        from src.change_requests import ChangeRequestNotifier, ChangeRequestStore
        from src.vault_md import MarkdownVault

        vault = MarkdownVault(root=tmp_path)
        notifier = ChangeRequestNotifier()
        store = ChangeRequestStore(vault=vault, notifier=notifier)

        async def _run():
            queue = await notifier.subscribe()
            cr = store.create(author="agent", title="x", rationale="r",
                              changes=[{"path": "statutes/x.md", "content": "# x"}])
            event = await asyncio.wait_for(queue.get(), timeout=2)
            return cr, event

        cr, event = asyncio.run(_run())
        assert event["type"] == "pending_cr" and event["cr_id"] == cr["id"]

    def test_notifier_is_noop_without_subscribers(self, tmp_path):
        from src.change_requests import ChangeRequestStore
        from src.vault_md import MarkdownVault

        vault = MarkdownVault(root=tmp_path)
        store = ChangeRequestStore(vault=vault)  # no notifier
        # Must not raise even though nothing is subscribed.
        cr = store.create(author="agent", title="x", rationale="r",
                          changes=[{"path": "statutes/x.md", "content": "# x"}])
        assert cr["id"].startswith("CR-")
