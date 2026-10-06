-- ============================================================
-- EVA SYNDICATE — migration v5: embedding dimension 1536 -> 1024
--
-- Why: vectors are now produced by the self-hosted BGE-M3 model
-- (see src/embeddings.py) instead of a third-party API. BGE-M3 emits 1024
-- dimensions, so every ``vector(N)`` column has to match — a mismatch is not a
-- cosmetic problem, it makes every cosine distance meaningless while still
-- returning rows.
--
-- Safe to replay: each column is checked first, and a column that already holds
-- ``vector(1024)`` is left alone.
--
-- IMPORTANT: vectors cannot be converted between dimensions. If a column still
-- holds 1536-dimension rows, this migration SKIPS it with a warning rather than
-- destroying data — the rows have to be re-embedded (they lived under a
-- different model, so their vectors would be incomparable anyway).
--
-- Apply with:
--     psql "$POSTGRES_DSN" -f config/postgres/migration_v5_embeddings_1024.sql
-- ============================================================

DO $migration$
DECLARE
    target      RECORD;
    existing    TEXT;
    non_null    BIGINT;
BEGIN
    FOR target IN
        SELECT * FROM (VALUES
            ('memory.episodes',      'content_vector', 'idx_episodes_vector_hnsw'),
            ('memory.semantic',      'content_vector', 'idx_semantic_vector_hnsw'),
            ('memory.lessons',       'lesson_vector',  'idx_lessons_vector_hnsw'),
            ('memory.response_cache','query_vector',   'idx_cache_vector_hnsw'),
            ('agents.sam_reflections','embedding',     NULL)
        ) AS t(tbl, col, idx_name)
    LOOP
        SELECT format_type(a.atttypid, a.atttypmod)
          INTO existing
          FROM pg_attribute a
          JOIN pg_class c     ON c.oid = a.attrelid
          JOIN pg_namespace n ON n.oid = c.relnamespace
         WHERE n.nspname || '.' || c.relname = target.tbl
           AND a.attname = target.col
           AND a.attnum > 0
           AND NOT a.attisdropped;

        IF existing IS NULL THEN
            -- Table or column absent in this deployment: nothing to migrate.
            CONTINUE;
        END IF;

        IF existing = 'vector(1024)' THEN
            CONTINUE;
        END IF;

        IF existing <> 'vector(1536)' THEN
            RAISE WARNING 'migration v5: %.% is %, expected vector(1024) or vector(1536) — left untouched',
                target.tbl, target.col, existing;
            CONTINUE;
        END IF;

        EXECUTE format('SELECT count(*) FROM %s WHERE %I IS NOT NULL', target.tbl, target.col)
           INTO non_null;

        IF non_null > 0 THEN
            RAISE WARNING
                'migration v5: SKIPPED %.% — % row(s) still hold 1536-dimension vectors. '
                'They cannot be converted; re-embed them before retrying.',
                target.tbl, target.col, non_null;
            CONTINUE;
        END IF;

        -- An HNSW index cannot survive a type change, so it is dropped and
        -- rebuilt on the new dimension (cheap: the column is empty).
        IF target.idx_name IS NOT NULL THEN
            EXECUTE format('DROP INDEX IF EXISTS %s', target.idx_name);
        END IF;

        EXECUTE format('ALTER TABLE %s ALTER COLUMN %I TYPE vector(1024)', target.tbl, target.col);

        IF target.idx_name IS NOT NULL THEN
            EXECUTE format(
                'CREATE INDEX IF NOT EXISTS %s ON %s USING hnsw (%I vector_cosine_ops) '
                'WITH (m = 16, ef_construction = 64)',
                target.idx_name, target.tbl, target.col
            );
        END IF;

        RAISE NOTICE 'migration v5: %.% -> vector(1024)', target.tbl, target.col;
    END LOOP;
END
$migration$;
