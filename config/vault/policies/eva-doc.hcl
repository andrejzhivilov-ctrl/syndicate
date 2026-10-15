# GENERATED FILE — do not edit by hand.
# Regenerate with: python tools/vault_policies.py --write
# Source of truth: src/vault_paths.py
#
# Agent policy: doc.
# Infrastructure: database, redis, api-keys.
# Own subtree: secret/data/eva-syndicate/agents/doc/<name>.
# Extra services: none (default deny).
# Cannot read other agents' subtrees or the server's own API key.

path "secret/data/eva-syndicate/database" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/database" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/redis" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/redis" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/api-keys" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/api-keys" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/agents/doc/*" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/agents/doc/*" {
  capabilities = ["list", "read"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
