"""
Kokoro-82M Local TTS & Zero-Shot Voice Cloning (F5-TTS / XTTS-v2) for SYNDICATE.

Provides:
1. KokoroTTSProvider ("kokoro_local"):
   - $0.00 token-free neural speech synthesis on CPU (ONNX / FastAPI microservice).
   - Mathematical Voice Blending: mixes multiple voice style vectors (e.g. "0.7*af_bella + 0.3*af_sarah")
     to give all 18 SYNDICATE agents a unique, unmistakable vocal timbre.
2. ZeroShotVoiceCloner ("f5_voice_clone"):
   - Local zero-shot voice cloning from a 15-30s WAV reference sample (/data/voices/clones/<id>.wav).
   - Supports cloning custom voices (including Andrii's Digital Twin or studio reference samples)
     without paying recurring ElevenLabs per-character fees.
"""

from __future__ import annotations

import io
import os
import struct
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
import structlog

from src.voice.base import BaseTTSProvider, VoiceResult

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class AgentVoiceProfile:
    """Acoustic persona & Kokoro-82M mathematical voice blend for a SYNDICATE agent."""

    agent_id: str
    display_name: str
    blend_formula: str
    speed: float
    pitch_shift: float
    persona_style: str
    clone_sample_path: Optional[str] = None


# 18 SYNDICATE Agents + Andrii's Digital Twin Voice Profiles
SYNDICATE_VOICE_PROFILES: Dict[str, AgentVoiceProfile] = {
    "eva": AgentVoiceProfile(
        agent_id="eva",
        display_name="Єва (Chief of Staff)",
        blend_formula="0.65*af_bella + 0.35*bf_emma",
        speed=1.02,
        pitch_shift=0.0,
        persona_style="Warm, aristocratic, composed executive assistant",
        clone_sample_path="/data/voices/clones/eva_reference.wav",
    ),
    "kira": AgentVoiceProfile(
        agent_id="kira",
        display_name="Кіра (Mentor, Psychotherapist & English Coach)",
        blend_formula="0.70*af_heart + 0.30*af_nicole",
        speed=0.94,
        pitch_shift=-0.2,
        persona_style="Empathetic, calm psychotherapist & articulate Oxford/Silicon Valley tutor",
        clone_sample_path="/data/voices/clones/kira_reference.wav",
    ),
    "architect": AgentVoiceProfile(
        agent_id="architect",
        display_name="Архітектор (Chief Systems Architect)",
        blend_formula="0.60*am_adam + 0.40*bm_george",
        speed=1.00,
        pitch_shift=-0.5,
        persona_style="Deep, analytical, structured engineering precision",
    ),
    "marshal": AgentVoiceProfile(
        agent_id="marshal",
        display_name="Маршал (Chief Security Officer)",
        blend_formula="0.80*bm_lewis + 0.20*am_michael",
        speed=0.98,
        pitch_shift=-1.0,
        persona_style="Firm, vigilant, zero-trust guardian",
    ),
    "fin": AgentVoiceProfile(
        agent_id="fin",
        display_name="Фін (CFO & Treasury)",
        blend_formula="0.50*bm_george + 0.50*am_michael",
        speed=1.03,
        pitch_shift=-0.3,
        persona_style="Crisp, rational institutional banker",
    ),
    "doc": AgentVoiceProfile(
        agent_id="doc",
        display_name="Док (Chief Medical & Longevity Officer)",
        blend_formula="0.75*bm_george + 0.25*am_adam",
        speed=0.96,
        pitch_shift=-0.2,
        persona_style="Reassuring, evidence-based clinical specialist",
    ),
    "sam": AgentVoiceProfile(
        agent_id="sam",
        display_name="Сем (Algorithmic Quant Trader)",
        blend_formula="0.70*am_michael + 0.30*am_fenrir",
        speed=1.08,
        pitch_shift=0.0,
        persona_style="Fast, sharp Wall Street quant desk lead",
    ),
    "kodex": AgentVoiceProfile(
        agent_id="kodex",
        display_name="Кодекс (Chief Knowledge Officer)",
        blend_formula="0.85*bm_george + 0.15*bm_lewis",
        speed=0.97,
        pitch_shift=-0.4,
        persona_style="Scholarly, encyclopedic keeper of the Second Brain",
    ),
    "alice": AgentVoiceProfile(
        agent_id="alice",
        display_name="Аліса / Antigravity (Lead AI Engineer)",
        blend_formula="0.60*af_sarah + 0.40*af_sky",
        speed=1.05,
        pitch_shift=0.2,
        persona_style="Energetic, hyper-capable deep-tech pair programmer",
    ),
    "oscar": AgentVoiceProfile(
        agent_id="oscar",
        display_name="Оскар (Creative & Media Director)",
        blend_formula="0.60*am_puck + 0.40*am_adam",
        speed=1.04,
        pitch_shift=0.1,
        persona_style="Charismatic storyteller and cinematic producer",
    ),
    "tyler": AgentVoiceProfile(
        agent_id="tyler",
        display_name="Тайлер (E-Commerce & Merch Director)",
        blend_formula="0.65*am_fenrir + 0.35*am_puck",
        speed=1.05,
        pitch_shift=0.0,
        persona_style="Pragmatic product strategist",
    ),
    "jack": AgentVoiceProfile(
        agent_id="jack",
        display_name="Джек (Mobile & GameDev Director)",
        blend_formula="0.70*am_puck + 0.30*am_michael",
        speed=1.06,
        pitch_shift=0.2,
        persona_style="Dynamic interactive systems builder",
    ),
    "ray": AgentVoiceProfile(
        agent_id="ray",
        display_name="Рей (Dropshipping & Supply Chain Director)",
        blend_formula="0.55*am_michael + 0.45*bm_lewis",
        speed=1.03,
        pitch_shift=-0.2,
        persona_style="Global logistics & unit-economics operator",
    ),
    "dex": AgentVoiceProfile(
        agent_id="dex",
        display_name="Декс (Affiliate & Traffic Arbitrage Director)",
        blend_formula="0.60*am_fenrir + 0.40*am_michael",
        speed=1.07,
        pitch_shift=0.1,
        persona_style="Data-driven growth & conversion hacker",
    ),
    "atlas": AgentVoiceProfile(
        agent_id="atlas",
        display_name="Атлас (Infrastructure & DevOps Director)",
        blend_formula="0.75*bm_lewis + 0.25*bm_george",
        speed=0.99,
        pitch_shift=-0.8,
        persona_style="Steady, unshakeable server reliability engineer",
    ),
    "trainer": AgentVoiceProfile(
        agent_id="trainer",
        display_name="Тренер (High-Performance Athletic Coach)",
        blend_formula="0.80*am_fenrir + 0.20*am_adam",
        speed=1.04,
        pitch_shift=-0.5,
        persona_style="Motivating, disciplined physical performance coach",
    ),
    "scout": AgentVoiceProfile(
        agent_id="scout",
        display_name="Скаут (Market & Trend Intelligence Director)",
        blend_formula="0.65*af_sky + 0.35*af_bella",
        speed=1.06,
        pitch_shift=0.3,
        persona_style="Alert, observant trend hunter",
    ),
    "sonar": AgentVoiceProfile(
        agent_id="sonar",
        display_name="Сонар (Deep Research & Fact-Checking Director)",
        blend_formula="0.70*bf_emma + 0.30*af_nicole",
        speed=1.00,
        pitch_shift=-0.1,
        persona_style="Objective, citation-grounded intelligence analyst",
    ),
    "andrii_twin": AgentVoiceProfile(
        agent_id="andrii_twin",
        display_name="Андрій (Digital Twin Voice)",
        blend_formula="1.00*custom_andrii_clone",
        speed=1.00,
        pitch_shift=0.0,
        persona_style="Founder's authentic cloned voice for bilingual podcasts & keynote briefings",
        clone_sample_path="/data/voices/clones/andrii_master.wav",
    ),
}


def get_agent_voice_profile(agent_id: str) -> AgentVoiceProfile:
    """Return the configured voice profile for an agent (falls back to Eva)."""
    return SYNDICATE_VOICE_PROFILES.get(agent_id.lower(), SYNDICATE_VOICE_PROFILES["eva"])


def _generate_deterministic_wav(text: str, sample_rate: int = 24000) -> bytes:
    """Generate a valid minimal PCM WAV byte stream for offline/test verification."""
    buf = io.BytesIO()
    num_samples = max(240, min(sample_rate, len(text) * 40))
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = b"".join(struct.pack("<h", (i * 17) % 500) for i in range(num_samples))
        wf.writeframes(frames)
    return buf.getvalue()


class KokoroTTSProvider(BaseTTSProvider):
    """
    Local Kokoro-82M ONNX/FastAPI TTS Provider ($0.00 token cost).
    Supports Mathematical Voice Blending across all 18 SYNDICATE directors.
    """

    PROVIDER_NAME = "kokoro_local"
    DEFAULT_URL = "http://kokoro-tts:8880/v1/audio/speech"

    def _endpoint(self) -> str:
        return (
            self._config.get("url")
            or os.environ.get("KOKORO_TTS_URL")
            or self.DEFAULT_URL
        )

    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        therapy_mode: bool = False,
        **opts: Any,
    ) -> VoiceResult:
        if not text or not text.strip():
            return VoiceResult(provider=self.PROVIDER_NAME, error="empty text")

        profile = get_agent_voice_profile(agent_id or voice_id or "eva")
        blend = voice_id if (voice_id and "*" in voice_id) else profile.blend_formula
        speed = float(opts.get("speed", 0.90 if therapy_mode else profile.speed))

        payload = {
            "model": self._config.get("model", "kokoro-82m-v1.0-int8"),
            "input": text,
            "voice": blend,
            "speed": speed,
            "response_format": "wav",
            "language": opts.get("language", "uk"),
        }

        # Allow deterministic offline mode when configured for local tests
        if self._config.get("offline_simulation", False):
            wav_bytes = _generate_deterministic_wav(text)
            return VoiceResult(
                provider=self.PROVIDER_NAME,
                audio_bytes=wav_bytes,
                mime_type="audio/wav",
                meta={
                    "agent_id": profile.agent_id,
                    "voice_blend": blend,
                    "speed": speed,
                    "therapy_mode": therapy_mode,
                    "token_cost_usd": 0.0,
                },
            )

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(self._endpoint(), json=payload)
            if resp.status_code != 200:
                return VoiceResult(
                    provider=self.PROVIDER_NAME,
                    error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                )
            return VoiceResult(
                provider=self.PROVIDER_NAME,
                audio_bytes=resp.content,
                mime_type="audio/wav",
                meta={
                    "agent_id": profile.agent_id,
                    "voice_blend": blend,
                    "speed": speed,
                    "therapy_mode": therapy_mode,
                    "token_cost_usd": 0.0,
                },
            )
        except Exception as exc:
            logger.warning("kokoro_tts_error", error=str(exc))
            return VoiceResult(provider=self.PROVIDER_NAME, error=str(exc))

    async def health_check(self) -> Dict[str, Any]:
        return {
            "provider": self.PROVIDER_NAME,
            "configured": True,
            "endpoint": self._endpoint(),
            "profiles_loaded": len(SYNDICATE_VOICE_PROFILES),
            "token_cost_usd": 0.0,
        }


class ZeroShotVoiceCloner(BaseTTSProvider):
    """
    Zero-Shot Voice Cloning via local F5-TTS / XTTS-v2 microservice.
    Clones any voice from a 15-30 second clean WAV reference file on the server
    (/data/voices/clones/<agent_id>.wav) at $0.00 API cost.
    """

    PROVIDER_NAME = "f5_voice_clone"
    DEFAULT_URL = "http://voice-cloner:8881/v1/audio/clone"

    def _endpoint(self) -> str:
        return (
            self._config.get("url")
            or os.environ.get("VOICE_CLONER_URL")
            or self.DEFAULT_URL
        )

    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        reference_wav: Optional[str | Path] = None,
        **opts: Any,
    ) -> VoiceResult:
        if not text or not text.strip():
            return VoiceResult(provider=self.PROVIDER_NAME, error="empty text")

        profile = get_agent_voice_profile(voice_id or "andrii_twin")
        ref_path = str(reference_wav or profile.clone_sample_path or "/data/voices/clones/default.wav")

        if self._config.get("offline_simulation", False):
            wav_bytes = _generate_deterministic_wav(text)
            return VoiceResult(
                provider=self.PROVIDER_NAME,
                audio_bytes=wav_bytes,
                mime_type="audio/wav",
                meta={
                    "agent_id": profile.agent_id,
                    "reference_wav": ref_path,
                    "engine": self._config.get("engine", "f5-tts"),
                    "token_cost_usd": 0.0,
                },
            )

        payload = {
            "text": text,
            "reference_audio_path": ref_path,
            "language": opts.get("language", "uk"),
            "engine": self._config.get("engine", "f5-tts"),
            "speed": float(opts.get("speed", profile.speed)),
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post(self._endpoint(), json=payload)
            if resp.status_code != 200:
                return VoiceResult(
                    provider=self.PROVIDER_NAME,
                    error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                )
            return VoiceResult(
                provider=self.PROVIDER_NAME,
                audio_bytes=resp.content,
                mime_type="audio/wav",
                meta={
                    "agent_id": profile.agent_id,
                    "reference_wav": ref_path,
                    "engine": payload["engine"],
                    "token_cost_usd": 0.0,
                },
            )
        except Exception as exc:
            logger.warning("voice_cloner_error", error=str(exc))
            return VoiceResult(provider=self.PROVIDER_NAME, error=str(exc))
