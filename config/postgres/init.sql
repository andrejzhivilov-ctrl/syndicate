-- SYNDICATE PostgreSQL Initialization
-- Requires: pgvector extension (image: pgvector/pgvector:pg16)

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create n8n database
CREATE DATABASE n8n;

-- ============================================================
-- SCHEMA: Agent Memory System
-- ============================================================

CREATE SCHEMA IF NOT EXISTS memory;
CREATE SCHEMA IF NOT EXISTS agents;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS auth;

-- ============================================================
-- TABLE: Episodic Memory (conversation history + agent events)
-- ============================================================

CREATE TABLE IF NOT EXISTS memory.episodes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id      UUID NOT NULL,
    agent_id        VARCHAR(64) NOT NULL,
    role            VARCHAR(16) NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content         TEXT NOT NULL,
    content_vector  vector(1024),  -- BAAI/bge-m3 dense (self-hosted, see src/embeddings.py)
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for episodic memory
CREATE INDEX IF NOT EXISTS idx_episodes_session ON memory.episodes (session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_episodes_agent ON memory.episodes (agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_episodes_metadata ON memory.episodes USING GIN (metadata);

-- HNSW index for vector similarity search (fast ANN)
CREATE INDEX IF NOT EXISTS idx_episodes_vector_hnsw
    ON memory.episodes
    USING hnsw (content_vector vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ============================================================
-- TABLE: Semantic Memory (long-term facts and knowledge)
-- ============================================================

CREATE TABLE IF NOT EXISTS memory.semantic (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id    VARCHAR(64) NOT NULL,
    category    VARCHAR(128) NOT NULL,
    content     TEXT NOT NULL,
    content_vector vector(1024),
    confidence  FLOAT DEFAULT 1.0,
    source      VARCHAR(256),
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_semantic_agent_category ON memory.semantic (agent_id, category);
CREATE INDEX IF NOT EXISTS idx_semantic_vector_hnsw
    ON memory.semantic
    USING hnsw (content_vector vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ============================================================
-- TABLE: Agent State (LangGraph checkpoint storage)
-- ============================================================

CREATE TABLE IF NOT EXISTS agents.checkpoints (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id       VARCHAR(256) NOT NULL,
    checkpoint_id   VARCHAR(256) NOT NULL,
    agent_id        VARCHAR(64) NOT NULL,
    state_data      JSONB NOT NULL,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (thread_id, checkpoint_id)
);

CREATE INDEX IF NOT EXISTS idx_checkpoints_thread ON agents.checkpoints (thread_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_checkpoints_agent ON agents.checkpoints (agent_id, created_at DESC);

-- ============================================================
-- TABLE: Task Queue (distributed task management)
-- ============================================================

CREATE TABLE IF NOT EXISTS agents.tasks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_type       VARCHAR(128) NOT NULL,
    assigned_agent  VARCHAR(64),
    status          VARCHAR(32) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    priority        INTEGER DEFAULT 5,
    payload         JSONB NOT NULL DEFAULT '{}',
    result          JSONB,
    error_message   TEXT,
    retry_count     INTEGER DEFAULT 0,
    max_retries     INTEGER DEFAULT 3,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    scheduled_for   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_status_priority ON agents.tasks (status, priority DESC, scheduled_for ASC);
CREATE INDEX IF NOT EXISTS idx_tasks_agent ON agents.tasks (assigned_agent, status);

-- ============================================================
-- TABLE: Audit Log (security events)
-- ============================================================

CREATE TABLE IF NOT EXISTS audit.events (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type  VARCHAR(128) NOT NULL,
    actor       VARCHAR(256) NOT NULL,
    resource    VARCHAR(256),
    action      VARCHAR(128) NOT NULL,
    outcome     VARCHAR(32) NOT NULL CHECK (outcome IN ('success', 'failure', 'blocked')),
    details     JSONB DEFAULT '{}',
    ip_address  INET,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit.events (event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit.events (actor, created_at DESC);

-- ============================================================
-- TABLE: Integration audit log (third-party connector calls)
-- ============================================================

CREATE TABLE IF NOT EXISTS audit.integration_audit_log (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connector     VARCHAR(64) NOT NULL,      -- google_workspace, telegram, mcp, ...
    operation     VARCHAR(128) NOT NULL,     -- gmail.create_draft, calendar.create_event, ...
    actor_agent   VARCHAR(64),               -- which agent initiated the call
    request_meta  JSONB DEFAULT '{}',        -- non-sensitive request context (never secrets)
    status        VARCHAR(32) NOT NULL CHECK (status IN ('success', 'failure', 'rate_limited', 'blocked')),
    latency_ms    INTEGER,
    error_message TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_integration_connector ON audit.integration_audit_log (connector, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_integration_agent ON audit.integration_audit_log (actor_agent, created_at DESC);

-- ============================================================
-- TABLE: Voice events (TTS / STT usage across agents)
-- ============================================================

CREATE TABLE IF NOT EXISTS audit.voice_events (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent         VARCHAR(64),               -- agent that produced/consumed audio
    direction     VARCHAR(8) NOT NULL CHECK (direction IN ('tts', 'stt')),
    provider      VARCHAR(64) NOT NULL,      -- elevenlabs, xai, openai, whisper, groq
    text_chars    INTEGER,                   -- characters synthesized / transcribed
    audio_bytes   INTEGER,
    latency_ms    INTEGER,
    status        VARCHAR(32) NOT NULL CHECK (status IN ('success', 'failure')),
    error_message TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_voice_provider ON audit.voice_events (provider, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_voice_agent ON audit.voice_events (agent, created_at DESC);

-- ============================================================
-- TABLE: Sam quant trade journal (self-learning)
-- ============================================================

CREATE TABLE IF NOT EXISTS agents.sam_trade_journal (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_id         VARCHAR(64) UNIQUE NOT NULL,
    symbol            VARCHAR(32) NOT NULL,
    venue             VARCHAR(32),            -- mt5, ibkr, binance, bybit, ...
    direction         VARCHAR(8) NOT NULL CHECK (direction IN ('long', 'short')),
    confluence_score  NUMERIC(5,2) NOT NULL,  -- 0-100 weighted confluence
    threshold         NUMERIC(5,2) NOT NULL,  -- gating threshold at decision time
    layers            JSONB NOT NULL DEFAULT '{}',   -- per-layer scores & rationale
    entry_price       NUMERIC(20,8),
    stop_loss         NUMERIC(20,8),
    take_profit       NUMERIC(20,8),
    risk_pct          NUMERIC(6,3),
    position_size     NUMERIC(20,8),
    status            VARCHAR(32) NOT NULL DEFAULT 'proposed'
                      CHECK (status IN ('proposed', 'approved', 'rejected', 'expired', 'open', 'closed')),
    hitl_decision     VARCHAR(32),            -- approve / reject / null (pending)
    hitl_by           VARCHAR(128),
    outcome           VARCHAR(16) CHECK (outcome IN ('win', 'loss', 'breakeven', 'scratch')),
    realized_r        NUMERIC(10,3),          -- realized reward in R multiples
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_at        TIMESTAMPTZ,
    closed_at         TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_sam_journal_symbol ON agents.sam_trade_journal (symbol, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sam_journal_status ON agents.sam_trade_journal (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sam_journal_outcome ON agents.sam_trade_journal (outcome, created_at DESC);

-- ============================================================
-- TABLE: Sam reflections (post-trade learning / negative constraints)
-- ============================================================

CREATE TABLE IF NOT EXISTS agents.sam_reflections (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_id      VARCHAR(64) REFERENCES agents.sam_trade_journal (signal_id) ON DELETE SET NULL,
    kind           VARCHAR(32) NOT NULL DEFAULT 'lesson'
                   CHECK (kind IN ('lesson', 'negative_constraint', 'pattern', 'calibration')),
    summary        TEXT NOT NULL,
    detail         JSONB DEFAULT '{}',
    embedding      vector(1024),              -- for RAG retrieval of past lessons
    weight         NUMERIC(5,2) DEFAULT 1.0,  -- salience of this lesson
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sam_reflections_kind ON agents.sam_reflections (kind, created_at DESC);

-- ============================================================
-- TABLE: Sam's hash-chained ledger (operator decision 29.10).
-- The journal above is a mutable "current state" table; this ledger is the
-- audit trail: every signal, decision and outcome is appended with the hash of
-- the previous entry, so a rewritten or deleted record breaks the chain.
-- UPDATE, DELETE and TRUNCATE are refused by trigger, for every role.
-- ============================================================

CREATE TABLE IF NOT EXISTS agents.sam_journal_ledger (
    seq         BIGSERIAL PRIMARY KEY,
    created_at  TIMESTAMPTZ NOT NULL,
    signal_id   VARCHAR(64),
    event       VARCHAR(32) NOT NULL,
    payload     JSONB NOT NULL,
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

-- ============================================================
-- Per-device client tokens (mobile / desktop apps).
-- A shared master API key must never be compiled into a client
-- binary — these are issued per device, stored only as a SHA-256
-- hash, short-lived and individually revocable.
-- ============================================================

CREATE TABLE IF NOT EXISTS auth.device_tokens (
    token_id      VARCHAR(32) PRIMARY KEY,
    secret_hash   VARCHAR(64) NOT NULL,          -- sha256 of the secret half
    device_id     VARCHAR(128) NOT NULL,         -- client-chosen stable id
    label         TEXT,                          -- "Andrii Pixel 8", etc.
    scopes        JSONB NOT NULL DEFAULT '[]',   -- [] == inherit everything
    issued_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at    TIMESTAMPTZ NOT NULL,
    revoked_at    TIMESTAMPTZ,
    last_seen_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_device_tokens_device ON auth.device_tokens (device_id, issued_at DESC);
CREATE INDEX IF NOT EXISTS idx_device_tokens_expires ON auth.device_tokens (expires_at);

-- ============================================================
-- FUNCTION: Updated timestamp trigger
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- DROP + CREATE (not CREATE OR REPLACE TRIGGER, which needs PostgreSQL 14+)
-- so the bootstrap script can be replayed on an existing database and so
-- 02-migration_v4.sql can be applied on top of it without "already exists".
DROP TRIGGER IF EXISTS trg_episodes_updated ON memory.episodes;
CREATE TRIGGER trg_episodes_updated
    BEFORE UPDATE ON memory.episodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- v4.0 TABLES (Included in init.sql for single-pass bootstrap)
-- ============================================================

CREATE TABLE IF NOT EXISTS memory.lessons (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id        VARCHAR(64) NOT NULL,
    kind            VARCHAR(32) NOT NULL DEFAULT 'lesson'
                    CHECK (kind IN ('lesson', 'negative_constraint', 'pattern', 'calibration', 'warning')),
    category        VARCHAR(128),
    summary         TEXT NOT NULL,
    context         TEXT,
    severity        VARCHAR(16) DEFAULT 'medium'
                    CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    lesson_vector   vector(1024),
    times_matched   INTEGER DEFAULT 0,
    do_not_compress BOOLEAN DEFAULT false,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lessons_agent ON memory.lessons (agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lessons_vector_hnsw
    ON memory.lessons USING hnsw (lesson_vector vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE TABLE IF NOT EXISTS memory.response_cache (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id        VARCHAR(64) NOT NULL,
    query_text      TEXT NOT NULL,
    query_vector    vector(1024),
    response_text   TEXT NOT NULL,
    model_used      VARCHAR(64),
    tokens_saved    INTEGER DEFAULT 0,
    hit_count       INTEGER DEFAULT 0,
    cache_tier      VARCHAR(16) DEFAULT 'dynamic'
                    CHECK (cache_tier IN ('dynamic', 'static', 'permanent')),
    ttl_hours       INTEGER DEFAULT 24,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_cache_agent ON memory.response_cache (agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cache_vector_hnsw
    ON memory.response_cache USING hnsw (query_vector vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE TABLE IF NOT EXISTS audit.decisions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id        VARCHAR(64) NOT NULL,
    action          VARCHAR(128) NOT NULL,
    task_type       VARCHAR(128),
    confidence      NUMERIC(5,3),
    escalation      VARCHAR(16) CHECK (escalation IN ('act', 'ask', 'refuse')),
    facts_used      JSONB DEFAULT '[]',
    lessons_checked JSONB DEFAULT '[]',
    model_used      VARCHAR(64),
    input_hash      VARCHAR(64),
    outcome         VARCHAR(32) DEFAULT 'pending'
                    CHECK (outcome IN ('pending', 'success', 'failure', 'overridden', 'blocked', 'refused')),
    hitl_override   BOOLEAN DEFAULT false,
    details         JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit.outbound_vetoes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id        VARCHAR(64) NOT NULL,
    action_type     VARCHAR(128) NOT NULL,
    policy_rule     VARCHAR(32) NOT NULL,
    allowed         BOOLEAN NOT NULL,
    reason          TEXT,
    risk_level      VARCHAR(16),
    details         JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================


CREATE INDEX IF NOT EXISTS idx_lessons_category ON memory.lessons (category, kind);

CREATE INDEX IF NOT EXISTS idx_lessons_severity ON memory.lessons (severity, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_decisions_agent ON audit.decisions (agent_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_decisions_outcome ON audit.decisions (outcome, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_decisions_action ON audit.decisions (action, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_cache_expires ON memory.response_cache (expires_at)
    WHERE expires_at IS NOT NULL;

-- ============================================================
-- MODULE 5: Eva Curator — Deadlines & Social Contacts
-- ============================================================

CREATE TABLE IF NOT EXISTS memory.deadlines (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           VARCHAR(512) NOT NULL,
    category        VARCHAR(128) DEFAULT 'general',
    due_date        DATE NOT NULL,
    remind_days_before INTEGER DEFAULT 7,
    recurring       VARCHAR(32) CHECK (recurring IN ('none', 'weekly', 'monthly', 'quarterly', 'yearly')),
    status          VARCHAR(16) DEFAULT 'active'
                    CHECK (status IN ('active', 'completed', 'expired', 'cancelled')),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_deadlines_due ON memory.deadlines (due_date, status);

CREATE INDEX IF NOT EXISTS idx_deadlines_category ON memory.deadlines (category, due_date);

CREATE TABLE IF NOT EXISTS memory.social_contacts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(256) NOT NULL,
    relationship    VARCHAR(128),
    birthday        DATE,
    phone           VARCHAR(32),
    email           VARCHAR(256),
    last_contact    DATE,
    importance      VARCHAR(16) DEFAULT 'normal'
                    CHECK (importance IN ('low', 'normal', 'high', 'critical')),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_social_birthday ON memory.social_contacts (birthday);

CREATE INDEX IF NOT EXISTS idx_social_last_contact ON memory.social_contacts (last_contact);

-- Keep social_contacts.updated_at fresh (mirrors 02-migration_v4.sql).
DROP TRIGGER IF EXISTS trg_social_contacts_updated ON memory.social_contacts;
CREATE TRIGGER trg_social_contacts_updated
    BEFORE UPDATE ON memory.social_contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- MODULE 6: Doc Health — Biomarkers, Screening, Compliance
-- ============================================================

CREATE TABLE IF NOT EXISTS agents.doc_biomarkers (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    marker_name     VARCHAR(128) NOT NULL,
    value           NUMERIC(12,4) NOT NULL,
    unit            VARCHAR(32),
    ref_range_low   NUMERIC(12,4),
    ref_range_high  NUMERIC(12,4),
    source          VARCHAR(128),
    test_date       DATE NOT NULL,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_biomarkers_name ON agents.doc_biomarkers (marker_name, test_date DESC);

CREATE TABLE IF NOT EXISTS agents.doc_screenings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    screening_type  VARCHAR(128) NOT NULL,
    last_done       DATE,
    next_due        DATE,
    interval_months INTEGER DEFAULT 12,
    status          VARCHAR(16) DEFAULT 'pending'
                    CHECK (status IN ('pending', 'scheduled', 'completed', 'overdue')),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_screenings_due ON agents.doc_screenings (next_due, status);

CREATE TABLE IF NOT EXISTS agents.doc_compliance (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_name       VARCHAR(256) NOT NULL,
    prescribed_freq VARCHAR(32) NOT NULL,
    logged_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed       BOOLEAN DEFAULT true,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_compliance_item ON agents.doc_compliance (item_name, logged_at DESC);

CREATE INDEX IF NOT EXISTS idx_vetoes_agent ON audit.outbound_vetoes (agent_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_vetoes_blocked ON audit.outbound_vetoes (allowed, created_at DESC)
    WHERE allowed = false;

-- ============================================================
-- PERMISSIONS (least privilege — NOLOGIN until Vault rotates password)
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'eva_agent') THEN
        CREATE ROLE eva_agent WITH NOLOGIN;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA memory, agents, audit TO eva_agent;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA memory TO eva_agent;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA agents TO eva_agent;
GRANT INSERT ON ALL TABLES IN SCHEMA audit TO eva_agent;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA memory TO eva_agent;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA agents TO eva_agent;

-- Tables created later (e.g. by 02-migration_v4.sql on an upgrade) must
-- inherit the same privileges, otherwise eva_agent silently loses access
-- to anything added after this point.
ALTER DEFAULT PRIVILEGES IN SCHEMA memory GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO eva_agent;
ALTER DEFAULT PRIVILEGES IN SCHEMA agents GRANT SELECT, INSERT, UPDATE ON TABLES TO eva_agent;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit  GRANT INSERT ON TABLES TO eva_agent;
ALTER DEFAULT PRIVILEGES IN SCHEMA memory GRANT USAGE ON SEQUENCES TO eva_agent;
ALTER DEFAULT PRIVILEGES IN SCHEMA agents GRANT USAGE ON SEQUENCES TO eva_agent;

-- Explicit grants so init.sql is a complete single-pass schema even if
-- 02-migration_v4.sql is not applied.
GRANT SELECT, INSERT, UPDATE, DELETE ON memory.deadlines TO eva_agent;
GRANT SELECT, INSERT, UPDATE ON memory.social_contacts TO eva_agent;
GRANT SELECT, INSERT, UPDATE ON agents.doc_biomarkers TO eva_agent;
GRANT SELECT, INSERT, UPDATE ON agents.doc_screenings TO eva_agent;
GRANT SELECT, INSERT ON agents.doc_compliance TO eva_agent;

-- Device tokens: the runtime issues, verifies, rotates and revokes them.
GRANT SELECT, INSERT, UPDATE, DELETE ON auth.device_tokens TO eva_agent;

-- Sam's ledger: read and append only (the trigger also refuses changes).
REVOKE UPDATE, DELETE, TRUNCATE ON agents.sam_journal_ledger FROM eva_agent;
GRANT SELECT, INSERT ON agents.sam_journal_ledger TO eva_agent;
