# HashiCorp Vault configuration for SYNDICATE (v4.1 Verified)
# Single-node Raft integrated storage

storage "raft" {
  path    = "/vault/data"
  node_id = "eva-vault-node-1"
}

listener "tcp" {
  address         = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  tls_disable     = true  # Internal Docker bridge + localhost bind

  telemetry {
    unauthenticated_metrics_access = false
  }
}

api_addr     = "http://vault:8200"
cluster_addr = "http://vault:8201"

ui = false

# Lease configuration
default_lease_ttl = "1h"
max_lease_ttl     = "24h"
disable_mlock     = true
