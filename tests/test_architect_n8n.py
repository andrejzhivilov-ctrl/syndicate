"""Live n8n mount: HITL, inactive-only, credentials from env not profile."""

from __future__ import annotations

import json

import httpx

from src.agent_platform.contracts import AccessRequest, ActionClass, DecisionCode, DecisionStatus
from src.agent_platform.policy import AgentPolicy
from src.agents.architect import n8n_builder
from src.agents.architect_access import architect_agent_profile, architect_n8n_live_allowed, load_architect_manifest
from src.agents.architect_n8n import mount_inactive_workflow
from src.agents.architect_preview import deliver_after_confirm


def test_mount_grant_is_exact_and_activate_is_not_granted() -> None:
    manifest = load_architect_manifest()
    assert manifest["capabilities"] == ["n8n.workflow.design", "n8n.workflow.mount"]
    assert manifest["resource_scopes"] == ["n8n/live"]
    assert manifest["n8n"]["control_plane"] is False
    assert manifest["n8n"]["permission_source"] is False
    assert manifest["n8n"]["create_active"] is False
    assert manifest["n8n"]["credentials_managed_in_profile"] is False
    assert "n8n.workflow.activate" not in manifest["capabilities"]
    dumped = json.dumps(manifest)
    assert "N8N_API_KEY" not in dumped or manifest["n8n"]["api_key_env"] == "N8N_API_KEY"
    assert architect_n8n_live_allowed(manifest) is True
    policy = AgentPolicy()
    profile = architect_agent_profile(manifest)
    design = policy.evaluate(
        profile,
        AccessRequest(agent_id="architect", capability="n8n.workflow.design", action_class=ActionClass.BOUNDED_WRITE),
    )
    mount = policy.evaluate(
        profile,
        AccessRequest(
            agent_id="architect",
            capability="n8n.workflow.mount",
            action_class=ActionClass.PRODUCTION_DEPLOYMENT,
            resource_scope="n8n/live",
        ),
    )
    activate = policy.evaluate(
        profile,
        AccessRequest(
            agent_id="architect",
            capability="n8n.workflow.activate",
            action_class=ActionClass.PRODUCTION_DEPLOYMENT,
            resource_scope="n8n/live",
        ),
    )
    assert design.status is DecisionStatus.ALLOWED
    assert mount.status is DecisionStatus.APPROVAL_REQUIRED
    assert mount.code is DecisionCode.HUMAN_APPROVAL_REQUIRED
    assert activate.status is DecisionStatus.DENIED


def test_unapproved_or_missing_env_does_not_call_n8n() -> None:
    workflow = n8n_builder.build_workflow(name="live-mount", trigger="manual")
    cancelled = mount_inactive_workflow(workflow, approved=False)
    assert cancelled["status"] == "cancelled"
    assert cancelled["calls_n8n_api"] is False
    missing = mount_inactive_workflow(workflow, approved=True, env={})
    assert missing["status"] == "mount_unavailable"
    assert missing["activates_n8n"] is False
    assert missing["calls_n8n_api"] is False


def test_approved_mount_posts_inactive_workflow() -> None:
    workflow = n8n_builder.build_workflow(name="live-mount", trigger="manual")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url).endswith("/api/v1/workflows")
        body = json.loads(request.content)
        assert body["active"] is False
        assert request.headers["X-N8N-API-KEY"] == "test-n8n-key"
        return httpx.Response(200, json={"id": "wf-1"})

    result = mount_inactive_workflow(
        workflow,
        approved=True,
        env={"N8N_BASE_URL": "http://n8n.internal:5678", "N8N_API_KEY": "test-n8n-key"},
        transport=httpx.MockTransport(handler),
    )
    assert result["status"] == "mounted_inactive"
    assert result["n8n_workflow_id"] == "wf-1"
    assert result["activates_n8n"] is False
    assert result["active"] is False


def test_deliver_after_confirm_uses_mount_path() -> None:
    workflow = n8n_builder.build_workflow(name="deliver", trigger="manual")
    result = deliver_after_confirm(workflow, approved=True)
    assert result["activates_n8n"] is False
    assert result["status"] in {"mounted_inactive", "mount_unavailable"}
