"""Scoped adapter seams for shared SYNDICATE memory and external services."""

from __future__ import annotations

import re
from typing import Any, Mapping, Protocol

from src.agent_platform.contracts import (
    AccessRequest,
    ActionClass,
    AgentProfile,
    DecisionStatus,
    PolicyDecision,
)
from src.agent_platform.policy import AgentPolicy
from src.pii import PIIRedactor


class MemoryManagerPort(Protocol):
    async def get_recent_episodes(
        self,
        session_id: str,
        agent_id: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Structural subset of ``MemoryManager`` used by this adapter."""

    async def save_episode(
        self,
        session_id: str | None = None,
        agent_id: str = "eva",
        role: str = "assistant",
        content: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Append an episodic-memory record."""


class MemoryAccessDenied(PermissionError):
    """Fixed-code denial raised before a memory backend can be touched."""

    def __init__(self, decision: PolicyDecision) -> None:
        self.decision = decision
        super().__init__(f"memory_access_denied:{decision.code.value}")


class MemoryManagerAdapter:
    """Bind the existing MemoryManager to one profile and one task session.

    The caller cannot supply a different namespace: reads and writes are always
    keyed by the profile's unique ``memory_namespace``. ``memory.read`` and
    ``memory.write`` are checked separately before the backend is touched. Text
    is PII-redacted; metadata is limited to short, allow-listed identifiers.
    """

    MAX_RECALL = 50
    _ROLES = frozenset({"user", "assistant", "system", "tool"})
    _METADATA_KEYS = frozenset({"category", "kind", "status", "task_type"})
    _SAFE_METADATA_VALUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$")

    def __init__(
        self,
        *,
        memory: MemoryManagerPort,
        profile: AgentProfile,
        session_id: str,
        pii_redactor: PIIRedactor | None = None,
        policy: AgentPolicy | None = None,
    ) -> None:
        if not isinstance(session_id, str) or not session_id or len(session_id) > 128:
            raise ValueError("invalid_session_id")
        self._memory = memory
        self._profile = profile
        self._session_id = session_id
        self._pii = pii_redactor or PIIRedactor()
        self._policy = policy or AgentPolicy()

    async def recall(self, *, limit: int = 20) -> list[dict[str, Any]]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= self.MAX_RECALL:
            raise ValueError("recall_limit_out_of_range")
        self._authorize("memory.read", ActionClass.INFORMATIONAL)
        return await self._memory.get_recent_episodes(
            session_id=self._session_id,
            agent_id=self._profile.memory_namespace,
            limit=limit,
        )

    async def save(
        self,
        *,
        role: str,
        content: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        if role not in self._ROLES:
            raise ValueError("invalid_memory_role")
        if not isinstance(content, str):
            raise ValueError("memory_content_must_be_text")
        self._authorize("memory.write", ActionClass.BOUNDED_WRITE)
        redacted_content, _redaction_events = self._pii.redact(content)
        safe_metadata = self._safe_metadata(metadata)
        return await self._memory.save_episode(
            session_id=self._session_id,
            agent_id=self._profile.memory_namespace,
            role=role,
            content=redacted_content,
            metadata=safe_metadata,
        )

    def _authorize(self, capability: str, action_class: ActionClass) -> None:
        decision = self._policy.evaluate(
            self._profile,
            AccessRequest(
                agent_id=self._profile.agent_id,
                capability=capability,
                action_class=action_class,
                resource_scope=self._profile.memory_namespace,
            ),
        )
        if decision.status is not DecisionStatus.ALLOWED:
            raise MemoryAccessDenied(decision)

    @classmethod
    def _safe_metadata(cls, metadata: Mapping[str, Any] | None) -> dict[str, str]:
        if not isinstance(metadata, Mapping):
            return {}
        return {
            key: value
            for key in sorted(cls._METADATA_KEYS)
            if isinstance((value := metadata.get(key)), str)
            and cls._SAFE_METADATA_VALUE.fullmatch(value)
        }


class ServiceAdapter(Protocol):
    """A service backend invoked only behind an explicit, policy-checked tool.

    Implementations must bind operations to a host-owned tool contract, check
    capability/action/resource scope with ``AgentPolicy`` before side effects,
    and never log arguments or returned private content. The existing
    ``ToolRegistry`` is not automatically wired to this policy yet.
    """

    async def invoke(
        self,
        *,
        resource_scope: str,
        operation: str,
        arguments: Mapping[str, object],
    ) -> object:
        """Perform one allow-listed operation against one explicit resource."""
