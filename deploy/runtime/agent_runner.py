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
import contextlib
import hmac
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

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
        structlog.processors.add_log_level,
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
    vault_renewal_task: Optional[Any] = None


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

        # 8. Start token renewal background task (keep a reference: a bare
        #    create_task() result can be garbage-collected mid-flight).
        app_state.vault_renewal_task = asyncio.create_task(
            app_state.vault_client.start_token_renewal()
        )

        app_state.ready = True
        logger.info("EVA SYNDICATE agent ready", uptime=0)

        yield

    except Exception as exc:
        logger.error("Fatal startup error", error=str(exc), exc_info=True)
        raise
    finally:
        logger.info("EVA SYNDICATE agent shutting down...")
        app_state.ready = False
        if app_state.vault_renewal_task is not None:
            app_state.vault_renewal_task.cancel()
            with contextlib.suppress(BaseException):
                await app_state.vault_renewal_task
            app_state.vault_renewal_task = None
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


# ─── JSON sanitization ───────────────────────────────────────────────────────

_MAX_STR = 20_000


def _json_safe(value: Any, _depth: int = 0) -> Any:
    """Convert an arbitrary agent result into something ``json.dumps`` accepts.

    Agent handlers occasionally return bytes, datetimes, sets or dataclasses.
    Those turned a successful task into a 500 at serialization time, so coerce
    them here instead of letting the error escape the endpoint.
    """
    if _depth > 12:
        return str(value)
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
            return str(value)
        if isinstance(value, str) and len(value) > _MAX_STR:
            return value[:_MAX_STR] + "…[truncated]"
        return value
    if isinstance(value, (bytes, bytearray)):
        return f"<{len(value)} bytes>"
    if isinstance(value, dict):
        return {str(k): _json_safe(v, _depth + 1) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_safe(v, _depth + 1) for v in value]
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _json_safe(value.to_dict(), _depth + 1)
    if hasattr(value, "__dict__"):
        return _json_safe(vars(value), _depth + 1)
    return str(value)


# ─── Request/Response Models ─────────────────────────────────────────────────

class ExecuteRequest(BaseModel):
    task_type: str = Field(..., description="Type of task to execute")
    payload: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None
    priority: int = Field(default=5, ge=1, le=10)


class ExecuteResponse(BaseModel):
    task_id: str
    status: str
    # Handlers legitimately return lists/scalars (e.g. ``sensory.*`` chunk lists)
    # and previously raw ``bytes`` leaked in and made json.dumps blow up with a
    # 500 after the task had already succeeded. Keep it permissive and sanitize
    # non-JSON-serialisable payloads at the edge instead of failing the request.
    result: Optional[Any] = None
    message: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    uptime: float
    vault_connected: bool
    memory_ready: bool
    orchestrator_ready: bool


# ─── Dependencies: Ready State & Authentication ─────────────────────────────

def _is_private_client(host: str) -> bool:
    """Loopback / RFC1918 / IPv6 ULA check for the unauthenticated dev fallback."""
    host = (host or "").strip().lower()
    if not host:
        return False
    if host in ("::1", "::ffff:127.0.0.1", "localhost"):
        return True
    if host.startswith("127.") or host.startswith("::ffff:127."):
        return True
    if host.startswith("10.") or host.startswith("192.168."):
        return True
    if host.startswith("172."):
        try:
            second = int(host.split(".")[1])
        except (IndexError, ValueError):
            return False
        return 16 <= second <= 31          # 172.16.0.0/12 only
    if host.startswith("fd") or host.startswith("fc"):
        return True                        # IPv6 unique local addresses
    return False


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
        # If no key is configured (dev only), allow internal requests from
        # loopback / RFC1918 private ranges. NOTE: "172." alone is NOT enough —
        # only 172.16.0.0/12 is private; 172.32.x.x is public address space.
        client_host = (request.client.host if request.client else "") or ""
        if _is_private_client(client_host):
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

@app.get("/", response_class=HTMLResponse)
@app.get("/cockpit", response_class=HTMLResponse)
async def cockpit_interface():
    """Serve the interactive SYNDIKAT Executive Cockpit interface."""
    # Ordered from the packaged layout (/app/cockpit.html, /app/runtime/cockpit.html)
    # to the source checkout (repository root). Earlier revisions probed a
    # directory layout that no longer exists in this repository.
    here = Path(__file__).resolve().parent
    candidates = [
        here / "cockpit.html",
        here.parent / "cockpit.html",
        here.parent / "static" / "cockpit.html",
        here.parents[1] / "cockpit.html",
        here.parents[1] / "syndikat_cockpit.html",
        here.parents[1] / "static" / "cockpit.html",
        Path("cockpit.html"),
    ]
    for p in candidates:
        if p.exists():
            text = p.read_text(encoding="utf-8")
            if "SYNDIKAT" not in text and "SYNDICATE" in text:
                text = text.replace("<title>SYNDICATE", "<title>SYNDIKAT / SYNDICATE")
            return HTMLResponse(content=text)
    return HTMLResponse("<h2>SYNDIKAT Cockpit File Not Found</h2>", status_code=404)


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
            result=_json_safe(result.get("result")),
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Task execution failed", error=str(exc), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal execution error")


@app.post("/webhook/error")
async def error_webhook(request: Request, state: AppState = Depends(require_ready)):
    """Dead-letter error recording from n8n / subagents (Floor 1)."""
    body = await request.json()
    result = await state.orchestrator.execute("record_error", body)
    return {"ok": True, "result": result}


@app.post("/webhook/{source}")
async def webhook_handler(
    source: str,
    request: Request,
    x_hub_signature_256: Optional[str] = Header(default=None, alias="X-Hub-Signature-256"),
    x_webhook_signature: Optional[str] = Header(default=None, alias="X-Webhook-Signature"),
    x_telegram_secret: Optional[str] = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
    state: AppState = Depends(require_ready),
):
    """Unified webhook endpoint with HMAC signature / secret token verification."""
    raw_bytes = await request.body()

    if state.webhook_secret:
        sig = x_hub_signature_256 or x_webhook_signature or ""
        if sig.startswith("sha256="):
            sig = sig[7:]
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


# ─── 10-Floor Specialized Endpoints ──────────────────────────────────────────

@app.get("/floors")
async def get_floors_registry(state: AppState = Depends(require_ready)):
    """Return the single source of truth 10-floor syndicate layout."""
    if state.orchestrator:
        return state.orchestrator.get_floors_registry()
    from src.floors import FLOORS, active_floors, reserved_floors
    return {"floors": FLOORS, "active": active_floors(), "reserved": reserved_floors()}


@app.post("/sensory/extract")
async def sensory_extract(request: Request, state: AppState = Depends(require_auth)):
    """Deterministic document extraction (Floor 1)."""
    body = await request.json()
    result = await state.orchestrator.execute("sensory_extract_doc", body)
    return result


@app.post("/sensory/chunk")
async def sensory_chunk(request: Request, state: AppState = Depends(require_auth)):
    """Deterministic text chunker for embeddings (Floor 1)."""
    body = await request.json()
    result = await state.orchestrator.execute("sensory_chunk_text", body)
    return result


@app.post("/proactive/morning")
async def trigger_morning_briefing(state: AppState = Depends(require_auth)):
    """Trigger 07:30 morning briefing (Floor 1 / Floor 10)."""
    result = await state.orchestrator.proactive_daily_briefing()
    return {"ok": True, "briefing": result}


@app.post("/proactive/evening")
async def trigger_evening_reflection(state: AppState = Depends(require_auth)):
    """Trigger 21:00 evening reflection (Floor 1 / Floor 8 / Floor 9)."""
    result = await state.orchestrator.proactive_evening_reflection()
    return {"ok": True, "reflection": result}


@app.post("/council")
async def deliberate_council(request: Request, state: AppState = Depends(require_auth)):
    """Multi-model LLM Council deliberation (Floor 10)."""
    body = await request.json()
    result = await state.orchestrator.execute("council_deliberate", body)
    return result


@app.post("/cr/submit")
async def submit_cr(request: Request, state: AppState = Depends(require_auth)):
    """Submit Change Request for protected statutes / dossiers (Floor 10)."""
    body = await request.json()
    result = await state.orchestrator.execute("submit_change_request", body)
    return result


@app.post("/cr/review")
async def review_cr(request: Request, state: AppState = Depends(require_auth)):
    """Review Change Request (approve/reject) (Floor 10)."""
    body = await request.json()
    result = await state.orchestrator.execute("review_change_request", body)
    return result


@app.post("/cr/apply")
async def apply_cr(request: Request, state: AppState = Depends(require_auth)):
    """Apply approved Change Request to vault (Floor 10)."""
    body = await request.json()
    result = await state.orchestrator.execute("apply_change_request", body)
    return result


# ─── Graceful Shutdown ───────────────────────────────────────────────────────
# NOTE: this module previously installed its own SIGTERM/SIGINT handler that only
# logged the signal and returned. Handlers registered at import time override the
# server's own ones, so the process never actually stopped on SIGTERM and had to
# be SIGKILLed (10s docker stop timeout, dropped in-flight requests). Signal
# handling is left to uvicorn, which shuts the ASGI app down gracefully.

if __name__ == "__main__":
    uvicorn.run(
        "agent_runner:app",
        host="0.0.0.0",
        port=8000,
        workers=1,
        log_config=None,
    )
