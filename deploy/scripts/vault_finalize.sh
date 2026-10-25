#!/usr/bin/env bash
# SYNDICATE — remove the Vault init material from the server once it is safe.
#
# vault-init.json holds all 5 unseal keys (and the already-revoked root token).
# Leaving it next to Vault makes Shamir splitting pointless. Run this ONLY after
# you copied every key into your password manager / offline storage.
#
# Usage: bash deploy/scripts/vault_finalize.sh
set -euo pipefail

SECRETS_DIR="${SECRETS_DIR:-/opt/eva/vault-secrets}"
INIT_FILE="${SECRETS_DIR}/vault-init.json"

if [[ ! -f "$INIT_FILE" ]]; then
    echo "[VAULT-FINALIZE] $INIT_FILE not found — nothing to shred."
    exit 0
fi

echo "This will PERMANENTLY destroy $INIT_FILE (5 unseal keys)."
echo "Type SAVED to confirm that all 5 keys are stored offline:"
read -r answer
if [[ "$answer" != "SAVED" ]]; then
    echo "Aborted. Nothing was changed."
    exit 1
fi

if command -v shred >/dev/null 2>&1; then
    shred -u -n 3 "$INIT_FILE"
else
    rm -f "$INIT_FILE"
fi
echo "[VAULT-FINALIZE] vault-init.json destroyed."
echo "Remaining files in $SECRETS_DIR: *.approle.env, directors.env, operator.token."
echo "Copy the values you need into the protected .env, then delete those files too."
