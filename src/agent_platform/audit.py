"""Privacy-minimized adapter to SYNDICATE's append-only decision audit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.agent_platform.contracts import ActionClass, DecisionCode, DispatchStatus


@dataclass(frozen=True, slots=True)
class AgentAuditEvent:
    """Only identifiers and fixed status codes; never includes prompt/output/scope."""

    request_id: str
    task_id: str
    agent_id: str
    action_class: ActionClass
    decision_code: DecisionCode
    status: DispatchStatus
    requires_hitl: bool
    allowed: bool


class AgentAuditSink(Protocol):
    async def record(self, event: AgentAuditEvent) -> bool:
        """Append an event; ``False`` means best-effort persistence was unavailable."""


class DecisionAuditWriter(Protocol):
    async def write_audit_decision(
        self,
        *,
        agent_id: str,
        action: str,
        task_type: str | None = None,
        escalation: str | None = None,
        outcome: str = "pending",
        hitl_override: bool = False,
        details: dict[str, object] | None = None,
    ) -> bool:
        """Structural subset of ``MemoryManager.write_audit_decision``."""


class MemoryManagerAuditSink:
    """Write only the existing allow-listed fields to ``audit.decisions``."""

    _OUTCOMES = {
        DispatchStatus.COMPLETED: "success",
        DispatchStatus.DENIED: "blocked",
        DispatchStatus.APPROVAL_REQUIRED: "pending",
        DispatchStatus.FAILED: "failure",
    }
    _ESCALATIONS = {
        DispatchStatus.COMPLETED: "act",
        DispatchStatus.DENIED: "refuse",
        DispatchStatus.APPROVAL_REQUIRED: "ask",
        DispatchStatus.FAILED: "refuse",
    }

    def __init__(self, memory: DecisionAuditWriter) -> None:
        self._memory = memory

    async def record(self, event: AgentAuditEvent) -> bool:
        return await self._memory.write_audit_decision(
            agent_id=event.agent_id,
            action=f"agent_platform_{event.decision_code.value}",
            task_type=event.action_class.value,
            escalation=self._ESCALATIONS[event.status],
            outcome=self._OUTCOMES[event.status],
            hitl_override=False,
            details={
                "task_id": event.task_id,
                "result_status": event.status.value,
                "requires_hitl": event.requires_hitl,
                "allowed": event.allowed,
            },
        )
