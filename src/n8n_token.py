"""Print the token n8n uses for one agent: python -m src.n8n_token trainer

Andrii pastes it into an n8n Header Auth credential (name ``Authorization``, value
``Bearer <token>``). It is derived from the master key in Vault, so nothing new is stored.
Logs go to stderr: stdout is only the token line.
"""
from __future__ import annotations

import asyncio
import sys

import structlog

from src.hermes_token import _master
from src.n8n_bridge import AGENT_KINDS, n8n_token


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in AGENT_KINDS:
        print(f"usage: python -m src.n8n_token {{{','.join(sorted(AGENT_KINDS))}}}", file=sys.stderr)
        return 2
    structlog.configure(logger_factory=structlog.PrintLoggerFactory(sys.stderr))
    print(f"Bearer {n8n_token(sys.argv[1], asyncio.run(_master()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
