"""Fail-closed capability and human-approval policy for the agent platform."""

from __future__ import annotations

from src.agent_platform.contracts import (
    AccessRequest,
    ActionClass,
    AgentProfile,
    DecisionCode,
    DecisionStatus,
    PolicyDecision,
    capability_root,
    is_prohibited_capability,
)


HUMAN_APPROVAL_ACTIONS = frozenset(
    {
        ActionClass.FINANCIAL_OPERATION,
        ActionClass.DATA_DESTRUCTION,
        ActionClass.SECURITY_CHANGE,
        ActionClass.PRODUCTION_DEPLOYMENT,
        ActionClass.EXTERNAL_COMMUNICATION,
        ActionClass.AUTHORITY_CHANGE,
        ActionClass.POLICY_CHANGE,
        ActionClass.SERVICE_CONNECTION,
        ActionClass.RESOURCE_EXPANSION,
        ActionClass.LOCATION_ACCESS,
    }
)


class AgentPolicy:
    """Shared policy gate; model confidence never substitutes for authorization."""

    def evaluate(
        self,
        profile: AgentProfile | None,
        request: AccessRequest,
    ) -> PolicyDecision:
        if profile is None:
            return PolicyDecision(DecisionStatus.DENIED, DecisionCode.UNKNOWN_AGENT)
        if profile.agent_id != request.agent_id:
            return PolicyDecision(DecisionStatus.DENIED, DecisionCode.AGENT_MISMATCH)
        if is_prohibited_capability(request.capability):
            return PolicyDecision(DecisionStatus.DENIED, DecisionCode.PROHIBITED_CAPABILITY)
        if request.capability not in profile.capabilities:
            return PolicyDecision(DecisionStatus.DENIED, DecisionCode.CAPABILITY_NOT_GRANTED)
        scope_error = self._resource_scope_error(profile, request)
        if scope_error is not None:
            return scope_error
        if request.action_class in HUMAN_APPROVAL_ACTIONS:
            return PolicyDecision(DecisionStatus.APPROVAL_REQUIRED, DecisionCode.HUMAN_APPROVAL_REQUIRED)
        return PolicyDecision(DecisionStatus.ALLOWED, DecisionCode.ALLOWED)

    @staticmethod
    def _resource_scope_error(profile: AgentProfile, request: AccessRequest) -> PolicyDecision | None:
        is_scoped = capability_root(request.capability) in {"memory", "service", "location"}
        if is_scoped and request.resource_scope is None:
            return PolicyDecision(DecisionStatus.DENIED, DecisionCode.RESOURCE_SCOPE_REQUIRED)
        if request.resource_scope is not None:
            own_memory = (
                capability_root(request.capability) == "memory"
                and request.resource_scope == profile.memory_namespace
            )
            if not own_memory and request.resource_scope not in profile.resource_scopes:
                return PolicyDecision(DecisionStatus.DENIED, DecisionCode.RESOURCE_SCOPE_NOT_GRANTED)
        return None
