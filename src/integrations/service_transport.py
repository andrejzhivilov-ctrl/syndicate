"""Bounded outbound JSON and subprocess transport for operator-configured services."""
from __future__ import annotations

import asyncio
import json
import os
import signal
from urllib.parse import urlsplit

import httpx

LIMIT = 2_000_000


def endpoint(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('invalid_service_endpoint')
    if parsed.query or parsed.fragment:
        raise ValueError('invalid_service_endpoint')
    return value.rstrip('/')


class JSONTransport:
    """URLs are trusted startup configuration, never tool/model arguments."""

    def __init__(self, url: str, token: str = '', *, transport=None):
        self.url = endpoint(url)
        self.token = token
        self.transport = transport

    async def request(self, path: str, body: dict) -> dict:
        headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
        async with httpx.AsyncClient(timeout=60, follow_redirects=False,
                                     trust_env=False, transport=self.transport) as client:
            async with client.stream('POST', self.url + path, json=body, headers=headers) as response:
                response.raise_for_status()
                raw = bytearray()
                async for chunk in response.aiter_bytes():
                    raw.extend(chunk)
                    if len(raw) > LIMIT:
                        raise ValueError('service_response_too_large')
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError('invalid_service_response')
        return value


async def _bounded(stream) -> bytes:
    data = bytearray()
    while chunk := await stream.read(65536):
        data.extend(chunk)
        if len(data) > LIMIT:
            raise ValueError('process_output_too_large')
    return bytes(data)


async def run_process(argv: list[str], body: dict, *, cwd: str, timeout: int = 120) -> bytes:
    """Fixed argv; credentials go via stdin, not process arguments or inherited env."""
    env = {k: os.environ[k] for k in ('PATH', 'LANG', 'HOME', 'HYPERFRAMES_BROWSER_PATH') if k in os.environ}
    env.update(DO_NOT_TRACK='1', HYPERFRAMES_SKIP_SKILLS='1')
    process = await asyncio.create_subprocess_exec(
        *argv, cwd=cwd, env=env, stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, start_new_session=True,
    )
    readers = [asyncio.create_task(_bounded(process.stdout)), asyncio.create_task(_bounded(process.stderr))]
    try:
        async with asyncio.timeout(timeout):
            process.stdin.write(json.dumps(body).encode())
            await process.stdin.drain()
            process.stdin.close()
            output, _ = await asyncio.gather(*readers)
            code = await process.wait()
            if code != 0:
                raise ValueError('service_process_failed')
            return output
    finally:
        if process.returncode is None:
            os.killpg(process.pid, signal.SIGKILL) if hasattr(os, 'killpg') else process.kill()
            await process.wait()
        for reader in readers:
            reader.cancel()
        await asyncio.gather(*readers, return_exceptions=True)
