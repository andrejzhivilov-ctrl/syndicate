"""
SYNDICATE — Agent Runner (v4.1 Verified)
FastAPI application serving as the main entry point for the EVA orchestrator agent.
Fixes applied:
- Wires LessonsStore, ConfidenceBudget, and PIIRedactor into EvaOrchestrator
- Enforces API key authentication (X-API-Key / Bearer) on /execute and /status
- Enforces HMAC-SHA256 signature verification (Sentinel.verify_webhook_signature) on /webhook/{source}
"""

from __future__ import annotations

import asyncio
import base64
import binascii
import contextlib
import hmac
import json
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

from pydantic import BaseModel, Field

# Running this file directly — ``python deploy/runtime/agent_runner.py`` — puts
# ``deploy/runtime`` on sys.path instead of the repository root, so every
# ``src.*`` import below died with ``ModuleNotFoundError: No module named 'src'``.
# The container sets PYTHONPATH=/app and the tests add the paths themselves, so
# only a local operator hit this. Third-party imports stay above the block, so
# just the project imports carry the E402 exception.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.agents.sentinel import SentinelAgent  # noqa: E402
from src.confidence import ConfidenceBudget  # noqa: E402
from src.change_requests import ChangeRequestError  # noqa: E402
from src.device_auth import DEFAULT_TTL_SECONDS, DeviceTokenStore, KNOWN_SCOPES  # noqa: E402
from src.integrations import build_default_registry  # noqa: E402
from src.lessons import LessonsStore  # noqa: E402
from src.embeddings import build_embedding_provider  # noqa: E402
from src.memory import MemoryManager  # noqa: E402
from src.orchestrator import OPERATOR_ONLY_TASK_TYPES, EvaOrchestrator  # noqa: E402
from src.hitl_queue import HitlError  # noqa: E402
from src.directors_registry import roster as directors_roster  # noqa: E402
from src.lockdown import Lockdown  # noqa: E402
from src.telegram_gateway import (  # noqa: E402
    TelegramGateway,
    extract_message,
    is_director,
    reply_text,
    verify_webhook_secret,
)
from src.obsidian_sync import from_env as obsidian_sync_from_env  # noqa: E402
from src.sensitive import voice_text  # noqa: E402
from src.voice_reply import (  # noqa: E402
    VOICE_MAX_BYTES,
    VOICE_MAX_SECONDS,
    RespeecherTTS,
    spoken_text,
    transcribe,
    wants_voice,
    wav_to_ogg_opus,
)
from src.agent_platform.director_client import build_director_clients  # noqa: E402
from src.pii import PIIRedactor  # noqa: E402
from src.runtime_config import build_runtime_config  # noqa: E402
from src.vault_client import VaultClient, is_placeholder_secret  # noqa: E402
from src.vault_paths import secret_path  # noqa: E402
from src.voice import build_voice_manager  # noqa: E402

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
    embedding_provider: Optional[Any] = None
    lessons_store: Optional[LessonsStore] = None
    confidence_budget: Optional[ConfidenceBudget] = None
    pii_redactor: Optional[PIIRedactor] = None
    orchestrator: Optional[EvaOrchestrator] = None
    sentinel: Optional[SentinelAgent] = None
    registry: Optional[Any] = None
    voice_manager: Optional[Any] = None
    api_key: Optional[str] = None
    webhook_secret: Optional[str] = None
    # Per-device tokens for PC/mobile clients. Never expose the master
    # api_key to a client binary — hand out these instead.
    device_tokens: Optional[DeviceTokenStore] = None
    device_purge_task: Optional[Any] = None
    # HITL surface: pending change-requests + an in-process push channel.
    change_request_store: Optional[Any] = None
    change_request_notifier: Optional[Any] = None
    telegram_gateway: Optional[TelegramGateway] = None
    respeecher: Optional[RespeecherTTS] = None
    start_time: float = time.time()
    ready: bool = False
    vault_renewal_task: Optional[Any] = None
    obsidian_sync_task: Optional[Any] = None


app_state = AppState()


# ─── Startup configuration ───────────────────────────────────────────────────

_VAULT_ENV_VARS = ("VAULT_ADDR", "VAULT_ROLE_ID", "VAULT_SECRET_ID")


def _load_local_dotenv() -> None:
    """Load ``.env`` once, for operators running outside Docker.

    ``python-dotenv`` was already a declared dependency and the runbook tells the
    operator to ``cp .env.example .env``, but nothing ever read the file — the
    agent only looked at the process environment, so a local run failed even with
    a perfectly good ``.env`` sitting in the repository root.

    ``override=False``: the real environment (Compose, systemd) always wins, so
    this can never silently replace injected production values.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:  # pragma: no cover - python-dotenv is a declared dependency
        logger.warning("dotenv_not_installed", note=".env will not be loaded")
        return

    env_file = Path(os.getenv("EVA_DOTENV_FILE") or (_REPO_ROOT / ".env"))
    if env_file.is_file():
        load_dotenv(env_file, override=False)
        logger.info("dotenv_loaded", path=str(env_file))


def _require_secret(secrets: Dict[str, Any], key: str, path: str) -> Any:
    """Read a mandatory key, naming the Vault path when it is unusable.

    ``db_secrets["password"]`` used to raise a bare ``KeyError: 'password'``
    inside the lifespan traceback — the operator had no way to tell whether the
    secret was missing, empty, or still holding a fill-me-in marker (the client
    drops placeholders, see ``VaultClient.get_secret``).
    """
    if key not in secrets or is_placeholder_secret(secrets.get(key)):
        keys = ", ".join(sorted(secrets)) or "none"
        raise RuntimeError(
            f"Vault secret '{path}' has no usable '{key}' "
            f"(usable keys: {keys}). Fill it in on the server: "
            f"deploy/scripts/vault_init.sh or `vault kv put {path.replace('/data/', '/')}`. "
            "Placeholder values (CHANGE_ME*/PLACEHOLDER*) count as absent by design."
        )
    return secrets[key]


def _vault_env() -> Dict[str, str]:
    """Read the Vault bootstrap variables, or fail with an actionable message.

    These used to be read with ``os.environ[...]``, so a missing variable
    surfaced as ``KeyError: 'VAULT_ADDR'`` inside a lifespan traceback: the
    operator saw a crash but no hint about which file to fix. A blank value is
    treated as missing — Compose happily substitutes an empty string for an
    unset variable, and an empty VAULT_ADDR fails much later with a confusing
    connection error instead of here.
    """
    missing = [name for name in _VAULT_ENV_VARS if not os.environ.get(name, "").strip()]
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + ". Copy .env.example to .env and fill them in (see DEPLOYMENT_RUNBOOK.md"
            " section 2), or export them before starting the agent."
        )
    return {name: os.environ[name] for name in _VAULT_ENV_VARS}


# ─── Lifespan ───────────────────────────────────────────────────────────────

async def _purge_device_tokens(interval_seconds: int = 3600) -> None:
    """Background sweep: drop device tokens that died long ago.

    Module-level (not a closure inside ``lifespan``) to keep the startup
    function's cyclomatic complexity under the C901 gate.

    This must stay a plain coroutine: ``lifespan`` starts it with
    ``asyncio.create_task()``. A stray ``@asynccontextmanager`` here (left over
    from an earlier refactor) turned the call into an
    ``_AsyncGeneratorContextManager``, so ``create_task`` raised
    ``TypeError: a coroutine was expected`` at startup step 8b and the agent
    could never boot — with or without a working Vault.
    """
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            if app_state.device_tokens is not None:
                removed = await app_state.device_tokens.purge_expired()
                if removed:
                    logger.info("device_tokens_purged", removed=removed)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.warning("device_token_purge_failed", error=str(exc))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("SYNDICATE agent starting up (v4.1)...")

    try:
        # 1. Initialize Vault client
        _load_local_dotenv()
        vault_env = _vault_env()
        app_state.vault_client = VaultClient(
            vault_addr=vault_env["VAULT_ADDR"],
            role_id=vault_env["VAULT_ROLE_ID"],
            secret_id=vault_env["VAULT_SECRET_ID"],
        )
        await app_state.vault_client.authenticate()
        logger.info("Vault authentication successful")

        # 2. Retrieve database credentials from Vault
        db_secrets = await app_state.vault_client.get_secret(secret_path("database"))

        # 3. Initialize Memory Manager
        db_path = secret_path("database")
        postgres_dsn = (
            f"postgresql+asyncpg://{_require_secret(db_secrets, 'user', db_path)}"
            f":{_require_secret(db_secrets, 'password', db_path)}"
            f"@{os.getenv('POSTGRES_HOST', 'postgres')}:{os.getenv('POSTGRES_PORT', '5432')}"
            f"/{os.getenv('POSTGRES_DB', 'syndicate')}"
        )
        redis_secrets = await app_state.vault_client.get_secret(secret_path("redis"))
        redis_password = _require_secret(redis_secrets, "password", secret_path("redis"))
        redis_url = f"redis://:{redis_password}@redis:6379/0"

        # Vector producer for semantic memory search. Absent EMBEDDINGS_URL is a
        # supported mode: memory keeps working, semantic recall reports "disabled".
        app_state.embedding_provider = build_embedding_provider()
        if app_state.embedding_provider is not None:
            probe = await app_state.embedding_provider.health()
            logger.info(
                "embedding_provider_configured",
                provider=app_state.embedding_provider.name,
                status=probe.get("status"),
                warning=probe.get("warning"),
            )

        app_state.memory_manager = MemoryManager(
            postgres_dsn=postgres_dsn,
            redis_url=redis_url,
            embedder=app_state.embedding_provider,
        )
        await app_state.memory_manager.initialize()
        logger.info("Memory manager initialized")

        # 4. Initialize v4 Core Modules (LessonsStore, ConfidenceBudget, PIIRedactor, Sentinel)
        app_state.lessons_store = LessonsStore(
            session_factory=app_state.memory_manager._session_factory,
            redis=app_state.memory_manager._redis,
            embedder=app_state.embedding_provider,
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
            auth_secrets = await app_state.vault_client.get_secret(secret_path("auth"))
        except Exception:
            # The agent API key is optional in dev (private-range fallback),
            # so a missing secret must not abort startup.
            auth_secrets = {}
        app_state.api_key = auth_secrets.get("api_key") or os.getenv("EVA_API_KEY") or os.getenv("MCP_SIGNING_KEY")
        app_state.webhook_secret = auth_secrets.get("webhook_secret") or os.getenv("WEBHOOK_SECRET") or os.getenv("MCP_SIGNING_KEY")

        # 6b. Per-device token store (PC/mobile clients). The master key above
        #     is never handed to a client binary; devices get their own
        #     short-lived, revocable tokens instead.
        app_state.device_tokens = DeviceTokenStore(
            memory=app_state.memory_manager,
            default_ttl_seconds=int(os.getenv("EVAS_DEVICE_TOKEN_TTL", DEFAULT_TTL_SECONDS)),
            max_tokens_per_device=int(os.getenv("EVAS_MAX_TOKENS_PER_DEVICE", "10")),
        )
        logger.info("Device token store initialized")

        # 7. Initialize Orchestrator with all v4 components wired
        llm_secrets = await app_state.vault_client.get_secret(secret_path("api-keys"))
        app_state.orchestrator = EvaOrchestrator(
            memory_manager=app_state.memory_manager,
            sentinel=app_state.sentinel,
            llm_config=llm_secrets,
            director_clients=build_director_clients(runtime_config, app_state.vault_client),
            vault_client=app_state.vault_client,
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
        app_state.vault_renewal_task = app_state.vault_client.ensure_token_renewal()

        # 8b. Sweep long-dead device tokens once an hour.
        app_state.device_purge_task = asyncio.create_task(_purge_device_tokens())

        # 8b'. Obsidian vault ⇄ Garage bucket (the hub for Andrii's PC and phone).
        sync = obsidian_sync_from_env(app_state.vault_client)
        if sync is not None:
            app_state.obsidian_sync_task = asyncio.create_task(sync.loop())

        # 8c. HITL surface: expose the orchestrator's change-request store and
        #     wire an in-process notifier so the client can be pushed when an
        #     agent proposes a protected change. The store is created inside the
        #     orchestrator, so we inject the notifier afterwards.
        from src.change_requests import ChangeRequestNotifier

        notifier = ChangeRequestNotifier()
        store = getattr(app_state.orchestrator, "_change_requests", None)
        if store is not None:
            store._notifier = notifier
        app_state.change_request_store = store
        app_state.change_request_notifier = notifier
        app_state.telegram_gateway = TelegramGateway(app_state.vault_client)
        logger.info("HITL surface initialized", change_requests=store is not None)

        app_state.ready = True
        logger.info("SYNDICATE agent ready", uptime=0)

        yield

    except Exception as exc:
        logger.error("Fatal startup error", error=str(exc), exc_info=True)
        raise
    finally:
        logger.info("SYNDICATE agent shutting down...")
        app_state.ready = False
        if app_state.vault_renewal_task is not None:
            app_state.vault_renewal_task.cancel()
            with contextlib.suppress(BaseException):
                await app_state.vault_renewal_task
        if app_state.device_purge_task is not None:
            app_state.device_purge_task.cancel()
            with contextlib.suppress(BaseException):
                await app_state.device_purge_task
            # This used to clear ``vault_renewal_task`` instead — a copy-paste
            # slip that dropped the reference to the wrong task and left the
            # purge task pointing at an already-cancelled object.
            app_state.device_purge_task = None
        if app_state.obsidian_sync_task is not None:
            app_state.obsidian_sync_task.cancel()
            with contextlib.suppress(BaseException):
                await app_state.obsidian_sync_task
            app_state.obsidian_sync_task = None
        if app_state.memory_manager:
            await app_state.memory_manager.close()
        if app_state.embedding_provider:
            await app_state.embedding_provider.close()
        if app_state.vault_client:
            await app_state.vault_client.revoke_token()
            await app_state.vault_client.aclose()
        logger.info("Shutdown complete.")


# ─── FastAPI App ─────────────────────────────────────────────────────────────

def _cors_origins() -> list:
    """Origins allowed to call this API from a browser.

    ``EVAS_CORS_ORIGINS`` is a comma-separated allowlist. It is empty by
    default: a desktop/mobile client that talks to the agent directly does not
    need CORS at all, and an open ``*`` policy would let any website the
    operator visits drive the agent with the browser's own credentials.
    """
    raw = os.getenv("EVAS_CORS_ORIGINS", "") or ""
    return [o.strip() for o in raw.split(",") if o.strip()]


app = FastAPI(
    title="SYNDICATE Agent",
    description="Autonomous multi-agent orchestration system",
    version="4.1.0",
    # OpenAPI stays on: it is the source of truth for the generated client
    # contract (apps/shared/api-contract.yaml). Serve it only when a key is
    # configured or the caller is on a private range.
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)


# ─── Emergency lockdown (manifest §11.2) ─────────────────────────────────────

#: While locked, only these state-changing routes stay reachable: the operator's
#: own HITL decisions, device-token admin and the lockdown endpoint itself.
_LOCKDOWN_ALLOWED_PREFIXES = ("/cr/review", "/cr/apply", "/hitl/", "/auth/", "/admin/lockdown")


@app.middleware("http")
async def lockdown_guard(request: Request, call_next):
    if request.method not in {"GET", "HEAD", "OPTIONS"} and Lockdown().is_locked():
        if not request.url.path.startswith(_LOCKDOWN_ALLOWED_PREFIXES):
            return Response(
                content=json.dumps({"detail": "lockdown_engaged", "status": "locked_down"}),
                status_code=503,
                media_type="application/json",
            )
    response = await call_next(request)
    # Credentials never belong in URLs, and the cockpit must not leak its own
    # address through Referer or be framed by another site.
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    return response


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


def _sse(event: str, data: Any) -> str:
    """Format one Server-Sent Event frame.

    ``data`` is run through ``_json_safe`` first, so a datetime or bytes from
    an agent result cannot crash serialization mid-stream (which would kill
    the response after the client already committed to reading it).
    """
    payload = json.dumps(_json_safe(data), ensure_ascii=False, default=str)
    # A literal newline inside data would terminate the frame early.
    payload = payload.replace("\n", "\\n")
    return f"event: {event}\ndata: {payload}\n\n"


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
    # Configuration-level facts, not a live probe of the embeddings service: a
    # healthcheck that blocked on another container would be worse than useless.
    # ``semantic_search_enabled=False`` is a supported mode (episodic memory only).
    semantic_search_enabled: bool = False
    embedding_failures: int = 0
    #: ``["<vault path>:<key>", ...]`` for secrets Vault holds only as
    #: fill-me-in markers (or empty). Names, never values: an operator needs to
    #: know *which* secret was never filled in, and the client drops such values
    #: anyway, so silently continuing would hide a half-configured Vault.
    vault_placeholder_secrets: List[str] = []


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


def _presented_credential(
    x_api_key: Optional[str],
    authorization: Optional[str],
    *,
    allow_basic: bool = False,
) -> str:
    """Read credentials from API-key/Bearer headers, and optionally Basic.

    Basic is only enabled for browser-facing read routes. Enter ``device`` as
    the username and a read-scoped device token as the password; sensitive
    API/HITL endpoints continue to require X-API-Key or Bearer explicitly.
    """
    if x_api_key:
        return x_api_key.strip()
    if not authorization:
        return ""

    scheme, separator, value = authorization.partition(" ")
    if not separator:
        return ""
    if scheme.lower() == "bearer":
        return value.strip()
    if scheme.lower() != "basic" or not allow_basic:
        return ""

    try:
        decoded = base64.b64decode(value.strip(), validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return ""
    username, colon, password = decoded.partition(":")
    # Only the documented username is accepted. A server-side edit once widened
    # this to admin/eva/root/empty, which turned the realm into a guessable
    # login form for the master key.
    if colon and hmac.compare_digest(username, "device"):
        return password
    return ""


def _client_host(request: Request) -> str:
    return (request.client.host if request.client else "") or "unknown"


def _private_dev_access_allowed(request: Request) -> bool:
    """Allow private-network fallback only on direct local/test connections.

    A request forwarded by Nginx carries these headers; its socket peer is the
    proxy's private container IP, not the original Internet client.
    """
    environment = (os.getenv("APP_ENV", "development") or "development").strip().lower()
    if environment not in {"dev", "development", "local", "test"}:
        return False
    if request.headers.get("x-forwarded-for") or request.headers.get("x-real-ip"):
        return False
    return _is_private_client(_client_host(request))


def _master_key_ok(provided: str, expected: Optional[str]) -> bool:
    """Constant-time compare against the shared master key."""
    if not provided or not expected:
        return False
    return hmac.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))


async def require_auth(
    request: Request,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    state: AppState = Depends(require_ready),
) -> AppState:
    """Verify a credential on protected endpoints.

    Two credential types are accepted:

    1. the **master key** (``EVA_API_KEY`` / Vault ``auth.api_key``) — for
       server-to-server calls and operator automation;
    2. a **per-device token** issued by ``POST /auth/device/enroll`` — for PC
       and mobile clients. These are short-lived, scoped and individually
       revocable, so a leaked phone does not mean re-keying the whole system.

    When no master key is configured, the private-range fallback is limited to
    direct loopback/RFC1918 requests in local/test ``APP_ENV`` modes; forwarded
    requests and production/staging environments fail closed.
    """
    expected = state.api_key
    provided = _presented_credential(x_api_key, authorization)

    if not expected and _private_dev_access_allowed(request):
        return state

    if expected and _master_key_ok(provided, expected):
        return state

    # Second credential type: a per-device token. The client never sees the
    # master key, so this is the only safe thing to compile into an app.
    if provided and state.device_tokens is not None:
        record = await state.device_tokens.verify(provided)
        if record is not None:
            # Expose to the endpoint so audit logs can name the device.
            request.state.device_id = record.device_id
            request.state.token_id = record.token_id
            request.state.scopes = list(record.scopes)
            return state

    logger.warning("Unauthorized API access attempt", client=_client_host(request))
    detail = "API authentication key not configured" if not expected else "Invalid or missing API key"
    raise HTTPException(status_code=401, detail=detail)


async def require_read(
    request: Request,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    state: AppState = Depends(require_ready),
) -> AppState:
    """Protect read-only UI/registry routes with a master key or ``read`` token.

    Unlike the development fallback in ``require_auth``, this surface fails
    closed when no master key is configured. Behind a reverse proxy,
    ``request.client.host`` is the proxy's private container address rather
    than the Internet client, so using the private-range fallback here would
    make an unauthenticated public request look trusted.
    """
    expected = state.api_key
    # Credentials are accepted only in headers (X-API-Key / Bearer / Basic). A
    # ``?token=`` query parameter was removed: URLs end up in nginx access logs,
    # browser history, screenshots and Referer headers.
    provided = _presented_credential(x_api_key, authorization, allow_basic=True)

    if expected and _master_key_ok(provided, expected):
        return state

    if provided and state.device_tokens is not None:
        record = await state.device_tokens.verify(provided, required_scope="read")
        if record is not None:
            request.state.device_id = record.device_id
            request.state.token_id = record.token_id
            request.state.scopes = list(record.scopes)
            return state

    logger.warning("Unauthorized read-surface access attempt", client=_client_host(request))
    detail = (
        "API authentication key not configured"
        if not expected
        else "Read scope required: use a read-scoped device token"
    )
    raise HTTPException(
        status_code=401,
        detail=detail,
        headers={"WWW-Authenticate": 'Basic realm="SYNDICATE", charset="UTF-8"'},
    )


async def require_master_key(
    request: Request,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    state: AppState = Depends(require_ready),
) -> AppState:
    """Administrative endpoints: the master key only.

    Device tokens must NOT be able to mint, list or revoke other devices'
    tokens — otherwise a stolen phone could replace the whole fleet.
    """
    expected = state.api_key
    provided = _presented_credential(x_api_key, authorization)

    if not expected:
        # Device administration must never fall back to a private-IP check:
        # through Nginx every public caller appears to come from its private
        # Docker address and could otherwise mint or revoke device tokens.
        raise HTTPException(status_code=401, detail="API authentication key not configured")

    if not _master_key_ok(provided, expected):
        logger.warning(
            "Unauthorized admin access attempt",
            client=_client_host(request),
        )
        if not provided:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
        # 403, not 401: the caller sent *a* credential, just not an
        # administrative one. Clients can tell "log in again" from
        # "you may not do this".
        raise HTTPException(status_code=403, detail="Master API key required for device administration")

    return state


async def require_hitl(
    request: Request,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    state: AppState = Depends(require_ready),
) -> AppState:
    """HITL surface: master key, or a device token carrying the ``hitl`` scope.

    Approving a change request is a sensitive action, so a general-purpose
    device token (``read`` / ``execute``) must NOT be able to do it. Only a
    token minted with ``scopes: ["hitl"]`` — or the master key — reaches these
    endpoints. This is what turns the phone into a deliberate "approve / reject"
    surface rather than a second, unconstrained control plane.
    """
    expected = state.api_key
    provided = _presented_credential(x_api_key, authorization)

    if not expected and _private_dev_access_allowed(request):
        request.state.actor = "operator:dev"
        return state

    if expected and _master_key_ok(provided, expected):
        request.state.actor = "operator"
        return state

    if provided and state.device_tokens is not None:
        record = await state.device_tokens.verify(provided, required_scope="hitl")
        if record is not None:
            request.state.device_id = record.device_id
            request.state.token_id = record.token_id
            request.state.actor = f"operator:device:{record.device_id}"
            return state

    logger.warning("Unauthorized HITL access attempt", client=_client_host(request))
    raise HTTPException(status_code=401, detail="HITL scope required: approve with a hitl-scoped token")


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
@app.get("/cockpit", response_class=HTMLResponse)
async def cockpit_interface(state: AppState = Depends(require_read)):  # noqa: ARG002
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
            if "<html" not in text.lower() and len(text.strip()) < 260:
                target = (p.parent / text.strip()).resolve()
                if target.is_file():
                    text = target.read_text(encoding="utf-8")
                else:
                    continue
            if "SYNDIKAT" not in text and "SYNDICATE" in text:
                text = text.replace("<title>SYNDICATE", "<title>SYNDIKAT / SYNDICATE")
            return HTMLResponse(content=text)
    return HTMLResponse("<h2>SYNDIKAT Cockpit File Not Found</h2>", status_code=404)


@app.get("/directors")
async def list_directors(state: AppState = Depends(require_read)) -> Dict[str, Any]:
    """The 18-director roster with *honest* live facts only.

    ``enabled`` is the orchestrator config flag (not a heartbeat) and
    ``bot_configured`` only says that a bot token exists in Vault. There is no
    fabricated "Working / Idle" state: if a fact is unknown it is ``null``.
    """
    gateway = state.telegram_gateway
    config = getattr(state.orchestrator, "_config", {}) or {}
    directors = directors_roster()

    async def _bot(agent_id: str) -> Optional[bool]:
        if gateway is None:
            return None
        try:
            return bool(await gateway.bot_token(agent_id))
        except Exception:  # noqa: BLE001
            return None

    flags = await asyncio.gather(*(_bot(d["id"]) for d in directors))
    for director, bot_ok in zip(directors, flags, strict=False):
        entry = config.get(director["id"]) if isinstance(config, dict) else None
        director["enabled"] = entry.get("enabled") is True if isinstance(entry, dict) and "enabled" in entry else None
        director["bot_configured"] = bot_ok
    return {"directors": directors, "count": len(directors), "lockdown": Lockdown().is_locked()}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Liveness/readiness probe."""
    return HealthResponse(
        status="healthy" if app_state.ready else "starting",
        uptime=round(time.time() - app_state.start_time, 2),
        vault_connected=app_state.vault_client is not None and app_state.vault_client.is_authenticated,
        memory_ready=app_state.memory_manager is not None and app_state.memory_manager.is_ready,
        orchestrator_ready=app_state.orchestrator is not None,
        semantic_search_enabled=bool(
            app_state.memory_manager is not None and app_state.memory_manager.embeddings_enabled
        ),
        embedding_failures=int(
            getattr(app_state.memory_manager, "embedding_failures", 0) or 0
        ),
        vault_placeholder_secrets=[
            f"{path}:{key}"
            for path, key in getattr(app_state.vault_client, "placeholder_keys", []) or []
        ],
    )


# ─── Device tokens (PC / mobile clients) ─────────────────────────────────────
#
# A client binary must never embed the master ``EVA_API_KEY``: anything shipped
# in an APK/IPA/desktop build can be extracted, and the master key cannot be
# revoked per device. Instead a device enrols once (using the master key, from
# the operator's own machine) and receives a short-lived, scoped token that it
# can rotate and that can be revoked individually.


class DeviceEnrollRequest(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=128, description="Stable id chosen by the client")
    label: str = Field(default="", max_length=200, description="Human label, e.g. 'Andrii Pixel 8'")
    scopes: list = Field(default_factory=list, description=f"Subset of {list(KNOWN_SCOPES)}; empty = no device scope")
    ttl_seconds: Optional[int] = Field(default=None, ge=60, le=365 * 24 * 3600)


class DeviceTokenRequest(BaseModel):
    token: str = Field(..., min_length=1, description="The device token to rotate")


class DeviceRevokeRequest(BaseModel):
    token_id: str = Field(..., min_length=1, max_length=32)


@app.post("/auth/device/enroll")
async def enroll_device(
    payload: DeviceEnrollRequest,
    state: AppState = Depends(require_master_key),
) -> Dict[str, Any]:
    """Issue a new per-device token. Returns the plaintext token exactly once."""
    if state.device_tokens is None:
        raise HTTPException(status_code=503, detail="Device token store not initialized")
    try:
        issued = await state.device_tokens.enroll(
            device_id=payload.device_id,
            label=payload.label,
            scopes=list(payload.scopes or []),
            ttl_seconds=payload.ttl_seconds,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    logger.info("device_enrolled", device_id=payload.device_id, token_id=issued["token_id"])
    return issued


@app.post("/auth/device/refresh")
async def refresh_device(
    payload: DeviceTokenRequest,
    state: AppState = Depends(require_ready),
) -> Dict[str, Any]:
    """Rotate a device token: revoke the presented one, issue a fresh one.

    Authenticated by the token **in the body**, not by a header: this is the
    refresh call, so requiring a still-valid credential in a header would make
    rotation impossible exactly when it is needed. The token is 32 bytes of
    CSPRNG output, so the endpoint is not a practical guessing oracle.
    """
    if state.device_tokens is None:
        raise HTTPException(status_code=503, detail="Device token store not initialized")
    rotated = await state.device_tokens.refresh(payload.token)
    if rotated is None:
        raise HTTPException(status_code=401, detail="Invalid, expired or revoked device token")
    return rotated


@app.post("/auth/device/revoke")
async def revoke_device(
    payload: DeviceRevokeRequest,
    state: AppState = Depends(require_master_key),
) -> Dict[str, Any]:
    """Revoke one device's token. Master key only — a token may not revoke others."""
    if state.device_tokens is None:
        raise HTTPException(status_code=503, detail="Device token store not initialized")
    revoked = await state.device_tokens.revoke(payload.token_id)
    return {"token_id": payload.token_id, "revoked": bool(revoked)}


@app.get("/auth/devices")
async def list_devices(state: AppState = Depends(require_master_key)) -> Dict[str, Any]:
    """List issued device tokens (never includes secrets or hashes)."""
    if state.device_tokens is None:
        raise HTTPException(status_code=503, detail="Device token store not initialized")
    devices = await state.device_tokens.list_devices()
    return {"devices": devices, "count": len(devices)}


@app.get("/auth/device/whoami")
async def device_whoami(
    request: Request,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    state: AppState = Depends(require_auth),
) -> Dict[str, Any]:
    """What credential am I using? Lets a client verify its token before relying on it."""
    presented = _presented_credential(x_api_key, authorization)
    if _master_key_ok(presented, state.api_key):
        return {"credential": "master_key", "scopes": list(KNOWN_SCOPES)}
    return {
        "credential": "device_token",
        "device_id": getattr(request.state, "device_id", None),
        "token_id": getattr(request.state, "token_id", None),
        "scopes": getattr(request.state, "scopes", []),
    }


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


def _refuse_operator_only(task_type: str) -> None:
    """Approving/applying changes is a human act: never reachable via /execute.

    This used to be possible with any ``execute``-scoped credential, which let an
    agent submit a change request and approve it itself in three calls.
    """
    if task_type in OPERATOR_ONLY_TASK_TYPES:
        raise HTTPException(
            status_code=403,
            detail="Operator-only task: use /cr/review or /cr/apply with a HITL-scoped credential",
        )


@app.post("/execute", response_model=ExecuteResponse)
async def execute_task(
    request: ExecuteRequest,
    state: AppState = Depends(require_auth),
):
    """Execute an agent task via the orchestrator (authenticated)."""
    logger.info("Task received", task_type=request.task_type, priority=request.priority)
    _refuse_operator_only(request.task_type)

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


@app.post("/execute/stream")
async def execute_task_stream(
    request: ExecuteRequest,
    state: AppState = Depends(require_auth),
) -> StreamingResponse:
    """Execute an agent task, streaming progress as Server-Sent Events.

    ``POST /execute`` blocks for the whole run (10-60 s is normal). A mobile
    client on a flaky connection sees nothing during that time — no progress,
    no proof the server is alive, and proxies may time out. This endpoint
    streams instead:

        event: accepted   -> {"task_id": ...}            (immediately)
        event: heartbeat  -> {"elapsed_seconds": N}      (every ~15 s)
        event: progress   -> interim state               (not yet available)
        event: result     -> final payload               (terminal)
        event: error      -> {"detail": ...}             (terminal)
        event: done       -> {"status": ...}             (always last)

    Honest limitation: the orchestrator exposes only ``ainvoke`` (one
    ``await`` for the entire graph), so there is no interim state to emit yet.
    Heartbeats are therefore **liveness only** — they prove the server is
    still working, they do not report agent progress. No synthetic progress
    events are invented. Once the graph is switched to ``astream_events``,
    ``event: progress`` will carry real per-node updates without any change
    to this wire format.

    Requires the client to send ``POST``; browsers' ``EventSource`` is GET-only,
    so JS callers use ``fetch`` + a stream reader. Native clients (Flutter,
    Swift, Kotlin) read the chunked body directly.
    """
    _refuse_operator_only(request.task_type)
    # Sentinel runs *before* the stream opens so that a blocked or unauthorised
    # task still returns a normal JSON error, not a 200 SSE stream.
    try:
        validation = await state.sentinel.validate_task(request.model_dump())
    except Exception as exc:  # noqa: BLE001
        logger.error("Sentinel validation failed", error=str(exc))
        raise HTTPException(status_code=500, detail="Internal validation error")
    if not validation.allowed:
        logger.warning("Task blocked by Sentinel", reason=validation.reason)
        raise HTTPException(status_code=403, detail=f"Task blocked: {validation.reason}")

    heartbeat = max(1, int(os.getenv("EVAS_SSE_HEARTBEAT", "15")))

    async def _event_stream():
        started = time.time()
        task: Optional[asyncio.Task] = None
        try:
            yield _sse("accepted", {
                "task_type": request.task_type,
                "heartbeat_seconds": heartbeat,
                "note": "heartbeats are liveness only; interim agent state is not yet streamed",
            })

            task = asyncio.create_task(state.orchestrator.execute(
                task_type=request.task_type,
                payload=request.payload,
                session_id=request.session_id,
            ))

            while not task.done():
                try:
                    # shield(): a heartbeat timeout must never cancel the run.
                    await asyncio.wait_for(asyncio.shield(task), timeout=heartbeat)
                except asyncio.TimeoutError:
                    yield _sse("heartbeat", {"elapsed_seconds": round(time.time() - started, 1)})

            try:
                result = task.result()
            except Exception as exc:  # noqa: BLE001
                logger.error("Streamed task execution failed", error=str(exc), exc_info=True)
                yield _sse("error", {"detail": "Internal execution error", "status": "error"})
                yield _sse("done", {"status": "error", "elapsed_seconds": round(time.time() - started, 1)})
                return

            yield _sse("result", {
                "task_id": result.get("task_id"),
                "status": result.get("status"),
                "result": _json_safe(result.get("result")),
            })
            yield _sse("done", {
                "status": result.get("status"),
                "elapsed_seconds": round(time.time() - started, 1),
            })

        except asyncio.CancelledError:
            # Client hung up. We deliberately do NOT cancel the orchestrator
            # task: killing a LangGraph run mid-graph can leave persisted
            # checkpoint state half-written. It finishes detached and its
            # result is simply discarded.
            logger.info("execute_stream_client_disconnected", task_type=request.task_type)
            raise
        except GeneratorExit:
            logger.info("execute_stream_closed", task_type=request.task_type)
            raise
        except Exception as exc:  # noqa: BLE001
            logger.error("execute_stream_failed", error=str(exc), exc_info=True)
            yield _sse("error", {"detail": "Internal execution error"})
            yield _sse("done", {"status": "error"})

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            # nginx buffers proxied responses by default, which would defeat
            # the entire point of streaming.
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/webhook/error")
async def error_webhook(request: Request, state: AppState = Depends(require_auth)):
    """Dead-letter error recording from n8n / subagents (Floor 1).

    Authenticated: the n8n templates already send ``X-API-Key``. It used to be
    open to anyone who could reach the port.
    """
    body = await request.json()
    result = await state.orchestrator.execute("record_error", body)
    return {"ok": True, "result": result}


async def _verify_generic_webhook(
    state: AppState, raw_bytes: bytes, source: str,
    x_hub_signature_256: Optional[str], x_webhook_signature: Optional[str],
) -> None:
    """HMAC-SHA256 check for non-Telegram webhooks. Fails closed."""
    if not state.webhook_secret:
        logger.error("Webhook rejected: no webhook secret configured", source=source)
        raise HTTPException(status_code=503, detail="Webhook secret not configured")
    sig = x_hub_signature_256 or x_webhook_signature or ""
    if sig.startswith("sha256="):
        sig = sig[7:]
    if not sig:
        logger.warning("Webhook missing signature header", source=source)
        raise HTTPException(status_code=401, detail="Missing webhook signature")
    if not await state.sentinel.verify_webhook_signature(raw_bytes, sig, state.webhook_secret):
        logger.warning("Webhook HMAC verification failed", source=source)
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


@app.post("/webhook/telegram/{agent_id}")
async def telegram_webhook(
    agent_id: str,
    request: Request,
    x_telegram_secret: Optional[str] = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
    state: AppState = Depends(require_ready),
):
    """One of the 18 director bots. Per-bot secret, owner-only, honest replies."""
    if not is_director(agent_id):
        raise HTTPException(status_code=404, detail="Unknown director")
    if not state.webhook_secret:
        logger.error("Telegram webhook rejected: no webhook secret configured", agent_id=agent_id)
        raise HTTPException(status_code=503, detail="Webhook secret not configured")
    if not verify_webhook_secret(state.webhook_secret, agent_id, x_telegram_secret):
        logger.warning("Telegram webhook secret mismatch", agent_id=agent_id)
        raise HTTPException(status_code=401, detail="Invalid Telegram secret token")

    try:
        update = await request.json()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON") from None
    message = extract_message(update)
    gateway = state.telegram_gateway
    if message is None or gateway is None:
        return {"ok": True}  # nothing actionable (e.g. a sticker); Telegram must get 200
    if message["chat_type"] != "private" or not await gateway.is_owner(message["user_id"]):
        # Not the owner: no reply, nothing logged about the content.
        logger.warning("telegram_non_owner_dropped", agent_id=agent_id)
        return {"ok": True}

    if message["kind"] == "voice":
        # Download + speech-to-text + reply can outlast Telegram's webhook wait;
        # answer 200 now so Telegram does not redeliver the note.
        task = asyncio.create_task(_telegram_voice(state, agent_id, message))
        _VOICE_TASKS.add(task)
        task.add_done_callback(_VOICE_TASKS.discard)
        return {"ok": True}
    text = await _telegram_reply(state, agent_id, message, message["text"])
    await gateway.send(agent_id, message["chat_id"], text)
    if wants_voice(message["text"]):
        # Synthesis can outlast Telegram's webhook wait, like a voice note.
        task = asyncio.create_task(_voice_on_request(state, agent_id, message["chat_id"], message["text"], text))
        _VOICE_TASKS.add(task)
        task.add_done_callback(_VOICE_TASKS.discard)
    return {"ok": True}


#: Running voice-note tasks (a bare create_task result can be garbage-collected).
_VOICE_TASKS: set = set()


async def _telegram_reply(state: AppState, agent_id: str, message: Dict[str, Any], text: str) -> str:
    payload = {
        "agent_id": agent_id,
        "text": text,
        "chat_id": message["chat_id"],
        "user_id": message["user_id"],
        "message": {"chat": {"id": message["chat_id"]}, "text": text},
    }
    try:
        outcome = await state.orchestrator.handle_webhook(source=f"telegram_{agent_id}", payload=payload)
        return reply_text(agent_id, outcome)
    except Exception as exc:  # noqa: BLE001
        logger.error("Telegram handling failed", agent_id=agent_id, error_type=type(exc).__name__)
        return f"⛔ [{agent_id}] внутрішня помилка обробки."


async def _telegram_voice(state: AppState, agent_id: str, message: Dict[str, Any]) -> None:
    """Owner's voice note: transcribe, answer as usual, then voice the answer."""
    gateway, chat_id = state.telegram_gateway, message["chat_id"]
    try:
        if message["duration"] > VOICE_MAX_SECONDS or message["file_size"] > VOICE_MAX_BYTES:
            await gateway.send(agent_id, chat_id, f"⚠️ Голосове задовге: до {VOICE_MAX_SECONDS // 60} хв.")
            return
        keys = await _voice_keys(state)
        audio = await gateway.download_file(agent_id, message["file_id"], VOICE_MAX_BYTES)
        if audio is None:
            await gateway.send(agent_id, chat_id, "⚠️ Не вдалося отримати голосове з Telegram.")
            return
        heard, provider = await transcribe(audio, keys)
        if not heard:
            await gateway.send(agent_id, chat_id, "⚠️ Не вдалося розпізнати голосове. Спробуй ще раз або напиши текстом.")
            return
        logger.info("telegram_voice_transcribed", agent_id=agent_id, provider=provider)
        reply = await _telegram_reply(state, agent_id, message, heard)
        await gateway.send(agent_id, chat_id, f"🎙 «{heard[:300]}»\n\n{reply}")
        # Text by default (operator, 29.10): voice only when the note asks for it.
        if wants_voice(heard):
            await _voice_answer(state, agent_id, chat_id, heard, reply, keys)
    except Exception as exc:  # noqa: BLE001 - a background task must not die silently
        logger.error("telegram_voice_failed", agent_id=agent_id, error_type=type(exc).__name__)
        await gateway.send(agent_id, chat_id, f"⛔ [{agent_id}] не вдалося обробити голосове.")


async def _voice_on_request(state: AppState, agent_id: str, chat_id: str, asked: str, reply: str) -> None:
    """A typed message asked for a spoken answer: voice the reply already sent as text."""
    try:
        await _voice_answer(state, agent_id, chat_id, asked, reply, await _voice_keys(state))
    except Exception as exc:  # noqa: BLE001 - the text answer is already delivered
        logger.warning("telegram_voice_on_request_failed", agent_id=agent_id, error_type=type(exc).__name__)


async def _voice_keys(state: AppState) -> Dict[str, Any]:
    try:
        return await state.vault_client.get_secret(secret_path("api-keys")) or {}
    except Exception as exc:  # noqa: BLE001 - STT then uses local Whisper, TTS is skipped
        logger.warning("voice_keys_unavailable", error_type=type(exc).__name__)
        return {}


async def _voice_answer(
    state: AppState, agent_id: str, chat_id: str, heard: str, reply: str, keys: Dict[str, Any]
) -> None:
    """Voice the reply when Respeecher is configured; otherwise the text stands alone.

    Military talk, account numbers and access codes never reach Respeecher: they
    are replaced by a spoken pointer to the text message already sent.
    """
    key = keys.get("respeecher_api_key")
    if not key or reply.startswith(("⛔", "⚠️", "⏸")):
        return
    if state.respeecher is None:
        state.respeecher = RespeecherTTS(key)
    spoken, why = voice_text(heard, reply)
    if why != "plain":
        logger.info("telegram_voice_sensitive", agent_id=agent_id, reason=why)
    wav = await state.respeecher.synthesize(agent_id, spoken_text(spoken))
    ogg = await wav_to_ogg_opus(wav) if wav else None
    if ogg:
        await state.telegram_gateway.send_voice(agent_id, chat_id, ogg)


@app.post("/webhook/{source}")
async def webhook_handler(
    source: str,
    request: Request,
    x_hub_signature_256: Optional[str] = Header(default=None, alias="X-Hub-Signature-256"),
    x_webhook_signature: Optional[str] = Header(default=None, alias="X-Webhook-Signature"),
    state: AppState = Depends(require_ready),
):
    """Generic signed webhook (n8n, CI, partners). HMAC-SHA256 over the raw body."""
    raw_bytes = await request.body()
    await _verify_generic_webhook(state, raw_bytes, source, x_hub_signature_256, x_webhook_signature)
    try:
        body = json.loads(raw_bytes or b"{}")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON") from None
    logger.info("Webhook received", source=source)
    try:
        result = await state.orchestrator.handle_webhook(source=source, payload=body)
        return {"ok": True, "result": result}
    except Exception as exc:  # noqa: BLE001
        logger.error("Webhook handling failed", source=source, error_type=type(exc).__name__)
        return Response(content='{"ok": false}', status_code=200, media_type="application/json")


# ─── 10-Floor Specialized Endpoints ──────────────────────────────────────────

@app.get("/floors")
async def get_floors_registry(state: AppState = Depends(require_read)):
    """Return the 10-floor registry to the operator's read-authorized clients."""
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
    """Trigger 21:00 evening reflection (Floor 1 / Floor 8 / Floor 9).

    Збираємо лише вже наявні звіти (файли KODEX за 24 год); жодного запуску агентів.
    Без KODEX_DATA_DIR звіт файлів чесно позначається unavailable.
    """
    from datetime import datetime

    from src.agents.kodex import evening_section

    evening = {"kodex": evening_section(os.getenv("KODEX_DATA_DIR"), datetime.now())}
    result = await state.orchestrator.proactive_evening_reflection(evening)
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


# ─── HITL surface (PC / mobile approval inbox) ───────────────────────────────
#
# The operator used to approve protected changes only from Telegram. These
# endpoints make the client app a first-class approval surface: it can list the
# pending inbox, open a change for review, approve/reject, and — via SSE — be
# pushed the moment an agent proposes something that needs a human.


def _cr_summary(cr: Dict[str, Any]) -> Dict[str, Any]:
    """Compact view for list/inbox endpoints (no full proposed content)."""
    return {
        "id": cr["id"],
        "title": cr.get("title"),
        "rationale": cr.get("rationale"),
        "risk": cr.get("risk"),
        "status": cr.get("status"),
        "author": cr.get("author"),
        "created_at": cr.get("created_at"),
        "paths": [ch.get("path") for ch in cr.get("changes", [])],
        "tests_passed": cr.get("tests_passed", []),
    }


def _cr_detail(cr: Dict[str, Any]) -> Dict[str, Any]:
    """Full view for the detail endpoint (includes proposed content)."""
    detail = dict(cr)
    # created_at is a unix float — give the client an ISO string too, but never
    # invent a timezone or a status it does not have.
    raw = cr.get("created_at")
    if isinstance(raw, (int, float)):
        try:
            from datetime import datetime, timezone

            detail["created_at_iso"] = datetime.fromtimestamp(raw, tz=timezone.utc).isoformat()
        except (OverflowError, OSError, ValueError):
            detail["created_at_iso"] = None
    return detail


@app.get("/cr/pending")
async def cr_pending(state: AppState = Depends(require_hitl)) -> Dict[str, Any]:
    """The operator's approval inbox: every change request awaiting a decision."""
    if state.change_request_store is None:
        raise HTTPException(status_code=503, detail="Change-request store not initialized")
    pending = sorted(
        state.change_request_store.list("pending"),
        key=lambda c: c.get("created_at", 0),
        reverse=True,
    )
    return {"pending": [_cr_summary(c) for c in pending], "count": len(pending)}


@app.get("/cr/list")
async def cr_list(status: Optional[str] = None, state: AppState = Depends(require_hitl)) -> Dict[str, Any]:
    """All change requests, optionally filtered by status (pending/approved/rejected/applied)."""
    if state.change_request_store is None:
        raise HTTPException(status_code=503, detail="Change-request store not initialized")
    items = state.change_request_store.list(status)
    items = sorted(items, key=lambda c: c.get("created_at", 0), reverse=True)
    return {"items": [_cr_summary(c) for c in items], "count": len(items)}


# NOTE: the static HITL routes (/cr/pending, /cr/list, /cr/stream) MUST be
# declared before the /cr/{cr_id} catch-all. Starlette matches the first
# registered route whose pattern fits, so a later /cr/stream would otherwise be
# swallowed by /cr/{cr_id}.
@app.get("/cr/stream")
async def cr_stream(state: AppState = Depends(require_hitl)) -> StreamingResponse:
    """Server-Sent Events: push a frame whenever a change request needs a human.

    This is the in-process half of HITL push. A real OS-level notification
    (FCM/APNs) is a separate client-side integration that registers a device
    push token with a gateway; this endpoint covers the case where the app is
    open and connected to this backend instance. On each event the client
    re-fetches ``GET /cr/pending`` for the authoritative list.
    """
    if state.change_request_notifier is None:
        raise HTTPException(status_code=503, detail="HITL notifier not initialized")
    return StreamingResponse(
        _cr_event_stream(state.change_request_notifier),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _cr_event_stream(notifier) -> None:
    """Yield SSE frames for pending change requests.

    Extracted from the endpoint so it can be driven deterministically in tests
    (Starlette's TestClient streaming blocks unpredictably). Emits ``connected``
    on subscribe, then ``pending_cr`` for each notification, and ``heartbeat``
    every 30s to prove liveness. Never emits a synthetic progress frame.
    """
    try:
        queue = await notifier.subscribe()
    except RuntimeError:
        # No event loop — cannot stream. The client should use polling.
        yield _sse("error", {"detail": "no event loop for streaming"})
        return
    try:
        yield _sse("connected", {"note": "subscribed to change-request events; re-fetch /cr/pending on each event"})
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30)
                yield _sse("pending_cr", event)
            except asyncio.TimeoutError:
                yield _sse("heartbeat", {"note": "HITL channel alive"})
    except asyncio.CancelledError:
        notifier.unsubscribe(queue)
        raise
    except GeneratorExit:
        notifier.unsubscribe(queue)
        raise


@app.get("/cr/{cr_id}")
async def cr_detail(cr_id: str, state: AppState = Depends(require_hitl)) -> Dict[str, Any]:
    """Full detail of one change request, including proposed content to review."""
    if state.change_request_store is None:
        raise HTTPException(status_code=503, detail="Change-request store not initialized")
    try:
        cr = state.change_request_store.get(cr_id)
    except ChangeRequestError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _cr_detail(cr)


@app.post("/cr/review")
async def review_cr(request: Request, state: AppState = Depends(require_hitl)):
    """Review Change Request (approve/reject) (Floor 10). HITL-scoped.

    The reviewer identity is fixed by the orchestrator; a ``reviewer`` field in
    the body is ignored, so the caller cannot pick who "approved".
    """
    body = await request.json()
    if not isinstance(body, dict):
        raise HTTPException(status_code=422, detail="JSON object required")
    body.pop("reviewer", None)
    result = await state.orchestrator.execute("review_change_request", body, operator_verified=True)
    return result


@app.post("/cr/apply")
async def apply_cr(request: Request, state: AppState = Depends(require_hitl)):
    """Apply approved Change Request to vault (Floor 10). HITL-scoped."""
    body = await request.json()
    if not isinstance(body, dict):
        raise HTTPException(status_code=422, detail="JSON object required")
    result = await state.orchestrator.execute("apply_change_request", body, operator_verified=True)
    return result


# ─── HITL queue (held outbound actions) ──────────────────────────────────────

class HitlDecision(BaseModel):
    item_id: str = Field(max_length=40)
    decision: str = Field(pattern="^(approve|reject)$")
    comment: str = Field(default="", max_length=500)


def _hitl_queue(state: AppState):
    queue = getattr(state.orchestrator, "_hitl_queue", None)
    if queue is None:
        raise HTTPException(status_code=503, detail="HITL queue not initialized")
    return queue


@app.get("/hitl/pending")
async def hitl_pending(state: AppState = Depends(require_hitl)) -> Dict[str, Any]:
    items = _hitl_queue(state).pending()
    return {"pending": items, "count": len(items)}


@app.get("/hitl/{item_id}")
async def hitl_item(item_id: str, state: AppState = Depends(require_hitl)) -> Dict[str, Any]:
    try:
        return _hitl_queue(state).get(item_id)
    except HitlError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/hitl/decide")
async def hitl_decide(
    decision: HitlDecision, request: Request, state: AppState = Depends(require_hitl)
) -> Dict[str, Any]:
    """Approve or reject a held action. The actor comes from the credential."""
    actor = getattr(request.state, "actor", "operator")
    try:
        return _hitl_queue(state).decide(decision.item_id, decision.decision, actor, decision.comment)
    except HitlError as exc:
        code = 404 if "not_found" in str(exc) else 409
        raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post("/hitl/release/{item_id}")
async def hitl_release(item_id: str, state: AppState = Depends(require_hitl)) -> Dict[str, Any]:
    """Hand the held actions of an *approved* item to the caller — exactly once."""
    try:
        actions = _hitl_queue(state).release(item_id)
    except HitlError as exc:
        code = 404 if "not_found" in str(exc) else 409
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    return {"item_id": item_id, "released_actions": actions, "count": len(actions)}


# ─── Admin: lockdown, Telegram webhook registration ──────────────────────────

class LockdownRequest(BaseModel):
    reason: str = Field(default="", max_length=300)


@app.post("/admin/lockdown")
async def engage_lockdown(
    body: LockdownRequest, request: Request, state: AppState = Depends(require_hitl)
) -> Dict[str, Any]:
    """PANIC STOP: block every state-changing route until released on the server.

    There is intentionally no unlock endpoint — see ``tools/unlock_lockdown.py``.
    """
    record = Lockdown().engage(getattr(request.state, "actor", "operator"), body.reason)
    logger.warning("LOCKDOWN ENGAGED", actor=record["actor"], reason=record["reason"])
    return {"status": "locked_down", **record}


@app.get("/admin/lockdown")
async def lockdown_status(state: AppState = Depends(require_read)) -> Dict[str, Any]:
    info = Lockdown().info()
    return {"locked": info is not None, "info": info}


class TelegramRegisterRequest(BaseModel):
    base_url: str = Field(max_length=200, pattern=r"^https://[A-Za-z0-9.-]+(:\d+)?$")


@app.post("/admin/telegram/register")
async def register_telegram_webhooks(
    body: TelegramRegisterRequest, state: AppState = Depends(require_master_key)
) -> Dict[str, Any]:
    """Point all 18 bots at this gateway (master key only). Reports per-bot status."""
    if state.telegram_gateway is None or not state.webhook_secret:
        raise HTTPException(status_code=503, detail="Telegram gateway or webhook secret not configured")
    report = await state.telegram_gateway.register_webhooks(body.base_url, state.webhook_secret)
    return {"registered": sum(1 for r in report if r["status"] == "ok"), "report": report}




class IntegrationDispatchRequest(BaseModel):
    operation: str = Field(max_length=64)
    payload: dict = Field(default_factory=dict)


@app.post("/integrations/{agent_id}/execute")
async def execute_integration(agent_id: str, request: IntegrationDispatchRequest,
                              state: AppState = Depends(require_master_key)):
    """Operator entry point; worker grants remain independently enforced."""
    from src.agent_platform.integration_client import dispatch_integration
    return await dispatch_integration(agent_id, request.operation, request.payload, state.vault_client)


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
