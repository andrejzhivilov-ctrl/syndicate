"""
EVA SYNDICATE — Agent Runner (v4.1 Verified)
FastAPI application serving as the main entry point for the EVA orchestrator agent.
Fixes applied:
- Wires LessonsStore, ConfidenceBudget, and PIIRedactor into EvaOrchestrator
- Enforces API key authentication (X-API-Key / Bearer) on /execute and /status
- Enforces HMAC-SHA256 signature verification (Sentinel.verify_webhook_signature) on /webhook/{source}
"""

from __future__ import annotations

import asyncio
import hmac
import logging
import os
import signal
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

import structlog
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.agents.sentinel import SentinelAgent
from src.confidence import ConfidenceBudget
from src.integrations import build_default_registry
from src.lessons import LessonsStore
from src.memory import MemoryManager
from src.orchestrator import EvaOrchestrator
from src.pii import PIIRedactor
from src.runtime_config import build_runtime_config
from src.vault_client import VaultClient
from src.voice import build_voice_manager

# ─── Logging ────────────────────────────────────────────────────────────────

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(logging, os.getenv("LOG_LEVEL", "INFO"))
    ),
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger(__name__)


# ─── Application State ───────────────────────────────────────────────────────

class AppState:
    vault_client: Optional[VaultClient] = None
    memory_manager: Optional[MemoryManager] = None
    lessons_store: Optional[LessonsStore] = None
    confidence_budget: Optional[ConfidenceBudget] = None
    pii_redactor: Optional[PIIRedactor] = None
    orchestrator: Optional[EvaOrchestrator] = None
    sentinel: Optional[SentinelAgent] = None
    registry: Optional[Any] = None
    voice_manager: Optional[Any] = None
    api_key: Optional[str] = None
    webhook_secret: Optional[str] = None
    start_time: float = time.time()
    ready: bool = False


app_state = AppState()


# ─── Lifespan ───────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("EVA SYNDICATE agent starting up (v4.1)...")

    try:
        # 1. Initialize Vault client
        app_state.vault_client = VaultClient(
            vault_addr=os.environ["VAULT_ADDR"],
            role_id=os.environ["VAULT_ROLE_ID"],
            secret_id=os.environ["VAULT_SECRET_ID"],
        )
        await app_state.vault_client.authenticate()
        logger.info("Vault authentication successful")

        # 2. Retrieve database credentials from Vault
        db_secrets = await app_state.vault_client.get_secret("eva/database/data/postgres")

        # 3. Initialize Memory Manager
        postgres_dsn = (
            f"postgresql+asyncpg://{db_secrets['user']}:{db_secrets['password']}"
            f"@{os.getenv('POSTGRES_HOST', 'postgres')}:{os.getenv('POSTGRES_PORT', '5432')}"
            f"/{os.getenv('POSTGRES_DB', 'eva_syndicate')}"
        )
        redis_password = await app_state.vault_client.get_secret("eva/config/data/redis")
        redis_url = f"redis://:{redis_password.get('password', '')}@redis:6379/0"

        app_state.memory_manager = MemoryManager(
            postgres_dsn=postgres_dsn,
            redis_url=redis_url,
        )
        await app_state.memory_manager.initialize()
        logger.info("Memory manager initialized")

        # 4. Initialize v4 Core Modules (LessonsStore, ConfidenceBudget, PIIRedactor, Sentinel)
        app_state.lessons_store = LessonsStore(
            session_factory=app_state.memory_manager._session_factory,
            redis=app_state.memory_manager._redis,
        )
        app_state.confidence_budget = ConfidenceBudget()
        app_state.pii_redactor = PIIRedactor()
        app_state.sentinel = SentinelAgent(
            vault_client=app_state.vault_client,
        )

        # 5. Assemble runtime config + connector registry + voice subsystem
        runtime_config = build_runtime_config()
        app_state.registry = build_default_registry(
            vault_client=app_state.vault_client,
            config=runtime_config,
        )
        app_state.voice_manager = build_voice_manager(
            vault_client=app_state.vault_client,
            config=runtime_config,
        )

        # 6. Load API key & Webhook secret (Vault first, env fallback)
        try:
            auth_secrets = await app_state.vault_client.get_secret("eva/config/data/auth")
        except Exception:
            auth_secrets = {}
        app_state.api_key = auth_secrets.get("api_key") or os.getenv("EVA_API_KEY") or os.getenv("MCP_SIGNING_KEY")
        app_state.webhook_secret = auth_secrets.get("webhook_secret") or os.getenv("WEBHOOK_SECRET") or os.getenv("MCP_SIGNING_KEY")

        # 7. Initialize Orchestrator with all v4 components wired
        llm_secrets = await app_state.vault_client.get_secret("eva/api-keys/data/llm")
        app_state.orchestrator = EvaOrchestrator(
            memory_manager=app_state.memory_manager,
            sentinel=app_state.sentinel,
            llm_config=llm_secrets,
            config=runtime_config,
            registry=app_state.registry,
            voice_manager=app_state.voice_manager,
            lessons_store=app_state.lessons_store,
            confidence_budget=app_state.confidence_budget,
            pii_redactor=app_state.pii_redactor,
        )
        await app_state.orchestrator.initialize()
        logger.info("EVA orchestrator v4.1 initialized")

        # 8. Start token renewal background task
        asyncio.create_task(app_state.vault_client.start_token_renewal())

        app_state.ready = True
        logger.info("EVA SYNDICATE agent ready", uptime=0)

        yield

    except Exception as exc:
        logger.error("Fatal startup error", error=str(exc), exc_info=True)
        raise
    finally:
        logger.info("EVA SYNDICATE agent shutting down...")
        app_state.ready = False
        if app_state.memory_manager:
            await app_state.memory_manager.close()
        if app_state.vault_client:
            await app_state.vault_client.revoke_token()
            await app_state.vault_client.aclose()
        logger.info("Shutdown complete.")


# ─── FastAPI App ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="EVA SYNDICATE Agent",
    description="Autonomous multi-agent orchestration system",
    version="4.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# ─── Request/Response Models ─────────────────────────────────────────────────

class ExecuteRequest(BaseModel):
    task_type: str = Field(..., description="Type of task to execute")
    payload: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None
    priority: int = Field(default=5, ge=1, le=10)


class ExecuteResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    uptime: float
    vault_connected: bool
    memory_ready: bool
    orchestrator_ready: bool


# ─── Dependencies: Ready State & Authentication ─────────────────────────────

async def require_ready() -> AppState:
    if not app_state.ready:
        raise HTTPException(status_code=503, detail="Agent not ready")
    return app_state


async def require_auth(
    request: Request,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    state: AppState = Depends(require_ready),
) -> AppState:
    """Verify API Key or Bearer token on protected endpoints."""
    expected = state.api_key
    if not expected:
        # If no key configured in dev, allow internal requests from private subnets only
        client_host = request.client.host if request.client else ""
        if client_host.startswith(("127.", "10.", "172.", "192.168.")):
            return state
        raise HTTPException(status_code=401, detail="API authentication key not configured")

    provided = x_api_key
    if not provided and authorization and authorization.lower().startswith("bearer "):
        provided = authorization[7:].strip()

    if not provided or not hmac.compare_digest(provided.encode("utf-8"), expected.encode("utf-8")):
        logger.warning("Unauthorized API access attempt", client=request.client.host if request.client else "unknown")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    return state


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Liveness/readiness probe."""
    return HealthResponse(
        status="healthy" if app_state.ready else "starting",
        uptime=round(time.time() - app_state.start_time, 2),
        vault_connected=app_state.vault_client is not None and app_state.vault_client.is_authenticated,
        memory_ready=app_state.memory_manager is not None and app_state.memory_manager.is_ready,
        orchestrator_ready=app_state.orchestrator is not None,
    )


@app.get("/status")
async def status(state: AppState = Depends(require_auth)):
    """Detailed system status (authenticated)."""
    return {
        "version": "4.1.0",
        "agent": "eva-orchestrator",
        "uptime": round(time.time() - state.start_time, 2),
        "ready": state.ready,
        "v4_modules": {
            "lessons_store": state.lessons_store is not None,
            "confidence_budget": state.confidence_budget is not None,
            "pii_redactor": state.pii_redactor is not None,
        },
        "connectors": list(state.registry._connectors) if state.registry else [],
        "voice": {
            "tts": [p.PROVIDER_NAME for p in state.voice_manager._tts]
            if state.voice_manager else [],
            "stt": [p.PROVIDER_NAME for p in state.voice_manager._stt]
            if state.voice_manager else [],
        },
    }


@app.post("/execute", response_model=ExecuteResponse)
async def execute_task(
    request: ExecuteRequest,
    state: AppState = Depends(require_auth),
):
    """Execute an agent task via the orchestrator (authenticated)."""
    logger.info("Task received", task_type=request.task_type, priority=request.priority)

    try:
        validation = await state.sentinel.validate_task(request.model_dump())
        if not validation.allowed:
            logger.warning("Task blocked by Sentinel", reason=validation.reason)
            raise HTTPException(status_code=403, detail=f"Task blocked: {validation.reason}")

        result = await state.orchestrator.execute(
            task_type=request.task_type,
            payload=request.payload,
            session_id=request.session_id,
        )

        return ExecuteResponse(
            task_id=result["task_id"],
            status=result["status"],
            result=result.get("result"),
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Task execution failed", error=str(exc), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal execution error")


@app.post("/webhook/{source}")
async def webhook_handler(
    source: str,
    request: Request,
    x_hub_signature_256: Optional[str] = Header(default=None, alias="X-Hub-Signature-256"),
    x_telegram_secret: Optional[str] = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
    state: AppState = Depends(require_ready),
):
    """Unified webhook endpoint with HMAC signature / secret token verification."""
    raw_bytes = await request.body()

    if state.webhook_secret:
        sig = x_hub_signature_256 or ""
        if sig:
            valid = await state.sentinel.verify_webhook_signature(raw_bytes, sig, state.webhook_secret)
            if not valid:
                logger.warning("Webhook HMAC verification failed", source=source)
                raise HTTPException(status_code=401, detail="Invalid webhook signature")
        elif x_telegram_secret:
            if not hmac.compare_digest(x_telegram_secret.encode("utf-8"), state.webhook_secret.encode("utf-8")):
                logger.warning("Telegram webhook secret mismatch", source=source)
                raise HTTPException(status_code=401, detail="Invalid Telegram secret token")
        else:
            logger.warning("Webhook missing signature header", source=source)
            raise HTTPException(status_code=401, detail="Missing webhook signature")

    body = await request.json()
    logger.info("Webhook received", source=source)

    try:
        result = await state.orchestrator.handle_webhook(source=source, payload=body)
        return {"ok": True, "result": result}
    except Exception as exc:
        logger.error("Webhook handling failed", source=source, error=str(exc))
        return Response(content='{"ok": false}', status_code=200, media_type="application/json")


# ─── Graceful Shutdown ───────────────────────────────────────────────────────

def _signal_handler(sig, frame):
    logger.info("Shutdown signal received", signal=sig)


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


if __name__ == "__main__":
    uvicorn.run(
        "agent_runner:app",
        host="0.0.0.0",
        port=8000,
        workers=1,
        log_config=None,
    )
