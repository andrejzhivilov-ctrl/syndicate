"""
Tool Contracts — narrow, validated, audited tools for agents.

Each tool declares: input schema, risk level, which agents may call it,
whether it is idempotent and whether a human must approve. The registry
enforces schema validation, least privilege, risk gating, duplicate-action
protection (idempotency keys), output size caps and secret-free audit logs.
"""

from __future__ import annotations

import inspect
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence

import structlog

from src.pii import PIIRedactor

logger = structlog.get_logger(__name__)

_TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict}
RISK_LEVELS = ("read", "draft", "write", "critical")


@dataclass
class ToolContract:
    name: str
    description: str
    handler: Callable[..., Any]
    input_schema: Dict[str, Dict[str, Any]]          # {"field": {"type": "string", "required": True, "enum": [...]}}
    risk: str = "read"
    allowed_agents: Sequence[str] = field(default_factory=tuple)   # empty = nobody (explicit grants only)
    idempotent: bool = True
    requires_hitl: Optional[bool] = None             # default: True for critical
    max_output_chars: int = 8000

    def __post_init__(self) -> None:
        if self.risk not in RISK_LEVELS:
            raise ValueError(f"bad_risk:{self.risk}")
        if self.requires_hitl is None:
            self.requires_hitl = self.risk == "critical"


@dataclass
class ToolResult:
    status: str                  # ok | invalid_input | forbidden | pending_approval | duplicate | error | unknown_tool
    output: Any = None
    detail: str = ""
    from_cache: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {"status": self.status, "output": self.output, "detail": self.detail, "from_cache": self.from_cache}


class ToolRegistry:
    def __init__(self, pii: Optional[PIIRedactor] = None) -> None:
        self._tools: Dict[str, ToolContract] = {}
        self._pii = pii or PIIRedactor()
        self._idem: Dict[str, ToolResult] = {}
        self.audit_log: List[Dict[str, Any]] = []

    def register(self, tool: ToolContract) -> None:
        self._tools[tool.name] = tool

    def catalogue(self, agent_id: str) -> List[Dict[str, Any]]:
        """Only the tools an agent may use — never the whole key ring."""
        return [
            {"name": t.name, "description": t.description, "risk": t.risk, "schema": t.input_schema}
            for t in self._tools.values() if agent_id in t.allowed_agents
        ]

    @staticmethod
    def validate(schema: Dict[str, Dict[str, Any]], args: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        for key in args:
            if key not in schema:
                errors.append(f"unexpected_field:{key}")
        for key, rule in schema.items():
            if key not in args:
                if rule.get("required"):
                    errors.append(f"missing_field:{key}")
                continue
            val = args[key]
            expected = _TYPES.get(rule.get("type", "string"), str)
            if isinstance(val, bool) and rule.get("type") in ("integer", "number"):
                errors.append(f"bad_type:{key}")
            elif not isinstance(val, expected):
                errors.append(f"bad_type:{key}")
            elif "enum" in rule and val not in rule["enum"]:
                errors.append(f"not_in_enum:{key}")
            elif isinstance(val, str) and "max_len" in rule and len(val) > rule["max_len"]:
                errors.append(f"too_long:{key}")
        return errors

    def _audit(self, agent_id: str, tool: str, args: Dict[str, Any], result: ToolResult) -> None:
        safe_args, _ = self._pii.redact(str(args)[:500])
        self.audit_log.append({
            "ts": time.time(), "agent": agent_id, "tool": tool, "args": safe_args,
            "status": result.status, "cached": result.from_cache,
        })
        if len(self.audit_log) > 5000:
            del self.audit_log[:1000]

    async def call(
        self,
        tool_name: str,
        args: Dict[str, Any],
        caller: str,
        idempotency_key: Optional[str] = None,
        approved: bool = False,
    ) -> ToolResult:
        tool = self._tools.get(tool_name)
        if tool is None:
            res = ToolResult("unknown_tool", detail=tool_name)
            self._audit(caller, tool_name, args, res)
            return res
        if caller not in tool.allowed_agents:
            res = ToolResult("forbidden", detail=f"{caller}_not_granted_{tool_name}")
            self._audit(caller, tool_name, args, res)
            return res
        errors = self.validate(tool.input_schema, args)
        if errors:
            res = ToolResult("invalid_input", detail=",".join(errors))
            self._audit(caller, tool_name, args, res)
            return res
        if tool.requires_hitl and not approved:
            res = ToolResult("pending_approval", detail=f"risk={tool.risk}")
            self._audit(caller, tool_name, args, res)
            return res

        cache_key = f"{tool_name}:{idempotency_key}" if idempotency_key else None
        if cache_key and cache_key in self._idem:
            cached = self._idem[cache_key]
            res = ToolResult(cached.status, cached.output, "duplicate_suppressed", from_cache=True)
            self._audit(caller, tool_name, args, res)
            return res

        try:
            out = tool.handler(**args)
            if inspect.isawaitable(out):
                out = await out
            if isinstance(out, str) and len(out) > tool.max_output_chars:
                out = out[: tool.max_output_chars] + "…[truncated]"
            res = ToolResult("ok", out)
        except Exception as exc:  # noqa: BLE001
            logger.warning("tool_failed", tool=tool_name, error=str(exc))
            res = ToolResult("error", detail=f"{type(exc).__name__}")
        if cache_key and res.status == "ok":
            self._idem[cache_key] = res
        self._audit(caller, tool_name, args, res)
        return res
