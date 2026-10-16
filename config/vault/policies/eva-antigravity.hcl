# GENERATED FILE — do not edit by hand.
# Regenerate with: python tools/vault_policies.py --write
# Source of truth: src/vault_paths.py
#
# Agent policy: antigravity.
# Infrastructure: none.
# Secret paths: none (retired profile; no Vault data access).
# Extra services: none (default deny).
# Cannot read other agents' subtrees or the server's own API key.

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
