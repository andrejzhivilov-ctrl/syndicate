"""Immutable registry for explicitly configured, isolated agent profiles."""

from __future__ import annotations

from collections.abc import Iterable
from types import MappingProxyType
from typing import Mapping

from src.agent_platform.contracts import AgentProfile, RuntimeKind


class AgentRegistry:
    """Resolve profile identifiers without inventing defaults or inherited grants."""

    def __init__(self, profiles: Iterable[AgentProfile] = ()) -> None:
        by_agent: dict[str, AgentProfile] = {}
        runtime_profiles: set[tuple[RuntimeKind, str]] = set()
        memory_namespaces: set[str] = set()

        for profile in profiles:
            runtime_key = (profile.runtime, profile.runtime_profile)
            if profile.agent_id in by_agent:
                raise ValueError("duplicate_agent_id")
            if runtime_key in runtime_profiles:
                raise ValueError("runtime_profile_must_be_isolated")
            if profile.memory_namespace in memory_namespaces:
                raise ValueError("memory_namespace_must_be_isolated")
            by_agent[profile.agent_id] = profile
            runtime_profiles.add(runtime_key)
            memory_namespaces.add(profile.memory_namespace)

        self._profiles: Mapping[str, AgentProfile] = MappingProxyType(by_agent)

    def get(self, agent_id: str) -> AgentProfile | None:
        """Return the registered profile, or ``None`` (never a default profile)."""
        return self._profiles.get(agent_id)

    @property
    def profiles(self) -> tuple[AgentProfile, ...]:
        """Return a stable, read-only snapshot suitable for inspection/tests."""
        return tuple(self._profiles[key] for key in sorted(self._profiles))
