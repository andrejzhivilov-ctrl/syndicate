"""Which of the seven agents owns each part of the system (operator, 04.11.2026).

The holding went from 19 agents to 7. The old agents' code stays where it is
for now, as parts of their new owner: nine old director containers still
import it by its old path until stage 4 of docs/MIGRATION_7_AGENTS.md stops
them. Their storage ids (``data/<id>``) stay too, so no record is lost.

``owner_of`` answers "whose work is this?" for every routing target of the
orchestrator. An unknown id has no owner (``None``): a new route must be
given one here, never fall to Eva silently.
"""
from __future__ import annotations

from typing import Dict, Optional

from src.vault_paths import AGENT_ROSTER

#: Old agents and what they became part of.
MERGED_INTO: Dict[str, str] = {
    "doc": "trainer",      # Alex: health
    "jack": "sam",         # bets join trading
    "scout": "tyler",      # business and content
    "sonar": "tyler",
    "dex": "tyler",
    "ray": "tyler",
    "oscar": "tyler",
    "atlas": "eva",        # travel
    "kodex": "eva",        # archive, Obsidian, NotebookLM, evening summary
}

#: Orchestrator subsystems that are not agents of their own.
SUBSYSTEMS: Dict[str, str] = {
    "eva_curator": "eva",
    "eva_office": "eva",
    "memory_command": "eva",
    "proactive": "eva",
    "sensory": "eva",
    "council": "eva",
    "orc_verifier": "eva",
    "floor_registry": "eva",
    "reserved_floor": "eva",
    "change_requests": "eva",
    "vault": "eva",
    "n8n_templates": "eva",         # n8n leaves in stage 6
    "error_collector": "eva",       # Eva watches the system's state
    "floor2": "tyler",              # content factory
    "floor2_enhancer": "tyler",
    "kira_socratic": "kira",
    "sentinel": "marshal",
    # Removed as agents in stage 3; engineering goes to Claude Code.
    "alice": "eva",
    "architect": "eva",
    "antigravity_gateway": "eva",
}


def owner_of(agent_id: Optional[str]) -> Optional[str]:
    """The roster agent that owns ``agent_id``, or None if nobody does."""
    if agent_id in AGENT_ROSTER:
        return agent_id
    if agent_id in MERGED_INTO:
        return MERGED_INTO[agent_id]
    return SUBSYSTEMS.get(agent_id or "")
