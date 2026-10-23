"""
Unit tests for SYNDICATE Voice Stack v2 (LiveKit + Silero VAD v5 + Kokoro-82M + F5-TTS + PronunciationCoach),
Kira Live Psychotherapy & English Pronunciation Coach, and NotebookLM 2.0 Mastery + 3-Tier Hybrid Memory.
"""

from __future__ import annotations

import asyncio
import struct
from pathlib import Path

from src.agents.kira import KiraAgent
from src.integrations.notebooklm_obsidian_bridge import (
    CORPORATE_DOMAIN,
    DEFAULT_STUDIO_LANGUAGE,
    MASTER_NOTEBOOK_ID,
    NOTEBOOKLM_12_BUSINESS_USE_CASES,
    NotebookLMObsidianBridge,
)
from src.voice import (
    SYNDICATE_VOICE_PROFILES,
    KokoroTTSProvider,
    LiveKitRealtimeBridge,
    PronunciationCoach,
    SileroVADProcessor,
    ZeroShotVoiceCloner,
    build_voice_manager,
    get_agent_voice_profile,
)

ROOT = Path(__file__).resolve().parents[1]


def _run(coro):
    return asyncio.run(coro)


def test_all_18_agents_and_digital_twin_have_kokoro_voice_blends() -> None:
    expected_agents = {
        "eva", "kira", "architect", "marshal", "fin", "doc", "sam", "kodex", "alice",
        "oscar", "tyler", "jack", "ray", "dex", "atlas", "trainer", "scout", "sonar",
        "andrii_twin",
    }
    assert expected_agents.issubset(set(SYNDICATE_VOICE_PROFILES.keys()))
    kira_prof = get_agent_voice_profile("kira")
    assert "af_heart" in kira_prof.blend_formula
    assert kira_prof.speed < 1.0  # Empathetic mentor cadence


def test_kokoro_tts_and_zero_shot_voice_cloner_offline_synthesis() -> None:
    vm = build_voice_manager(
        config={
            "tts_priority": ["kokoro_local", "f5_voice_clone"],
            "kokoro_local": {"offline_simulation": True},
            "f5_voice_clone": {"offline_simulation": True},
        }
    )
    res = _run(vm.speak("Вітаю, Андрію! Голосовий стек Кокоро працює без витрати токенів.", agent_id="kira", therapy_mode=True))
    assert res.ok
    assert res.provider == "kokoro_local"
    assert res.meta["token_cost_usd"] == 0.0
    assert res.meta["therapy_mode"] is True

    cloner = ZeroShotVoiceCloner(config={"offline_simulation": True})
    clone_res = _run(cloner.synthesize("Це клонований голос для ранкового подкасту.", voice_id="andrii_twin"))
    assert clone_res.ok
    assert clone_res.provider == "f5_voice_clone"
    assert clone_res.meta["token_cost_usd"] == 0.0


def test_silero_vad_filters_silence_and_triggers_barge_in() -> None:
    vad = SileroVADProcessor(threshold=0.45)
    # 1. Pure silence frame
    silence_pcm = b"\x00\x00" * 320
    d_silence = vad.analyze_pcm16_frame(silence_pcm)
    assert d_silence.is_speech is False
    assert d_silence.barge_in_triggered is False

    # 2. Agent is currently speaking, and Andrii starts speaking (loud PCM frame -> Barge-in!)
    vad.set_agent_speaking(True)
    loud_pcm = b"".join(struct.pack("<h", 12000) for _ in range(320))
    d_speech = vad.analyze_pcm16_frame(loud_pcm)
    assert d_speech.is_speech is True
    assert d_speech.barge_in_triggered is True
    assert vad.stats["silence_frames_dropped"] == 1


def test_kira_live_psychotherapy_and_english_pronunciation_coach() -> None:
    kira = KiraAgent(memory=None, llm=None)

    # 1. Live Psychotherapy session via LiveKit + Silero VAD + Kokoro-82M
    therapy_res = _run(
        kira.execute({
            "action": "live_therapy_session",
            "session_id": "therapy-001",
            "mode": "psychotherapy",
        })
    )
    assert therapy_res["status"] == "ok"
    assert therapy_res["voice_token_cost_usd"] == 0.0
    assert "Kokoro-82M" in therapy_res["live_room"]["stack"]["tts"]
    assert "Silero VAD v5" in therapy_res["live_room"]["stack"]["vad"]

    # 2. English Pronunciation Assessment (detecting /θ/ -> /s/ and /w/ -> /v/)
    pron_res = _run(
        kira.execute({
            "action": "english_pronunciation_assessment",
            "target_phrase": "We think this ship is fast",
            "simulated_substitutions": {"think": "/sɪŋk/", "we": "/viː/"},
        })
    )
    assert pron_res["status"] == "ok"
    assessment = pron_res["assessment"]
    assert assessment["overall_score_pct"] < 90.0
    assert "think" in assessment["drill_words"]
    assert "we" in assessment["drill_words"]
    assert "між зубами" in assessment["kira_feedback_uk"]


def test_notebooklm_v2_ukrainian_policy_alchemy_and_hybrid_memory(tmp_path: Path) -> None:
    bridge = NotebookLMObsidianBridge(vault_path=tmp_path / "vault")
    assert bridge.master_notebook_id == MASTER_NOTEBOOK_ID
    assert DEFAULT_STUDIO_LANGUAGE == "uk"
    assert CORPORATE_DOMAIN == "syndicateholding.com"
    assert len(NOTEBOOKLM_12_BUSINESS_USE_CASES) == 12

    # 1. Mandatory Ukrainian Studio artifact request even if 'en' was accidentally passed without override
    req = bridge.build_studio_artifact_request(
        artifact_type="audio",
        instructions="Зроби глибокий розбір архітектури",
        language="en",
        allow_non_ukrainian=False,
    )
    assert req["language"] == "uk"
    assert "--language uk" in req["cli_command"]
    assert MASTER_NOTEBOOK_ID in req["cli_command"]

    # 2. Information Alchemy (Compress & Convert to Source)
    alchemy = bridge.compress_and_convert_sources(
        cluster_title="RAG_Optimization_2026",
        raw_sources=[
            {"title": f"Paper_{i}", "content": f"Detailed finding #{i} on Late Chunking and HNSW."}
            for i in range(1, 7)
        ],
    )
    assert alchemy["status"] == "compressed_and_converted"
    assert alchemy["original_sources_count"] == 6
    assert alchemy["new_sources_count"] == 1
    assert alchemy["slots_saved"] == 5
    assert Path(alchemy["obsidian_path"]).exists()

    # 3. Master Instructions Doc & Late Chunking
    master_doc = bridge.build_master_instructions_doc()
    assert "syndicateholding.com" in master_doc
    chunks = bridge.late_chunk_document(
        title="Contabo_VPS_Spec",
        full_text="A" * 2500,
        global_context_summary="Cloud VPS 12 48GB RAM 400GB SSD",
        chunk_size_chars=1000,
    )
    assert len(chunks) == 3
    assert all("Cloud VPS 12 48GB RAM" in c["contextualized_chunk"] for c in chunks)

    # 4. 3-Tier Hybrid Memory Router
    r_fast = bridge.route_hybrid_memory_query("Який порт LiveKit?", latency_budget_ms=15)
    assert r_fast["selected_tier"] == "tier_2_pgvector_fast_rag"
    r_deep = bridge.route_hybrid_memory_query("Синтезуй 129 джерел у посібник", require_deep_synthesis=True)
    assert r_deep["selected_tier"] == "tier_3_notebooklm_deep_synthesis"


def test_second_brain_knowledge_web_synced_in_repo() -> None:
    sb_dir = ROOT / "knowledge_pools" / "notebooklm_second_brain"
    assert sb_dir.exists()
    md_files = list(sb_dir.rglob("*.md"))
    assert len(md_files) >= 35
    assert (sb_dir / "Екосистема_NotebookLM.canvas").exists()
