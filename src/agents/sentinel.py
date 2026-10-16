"""
Sentinel Protocol — Backward-Compatibility Layer for Marshal (Chief Security Officer).

NOTE: Sentinel is NOT a separate LLM agent.
All security functions in SYNDICATE are commanded solely by Marshal (CSO, Floor 10).
All security gate validations (inbound prompt injection scans, outbound vetoes,
lethal trifecta guard, destructive command blocking, slopsquatting checks, secret redaction,
and HMAC verification) run as deterministic, zero-token Python algorithms (0 tokens burned).

This module re-exports MarshalAgent as SentinelAgent to preserve backward compatibility
with existing orchestration pipelines while guaranteeing 0 token burn.
"""

from __future__ import annotations

from src.agents.marshal import (
    MarshalAgent,
    ValidationResult,
    OUTBOUND_POLICIES,
    BLOCKED_TASK_TYPES,
    SUSPICIOUS_PACKAGES,
)

# SentinelAgent is an exact alias for MarshalAgent — no extra agent, no extra token cost
SentinelAgent = MarshalAgent

__all__ = [
    "SentinelAgent",
    "MarshalAgent",
    "ValidationResult",
    "OUTBOUND_POLICIES",
    "BLOCKED_TASK_TYPES",
    "SUSPICIOUS_PACKAGES",
]
