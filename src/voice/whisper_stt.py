"""STT providers: local Whisper service (primary) + Groq Whisper (cloud fallback)."""

from __future__ import annotations

from typing import Any, Dict

import structlog

from src.voice._util import read_vault_secret
from src.voice.base import BaseSTTProvider, VoiceResult

logger = structlog.get_logger(__name__)

try:
    import httpx
    _HTTPX = True
except ImportError:  # pragma: no cover
    _HTTPX = False


class WhisperSTT(BaseSTTProvider):
    """Local faster-whisper service (see deploy/docker/whisper.Dockerfile)."""

    PROVIDER_NAME = "whisper_local"

    async def transcribe(self, audio_bytes: bytes, language: str = "uk", **opts: Any) -> VoiceResult:
        if not _HTTPX:
            return VoiceResult(provider=self.PROVIDER_NAME, error="httpx not installed")
        url = self._config.get("whisper_url", "http://whisper:9000/asr")
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                files = {"audio_file": ("audio.ogg", audio_bytes, "application/octet-stream")}
                resp = await client.post(url, params={"language": language}, files=files)
                resp.raise_for_status()
                data = resp.json()
                return VoiceResult(
                    provider=self.PROVIDER_NAME,
                    text=data.get("text"),
                    meta={"language": data.get("language"), "duration": data.get("duration")},
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("whisper_local_stt_failed", error=str(exc))
            return VoiceResult(provider=self.PROVIDER_NAME, error=str(exc))

    async def health_check(self) -> Dict[str, Any]:
        if not _HTTPX:
            return {"provider": self.PROVIDER_NAME, "configured": False}
        base = self._config.get("whisper_url", "http://whisper:9000/asr").rsplit("/", 1)[0]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{base}/health")
                return {"provider": self.PROVIDER_NAME, "configured": True, "healthy": resp.status_code == 200}
        except Exception as exc:  # noqa: BLE001
            return {"provider": self.PROVIDER_NAME, "configured": True, "healthy": False, "detail": str(exc)}


class GroqWhisperSTT(BaseSTTProvider):
    """Cloud fallback: Groq whisper-large-v3 (OpenAI-compatible transcriptions API)."""

    PROVIDER_NAME = "groq_whisper"
    ENDPOINT = "https://api.groq.com/openai/v1/audio/transcriptions"

    async def transcribe(self, audio_bytes: bytes, language: str = "uk", **opts: Any) -> VoiceResult:
        if not _HTTPX:
            return VoiceResult(provider=self.PROVIDER_NAME, error="httpx not installed")
        api_key = await read_vault_secret(self._vault, "groq", "api_key")
        if not api_key:
            return VoiceResult(provider=self.PROVIDER_NAME, error="groq api_key missing")
        model = opts.get("model") or self._config.get("model", "whisper-large-v3")
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                files = {"file": ("audio.ogg", audio_bytes, "application/octet-stream")}
                data = {"model": model, "language": language, "response_format": "json"}
                headers = {"Authorization": f"Bearer {api_key}"}
                resp = await client.post(self.ENDPOINT, headers=headers, data=data, files=files)
                resp.raise_for_status()
                payload = resp.json()
                return VoiceResult(
                    provider=self.PROVIDER_NAME,
                    text=payload.get("text"),
                    meta={"model": model},
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("groq_whisper_stt_failed", error=str(exc))
            return VoiceResult(provider=self.PROVIDER_NAME, error=str(exc))

    async def health_check(self) -> Dict[str, Any]:
        key = await read_vault_secret(self._vault, "groq", "api_key")
        return {"provider": self.PROVIDER_NAME, "configured": bool(key)}
