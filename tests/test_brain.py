"""Every move in the Second Brain, search by meaning, Eva's monthly audit (Andrii, 20.11.2026)."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from datetime import datetime, timezone

import numpy as np

from src import agent_schedule, brain, brain_audit, brain_index

NOW = datetime(2026, 11, 20, 10, 30, tzinfo=timezone.utc)


def _env(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", str(vault))
    return vault


def test_a_move_lands_in_the_agents_journal_and_in_full_without_secrets_or_coordinates(tmp_path, monkeypatch):
    vault = _env(tmp_path, monkeypatch)
    token = "sk-proj-" + "a" * 30
    assert brain.record("sam", "strategy", "нова ідея ema_20_55", f"ключ {token}, позиція 50.4501, 30.5234 [[Каталог]]",
                        ["Сем/Стратегії/ema_20_55_rsi_4h.md"], now=NOW)
    journal = (vault / "Сем" / "Журнал" / "Дії" / "2026-11-20.md").read_text(encoding="utf-8")
    assert "12:30 **strategy** нова ідея ema_20_55" in journal  # Kyiv time
    assert "[[Сем/Стратегії/ema_20_55_rsi_4h]]" in journal and "[[Каталог]]" in journal
    full = (tmp_path / "data" / "brain" / "sam" / "2026-11-20.jsonl").read_text(encoding="utf-8")
    for text in (journal, full):
        assert token not in text and "50.4501" not in text and "[прибрано]" in text


def test_the_doors_never_raise_and_an_idle_engine_tick_says_nothing(tmp_path, monkeypatch):
    vault = _env(tmp_path, monkeypatch)
    brain.job("sam", "sam_scalp", {"status": "ok", "opened": 0})
    brain.tool("sam", "paper_trade", {"action": "status"}, object())  # an odd result is written as text
    brain.chat("trainer", "як спав?", None)
    days = list((vault / "Сем" / "Журнал" / "Дії").glob("*.md"))
    text = days[0].read_text(encoding="utf-8")
    assert "sam_scalp" not in text and "paper_trade" in text
    assert list((vault / "Health_Coach" / "Журнал" / "Дії").glob("*.md"))
    monkeypatch.setattr(brain, "_record", lambda *a: 1 / 0)
    assert brain.record("sam", "task", "x") is False  # a broken disk never takes an agent down
    assert agent_schedule.JOBS["brain_index"].cron == "*/15 * * * *"
    assert agent_schedule.JOBS["eva_brain_audit"].cron == "0 7 1 * *"


class _Embedder:
    """Deterministic bag-of-words vectors: shared words make vectors close, like meaning does."""

    def __init__(self):
        self.calls = 0

    async def embed(self, texts):
        self.calls += len(texts)
        out = []
        for text in texts:
            v = np.zeros(1024)
            for word in brain_index._words(text):
                v[int(hashlib.md5(word.encode()).hexdigest(), 16) % 1024] += 1
            out.append(list(v + 1e-3))
        return out


def test_the_index_reads_only_what_changed_and_search_finds_by_meaning(tmp_path, monkeypatch):
    vault = _env(tmp_path, monkeypatch)
    (vault / "Сем").mkdir()
    (vault / "Сем" / "Рівні.md").write_text("# Рівні\n\nвчорашній максимум пробій рівня підтримки", encoding="utf-8")
    (vault / "Health_Coach.md").write_text("# Сон\n\nсон вісім годин відновлення м'язів", encoding="utf-8")
    (vault / ".obsidian").mkdir()
    (vault / ".obsidian" / "x.md").write_text("службове", encoding="utf-8")
    emb = _Embedder()
    first = asyncio.run(brain_index.update(vault, emb))
    assert first["notes"] == 2 and first["indexed"] == 2
    calls = emb.calls
    assert asyncio.run(brain_index.update(vault, emb))["indexed"] == 0 and emb.calls == calls  # nothing re-read
    found = asyncio.run(brain_index.search("пробій максимуму рівня", emb, "Сем"))
    assert found["mode"] == "meaning" and found["hits"][0]["path"] == "Сем/Рівні.md"
    (vault / "Health_Coach.md").unlink()
    gone = asyncio.run(brain_index.update(vault, emb))
    assert gone["removed"] == 1 and all(r["path"] != "Health_Coach.md" for r in brain_index.Index().rows)


def test_without_the_embeddings_service_the_search_says_so_and_uses_words(tmp_path, monkeypatch):
    vault = _env(tmp_path, monkeypatch)
    (vault / "Сем").mkdir()
    (vault / "Сем" / "Рівні.md").write_text("# Рівні\n\nвчорашній максимум", encoding="utf-8")
    monkeypatch.delenv("EMBEDDINGS_URL", raising=False)
    found = asyncio.run(brain_index.search_or_words("максимум", "sam"))
    assert found["mode"] == "words" and found["warning"] and "Рівні" in found["text"]
    assert asyncio.run(brain_index.run_job())["reason"] == "embeddings_disabled"


def test_evas_audit_moves_only_safe_rubbish_to_the_bin_and_asks_for_the_rest(tmp_path, monkeypatch):
    vault = _env(tmp_path, monkeypatch)
    old = time.time() - 30 * 86400
    notes = {"Порожня.md": "", "А/Копія1.md": "однаковий текст нотатки про рівні", "А/Копія2.md": "однаковий текст нотатки про рівні",
             "Мітка.md": "---\nandrii_protected: true\n---\n", "Свіжа.md": " "}
    for rel, text in notes.items():
        path = vault / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        if rel != "Свіжа.md":
            os.utime(path, (old, old))
    result = brain_audit.run(vault)
    bin_ = vault / "_Кошик_агентів"
    assert (bin_ / "Порожня.md").is_file() and not (vault / "Порожня.md").exists()
    assert len(list((vault / "А").glob("*.md"))) == 1 and len(list((bin_ / "А").glob("*.md"))) == 1
    assert (vault / "Мітка.md").is_file() and (vault / "Свіжа.md").is_file()  # protected and fresh wait for Andrii
    assert result["moved"] == 2 and result["asked"] >= 1
    report = (vault / result["report"]).read_text(encoding="utf-8")
    assert "Нічого не видалено" in report and "Свіжа" in report
    rows = [json.loads(line) for line in (tmp_path / "data" / "brain" / "eva").glob("*.jsonl").__next__().read_text(
        encoding="utf-8").splitlines()]
    assert rows[-1]["kind"] == "job" and "аудит" in rows[-1]["summary"]
