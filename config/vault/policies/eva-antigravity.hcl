# HashiCorp Vault Policy for Director #10: Antigravity
# Grants isolated access to Antigravity's own secrets subtree in KV v2 mount.

path "secret/data/eva-syndicate/agents/antigravity/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/eva-syndicate/agents/antigravity/*" {
  capabilities = ["list", "read"]
}

# Read access to common LLM keys (Gemini, Anthropic, Groq)
path "secret/data/eva-syndicate/llm/*" {
  capabilities = ["read"]
}

# Read access to GitHub development token
path "secret/data/eva-syndicate/github/*" {
  capabilities = ["read"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/lookup-self" {
  capabilities = ["read"]
}
