"""
EVA SYNDICATE — Agent Runner
FastAPI application serving as the main entry point for the EVA orchestrator agent.
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.vault_client import VaultClient
from src.memory import MemoryManager
from src.orchestrator import EvaOrchestrator
from src.agents.sentinel import SentinelAgent

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
    orchestrator: Optional[EvaOrchestrator] = None
    sentinel: Optional[SentinelAgent] = None
    start_time: float = time.time()
    ready: bool = False

app_state = AppState()


# ─── Lifespan ───────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("EVA SYNDICATE agent starting up...")

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

        # 4. Initialize Sentinel
        app_state.sentinel = SentinelAgent(
            vault_client=app_state.vault_client,
        )

        # 5. Initialize Orchestrator
        llm_secrets = await app_state.vault_client.get_secret("eva/api-keys/data/llm")
        app_state.orchestrator = EvaOrchestrator(
            memory_manager=app_state.memory_manager,
            sentinel=app_state.sentinel,
            llm_config=llm_secrets,
        )
        await app_state.orchestrator.initialize()
        logger.info("EVA orchestrator initialized")

        # 6. Start token renewal background task
        asyncio.create_task(app_state.vault_client.start_token_renewal())

        app_state.ready = True
        logger.info("EVA SYNDICATE agent ready", uptime=0)

        yield  # Application runs here

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
    version="1.0.0",
    docs_url=None,  # Disable Swagger UI in production
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],  # No CORS — internal service
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


# ─── Dependency: Require Ready State ─────────────────────────────────────────

async def require_ready():
    if not app_state.ready:
        raise HTTPException(status_code=503, detail="Agent not ready")
    return app_state


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
async def status(state: AppState = Depends(require_ready)):
    """Detailed system status."""
    return {
        "version": "1.0.0",
        "agent": "eva-orchestrator",
        "uptime": round(time.time() - state.start_time, 2),
        "ready": state.ready,
    }


@app.post("/execute", response_model=ExecuteResponse)
async def execute_task(
    request: ExecuteRequest,
    state: AppState = Depends(require_ready),
):
    """Execute an agent task via the orchestrator."""
    logger.info("Task received", task_type=request.task_type, priority=request.priority)

    try:
        # Sentinel validation
        validation = await state.sentinel.validate_task(request.model_dump())
        if not validation.allowed:
            logger.warning("Task blocked by Sentinel", reason=validation.reason)
            raise HTTPException(status_code=403, detail=f"Task blocked: {validation.reason}")

        # Execute via orchestrator
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
    state: AppState = Depends(require_ready),
):
    """Unified webhook endpoint for external integrations (Telegram, n8n, etc.)."""
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
        log_config=None,  # structlog handles logging
    )
