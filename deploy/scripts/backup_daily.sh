#!/bin/bash
# Daily backup set: both PostgreSQL databases, n8n home, Obsidian, bootstrap .env, Vault snapshot.
# Every step reports ok or unavailable; a skipped step is never reported as ok.
# Each database dump is proven by restoring it into a throwaway container.
set -uo pipefail
umask 077

BACKUP_ROOT="${EVA_BACKUP_DIR:-/data/backups}"
KEEP_DAYS="${EVA_BACKUP_KEEP_DAYS:-7}"
REPO_DIR="${SYNDICATE_DIR:-/opt/syndicate}"
OBSIDIAN_DIR="${OBSIDIAN_DIR:-/data/obsidian_vault}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-syndicate-postgres-1}"
N8N_VOLUME="${N8N_VOLUME:-syndicate_n8n_data}"
RESTORE_IMAGE="${RESTORE_IMAGE:-pgvector/pgvector:pg16}"
VAULT_TOKEN_FILE="${VAULT_BACKUP_TOKEN_FILE:-/root/.vault-backup-token}"

STAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
DEST="$BACKUP_ROOT/$STAMP"
mkdir -p "$DEST"
MANIFEST="$DEST/manifest.tsv"
FAILED=0

record() {  # name status detail
    printf '%s\t%s\t%s\n' "$1" "$2" "$3" | tee -a "$MANIFEST"
    [ "$2" = "ok" ] || FAILED=1
}

checked() {  # name file
    if [ -s "$2" ]; then
        record "$1" ok "$(stat -c %s "$2") bytes sha256 $(sha256sum "$2" | cut -d' ' -f1)"
    else
        rm -f "$2"
        record "$1" unavailable "empty or missing output"
    fi
}

backup_database() {  # name database
    local target="$DEST/$1.dump"
    if ! docker exec -e PGDATABASE="$2" "$POSTGRES_CONTAINER" sh -c 'exec pg_dump -U "$POSTGRES_USER" -Fc --no-owner --no-privileges' > "$target"; then
        rm -f "$target"
        record "$1" unavailable "pg_dump failed"
        return
    fi
    checked "$1" "$target"
}

verify_restore() {  # name database
    local dump="$DEST/$1.dump" name="syndicate-restore-test-$$" expected restored
    local tables="select count(*) from information_schema.tables where table_type='BASE TABLE' and table_schema not in ('pg_catalog','information_schema')"
    if [ ! -s "$dump" ]; then
        record "restore_$1" unavailable "no dump to restore"
        return
    fi
    expected="$(docker exec -e PGDATABASE="$2" -e TABLES="$tables" "$POSTGRES_CONTAINER" sh -c 'psql -U "$POSTGRES_USER" -Atc "$TABLES"')"
    if ! docker run -d --rm --name "$name" --network none -e POSTGRES_PASSWORD=restore-test "$RESTORE_IMAGE" > /dev/null; then
        record "restore_$1" unavailable "cannot start restore container"
        return
    fi
    for _ in $(seq 1 30); do
        docker exec "$name" pg_isready -U postgres -q 2> /dev/null && break
        sleep 2
    done
    docker exec "$name" psql -U postgres -qc "create database restore_test" > /dev/null
    docker exec -i "$name" pg_restore -U postgres -d restore_test --no-owner < "$dump" 2> "$DEST/restore_$1.log"
    restored="$(docker exec "$name" psql -U postgres -d restore_test -Atc "$tables")"
    docker stop "$name" > /dev/null
    if [ -n "$expected" ] && [ "$expected" = "$restored" ]; then
        record "restore_$1" ok "$restored of $expected tables restored"
    else
        record "restore_$1" unavailable "restored ${restored:-0} of ${expected:-unknown} tables"
    fi
}

backup_n8n_home() {
    local target="$DEST/n8n_home.tar.gz"
    docker run --rm --network none -v "$N8N_VOLUME:/source:ro" alpine:3.20 tar -czf - -C /source . > "$target" 2> /dev/null
    checked n8n_home "$target"
}

backup_obsidian() {
    local target="$DEST/obsidian.tar.gz"
    tar -czf "$target" -C "$(dirname "$OBSIDIAN_DIR")" "$(basename "$OBSIDIAN_DIR")" 2> /dev/null
    checked obsidian "$target"
}

backup_env() {
    if [ -f "$REPO_DIR/.env" ]; then
        cp "$REPO_DIR/.env" "$DEST/env.bootstrap"
        checked env "$DEST/env.bootstrap"
    else
        record env unavailable "$REPO_DIR/.env not found"
    fi
}

backup_vault() {
    local target="$DEST/vault.snap" container="${VAULT_CONTAINER:-syndicate-vault-1}"
    if [ ! -s "$VAULT_TOKEN_FILE" ]; then
        record vault unavailable "no snapshot token at $VAULT_TOKEN_FILE"
        return
    fi
    docker exec -i -e VAULT_ADDR=http://127.0.0.1:8200 "$container" sh -c \
        'read -r VAULT_TOKEN; export VAULT_TOKEN; vault operator raft snapshot save /tmp/backup.snap >/dev/null && cat /tmp/backup.snap; rm -f /tmp/backup.snap' \
        < "$VAULT_TOKEN_FILE" > "$target"
    checked vault "$target"
}

prune_old() {
    [ "$KEEP_DAYS" -gt 0 ] || return 0
    find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -name '20*Z' -mtime "+$KEEP_DAYS" -exec rm -rf {} +
}

backup_database postgres "${POSTGRES_DB_NAME:-syndicate}"
verify_restore postgres "${POSTGRES_DB_NAME:-syndicate}"
backup_database n8n "${N8N_DB_NAME:-n8n}"
verify_restore n8n "${N8N_DB_NAME:-n8n}"
backup_n8n_home
backup_obsidian
backup_env
backup_vault
if [ "$FAILED" -eq 0 ]; then
    prune_old
fi

echo "set: $DEST"
exit "$FAILED"
