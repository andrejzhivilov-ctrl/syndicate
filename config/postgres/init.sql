-- EVA SYNDICATE PostgreSQL Initialization
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

-- ============================================================
-- TABLE: Episodic Memory (conversation history + agent events)
-- ============================================================

CREATE TABLE IF NOT EXISTS memory.episodes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id      UUID NOT NULL,
    agent_id        VARCHAR(64) NOT NULL,
    role            VARCHAR(16) NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content         TEXT NOT NULL,
    content_vector  vector(1536),  -- OpenAI text-embedding-3-small dimensions
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
    content_vector vector(1536),
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
    embedding      vector(1536),              -- for RAG retrieval of past lessons
    weight         NUMERIC(5,2) DEFAULT 1.0,  -- salience of this lesson
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sam_reflections_kind ON agents.sam_reflections (kind, created_at DESC);

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
    lesson_vector   vector(1536),
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
    query_vector    vector(1536),
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

