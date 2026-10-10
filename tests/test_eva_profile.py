"""Deployment-readiness checks for the Eva-only profile package."""

from __future__ import annotations

import json
import re
from pathlib import Path

from src.agent_platform.contracts import AgentProfile, RuntimeKind

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "config" / "agents" / "eva.profile.json"


def test_eva_manifest_is_prepared_but_not_enabled_and_has_no_grants() -> None:
    manifest = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    profile = AgentProfile(
        agent_id=manifest["agent_id"],
        hermes_profile=manifest["hermes_profile"],
        memory_namespace=manifest["memory_namespace"],
        capabilities=frozenset(manifest["capabilities"]),
        resource_scopes=frozenset(manifest["resource_scopes"]),
        runtime=RuntimeKind(manifest["runtime"]),
    )

    assert manifest["activation"] == "prepared_not_enabled"
    assert profile.runtime is RuntimeKind.HERMES
    assert profile.capabilities == frozenset()
    assert profile.resource_scopes == frozenset()
    assert manifest["services_enabled"] == []
    assert manifest["knowledge_bases"]["psychology"]["status"] == "not_loaded"
    telegram = manifest["inbound_channels"]["telegram"]
    assert telegram["enabled"] is False
    assert telegram["bot_id"] is None
    assert telegram["chat_allowlist"] == []


def test_nightly_schedule_is_three_am_kyiv_and_not_live_yet() -> None:
    manifest = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    schedule = manifest["nightly_analysis"]
    assert schedule["local_time"] == "03:00"
    assert schedule["timezone"] == "Europe/Kyiv"
    assert schedule["activation"] == "pending_n8n_workflow"
    assert schedule["source_provider"] == "not_configured"
    assert schedule["public_action_enabled"] is False
    assert schedule["audio_saved_by_default"] is False


def test_prompt_and_skill_files_exist_and_skill_ids_match_directories() -> None:
    manifest = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    prompt_path = ROOT / manifest["prompt_file"]
    assert prompt_path.is_file()
    assert "Ніколи не проси вставити" in prompt_path.read_text(encoding="utf-8")

    for skill in manifest["skills"]:
        assert skill["activation"] == "draft"
        path = ROOT / skill["path"]
        text = path.read_text(encoding="utf-8")
        frontmatter = re.search(r"\A---\s*\n(.*?)\n---", text, re.S)
        assert frontmatter
        name = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", frontmatter.group(1))
        assert name and name.group(1) == skill["id"]
        assert re.search(r"(?m)^status:\s*draft\s*$", frontmatter.group(1))
        assert not re.search(r"(?mi)^\s*(?:capabilities|permissions|api_key|token):", frontmatter.group(1))


def test_humanizer_does_not_claim_deceptive_provenance_or_fake_experience() -> None:
    text = (ROOT / "eva_core/skills/eva-humanizer/SKILL.md").read_text(encoding="utf-8").lower()
    assert "never claim the text is human-written" in text
    assert "never invent personal anecdotes or feelings" in text


def test_youtube_access_is_declared_but_not_enabled() -> None:
    manifest = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    sources = manifest["external_sources"]
    assert sources["youtube"]["status"] == "approved_by_andrii_2026-10-10_keys_pending_deploy"
    assert sources["youtube_music"]["status"] == "requires_andrii_decision"
    assert sources["youtube_music"]["official_api"] is False
    assert "завантаження відео чи аудіо з YouTube" in sources["youtube"]["not_allowed"]
    # YouTube не потрапляє в capabilities чи services: Єва без grants, доки Андрій не погодить
    assert manifest["capabilities"] == [] and manifest["services_enabled"] == []
