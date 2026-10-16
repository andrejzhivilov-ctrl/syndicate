#!/usr/bin/env python3
"""Copy Vault KV v2 secrets into the canonical Syndicate namespace.

The default is a read-only dry run. The tool never deletes legacy secrets,
never overwrites a destination, and never prints secret values. Use a temporary
operator token with LIST/READ on the legacy namespace and READ/CREATE on the
canonical namespace; do not use an agent runtime token.

Examples (credentials are read only from the process environment)::

    VAULT_ADDR=https://vault.example VAULT_TOKEN=... \\
        python tools/migrate_vault_namespace.py
    VAULT_ADDR=https://vault.example VAULT_TOKEN=... \\
        python tools/migrate_vault_namespace.py --apply

The live migration must be separately approved and run through the protected
server channel. KV v2 history is not copied: each destination receives the
current active data as a new version, while legacy versions remain untouched.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src import vault_paths  # noqa: E402

MAX_SECRETS = 10_000


class MigrationError(RuntimeError):
    """Safe-to-display operational error; contains paths, never secret values."""


class MigrationConflict(MigrationError):
    """A canonical destination already exists with different secret data."""


@dataclass(frozen=True)
class SecretCopy:
    source_path: str
    target_path: str
    action: str
    data: dict[str, Any] | None = field(default=None, repr=False)


class VaultNamespaceMigrator:
    """Plan or copy active KV v2 values from the old prefix to the new prefix."""

    def __init__(
        self,
        vault_addr: str,
        token: str,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        if not vault_addr.strip() or not token.strip():
            raise ValueError("vault_addr_and_token_required")
        self.vault_addr = vault_addr.rstrip("/")
        self._token = token
        self._client = client or httpx.Client(timeout=15.0, follow_redirects=False)

    def close(self) -> None:
        self._client.close()

    @staticmethod
    def _url_path(path: str) -> str:
        return "/".join(quote(part, safe="") for part in path.split("/"))

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        missing_ok: bool = False,
    ) -> dict[str, Any] | None:
        response = self._client.request(
            method,
            f"{self.vault_addr}/v1/{self._url_path(path)}",
            headers={"X-Vault-Token": self._token},
            params=params,
            json=body,
        )
        if response.status_code == 404 and missing_ok:
            return None
        if response.is_error:
            raise MigrationError(
                f"Vault {method} failed with HTTP {response.status_code} for path {path}"
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise MigrationError(f"Vault returned invalid JSON for path {path}") from exc
        if not isinstance(payload, dict):
            raise MigrationError(f"Vault returned an unexpected response for path {path}")
        return payload

    def list_source_paths(self) -> list[str]:
        """Recursively list metadata keys beneath the legacy prefix."""
        root = f"{vault_paths.MOUNT}/metadata/{vault_paths.LEGACY_PREFIX}"
        pending = [root]
        visited: set[str] = set()
        data_paths: set[str] = set()
        while pending:
            folder = pending.pop()
            if folder in visited:
                continue
            visited.add(folder)
            payload = self._request("LIST", folder, missing_ok=True)
            if payload is None:
                continue
            values = (payload.get("data") or {}).get("keys")
            if not isinstance(values, list):
                raise MigrationError(f"Vault LIST response has no keys for path {folder}")
            for item in values:
                if not isinstance(item, str) or not item or item.startswith("/"):
                    raise MigrationError(f"Vault returned an invalid key beneath {folder}")
                parts = item.rstrip("/").split("/")
                if any(part in {"", ".", ".."} for part in parts):
                    raise MigrationError(f"Vault returned an unsafe key beneath {folder}")
                full = f"{folder}/{item.rstrip('/')}"
                if item.endswith("/"):
                    pending.append(full)
                else:
                    prefix = f"{vault_paths.MOUNT}/metadata/{vault_paths.LEGACY_PREFIX}/"
                    relative = full.removeprefix(prefix)
                    data_paths.add(f"{vault_paths.MOUNT}/data/{vault_paths.LEGACY_PREFIX}/{relative}")
                    if len(data_paths) > MAX_SECRETS:
                        raise MigrationError(f"source namespace exceeds the {MAX_SECRETS} secret safety limit")
        return sorted(data_paths)

    def _secret_data(self, path: str) -> dict[str, Any] | None:
        payload = self._request("GET", path, missing_ok=True)
        if payload is None:
            return None
        try:
            data = payload["data"]["data"]
        except (KeyError, TypeError):
            raise MigrationError(f"Vault KV v2 response has an unexpected envelope for path {path}") from None
        if not isinstance(data, dict):
            raise MigrationError(f"Vault KV v2 data is not an object for path {path}")
        return data

    @staticmethod
    def _target_for(source_path: str) -> str:
        old = f"{vault_paths.MOUNT}/data/{vault_paths.LEGACY_PREFIX}/"
        if not source_path.startswith(old):
            raise MigrationError("refusing to migrate a path outside the legacy namespace")
        return f"{vault_paths.MOUNT}/data/{vault_paths.PREFIX}/{source_path[len(old):]}"

    def plan(self) -> tuple[list[SecretCopy], list[str]]:
        """Read a complete plan; collect all conflicts before any destination write."""
        records: list[SecretCopy] = []
        conflicts: list[str] = []
        for source in self.list_source_paths():
            target = self._target_for(source)
            source_data = self._secret_data(source)
            if source_data is None:
                records.append(SecretCopy(source, target, "missing"))
                continue
            target_data = self._secret_data(target)
            if target_data is None:
                records.append(SecretCopy(source, target, "copy", source_data))
            elif target_data == source_data:
                records.append(SecretCopy(source, target, "identical"))
            else:
                conflicts.append(target)
        return records, conflicts

    def migrate(self, *, apply: bool = False) -> dict[str, int]:
        """Dry-run by default; apply creates only absent canonical secrets (CAS=0)."""
        records, conflicts = self.plan()
        if conflicts:
            raise MigrationConflict(
                "destination conflicts; no writes were made: " + ", ".join(sorted(conflicts))
            )
        counts = {"copy": 0, "identical": 0, "missing": 0}
        for record in records:
            counts[record.action] += 1
            if apply and record.action == "copy":
                assert record.data is not None
                self._request(
                    "POST",
                    record.target_path,
                    body={"options": {"cas": 0}, "data": record.data},
                )
        return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="create absent canonical secrets; default is a read-only dry run",
    )
    args = parser.parse_args(argv)
    address = os.getenv("VAULT_ADDR", "").strip()
    token = os.getenv("VAULT_TOKEN", "").strip()
    if not address or not token:
        parser.error("set VAULT_ADDR and VAULT_TOKEN in the protected environment")
    migrator = VaultNamespaceMigrator(address, token)
    try:
        counts = migrator.migrate(apply=args.apply)
    except MigrationConflict as exc:
        print(f"CONFLICT: {exc}", file=sys.stderr)
        return 2
    except MigrationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except httpx.HTTPError as exc:
        # Transport exceptions may include the configured URL; log only the type.
        print(f"ERROR: Vault transport failed ({type(exc).__name__})", file=sys.stderr)
        return 1
    finally:
        migrator.close()
    copied = counts["copy"] if args.apply else 0
    planned = counts["copy"] if not args.apply else counts["copy"]
    mode = "APPLIED" if args.apply else "DRY RUN"
    print(
        f"{mode}: {planned} to copy, {counts['identical']} already identical, "
        f"{counts['missing']} deleted/missing; copied now: {copied}. "
        "No values printed; legacy secrets were not deleted."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
