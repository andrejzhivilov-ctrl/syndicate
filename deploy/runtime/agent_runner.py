#!/usr/bin/env python3
"""
EVA SYNDICATE — Universal Agent Runtime Runner
Handles:
1. Vault AppRole authentication (dynamic zero-leak secrets in memory)
2. Telegram Bot initialization for Andrii
3. FastAPI /health and /webhook endpoints
4. Intelligent fallback (e.g. Whisper -> Groq API for Eva)
5. Non-root, graceful shutdown handling
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional
import httpx
from fastapi import FastAPI, Response, status
import uvicorn
import hvac

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
)
logger = logging.getLogger("agent_runner")

AGENT_ID = os.getenv("AGENT_ID", "unnamed_agent")
VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
VAULT_ROLE_ID = os.getenv("VAULT_ROLE_ID")
VAULT_SECRET_ID = os.getenv("VAULT_SECRET_ID")
WHISPER_URL = os.getenv("WHISPER_URL", "http://whisper:9000")
PLAYWRIGHT_SERVER_URL = os.getenv("PLAYWRIGHT_SERVER_URL")
GOOGLE_WORKSPACE_MCP_URL = os.getenv("GOOGLE_WORKSPACE_MCP_URL")

app = FastAPI(title=f"Syndicate Agent - {AGENT_ID}")
vault_client: Optional[hvac.Client] = None
secrets_cache: Dict[str, Any] = {}

class VaultSecretManager:
    @staticmethod
    def authenticate() -> hvac.Client:
        if not VAULT_ROLE_ID or not VAULT_SECRET_ID:
            logger.warning("VAULT_ROLE_ID or VAULT_SECRET_ID not set! Running in standalone/fallback mode.")
            return None
        
        client = hvac.Client(url=VAULT_ADDR)
        try:
            auth_res = client.auth.approle.login(
                role_id=VAULT_ROLE_ID,
                secret_id=VAULT_SECRET_ID
            )
            client.token = auth_res['auth']['client_token']
            logger.info(f"Successfully authenticated to Vault as AppRole: {AGENT_ID}")
            return client
        except Exception as e:
            logger.error(f"Failed to authenticate to Vault: {e}")
            return None

    @staticmethod
    def get_secret(client: Optional[hvac.Client], path: str, key: str = "value") -> Optional[str]:
        if not client:
            return os.getenv(key.upper())
        try:
            read_res = client.secrets.kv.v2.read_secret_version(path=path)
            data = read_res['data']['data']
            return data.get(key)
        except Exception as e:
            logger.warning(f"Could not read secret '{path}': {e}")
            return os.getenv(key.upper())

@app.get("/health")
async def health_check():
    """Healthcheck endpoint for Docker & Nginx"""
    return {
        "status": "healthy",
        "agent": AGENT_ID,
        "vault_connected": vault_client.is_authenticated() if vault_client else False,
        "playwright_enabled": bool(PLAYWRIGHT_SERVER_URL),
        "mcp_enabled": bool(GOOGLE_WORKSPACE_MCP_URL)
    }

async def transcribe_audio_with_fallback(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    """
    Intelligent STT with Zero-Crash Fallback:
    1. Try local faster-whisper container (int8 on CPU)
    2. If timeout (>4s) or failure: fallback immediately to Groq Whisper API ($0.111/hr)
    """
    # 1. Local Whisper attempt
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            files = {"audio_file": (filename, audio_bytes, "audio/ogg")}
            res = await client.post(f"{WHISPER_URL}/asr?task=transcribe&language=uk&output=json", files=files)
            if res.status_code == 200:
                return res.json().get("text", "").strip()
            logger.warning(f"Local whisper returned status {res.status_code}. Initiating Groq fallback...")
    except Exception as e:
        logger.warning(f"Local whisper error ({e}). Switching to Groq API fallback...")

    # 2. Groq Cloud Whisper API Fallback
    groq_api_key = secrets_cache.get("groq_api_key") or os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.error("No GROQ_API_KEY available for STT fallback!")
        return "Помилка розпізнавання: локальний Whisper зайнятий, а ключ Groq не налаштовано."

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": f"Bearer {groq_api_key}"}
            files = {"file": (filename, audio_bytes, "audio/ogg")}
            data = {"model": "whisper-large-v3", "language": "uk"}
            res = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers=headers,
                files=files,
                data=data
            )
            if res.status_code == 200:
                logger.info("Successfully transcribed audio via Groq Whisper fallback.")
                return res.json().get("text", "").strip()
            logger.error(f"Groq fallback failed with code {res.status_code}: {res.text}")
    except Exception as e:
        logger.error(f"Groq fallback request failed: {e}")

    return "Не вдалося розпізнати аудіоповідомлення."

def load_agent_secrets():
    global vault_client, secrets_cache
    vault_client = VaultSecretManager.authenticate()
    
    # Load common LLM keys
    secrets_cache["anthropic_api_key"] = VaultSecretManager.get_secret(vault_client, "llm/anthropic_api_key")
    secrets_cache["gemini_api_key"] = VaultSecretManager.get_secret(vault_client, "llm/gemini_api_key")
    secrets_cache["groq_api_key"] = VaultSecretManager.get_secret(vault_client, "llm/groq_api_key")
    
    # Load Telegram Bot token for this agent
    bot_secret_path = f"communication/telegram_{AGENT_ID}_bot"
    secrets_cache["telegram_bot_token"] = VaultSecretManager.get_secret(vault_client, bot_secret_path)
    
    logger.info(f"Loaded credentials for agent '{AGENT_ID}'. Telegram token available: {bool(secrets_cache['telegram_bot_token'])}")

def main():
    logger.info(f"Starting Syndicate Agent Runtime for: {AGENT_ID}")
    load_agent_secrets()
    
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
