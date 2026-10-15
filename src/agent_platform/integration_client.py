"""Coordinator bridge: fixed worker origins and scoped API keys from Vault auth."""
from __future__ import annotations

import ipaddress
import json
import os
import re
from urllib.parse import urlsplit

import httpx

from src.integrations.service_transport import LIMIT, endpoint
from src.vault_paths import secret_path


def worker_endpoint(value: str) -> str:
    """TLS by default; explicitly approved private IPs/Docker aliases may use HTTP."""
    url = endpoint(value)
    parsed = urlsplit(url)
    if parsed.scheme == 'https':
        return url
    host = parsed.hostname
    allowed = json.loads(os.getenv('SYNDICATE_INTEGRATION_HTTP_HOSTS', '[]'))
    if not isinstance(allowed, list) or host not in allowed:
        raise ValueError('http_worker_not_approved')
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        # Private Docker aliases are single-label names; public DNS names require TLS.
        private = bool(re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_-]*', host))
    else:
        private = address.is_private and not (address.is_unspecified or address.is_multicast or address.is_reserved)
    if not private:
        raise ValueError('http_worker_must_be_private')
    return url


async def dispatch_integration(agent_id: str, operation: str, payload: dict, vault, *, transport=None) -> dict:
    try:
        # Deployment configuration, not request data, controls all destinations.
        endpoints = json.loads(os.getenv('SYNDICATE_INTEGRATION_URLS', '{}'))
        url = worker_endpoint(endpoints[agent_id])
        secrets = await vault.get_secret(secret_path('auth'))
        key = secrets['integration_worker_keys'][agent_id]
        if not isinstance(key, str) or len(key) < 32:
            raise ValueError('invalid_worker_key')
        async with httpx.AsyncClient(timeout=650, follow_redirects=False, trust_env=False,
                                     transport=transport) as client:
            async with client.stream('POST', url + '/execute', headers={'X-API-Key': key},
                                     json={'operation': operation, 'payload': payload}) as response:
                response.raise_for_status()
                raw = bytearray()
                async for chunk in response.aiter_bytes():
                    raw.extend(chunk)
                    if len(raw) > LIMIT:
                        raise ValueError('worker_response_too_large')
        result = json.loads(raw)
        if result.get('agent') != agent_id or 'status' not in result:
            raise ValueError('worker_identity_mismatch')
        return result
    except Exception:
        return {'status': 'unavailable', 'agent': agent_id, 'value': None,
                'warning': 'integration_worker_unavailable'}
