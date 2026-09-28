"""
MCP Gateway — unified client for Model Context Protocol (MCP) servers.

Each MCP server is isolated in its own container and reachable only via an
HMAC-signed request (the "signed request from Marshal" rule in EVA_TOOLKIT_SPEC §2).
Communication uses JSON-RPC 2.0 over HTTP.

Server registry is provided via config ``mcp_servers`` as a mapping
``{name: base_url}`` (or parsed from the MCP_SERVERS env string
``name=url,name=url`` by the registry factory).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from typing import Any, Dict, List, Optional

import structlog

from src.integrations.base import BaseConnector, ConnectorError

logger = structlog.get_logger(__name__)


class MCPGateway(BaseConnector):
    """Talks JSON-RPC 2.0 to a set of registered MCP servers."""

    SERVICE_NAME = "mcp"

    def __init__(self, vault_client: Any = None, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(vault_client, config)
        self._servers: Dict[str, str] = dict(self._config.get("mcp_servers", {}))
        self._signing_key: Optional[str] = None

    def register_server(self, name: str, base_url: str) -> None:
        self._servers[name] = base_url.rstrip("/")

    async def _get_signing_key(self) -> str:
        if self._signing_key is None:
            self._signing_key = await self._get_secret("mcp_signing_key")
        return self._signing_key

    def _sign(self, key: str, body: str) -> str:
        return hmac.new(key.encode(), body.encode(), hashlib.sha256).hexdigest()

    async def _rpc(self, server_name: str, method: str, params: Dict[str, Any]) -> Any:
        if server_name not in self._servers:
            raise ConnectorError(f"MCP server '{server_name}' is not registered.")
        base_url = self._servers[server_name]

        envelope = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params,
        }
        body = json.dumps(envelope, separators=(",", ":"), sort_keys=True)

        headers = {"Content-Type": "application/json"}
        try:
            signing_key = await self._get_signing_key()
            headers["X-Marshal-Signature"] = self._sign(signing_key, body)
        except ConnectorError:
            logger.warning("mcp_signing_key_missing", server=server_name)

        result = await self._request(
            "POST", base_url, headers=headers, data=body,
        )
        if isinstance(result, dict) and result.get("error"):
            raise ConnectorError(f"MCP {server_name}.{method} error: {result['error']}")
        return result.get("result") if isinstance(result, dict) else result

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        result = await self._rpc(server_name, "tools/list", {})
        if isinstance(result, dict):
            return result.get("tools", [])
        return result or []

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Any:
        return await self._rpc(
            server_name, "tools/call", {"name": tool_name, "arguments": arguments}
        )

    async def health_check(self) -> Dict[str, Any]:
        statuses: Dict[str, Any] = {}
        healthy = True
        for name in self._servers:
            try:
                await self.list_tools(name)
                statuses[name] = "ok"
            except Exception as exc:  # noqa: BLE001
                statuses[name] = f"error: {exc}"
                healthy = False
        return {"service": self.SERVICE_NAME, "healthy": healthy, "detail": statuses}
