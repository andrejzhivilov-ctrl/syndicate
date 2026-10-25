# GENERATED FILE — do not edit by hand.
# Regenerate with: python tools/vault_policies.py --write
# Source of truth: src/vault_paths.py
#
# Agent policy: dex.
# Infrastructure: none.
# Own subtree: secret/data/syndicate/agents/dex/<name>.
# Extra services: none (default deny).
# Cannot read other agents' subtrees or the server's own API key.

path "secret/data/syndicate/agents/dex/*" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/agents/dex/*" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/agents/dex/*" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/agents/dex/*" {
  capabilities = ["list", "read"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
