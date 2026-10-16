"""Single source of truth for HashiCorp Vault secret paths.

The canonical KV v2 prefix is ``syndicate``. During the controlled migration,
``VaultClient`` tries that prefix first and falls back to the historical
``eva-syndicate`` namespace only on HTTP 404. Generated ACL policies grant the
same exact least-privilege paths beneath both prefixes until an operator
completes the migration and separately approves retirement of the legacy
namespace. Never infer that static policy files have been applied to live Vault.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

#: KV v2 mount point. Vault exposes data at ``<mount>/data/<path>``.
MOUNT = "secret"

#: Canonical logical prefix inside the mount.
PREFIX = "syndicate"

#: Temporary compatibility prefix. Keep until the operator completes Vault
#: migration and separately approves removal of legacy reads/grants.
LEGACY_PREFIX = "eva-syndicate"

PREFIXES: Tuple[str, ...] = (PREFIX, LEGACY_PREFIX)

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
AGENTS_IDS: Tuple[str, ...] = ("eva", "marshal", "architect", "fin", "doc", "kira", "sam", "oscar", "tyler", "jack", "alice")

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
    "alice": (),
}


def secret_path(service: str) -> str:
    """Return the Vault HTTP path for ``service``'s KV v2 secret.

    >>> secret_path("database")
    'secret/data/syndicate/database'
    """
    service = (service or "").strip().strip("/")
    if not service:
        raise ValueError("secret_path() requires a non-empty service name")
    return f"{MOUNT}/data/{PREFIX}/{service}"


def agent_secret_path(agent_id: str, name: str = "") -> str:
    """Return the path of one agent's own secret, e.g. Sam's broker keys.

    >>> agent_secret_path("sam", "broker")
    'secret/data/syndicate/agents/sam/broker'
    """
    agent_id = (agent_id or "").strip().strip("/")
    if not agent_id:
        raise ValueError("agent_secret_path() requires a non-empty agent id")
    parts = [MOUNT, "data", PREFIX, AGENTS, agent_id]
    if name:
        parts.append(name.strip().strip("/"))
    return "/".join(parts)


def legacy_secret_path(service: str) -> str:
    """Return the old KV v2 data path for read-only migration compatibility."""
    return secret_path(service).replace(f"/{PREFIX}/", f"/{LEGACY_PREFIX}/", 1)


def legacy_agent_secret_path(agent_id: str, name: str = "") -> str:
    """Return an agent path in the legacy namespace (migration tooling only)."""
    return agent_secret_path(agent_id, name).replace(f"/{PREFIX}/", f"/{LEGACY_PREFIX}/", 1)


def read_path_candidates(path: str) -> List[str]:
    """Return canonical-first Vault paths, accepting either namespace as input.

    Only KV v2 data/metadata paths beneath this application's two known prefixes
    are translated. Other mounts and paths are returned unchanged.
    """
    pairs = (
        (f"{MOUNT}/data/{PREFIX}/", f"{MOUNT}/data/{LEGACY_PREFIX}/"),
        (f"{MOUNT}/metadata/{PREFIX}/", f"{MOUNT}/metadata/{LEGACY_PREFIX}/"),
    )
    for canonical, legacy in pairs:
        if path.startswith(canonical):
            return [path, legacy + path[len(canonical):]]
        if path.startswith(legacy):
            return [canonical + path[len(legacy):], path]
    return [path]


def metadata_path(service: str) -> str:
    """Return the canonical KV v2 metadata path (needed for list/read grants).

    >>> metadata_path("database")
    'secret/metadata/syndicate/database'
    """
    return secret_path(service).replace(f"{MOUNT}/data/", f"{MOUNT}/metadata/", 1)


def policy_paths_for_service(service: str) -> List[str]:
    """Exact data + metadata grants under canonical and migration prefixes."""
    canonical_data = secret_path(service)
    canonical_metadata = metadata_path(service)
    legacy_data = legacy_secret_path(service)
    legacy_metadata = canonical_metadata.replace(f"/{PREFIX}/", f"/{LEGACY_PREFIX}/", 1)
    return [canonical_data, canonical_metadata, legacy_data, legacy_metadata]


def agent_prefix(agent_id: str) -> str:
    """Return the canonical glob covering one agent's own subtree."""
    agent_id = (agent_id or "").strip().strip("/")
    if not agent_id:
        raise ValueError("agent_prefix() requires a non-empty agent id")
    return f"{MOUNT}/data/{PREFIX}/{AGENTS}/{agent_id}/*"


def agent_prefixes(agent_id: str) -> List[str]:
    """Return per-agent subtree globs for canonical and legacy namespaces."""
    canonical = agent_prefix(agent_id)
    return [canonical, canonical.replace(f"/{PREFIX}/", f"/{LEGACY_PREFIX}/", 1)]


def mount_path() -> str:
    """Return the KV v2 mount path used by :func:`secret_path`."""
    return MOUNT


def policy_paths() -> List[str]:
    """Read globs for the **runtime** policy (the container that exists today).

    The runtime hosts every floor in one process, so its policy is the union of
    everything the running code reads. It is deliberately explicit per service
    under both the canonical and migration prefixes; no whole-prefix wildcard
    is granted. Per-agent paths remain scoped to the runtime's existing role.
    """
    grants: List[str] = []
    for service in INFRA_SERVICES + (AUTH,) + CONNECTOR_SERVICES + VOICE_SERVICES:
        grants.extend(policy_paths_for_service(service))
    # The current shared runtime sees each agent subtree. A separately deployed
    # worker receives only its own subtree from agent_policy_paths().
    for prefix in PREFIXES:
        grants.append(f"{MOUNT}/data/{prefix}/{AGENTS}/*")
        grants.append(f"{MOUNT}/metadata/{prefix}/{AGENTS}/*")
    return grants


def agent_policy_paths(agent_id: str) -> List[str]:
    """Read paths for one agent's policy (future per-agent container)."""
    if agent_id == "alice":
        # Alice's initial API-only profile needs its worker auth key and Gemini
        # key, but no shared database/Redis/LLM secrets and no future subtree
        # wildcard. Add optional provider paths only with a separately reviewed
        # implementation and grant.
        grants: List[str] = []
        for name in ("auth", "gemini"):
            for data_path in (
                agent_secret_path(agent_id, name),
                legacy_agent_secret_path(agent_id, name),
            ):
                grants.extend(
                    [
                        data_path,
                        data_path.replace(f"{MOUNT}/data/", f"{MOUNT}/metadata/", 1),
                    ]
                )
        return grants

    # Domain tool workers need only their own auth/provider subtree.
    infra = () if agent_id in {"oscar", "tyler", "jack"} else INFRA_SERVICES
    services = infra + AGENT_SERVICES.get(agent_id, ())
    grants = []
    for service in services:
        grants.extend(policy_paths_for_service(service))
    for data_glob in agent_prefixes(agent_id):
        grants.append(data_glob)
        grants.append(data_glob.replace(f"{MOUNT}/data/", f"{MOUNT}/metadata/", 1))
    return grants
