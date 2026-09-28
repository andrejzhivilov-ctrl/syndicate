"""OpenAI TTS provider (fallback voice)."""

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


class OpenAITTS(BaseTTSProvider):
    PROVIDER_NAME = "openai"
    ENDPOINT = "https://api.openai.com/v1/audio/speech"

    async def synthesize(self, text: str, voice_id: Optional[str] = None, **opts: Any) -> VoiceResult:
        if not _HTTPX:
            return VoiceResult(provider=self.PROVIDER_NAME, error="httpx not installed")
        api_key = await read_vault_secret(self._vault, "openai", "api_key")
        if not api_key:
            return VoiceResult(provider=self.PROVIDER_NAME, error="openai api_key missing")

        voice = voice_id or self._config.get("voice", "alloy")
        model = opts.get("model") or self._config.get("model", "tts-1")
        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            "response_format": opts.get("response_format", "mp3"),
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(self.ENDPOINT, headers=headers, json=payload)
                resp.raise_for_status()
                return VoiceResult(
                    provider=self.PROVIDER_NAME,
                    audio_bytes=resp.content,
                    mime_type="audio/mpeg",
                    meta={"model": model, "voice": voice},
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("openai_tts_failed", error=str(exc))
            return VoiceResult(provider=self.PROVIDER_NAME, error=str(exc))

    async def health_check(self) -> Dict[str, Any]:
        key = await read_vault_secret(self._vault, "openai", "api_key")
        return {"provider": self.PROVIDER_NAME, "configured": bool(key)}
