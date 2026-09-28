"""Voice subsystem for the EVA Syndicate.

Provides a provider-agnostic Text-to-Speech / Speech-to-Text layer with a
priority-based fallback chain so every agent can gain a voice regardless of
which external provider is configured (ElevenLabs, xAI/Grok, OpenAI, Whisper,
Groq-Whisper).

All API keys are resolved through Vault (``secret/data/eva-syndicate/<service>``)
with an environment-variable fallback that is intended for local development
only.  Third-party HTTP is performed through ``httpx`` and every module is
import-safe (optional dependencies are wrapped in ``try/except``).
"""
from __future__ import annotations

from .base import BaseSTTProvider, BaseTTSProvider, VoiceResult
from .elevenlabs import ElevenLabsTTS
from .manager import VoiceManager, build_voice_manager
from .openai_tts import OpenAITTS
from .whisper_stt import GroqWhisperSTT, WhisperSTT
from .xai_grok import XAIGrokVoice

__all__ = [
    "VoiceResult",
    "BaseTTSProvider",
    "BaseSTTProvider",
    "VoiceManager",
    "build_voice_manager",
    "ElevenLabsTTS",
    "XAIGrokVoice",
    "OpenAITTS",
    "WhisperSTT",
    "GroqWhisperSTT",
]
