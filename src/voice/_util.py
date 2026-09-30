"""Vault secret helper for voice providers."""

from __future__ import annotations

import os
from typing import Any, Optional


async def read_vault_secret(vault: Any, path: str, key: str) -> Optional[str]:
    """Read secret from VaultClient or fall back to environment variable."""
    if vault is not None:
        try:
            data = await vault.get_secret(path)
            if isinstance(data, dict) and data.get(key):
                val = str(data[key])
                if val != "PLACEHOLDER_UPDATE_ME":
                    return val
        except Exception:  # noqa: BLE001
            pass
    env_key = f"{path.upper()}_{key.upper()}"
    return os.environ.get(env_key)
