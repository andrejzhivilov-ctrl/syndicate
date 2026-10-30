#!/usr/bin/env python3
"""Renew the Vault operator token (``/opt/eva/vault-secrets/operator.token``).

Vault caps token leases at ``max_lease_ttl`` (24h here), so the operator token
silently dies a day after it was created unless somebody renews it. Run from a
systemd timer every ~12h (``deploy/systemd/syndicate-operator-token-renew.*``).

The token is read from the 0600 file and sent in a header; it is never put in
argv or printed. Only the remaining TTL is reported.
"""
from __future__ import annotations

import json
import os
import stat
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
TOKEN_FILE = Path(os.getenv("VAULT_OPERATOR_TOKEN_FILE", "/opt/eva/vault-secrets/operator.token"))
TIMEOUT_S = 15


def read_token(path: Path = TOKEN_FILE) -> str:
    if not path.is_file():
        raise SystemExit(f"{path} not found")
    if path.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise SystemExit(f"{path} must be mode 0600")
    token = path.read_text(encoding="utf-8").strip()
    if not token:
        raise SystemExit(f"{path} is empty")
    return token


def renew(token: str, addr: str = VAULT_ADDR) -> Optional[int]:
    """Renew the token; returns the new TTL in seconds, or None when Vault gave none."""
    request = urllib.request.Request(f"{addr}/v1/auth/token/renew-self", data=b"{}", method="POST",
                                     headers={"X-Vault-Token": token, "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:  # noqa: S310 - fixed local Vault URL
        auth = json.loads(response.read()).get("auth") or {}
    ttl = auth.get("lease_duration")
    return int(ttl) if ttl is not None else None


def main() -> int:
    try:
        ttl = renew(read_token())
    except urllib.error.HTTPError as exc:
        print(f"renew failed: Vault answered HTTP {exc.code}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, OSError, ValueError) as exc:
        print(f"renew failed: {type(exc).__name__}", file=sys.stderr)
        return 1
    if ttl is None:
        print("renew failed: Vault returned no TTL", file=sys.stderr)
        return 1
    print(f"operator token renewed, ttl {ttl // 3600}h")
    return 0


if __name__ == "__main__":
    sys.exit(main())
