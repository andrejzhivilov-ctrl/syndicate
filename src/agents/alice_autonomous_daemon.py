"""
Alice (Antigravity) Autonomous Workstation Daemon (`src/agents/alice_autonomous_daemon.py`).

Because Alice (Antigravity) runs on a dedicated machine (Andrii's workstation / R&D node)
connected to the Contabo Cloud VPS 12 via `AntigravityBridge` (Tailscale / mTLS tunnel),
this autonomous background daemon enables Alice to act as a full peer of the 18-agent
SYNDICATE holding without waiting for manual chat prompts:

1. **03:30 Nightly Self-Reflection & Skill Genesis:**
   - Analyzes all commits, SaaS builds, scrapes, and tests executed during the day.
   - Identifies architectural bottlenecks, missing tools, and R&D opportunities.
   - Sends `CMD:KODEX_CREATE_AND_BIND_SKILL` to Kodex for new engineering/cloning skills.
2. **04:20 Mon & Thu Knowledge Audit (`CMD:ALICE_KNOWLEDGE_AUDIT_AND_OBSIDIAN_EXPORT`):**
   - Receives the knowledge harvest package uploaded by the 18 agents to NotebookLM at 04:00
     (under Marshal's supervision).
   - Performs deep structural & factual audit, builds cross-agent links, and writes clean
     Markdown notes directly into the local Obsidian Vault (`C:\\Second Brain\\`).
3. **06:45 & 20:45 Autonomous Reporting to Eva:**
   - Submits Alice's readiness status, task queue from agents, scheduled scrapes/SaaS builds,
     NotebookLM/Obsidian audit metrics, and **Alice's own R&D ideas & architectural proposals**
     to Eva over the bridge so Eva includes them in the 07:00 and 21:00 briefings.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class AliceAutonomousDaemon:
    """Autonomous background service for Alice (Antigravity) on her dedicated machine."""

    AGENT_ID = "alice"

    def __init__(
        self,
        obsidian_vault_path: Path | str = Path("C:/Second Brain"),
        workspace_root: Path | str = Path("."),
    ) -> None:
        self.obsidian_vault_path = Path(obsidian_vault_path)
        self.workspace_root = Path(workspace_root)

    def run_0330_self_reflection(
        self,
        date_str: str,
        commits_pushed: Optional[int] = None,
        saas_projects_active: Optional[List[str]] = None,
        scrapes_completed: Optional[int] = None,
        new_skills_to_request: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Builds the 03:30 reflection from facts the caller supplies.

        Zero-Faking: unknown counters stay ``None`` ("not measured") instead of
        defaulting to plausible numbers; there is no invented score, lessons or ideas.
        """
        skills = new_skills_to_request or []
        return {
            "agent_id": self.AGENT_ID,
            "date": date_str,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "execution_node": "alice_dedicated_machine",
            "commits_pushed": commits_pushed,
            "saas_projects_active": saas_projects_active or [],
            "scrapes_completed": scrapes_completed,
            "what_learned": [],
            "ideas_and_plans": [],
            "missing_resources": [],
            "kodex_skill_requests": [
                {
                    "command": "CMD:KODEX_CREATE_AND_BIND_SKILL",
                    "target_agent": "kodex",
                    "requested_by": self.AGENT_ID,
                    "skill_name": sk,
                    "scope": "shared_or_agent_specific",
                }
                for sk in skills
            ],
            "score": None,
        }

    def build_bridge_report_for_eva(
        self,
        period: str,
        date_str: str,
        queued_tasks_from_agents: Optional[List[str]] = None,
        notebooklm_packs_audited: Optional[int] = None,
        obsidian_notes_exported: Optional[int] = None,
        bridge_status: str = "UNKNOWN (not probed)",
    ) -> Dict[str, Any]:
        """Builds the 06:45 / 20:45 report. Everything is caller-supplied; nothing is made up."""
        queue = queued_tasks_from_agents or []
        return {
            "agent_id": self.AGENT_ID,
            "period": period,
            "date": date_str,
            "bridge_status": bridge_status,
            "queued_tasks_count": len(queue),
            "queued_tasks_from_agents": queue,
            "notebooklm_packs_audited": notebooklm_packs_audited,
            "obsidian_notes_exported": obsidian_notes_exported,
            "own_rd_ideas_and_proposals": [],
            "self_critique_summary": None,
        }
