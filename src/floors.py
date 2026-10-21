"""
SYNDICATE — Directorial Boardroom & Neural Core Registry.

Architectural Paradigm:
The hierarchical 10-floor skyscraper model is superseded by the Directorial Round Table
and Neural Core topology (Radial peer-to-peer network surrounding the shared core).
All agents sit as Directors and Specialists around the circular command core.

Legacy floor constants (FLOORS, active_floors, floor_of) are maintained as compatibility
aliases so existing worker contracts and tests remain completely functional.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# ─── Boardroom Directorial Topology ──────────────────────────────────────────

BOARDROOM_DIRECTORS: Dict[str, Dict[str, Any]] = {
    "eva": {
        "title": "Chief of Staff & Core Moderator",
        "department": "Strategy & Core Command",
        "role": "Strategic coordination, daily briefing, operator interface",
    },
    "architect": {
        "title": "Chief Technology Officer",
        "department": "Systems & Engineering",
        "role": "System architecture, n8n design, code synthesis, Antigravity Bridge",
    },
    "marshal": {
        "title": "Chief Security Officer",
        "department": "Security & Sentinel Protocol",
        "role": "Zero-trust validation, outbound action veto, prompt injection shield",
    },
    "fin": {
        "title": "Chief Financial Officer",
        "department": "Capital & Financial Governance",
        "role": "Banking sync, runway management, capital audit, basket approvals",
    },
    "sam": {
        "title": "Director of Quant & Capital Markets",
        "department": "Quant Trading & Markets",
        "role": "Confluence analysis, position sizing, market intelligence",
    },
    "doc": {
        "title": "Chief Medical Officer",
        "department": "Clinical Medicine & Diagnostics",
        "role": "Biomarkers, preventative screenings, pre-visit dossiers, clinical recovery",
    },
    "trainer": {
        "title": "Head of Physical Performance & Lifestyle",
        "department": "Performance & Nutrition",
        "role": "Workout protocols, Mifflin-St Jeor TDEE, meal plans, basket lists, habits",
    },
    "kira": {
        "title": "Dean of Academy & Knowledge Synthesis",
        "department": "Academy & Mentorship",
        "role": "Socratic dialogue, code reviews, language training, micro-quizzes",
    },
    "oscar": {
        "title": "Creative Director",
        "department": "Media & Creative Operations",
        "role": "Viral shorts, video prompt enhancement, POD mockups, release packs",
    },
    "tyler": {
        "title": "Director of Operations & Supply Chain",
        "department": "Operations & Commerce",
        "role": "Supplier verification, price comparison, order fulfillment",
    },
    "jack": {
        "title": "Director of Probabilistic Analytics",
        "department": "Quant Risk & Game Theory",
        "role": "Odds evaluation, anti-tilt tracking, probabilistic modeling",
    },
    "alice": {
        "title": "SDK & Systems Integration Engineer",
        "department": "Platform SDK & Workers",
        "role": "Autonomous code review, Hermes worker bridge, SDK engineering",
    },
    "kodex": {
        "title": "Chief Archivist & Knowledge Custodian",
        "department": "Knowledge Base & Archives",
        "role": "Obsidian sync, NotebookLM integration, prompt and skill cataloging",
    },
    "antigravity": {
        "title": "Chief External Super-Agent & Deep Engineer",
        "department": "External High-Cognitive Bridge",
        "role": "High-complexity reasoning, app cloning, reverse engineering, system scaling",
    },
}

# ─── Legacy Compatibility Mapping (Preserved for existing imports) ───────────

FLOORS: Dict[int, Dict[str, Any]] = {
    10: {
        "name": "Командний центр (Command & Governance)",
        "agents": ["eva", "fin", "marshal", "architect"],
        "services": ["council", "orc_verifier", "change_requests", "sentinel"],
        "status": "active",
    },
    9: {
        "name": "Здоров'я, форма та енергія (Health & Performance)",
        "agents": ["doc", "trainer"],
        "services": [],
        "status": "active",
    },
    8: {
        "name": "SYNDICATE Academy",
        "agents": ["kira"],
        "services": ["socratic_tutor"],
        "status": "active",
    },
    7: {
        "name": "Квант & капітал (Quant & Markets)",
        "agents": ["sam"],
        "services": [],
        "status": "active",
    },
    6: {"name": "Резервний сектор 6", "agents": [], "services": [], "status": "reserved"},
    5: {"name": "Резервний сектор 5", "agents": [], "services": [], "status": "reserved"},
    4: {"name": "Резервний сектор 4", "agents": [], "services": [], "status": "reserved"},
    3: {"name": "Резервний сектор 3", "agents": [], "services": [], "status": "reserved"},
    2: {
        "name": "Контент-завод (Media & Creative Operations)",
        "agents": ["floor2_coordinator", "oscar"],
        "services": ["humanizer", "video_prompt_enhancer", "release_pack"],
        "status": "active",
    },
    1: {
        "name": "Сервер & сенсорика (Sensory & Ingestion)",
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
