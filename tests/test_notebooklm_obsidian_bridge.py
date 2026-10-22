"""
Unit tests for NotebookLM ↔ Obsidian Bridge, Kodex Agent, Eva Morning Briefing,
and Cold Disaster Recovery Flash Bundle.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from src.agents.eva import EvaAgent
from src.agents.kodex import KodexAgent
from src.integrations.notebooklm_obsidian_bridge import KnowledgeCard, NotebookLMObsidianBridge
from tools.export_cold_recovery_bundle import create_cold_recovery_bundle


def test_notebooklm_obsidian_bridge_export_and_deduplication(tmp_path: Path):
    vault = tmp_path / "obsidian_vault"
    bridge = NotebookLMObsidianBridge(vault_path=vault)

    # 1. First export
    res1 = bridge.synthesize_and_export(
        agent_id="kodex",
        title="GDPR Compliance in Multi-Agent Architecture",
        raw_content="All PII data must be redacted at boundary.",
        category="legal",
        key_insights=["Zero plain PII to external LLMs", "Audit logs stored securely"],
        backlinks=["Security", "Marshal"],
        tags=["gdpr", "compliance"],
    )
    assert res1["status"] == "exported"
    target_file = Path(res1["path"])
    assert target_file.exists()

    content = target_file.read_text(encoding="utf-8")
    assert 'title: "GDPR Compliance in Multi-Agent Architecture"' in content
    assert "- [[Security]]" in content
    assert "- [[Marshal]]" in content
    assert "agent: \"kodex\"" in content

    # 2. Second export with identical content (Deduplication Check)
    res2 = bridge.synthesize_and_export(
        agent_id="kodex",
        title="GDPR Compliance in Multi-Agent Architecture",
        raw_content="All PII data must be redacted at boundary.",
        category="legal",
        key_insights=["Zero plain PII to external LLMs", "Audit logs stored securely"],
    )
    assert res2["status"] == "duplicate_skipped"


def test_obsidian_user_notes_scanning(tmp_path: Path):
    vault = tmp_path / "obsidian_vault"
    bridge = NotebookLMObsidianBridge(vault_path=vault)

    # Create a note written by Andrii
    user_note = bridge.user_dir / "Directive_November.md"
    user_note.write_text("# Directive\nFocus heavily on mobile app performance and offline sync.", encoding="utf-8")

    scanned = bridge.scan_user_notes()
    assert len(scanned) == 1
    assert scanned[0]["title"] == "Directive_November"
    assert "Focus heavily on mobile app" in scanned[0]["snippet"]


def test_kodex_agent_notebooklm_obsidian_actions(tmp_path: Path):
    vault = tmp_path / "obsidian_vault"
    bridge = NotebookLMObsidianBridge(vault_path=vault)
    agent = KodexAgent(config={"obsidian_vault_path": str(vault)}, bridge=bridge)

    async def _run():
        # 1. Capabilities
        caps = await agent.execute({"action": "capabilities"})
        assert caps["agent"] == "kodex"
        assert "NotebookLM" in caps["integrations"]

        # 2. Process with NotebookLM and export
        proc_res = await agent.execute({
            "action": "process_with_notebooklm",
            "title": "Biohacking Protocol 2026",
            "content": "Deep research on sleep optimization and HRV.",
            "category": "health",
            "key_insights": ["HRV baseline 55ms+", "Cold showers boost noradrenaline"],
            "backlinks": ["Doc", "Trainer"],
            "cleanup": True,
        })
        assert proc_res["status"] == "exported"
        assert Path(proc_res["path"]).exists()

        # 3. Read user notes
        notes_res = await agent.execute({"action": "scan_user_notes"})
        assert notes_res["status"] == "ok"

    asyncio.run(_run())


def test_eva_morning_briefing_contains_disaster_recovery_status():
    eva = EvaAgent(memory=None, llm=None)

    async def _run():
        res = await eva.execute({
            "action": "compose_briefing",
            "agent_data": {
                "doc": {"readiness_score": 90, "zone": "green"},
                "fin": {"runway_months": 24},
                "marshal": {"status": "nominal"},
                "kira": {"focus": "Agent Orchestration"},
            },
        })
        briefing = res.get("response", "")
        # Operator requirement: mandatory disaster recovery readiness line
        mandatory_line = (
            "🛡️ Статус безпеки: Бекап знаходиться у стані готовності до вигрузки на флеш носій "
            "(Disaster Recovery Ready)."
        )
        assert mandatory_line in briefing

    asyncio.run(_run())


def test_cold_recovery_bundle_generation(tmp_path: Path):
    dest = tmp_path / "usb_drive"
    bundle_path = create_cold_recovery_bundle(
        dest_dir=dest,
        include_antigravity=False,
        include_obsidian=False,
    )
    assert bundle_path.exists()
    assert bundle_path.stat().st_size > 0

    manifests = list(dest.glob("*.manifest.json"))
    assert len(manifests) == 1
    manifest_data = json.loads(manifests[0].read_text(encoding="utf-8"))
    assert manifest_data["status"] == "ready_for_physical_flash_export"
    assert "PostgreSQL & pgvector" in manifest_data["included_components"]

    # Check that standalone restore scripts were generated for USB drive
    assert (dest / "restore_syndicate.py").exists()
    assert (dest / "restore_syndicate.sh").exists()
    assert (dest / "restore_syndicate.bat").exists()
