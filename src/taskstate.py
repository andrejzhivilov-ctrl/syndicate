"""
Task State vs Long-term Memory.

* TaskState  — working context of ONE task (steps, drafts, scratch). Discarded
  or archived when the task closes.
* MemoryPolicy — decides what may become long-term memory:
  save / ask (needs operator confirmation) / deny (secrets, drafts) / discard.
* TaskStateStore.close() promotes only policy-approved items to memory.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import structlog

from src.pii import PIIRedactor

logger = structlog.get_logger(__name__)

SAVE_KINDS = {"lesson", "config_change", "operator_command", "decision", "preference", "fact"}
ASK_KINDS = {"medical_protocol_change", "trading_limit_change", "financial_limit_change", "contact_share"}
DENY_KINDS = {"scratch", "draft", "raw_transcript", "intermediate_thought", "credential"}


@dataclass
class TaskState:
    task_id: str
    agent_id: str
    goal: str
    created_at: float = field(default_factory=time.time)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    scratch: Dict[str, Any] = field(default_factory=dict)
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "open"

    def add_step(self, name: str, detail: Any = None, ok: bool = True) -> None:
        self.steps.append({"name": name, "detail": detail, "ok": ok, "ts": time.time()})

    def checkpoint(self, label: str) -> Dict[str, Any]:
        cp = {"label": label, "steps_done": len(self.steps), "scratch_keys": sorted(self.scratch), "ts": time.time()}
        self.checkpoints.append(cp)
        return cp


@dataclass
class PolicyDecision:
    action: str          # save | ask | deny | discard
    reason: str


class MemoryPolicy:
    def __init__(self, pii: Optional[PIIRedactor] = None) -> None:
        self._pii = pii or PIIRedactor()

    def decide(self, item: Dict[str, Any]) -> PolicyDecision:
        kind = str(item.get("kind", "")).lower()
        content = str(item.get("content", ""))
        redacted, _events = self._pii.redact(content)
        if kind in DENY_KINDS:
            return PolicyDecision("deny", f"kind_not_storable:{kind}")
        if "[REDACTED_KEY]" in redacted:
            return PolicyDecision("deny", "contains_secret")
        if kind in ASK_KINDS:
            return PolicyDecision("ask", f"operator_confirmation_required:{kind}")
        if kind in SAVE_KINDS:
            return PolicyDecision("save", f"auto_save:{kind}")
        return PolicyDecision("discard", f"unknown_kind:{kind or 'none'}")


class TaskStateStore:
    def __init__(self, memory: Optional[Any] = None, policy: Optional[MemoryPolicy] = None) -> None:
        self._memory = memory
        self._policy = policy or MemoryPolicy()
        self._open: Dict[str, TaskState] = {}
        self.pending_confirmation: List[Dict[str, Any]] = []

    def open(self, task_id: str, agent_id: str, goal: str) -> TaskState:
        st = TaskState(task_id, agent_id, goal)
        self._open[task_id] = st
        return st

    def get(self, task_id: str) -> Optional[TaskState]:
        return self._open.get(task_id)

    async def close(self, task_id: str, promote: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        st = self._open.pop(task_id, None)
        if st is None:
            return {"status": "unknown_task"}
        st.status = "closed"
        saved, asked, denied, discarded = [], [], [], []
        for item in promote or []:
            d = self._policy.decide(item)
            if d.action == "save":
                saved.append(item)
                if self._memory is not None and hasattr(self._memory, "save_episode"):
                    try:
                        await self._memory.save_episode(
                            session_id=task_id, agent_id=st.agent_id, role="memory",
                            content=str(item.get("content", "")),
                            metadata={"kind": item.get("kind"), "promoted_from_task": task_id},
                        )
                    except Exception as exc:  # noqa: BLE001
                        logger.warning("taskstate_promote_failed", error=str(exc))
            elif d.action == "ask":
                self.pending_confirmation.append({**item, "agent_id": st.agent_id, "task_id": task_id, "reason": d.reason})
                asked.append(item)
            elif d.action == "deny":
                denied.append({"kind": item.get("kind"), "reason": d.reason})
            else:
                discarded.append(item)
        return {
            "status": "closed", "task_id": task_id, "steps_dropped": len(st.steps),
            "saved": len(saved), "asked": len(asked), "denied": denied, "discarded": len(discarded),
        }
