"""ElevenLabs TTS provider (EVA's primary live voice)."""

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


class ElevenLabsTTS(BaseTTSProvider):
    PROVIDER_NAME = "elevenlabs"
    BASE = "https://api.elevenlabs.io/v1"

    async def synthesize(self, text: str, voice_id: Optional[str] = None, **opts: Any) -> VoiceResult:
        if not _HTTPX:
            return VoiceResult(provider=self.PROVIDER_NAME, error="httpx not installed")
        api_key = await read_vault_secret(self._vault, "elevenlabs", "api_key")
        if not api_key:
            return VoiceResult(provider=self.PROVIDER_NAME, error="elevenlabs api_key missing")

        voice = voice_id or self._config.get("voice_id") or await read_vault_secret(
            self._vault, "elevenlabs", "voice_id"
        )
        if not voice:
            return VoiceResult(provider=self.PROVIDER_NAME, error="elevenlabs voice_id missing")

        model_id = opts.get("model_id") or self._config.get("model_id", "eleven_multilingual_v2")
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": float(opts.get("stability", self._config.get("stability", 0.5))),
                "similarity_boost": float(
                    opts.get("similarity_boost", self._config.get("similarity_boost", 0.75))
                ),
            },
        }
        headers = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
        url = f"{self.BASE}/text-to-speech/{voice}/stream"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                return VoiceResult(
                    provider=self.PROVIDER_NAME,
                    audio_bytes=resp.content,
                    mime_type="audio/mpeg",
                    meta={"model_id": model_id, "voice_id": voice},
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("elevenlabs_tts_failed", error=str(exc))
            return VoiceResult(provider=self.PROVIDER_NAME, error=str(exc))

    async def health_check(self) -> Dict[str, Any]:
        key = await read_vault_secret(self._vault, "elevenlabs", "api_key")
        return {"provider": self.PROVIDER_NAME, "configured": bool(key)}
