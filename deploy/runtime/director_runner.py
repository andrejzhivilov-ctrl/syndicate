"""Isolated local director worker API; Hermes can call it as a gated tool.

Vault authentication is mandatory. No request can select another director,
turn on providers or grant permission to publish, charge or place bets.
"""
from __future__ import annotations

import hmac
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from src.agents.oscar import OscarAgent
from src.agents.tyler import TylerAgent
from src.agents.jack import JackAgent
from src.agents.antigravity_worker import AntigravityDirectorAgent
from src.agents.director_providers import build_provider
from src.vault_client import VaultClient, is_placeholder_secret
from src.vault_paths import agent_secret_path

AGENTS = {"oscar": OscarAgent, "tyler": TylerAgent, "jack": JackAgent, "antigravity": AntigravityDirectorAgent}


class DirectorRequest(BaseModel):
    payload: dict = Field(default_factory=dict)


def create_app(agent=None, *, api_key: str | None = None, allowed_actions: set[str] | None = None) -> FastAPI:
    """Injected agent/key is a local test seam; production always boots via Vault."""
    state = {"agent": agent, "key": api_key, "vault": None, "actions": allowed_actions}

    @asynccontextmanager
    async def lifespan(app):
        if state["agent"] is None:
            vault = VaultClient(os.environ["VAULT_ADDR"], os.environ["VAULT_ROLE_ID"], os.environ["VAULT_SECRET_ID"])
            state["vault"] = vault
            try:
                state["agent"], state["key"] = await boot_director(vault)
                state["actions"] = allowed_local_actions(state["agent"])
                vault.ensure_token_renewal()
                yield
            finally:
                state["agent"] = None
                state["key"] = None
                await vault.aclose()
        else:
            yield

    app = FastAPI(title="SYNDICATE Agent Worker", lifespan=lifespan)

    async def authorized(x_api_key: str | None = Header(default=None)):
        expected = state["key"]
        if not expected or not x_api_key or not hmac.compare_digest(x_api_key.encode(), expected.encode()):
            raise HTTPException(status_code=401, detail="unauthorized")
        if state["agent"] is None:
            raise HTTPException(status_code=503, detail="director_unavailable")
        return state["agent"]

    @app.get("/health")
    async def health():
        ready = state["agent"] is not None and bool(state["key"])
        if not ready:
            raise HTTPException(status_code=503, detail="not_ready")
        return {
            "status": "ok",
            "agent": state["agent"].AGENT_ID,
            "mode": getattr(state["agent"], "HEALTH_MODE", "local_tools_no_external_execution"),
        }

    @app.post("/execute")
    async def execute(request: DirectorRequest, director=Depends(authorized)):
        action = request.payload.get("action", "capabilities")
        if state["actions"] is not None and (not isinstance(action, str) or action not in state["actions"]):
            raise HTTPException(status_code=403, detail="action_not_granted")
        return await director.execute(request.payload)

    return app


def allowed_local_actions(agent) -> set[str]:
    requested = {a.strip() for a in os.getenv("SYNDICATE_DIRECTOR_ACTIONS", "capabilities").split(",") if a.strip()}
    if not requested <= agent.ACTIONS.keys():
        raise RuntimeError("unknown_action_grant")
    return requested


async def boot_director(vault):
    agent_id = os.environ["SYNDICATE_DIRECTOR_ID"]
    if agent_id not in AGENTS:
        raise RuntimeError("unknown_director")
    await vault.authenticate()
    secrets = await vault.get_secret(agent_secret_path(agent_id, "auth"))
    key = secrets.get("api_key")
    if not isinstance(key, str) or len(key) < 32 or is_placeholder_secret(key):
        raise RuntimeError("director_auth_key_missing")
    kwargs = await provider_kwargs(vault, agent_id)
    return AGENTS[agent_id](**kwargs), key


async def provider_kwargs(vault, agent_id: str) -> dict:
    # Startup configuration is operator-owned; the request body cannot enable it.
    enabled = {p.strip() for p in os.getenv("SYNDICATE_DIRECTOR_PROVIDERS", "").split(",") if p.strip()}
    if not enabled:
        return {}
    if agent_id == "oscar":
        allowed = {"grok", "gemini", "haiku", "youtube"}
        if not enabled <= allowed:
            raise RuntimeError("provider_not_allowed")
        providers = {p: await build_provider(vault, agent_id, p) for p in sorted(enabled - {"youtube"})}
        result = {"providers": providers}
        if "youtube" in enabled:
            result["comments_client"] = await build_provider(vault, agent_id, "youtube")
        return result
    if agent_id == "jack" and enabled == {"odds"}:
        return {"scout": await build_provider(vault, agent_id, "odds")}
    raise RuntimeError("provider_not_allowed")


app = create_app()
