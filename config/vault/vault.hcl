# HashiCorp Vault configuration for EVA SYNDICATE
# Raft integrated storage for HA without external dependencies

storage "raft" {
  path    = "/vault/data"
  node_id = "eva-vault-node-1"

  retry_join {
    leader_api_addr = "http://127.0.0.1:8200"
  }
}

listener "tcp" {
  address       = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  tls_disable   = true  # TLS terminated at nginx/host level

  # Security headers
  telemetry {
    unauthenticated_metrics_access = false
  }
}

api_addr     = "http://vault:8200"
cluster_addr = "http://vault:8201"

ui = false  # Disable UI in production

# Audit logging
audit_device_count_ignore_acl = true

# Performance
default_lease_ttl = "1h"
max_lease_ttl     = "24h"

# Disable mlock for containers (IPC_LOCK cap handles this)
disable_mlock = false
