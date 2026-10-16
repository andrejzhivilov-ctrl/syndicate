from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from src import vault_paths
from src.vault_client import VaultClient
from tools.migrate_postgres_db_name import DatabaseMigrationError, migrate_database
from tools.migrate_vault_namespace import MigrationConflict, VaultNamespaceMigrator


def test_vault_paths_prefer_canonical_and_retain_exact_legacy_grants() -> None:
    assert vault_paths.secret_path("database") == "secret/data/syndicate/database"
    assert vault_paths.legacy_secret_path("database") == "secret/data/eva-syndicate/database"
    assert vault_paths.read_path_candidates("secret/data/syndicate/redis") == [
        "secret/data/syndicate/redis",
        "secret/data/eva-syndicate/redis",
    ]
    assert vault_paths.read_path_candidates("secret/data/eva-syndicate/redis") == [
        "secret/data/syndicate/redis",
        "secret/data/eva-syndicate/redis",
    ]
    assert vault_paths.read_path_candidates("secret/data/other/path") == ["secret/data/other/path"]


def test_vault_client_falls_back_only_after_canonical_404() -> None:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        if request.url.path.endswith("/data/syndicate/redis"):
            return httpx.Response(404, json={"errors": ["not found"]})
        return httpx.Response(200, json={"data": {"data": {"password": "test-only-value"}}})

    async def run() -> dict:
        client = VaultClient("http://vault", "role", "secret")
        client._token = "synthetic-token"
        client._token_expires_at = 9_999_999_999
        client._http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        try:
            return await client.get_secret(vault_paths.secret_path("redis"))
        finally:
            await client._http.aclose()

    assert asyncio.run(run()) == {"password": "test-only-value"}
    assert seen == [
        "/v1/secret/data/syndicate/redis",
        "/v1/secret/data/eva-syndicate/redis",
    ]


def test_vault_client_does_not_mask_permission_errors_with_legacy_fallback() -> None:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        return httpx.Response(403, json={"errors": ["permission denied"]})

    async def run() -> None:
        client = VaultClient("http://vault", "role", "secret")
        client._token = "synthetic-token"
        client._token_expires_at = 9_999_999_999
        client._http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        try:
            with pytest.raises(httpx.HTTPStatusError):
                await client.get_secret(vault_paths.secret_path("redis"))
        finally:
            await client._http.aclose()

    asyncio.run(run())
    assert seen == ["/v1/secret/data/syndicate/redis"]


class _VaultStub:
    def __init__(self, secrets: dict[str, dict]) -> None:
        self.secrets = secrets
        self.writes: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path.removeprefix("/v1/")
        if request.method == "LIST":
            if path == "secret/metadata/eva-syndicate":
                return httpx.Response(200, json={"data": {"keys": ["database", "agents/"]}})
            if path == "secret/metadata/eva-syndicate/agents":
                return httpx.Response(200, json={"data": {"keys": ["alice/"]}})
            if path == "secret/metadata/eva-syndicate/agents/alice":
                return httpx.Response(200, json={"data": {"keys": ["gemini"]}})
            return httpx.Response(404, json={"errors": ["not found"]})
        if request.method == "GET":
            if path in self.secrets:
                return httpx.Response(200, json={"data": {"data": self.secrets[path]}})
            return httpx.Response(404, json={"errors": ["not found"]})
        if request.method == "POST":
            body = json.loads(request.content)
            assert body["options"]["cas"] == 0
            target = path
            self.secrets[target] = body["data"]
            self.writes.append(target)
            return httpx.Response(200, json={"data": {"version": 1}})
        raise AssertionError(f"unexpected HTTP method {request.method}")


def _migrator(stub: _VaultStub) -> VaultNamespaceMigrator:
    return VaultNamespaceMigrator(
        "https://vault.invalid",
        "synthetic-token",
        client=httpx.Client(transport=httpx.MockTransport(stub)),
    )


def test_vault_migration_dry_run_is_read_only_and_copies_no_values_to_output() -> None:
    stub = _VaultStub(
        {
            "secret/data/eva-syndicate/database": {"user": "db-user", "password": "private-test-value"},
            "secret/data/eva-syndicate/agents/alice/gemini": {"api_key": "private-test-key"},
        }
    )
    migrator = _migrator(stub)
    try:
        assert migrator.migrate() == {"copy": 2, "identical": 0, "missing": 0}
    finally:
        migrator.close()
    assert stub.writes == []
    assert "secret/data/syndicate/database" not in stub.secrets
    assert "secret/data/eva-syndicate/database" in stub.secrets


def test_vault_migration_apply_creates_only_absent_destinations() -> None:
    stub = _VaultStub({"secret/data/eva-syndicate/database": {"user": "db-user"}})
    migrator = _migrator(stub)
    try:
        assert migrator.migrate(apply=True) == {"copy": 1, "identical": 0, "missing": 1}
    finally:
        migrator.close()
    assert stub.writes == ["secret/data/syndicate/database"]
    assert stub.secrets["secret/data/syndicate/database"] == {"user": "db-user"}
    assert "secret/data/eva-syndicate/database" in stub.secrets


def test_vault_migration_conflicts_abort_before_any_write() -> None:
    stub = _VaultStub(
        {
            "secret/data/eva-syndicate/database": {"user": "old-user"},
            "secret/data/syndicate/database": {"user": "different-user"},
        }
    )
    migrator = _migrator(stub)
    try:
        with pytest.raises(MigrationConflict, match="no writes were made"):
            migrator.migrate(apply=True)
    finally:
        migrator.close()
    assert stub.writes == []


class _CursorStub:
    def __init__(self, connection: "_ConnectionStub") -> None:
        self.connection = connection
        self.result: list[tuple] = []

    def __enter__(self) -> "_CursorStub":
        return self

    def __exit__(self, *_args) -> None:
        return None

    def execute(self, query: str, params: tuple | None = None) -> None:
        self.connection.queries.append((query, params))
        if query == "SELECT current_database()":
            self.result = [(self.connection.current_database,)]
        elif query.startswith("SELECT datname FROM pg_database"):
            self.result = [(name,) for name in self.connection.databases if name in (params or ())]
        elif query.startswith("SELECT count(*) FROM pg_stat_activity"):
            active = self.connection.active_counts.pop(0) if self.connection.active_counts else 0
            self.result = [(active,)]
        elif query.startswith("ALTER DATABASE"):
            return
        else:
            raise AssertionError(f"unexpected SQL: {query}")

    def fetchone(self) -> tuple:
        return self.result[0]

    def fetchall(self) -> list[tuple]:
        return self.result


class _ConnectionStub:
    def __init__(
        self,
        databases: set[str],
        active_counts: list[int] | None = None,
        current_database: str = "postgres",
    ) -> None:
        self.databases = databases
        self.active_counts = list(active_counts or [0])
        self.current_database = current_database
        self.autocommit = False
        self.queries: list[tuple[str, tuple | None]] = []

    def cursor(self) -> _CursorStub:
        return _CursorStub(self)


def test_postgres_migration_dry_run_has_no_ddl() -> None:
    connection = _ConnectionStub({"eva_syndicate"})
    result = migrate_database(connection)
    assert result == {
        "source": "eva_syndicate",
        "target": "syndicate",
        "state": "ready",
        "active_connections": 0,
    }
    assert not any(query.startswith("ALTER DATABASE") for query, _ in connection.queries)


def test_postgres_migration_renames_in_place_only_after_session_checks() -> None:
    connection = _ConnectionStub({"eva_syndicate"}, active_counts=[0, 0])
    result = migrate_database(connection, apply=True)
    assert result["state"] == "renamed"
    assert connection.autocommit is True
    ddl = [query for query, _ in connection.queries if query.startswith("ALTER DATABASE")]
    assert ddl == [
        'ALTER DATABASE "eva_syndicate" WITH ALLOW_CONNECTIONS false',
        'ALTER DATABASE "eva_syndicate" RENAME TO "syndicate"',
        'ALTER DATABASE "syndicate" WITH ALLOW_CONNECTIONS true',
    ]


def test_postgres_migration_aborts_if_sessions_race_after_connections_are_disabled() -> None:
    connection = _ConnectionStub({"eva_syndicate"}, active_counts=[0, 2])
    result = migrate_database(connection, apply=True)
    assert result["state"] == "blocked_active_connections"
    ddl = [query for query, _ in connection.queries if query.startswith("ALTER DATABASE")]
    assert ddl == [
        'ALTER DATABASE "eva_syndicate" WITH ALLOW_CONNECTIONS false',
        'ALTER DATABASE "eva_syndicate" WITH ALLOW_CONNECTIONS true',
    ]


def test_postgres_migration_requires_maintenance_database() -> None:
    connection = _ConnectionStub({"eva_syndicate"}, current_database="syndicate")
    with pytest.raises(DatabaseMigrationError, match="admin_url_must_connect_to_postgres_database"):
        migrate_database(connection)


def test_postgres_migration_is_idempotent_and_supports_rollback() -> None:
    already_migrated = _ConnectionStub({"syndicate"})
    assert migrate_database(already_migrated)["state"] == "already_migrated"

    rollback = _ConnectionStub({"syndicate"}, active_counts=[0, 0])
    result = migrate_database(rollback, apply=True, rollback=True)
    assert result == {
        "source": "syndicate",
        "target": "eva_syndicate",
        "state": "renamed",
        "active_connections": 0,
    }
    ddl = [query for query, _ in rollback.queries if query.startswith("ALTER DATABASE")]
    assert 'ALTER DATABASE "syndicate" RENAME TO "eva_syndicate"' in ddl


def test_postgres_rename_failure_attempts_to_restore_both_allowlisted_names() -> None:
    class FailingRenameCursor(_CursorStub):
        def execute(self, query: str, params: tuple | None = None) -> None:
            if query.startswith("ALTER DATABASE") and " RENAME TO " in query:
                self.connection.queries.append((query, params))
                raise RuntimeError("simulated DDL transport failure")
            super().execute(query, params)

    class FailingRenameConnection(_ConnectionStub):
        def cursor(self) -> FailingRenameCursor:
            return FailingRenameCursor(self)

    connection = FailingRenameConnection({"eva_syndicate"}, active_counts=[0, 0])
    with pytest.raises(RuntimeError, match="simulated DDL transport failure"):
        migrate_database(connection, apply=True)
    ddl = [query for query, _ in connection.queries if query.startswith("ALTER DATABASE")]
    assert 'ALTER DATABASE "eva_syndicate" WITH ALLOW_CONNECTIONS true' in ddl
    assert 'ALTER DATABASE "syndicate" WITH ALLOW_CONNECTIONS true' in ddl
