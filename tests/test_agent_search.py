"""Agents search Obsidian by words without a magic word, see big cards and get summaries (19.11.2026)."""

from __future__ import annotations

import asyncio

from src import hermes_gateway
from src.obsidian_notes import search_notes


def _card(path, summary, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\nsummary: "{summary}"\n---\n\n# {path.stem}\n\n{body}', encoding="utf-8")


def test_a_plain_query_finds_cards_own_folder_first_with_summaries(tmp_path):
    _card(tmp_path / "Health_Coach/Матеріали/Добавки/креатин.pdf.md", "Креатин 3-5 г на день", "креатин " * 3)
    _card(tmp_path / "09_База_Знань/Матеріали/креатин огляд.md", "Огляд ринку креатину", "креатин " * 3)
    big = "креатин моногідрат " + "x" * 400_000  # a whole book: bigger than the old 200 KB limit
    _card(tmp_path / "Health_Coach/Матеріали/Добавки/книга.pdf.md", "Книга про добавки", big)
    found = search_notes("креатин дозування", tmp_path, "Health_Coach")
    lines = found.splitlines()
    assert lines[1].startswith("- Health_Coach/") and "Креатин 3-5 г на день" in found
    assert "книга.pdf.md — Книга про добавки" in found  # the big card is seen by its head
    assert "09_База_Знань/Матеріали/креатин огляд.md" in found
    assert "нічого не знайдено" in search_notes("квантова фізика", tmp_path, "Health_Coach")


def test_obsidian_search_tool_no_longer_needs_the_word_notes(tmp_path, monkeypatch):
    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", str(tmp_path))
    _card(tmp_path / "Health_Coach/Програми/сила.md", "Програма на силу 5x5", "присід жим тяга")
    reply = asyncio.run(hermes_gateway._run_tool("trainer", "obsidian_search", {"query": "присід"}, None))
    assert "Health_Coach/Програми/сила.md" in reply


def test_a_long_card_is_read_by_its_head_and_the_rest_through_material_read(tmp_path, monkeypatch):
    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", str(tmp_path))
    _card(tmp_path / "Health_Coach/Матеріали/книга.pdf.md", "Книга", "y" * 30_000)
    text = hermes_gateway._read_note("Health_Coach/Матеріали/книга.pdf.md")
    assert len(text) < hermes_gateway.NOTE_READ_CHARS + 300 and "material_read" in text
