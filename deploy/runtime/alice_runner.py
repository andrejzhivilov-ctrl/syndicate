"""Isolated API-first worker for Alice; profile and Vault remain fail-closed."""
from __future__ import annotations

import hmac
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from src.agents.alice import AliceAgent, load_alice_manifest
from src.vault_client import VaultClient, is_placeholder_secret
from src.vault_paths import agent_secret_path


class AliceRequest(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


def _enabled(name: str) -> bool:
    return os.getenv(name, "false").strip().lower() in {"1", "true", "yes", "on"}


def _profile_provider_ready(profile: dict[str, Any]) -> bool:
    live_modes = profile.get("live_modes") if isinstance(profile.get("live_modes"), dict) else {}
    provider = profile.get("provider") if isinstance(profile.get("provider"), dict) else {}
    gates = profile.get("activation_gates") if isinstance(profile.get("activation_gates"), dict) else {}
    capabilities = profile.get("capabilities") if isinstance(profile.get("capabilities"), list) else []
    services = profile.get("services_enabled") if isinstance(profile.get("services_enabled"), list) else []
    try:
        daily_requests = int(os.getenv("ALICE_MAX_REQUESTS_PER_DAY", "0"))
        daily_tokens = int(os.getenv("ALICE_MAX_TOKENS_PER_DAY", "0"))
    except ValueError:
        return False
    return (
        profile.get("activation") == "active"
        and profile.get("model_status") == "operator_selected"
        and live_modes.get("api") is True
        and provider.get("primary") == "gemini_developer_api"
        and isinstance(provider.get("model"), str)
        and provider.get("model") != "not_selected"
        and "gemini_developer_api" in services
        and "alice.model.invoke" in capabilities
        and gates.get("provider_billing_limit_reviewed") is True
        and gates.get("filtered_provider_egress_verified") is True
        and _enabled("ALICE_EGRESS_ALLOWLIST_VERIFIED")
        and daily_requests > 0
        and daily_tokens > 0
    )


async def boot_alice(vault: Any) -> tuple[AliceAgent, str]:
    """Authenticate one Alice AppRole and retrieve only secrets in her Vault scope."""
    await vault.authenticate()
    auth = await vault.get_secret(agent_secret_path("alice", "auth"))
    worker_key = auth.get("api_key")
    if not isinstance(worker_key, str) or len(worker_key) < 32 or is_placeholder_secret(worker_key):
        raise RuntimeError("alice_worker_auth_missing")

    profile = load_alice_manifest()
    providers = {part.strip() for part in os.getenv("ALICE_PROVIDERS", "").split(",") if part.strip()}
    api_key = None
    model = None
    api_enabled = False
    if providers:
        if providers != {"gemini"}:
            raise RuntimeError("alice_provider_not_allowed")
        if not _enabled("ALICE_API_ENABLED") or not _profile_provider_ready(profile):
            raise RuntimeError("alice_activation_gates_incomplete")
        provider_secret = await vault.get_secret(agent_secret_path("alice", "gemini"))
        api_key = provider_secret.get("api_key")
        model = provider_secret.get("model")
        if (
            not isinstance(api_key, str)
            or len(api_key) < 16
            or is_placeholder_secret(api_key)
            or not isinstance(model, str)
            or is_placeholder_secret(model)
            or model != profile.get("provider", {}).get("model")
        ):
            raise RuntimeError("alice_provider_secret_invalid")
        api_enabled = True

    agent = AliceAgent(
        api_key=api_key,
        model=model,
        profile=profile,
        api_enabled=api_enabled,
        egress_allowlist_verified=_enabled("ALICE_EGRESS_ALLOWLIST_VERIFIED"),
    )
    return agent, worker_key


def allowed_actions(agent: AliceAgent) -> set[str]:
    requested = {part.strip() for part in os.getenv("ALICE_ACTIONS", "capabilities").split(",") if part.strip()}
    if not requested <= agent.ACTIONS.keys():
        raise RuntimeError("alice_unknown_action_grant")
    if not requested <= agent.allowed_actions():
        raise RuntimeError("alice_action_not_granted")
    return requested


def create_app(
    agent: AliceAgent | None = None,
    *,
    api_key: str | None = None,
    allowed: set[str] | None = None,
) -> FastAPI:
    """Test injection is supported; production always creates the AppRole client."""
    state: dict[str, Any] = {"agent": agent, "key": api_key, "vault": None, "actions": allowed}

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if state["agent"] is None:
            vault = VaultClient(
                os.getenv("VAULT_ADDR", ""),
                os.getenv("VAULT_ROLE_ID", ""),
                os.getenv("VAULT_SECRET_ID", ""),
            )
            state["vault"] = vault
            try:
                state["agent"], state["key"] = await boot_alice(vault)
                state["actions"] = allowed_actions(state["agent"])
                vault.ensure_token_renewal()
                yield
            finally:
                state["agent"] = None
                state["key"] = None
                await vault.aclose()
        else:
            yield

    app = FastAPI(title="SYNDICATE Alice API Worker", lifespan=lifespan)

    async def authorized(x_api_key: str | None = Header(default=None)) -> AliceAgent:
        expected = state["key"]
        if not expected or not x_api_key or not hmac.compare_digest(x_api_key.encode(), expected.encode()):
            raise HTTPException(status_code=401, detail="unauthorized")
        if state["agent"] is None:
            raise HTTPException(status_code=503, detail="alice_unavailable")
        return state["agent"]

    @app.get("/health")
    async def health() -> dict[str, str]:
        ready = state["agent"] is not None and bool(state["key"])
        if not ready:
            raise HTTPException(status_code=503, detail="not_ready")
        return {"status": "ok", "agent": "alice", "mode": AliceAgent.HEALTH_MODE}

    @app.post("/execute")
    async def execute(request: AliceRequest, alice: AliceAgent = Depends(authorized)) -> dict[str, Any]:
        action = request.payload.get("action", "capabilities")
        if state["actions"] is not None and (not isinstance(action, str) or action not in state["actions"]):
            raise HTTPException(status_code=403, detail="action_not_granted")
        return await alice.execute(request.payload)

    return app


app = create_app()
