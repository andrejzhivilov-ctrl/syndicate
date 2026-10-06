#!/usr/bin/env bash
# EVA SYNDICATE — Vault initialization script
#
# What it does, in order:
#   1. initializes Vault (Shamir 3-of-5) and auto-unseals for setup
#   2. enables the KV v2 mount and audit logging
#   3. uploads config/vault/policies/*.hcl (generated — see tools/vault_policies.py)
#   4. creates one AppRole per policy, so each floor can get its own token
#   5. stores the real secrets it is given (NO placeholders — see below)
#   6. revokes the root token unless KEEP_ROOT_TOKEN=1
#
# Where the secrets come from:
#   POSTGRES_PASSWORD / REDIS_PASSWORD  must be supplied (they already live in
#   .env for docker-compose) and are pushed into Vault, so both sides hold the
#   same value instead of a script-invented default.
#   OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY / XAI_API_KEY / GROQ_API_KEY
#   are optional: a key that is not supplied is simply **absent** from Vault.
#   Earlier revisions wrote "PLACEHOLDER_UPDATE_ME" / "CHANGE_ME_BEFORE_PRODUCTION";
#   those strings are worse than nothing, because a filled-in-looking value
#   hides the fact that nobody configured anything. VaultClient now also drops
#   such values, so an old deployment cannot silently keep using one.
#
# SECURITY: unseal keys and root token are written to 0600 files only, never
# logged. Distribute the unseal keys and delete vault-init.json afterwards.

set -euo pipefail
IFS=$'\n\t'

VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
SECRETS_DIR="${SECRETS_DIR:-/opt/eva/vault-secrets}"
INIT_OUTPUT_FILE="${SECRETS_DIR}/vault-init.json"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
POLICY_DIR="${REPO_ROOT}/config/vault/policies"
KEEP_ROOT_TOKEN="${KEEP_ROOT_TOKEN:-0}"
ROTATE="${ROTATE:-0}"
VAULT_TOKEN=""

log() { echo "[VAULT-INIT] $(date '+%H:%M:%S') $*"; }
err() { echo "[VAULT-INIT] ERROR: $*" >&2; exit 1; }
require_cmd() { command -v "$1" >/dev/null 2>&1 || err "required command '$1' not found"; }

api() {  # api METHOD PATH [JSON]
    local method="$1" path="$2" body="${3:-}"
    if [[ -n "$body" ]]; then
        curl -sf -X "$method" -H "X-Vault-Token: ${VAULT_TOKEN}" \
            -H "Content-Type: application/json" -d "$body" "${VAULT_ADDR}/v1/${path}"
    else
        curl -sf -X "$method" -H "X-Vault-Token: ${VAULT_TOKEN}" "${VAULT_ADDR}/v1/${path}"
    fi
}

is_placeholder() {  # a value that only looks like a secret (or is empty)
    local value="${1:-}"
    if [[ -z "$value" ]]; then
        return 0
    fi
    local upper="${value^^}"
    local marker
    for marker in CHANGE_ME PLACEHOLDER REPLACE_ME UPDATE_ME FIXME TODO; do
        if [[ "$upper" == *"$marker"* ]]; then
            return 0
        fi
    done
    return 1
}

# NOTE on `set -e`: every guard below is written as `if ...; then err ...; fi`
# on purpose. `is_placeholder "$x" && err` would abort the script *when the
# value is fine*, because the failing `&&` list itself returns non-zero.


check_vault_available() {
    local retries=0
    while ! curl -sf "${VAULT_ADDR}/v1/sys/health?uninitcode=200&sealedcode=200" &>/dev/null; do
        retries=$((retries + 1))
        [[ $retries -gt 30 ]] && err "Vault not available after 30 attempts"
        log "Waiting for Vault to start... attempt $retries"
        sleep 2
    done
    log "Vault is available."
}

check_already_initialized() {
    local status
    status=$(curl -sf "${VAULT_ADDR}/v1/sys/health" | jq -r '.initialized' 2>/dev/null || echo "false")
    if [[ "$status" == "true" ]]; then
        log "Vault is already initialized. Use vault_unseal.sh to unseal."
        exit 0
    fi
}

initialize_vault() {
    log "Initializing Vault with Shamir secret sharing (3-of-5)..."
    mkdir -p "$SECRETS_DIR"
    chmod 700 "$SECRETS_DIR"

    local init_response
    init_response=$(curl -sf -X POST \
        -H "Content-Type: application/json" \
        -d '{"secret_shares": 5, "secret_threshold": 3}' \
        "${VAULT_ADDR}/v1/sys/init")

    echo "$init_response" > "$INIT_OUTPUT_FILE"
    chmod 600 "$INIT_OUTPUT_FILE"

    # Guard: an empty or error-shaped response used to be written silently, and
    # the script then "unsealed" with empty keys — failing much later with 400s
    # that point at the wrong thing. /sys/init is POST in current Vault docs
    # (older revisions documented PUT; Vault accepts both).
    if ! jq -e '.root_token and (.keys_base64 | length) > 0' "$INIT_OUTPUT_FILE" > /dev/null 2>&1; then
        err "Vault did not return a root token / unseal keys. Response starts with:
         $(head -c 200 "$INIT_OUTPUT_FILE")
         Check that VAULT_ADDR (${VAULT_ADDR}) is a Vault 1.x server and that this
         node was not initialised concurrently."
    fi

    log "IMPORTANT: Vault initialized. Unseal keys saved to: $INIT_OUTPUT_FILE"
    log "SECURITY ACTION REQUIRED:"
    log "  1. Extract and distribute the 5 unseal keys to 5 different trusted parties."
    log "  2. Store the root token in a hardware security module or password manager."
    log "  3. Delete $INIT_OUTPUT_FILE from this server after distributing keys."
    log "  4. NEVER commit vault-init.json to version control."

    VAULT_TOKEN=$(jq -r '.root_token' "$INIT_OUTPUT_FILE")
    export VAULT_TOKEN

    log "Auto-unsealing for initial configuration..."
    local i key
    for i in 0 1 2; do
        key=$(jq -r ".keys_base64[$i]" "$INIT_OUTPUT_FILE")
        curl -sf -X POST -d "{\"key\": \"$key\"}" "${VAULT_ADDR}/v1/sys/unseal" > /dev/null
    done
    log "Vault unsealed."
}

enable_audit_logging() {
    log "Enabling audit logging..."
    api PUT "sys/audit/file" '{"type": "file", "options": {"file_path": "/vault/data/audit.log"}}' > /dev/null \
        || log "Audit device already enabled (or path exists) — continuing."
    log "Audit logging enabled."
}

enable_kv_secrets() {
    log "Enabling KV v2 secrets engine..."
    api POST "sys/mounts/secret" '{"type": "kv", "options": {"version": "2"}}' > /dev/null \
        || log "KV v2 mount already exists — continuing."
    log "KV secrets engine configured (mount: secret, prefix: eva-syndicate)."
}

upload_policies() {
    log "Uploading Vault policies from config/vault/policies/..."
    [[ -d "$POLICY_DIR" ]] || err "policy directory not found: $POLICY_DIR"
    shopt -s nullglob
    local policy_files=("$POLICY_DIR"/*.hcl)
    shopt -u nullglob
    [[ ${#policy_files[@]} -gt 0 ]] || err "no policies in $POLICY_DIR (run: python tools/vault_policies.py --write)"

    local policy_file policy_name payload
    for policy_file in "${policy_files[@]}"; do
        policy_name="$(basename "$policy_file" .hcl)"
        payload="$(jq -Rs '{policy: .}' < "$policy_file")"
        api PUT "sys/policies/acl/${policy_name}" "$payload" > /dev/null
        log "  uploaded policy: $policy_name"
    done
    log "Policies uploaded: ${#policy_files[@]}."
}

create_approles() {
    log "Creating AppRole per policy..."
    api POST "sys/auth/approle" '{"type": "approle"}' > /dev/null 2>&1 || true

    shopt -s nullglob
    local policy_files=("$POLICY_DIR"/*.hcl)
    shopt -u nullglob

    local policy_file policy_name role_id secret_id
    for policy_file in "${policy_files[@]}"; do
        policy_name="$(basename "$policy_file" .hcl)"
        api POST "auth/approle/role/${policy_name}" "{
            \"token_policies\": [\"${policy_name}\"],
            \"token_ttl\": \"1h\",
            \"token_max_ttl\": \"24h\",
            \"token_num_uses\": 0,
            \"secret_id_num_uses\": 0,
            \"secret_id_ttl\": \"0\"
        }" > /dev/null

        role_id=$(api GET "auth/approle/role/${policy_name}/role-id" | jq -r '.data.role_id // empty')
        secret_id=$(api POST "auth/approle/role/${policy_name}/secret-id" | jq -r '.data.secret_id // empty')
        if [[ -z "$role_id" || -z "$secret_id" ]]; then
            err "AppRole '${policy_name}' did not yield a role_id/secret_id — refusing to write
         a half-empty credentials file (agent_runner requires both, see _vault_env)."
        fi

        cat > "${SECRETS_DIR}/${policy_name}.approle.env" << EOF
# AppRole credentials for policy '${policy_name}' — generated $(date -u '+%Y-%m-%dT%H:%M:%SZ')
# Put these two values into .env (VAULT_ROLE_ID / VAULT_SECRET_ID for the
# runtime container) and delete this file.
VAULT_ROLE_ID=${role_id}
VAULT_SECRET_ID=${secret_id}
EOF
        chmod 600 "${SECRETS_DIR}/${policy_name}.approle.env"
        log "  ${policy_name}: role + secret id written to ${policy_name}.approle.env"
    done
    log "AppRoles created. Copy ${SECRETS_DIR}/eva-agent.approle.env into .env."
}

store_secret() {  # store_secret <path> <json-data> [--rotate]
    local path="$1" data="$2" rotate="${3:-}"
    local vault_path="secret/data/eva-syndicate/${path}"

    if [[ "$rotate" != "--rotate" ]] && api GET "$vault_path" > /dev/null 2>&1; then
        log "  ${path}: already present in Vault — left untouched (ROTATE=1 to overwrite)"
        return 0
    fi
    api POST "$vault_path" "{\"data\": ${data}}" > /dev/null
    log "  ${path}: stored"
}

store_initial_secrets() {
    log "Storing secrets (no placeholders: anything not supplied stays absent)..."

    # Database + Redis: these already live in .env for docker-compose, so the
    # script pushes the same values instead of inventing its own. A mismatch
    # between Postgres and Vault is the classic deployment failure.
    # Defaults MUST match docker-compose.yml (`${POSTGRES_USER:-eva}`) and
    # .env.example, or Vault would hold a user the database does not have and
    # the agent's DSN would be rejected.
    local db_password="${POSTGRES_PASSWORD:-}" db_user="${POSTGRES_USER:-eva}"
    local db_name="${POSTGRES_DB:-eva_syndicate}"
    if is_placeholder "$db_password"; then
        err "POSTGRES_PASSWORD is empty or still a placeholder — set a real password in
         .env first (Vault must hold the same password Postgres was initialised with)."
    fi

    local redis_password="${REDIS_PASSWORD:-}"
    if is_placeholder "$redis_password"; then
        err "REDIS_PASSWORD is empty or still a placeholder — set a real password in .env first."
    fi

    local rotate=""
    if [[ "$ROTATE" == "1" ]]; then
        rotate="--rotate"
    fi

    store_secret "database" "{
        \"host\": \"postgres\",
        \"port\": \"5432\",
        \"name\": \"${db_name}\",
        \"user\": \"${db_user}\",
        \"password\": \"${db_password}\"
    }" "$rotate"

    store_secret "redis" "{\"password\": \"${redis_password}\"}" "$rotate"

    # Server API key + webhook HMAC. Generated once, randomly: these are new
    # secrets, not placeholders, so nobody has to fill them in.
    store_secret "auth" "{
        \"api_key\": \"$(openssl rand -hex 32)\",
        \"webhook_secret\": \"$(openssl rand -hex 32)\"
    }" "$rotate"

    # LLM provider keys: only what the operator actually supplied.
    store_llm_keys "$rotate"

    log "Absent secrets are simply not created — that is deliberate. Add them later with:"
    log "  vault kv put secret/eva-syndicate/<service> key=value"
    log "  (services: telegram, google_workspace, mcp, elevenlabs, groq, openai, xai,"
    log "   agents/<agent>/<name> — see config/vault/policies/*.hcl for who may read what)"
    log "Auth secrets (API key / webhook HMAC) were generated randomly —"
    log "retrieve them with: vault kv get secret/eva-syndicate/auth"
}

store_llm_keys() {
    local rotate="${1:-}"
    local data="{" first=1
    local pair name var value
    for pair in "openai_api_key:OPENAI_API_KEY" "anthropic_api_key:ANTHROPIC_API_KEY" \
                "google_api_key:GOOGLE_API_KEY" "xai_api_key:XAI_API_KEY" \
                "groq_api_key:GROQ_API_KEY"; do
        name="${pair%%:*}"
        var="${pair#*:}"
        value="${!var:-}"
        if [[ -z "$value" ]]; then
            continue
        fi
        if is_placeholder "$value"; then
            err "environment variable ${var} still holds a placeholder value"
        fi
        if [[ $first -eq 0 ]]; then
            data+=","
        fi
        data+="\"${name}\": \"${value}\""
        first=0
    done
    data+="}"

    if [[ "$first" -eq 1 ]]; then
        log "  api-keys: no provider keys supplied (OPENAI_API_KEY, ANTHROPIC_API_KEY, ...)"
        log "            → secret left absent; the agent will report LLM as unavailable,"
        log "              which is honest. Add keys and re-run with ROTATE=1 to store them."
        return 0
    fi
    store_secret "api-keys" "$data" "$rotate"
}

revoke_root_token() {
    if [[ "$KEEP_ROOT_TOKEN" == "1" ]]; then
        log "KEEP_ROOT_TOKEN=1 — root token NOT revoked. Revoke it manually when done:"
        log "  VAULT_TOKEN=<root> vault token revoke -self"
        return 0
    fi
    log "Revoking the root token (break-glass stays available via 3-of-5 unseal keys"
    log " + 'vault operator generate-root'). Set KEEP_ROOT_TOKEN=1 to skip."
    api POST "auth/token/revoke-self" > /dev/null || log "Root token revocation failed — revoke it manually."
    VAULT_TOKEN=""
    log "Root token revoked."
}

main() {
    require_cmd curl
    require_cmd jq
    require_cmd openssl

    log "====== EVA SYNDICATE Vault initialization ======"
    check_vault_available
    check_already_initialized
    initialize_vault
    enable_audit_logging
    enable_kv_secrets
    upload_policies
    store_initial_secrets
    create_approles
    revoke_root_token
    log "====== Vault initialization complete ======"
    log "Next steps:"
    log "  1. cp ${SECRETS_DIR}/eva-agent.approle.env  →  append to .env, then delete it"
    log "  2. Run vault_unseal.sh after every Vault restart."
    log "  3. Verify policies match the code:  python tools/vault_policies.py --check"
}

main "$@"
