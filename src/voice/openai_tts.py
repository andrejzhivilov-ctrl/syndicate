"""OpenAI TTS fallback provider."""

from __future__ import annotations

from typing import Any, Optional

import httpx
import structlog

from src.voice._util import read_vault_secret
from src.voice.base import BaseTTSProvider, VoiceResult

logger = structlog.get_logger(__name__)


class OpenAITTS(BaseTTSProvider):
    PROVIDER_NAME = "openai"
    BASE = "https://api.openai.com/v1/audio/speech"

    async def synthesize(self, text: str, voice_id: Optional[str] = None, **opts: Any) -> VoiceResult:
        api_key = await read_vault_secret(self._vault, "llm", "openai_api_key") or await read_vault_secret(
            self._vault, "openai", "api_key"
        )
        if not api_key:
            return VoiceResult(provider=self.PROVIDER_NAME, error="openai api_key missing")

        voice = voice_id or self._config.get("voice", "nova")
        model = opts.get("model") or self._config.get("model", "tts-1")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    self.BASE,
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"model": model, "input": text, "voice": voice, "response_format": "mp3"},
                )
                resp.raise_for_status()
                return VoiceResult(
                    provider=self.PROVIDER_NAME,
                    audio_bytes=resp.content,
                    mime_type="audio/mpeg",
                    meta={"voice": voice, "model": model},
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("openai_tts_failed", error=str(exc))
            return VoiceResult(provider=self.PROVIDER_NAME, error=str(exc))
