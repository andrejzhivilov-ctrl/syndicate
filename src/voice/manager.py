"""
VoiceManager — provider-agnostic voice with priority + fallback chains.

TTS priority example: ["elevenlabs", "xai_grok", "openai"]
STT priority example: ["whisper_local", "groq_whisper"]

Providers are tried in order; on failure the next provider is used. The first
successful result is returned. If all fail, a VoiceResult with an aggregated
error is returned.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from src.voice.base import BaseSTTProvider, BaseTTSProvider, VoiceResult
from src.voice.elevenlabs import ElevenLabsTTS
from src.voice.openai_tts import OpenAITTS
from src.voice.whisper_stt import GroqWhisperSTT, WhisperSTT
from src.voice.xai_grok import XAIGrokVoice

logger = structlog.get_logger(__name__)

_TTS_REGISTRY = {
    ElevenLabsTTS.PROVIDER_NAME: ElevenLabsTTS,
    XAIGrokVoice.PROVIDER_NAME: XAIGrokVoice,
    OpenAITTS.PROVIDER_NAME: OpenAITTS,
}
_STT_REGISTRY = {
    WhisperSTT.PROVIDER_NAME: WhisperSTT,
    GroqWhisperSTT.PROVIDER_NAME: GroqWhisperSTT,
}


class VoiceManager:
    def __init__(
        self,
        tts_providers: List[BaseTTSProvider],
        stt_providers: List[BaseSTTProvider],
    ) -> None:
        self._tts = tts_providers
        self._stt = stt_providers

    async def speak(self, text: str, voice_id: Optional[str] = None, **opts: Any) -> VoiceResult:
        errors: List[str] = []
        for provider in self._tts:
            result = await provider.synthesize(text, voice_id=voice_id, **opts)
            if result.ok and result.audio_bytes:
                logger.info("tts_success", provider=provider.PROVIDER_NAME, chars=len(text))
                return result
            errors.append(f"{provider.PROVIDER_NAME}: {result.error}")
            logger.warning("tts_provider_fallthrough", provider=provider.PROVIDER_NAME, error=result.error)
        return VoiceResult(provider="none", error="all TTS providers failed: " + "; ".join(errors))

    async def listen(self, audio_bytes: bytes, language: str = "uk", **opts: Any) -> VoiceResult:
        errors: List[str] = []
        for provider in self._stt:
            result = await provider.transcribe(audio_bytes, language=language, **opts)
            if result.ok and result.text:
                logger.info("stt_success", provider=provider.PROVIDER_NAME)
                return result
            errors.append(f"{provider.PROVIDER_NAME}: {result.error}")
            logger.warning("stt_provider_fallthrough", provider=provider.PROVIDER_NAME, error=result.error)
        return VoiceResult(provider="none", error="all STT providers failed: " + "; ".join(errors))

    async def health(self) -> Dict[str, Any]:
        tts = {p.PROVIDER_NAME: await p.health_check() for p in self._tts}
        stt = {p.PROVIDER_NAME: await p.health_check() for p in self._stt}
        return {"tts": tts, "stt": stt}


def build_voice_manager(vault_client: Any = None, config: Optional[Dict[str, Any]] = None) -> VoiceManager:
    """Build a VoiceManager from config.

    config keys:
      tts_priority: list[str] | comma-string  (default elevenlabs,xai_grok,openai)
      stt_priority: list[str] | comma-string  (default whisper_local,groq_whisper)
      <provider_name>: dict  — per-provider config (e.g. elevenlabs voice_id, whisper_url)
    """
    config = config or {}

    def _as_list(val: Any, default: List[str]) -> List[str]:
        if isinstance(val, list):
            return val
        if isinstance(val, str) and val.strip():
            return [x.strip() for x in val.split(",") if x.strip()]
        return default

    tts_order = _as_list(config.get("tts_priority"), ["elevenlabs", "xai_grok", "openai"])
    stt_order = _as_list(config.get("stt_priority"), ["whisper_local", "groq_whisper"])

    tts_providers: List[BaseTTSProvider] = []
    for name in tts_order:
        cls = _TTS_REGISTRY.get(name)
        if cls:
            tts_providers.append(cls(vault_client, config.get(name, {})))
        else:
            logger.warning("unknown_tts_provider", name=name)

    stt_providers: List[BaseSTTProvider] = []
    for name in stt_order:
        cls = _STT_REGISTRY.get(name)
        if cls:
            stt_providers.append(cls(vault_client, config.get(name, {})))
        else:
            logger.warning("unknown_stt_provider", name=name)

    return VoiceManager(tts_providers, stt_providers)
