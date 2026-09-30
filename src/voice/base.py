"""Base classes and result container for EVA SYNDICATE voice providers (TTS & STT)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class VoiceResult:
    provider: str
    audio_bytes: Optional[bytes] = None
    mime_type: Optional[str] = None
    text: Optional[str] = None
    error: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.error is None and (self.audio_bytes is not None or self.text is not None)


class BaseTTSProvider:
    PROVIDER_NAME: str = "base_tts"

    def __init__(self, vault_client: Any = None, config: Optional[Dict[str, Any]] = None) -> None:
        self._vault = vault_client
        self._config = dict(config or {})

    async def synthesize(self, text: str, voice_id: Optional[str] = None, **opts: Any) -> VoiceResult:
        raise NotImplementedError

    async def health_check(self) -> Dict[str, Any]:
        return {"provider": self.PROVIDER_NAME, "configured": True}


class BaseSTTProvider:
    PROVIDER_NAME: str = "base_stt"

    def __init__(self, vault_client: Any = None, config: Optional[Dict[str, Any]] = None) -> None:
        self._vault = vault_client
        self._config = dict(config or {})

    async def transcribe(self, audio_bytes: bytes, language: str = "uk", **opts: Any) -> VoiceResult:
        raise NotImplementedError

    async def health_check(self) -> Dict[str, Any]:
        return {"provider": self.PROVIDER_NAME, "configured": True}
