"""Vault secret helper for voice providers."""

from __future__ import annotations

import os
import re
from typing import Any, Optional

from src.vault_paths import secret_path

#: Vault stores the literal string below for secrets nobody has filled in yet
#: (see ``deploy/scripts/vault_init.sh``). Treat it as "not configured".
_PLACEHOLDER = "PLACEHOLDER_UPDATE_ME"


def _env_var(service: str, key: str) -> str:
    """Build a sane environment-variable name from a Vault service name.

    ``api-keys`` + ``openai_api_key`` -> ``API_KEYS_OPENAI_API_KEY``.
    """
    svc = re.sub(r"[^A-Z0-9]+", "_", service.upper()).strip("_")
    return f"{svc}_{key.upper()}"


async def read_vault_secret(
    vault: Any, service: str, key: str, env_key: Optional[str] = None
) -> Optional[str]:
    """Read ``key`` for ``service`` from Vault, falling back to the environment.

    ``service`` is a logical name (e.g. ``"elevenlabs"``, ``"api-keys"``), not a
    raw Vault path: the HTTP path is built by :func:`src.vault_paths.secret_path`
    so the voice subsystem uses the same convention as everything else. The old
    code passed the bare name straight to ``VaultClient.get_secret()``, which
    requested ``/v1/<name>`` — a path that does not exist, so every provider
    silently fell through to the environment even when Vault held the key.
    """
    if vault is not None:
        try:
            data = await vault.get_secret(secret_path(service))
            if isinstance(data, dict) and data.get(key):
                val = str(data[key])
                if val != _PLACEHOLDER:
                    return val
        except Exception:  # noqa: BLE001
            # Missing secret / denied path: fall through to the environment.
            pass

    for candidate in (env_key, _env_var(service, key), key.upper()):
        if not candidate:
            continue
        value = os.environ.get(candidate)
        if value:
            return value
    return None
