"""The seven SYNDICATE agents and the bots kept without an agent — single source for roster data.

The roster follows Andrii's decision of 4 Nov 2026 (docs/MIGRATION_7_AGENTS.md). This module
holds *descriptive* data only: what a director is allowed to do is decided by Vault policies,
orchestrator config and the HITL gate — never by this table.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from src.vault_paths import DIRECTOR_IDS

#: id -> (display name, role, wing, bot handle)
_ROSTER: Dict[str, Tuple[str, str, str, str]] = {
    "eva": ("Єва", "CEO / Assistant / System status / Travel / Archive", "core", "SyndicateEvaBot"),
    "trainer": ("Алекс", "Health: training, nutrition, biomarkers", "lifeops", "SyndicateTrainerBot"),
    "kira": ("Кіра", "Academy / Socratic mentor", "lifeops", "SyndicateKiraBot"),
    "fin": ("Фін", "CFO / Ledger", "intelligence", "SyndicateFinBot"),
    "sam": ("Сем", "Quant: trading and sports models (paper)", "intelligence", "SyndicateSamBot"),
    "tyler": ("Тайлер", "Business and content", "commerce", "SyndicateTylerBot"),
    "marshal": ("Маршал", "CSO / Sentinel Guard", "core", "SyndicateMarshalBot"),
    "alice": ("Аліса", "Bot without an agent: alarm feed", "channel", "SyndicateAliceBot"),
    "kodex": ("Кодекс", "Bot without an agent", "channel", "SyndicateKodexBot"),
}

#: The old worker containers were removed on 04.11.2026; Alex runs on Hermes (its own
#: container, deploy/docker-compose.hermes.yml), the rest inside eva-agent.
_CONTAINERISED = {"trainer"}


def roster() -> List[Dict[str, str]]:
    """Static roster in manifest order. Contains no live status."""
    missing = set(DIRECTOR_IDS) - set(_ROSTER)
    if missing:  # a new director was added to vault_paths without a roster entry
        raise RuntimeError(f"directors_registry is missing: {sorted(missing)}")
    out = []
    for agent_id in DIRECTOR_IDS:
        name, role, wing, handle = _ROSTER[agent_id]
        out.append(
            {
                "id": agent_id,
                "name": name,
                "role": role,
                "wing": wing,
                "bot_handle": f"@{handle}",
                "runtime": "container" if agent_id in _CONTAINERISED else "in-process",
            }
        )
    return out
