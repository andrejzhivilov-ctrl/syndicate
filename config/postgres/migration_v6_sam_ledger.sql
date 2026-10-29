-- SYNDICATE — migration v6: Sam's hash-chained, append-only ledger (29.10).
--
-- For databases created before this table existed. init.sql carries the same
-- block for fresh installs; tests/test_postgres_paths.py checks they match.
-- Idempotent: safe to apply any number of times.
--
-- Apply on the server (operator approval required):
--   docker exec -i syndicate-postgres-1 psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
--     < config/postgres/migration_v6_sam_ledger.sql

CREATE TABLE IF NOT EXISTS agents.sam_journal_ledger (
    seq         BIGSERIAL PRIMARY KEY,
    created_at  TIMESTAMPTZ NOT NULL,
    signal_id   VARCHAR(64),
    event       VARCHAR(32) NOT NULL,
    payload     JSONB NOT NULL,
    body        TEXT NOT NULL,
    prev_hash   CHAR(64) NOT NULL,
    entry_hash  CHAR(64) NOT NULL UNIQUE
);

CREATE OR REPLACE FUNCTION agents.sam_ledger_append_only()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'agents.sam_journal_ledger is append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sam_ledger_no_update ON agents.sam_journal_ledger;
CREATE TRIGGER trg_sam_ledger_no_update
    BEFORE UPDATE OR DELETE ON agents.sam_journal_ledger
    FOR EACH ROW EXECUTE FUNCTION agents.sam_ledger_append_only();
DROP TRIGGER IF EXISTS trg_sam_ledger_no_truncate ON agents.sam_journal_ledger;
CREATE TRIGGER trg_sam_ledger_no_truncate
    BEFORE TRUNCATE ON agents.sam_journal_ledger
    FOR EACH STATEMENT EXECUTE FUNCTION agents.sam_ledger_append_only();

REVOKE UPDATE, DELETE, TRUNCATE ON agents.sam_journal_ledger FROM eva_agent;
GRANT SELECT, INSERT ON agents.sam_journal_ledger TO eva_agent;
GRANT USAGE ON SEQUENCE agents.sam_journal_ledger_seq_seq TO eva_agent;
