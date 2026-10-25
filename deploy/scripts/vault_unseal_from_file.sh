#!/usr/bin/env bash
# Reads up to 3 unseal keys from a root-only file and applies them. Used by the
# optional systemd unit. Never prints key material.
set -euo pipefail
VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
KEYS_FILE="${UNSEAL_KEYS_FILE:-/etc/syndicate/vault-unseal.keys}"

[[ -r "$KEYS_FILE" ]] || { echo "[VAULT-UNSEAL] no key file at $KEYS_FILE" >&2; exit 1; }
perm=$(stat -c '%a' "$KEYS_FILE")
[[ "$perm" == "400" || "$perm" == "600" ]] || { echo "[VAULT-UNSEAL] $KEYS_FILE must be 0400/0600 (is $perm)" >&2; exit 1; }

for _ in $(seq 1 60); do
    curl -sf "${VAULT_ADDR}/v1/sys/health?uninitcode=200&sealedcode=200" >/dev/null && break
    sleep 2
done

sealed=$(curl -sf "${VAULT_ADDR}/v1/sys/health?sealedcode=200" | jq -r '.sealed' || echo true)
[[ "$sealed" == "true" ]] || { echo "[VAULT-UNSEAL] already unsealed"; exit 0; }

head -n 3 "$KEYS_FILE" | while read -r key; do
    [[ -n "$key" ]] || continue
    curl -sf -X POST -H "Content-Type: application/json" -d "{\"key\": \"${key}\"}" \
        "${VAULT_ADDR}/v1/sys/unseal" >/dev/null
done
sealed=$(curl -sf "${VAULT_ADDR}/v1/sys/health?sealedcode=200" | jq -r '.sealed' || echo true)
[[ "$sealed" == "false" ]] || { echo "[VAULT-UNSEAL] still sealed" >&2; exit 1; }
echo "[VAULT-UNSEAL] unsealed"
