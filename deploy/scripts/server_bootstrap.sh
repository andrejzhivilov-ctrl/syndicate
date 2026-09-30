#!/usr/bin/env bash
# EVA SYNDICATE — Server Bootstrap Script
# Run as root on a fresh Ubuntu 24.04 LTS VPS
# Usage: sudo bash server_bootstrap.sh

set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/eva-syndicate-bootstrap.log"
EVA_USER="syndicate"
EVA_GROUP="syndicate"
EVA_UID=1001
EVA_GID=1001
DATA_ROOT="/data"

# UIDs for services
POSTGRES_UID=999
REDIS_UID=999
VAULT_UID=100
N8N_UID=1000

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo "ERROR: This script must be run as root"
        exit 1
    fi
}

install_dependencies() {
    log "Installing system dependencies..."
    apt-get update -qq
    apt-get install -y --no-install-recommends \
        curl \
        wget \
        git \
        jq \
        openssl \
        ca-certificates \
        gnupg \
        lsb-release \
        ufw \
        fail2ban \
        unattended-upgrades \
        apt-transport-https
    log "System dependencies installed."
}

install_docker() {
    if command -v docker &>/dev/null; then
        log "Docker already installed: $(docker --version)"
        return
    fi

    log "Installing Docker CE..."
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -qq
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    systemctl enable --now docker
    log "Docker installed: $(docker --version)"
}

create_eva_user() {
    log "Creating EVA SYNDICATE system user..."
    if ! getent group "$EVA_GROUP" &>/dev/null; then
        groupadd -g "$EVA_GID" "$EVA_GROUP"
    fi
    if ! id "$EVA_USER" &>/dev/null; then
        useradd -u "$EVA_UID" -g "$EVA_GID" -s /sbin/nologin -M -d /opt/eva "$EVA_USER"
    fi
    usermod -aG docker "$EVA_USER" 2>/dev/null || true
    log "User '$EVA_USER' (UID=$EVA_UID) ready."
}

create_data_directories() {
    log "Creating data directories under $DATA_ROOT..."
    mkdir -p \
        "$DATA_ROOT/postgres" \
        "$DATA_ROOT/redis" \
        "$DATA_ROOT/vault" \
        "$DATA_ROOT/vault/audit" \
        "$DATA_ROOT/n8n" \
        "$DATA_ROOT/whisper" \
        "$DATA_ROOT/nginx-certs"

    # Postgres data directory (UID 999)
    chown -R "$POSTGRES_UID:$POSTGRES_UID" "$DATA_ROOT/postgres"
    chmod 700 "$DATA_ROOT/postgres"

    # Redis data directory (UID 999)
    chown -R "$REDIS_UID:$REDIS_UID" "$DATA_ROOT/redis"
    chmod 750 "$DATA_ROOT/redis"

    # Vault data directory (UID 100)
    chown -R "$VAULT_UID:$VAULT_UID" "$DATA_ROOT/vault"
    chmod 700 "$DATA_ROOT/vault"
    chmod 700 "$DATA_ROOT/vault/audit"

    # n8n data directory (UID 1000)
    chown -R "$N8N_UID:$N8N_UID" "$DATA_ROOT/n8n"
    chmod 750 "$DATA_ROOT/n8n"

    # Whisper model cache (root — whisper container runs as root for model download)
    chmod 755 "$DATA_ROOT/whisper"

    # Nginx SSL certs directory
    chmod 755 "$DATA_ROOT/nginx-certs"

    log "Data directories created and permissions set."
}

configure_firewall() {
    log "Configuring UFW firewall..."
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing

    # Allow SSH (customize port if needed)
    ufw allow 22/tcp comment 'SSH'
    # Allow HTTP/HTTPS
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'

    # DENY external access to internal services
    # Vault 8200, Postgres 5432, Redis 6379 — these are internal-only via Docker networks
    ufw deny 8200/tcp comment 'Vault - internal only'
    ufw deny 5432/tcp comment 'Postgres - internal only'
    ufw deny 6379/tcp comment 'Redis - internal only'
    ufw deny 5678/tcp comment 'n8n - internal only'

    ufw --force enable
    log "Firewall configured."
}

configure_fail2ban() {
    log "Configuring fail2ban..."
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
ignoreip = 127.0.0.1/8 ::1

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 86400
EOF
    systemctl enable --now fail2ban
    log "fail2ban configured."
}

harden_sysctl() {
    log "Applying sysctl hardening..."
    cat > /etc/sysctl.d/99-eva-syndicate.conf << 'EOF'
# Network hardening
net.ipv4.ip_forward = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048

# Memory hardening
kernel.randomize_va_space = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2

# File descriptor limits
fs.file-max = 1048576
EOF
    sysctl -p /etc/sysctl.d/99-eva-syndicate.conf
    log "Sysctl hardening applied."
}

setup_unattended_upgrades() {
    log "Configuring automatic security updates..."
    cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF
    systemctl enable --now unattended-upgrades
    log "Automatic security updates configured."
}

main() {
    check_root
    log "====== EVA SYNDICATE Bootstrap Started ======"
    install_dependencies
    install_docker
    create_eva_user
    create_data_directories
    configure_firewall
    configure_fail2ban
    harden_sysctl
    setup_unattended_upgrades
    log "====== Bootstrap Complete ======"
    log "Next step: Run deploy/scripts/vault_init.sh after starting the stack."
}

main "$@"
