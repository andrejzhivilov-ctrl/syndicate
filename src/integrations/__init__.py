"""EVA SYNDICATE integration / connector layer."""

from src.integrations.base import BaseConnector, ConnectorError
from src.integrations.google_workspace import GoogleWorkspaceConnector
from src.integrations.mcp_gateway import MCPGateway
from src.integrations.registry import ConnectorRegistry, build_default_registry
from src.integrations.telegram import TelegramConnector

__all__ = [
    "BaseConnector",
    "ConnectorError",
    "GoogleWorkspaceConnector",
    "MCPGateway",
    "TelegramConnector",
    "ConnectorRegistry",
    "build_default_registry",
]
