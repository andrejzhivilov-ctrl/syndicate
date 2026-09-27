#!/bin/bash
# ===============================================================
# EVA SYNDICATE — server_bootstrap.sh
# Підготовка Contabo VPS Ubuntu 24.04 LTS до розгортання
# Запускати: sudo bash server_bootstrap.sh
# ===============================================================

set -euo pipefail
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[SYNDICATE]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
section() { echo -e "\n${BLUE}══════════════════════════════════════${NC}"; echo -e "${BLUE} $1${NC}"; echo -e "${BLUE}══════════════════════════════════════${NC}"; }

[[ $EUID -ne 0 ]] && error "Запускай від root: sudo bash $0"

# ── КРОК 1: ОНОВЛЕННЯ СИСТЕМИ ──────────────────────────────────
section "КРОК 1: Оновлення Ubuntu 24.04 LTS"
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
    curl wget git unzip \
    ufw fail2ban \
    htop ncdu \
    ca-certificates gnupg \
    lsb-release \
    python3 python3-pip
log "✅ Система оновлена"

# ── КРОК 2: СТВОРЕННЯ NON-ROOT КОРИСТУВАЧА ─────────────────────
section "КРОК 2: Створення користувача syndicate"
if ! id "syndicate" &>/dev/null; then
    useradd -m -s /bin/bash -u 1000 syndicate
    usermod -aG sudo syndicate
    log "✅ Користувач syndicate створено (uid=1000)"
else
    warn "Користувач syndicate вже існує — пропускаємо"
fi

# ── КРОК 3: ВСТАНОВЛЕННЯ DOCKER ────────────────────────────────
section "КРОК 3: Встановлення Docker Engine"
if ! command -v docker &>/dev/null; then
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    usermod -aG docker syndicate
    systemctl enable docker
    systemctl start docker
    log "✅ Docker $(docker --version) встановлено"
else
    warn "Docker вже встановлено: $(docker --version)"
fi

# ── КРОК 4: UFW БРАНДМАУЕР ─────────────────────────────────────
section "КРОК 4: Налаштування UFW брандмауера"
ufw --force reset
ufw default deny incoming
ufw default deny outgoing

# Вихідний трафік — лише необхідний
ufw allow out 443/tcp comment "HTTPS"
ufw allow out 80/tcp comment "HTTP (для оновлень)"
ufw allow out 53/udp comment "DNS"
ufw allow out 53/tcp comment "DNS over TCP"

# Вхідний — SSH та HTTPS
ufw allow in 22/tcp comment "SSH"
ufw allow in 80/tcp comment "HTTP (redirect to HTTPS)"
ufw allow in 443/tcp comment "HTTPS"

# Docker internal
ufw allow in on docker0
ufw allow out on docker0

# Дозволити внутрішні Docker мережі
ufw allow in on br-+ comment "Docker bridge networks"

ufw --force enable
log "✅ UFW налаштовано: SSH + HTTPS дозволено, все інше — заборонено"

# ── КРОК 5: FAIL2BAN ───────────────────────────────────────────
section "КРОК 5: Налаштування Fail2ban"
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
backend = systemd

[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 86400
EOF
systemctl enable fail2ban
systemctl restart fail2ban
log "✅ Fail2ban активний: 3 спроби SSH → бан на 24 години"

# ── КРОК 6: НАЛАШТУВАННЯ SSH БЕЗПЕКИ ──────────────────────────
section "КРОК 6: Захист SSH"
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd
warn "⚠️  SSH: пароль вимкнено! Переконайся що твій SSH-ключ вже додано до authorized_keys"
log "✅ SSH захищено: root login = NO, password auth = NO"

# ── КРОК 7: СТРУКТУРА ДИРЕКТОРІЙ ──────────────────────────────
section "КРОК 7: Створення структури директорій"
mkdir -p /opt/eva-syndicate/{deploy,config,scripts,secrets,logs}
mkdir -p /opt/eva-syndicate/config/{postgres,nginx,vault}
mkdir -p /opt/eva-syndicate/config/nginx/conf.d
mkdir -p /data/{eva,marshal,architect,fin,doc,n8n}
chown -R syndicate:syndicate /opt/eva-syndicate /data
chmod 700 /opt/eva-syndicate/secrets
log "✅ Директорії створено у /opt/eva-syndicate та /data"

# ── КРОК 8: КЛОНУВАННЯ РЕПОЗИТОРІЮ ────────────────────────────
section "КРОК 8: Клонування репозиторію EVA SYNDICATE"
if [ ! -d "/opt/eva-syndicate/.git" ]; then
    # Буде запитано токен або він передається як аргумент
    GITHUB_TOKEN="${1:-}"
    if [ -z "$GITHUB_TOKEN" ]; then
        warn "GitHub токен не передано. Клонуй вручну:"
        warn "  cd /opt/eva-syndicate"
        warn "  git clone https://<TOKEN>@github.com/andrejzhivilov-ctrl/eva-syndicate.git ."
    else
        cd /opt/eva-syndicate
        git clone "https://${GITHUB_TOKEN}@github.com/andrejzhivilov-ctrl/eva-syndicate.git" .
        chown -R syndicate:syndicate /opt/eva-syndicate
        log "✅ Репозиторій клоновано"
    fi
else
    warn "Репозиторій вже клоновано — пропускаємо"
fi

# ── КРОК 9: НАЛАШТУВАННЯ SWAP (захист від OOM) ────────────────
section "КРОК 9: Налаштування Swap (4GB)"
if [ ! -f /swapfile ]; then
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    log "✅ Swap 4GB активовано"
else
    warn "Swap вже існує — пропускаємо"
fi

# ── ПІДСУМОК ───────────────────────────────────────────────────
section "✅ BOOTSTRAP ЗАВЕРШЕНО"
echo ""
echo "  Система:     Ubuntu 24.04 LTS"
echo "  Docker:      $(docker --version)"
echo "  UFW:         Активний (SSH + HTTPS)"
echo "  Fail2ban:    Активний"
echo "  SSH:         Тільки по ключу"
echo ""
echo "  📂 Проект:   /opt/eva-syndicate/"
echo "  📂 Дані:     /data/"
echo ""
echo "  НАСТУПНИЙ КРОК:"
echo "  cd /opt/eva-syndicate/deploy"
echo "  cp .env.example .env"
echo "  nano .env  (заповни значення)"
echo "  docker compose up -d postgres redis vault nginx"
echo "  ./scripts/vault_init.sh"
echo ""
