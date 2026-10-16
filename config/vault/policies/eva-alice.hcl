# GENERATED FILE — do not edit by hand.
# Regenerate with: python tools/vault_policies.py --write
# Source of truth: src/vault_paths.py
#
# Agent policy: alice.
# Infrastructure: none.
# Own secrets: secret/data/syndicate/agents/alice/auth and secret/data/syndicate/agents/alice/gemini.
# Extra services: none (default deny).
# Cannot read other agents' subtrees or the server's own API key.

path "secret/data/syndicate/agents/alice/auth" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/agents/alice/auth" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/agents/alice/auth" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/agents/alice/auth" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/agents/alice/gemini" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/agents/alice/gemini" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/agents/alice/gemini" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/agents/alice/gemini" {
  capabilities = ["list", "read"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
