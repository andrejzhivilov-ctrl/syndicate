# GENERATED FILE — do not edit by hand.
# Regenerate with: python tools/vault_policies.py --write
# Source of truth: src/vault_paths.py
#
# Runtime policy (server + all floors in one container).
# Holds exactly the secrets the running code reads — see
# vault_paths.INFRA_SERVICES / CONNECTOR_SERVICES / VOICE_SERVICES.
# Replace with the per-agent policies once each floor gets its own
# container: this token can read every floor's secrets by design.

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

path "secret/data/eva-syndicate/auth" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/auth" {
  capabilities = [""list"", ""read"", "list"]
}

path "secret/data/eva-syndicate/google_workspace" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/google_workspace" {
  capabilities = [""list"", ""read"", "list"]
}

path "secret/data/eva-syndicate/mcp" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/mcp" {
  capabilities = [""list"", ""read"", "list"]
}

path "secret/data/eva-syndicate/telegram" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/telegram" {
  capabilities = [""list"", ""read"", "list"]
}

path "secret/data/eva-syndicate/elevenlabs" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/elevenlabs" {
  capabilities = [""list"", ""read"", "list"]
}

path "secret/data/eva-syndicate/groq" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/groq" {
  capabilities = [""list"", ""read"", "list"]
}

path "secret/data/eva-syndicate/openai" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/openai" {
  capabilities = [""list"", ""read"", "list"]
}

path "secret/data/eva-syndicate/xai" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/xai" {
  capabilities = [""list"", ""read"", "list"]
}

path "secret/data/eva-syndicate/agents/*" {
  capabilities = [""read""]
}

path "secret/metadata/eva-syndicate/agents/*" {
  capabilities = [""list"", ""read"", "list"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
