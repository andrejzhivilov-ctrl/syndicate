"""
Provider-agnostic voice interfaces (TTS + STT).
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class VoiceResult:
    """Unified result for TTS/STT operations."""
    provider: str
    audio_bytes: Optional[bytes] = None
    text: Optional[str] = None
    mime_type: str = "application/octet-stream"
    error: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    @property
    def ok(self) -> bool:
        return self.error is None


class BaseTTSProvider(abc.ABC):
    """Text-to-speech provider."""

    PROVIDER_NAME: str = "base_tts"

    def __init__(self, vault_client: Any = None, config: Optional[Dict[str, Any]] = None) -> None:
        self._vault = vault_client
        self._config = config or {}

    @abc.abstractmethod
    async def synthesize(self, text: str, voice_id: Optional[str] = None, **opts: Any) -> VoiceResult:
        raise NotImplementedError

    @abc.abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        raise NotImplementedError


class BaseSTTProvider(abc.ABC):
    """Speech-to-text provider."""

    PROVIDER_NAME: str = "base_stt"

    def __init__(self, vault_client: Any = None, config: Optional[Dict[str, Any]] = None) -> None:
        self._vault = vault_client
        self._config = config or {}

    @abc.abstractmethod
    async def transcribe(self, audio_bytes: bytes, language: str = "uk", **opts: Any) -> VoiceResult:
        raise NotImplementedError

    @abc.abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        raise NotImplementedError
