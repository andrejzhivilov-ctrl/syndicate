# GENERATED FILE — do not edit by hand.
# Regenerate with: python tools/vault_policies.py --write
# Source of truth: src/vault_paths.py
#
# Operator policy (scripts/syndicate_vault.py).
# Create/update provider keys, the master API key and Telegram bot tokens.
# Issue with:  vault token create -policy=eva-operator -ttl=1h
# No access to AppRole/auth/policy administration or other mounts.

path "secret/data/syndicate/api-keys" {
  capabilities = ["create", "read", "update"]
}

path "secret/data/syndicate/auth" {
  capabilities = ["create", "read", "update"]
}

path "secret/data/syndicate/telegram" {
  capabilities = ["create", "read", "update"]
}

path "secret/data/syndicate/telegram_bots" {
  capabilities = ["create", "read", "update"]
}

path "secret/data/syndicate/google_workspace" {
  capabilities = ["create", "read", "update"]
}

path "secret/data/syndicate/youtube" {
  capabilities = ["create", "read", "update"]
}

path "secret/data/syndicate/mcp" {
  capabilities = ["create", "read", "update"]
}

path "secret/data/syndicate/telegram/*" {
  capabilities = ["create", "read", "update"]
}

path "secret/data/syndicate/agents/*" {
  capabilities = ["create", "read", "update"]
}

path "secret/metadata/syndicate/api-keys" {
  capabilities = ["list", "read"]
}

path "secret/metadata/syndicate/auth" {
  capabilities = ["list", "read"]
}

path "secret/metadata/syndicate/telegram" {
  capabilities = ["list", "read"]
}

path "secret/metadata/syndicate/telegram_bots" {
  capabilities = ["list", "read"]
}

path "secret/metadata/syndicate/google_workspace" {
  capabilities = ["list", "read"]
}

path "secret/metadata/syndicate/youtube" {
  capabilities = ["list", "read"]
}

path "secret/metadata/syndicate/mcp" {
  capabilities = ["list", "read"]
}

path "secret/metadata/syndicate/telegram/*" {
  capabilities = ["list", "read"]
}

path "secret/metadata/syndicate/agents/*" {
  capabilities = ["list", "read"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
