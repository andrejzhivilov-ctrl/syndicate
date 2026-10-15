"""One authenticated integration worker per agent, bootstrapped exclusively via Vault."""
from __future__ import annotations

import hmac
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from src.integrations.service_hub import ServiceHub
from src.vault_client import VaultClient, is_placeholder_secret
from src.vault_paths import agent_secret_path


class IntegrationRequest(BaseModel):
    operation: str = Field(max_length=64)
    payload: dict = Field(default_factory=dict)


def create_app(hub=None, *, api_key: str | None = None):
    state = {'hub': hub, 'key': api_key}

    @asynccontextmanager
    async def lifespan(app):
        if hub is not None:
            yield
            return
        vault = VaultClient(os.environ['VAULT_ADDR'], os.environ['VAULT_ROLE_ID'], os.environ['VAULT_SECRET_ID'])
        try:
            await vault.authenticate()
            agent = os.environ['SYNDICATE_INTEGRATION_AGENT']
            config = await vault.get_secret(agent_secret_path(agent, 'integrations'))
            key = config.pop('worker_api_key', None)
            if not isinstance(key, str) or len(key) < 32 or is_placeholder_secret(key):
                raise RuntimeError('integration_auth_missing')
            state.update(hub=ServiceHub(agent, config), key=key)
            vault.ensure_token_renewal()
            yield
        finally:
            state.update(hub=None, key=None)
            await vault.aclose()

    app = FastAPI(title='SYNDICATE Integration Worker', lifespan=lifespan)

    async def authorized(x_api_key: str | None = Header(default=None)):
        if not state['key'] or not x_api_key or not hmac.compare_digest(x_api_key.encode(), state['key'].encode()):
            raise HTTPException(status_code=401, detail='unauthorized')
        if state['hub'] is None:
            raise HTTPException(status_code=503, detail='not_ready')
        return state['hub']

    @app.get('/health')
    async def health():
        if state['hub'] is None:
            raise HTTPException(status_code=503, detail='not_ready')
        return {'status': 'ok', 'agent': state['hub'].agent_id}

    @app.post('/execute')
    async def execute(request: IntegrationRequest, worker=Depends(authorized)):
        return await worker.execute(request.operation, request.payload)

    return app


app = create_app()
