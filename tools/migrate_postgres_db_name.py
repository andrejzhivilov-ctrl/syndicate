#!/usr/bin/env python3
"""Safely rename the application's PostgreSQL database to ``syndicate``.

The default is a read-only preflight. The tool does not terminate sessions,
create/drop databases, copy records, or alter schema. Before ``--apply``, make a
verified backup and stop the API/workers. It connects to the maintenance database
``postgres`` using ``SYNDICATE_POSTGRES_ADMIN_URL``; the URL is never printed.

Examples::

    SYNDICATE_POSTGRES_ADMIN_URL='postgresql://.../postgres' \\
        python tools/migrate_postgres_db_name.py
    SYNDICATE_POSTGRES_ADMIN_URL='postgresql://.../postgres' \\
        python tools/migrate_postgres_db_name.py --apply
    # Roll back the catalog rename if needed:
    SYNDICATE_POSTGRES_ADMIN_URL='postgresql://.../postgres' \\
        python tools/migrate_postgres_db_name.py --rollback --apply

The migration is idempotent when the requested target name is already present.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

OLD_DATABASE = "eva_syndicate"
NEW_DATABASE = "syndicate"
MAINTENANCE_DATABASE = "postgres"


class DatabaseMigrationError(RuntimeError):
    """A safe-to-display preflight or migration failure."""


def _identifier(name: str) -> str:
    """Quote a fixed, allowlisted SQL identifier."""
    if name not in {OLD_DATABASE, NEW_DATABASE}:
        raise DatabaseMigrationError("database_name_not_allowlisted")
    return '"' + name.replace('"', '""') + '"'


def _result(source: str, target: str, state: str, active: int = 0) -> dict[str, Any]:
    return {
        "source": source,
        "target": target,
        "state": state,
        "active_connections": active,
    }


def _active_connection_count(cursor: Any, database: str) -> int:
    cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = %s", (database,))
    return int(cursor.fetchone()[0])


def _preflight(cursor: Any, source: str, target: str) -> dict[str, Any]:
    cursor.execute("SELECT current_database()")
    if cursor.fetchone()[0] != MAINTENANCE_DATABASE:
        raise DatabaseMigrationError("admin_url_must_connect_to_postgres_database")

    cursor.execute(
        "SELECT datname FROM pg_database WHERE datname IN (%s, %s)",
        (source, target),
    )
    present = {row[0] for row in cursor.fetchall()}
    if source not in present and target in present:
        return _result(source, target, "already_migrated")
    if source not in present or target in present:
        raise DatabaseMigrationError("source_or_target_database_state_conflict")

    active = _active_connection_count(cursor, source)
    if active:
        return _result(source, target, "blocked_active_connections", active)
    return _result(source, target, "ready")


def _enable_connections(cursor: Any, database: str) -> None:
    cursor.execute(f"ALTER DATABASE {_identifier(database)} WITH ALLOW_CONNECTIONS true")


def _best_effort_restore(cursor: Any, *databases: str) -> None:
    """Re-enable whichever pre/post-rename catalog name currently exists."""
    for database in databases:
        try:
            _enable_connections(cursor, database)
        except Exception:
            # One candidate may not exist if the rename completed before an
            # I/O error; continue to the other allowlisted name.
            continue


def _rename_in_place(cursor: Any, source: str, target: str) -> dict[str, Any]:
    source_id = _identifier(source)
    target_id = _identifier(target)
    disabled = False
    try:
        # Set this before sending DDL: if the connection drops after the server
        # applies the change, the exception path still attempts to restore it.
        disabled = True
        cursor.execute(f"ALTER DATABASE {source_id} WITH ALLOW_CONNECTIONS false")
        active = _active_connection_count(cursor, source)
        if active:
            _enable_connections(cursor, source)
            disabled = False
            return _result(source, target, "blocked_active_connections", active)
        cursor.execute(f"ALTER DATABASE {source_id} RENAME TO {target_id}")
        _enable_connections(cursor, target)
        disabled = False
    except Exception:
        # The server may have completed the rename even if the client did not
        # receive its response; attempt both fixed, allowlisted catalog names.
        if disabled:
            _best_effort_restore(cursor, source, target)
        raise
    return _result(source, target, "renamed")


def migrate_database(
    connection: Any,
    *,
    apply: bool = False,
    rollback: bool = False,
) -> dict[str, Any]:
    """Preflight or execute a no-copy catalog rename using a DB-API connection."""
    source, target = (NEW_DATABASE, OLD_DATABASE) if rollback else (OLD_DATABASE, NEW_DATABASE)
    if apply:
        connection.autocommit = True  # ALTER DATABASE cannot run inside a transaction.
    with connection.cursor() as cursor:
        state = _preflight(cursor, source, target)
        if state["state"] != "ready" or not apply:
            return state
        return _rename_in_place(cursor, source, target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="execute the catalog rename; default is preflight only")
    parser.add_argument("--rollback", action="store_true", help="plan/rename from syndicate back to eva_syndicate")
    args = parser.parse_args(argv)
    admin_url = os.getenv("SYNDICATE_POSTGRES_ADMIN_URL", "").strip()
    if not admin_url:
        parser.error("set SYNDICATE_POSTGRES_ADMIN_URL in the protected environment")

    try:
        import psycopg2

        connection = psycopg2.connect(admin_url)
    except Exception as exc:  # credentials/URL intentionally omitted from diagnostics
        print(f"ERROR: could not connect to PostgreSQL maintenance database ({type(exc).__name__})", file=sys.stderr)
        return 1
    try:
        result = migrate_database(connection, apply=args.apply, rollback=args.rollback)
    except DatabaseMigrationError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - do not echo driver messages that may contain DSNs
        print(f"ERROR: PostgreSQL migration failed ({type(exc).__name__}); inspect server logs securely", file=sys.stderr)
        return 1
    finally:
        connection.close()

    mode = "APPLIED" if result["state"] == "renamed" else "DRY RUN"
    print(
        f"{mode}: {result['source']} -> {result['target']}; "
        f"state={result['state']}; active_connections={result['active_connections']}. "
        "No sessions were terminated and no row data was copied."
    )
    return 2 if result["state"] == "blocked_active_connections" else 0


if __name__ == "__main__":
    raise SystemExit(main())
