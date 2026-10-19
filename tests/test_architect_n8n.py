"""Live n8n mount: HITL, inactive-only, credentials from env not profile."""

from __future__ import annotations

import httpx

from src.agent_platform.contracts import AccessRequest, ActionClass, DecisionCode, DecisionStatus
from src.agent_platform.policy import AgentPolicy
from src.agents.architect import n8n_builder
from src.agents.architect_access import architect_agent_profile, architect_n8n_live_allowed, load_architect_manifest
from src.agents.architect_n8n import mount_inactive_workflow
from src.agents.architect_preview import deliver_after_confirm


def test_n8n_is_not_configured_and_prepared_architect_is_denied() -> None:
    manifest = load_architect_manifest()
    assert manifest["activation"] == "prepared_not_enabled"
    assert manifest["capabilities"] == []
    assert manifest["resource_scopes"] == []
    assert manifest["services_enabled"] == []
    assert all(grant["status"] == "proposed_not_applied" for grant in manifest["proposed_grants"])
    assert manifest["n8n"]["status"] == "not_configured"
    assert manifest["n8n"]["control_plane"] is False
    assert manifest["n8n"]["permission_source"] is False
    assert manifest["n8n"]["live_api"] is False
    assert manifest["n8n"]["create_active"] is False
    assert manifest["n8n"]["credentials_managed_in_profile"] is False
    assert architect_n8n_live_allowed(manifest) is False

    policy = AgentPolicy()
    profile = architect_agent_profile(manifest)
    for capability, action, scope in (
        ("n8n.workflow.design", ActionClass.BOUNDED_WRITE, None),
        ("n8n.workflow.mount", ActionClass.PRODUCTION_DEPLOYMENT, "n8n/live"),
        ("n8n.workflow.activate", ActionClass.PRODUCTION_DEPLOYMENT, "n8n/live"),
    ):
        decision = policy.evaluate(
            profile,
            AccessRequest(
                agent_id="architect",
                capability=capability,
                action_class=action,
                resource_scope=scope,
            ),
        )
        assert decision.status is DecisionStatus.DENIED
        assert decision.code is DecisionCode.AGENT_NOT_ENABLED


def test_future_n8n_policy_keeps_mount_human_gated() -> None:
    manifest = load_architect_manifest()
    hypothetical = dict(manifest)
    hypothetical["activation"] = "enabled"
    hypothetical["capabilities"] = ["n8n.workflow.design", "n8n.workflow.mount"]
    hypothetical["resource_scopes"] = ["n8n/live"]
    hypothetical["services_enabled"] = ["n8n"]
    hypothetical["n8n"] = {
        **manifest["n8n"],
        "status": "configured",
        "activation": "live_mount_after_hitl",
        "live_api": True,
    }
    assert architect_n8n_live_allowed(hypothetical) is True
    profile = architect_agent_profile(hypothetical)
    policy = AgentPolicy()
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
    assert missing["status"] == "denied"
    assert missing["error"] == "n8n_live_not_granted"
    assert missing["activates_n8n"] is False
    assert missing["calls_n8n_api"] is False


def test_approval_and_synthetic_credentials_cannot_bypass_unconfigured_policy() -> None:
    workflow = n8n_builder.build_workflow(name="live-mount", trigger="manual")
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"id": "should-not-be-called"})

    result = mount_inactive_workflow(
        workflow,
        approved=True,
        env={"N8N_BASE_URL": "http://n8n.internal:5678", "N8N_API_KEY": "synthetic-test-key"},
        transport=httpx.MockTransport(handler),
    )
    assert result["status"] == "denied"
    assert result["error"] == "n8n_live_not_granted"
    assert result["calls_n8n_api"] is False
    assert result["activates_n8n"] is False
    assert calls == []


def test_confirmed_delivery_still_denies_unconfigured_n8n() -> None:
    workflow = n8n_builder.build_workflow(name="deliver", trigger="manual")
    result = deliver_after_confirm(workflow, approved=True)
    assert result["activates_n8n"] is False
    assert result["status"] == "denied"
    assert result["calls_n8n_api"] is False
