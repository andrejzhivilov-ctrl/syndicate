"""
xAI Grok voice (TTS) provider.

NOTE: xAI's audio/TTS route is evolving. The endpoint is fully configurable via
config ``tts_endpoint`` (or Vault key ``tts_endpoint`` / env XAI_TTS_ENDPOINT),
defaulting to https://api.x.ai/v1/audio/speech. Given a correct endpoint + key,
this provider is fully functional. Request shape mirrors the OpenAI-compatible
audio API that xAI exposes.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import structlog

from src.voice._util import read_vault_secret
from src.voice.base import BaseTTSProvider, VoiceResult

logger = structlog.get_logger(__name__)

try:
    import httpx
    _HTTPX = True
except ImportError:  # pragma: no cover
    _HTTPX = False


class XAIGrokVoice(BaseTTSProvider):
    PROVIDER_NAME = "xai_grok"
    DEFAULT_ENDPOINT = "https://api.x.ai/v1/audio/speech"

    async def synthesize(self, text: str, voice_id: Optional[str] = None, **opts: Any) -> VoiceResult:
        if not _HTTPX:
            return VoiceResult(provider=self.PROVIDER_NAME, error="httpx not installed")
        api_key = await read_vault_secret(self._vault, "xai", "api_key")
        if not api_key:
            return VoiceResult(provider=self.PROVIDER_NAME, error="xai api_key missing")

        endpoint = (
            opts.get("tts_endpoint")
            or self._config.get("tts_endpoint")
            or await read_vault_secret(self._vault, "xai", "tts_endpoint")
            or self.DEFAULT_ENDPOINT
        )
        voice = voice_id or self._config.get("voice", "grok")
        model = opts.get("model") or self._config.get("model", "grok-voice")
        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            "response_format": opts.get("response_format", "mp3"),
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(endpoint, headers=headers, json=payload)
                resp.raise_for_status()
                return VoiceResult(
                    provider=self.PROVIDER_NAME,
                    audio_bytes=resp.content,
                    mime_type="audio/mpeg",
                    meta={"model": model, "voice": voice, "endpoint": endpoint},
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("xai_grok_tts_failed", error=str(exc))
            return VoiceResult(provider=self.PROVIDER_NAME, error=str(exc))

    async def health_check(self) -> Dict[str, Any]:
        key = await read_vault_secret(self._vault, "xai", "api_key")
        return {"provider": self.PROVIDER_NAME, "configured": bool(key)}
