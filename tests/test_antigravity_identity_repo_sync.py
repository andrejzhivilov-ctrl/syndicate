"""
Tests for Antigravity Identity Repository Synchronizer (`tools/sync_antigravity_identity_repo.py`).
Covers both success and failure/security scenarios per SOP.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.sync_antigravity_identity_repo import (
    REPO_IDENTITY_DIR,
    restore_identity_from_repo,
    sync_identity_to_repo,
    verify_repo_identity,
)


def test_committed_antigravity_identity_is_valid_and_complete() -> None:
    """Verify the repository's tracked `antigravity_identity/` directory passes SHA-256 and secret checks."""
    ok, errors = verify_repo_identity(REPO_IDENTITY_DIR)
    assert ok is True, f"Identity verification failed: {errors}"

    manifest = json.loads((REPO_IDENTITY_DIR / "IDENTITY_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["agent_id"] == "antigravity"
    assert manifest["rules_count"] >= 4
    assert manifest["skills_count"] >= 45
    assert manifest["mcp_categories_indexed"] == 70
    assert manifest["mcp_servers_cataloged"] == 18789

    required_skills = {
        "syndicate-app-cloner",
        "syndicate-n8n-and-prompts",
        "syndicate-mcp-navigator",
        "replica-recon",
        "replica-test",
        "api-and-interface-design",
        "context-engineering",
        "debugging-and-error-recovery",
        "test-driven-development",
        "agent-security-hardening",
        "kodex-notebooklm",
        "kodex-obsidian",
    }
    assert required_skills.issubset(set(manifest["skills"]))
    assert (REPO_IDENTITY_DIR / "rules" / "standard_operating_procedure.md").is_file()
    assert (REPO_IDENTITY_DIR / "rules" / "antigravity_syndicate_identity.md").is_file()
    assert (REPO_IDENTITY_DIR / "memory" / "CORE_IDENTITY_AND_MEMORY.md").is_file()
    assert (REPO_IDENTITY_DIR / "mcp" / "mcp_practical_arsenal.json").is_file()


def test_sync_scrubs_secrets_and_pii_before_writing_to_repo(tmp_path: Path) -> None:
    """Ensure API tokens and PII in live config are automatically scrubbed before hitting the repo."""
    fake_gemini = tmp_path / "gemini_config"
    (fake_gemini / "rules").mkdir(parents=True)
    (fake_gemini / "skills" / "custom-skill").mkdir(parents=True)

    leaked_token = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
    leaked_anthropic = "sk-ant-api03-SecretKeyMaterial1234567890abcdef"
    (fake_gemini / "rules" / "test_rule.md").write_text(
        f"Never expose token {leaked_token} or email secret.user@example.com\r\n",
        encoding="utf-8",
    )
    (fake_gemini / "skills" / "custom-skill" / "SKILL.md").write_text(
        f"---\nname: custom-skill\n---\nKey: {leaked_anthropic}\n",
        encoding="utf-8",
    )

    out_identity = tmp_path / "repo_identity"
    manifest = sync_identity_to_repo(
        gemini_config_dir=fake_gemini,
        repo_identity_dir=out_identity,
        install_repo_skills=False,
    )
    assert manifest["rules_count"] == 1
    assert manifest["skills_count"] == 1

    rule_content = (out_identity / "rules" / "test_rule.md").read_text(encoding="utf-8")
    skill_content = (out_identity / "skills" / "custom-skill" / "SKILL.md").read_text(encoding="utf-8")

    assert leaked_token not in rule_content
    assert "secret.user@example.com" not in rule_content
    assert "\r" not in rule_content
    assert leaked_anthropic not in skill_content

    ok, errors = verify_repo_identity(out_identity)
    assert ok is True, f"Expected clean verification, got {errors}"


def test_verify_detects_tampering_and_injected_secrets(tmp_path: Path) -> None:
    """Failure scenario: tampering with a tracked file or injecting a raw token must fail verification."""
    fake_gemini = tmp_path / "gemini_config"
    (fake_gemini / "rules").mkdir(parents=True)
    (fake_gemini / "rules" / "sop.md").write_text("# Clean SOP\n", encoding="utf-8")

    out_identity = tmp_path / "repo_identity"
    sync_identity_to_repo(
        gemini_config_dir=fake_gemini,
        repo_identity_dir=out_identity,
        install_repo_skills=False,
    )

    # Inject a raw GitHub token directly into the synced file without scrubbing
    raw_token = "ghp_" + "Z9y8X7w6V5u4T3s2R1q0P9o8N7m6L5k4J3i2"
    (out_identity / "rules" / "sop.md").write_text(f"# Tampered {raw_token}\n", encoding="utf-8")

    ok, errors = verify_repo_identity(out_identity)
    assert ok is False
    assert any("SHA-256 mismatch" in e for e in errors)
    assert any("Secret pattern detected" in e for e in errors)


def test_restore_identity_from_repo_roundtrip(tmp_path: Path) -> None:
    """Verify a fresh VM target directory can be hydrated from `antigravity_identity/`."""
    vm_config_dir = tmp_path / "vm_gemini_config"
    res = restore_identity_from_repo(target_config_dir=vm_config_dir, repo_identity_dir=REPO_IDENTITY_DIR)

    assert res["status"] == "restored"
    assert res["skills_count"] >= 45
    assert res["rules_count"] >= 4
    assert (vm_config_dir / "rules" / "standard_operating_procedure.md").is_file()
    assert (vm_config_dir / "rules" / "antigravity_syndicate_identity.md").is_file()
    assert (vm_config_dir / "skills" / "syndicate-app-cloner" / "SKILL.md").is_file()
    assert (vm_config_dir / "skills" / "replica-recon" / "SKILL.md").is_file()
    assert (vm_config_dir / "memory" / "CORE_IDENTITY_AND_MEMORY.md").is_file()


def test_all_skills_have_valid_yaml_frontmatter() -> None:
    """Every SKILL.md in antigravity_identity/skills must have valid YAML frontmatter with name and description."""
    import yaml

    skill_files = sorted((REPO_IDENTITY_DIR / "skills").rglob("SKILL.md"))
    assert len(skill_files) >= 48
    for p in skill_files:
        text = p.read_text(encoding="utf-8")
        assert text.startswith("---"), f"Missing frontmatter delimiter in {p}"
        parts = text.split("---", 2)
        assert len(parts) >= 3, f"Unclosed frontmatter in {p}"
        data = yaml.safe_load(parts[1])
        assert isinstance(data, dict), f"Frontmatter is not a YAML mapping in {p}"
        assert data.get("name"), f"Missing 'name' in frontmatter of {p}"
        assert data.get("description"), f"Missing 'description' in frontmatter of {p}"

