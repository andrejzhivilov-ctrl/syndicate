"""Single source of truth for HashiCorp Vault secret paths.

Before this module existed the repository used two incompatible conventions:

* ``src/integrations/base.py`` (and the documented convention in
  ``INTEGRATIONS_AND_CAPABILITIES.md``) read
  ``secret/data/eva-syndicate/<SERVICE>`` — the default ``secret/`` KV v2 mount;
* ``deploy/runtime/agent_runner.py`` read ``eva/database/data/postgres``,
  ``eva/config/data/redis``, ``eva/config/data/auth`` and
  ``eva/api-keys/data/llm`` — four *additional* KV v2 mounts that
  ``deploy/scripts/vault_init.sh`` created but only ever populated for
  ``database`` and ``api-keys``.

Consequences in production:

* ``eva/config/data/redis`` and ``eva/config/data/auth`` were never written by
  ``vault_init.sh``, so ``agent_runner`` got a 404 on boot and the agent could
  not start at all;
* the ``eva-agent`` Vault policy granted ``secret/data/eva/*`` and the four
  ``eva/*`` mounts, **not** ``secret/data/eva-syndicate/*`` — so every
  connector's secret read was denied.

Everything now lives under one KV v2 mount (``secret/``) and one prefix
(``eva-syndicate``). Change :data:`PREFIX` here and every caller follows.
"""

from __future__ import annotations

#: KV v2 mount point. Vault exposes data at ``<mount>/data/<path>``.
MOUNT = "secret"

#: Logical prefix inside the mount.
PREFIX = "eva-syndicate"

#: Well-known service keys.
DATABASE = "database"      # Postgres: user, password
REDIS = "redis"            # Redis: password
AUTH = "auth"              # Agent API: api_key, webhook_secret
API_KEYS = "api-keys"      # LLM provider keys
AGENTS = "agents"          # Per-agent connector secrets (see integrations/base.py)


def secret_path(service: str) -> str:
    """Return the Vault HTTP path for ``service``'s KV v2 secret.

    >>> secret_path("database")
    'secret/data/eva-syndicate/database'
    """
    service = (service or "").strip().strip("/")
    if not service:
        raise ValueError("secret_path() requires a non-empty service name")
    return f"{MOUNT}/data/{PREFIX}/{service}"


def mount_path() -> str:
    """Return the KV v2 mount path used by :func:`secret_path`."""
    return MOUNT


def policy_paths() -> list[str]:
    """Glob patterns the ``eva-agent`` Vault policy must grant read access to."""
    return [
        f"{MOUNT}/data/{PREFIX}/*",
        f"{MOUNT}/metadata/{PREFIX}/*",
    ]
