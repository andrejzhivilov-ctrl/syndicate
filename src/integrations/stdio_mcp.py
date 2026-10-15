"""Official MCP SDK adapter; host-owned commands and explicit tool grants only."""
from __future__ import annotations

import asyncio
import json
import os

from src.integrations.service_transport import LIMIT


async def call_mcp(config: dict, tool: str | None, arguments: dict) -> dict:
    # Optional dependency lives in the isolated integration image, not the core venv.
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    if not isinstance(arguments, dict) or len(json.dumps(arguments)) > 20000:
        raise ValueError('invalid_mcp_arguments')
    params = StdioServerParameters(command=config['command'], args=config.get('args', []),
                                  env=config.get('env', {}), cwd=config.get('cwd'))
    async with asyncio.timeout(60):
        # Child stderr is intentionally not forwarded: it may contain provider secrets.
        with open(os.devnull, 'w') as errors:
            async with stdio_client(params, errlog=errors) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    if tool is None:
                        result = await session.list_tools()
                        allowed = set(config.get('tools', []))
                        data = {'tools': [t.model_dump(mode='json') for t in result.tools if t.name in allowed]}
                    else:
                        if tool not in config.get('tools', []):
                            raise ValueError('mcp_tool_not_granted')
                        result = await session.call_tool(tool, arguments)
                        if result.isError:
                            raise ValueError('mcp_tool_failed')
                        data = result.model_dump(mode='json')
                    if len(json.dumps(data)) > LIMIT:
                        raise ValueError('mcp_result_too_large')
                    return data
