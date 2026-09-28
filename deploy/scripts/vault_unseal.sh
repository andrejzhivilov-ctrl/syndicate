#!/usr/bin/env bash
# EVA SYNDICATE — Vault Unseal Script
# Reads unseal keys from environment variables (never from disk)
# Usage: VAULT_UNSEAL_KEY_1=... VAULT_UNSEAL_KEY_2=... VAULT_UNSEAL_KEY_3=... bash vault_unseal.sh

set -euo pipefail

VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"

log() { echo "[VAULT-UNSEAL] $(date '+%H:%M:%S') $*"; }
err() { echo "[VAULT-UNSEAL] ERROR: $*" >&2; exit 1; }

# Validate required keys are provided
[[ -z "${VAULT_UNSEAL_KEY_1:-}" ]] && err "VAULT_UNSEAL_KEY_1 not set"
[[ -z "${VAULT_UNSEAL_KEY_2:-}" ]] && err "VAULT_UNSEAL_KEY_2 not set"
[[ -z "${VAULT_UNSEAL_KEY_3:-}" ]] && err "VAULT_UNSEAL_KEY_3 not set"

check_sealed() {
    local sealed
    sealed=$(curl -sf "${VAULT_ADDR}/v1/sys/health" | jq -r '.sealed' 2>/dev/null || echo "true")
    [[ "$sealed" == "true" ]]
}

unseal_vault() {
    log "Unsealing Vault..."
    for key_var in VAULT_UNSEAL_KEY_1 VAULT_UNSEAL_KEY_2 VAULT_UNSEAL_KEY_3; do
        local key="${!key_var}"
        local response
        response=$(curl -sf -X POST \
            -H "Content-Type: application/json" \
            -d "{\"key\": \"$key\"}" \
            "${VAULT_ADDR}/v1/sys/unseal")
        local sealed
        sealed=$(echo "$response" | jq -r '.sealed')
        log "Applied unseal key from $key_var — sealed=$sealed"
    done
}

main() {
    if ! check_sealed; then
        log "Vault is already unsealed."
        exit 0
    fi
    unseal_vault
    if check_sealed; then
        err "Vault is still sealed after applying 3 keys. Check keys and retry."
    fi
    log "Vault successfully unsealed."
}

main "$@"
