"""Print the env file of one Hermes container: python -m src.hermes_token trainer

The operator redirects this into a root-only file. Both values are derived from the
master key in Vault, so nothing new is stored there and the output is never logged.
"""
from __future__ import annotations

import asyncio
import os
import sys

import structlog

from src.hermes_gateway import AGENT_ACTIONS, agent_token
from src.vault_client import VaultClient
from src.vault_paths import secret_path


async def _master() -> str:
    vault = VaultClient(os.environ["VAULT_ADDR"], os.environ["VAULT_ROLE_ID"], os.environ["VAULT_SECRET_ID"])
    await vault.authenticate()
    try:
        return (await vault.get_secret(secret_path("auth"))).get("api_key") or os.environ["EVA_API_KEY"]
    finally:
        await vault.aclose()


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in AGENT_ACTIONS:
        print(f"usage: python -m src.hermes_token {{{','.join(sorted(AGENT_ACTIONS))}}}", file=sys.stderr)
        return 2
    # stdout is the env file itself: a log line there breaks it (docker: "key cannot contain a space").
    structlog.configure(logger_factory=structlog.PrintLoggerFactory(sys.stderr))
    token = agent_token(sys.argv[1], asyncio.run(_master()))
    print(f"API_SERVER_KEY={token}\nSYNDICATE_TOKEN={token}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
