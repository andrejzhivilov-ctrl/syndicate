"""Live PostgreSQL + pgvector tests — the SQL paths that used to be unreachable.

Every SQL branch in ``src/`` carried ``# pragma: no cover - needs live DB`` and
was only compared *statically* against ``config/postgres/init.sql``. Applying the
schema to a real server immediately exposed defects that no static test can see:

1. ``MemoryManager.semantic_search`` and ``check_response_cache`` raised
   ``AmbiguousParameterError`` from asyncpg for ``(:agent_id IS NULL OR …)`` —
   both were broken against a real database.
2. ``init.sql`` could not be replayed (duplicate trigger) and
   ``migration_v4.sql`` could not be applied on top of it.
3. ``TradeJournal``/``DeviceTokenStore`` silently used volatile in-memory
   storage because ``MemoryManager`` never exposed the ``asyncpg`` pool they
   look for.

Run with:   .venv/bin/python -m pytest tests/test_postgres_paths.py -q
CI:         EVA_TEST_DATABASE_URL=<dsn> EVA_REQUIRE_LIVE_DB=1 (pgvector/pgvector:pg16)
No DB?:     tests skip with an explicit reason unless EVA_REQUIRE_LIVE_DB=1.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import re
import sys
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from live_pg import INIT_SQL, MIGRATION_SQL, split_sql_statements, sql_tables  # noqa: E402

VEC = 1536  # OpenAI text-embedding-3-small, the column dimension in init.sql


def _run(coro):
    return asyncio.run(coro)


def _tag(prefix: str) -> str:
    """A unique per-test identifier — the session database is shared."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _vector(axis: int) -> list:
    values = [0.0] * VEC
    values[axis] = 1.0
    return values


def _init_tables() -> list:
    return sorted(sql_tables(INIT_SQL.read_text(encoding="utf-8")))


def _init_indexes() -> list:
    text = INIT_SQL.read_text(encoding="utf-8")
    return sorted(set(re.findall(r"CREATE INDEX IF NOT EXISTS\s+([\w.]+)", text)))


async def _memory(pg):
    """An initialized MemoryManager bound to the live database (Redis disabled)."""
    from src.memory import MemoryManager

    manager = MemoryManager(postgres_dsn=pg.sqlalchemy_dsn, redis_url="")
    await manager.initialize()
    return manager


# ─────────────────────────────────────────────────────────────────────────────
# SQL statement splitting (no database needed)
# ─────────────────────────────────────────────────────────────────────────────
class TestSqlScriptSplitting:
    def test_dollar_quoted_do_block_is_one_statement(self):
        """``DO $$ … ; … $$`` contains semicolons — a naive split breaks it."""
        statements = split_sql_statements(
            "CREATE TABLE t (id int);\n"
            "DO $$\nBEGIN\n    IF NOT EXISTS (SELECT 1) THEN\n        CREATE ROLE r;\n    END IF;\nEND\n$$;\n"
            "SELECT 1;"
        )
        assert len(statements) == 3
        assert statements[1].startswith("DO $$") and statements[1].rstrip().endswith("$$")

    def test_semicolon_inside_string_literal_is_not_a_boundary(self):
        statements = split_sql_statements("INSERT INTO t VALUES ('a; b'); SELECT 1;")
        assert len(statements) == 2
        assert statements[0].endswith("('a; b')")

    def test_comments_do_not_produce_statements(self):
        assert split_sql_statements("-- header only;\n/* block; */\nSELECT 1;") == ["SELECT 1"]

    def test_init_sql_do_block_survives_the_splitter(self):
        text = INIT_SQL.read_text(encoding="utf-8")
        assert any(statement.startswith("DO $$") for statement in split_sql_statements(text))


# ─────────────────────────────────────────────────────────────────────────────
# The schema itself, applied to a real server
# ─────────────────────────────────────────────────────────────────────────────
class TestSchemaOnLivePostgres:
    def test_schema_was_applied_without_skips_in_a_complete_cluster(self, live_pg):
        """The bundled pgserver ships only pgvector; the CI image also has
        uuid-ossp/pg_trgm. Any skipped statement must be justified by a missing
        extension, and in a complete cluster nothing may be skipped at all."""
        for statement, reason in live_pg.skipped_statements:
            assert "not available in this PostgreSQL cluster" in reason, (
                f"unexplained skipped statement: {statement[:80]}"
            )
        if not live_pg.degraded_extensions:
            assert live_pg.skipped_statements == []
            assert live_pg.notes == []

    def test_ci_image_provides_every_extension_init_sql_requests(self, live_pg):
        """init.sql asks for ``vector``, ``uuid-ossp`` and ``pg_trgm``.

        The CI image (``pgvector/pgvector:pg16``) must provide all three —
        otherwise the harness silently shims/skips statements there, and a
        "green" CI run would no longer mean the real schema was applied.
        Locally the bundled pgserver ships only ``vector``, where shimming is
        the documented, visible fallback.
        """
        require = os.getenv("EVA_REQUIRE_LIVE_DB", "").strip().lower() in {"1", "true", "yes", "on"}
        if not require:
            pytest.skip("only enforced for the CI database image (EVA_REQUIRE_LIVE_DB=1)")
        requested = set(
            re.findall(r'CREATE EXTENSION IF NOT EXISTS\s+"?([\w-]+)"?', INIT_SQL.read_text(encoding="utf-8"))
        )
        missing = sorted(requested - live_pg.available_extensions)
        assert not missing, f"the CI database image is missing extensions required by init.sql: {missing}"

    def test_every_table_from_init_sql_exists(self, live_pg):
        missing = [
            name for name in _init_tables()
            if live_pg.scalar("SELECT to_regclass(%s)", (name,)) is None
        ]
        assert not missing, f"init.sql declares tables the server does not have: {missing}"

    def test_every_index_from_init_sql_exists(self, live_pg):
        present = {row[0] for row in live_pg.fetch("SELECT indexname FROM pg_indexes")}
        missing = [name for name in _init_indexes() if name not in present]
        assert not missing, f"init.sql declares indexes the server does not have: {missing}"

    def test_pgvector_and_hnsw_indexes_are_real(self, live_pg):
        assert live_pg.scalar("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        hnsw = live_pg.fetch("SELECT indexdef FROM pg_indexes WHERE indexdef ILIKE '%USING hnsw%'")
        assert len(hnsw) >= 4, f"expected HNSW vector indexes, got: {hnsw}"

    def test_init_sql_can_be_replayed(self, live_pg):
        """The bootstrap script uses IF NOT EXISTS everywhere, so replaying it
        must work. It used to die on ``trigger "trg_episodes_updated" already
        exists``."""
        live_pg.apply_sql_file(INIT_SQL)

    def test_migration_replays_on_top_of_init(self, live_pg):
        """init.sql is the complete schema; 02-migration_v4.sql is the upgrade
        path for older databases. Applying it to a fresh database must be a
        no-op, not a DuplicateObject error."""
        live_pg.apply_sql_file(MIGRATION_SQL)

    def test_eva_agent_role_is_least_privilege(self, live_pg):
        role = live_pg.fetch("SELECT rolsuper, rolcanlogin FROM pg_roles WHERE rolname = 'eva_agent'")
        assert role, "init.sql must create the eva_agent role"
        assert role[0] == (False, False), "eva_agent must be NOLOGIN and not a superuser"

        def privilege(table: str, priv: str) -> bool:
            return bool(live_pg.scalar("SELECT has_table_privilege('eva_agent', %s, %s)", (table, priv)))

        # The runtime writes these tables…
        for table in ("auth.device_tokens", "agents.sam_trade_journal", "memory.episodes",
                      "agents.checkpoints", "memory.lessons"):
            assert privilege(table, "INSERT"), f"eva_agent needs INSERT on {table}"
        assert privilege("auth.device_tokens", "UPDATE")
        assert privilege("agents.sam_trade_journal", "UPDATE")
        # …but not beyond what it needs.
        assert not privilege("audit.outbound_vetoes", "SELECT"), "vetoes are write-only for the agent"
        assert not privilege("audit.decisions", "DELETE")
        assert not privilege("agents.sam_trade_journal", "DELETE"), "journal history must be append-only"
        assert not live_pg.scalar("SELECT has_schema_privilege('eva_agent', 'memory', 'CREATE')")


# ─────────────────────────────────────────────────────────────────────────────
# MemoryManager: episodes, pgvector search, response cache, checkpoints, lessons
# ─────────────────────────────────────────────────────────────────────────────
class TestMemoryManagerLiveSql:
    def test_episodes_round_trip_with_uuid5_normalisation(self, live_pg):
        agent_id, session = _tag("ep"), _tag("plain-session-id")

        async def scenario():
            memory = await _memory(live_pg)
            try:
                await memory.save_episode(
                    session_id=session, agent_id=agent_id, role="user",
                    content="обговорили бюджет", metadata={"topic": "fin"},
                )
                return await memory.get_recent_episodes(session_id=session, agent_id=agent_id)
            finally:
                await memory.close()

        rows = _run(scenario())
        assert len(rows) == 1
        assert rows[0]["content"] == "обговорили бюджет" and rows[0]["role"] == "user"
        assert rows[0]["metadata"]["topic"] == "fin", "JSONB must come back as a dict, not a string"
        # The arbitrary string session id was normalised to a deterministic UUID,
        # otherwise the UUID column would have rejected the insert.
        stored = live_pg.scalar(
            "SELECT count(*) FROM memory.episodes WHERE session_id = %s",
            (str(uuid.uuid5(uuid.NAMESPACE_DNS, session)),),
        )
        assert stored == 1

    def test_semantic_search_orders_by_cosine_distance(self, live_pg):
        """Regression: ``(:agent_id IS NULL OR …)`` made asyncpg unable to infer
        the parameter type, so semantic search always failed against a real DB."""
        agent_id = _tag("vec")

        async def scenario():
            memory = await _memory(live_pg)
            try:
                await memory.save_episode(session_id=_tag("s"), agent_id=agent_id,
                                          content="alpha", embedding=_vector(0))
                await memory.save_episode(session_id=_tag("s"), agent_id=agent_id,
                                          content="beta", embedding=_vector(1))
                scoped = await memory.semantic_search(
                    query_embedding=_vector(0), agent_id=agent_id, min_similarity=0.7
                )
                unscoped = await memory.semantic_search(query_embedding=_vector(0), min_similarity=0.0)
                return scoped, unscoped
            finally:
                await memory.close()

        scoped, unscoped = _run(scenario())
        assert [row["content"] for row in scoped] == ["alpha"], "orthogonal vector must miss the 0.7 cut"
        assert scoped[0]["similarity"] == pytest.approx(1.0, abs=1e-6)
        assert any(row["agent_id"] == agent_id for row in unscoped), "agent_id=None must not raise"

    def test_response_cache_hit_and_miss(self, live_pg):
        """Regression: the response cache had the same asyncpg parameter bug as
        semantic search — token savings never worked against PostgreSQL."""
        agent_id = _tag("cache")

        async def scenario():
            memory = await _memory(live_pg)
            try:
                await memory.cache_response(
                    query_text="скільки грошей на рахунку?", query_embedding=_vector(0),
                    response_text="cached answer", agent_id=agent_id, tokens_saved=42,
                )
                hit = await memory.check_response_cache(query_embedding=_vector(0), agent_id=agent_id)
                miss = await memory.check_response_cache(query_embedding=_vector(1), agent_id=agent_id)
                return hit, miss
            finally:
                await memory.close()

        hit, miss = _run(scenario())
        assert hit is not None and hit["response"] == "cached answer" and hit["tokens_saved"] == 42
        assert miss is None, "an orthogonal query must not hit the cache"
        assert live_pg.scalar(
            "SELECT hit_count FROM memory.response_cache WHERE agent_id = %s", (agent_id,)
        ) == 1

    def test_checkpoint_is_upserted(self, live_pg):
        thread_id = _tag("thread")

        async def scenario():
            memory = await _memory(live_pg)
            try:
                await memory.save_checkpoint(thread_id, "cp-1", "eva", {"step": 1})
                await memory.save_checkpoint(thread_id, "cp-1", "eva", {"step": 2})
                return await memory.load_checkpoint(thread_id, "cp-1"), await memory.load_checkpoint(thread_id)
            finally:
                await memory.close()

        exact, latest = _run(scenario())
        assert exact == {"step": 2}, "ON CONFLICT … DO UPDATE must overwrite the checkpoint"
        assert latest == {"step": 2}

    def test_pool_is_exposed_for_dollar_placeholder_components(self, live_pg):
        """TradeJournal/DeviceTokenStore probe ``memory.pool``/``_pool``/``db_pool``.

        Without a real pool they silently degrade to memory-only storage: the
        tables stay empty and every restart loses device tokens and lessons."""
        from src.agents.sam.journal import TradeJournal
        from src.device_auth import DeviceTokenStore

        async def scenario():
            memory = await _memory(live_pg)
            try:
                return memory.pool, TradeJournal(memory=memory)._pool(), DeviceTokenStore(memory=memory)._pool()
            finally:
                await memory.close()

        pool, journal_pool, device_pool = _run(scenario())
        assert pool is not None, "MemoryManager must own an asyncpg pool"
        assert journal_pool is pool
        assert device_pool is pool

    def test_lessons_store_round_trip_and_vector_search(self, live_pg):
        from src.lessons import LessonsStore

        agent_id = _tag("lessons")

        async def scenario():
            memory = await _memory(live_pg)
            try:
                store = LessonsStore(session_factory=memory._session_factory)
                lesson_id = await store.record_lesson(
                    agent_id=agent_id, kind="warning", summary="не публікувати без HITL",
                    severity="high", embedding=_vector(0),
                )
                hits = await store.check_before_action(agent_id=agent_id, action_embedding=_vector(0))
                listed = await store.get_agent_lessons(agent_id=agent_id)
                return lesson_id, hits, listed
            finally:
                await memory.close()

        lesson_id, hits, listed = _run(scenario())
        assert lesson_id, "record_lesson must return the row id"
        assert [row["summary"] for row in listed] == ["не публікувати без HITL"]
        matched = [row for row in hits if row["id"] == lesson_id]
        assert matched and matched[0]["similarity"] == pytest.approx(1.0, abs=1e-6)


# ─────────────────────────────────────────────────────────────────────────────
# Sam's trade journal — the SQL branch, including the symbol filter
# ─────────────────────────────────────────────────────────────────────────────
class TestTradeJournalLiveSql:
    @staticmethod
    def _entry(signal_id: str, symbol: str):
        from src.agents.sam.journal import JournalEntry

        return JournalEntry(
            signal_id=signal_id, symbol=symbol, direction="long", confluence_score=96.5,
            threshold=95.0, venue="binance", entry_price=61234.5, stop_loss=60500.0,
            take_profit=63000.0, risk_pct=1.0, position_size=0.02, layers={"smc": 1.0},
        )

    def test_signal_is_persisted_to_postgres(self, live_pg):
        from src.agents.sam.journal import TradeJournal

        signal_id = _tag("SIG")

        async def scenario():
            memory = await _memory(live_pg)
            try:
                journal = TradeJournal(memory=memory)
                await journal.record_signal(self._entry(signal_id, "BTCUSDT"))
                return await journal.get_signal(signal_id)
            finally:
                await memory.close()

        row = _run(scenario())
        assert row is not None, "record_signal must write through to agents.sam_trade_journal"
        assert row["symbol"] == "BTCUSDT" and row["status"] == "proposed"
        assert live_pg.scalar(
            "SELECT count(*) FROM agents.sam_trade_journal WHERE signal_id = %s", (signal_id,)
        ) == 1

    def test_negative_constraint_is_scoped_to_its_symbol(self, live_pg):
        """Backlog #16: the symbol filter lives in the SQL branch and was never
        tested. Without it a lesson learned on one symbol gated all others."""
        from src.agents.sam.journal import TradeJournal

        signal_id = _tag("SIG")
        symbol = _tag("BTC").upper()

        async def scenario():
            memory = await _memory(live_pg)
            try:
                journal = TradeJournal(memory=memory)
                await journal.record_signal(self._entry(signal_id, symbol))
                await journal.record_decision(
                    signal_id, "reject", by="andrii", reason="spread too wide",
                    symbol=symbol, direction="long",
                )
                return (
                    await journal.negative_constraints(symbol=symbol),
                    await journal.negative_constraints(symbol="ETHUSDT"),
                    await journal.negative_constraints(),
                )
            finally:
                await memory.close()

        for_symbol, for_other, all_constraints = _run(scenario())
        assert [row["summary"] for row in for_symbol] == [f"{symbol}:long — spread too wide"]
        assert for_other == [], "a constraint from another symbol must not leak into the gate"
        assert any(row["signal_id"] == signal_id for row in all_constraints)
        assert live_pg.scalar(
            "SELECT count(*) FROM agents.sam_reflections WHERE kind = 'negative_constraint' "
            "AND signal_id = %s", (signal_id,)
        ) == 1

    def test_approval_outcome_and_realised_stats(self, live_pg):
        from src.agents.sam.journal import TradeJournal

        signal_id = _tag("SIG")

        async def scenario():
            memory = await _memory(live_pg)
            try:
                journal = TradeJournal(memory=memory)
                await journal.record_signal(self._entry(signal_id, "ETHUSDT"))
                await journal.record_decision(signal_id, "approve", by="andrii")
                await journal.record_outcome(signal_id, "win", realized_r=2.4)
                return await journal.get_signal(signal_id), await journal.performance_stats()
            finally:
                await memory.close()

        row, stats = _run(scenario())
        assert row["status"] == "closed", "record_outcome must close the trade"
        stored = live_pg.fetch(
            "SELECT hitl_decision, hitl_by, outcome, realized_r FROM agents.sam_trade_journal "
            "WHERE signal_id = %s", (signal_id,)
        )
        assert stored[0][:3] == ("approve", "andrii", "win"), "the HITL approval must be persisted"
        assert float(stored[0][3]) == pytest.approx(2.4)
        assert stats["sample"] >= 1 and stats["wins"] >= 1
        assert stats["realized_win_rate"] <= 1.0, "realised stats only, never a projection"


# ─────────────────────────────────────────────────────────────────────────────
# Per-device tokens — the SQL branch
# ─────────────────────────────────────────────────────────────────────────────
class TestDeviceTokenStoreLiveSql:
    @staticmethod
    async def _store(pg, **kwargs):
        from src.device_auth import DeviceTokenStore

        memory = await _memory(pg)
        return memory, DeviceTokenStore(memory=memory, default_ttl_seconds=3600, **kwargs)

    def test_enroll_stores_only_the_hash(self, live_pg):
        device_id = _tag("device")

        async def scenario():
            memory, store = await self._store(live_pg)
            try:
                issued = await store.enroll(device_id, label="probe", scopes=["read"])
                return issued, await store.verify(issued["token"], required_scope="read")
            finally:
                await memory.close()

        issued, verified = _run(scenario())
        assert verified is not None and verified.device_id == device_id
        assert verified.scopes == ["read"], "JSONB scopes must round-trip as a list"
        token_id, _, secret = issued["token"].partition(".")
        stored = live_pg.fetch(
            "SELECT secret_hash, scopes FROM auth.device_tokens WHERE token_id = %s", (token_id,)
        )
        assert stored, "the token row must be in auth.device_tokens, not only in memory"
        assert stored[0][0] == hashlib.sha256(secret.encode()).hexdigest()
        assert live_pg.scalar(
            "SELECT count(*) FROM auth.device_tokens WHERE token_id = %s AND secret_hash = %s",
            (token_id, issued["token"]),
        ) == 0, "the plaintext token must never be stored"

    def test_scope_enforcement_and_last_seen_touch(self, live_pg):
        device_id = _tag("device")

        async def scenario():
            memory, store = await self._store(live_pg)
            try:
                issued = await store.enroll(device_id, scopes=["read"])
                allowed = await store.verify(issued["token"], required_scope="read")
                denied = await store.verify(issued["token"], required_scope="hitl")
                unknown = await store.verify("deadbeef.not-a-secret")
                return issued, allowed, denied, unknown
            finally:
                await memory.close()

        issued, allowed, denied, unknown = _run(scenario())
        assert allowed is not None, "a read-scoped token must verify for read"
        assert denied is None, "a read-only device token must not approve HITL changes"
        assert unknown is None
        assert live_pg.scalar(
            "SELECT last_seen_at IS NOT NULL FROM auth.device_tokens WHERE token_id = %s",
            (issued["token_id"],),
        ) is True, "verify must persist last_seen_at"

    def test_refresh_rotates_and_revokes_the_old_token(self, live_pg):
        device_id = _tag("device")

        async def scenario():
            memory, store = await self._store(live_pg)
            try:
                first = await store.enroll(device_id, scopes=["read"])
                rotated = await store.refresh(first["token"])
                return first, rotated, await store.verify(first["token"])
            finally:
                await memory.close()

        first, rotated, old_token = _run(scenario())
        assert rotated is not None and rotated["token"] != first["token"]
        assert old_token is None, "the rotated token must stop working"
        assert live_pg.scalar(
            "SELECT revoked_at IS NOT NULL FROM auth.device_tokens WHERE token_id = %s",
            (first["token_id"],),
        ) is True, "revocation must be persisted, not only kept in memory"

    def test_revoke_is_persisted_and_listed(self, live_pg):
        device_id = _tag("device")

        async def scenario():
            memory, store = await self._store(live_pg)
            try:
                issued = await store.enroll(device_id, scopes=["read"])
                revoked = await store.revoke(issued["token_id"])
                return issued, revoked, await store.list_devices(), await store.verify(issued["token"])
            finally:
                await memory.close()

        issued, revoked, listed, after = _run(scenario())
        assert revoked is True and after is None
        assert any(row["token_id"] == issued["token_id"] for row in listed), "list_devices reads PostgreSQL"

    def test_purge_expired_removes_only_dead_rows(self, live_pg):
        device_id, stale_id = _tag("device"), _tag("stale")
        live_pg.execute(
            "INSERT INTO auth.device_tokens (token_id, secret_hash, device_id, label, scopes, expires_at) "
            "VALUES (%s, %s, %s, 'stale', '[]', NOW() - INTERVAL '30 days')",
            (stale_id, "0" * 64, device_id),
        )

        async def scenario():
            memory, store = await self._store(live_pg)
            try:
                issued = await store.enroll(device_id, scopes=["read"])
                return issued, await store.purge_expired(older_than_seconds=7 * 24 * 3600)
            finally:
                await memory.close()

        issued, purged = _run(scenario())
        assert purged >= 1, "a token dead for 30 days must be swept"
        assert live_pg.scalar(
            "SELECT count(*) FROM auth.device_tokens WHERE token_id = %s", (stale_id,)
        ) == 0
        assert live_pg.scalar(
            "SELECT count(*) FROM auth.device_tokens WHERE token_id = %s", (issued["token_id"],)
        ) == 1, "a live token must survive the sweep"
