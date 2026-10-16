# GENERATED FILE — do not edit by hand.
# Regenerate with: python tools/vault_policies.py --write
# Source of truth: src/vault_paths.py
#
# Runtime policy (server + all floors in one container).
# Holds exactly the secrets the running code reads — see
# vault_paths.INFRA_SERVICES / CONNECTOR_SERVICES / VOICE_SERVICES.
# Replace with the per-agent policies once each floor gets its own
# container: this token can read every floor's secrets by design.

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

path "secret/data/syndicate/auth" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/auth" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/auth" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/auth" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/google_workspace" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/google_workspace" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/google_workspace" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/google_workspace" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/mcp" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/mcp" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/mcp" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/mcp" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/telegram" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/telegram" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/telegram" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/telegram" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/youtube" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/youtube" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/youtube" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/youtube" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/elevenlabs" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/elevenlabs" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/elevenlabs" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/elevenlabs" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/groq" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/groq" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/groq" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/groq" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/openai" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/openai" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/openai" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/openai" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/xai" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/xai" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/xai" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/xai" {
  capabilities = ["list", "read"]
}

path "secret/data/syndicate/agents/*" {
  capabilities = ["read"]
}

path "secret/metadata/syndicate/agents/*" {
  capabilities = ["list", "read"]
}

path "secret/data/eva-syndicate/agents/*" {
  capabilities = ["read"]
}

path "secret/metadata/eva-syndicate/agents/*" {
  capabilities = ["list", "read"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
