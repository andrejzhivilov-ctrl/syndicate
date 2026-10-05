-- ============================================================
-- EVA SYNDICATE v4.0 — Additional Tables (Enhancement Modules)
-- Run AFTER init.sql
-- ============================================================

-- ============================================================
-- MODULE 1: Syndicate Lessons Layer (cross-agent anti-fragility)
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
CREATE INDEX IF NOT EXISTS idx_lessons_category ON memory.lessons (category, kind);
CREATE INDEX IF NOT EXISTS idx_lessons_severity ON memory.lessons (severity, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lessons_vector_hnsw
    ON memory.lessons USING hnsw (lesson_vector vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ============================================================
-- MODULE 3: Decision Audit Log (immutable decision trail)
-- ============================================================

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

CREATE INDEX IF NOT EXISTS idx_decisions_agent ON audit.decisions (agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_decisions_outcome ON audit.decisions (outcome, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_decisions_action ON audit.decisions (action, created_at DESC);

-- ============================================================
-- MODULE 4: Semantic Response Cache
-- ============================================================

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

-- ============================================================
-- MODULE 7: Sentinel — Outbound Action Audit
-- ============================================================

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

CREATE INDEX IF NOT EXISTS idx_vetoes_agent ON audit.outbound_vetoes (agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_vetoes_blocked ON audit.outbound_vetoes (allowed, created_at DESC)
    WHERE allowed = false;

-- ============================================================
-- PERMISSIONS: Grant new tables to eva_agent role
-- ============================================================

GRANT SELECT, INSERT, UPDATE ON memory.lessons TO eva_agent;
GRANT SELECT, INSERT, UPDATE ON memory.response_cache TO eva_agent;
GRANT SELECT, INSERT, UPDATE, DELETE ON memory.deadlines TO eva_agent;
GRANT SELECT, INSERT, UPDATE ON memory.social_contacts TO eva_agent;
GRANT SELECT, INSERT, UPDATE ON agents.doc_biomarkers TO eva_agent;
GRANT SELECT, INSERT, UPDATE ON agents.doc_screenings TO eva_agent;
GRANT SELECT, INSERT ON agents.doc_compliance TO eva_agent;
GRANT INSERT ON audit.decisions TO eva_agent;
GRANT INSERT ON audit.outbound_vetoes TO eva_agent;

-- ============================================================
-- MODULE 8: Per-device client tokens (mobile / desktop apps)
-- A shared master API key must never be compiled into a client
-- binary — these are issued per device, stored only as a hash,
-- short-lived and individually revocable.
-- ============================================================

CREATE SCHEMA IF NOT EXISTS auth;

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

GRANT SELECT, INSERT, UPDATE, DELETE ON auth.device_tokens TO eva_agent;
