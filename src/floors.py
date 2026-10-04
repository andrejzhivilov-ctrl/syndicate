"""
EVA SYNDICATE — floor registry (single source of truth).

Agents with a strict specialisation (Doc, Kira, Sam) own their floor and are
never handed foreign duties; they only report/propose inside their competence.
Floors 3-6 are reserved (no agent defined yet) and are exposed explicitly as
``reserved`` so nothing silently depends on them.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

FLOORS: Dict[int, Dict[str, Any]] = {
    10: {
        "name": "Командний поверх",
        "agents": ["eva", "fin", "marshal", "architect"],
        "services": ["council", "orc_verifier", "change_requests", "sentinel"],
        "status": "active",
    },
    9: {"name": "Здоров'я та енергія", "agents": ["doc"], "services": [], "status": "active"},
    8: {"name": "SYNDICATE Academy", "agents": ["kira"], "services": ["socratic_tutor"], "status": "active"},
    7: {"name": "Квант & капітал", "agents": ["sam"], "services": [], "status": "active"},
    6: {"name": "Резерв", "agents": [], "services": [], "status": "reserved"},
    5: {"name": "Резерв", "agents": [], "services": [], "status": "reserved"},
    4: {"name": "Резерв", "agents": [], "services": [], "status": "reserved"},
    3: {"name": "Резерв", "agents": [], "services": [], "status": "reserved"},
    2: {
        "name": "Контент-завод",
        "agents": ["floor2_coordinator"],
        "services": ["humanizer", "video_prompt_enhancer", "release_pack"],
        "status": "active",
    },
    1: {
        "name": "Сервер & n8n",
        "agents": [],
        "services": ["sensory_router", "error_collector", "n8n_templates", "scheduler"],
        "status": "active",
    },
}

AGENT_FLOOR: Dict[str, int] = {
    agent: floor for floor, meta in FLOORS.items() for agent in meta["agents"]
}


def floor_of(agent_id: str) -> Optional[int]:
    return AGENT_FLOOR.get(agent_id)


def active_floors() -> List[int]:
    return sorted(f for f, m in FLOORS.items() if m["status"] == "active")


def reserved_floors() -> List[int]:
    return sorted(f for f, m in FLOORS.items() if m["status"] == "reserved")
