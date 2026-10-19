"""Common, role-neutral SYNDICATE agent-platform contracts."""

from src.agent_platform.adapters import MemoryAccessDenied, MemoryManagerAdapter, ServiceAdapter
from src.agent_platform.audit import AgentAuditEvent, MemoryManagerAuditSink
from src.agent_platform.contracts import (
    AccessRequest,
    ActionClass,
    ActivationStatus,
    AgentInvocation,
    AgentProfile,
    DecisionCode,
    DecisionStatus,
    DispatchStatus,
    RuntimeKind,
)
from src.agent_platform.dispatcher import AgentDispatcher, AgentDispatchResult
from src.agent_platform.policy import AgentPolicy
from src.agent_platform.registry import AgentRegistry

__all__ = [
    "AccessRequest",
    "ActionClass",
    "ActivationStatus",
    "AgentAuditEvent",
    "AgentDispatcher",
    "AgentDispatchResult",
    "AgentInvocation",
    "AgentPolicy",
    "AgentProfile",
    "AgentRegistry",
    "DecisionCode",
    "DecisionStatus",
    "DispatchStatus",
    "MemoryAccessDenied",
    "MemoryManagerAdapter",
    "MemoryManagerAuditSink",
    "RuntimeKind",
    "ServiceAdapter",
]
