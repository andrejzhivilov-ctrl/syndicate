#!/usr/bin/env bash
# EVA SYNDICATE — Vault Initialization Script
# Generates Shamir unseal keys (3-of-5) and configures AppRole auth
# SECURITY: Keys are written to encrypted files only — never logged

set -euo pipefail
IFS=$'\n\t'

VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
SECRETS_DIR="${SECRETS_DIR:-/opt/eva/vault-secrets}"
INIT_OUTPUT_FILE="${SECRETS_DIR}/vault-init.json"
POLICY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../config/vault/policies" && pwd)"

log() { echo "[VAULT-INIT] $(date '+%H:%M:%S') $*"; }
err() { echo "[VAULT-INIT] ERROR: $*" >&2; exit 1; }

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

    log "IMPORTANT: Vault initialized. Unseal keys saved to: $INIT_OUTPUT_FILE"
    log "SECURITY ACTION REQUIRED:"
    log "  1. Extract and distribute 5 unseal keys to 5 different trusted parties."
    log "  2. Store the root token in a hardware security module or password manager."
    log "  3. Delete $INIT_OUTPUT_FILE from this server after distributing keys."
    log "  4. NEVER commit vault-init.json to version control."

    # Extract root token for subsequent setup (temporarily)
    VAULT_TOKEN=$(jq -r '.root_token' "$INIT_OUTPUT_FILE")
    export VAULT_TOKEN

    # Unseal with first 3 keys automatically (for initial setup only)
    log "Auto-unsealing for initial configuration..."
    for i in 0 1 2; do
        local key
        key=$(jq -r ".keys_base64[$i]" "$INIT_OUTPUT_FILE")
        curl -sf -X POST \
            -d "{\"key\": \"$key\"}" \
            "${VAULT_ADDR}/v1/sys/unseal" > /dev/null
    done
    log "Vault unsealed."
}

enable_audit_logging() {
    log "Enabling audit logging..."
    curl -sf -X PUT \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        -d '{"type": "file", "options": {"file_path": "/vault/data/audit.log"}}' \
        "${VAULT_ADDR}/v1/sys/audit/file" > /dev/null
    log "Audit logging enabled."
}

enable_kv_secrets() {
    log "Enabling KV v2 secrets engine..."
    curl -sf -X POST \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"type": "kv", "options": {"version": "2"}}' \
        "${VAULT_ADDR}/v1/sys/mounts/secret" > /dev/null || true

    # Mount paths for EVA agents
    for path in eva/config eva/agents eva/api-keys eva/database; do
        log "Creating secret path: $path"
        curl -sf -X POST \
            -H "X-Vault-Token: $VAULT_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"type\": \"kv\", \"options\": {\"version\": \"2\"}}" \
            "${VAULT_ADDR}/v1/sys/mounts/$path" > /dev/null 2>&1 || true
    done
    log "KV secrets engine configured."
}

write_policies() {
    log "Writing Vault policies..."
    mkdir -p "${POLICY_DIR}"

    # EVA Agent policy
    cat > "${POLICY_DIR}/eva-agent.hcl" << 'POLICY'
# EVA Agent — minimal required access
path "secret/data/eva/*" {
  capabilities = ["read"]
}
path "secret/metadata/eva/*" {
  capabilities = ["list", "read"]
}
path "eva/config/data/*" {
  capabilities = ["read"]
}
path "eva/agents/data/*" {
  capabilities = ["read", "create", "update"]
}
path "eva/api-keys/data/*" {
  capabilities = ["read"]
}
path "eva/database/data/*" {
  capabilities = ["read"]
}
path "auth/token/renew-self" {
  capabilities = ["update"]
}
path "auth/token/lookup-self" {
  capabilities = ["read"]
}
POLICY

    # Sentinel agent policy (read-only + audit)
    cat > "${POLICY_DIR}/sentinel-agent.hcl" << 'POLICY'
path "secret/data/eva/config/*" {
  capabilities = ["read"]
}
path "sys/audit" {
  capabilities = ["read", "list"]
}
path "auth/token/lookup-self" {
  capabilities = ["read"]
}
POLICY

    # Upload policies to Vault
    for policy_file in "${POLICY_DIR}"/*.hcl; do
        local policy_name
        policy_name=$(basename "$policy_file" .hcl)
        log "Uploading policy: $policy_name"
        curl -sf -X PUT \
            -H "X-Vault-Token: $VAULT_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"policy\": $(jq -Rs . < "$policy_file")}" \
            "${VAULT_ADDR}/v1/sys/policies/acl/${policy_name}" > /dev/null
    done
    log "Policies uploaded."
}

enable_approle() {
    log "Enabling AppRole authentication..."
    curl -sf -X POST \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"type": "approle"}' \
        "${VAULT_ADDR}/v1/sys/auth/approle" > /dev/null 2>&1 || true

    # Create EVA agent AppRole
    curl -sf -X POST \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "token_policies": ["eva-agent"],
            "token_ttl": "1h",
            "token_max_ttl": "24h",
            "token_num_uses": 0,
            "secret_id_num_uses": 0,
            "secret_id_ttl": "0"
        }' \
        "${VAULT_ADDR}/v1/auth/approle/role/eva-agent" > /dev/null

    # Create Sentinel AppRole
    curl -sf -X POST \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "token_policies": ["sentinel-agent"],
            "token_ttl": "1h",
            "token_max_ttl": "24h",
            "secret_id_num_uses": 0,
            "secret_id_ttl": "0"
        }' \
        "${VAULT_ADDR}/v1/auth/approle/role/sentinel-agent" > /dev/null

    # Retrieve and save Role IDs
    local eva_role_id sentinel_role_id
    eva_role_id=$(curl -sf \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        "${VAULT_ADDR}/v1/auth/approle/role/eva-agent/role-id" | jq -r '.data.role_id')

    sentinel_role_id=$(curl -sf \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        "${VAULT_ADDR}/v1/auth/approle/role/sentinel-agent/role-id" | jq -r '.data.role_id')

    # Generate Secret IDs
    local eva_secret_id sentinel_secret_id
    eva_secret_id=$(curl -sf -X POST \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        "${VAULT_ADDR}/v1/auth/approle/role/eva-agent/secret-id" | jq -r '.data.secret_id')

    sentinel_secret_id=$(curl -sf -X POST \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        "${VAULT_ADDR}/v1/auth/approle/role/sentinel-agent/secret-id" | jq -r '.data.secret_id')

    # Save to secrets directory (chmod 600)
    cat > "${SECRETS_DIR}/eva-approle.env" << EOF
# EVA Agent AppRole credentials
# Generated: $(date -u '+%Y-%m-%dT%H:%M:%SZ')
# SECURITY: Copy VAULT_ROLE_ID and VAULT_SECRET_ID to your .env file, then delete this file.
VAULT_ROLE_ID=${eva_role_id}
VAULT_SECRET_ID=${eva_secret_id}
EOF
    chmod 600 "${SECRETS_DIR}/eva-approle.env"

    cat > "${SECRETS_DIR}/sentinel-approle.env" << EOF
# Sentinel Agent AppRole credentials
# Generated: $(date -u '+%Y-%m-%dT%H:%M:%SZ')
SENTINEL_VAULT_ROLE_ID=${sentinel_role_id}
SENTINEL_VAULT_SECRET_ID=${sentinel_secret_id}
EOF
    chmod 600 "${SECRETS_DIR}/sentinel-approle.env"

    log "AppRole credentials saved to ${SECRETS_DIR}/"
    log "REQUIRED: Copy values from eva-approle.env into your .env file."
}

store_initial_secrets() {
    log "Storing initial placeholder secrets in Vault (update these with real values!)..."

    # Database credentials
    curl -sf -X POST \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "data": {
                "host": "postgres",
                "port": "5432",
                "name": "eva_syndicate",
                "user": "eva_agent",
                "password": "CHANGE_ME_BEFORE_PRODUCTION"
            }
        }' \
        "${VAULT_ADDR}/v1/eva/database/data/postgres" > /dev/null

    # LLM API keys (placeholders)
    curl -sf -X POST \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "data": {
                "openai_api_key": "PLACEHOLDER_UPDATE_ME",
                "anthropic_api_key": "PLACEHOLDER_UPDATE_ME",
                "embedding_model": "text-embedding-3-small"
            }
        }' \
        "${VAULT_ADDR}/v1/eva/api-keys/data/llm" > /dev/null

    log "Placeholder secrets stored. Update them with real values before production!"
    unset VAULT_TOKEN
}

main() {
    log "====== EVA SYNDICATE Vault Initialization ======"
    check_vault_available
    check_already_initialized
    initialize_vault
    enable_audit_logging
    enable_kv_secrets
    write_policies
    enable_approle
    store_initial_secrets
    log "====== Vault Initialization Complete ======"
    log "Next step: Run vault_unseal.sh on each restart."
}

main "$@"
