"""End-to-end safety checks for Eva chat, durable memory, and nightly analysis."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import pytest

from src.agents.eva import EvaAgent
from src.memory_commands import execute_command, parse_command
from src.proactive import ProactiveScheduler
from src.vault_md import MarkdownVault, VaultError


class _LLM:
    def __init__(self, response: str) -> None:
        self.response = response
        self.prompts = []

    async def ainvoke(self, messages):
        self.prompts.append(messages)
        return type("Reply", (), {"content": self.response})()


class _Memory:
    def __init__(self) -> None:
        self.saved = []

    async def save_episode(self, **kwargs):
        self.saved.append(kwargs)


def _run(coro):
    return asyncio.run(coro)


def test_regular_chat_never_saves_user_or_assistant_turns(tmp_path) -> None:
    vault = MarkdownVault(vault_root=tmp_path / "vault")
    memory = _Memory()
    llm = _LLM("Відповідь без довготривалого запису.")
    agent = EvaAgent(memory=memory, llm=llm, vault=vault)

    result = _run(agent.execute({"action": "chat", "message": "Привіт, обговорімо ідею."}))

    assert result["status"] == "completed"
    assert memory.saved == []
    assert not vault.exists("agents/eva/memory.md")
    assert not vault.exists("raw/memory_review.md")


def test_explicit_low_sensitivity_remember_writes_provenance_to_obsidian(tmp_path) -> None:
    vault = MarkdownVault(vault_root=tmp_path / "vault")
    agent = EvaAgent(memory=None, llm=None, vault=vault)

    result = _run(agent.execute({
        "action": "chat",
        "message": "Запам'ятай: Obsidian є канонічним архівом проєкту.",
    }))

    content = vault.read("agents/eva/memory.md")
    assert result["status"] == "created"
    assert "Obsidian є канонічним архівом" in content
    assert "date=" in content and "source=explicit_memory_request" in content
    assert "confirmed=yes" in content


def test_sensitive_request_is_only_a_review_draft(tmp_path) -> None:
    vault = MarkdownVault(vault_root=tmp_path / "vault")
    agent = EvaAgent(memory=None, llm=None, vault=vault)

    result = _run(agent.execute({
        "action": "chat",
        "message": "Запам'ятай: я проходжу психологічну терапію.",
    }))

    assert result["status"] == "review_required"
    assert result["memory_command"]["draft_stored"] is True
    assert vault.exists("raw/memory_review.md")
    assert not vault.exists("agents/eva/memory.md")
    assert "confirmed=no" in vault.read("raw/memory_review.md")


def test_secret_like_chat_is_refused_before_llm_or_storage(tmp_path) -> None:
    secret = "ghp_abcdefghijklmnopqrstuvwxyz0123456789"
    vault = MarkdownVault(vault_root=tmp_path / "vault")
    llm = _LLM("This should never be called.")
    agent = EvaAgent(memory=None, llm=llm, vault=vault)

    result = _run(agent.execute({"action": "chat", "message": f"Запам'ятай token={secret}"}))

    assert result["status"] == "refused"
    assert llm.prompts == []
    assert not vault.exists("agents/eva/memory.md")
    assert not vault.exists("raw/memory_review.md")
    assert secret not in str(result)


def test_memory_duplicate_does_not_overwrite_and_forget_requires_confirmation(tmp_path) -> None:
    vault = MarkdownVault(vault_root=tmp_path / "vault")
    first = parse_command("Запам'ятай: Canonical archive is Obsidian.")
    assert first is not None
    assert execute_command(first, vault)["status"] == "created"
    original = vault.read("agents/eva/memory.md")

    duplicate = execute_command(first, vault)
    assert duplicate["status"] == "confirmation_required"
    assert vault.read("agents/eva/memory.md") == original

    update = parse_command("Онови: canonical archive is obsidian: Obsidian remains the canonical archive.")
    assert update is not None and update.kind == "update"
    updated = execute_command(update, vault)
    assert updated["status"] == "updated"
    assert "Obsidian remains the canonical archive" in vault.read("agents/eva/memory.md")
    assert "superseded" in vault.read("archive/eva.md")
    after_update = vault.read("agents/eva/memory.md")

    forget = parse_command("Забудь: canonical archive is obsidian")
    assert forget is not None
    assert execute_command(forget, vault)["status"] == "confirmation_required"
    assert vault.read("agents/eva/memory.md") == after_update

    archived = execute_command(forget, vault, operator_confirmed_forget=True)
    assert archived["status"] == "archived"
    assert "forgotten" in vault.read("archive/eva.md")
    assert "Canonical archive is Obsidian" not in vault.read("agents/eva/memory.md")


def test_direct_generic_write_cannot_bypass_memory_policy(tmp_path) -> None:
    vault = MarkdownVault(vault_root=tmp_path / "vault")
    with pytest.raises(VaultError, match="managed_memory_path_requires_policy_gate"):
        vault.write("agents/eva/memory.md", "unreviewed content")
    with pytest.raises(VaultError, match="managed_memory_path_requires_policy_gate"):
        vault.write("raw/memory_review.md", "unreviewed content")


def test_nightly_archive_rechecks_secret_location_and_sensitive_content(tmp_path) -> None:
    vault = MarkdownVault(vault_root=tmp_path / "vault")

    secret = vault.archive_nightly_summary("password=hunter2-with-enough-length", "2026-10-08")
    location = vault.archive_nightly_summary("Coordinates: 48.45123, 35.04123", "2026-10-08")
    sensitive = vault.archive_nightly_summary("Психологічний стан: високий рівень тривоги", "2026-10-08")

    assert secret["status"] == "refused"
    assert location["status"] == "refused"
    assert sensitive["status"] == "review_required"
    assert not vault.list_files("archive/nightly")


def test_curator_only_archives_explicit_low_sensitivity_records_and_drafts_contacts(tmp_path) -> None:
    from src.agents.eva_curator import EvaCurator

    vault = MarkdownVault(vault_root=tmp_path / "vault")
    memory = _Memory()
    curator = EvaCurator(memory=memory, llm=None, vault=vault)

    decision = _run(curator.execute({
        "action": "record_decision",
        "decision": "Use Obsidian for the project archive.",
        "reasoning": "This was explicitly agreed.",
    }))
    contact = _run(curator.execute({
        "action": "add_contact",
        "name": "Alex",
        "relationship": "friend",
        "notes": "Prefers email.",
    }))

    assert decision["memory_write"]["status"] == "created"
    assert "date=" in vault.read("agents/eva/memory.md")
    assert contact["memory_write"]["status"] == "review_required"
    assert vault.exists("raw/memory_review.md")
    assert memory.saved == []


def test_unknown_actions_fail_closed_instead_of_falling_back_to_chat() -> None:
    llm = _LLM("Should not be invoked.")
    agent = EvaAgent(memory=None, llm=llm, vault=None)

    result = _run(agent.execute({"action": "arbitrary_tool", "message": "hello"}))

    assert result["error"] == "unknown_action"
    assert result["status"] == "error"
    assert llm.prompts == []


def test_nightly_analysis_archives_only_bounded_authorized_text_and_never_overwrites(tmp_path) -> None:
    vault = MarkdownVault(vault_root=tmp_path / "vault")
    summary = (
        "## Факти\n- У повідомленнях згадано Obsidian.\n"
        "## Підтверджені рішення\n- Архів проєкту — Obsidian.\n"
        "## Задачі/статуси\n- Погоджених задач не надано.\n"
        "## Ідеї\n- Нових ідей не надано.\n"
        "## Ризики\n- Даних для оцінки ризиків немає.\n"
        "## Відкриті питання\n- Відкритих питань у джерелі не зазначено."
    )
    llm = _LLM(summary)
    agent = EvaAgent(memory=None, llm=llm, vault=vault)
    trusted_text_items = [
        {"kind": "text_conversation", "text": "Ми підтвердили Obsidian як архів."},
        {"kind": "eva_work_note", "text": "Інших задач Єва не створювала."},
    ]

    # Exercise only the internal helper; no public action accepts request-body authorization flags.
    first = _run(agent._nightly_analysis(trusted_text_items))
    archive_path = first["archive"]["path"]
    archived_content = vault.read(archive_path)
    second = _run(agent._nightly_analysis(trusted_text_items))

    assert first["status"] == "archived"
    assert first["confirmation"] == "generated_unconfirmed"
    assert "confirmed=no" in archived_content
    assert "## Відкриті питання" in archived_content
    assert second["status"] == "already_archived"
    assert vault.read(archive_path) == archived_content
    assert not vault.exists("agents/eva/memory.md")
    assert first["agent_tasks_dispatched"] is False
    assert first["external_actions"] is False


def test_nightly_analysis_is_not_a_public_action_and_rejects_audio_sources(tmp_path) -> None:
    vault = MarkdownVault(vault_root=tmp_path / "vault")
    llm = _LLM("Should not be invoked.")
    agent = EvaAgent(memory=None, llm=llm, vault=vault)

    public_action = _run(agent.execute({
        "action": "nightly_analysis",
        "authorized_text_items": [{"kind": "text_conversation", "text": "Probe"}],
    }))
    audio = _run(agent._nightly_analysis([{"kind": "audio_transcript", "text": "Transcript"}]))
    secret = _run(agent._nightly_analysis([
        {"kind": "text_conversation", "text": "password=hunter2-with-enough-length"}
    ]))

    assert public_action["status"] == "error"
    assert public_action["error"] == "unknown_action"
    assert audio["status"] == "refused"
    assert secret["status"] == "refused"
    assert llm.prompts == []
    assert not vault.list_files("archive/nightly")


def test_nightly_schedule_is_daily_at_three_in_europe_kyiv() -> None:
    scheduler = ProactiveScheduler()
    assert [job.name for job in scheduler.jobs] == ["nightly_analysis"]
    assert scheduler.jobs[0].cron == "0 3 * * *"
    assert scheduler.jobs[0].timezone == "Europe/Kyiv"
    assert [job.name for job in scheduler.due(datetime(2026, 10, 4, 3, 0))] == ["nightly_analysis"]
    assert [job.name for job in scheduler.due(datetime(2026, 10, 4, 0, 0, tzinfo=timezone.utc))] == [
        "nightly_analysis"
    ]


def test_scheduled_nightly_entry_stays_unavailable_without_a_source_provider() -> None:
    from src.orchestrator import EvaOrchestrator

    result = _run(EvaOrchestrator.proactive_nightly_analysis(object.__new__(EvaOrchestrator)))

    assert result["status"] == "unavailable"
    assert result["reason"] == "nightly_source_provider_not_configured"
    assert result["agent_tasks_dispatched"] is False
    assert result["external_actions"] is False
