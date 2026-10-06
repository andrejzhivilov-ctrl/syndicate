# GENERATED FILE — do not edit by hand.
# Regenerate with: python tools/vault_policies.py --write
# Source of truth: src/vault_paths.py
#
# Agent policy: fin.
# Infrastructure: database, redis, api-keys.
# Own subtree: secret/data/eva-syndicate/agents/fin/<name>.
# Extra services: google_workspace.
# Cannot read other agents' subtrees or the server's own API key.

path "secret/data/eva-syndicate/database" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/database" {
  capabilities = [""list"", ""read"", "list"]
}

path "secret/data/eva-syndicate/redis" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/redis" {
  capabilities = [""list"", ""read"", "list"]
}

path "secret/data/eva-syndicate/api-keys" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/api-keys" {
  capabilities = [""list"", ""read"", "list"]
}

path "secret/data/eva-syndicate/google_workspace" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/google_workspace" {
  capabilities = [""list"", ""read"", "list"]
}

path "secret/data/eva-syndicate/agents/fin/*" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/agents/fin/*" {
  capabilities = [""list"", ""read"", "list"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
