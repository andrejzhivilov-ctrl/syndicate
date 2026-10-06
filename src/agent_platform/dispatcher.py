"""Policy-gated boundary used by LangGraph nodes to call a Hermes runtime."""

from __future__ import annotations

from dataclasses import dataclass, replace

import structlog

from src.agent_platform.audit import AgentAuditEvent, AgentAuditSink
from src.agent_platform.contracts import (
    AgentInvocation,
    AgentRuntime,
    DecisionStatus,
    DispatchStatus,
    PolicyDecision,
)
from src.agent_platform.policy import AgentPolicy
from src.agent_platform.registry import AgentRegistry
from src.pii import PIIRedactor

logger = structlog.get_logger(__name__)


@dataclass(frozen=True, slots=True)
class AgentDispatchResult:
    status: DispatchStatus
    decision: PolicyDecision
    content: str | None = None
    error_code: str | None = None


class AgentDispatcher:
    """Check explicit grants, redact input, invoke one runtime, and audit metadata.

    This dispatcher is an outer control-plane boundary. A Hermes implementation
    must separately ensure that internal tool calls are mediated by SYNDICATE's
    policy/tool gateways; no direct Hermes built-in toolset is enabled here.
    """

    def __init__(
        self,
        *,
        registry: AgentRegistry,
        runtime: AgentRuntime,
        audit_sink: AgentAuditSink,
        policy: AgentPolicy | None = None,
        pii_redactor: PIIRedactor | None = None,
    ) -> None:
        self._registry = registry
        self._runtime = runtime
        self._audit = audit_sink
        self._policy = policy or AgentPolicy()
        self._pii = pii_redactor or PIIRedactor()

    async def dispatch(self, request: AgentInvocation) -> AgentDispatchResult:
        profile = self._registry.get(request.access.agent_id)
        decision = self._policy.evaluate(profile, request.access)
        if decision.status is not DecisionStatus.ALLOWED:
            status = self._dispatch_status(decision.status)
            await self._record(request, decision, status)
            return AgentDispatchResult(status=status, decision=decision)

        # PIIRedactor returns original matches for diagnostics; deliberately drop
        # them here so they cannot enter logs, runtime metadata, or the audit sink.
        redacted_prompt, _redaction_events = self._pii.redact(request.prompt)
        safe_request = replace(request, prompt=redacted_prompt)
        try:
            content = await self._runtime.invoke(profile=profile, request=safe_request)
            if not isinstance(content, str):
                raise TypeError("runtime_response_must_be_text")
        except Exception as exc:  # noqa: BLE001 - do not leak provider exception text
            logger.warning(
                "agent_runtime_failed",
                agent_id=request.access.agent_id,
                request_id=request.request_id,
                error_type=type(exc).__name__,
            )
            await self._record(request, decision, DispatchStatus.FAILED)
            return AgentDispatchResult(
                status=DispatchStatus.FAILED,
                decision=decision,
                error_code="runtime_error",
            )

        await self._record(request, decision, DispatchStatus.COMPLETED)
        return AgentDispatchResult(
            status=DispatchStatus.COMPLETED,
            decision=decision,
            content=content,
        )

    async def _record(
        self,
        request: AgentInvocation,
        decision: PolicyDecision,
        status: DispatchStatus,
    ) -> None:
        event = AgentAuditEvent(
            request_id=request.request_id,
            task_id=request.task_id,
            agent_id=request.access.agent_id,
            action_class=request.access.action_class,
            decision_code=decision.code,
            status=status,
            requires_hitl=decision.status is DecisionStatus.APPROVAL_REQUIRED,
            allowed=decision.status is DecisionStatus.ALLOWED,
        )
        try:
            await self._audit.record(event)
        except Exception as exc:  # noqa: BLE001 - audit persistence is best-effort by contract
            logger.warning(
                "agent_platform_audit_failed",
                agent_id=request.access.agent_id,
                request_id=request.request_id,
                error_type=type(exc).__name__,
            )

    @staticmethod
    def _dispatch_status(status: DecisionStatus) -> DispatchStatus:
        if status is DecisionStatus.APPROVAL_REQUIRED:
            return DispatchStatus.APPROVAL_REQUIRED
        return DispatchStatus.DENIED
