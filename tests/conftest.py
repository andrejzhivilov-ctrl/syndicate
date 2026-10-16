"""Shared pytest fixtures for the SYNDICATE test suite.

The important one is :func:`live_pg` — it provides a **real** PostgreSQL +
pgvector database with ``config/postgres/init.sql`` applied, so the SQL branches
that carry ``# pragma: no cover`` can actually be exercised. See
``tests/live_pg.py`` for how the server is obtained (CI service container or the
bundled ``pgserver`` dev dependency) and why ``EVA_REQUIRE_LIVE_DB=1`` exists.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = Path(__file__).resolve().parent
for _path in (str(REPO_ROOT), str(TESTS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)


@pytest.fixture(scope="session")
def live_pg():
    """A live PostgreSQL with the syndicate schema applied, or a skip.

    The fixture is session-scoped and read-only with respect to the schema
    (``init.sql``/``migration_v4.sql`` are idempotent by design), so tests share
    it. Each test uses its own identifiers instead of cleaning shared tables.
    """
    from live_pg import LivePostgresUnavailable, start_live_postgres

    try:
        handle = start_live_postgres()
    except LivePostgresUnavailable as exc:
        # EVA_REQUIRE_LIVE_DB=1 was set and the environment could not deliver:
        # that must fail the run, never skip.
        raise AssertionError(f"live PostgreSQL required but unavailable: {exc}") from exc

    if handle is None:
        if os.getenv("EVA_REQUIRE_LIVE_DB", "").strip().lower() in {"1", "true", "yes", "on"}:
            raise AssertionError("live PostgreSQL required but unavailable (no DSN, no pgserver)")
        pytest.skip(
            "no live PostgreSQL: set EVA_TEST_DATABASE_URL or install pgserver "
            "(see requirements-dev.txt) — SQL paths stay unverified in this run"
        )

    try:
        yield handle
    finally:
        handle.close()
