#!/usr/bin/env bash
# SYNDICATE — issue a fresh SecretID for one AppRole (e.g. every 60-80 days).
#
# Needs an operator-capable token that may administer AppRoles. That is NOT the
# eva-operator token (by design); use a root token generated with
# `vault operator generate-root` for the few minutes this takes, then revoke it.
#
# Usage: VAULT_TOKEN=<token> bash deploy/scripts/vault_rotate_approle.sh eva-sonar
set -euo pipefail

ROLE="${1:?usage: vault_rotate_approle.sh <role-name e.g. eva-sonar>}"
VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
: "${VAULT_TOKEN:?set VAULT_TOKEN to a token allowed to write auth/approle/role/*}"
SECRETS_DIR="${SECRETS_DIR:-/opt/eva/vault-secrets}"

new_secret=$(curl -sf -X POST -H "X-Vault-Token: ${VAULT_TOKEN}" \
    "${VAULT_ADDR}/v1/auth/approle/role/${ROLE}/secret-id" | jq -r '.data.secret_id // empty')
[[ -n "$new_secret" ]] || { echo "no secret_id returned for ${ROLE}" >&2; exit 1; }

agent="${ROLE#eva-}"
umask 077
out="${SECRETS_DIR}/${ROLE}.rotated.env"
echo "${agent^^}_VAULT_SECRET_ID=${new_secret}" > "$out"
echo "New SecretID written to $out"
echo "1) put it into the protected .env  2) restart the container  3) delete $out"
echo "Old SecretIDs expire on their own TTL; to cut them off now:"
echo "  vault list auth/approle/role/${ROLE}/secret-id  &&  vault write auth/approle/role/${ROLE}/secret-id-accessor/destroy secret_id_accessor=<accessor>"
