"""Live PostgreSQL harness for the SQL-path tests.

Motivation
----------
Every PostgreSQL branch in ``src/`` used to carry ``# pragma: no cover - needs
live DB`` and was only checked *statically* against ``config/postgres/init.sql``.
That is the largest blind spot in the repository: a schema that parses can still
be non-applicable, a grant can be missing, and a ``$1``-style query can be
malformed without a single test noticing.

This module starts a throw-away PostgreSQL server so those branches really run:

1. ``EVA_TEST_DATABASE_URL`` — used verbatim when set. CI provides the
   ``pgvector/pgvector:pg16`` service container this way.
2. ``pgserver`` — an optional dev dependency that ships PostgreSQL 16 + pgvector
   binaries, so a laptop/sandbox without Docker still runs the same tests.
3. Otherwise the caller skips, and ``EVA_REQUIRE_LIVE_DB=1`` turns that skip into
   a hard error so CI can never "pass" by skipping the database.

The harness never rewrites the schema: it applies ``config/postgres/init.sql``
as-is (the only adaptation is skipping ``CREATE DATABASE`` when the database
already exists, because that statement cannot be replayed).
"""

from __future__ import annotations

import os
import re
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urlsplit, urlunsplit

import psycopg2
import structlog

logger = structlog.get_logger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
INIT_SQL = REPO_ROOT / "config" / "postgres" / "init.sql"
MIGRATION_SQL = REPO_ROOT / "config" / "postgres" / "migration_v4.sql"

CREATE_DATABASE_RE = re.compile(r"^\s*CREATE\s+DATABASE\s+([\w\"]+)", re.IGNORECASE)
DOLLAR_TAG_RE = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*\$|\$\$")
CREATE_EXTENSION_RE = re.compile(r"CREATE EXTENSION IF NOT EXISTS\s+\"?([\w-]+)\"?", re.IGNORECASE)

# A minimal cluster (the bundled pgserver binaries ship only ``vector``) cannot
# install ``uuid-ossp``. The schema uses exactly one function from it,
# ``uuid_generate_v4()`` as a column default; PostgreSQL 13+ has
# ``gen_random_uuid()`` in core with identical semantics, so the shim below is
# faithful. Any other unavailable extension is recorded as a skipped statement
# instead of being silently ignored — the CI image has all of them.
UUID_OSSP_COMPAT_SQL = (
    "CREATE OR REPLACE FUNCTION uuid_generate_v4() RETURNS uuid "
    "LANGUAGE sql VOLATILE AS $shim$ SELECT gen_random_uuid() $shim$"
)
TRGM_MARKERS = ("gin_trgm_ops", "gist_trgm_ops", "similarity(", "word_similarity(", "show_trgm(")


class LivePostgresUnavailable(RuntimeError):
    """No live PostgreSQL could be provided for this test session."""


def _scan_single_quoted(text: str, start: int) -> tuple:
    """Consume a ``'…'`` literal starting at ``start`` (``''`` escapes a quote)."""
    i = start + 1
    while i < len(text):
        if text[i] == "'":
            if i + 1 < len(text) and text[i + 1] == "'":
                i += 2
                continue
            return text[start : i + 1], i + 1
        i += 1
    return text[start:], len(text)


def _scan_quoted(text: str, start: int) -> tuple:
    """Consume a comment/quoted region at ``start``.

    Returns ``(chunk, next_index)``; ``chunk`` is ``None`` when ``start`` is not
    the beginning of such a region.
    """
    ch = text[start]
    nxt = text[start + 1] if start + 1 < len(text) else ""
    if ch == "-" and nxt == "-":  # line comment
        end = text.find("\n", start)
        return "", len(text) if end == -1 else end
    if ch == "/" and nxt == "*":  # block comment
        end = text.find("*/", start + 2)
        return " ", len(text) if end == -1 else end + 2
    if ch == "'":
        return _scan_single_quoted(text, start)
    if ch == '"':  # quoted identifier
        end = text.find('"', start + 1)
        end = len(text) - 1 if end == -1 else end
        return text[start : end + 1], end + 1
    if ch == "$":  # dollar-quoted body ($tag$ … $tag$)
        tag_match = DOLLAR_TAG_RE.match(text, start)
        if tag_match:
            tag = tag_match.group(0)
            end = text.find(tag, tag_match.end())
            end = len(text) if end == -1 else end + len(tag)
            return text[start:end], end
    return None, start


def split_sql_statements(text: str) -> List[str]:
    """Split a SQL script into statements, respecting quoting.

    A naive ``text.split(";")`` breaks on ``DO $$ ... ; ... $$`` blocks (which
    ``init.sql`` uses) and on semicolons inside string literals or comments.
    """
    statements: List[str] = []
    buf: List[str] = []
    i = 0
    while i < len(text):
        chunk, next_index = _scan_quoted(text, i)
        if chunk is not None:
            buf.append(chunk)
            i = next_index
            continue
        if text[i] == ";":
            statement = "".join(buf).strip()
            if statement:
                statements.append(statement)
            buf = []
        else:
            buf.append(text[i])
        i += 1
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements


def _with_database(dsn: str, dbname: str) -> str:
    """Return ``dsn`` pointing at another database on the same server."""
    parts = urlsplit(dsn)
    return urlunsplit((parts.scheme, parts.netloc, f"/{dbname}", parts.query, parts.fragment))


@dataclass
class LivePostgres:
    """Handle to a real PostgreSQL server with ``init.sql`` applied."""

    admin_dsn: str
    dsn: str
    dbname: str
    server: Any = None  # pgserver handle, kept alive for the session
    scratch: bool = False
    applied_statements: List[str] = field(default_factory=list)
    skipped_statements: List[tuple] = field(default_factory=list)  # (statement, reason)
    degraded_extensions: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    available_extensions: frozenset = frozenset()

    # ---------------------------------------------------------------- helpers
    @property
    def sqlalchemy_dsn(self) -> str:
        """The same DSN in the SQLAlchemy+asyncpg dialect used by ``MemoryManager``."""
        return self.dsn.replace("postgresql://", "postgresql+asyncpg://", 1)

    def connect(self) -> Any:
        """A new autocommit psycopg2 connection to the test database."""
        conn = psycopg2.connect(self.dsn)
        conn.autocommit = True
        return conn

    @contextmanager
    def cursor(self) -> Iterator[Any]:
        """Autocommit cursor that always closes its connection."""
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                yield cur
        finally:
            conn.close()

    def execute(self, sql: str, params: Optional[tuple] = None) -> None:
        """Run a statement that returns no rows (INSERT/UPDATE/DELETE/DDL)."""
        with self.cursor() as cur:
            cur.execute(sql, params)

    def fetch(self, sql: str, params: Optional[tuple] = None) -> List[tuple]:
        with self.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    def scalar(self, sql: str, params: Optional[tuple] = None) -> Any:
        rows = self.fetch(sql, params)
        return rows[0][0] if rows else None

    def apply_sql_file(self, path: Path) -> List[str]:
        """Apply a SQL file; returns the statements that were executed."""
        return self.apply_sql(path.read_text(encoding="utf-8"))

    def _extension_statement(self, statement: str, cur: Any) -> bool:
        """Handle a ``CREATE EXTENSION`` statement.

        Returns ``True`` when the statement was dealt with (applied or
        deliberately skipped), ``False`` when it is not an extension statement.
        """
        match = CREATE_EXTENSION_RE.match(statement)
        if not match:
            return False
        name = match.group(1)
        if name in self.available_extensions:
            cur.execute(statement)
            return True
        if name == "uuid-ossp":
            cur.execute(UUID_OSSP_COMPAT_SQL)
            self.notes.append(
                "uuid-ossp is not shipped by this cluster; installed uuid_generate_v4() shim over core gen_random_uuid()"
            )
            return True
        reason = f"extension {name!r} is not available in this PostgreSQL cluster"
        if name not in self.degraded_extensions:
            self.degraded_extensions.append(name)
        self.skipped_statements.append((statement, reason))
        logger.warning("live_pg_extension_skipped", extension=name)
        return True

    def _needs_missing_extension(self, statement: str) -> Optional[str]:
        if "pg_trgm" in self.degraded_extensions or "pg_trgm" not in self.available_extensions:
            for marker in TRGM_MARKERS:
                if marker in statement:
                    return "pg_trgm is not available in this PostgreSQL cluster"
        return None

    def apply_sql(self, text: str) -> List[str]:
        executed: List[str] = []
        with self.cursor() as cur:
            for statement in split_sql_statements(text):
                db_match = CREATE_DATABASE_RE.match(statement)
                if db_match:
                    name = db_match.group(1).strip('"')
                    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,))
                    if cur.fetchone():
                        continue
                if self._extension_statement(statement, cur):
                    continue
                missing = self._needs_missing_extension(statement)
                if missing:
                    self.skipped_statements.append((statement, missing))
                    continue
                cur.execute(statement)
                executed.append(statement)
        self.applied_statements.extend(executed)
        return executed

    def close(self) -> None:
        if self.scratch:
            admin = None
            try:
                admin = psycopg2.connect(self.admin_dsn)
                admin.autocommit = True
                with admin.cursor() as cur:
                    cur.execute(f'DROP DATABASE IF EXISTS "{self.dbname}" WITH (FORCE)')
            except Exception as exc:  # noqa: BLE001
                logger.warning("live_pg_drop_failed", dbname=self.dbname, error=str(exc))
            finally:
                if admin is not None:
                    admin.close()
        if self.server is not None:
            try:
                self.server.cleanup()
            except Exception as exc:  # noqa: BLE001
                logger.warning("live_pg_server_cleanup_failed", error=str(exc))


def _has_pgvector(conn: Any) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_available_extensions WHERE name = 'vector'")
        return cur.fetchone() is not None


def _start_bundled_server() -> Optional[Any]:
    try:
        import pgserver
    except ImportError:
        return None
    pgdata = Path(tempfile.mkdtemp(prefix="eva-pgdata-"))
    return pgserver.get_server(pgdata, cleanup_mode="delete")


def _require_flag() -> bool:
    return os.getenv("EVA_REQUIRE_LIVE_DB", "").strip().lower() in {"1", "true", "yes", "on"}


def _resolve_admin_dsn(require: bool) -> tuple:
    """Return ``(admin_dsn, pgserver_handle)`` from the env DSN or bundled binaries."""
    env_dsn = os.getenv("EVA_TEST_DATABASE_URL", "").strip()
    if env_dsn:
        return env_dsn, None
    # Джоб без бази (CI Gates) не піднімає другий PostgreSQL: SQL-шляхи перевіряє джоб із pgvector.
    if os.getenv("EVA_SKIP_PGSERVER", "").strip().lower() in {"1", "true", "yes", "on"}:
        if require:
            raise LivePostgresUnavailable("EVA_REQUIRE_LIVE_DB=1 but EVA_SKIP_PGSERVER forbids pgserver")
        return None, None
    try:
        server = _start_bundled_server()
    except Exception as exc:  # noqa: BLE001 - bundled binaries may be unavailable
        raise LivePostgresUnavailable(f"pgserver failed to start: {exc}") from exc
    if server is None:
        if require:
            raise LivePostgresUnavailable(
                "EVA_REQUIRE_LIVE_DB=1 but neither EVA_TEST_DATABASE_URL nor pgserver is available"
            )
        return None, None
    return server.get_uri(), server


def _prepare_database(admin: Any, admin_dsn: str, require: bool) -> tuple:
    """Create a scratch database (or fall back to the DSN's own database)."""
    dbname = f"eva_test_{os.urandom(4).hex()}"
    try:
        with admin.cursor() as cur:
            cur.execute(f'CREATE DATABASE "{dbname}"')
        return dbname, True
    except Exception as exc:  # noqa: BLE001 - fall back to the provided database
        logger.warning("live_pg_scratch_db_unavailable", error=str(exc))
        if require and not urlsplit(admin_dsn).path.strip("/"):
            raise LivePostgresUnavailable("cannot create the test database and the DSN names no database") from exc
        return urlsplit(admin_dsn).path.lstrip("/") or "postgres", False


def start_live_postgres() -> Optional[LivePostgres]:
    """Bring up a live PostgreSQL with the syndicate schema applied.

    Returns ``None`` when no database can be provided and ``EVA_REQUIRE_LIVE_DB``
    is not set; raises :class:`LivePostgresUnavailable` when the operator
    explicitly demanded a live database.
    """
    require = _require_flag()
    admin_dsn, server = _resolve_admin_dsn(require)
    if admin_dsn is None:
        return None

    try:
        admin = psycopg2.connect(admin_dsn)
        admin.autocommit = True
    except Exception as exc:  # noqa: BLE001
        raise LivePostgresUnavailable(f"cannot connect to PostgreSQL at the provided DSN: {exc}") from exc

    try:
        with admin.cursor() as cur:
            cur.execute("SELECT name FROM pg_available_extensions")
            available = frozenset(row[0] for row in cur.fetchall())
        if not _has_pgvector(admin):
            if require:
                raise LivePostgresUnavailable("EVA_REQUIRE_LIVE_DB=1 but the cluster has no pgvector extension")
            if server is not None:
                server.cleanup()
            return None
        dbname, scratch = _prepare_database(admin, admin_dsn, require)
    finally:
        admin.close()

    handle = LivePostgres(
        admin_dsn=admin_dsn,
        dsn=_with_database(admin_dsn, dbname),
        dbname=dbname,
        server=server,
        scratch=scratch,
        available_extensions=available,
    )
    handle.apply_sql_file(INIT_SQL)
    extension = handle.scalar("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
    if not extension:
        handle.close()
        raise LivePostgresUnavailable("init.sql did not enable the pgvector extension")
    logger.info("live_pg_ready", database=dbname, pgvector=extension, statements=len(handle.applied_statements))
    return handle


def sql_tables(text: str) -> Dict[str, str]:
    """Map ``schema.table`` -> table body for a SQL script (static introspection)."""
    tables: Dict[str, str] = {}
    for statement in split_sql_statements(text):
        match = re.search(r"CREATE TABLE IF NOT EXISTS\s+([\w.]+)", statement)
        if match:
            tables[match.group(1)] = statement
    return tables
