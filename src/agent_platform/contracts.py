"""Neutral contracts for the SYNDICATE agent control plane.

This module deliberately describes no business roles and grants no default
capabilities. A runtime profile, its permissions, and its resource scopes must
be explicitly configured before a runtime can be dispatched.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Protocol


_PROFILE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")
_CAPABILITY_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:[._:-][a-z0-9]+)*$")
_SCOPE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")
_CORRELATION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_MAX_PROMPT_CHARS = 120_000


class RuntimeKind(str, Enum):
    """Supported runtime adapters; selecting one does not activate an agent."""

    HERMES = "hermes"
    ANTIGRAVITY_SDK = "antigravity_sdk"


class ActivationStatus(str, Enum):
    """Host-controlled runtime lifecycle; prepared profiles are never dispatchable."""

    PREPARED_NOT_ENABLED = "prepared_not_enabled"
    ENABLED = "enabled"


class ActionClass(str, Enum):
    """Host-assigned action category; never trust the model to classify itself."""

    INFORMATIONAL = "informational"
    BOUNDED_WRITE = "bounded_write"
    FINANCIAL_OPERATION = "financial_operation"
    DATA_DESTRUCTION = "data_destruction"
    SECURITY_CHANGE = "security_change"
    PRODUCTION_DEPLOYMENT = "production_deployment"
    EXTERNAL_COMMUNICATION = "external_communication"
    AUTHORITY_CHANGE = "authority_change"
    POLICY_CHANGE = "policy_change"
    SERVICE_CONNECTION = "service_connection"
    RESOURCE_EXPANSION = "resource_expansion"
    LOCATION_ACCESS = "location_access"


class DecisionStatus(str, Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    APPROVAL_REQUIRED = "approval_required"


class DecisionCode(str, Enum):
    ALLOWED = "allowed"
    UNKNOWN_AGENT = "unknown_agent"
    AGENT_MISMATCH = "agent_mismatch"
    AGENT_NOT_ENABLED = "agent_not_enabled"
    PROHIBITED_CAPABILITY = "prohibited_capability"
    CAPABILITY_NOT_GRANTED = "capability_not_granted"
    RESOURCE_SCOPE_REQUIRED = "resource_scope_required"
    RESOURCE_SCOPE_NOT_GRANTED = "resource_scope_not_granted"
    HUMAN_APPROVAL_REQUIRED = "human_approval_required"


class DispatchStatus(str, Enum):
    COMPLETED = "completed"
    DENIED = "denied"
    APPROVAL_REQUIRED = "approval_required"
    FAILED = "failed"


PROHIBITED_CAPABILITY_PREFIXES = frozenset(
    {
        "communication.email.send",
        "authentication.diia.login",
        "authentication.army_plus.login",
        "authentication.bankid.login",
        "browser.fingerprint.spoof",
        "network.residential_proxy.rotate",
    }
)


def capability_root(capability: str) -> str:
    """Return the first segment in a canonical capability identifier."""
    return re.split(r"[._:-]", capability, maxsplit=1)[0]


def is_prohibited_capability(capability: str) -> bool:
    """Return whether a capability is explicitly outside the platform scope."""
    separators = (".", "_", ":", "-")
    return any(
        capability == prefix
        or any(capability.startswith(f"{prefix}{separator}") for separator in separators)
        for prefix in PROHIBITED_CAPABILITY_PREFIXES
    )


def _freeze_identifiers(values: object, *, label: str, pattern: re.Pattern[str]) -> frozenset[str]:
    if isinstance(values, (str, bytes)):
        raise ValueError(f"{label}_must_be_a_collection")
    try:
        frozen = frozenset(values)  # type: ignore[arg-type]
    except TypeError as exc:
        raise ValueError(f"{label}_must_be_a_collection") from exc
    if any(not isinstance(value, str) for value in frozen):
        raise ValueError(f"invalid_{label}")
    if any("*" in value or ".." in value.split("/") for value in frozen):
        raise ValueError(f"wildcards_or_parent_paths_forbidden_in_{label}")
    if any(not pattern.fullmatch(value) for value in frozen):
        raise ValueError(f"invalid_{label}")
    return frozen


@dataclass(frozen=True, slots=True)
class AgentProfile:
    """An isolated runtime profile and its explicit, immutable grants.

    ``role``, prompts, model selection, and service credentials are intentionally
    absent: those agent-specific decisions are made later. Secret values must
    never be stored in this manifest.
    """

    agent_id: str
    runtime_profile: str
    memory_namespace: str
    capabilities: frozenset[str] = frozenset()
    resource_scopes: frozenset[str] = frozenset()
    runtime: RuntimeKind = RuntimeKind.HERMES
    activation_status: ActivationStatus = ActivationStatus.PREPARED_NOT_ENABLED

    def __post_init__(self) -> None:
        if not isinstance(self.agent_id, str) or not _PROFILE_ID_RE.fullmatch(self.agent_id):
            raise ValueError("invalid_agent_id")
        if not isinstance(self.runtime_profile, str) or not _PROFILE_ID_RE.fullmatch(self.runtime_profile):
            raise ValueError("invalid_runtime_profile")
        if not isinstance(self.memory_namespace, str) or not _SCOPE_ID_RE.fullmatch(self.memory_namespace):
            raise ValueError("invalid_memory_namespace")
        if "*" in self.memory_namespace or ".." in self.memory_namespace.split("/"):
            raise ValueError("wildcards_or_parent_paths_forbidden_in_memory_namespace")
        if not isinstance(self.runtime, RuntimeKind):
            raise ValueError("invalid_runtime_kind")
        if not isinstance(self.activation_status, ActivationStatus):
            raise ValueError("invalid_activation_status")

        capabilities = _freeze_identifiers(
            self.capabilities, label="capabilities", pattern=_CAPABILITY_ID_RE
        )
        if any(is_prohibited_capability(capability) for capability in capabilities):
            raise ValueError("prohibited_capability_cannot_be_granted")
        resource_scopes = _freeze_identifiers(
            self.resource_scopes, label="resource_scopes", pattern=_SCOPE_ID_RE
        )
        object.__setattr__(self, "capabilities", capabilities)
        object.__setattr__(self, "resource_scopes", resource_scopes)


@dataclass(frozen=True, slots=True)
class AccessRequest:
    """A host-authored permission check, separate from untrusted prompt text."""

    agent_id: str
    capability: str
    action_class: ActionClass = ActionClass.INFORMATIONAL
    resource_scope: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.agent_id, str) or not _PROFILE_ID_RE.fullmatch(self.agent_id):
            raise ValueError("invalid_agent_id")
        if not isinstance(self.capability, str) or not _CAPABILITY_ID_RE.fullmatch(self.capability):
            raise ValueError("invalid_capability")
        if not isinstance(self.action_class, ActionClass):
            raise ValueError("invalid_action_class")
        if self.resource_scope is not None:
            if not isinstance(self.resource_scope, str) or not _SCOPE_ID_RE.fullmatch(self.resource_scope):
                raise ValueError("invalid_resource_scope")
            if "*" in self.resource_scope or ".." in self.resource_scope.split("/"):
                raise ValueError("wildcards_or_parent_paths_forbidden_in_resource_scope")


@dataclass(frozen=True, slots=True)
class AgentInvocation:
    """A LangGraph-to-runtime request with no caller-supplied permission grants."""

    request_id: str
    task_id: str
    access: AccessRequest
    prompt: str

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not _CORRELATION_ID_RE.fullmatch(self.request_id):
            raise ValueError("invalid_request_id")
        if not isinstance(self.task_id, str) or not _CORRELATION_ID_RE.fullmatch(self.task_id):
            raise ValueError("invalid_task_id")
        if not isinstance(self.prompt, str) or len(self.prompt) > _MAX_PROMPT_CHARS:
            raise ValueError("invalid_prompt")


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    status: DecisionStatus
    code: DecisionCode


class AgentRuntime(Protocol):
    """Transport boundary for a configured agent runtime; not an adapter by itself."""

    async def invoke(self, *, profile: AgentProfile, request: AgentInvocation) -> str:
        """Run one bounded turn and return assistant text without logging it."""
