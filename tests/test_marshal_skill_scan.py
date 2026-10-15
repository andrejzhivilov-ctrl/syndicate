"""SkillSpector wrapper: local --no-llm scan, never an install grant."""

from __future__ import annotations

from types import SimpleNamespace

from src.agents.marshal_skill_scan import marshal_skill_scan_allowed, scan_skill_proposal
from src.agents.marshal_access import load_marshal_manifest


def test_skill_scan_config_is_not_a_grant() -> None:
    manifest = load_marshal_manifest()
    scan = manifest["skill_scan"]
    assert manifest["skills"] == []
    assert manifest["capabilities"] == []
    assert scan["mode"] == "no_llm"
    assert scan["llm_pass"] is False
    assert scan["installs_skills"] is False
    assert scan["remote_urls"] is False
    assert marshal_skill_scan_allowed(manifest) is True


def test_missing_binary_is_unavailable_not_safe(tmp_path, monkeypatch) -> None:
    skill = tmp_path / "demo"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# demo\n", encoding="utf-8")
    monkeypatch.delenv("MARSHAL_SKILLSPECTOR_BIN", raising=False)
    monkeypatch.setattr("src.agents.marshal_skill_scan._LOCAL_BIN", tmp_path / "missing")
    result = scan_skill_proposal(skill, which=lambda _name: None)
    assert result["status"] == "scan_unavailable"
    assert result["error"] == "skillspector_not_installed"
    assert result["installs_skill"] is False
    assert result["recommendation"] == "unknown"


def test_remote_url_is_denied() -> None:
    result = scan_skill_proposal("https://github.com/example/skill")
    assert result["status"] == "denied"
    assert result["error"] == "remote_or_missing_path"


def test_mocked_scan_redacts_secrets_and_does_not_install(tmp_path) -> None:
    skill = tmp_path / "demo"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# demo\n", encoding="utf-8")

    def fake_run(command, **_kwargs):
        assert command[1] == "scan"
        assert "--no-llm" in command
        assert "--format" in command
        body = '{"risk_score": 77, "findings": [{"id": "x"}], "note": "sk-ant-abcdefghijklmnopqrstuv"}'
        return SimpleNamespace(returncode=0, stdout=body, stderr="Bearer abc.def")

    result = scan_skill_proposal(skill, runner=fake_run, which=lambda _name: "/usr/bin/skillspector")
    assert result["status"] == "scanned"
    assert result["installs_skill"] is False
    assert result["risk_score"] == 77
    assert result["recommendation"] == "do_not_install"
    assert result["findings_count"] == 1
    assert "sk-ant-" not in result["stderr_redacted"]
    assert "Bearer " not in result["stderr_redacted"]
