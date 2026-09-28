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
-- PERMISSIONS (least privilege)
-- ============================================================

-- EVA agent user (limited to DML on specific schemas)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'eva_agent') THEN
        CREATE ROLE eva_agent WITH LOGIN PASSWORD 'CHANGE_ME_IN_VAULT';
    END IF;
END
$$;

GRANT USAGE ON SCHEMA memory, agents, audit TO eva_agent;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA memory TO eva_agent;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA agents TO eva_agent;
GRANT INSERT ON audit.events TO eva_agent;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA memory TO eva_agent;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA agents TO eva_agent;
