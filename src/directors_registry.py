"""The 18 directors of the SYNDICATE holding — single source for roster data.

Names, roles, wings and bot handles come from the architecture manifest
(v5.0, 25 Oct 2026). This module holds *descriptive* data only: what a director
is allowed to do is decided by Vault policies, orchestrator config and the HITL
gate — never by this table.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from src.vault_paths import DIRECTOR_IDS, ISOLATED_WORKERS

#: id -> (display name, role, wing, bot handle)
_ROSTER: Dict[str, Tuple[str, str, str, str]] = {
    "eva": ("Єва", "CEO / Chief of Staff", "core", "SyndicateEvaBot"),
    "alice": ("Аліса", "Head of Delivery / R&D", "core", "SyndicateAliceBot"),
    "architect": ("Архітектор", "CTO / n8n", "core", "SyndicateArchitectBot"),
    "kodex": ("Кодекс", "CKO / Second Brain / Legal", "core", "SyndicateKodexBot"),
    "marshal": ("Маршал", "CSO / Sentinel Guard", "core", "SyndicateMarshalBot"),
    "sonar": ("Сонар", "Deep Research / Perplexity", "intelligence", "SyndicateSonarBot"),
    "fin": ("Фін", "CFO / Ledger", "intelligence", "SyndicateFinBot"),
    "sam": ("Сем", "Quant / Trading (paper)", "intelligence", "SyndicateSamBot"),
    "jack": ("Джек", "OSINT / Gaming models (simulation)", "intelligence", "SyndicateJackBot"),
    "scout": ("Скаут", "Trend Scout", "intelligence", "SyndicateScoutBot"),
    "oscar": ("Оскар", "Publicist (drafts only)", "commerce", "SyndicateOscarBot"),
    "tyler": ("Тайлер", "Print-on-Demand / Merch", "commerce", "SyndicateTylerBot"),
    "ray": ("Рей", "Physical Dropshipping (analysis only)", "commerce", "SyndicateRayBot"),
    "dex": ("Декс", "Affiliate / CPA", "commerce", "SyndicateDexBot"),
    "doc": ("Док", "CMO / Health / HRV", "lifeops", "SyndicateDocBot"),
    "trainer": ("Тренер", "Sport & Nutrition", "lifeops", "SyndicateTrainerBot"),
    "kira": ("Кіра", "Academy / Socratic mentor", "lifeops", "SyndicateKiraBot"),
    "atlas": ("Атлас", "Travel & Logistics", "lifeops", "SyndicateAtlasBot"),
}

#: Trainer also runs as an isolated container (deploy/docker-compose.directors.yml).
_CONTAINERISED = set(ISOLATED_WORKERS) | {"trainer"}


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
