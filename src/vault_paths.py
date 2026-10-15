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

from typing import Dict, List, Tuple

#: KV v2 mount point. Vault exposes data at ``<mount>/data/<path>``.
MOUNT = "secret"

#: Logical prefix inside the mount.
PREFIX = "eva-syndicate"

#: Well-known service keys.
DATABASE = "database"      # Postgres: user, password
REDIS = "redis"            # Redis: password
AUTH = "auth"              # Agent API: api_key, webhook_secret
API_KEYS = "api-keys"      # LLM provider keys
AGENTS = "agents"          # Per-agent secrets: agents/<agent_id>/<name>

#: Secrets every process needs just to boot (runtime + any future per-agent
#: container). ``auth`` is deliberately **not** here: that is the server's own
#: API key, and an agent container has no business reading it.
INFRA_SERVICES: Tuple[str, ...] = (DATABASE, REDIS, API_KEYS)

#: Secrets read by connector plugins (``src/integrations/*``).
CONNECTOR_SERVICES: Tuple[str, ...] = ("google_workspace", "mcp", "telegram", "youtube")

#: Secrets read by voice providers (``src/voice/*``).
VOICE_SERVICES: Tuple[str, ...] = ("elevenlabs", "groq", "openai", "xai")

#: Canonical agent ids (``src/floors.py`` holds the floor mapping).
AGENTS_IDS: Tuple[str, ...] = ("eva", "marshal", "architect", "fin", "doc", "kira", "sam", "oscar", "tyler", "jack")

#: Which *extra* services each agent may read, on top of ``INFRA_SERVICES`` and
#: its own ``agents/<id>/*`` subtree. Default deny: an agent without an entry
#: here gets infrastructure and its own subtree, nothing else. This is the map
#: that makes one compromised agent unable to read another's provider keys.
AGENT_SERVICES: Dict[str, Tuple[str, ...]] = {
    "eva": CONNECTOR_SERVICES + VOICE_SERVICES,
    "marshal": ("mcp", "telegram"),
    "architect": ("mcp",),
    "fin": ("google_workspace",),
    "doc": (),
    "kira": (),
    "sam": (),
}


def secret_path(service: str) -> str:
    """Return the Vault HTTP path for ``service``'s KV v2 secret.

    >>> secret_path("database")
    'secret/data/eva-syndicate/database'
    """
    service = (service or "").strip().strip("/")
    if not service:
        raise ValueError("secret_path() requires a non-empty service name")
    return f"{MOUNT}/data/{PREFIX}/{service}"


def agent_secret_path(agent_id: str, name: str = "") -> str:
    """Return the path of one agent's own secret, e.g. Sam's broker keys.

    >>> agent_secret_path("sam", "broker")
    'secret/data/eva-syndicate/agents/sam/broker'
    """
    agent_id = (agent_id or "").strip().strip("/")
    if not agent_id:
        raise ValueError("agent_secret_path() requires a non-empty agent id")
    parts = [MOUNT, "data", PREFIX, AGENTS, agent_id]
    if name:
        parts.append(name.strip().strip("/"))
    return "/".join(parts)


def metadata_path(service: str) -> str:
    """Return the KV v2 metadata path (needed for ``list``/``read`` grants).

    >>> metadata_path("database")
    'secret/metadata/eva-syndicate/database'
    """
    return secret_path(service).replace(f"{MOUNT}/data/", f"{MOUNT}/metadata/", 1)


def policy_paths_for_service(service: str) -> List[str]:
    """Data + metadata paths a policy must grant to read one service."""
    return [secret_path(service), metadata_path(service)]


def agent_prefix(agent_id: str) -> str:
    """Return the glob covering one agent's own subtree."""
    agent_id = (agent_id or "").strip().strip("/")
    if not agent_id:
        raise ValueError("agent_prefix() requires a non-empty agent id")
    return f"{MOUNT}/data/{PREFIX}/{AGENTS}/{agent_id}/*"


def mount_path() -> str:
    """Return the KV v2 mount path used by :func:`secret_path`."""
    return MOUNT


def policy_paths() -> List[str]:
    """Read globs for the **runtime** policy (the container that exists today).

    The runtime hosts every floor in one process, so its policy is the union of
    everything the running code reads. It is deliberately explicit per secret
    instead of ``secret/data/eva-syndicate/*``: a wildcard would also grant any
    secret added later, including other agents' provider keys.
    """
    grants: List[str] = []
    for service in INFRA_SERVICES + (AUTH,) + CONNECTOR_SERVICES + VOICE_SERVICES:
        grants.extend(policy_paths_for_service(service))
    # Per-agent subtrees: connectors read ``agents/<id>/<name>`` when a floor
    # keeps its keys under its own name. The runtime sees all of them because
    # all floors share this process; per-agent containers do not (see
    # ``agent_policy_paths``).
    grants.append(f"{MOUNT}/data/{PREFIX}/{AGENTS}/*")
    grants.append(f"{MOUNT}/metadata/{PREFIX}/{AGENTS}/*")
    return grants


def agent_policy_paths(agent_id: str) -> List[str]:
    """Read globs for one agent's policy (future per-agent container)."""
    # Domain tool workers need only their own auth/provider subtree.
    infra = () if agent_id in {"oscar", "tyler", "jack"} else INFRA_SERVICES
    services = infra + AGENT_SERVICES.get(agent_id, ())
    grants: List[str] = []
    for service in services:
        grants.extend(policy_paths_for_service(service))
    grants.append(agent_prefix(agent_id))
    grants.append(f"{MOUNT}/metadata/{PREFIX}/{AGENTS}/{agent_id}/*")
    return grants
