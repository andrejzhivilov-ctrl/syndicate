"""Retired Antigravity director placeholder; Antigravity is runtime technology.

The old independently addressable director is deliberately not registered.
This class name is retained for import compatibility but exposes no external
operations. Alice is the agent identity; the Antigravity SDK is only her runtime.
"""

from __future__ import annotations

from typing import ClassVar

from src.agents.director_base import DirectorAgent


class AntigravityDirectorAgent(DirectorAgent):
    """Compatibility descriptor with no operational grants or side effects."""

    AGENT_ID = "alice"
    ACTIONS: ClassVar[dict[str, str]] = {"capabilities": "capabilities"}

    async def capabilities(self, _payload: dict) -> dict:
        return {
            "status": "ok",
            "agent_id": self.AGENT_ID,
            "runtime": "antigravity_sdk",
            "role": "engineering runtime descriptor",
            "available_actions": ["capabilities"],
            "grants_level": "none",
            "external_actions": False,
            "activation": "prepared_not_enabled",
        }
