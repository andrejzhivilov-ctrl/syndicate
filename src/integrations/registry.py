"""
Connector registry — central discovery + health for all integrations.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import structlog

from src.integrations.base import BaseConnector
from src.integrations.google_workspace import GoogleWorkspaceConnector
from src.integrations.mcp_gateway import MCPGateway
from src.integrations.telegram import TelegramConnector

logger = structlog.get_logger(__name__)


def _parse_mcp_servers(raw: Any) -> Dict[str, str]:
    """Accept either a dict or a 'name=url,name=url' string."""
    if isinstance(raw, dict):
        return {k: str(v).rstrip("/") for k, v in raw.items()}
    servers: Dict[str, str] = {}
    if isinstance(raw, str) and raw.strip():
        for pair in raw.split(","):
            if "=" in pair:
                name, url = pair.split("=", 1)
                servers[name.strip()] = url.strip().rstrip("/")
    return servers


class ConnectorRegistry:
    """Holds connector instances and exposes lookup + aggregated health."""

    def __init__(self) -> None:
        self._connectors: Dict[str, BaseConnector] = {}

    def register(self, name: str, connector: BaseConnector) -> None:
        self._connectors[name] = connector
        logger.info("connector_registered", name=name)

    def get(self, name: str) -> BaseConnector:
        if name not in self._connectors:
            raise KeyError(f"Connector '{name}' is not registered.")
        return self._connectors[name]

    def names(self) -> List[str]:
        return list(self._connectors)

    async def all_health(self) -> Dict[str, Any]:
        results = await asyncio.gather(
            *(c.health_check() for c in self._connectors.values()),
            return_exceptions=True,
        )
        out: Dict[str, Any] = {}
        for name, res in zip(self._connectors, results, strict=True):
            out[name] = res if not isinstance(res, Exception) else {
                "service": name, "healthy": False, "detail": str(res),
            }
        return out


def build_default_registry(
    vault_client: Any = None, config: Optional[Dict[str, Any]] = None
) -> ConnectorRegistry:
    """Instantiate the connectors that are enabled in config.

    config keys:
      enabled: list[str]  — which connectors to build
                            (google_workspace, mcp, telegram). Defaults to all.
      google_workspace: dict  — per-connector config
      telegram: dict
      mcp_servers: dict | 'name=url,...'
    """
    config = config or {}
    enabled = set(config.get("enabled", ["google_workspace", "mcp", "telegram"]))
    registry = ConnectorRegistry()

    if "google_workspace" in enabled:
        registry.register(
            "google_workspace",
            GoogleWorkspaceConnector(vault_client, config.get("google_workspace", {})),
        )
    if "telegram" in enabled:
        registry.register(
            "telegram",
            TelegramConnector(vault_client, config.get("telegram", {})),
        )
    if "mcp" in enabled:
        mcp_cfg = dict(config.get("mcp", {}))
        mcp_cfg["mcp_servers"] = _parse_mcp_servers(
            config.get("mcp_servers", mcp_cfg.get("mcp_servers", {}))
        )
        registry.register("mcp", MCPGateway(vault_client, mcp_cfg))

    return registry
