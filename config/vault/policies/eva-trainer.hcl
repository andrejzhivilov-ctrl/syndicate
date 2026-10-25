# GENERATED FILE — do not edit by hand.
# Regenerate with: python tools/vault_policies.py --write
# Source of truth: src/vault_paths.py
#
# Agent policy: trainer.
# Infrastructure: database, redis, api-keys.
# Own subtree: secret/data/syndicate/agents/trainer/<name>.
# Extra services: none (default deny).
# Cannot read other agents' subtrees or the server's own API key.

path "secret/data/syndicate/database" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/database" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/database" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/database" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/redis" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/redis" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/redis" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/redis" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/api-keys" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/api-keys" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/api-keys" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/api-keys" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/agents/trainer/*" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/agents/trainer/*" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/agents/trainer/*" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/agents/trainer/*" {
  capabilities = ["list", "read"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
