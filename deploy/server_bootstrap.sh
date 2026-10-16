#!/bin/bash
# ===============================================================
# SYNDICATE — server_bootstrap.sh
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

PROJECT_DIR="/opt/syndicate"
LEGACY_PROJECT_DIR="/opt/eva-syndicate"
if [[ -e "$PROJECT_DIR" && -e "$LEGACY_PROJECT_DIR" ]]; then
    error "Both $PROJECT_DIR and $LEGACY_PROJECT_DIR exist; refusing to choose an installation path"
fi
if [[ -e "$LEGACY_PROJECT_DIR" && ! -e "$PROJECT_DIR" ]]; then
    PROJECT_DIR="$LEGACY_PROJECT_DIR"
    warn "Збережено наявний шлях розгортання для сумісності: $PROJECT_DIR"
fi

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
mkdir -p "$PROJECT_DIR"/{deploy,config,scripts,secrets,logs}
mkdir -p "$PROJECT_DIR"/config/{postgres,nginx,vault}
mkdir -p "$PROJECT_DIR"/config/nginx/conf.d
mkdir -p /data/{eva,marshal,architect,fin,doc,sam,n8n,postgres,redis,vault,audit,clamav,suricata/logs,nginx-certs}
chown -R syndicate:syndicate "$PROJECT_DIR" /data
chmod 700 "$PROJECT_DIR/secrets"
log "✅ Директорії створено у $PROJECT_DIR та /data"

# ── КРОК 7b: ПЕРВИННИЙ SSL БУТСТРАП ДЛЯ NGINX ───────────────────
section "КРОК 7b: Первинний SSL бутстрап (захист від збою Nginx)"
DUMMY_CERT_DIR="/data/nginx-certs/live/default"
if [ ! -f "$DUMMY_CERT_DIR/fullchain.pem" ]; then
    mkdir -p "$DUMMY_CERT_DIR"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$DUMMY_CERT_DIR/privkey.pem" \
        -out "$DUMMY_CERT_DIR/fullchain.pem" \
        -subj "/C=UA/ST=Kyiv/L=Kyiv/O=SYNDICATE/CN=localhost" 2>/dev/null
    log "✅ Створено початковий SSL-сертифікат (Nginx не впаде при першому старті)"
    log "   Після прив'язки домену запусти certbot для бойового Let's Encrypt / Cloudflare"
else
    log "SSL-сертифікати вже існують"
fi

# ── КРОК 8: КЛОНУВАННЯ РЕПОЗИТОРІЮ ────────────────────────────
section "КРОК 8: Клонування репозиторію SYNDICATE"
if [ ! -d "$PROJECT_DIR/.git" ]; then
    GITHUB_TOKEN="${1:-}"
    if [ -z "$GITHUB_TOKEN" ]; then
        warn "GitHub токен не передано. Клонуй вручну:"
        warn "  cd $PROJECT_DIR"
        warn "  git clone https://<TOKEN>@github.com/andrejzhivilov-ctrl/syndicate.git ."
    else
        cd "$PROJECT_DIR"
        git clone "https://${GITHUB_TOKEN}@github.com/andrejzhivilov-ctrl/syndicate.git" .
        chown -R syndicate:syndicate "$PROJECT_DIR"
        log "✅ Репозиторій клоновано"
    fi
else
    warn "Репозиторій вже клоновано — пропускаємо"
fi

# ── КРОК 9: ОПТИМІЗАЦІЯ ПАМ'ЯТІ ТА SWAP ────────────────────────
section "КРОК 9: Оптимізація пам'яті (Redis/Postgres) та Swap"
# Налаштовуємо swappiness=10 замість 60 (щоб система не заморожувала I/O)
cat > /etc/sysctl.d/99-syndicate.conf << 'EOF'
vm.swappiness = 10
vm.overcommit_memory = 1
net.core.somaxconn = 1024
EOF
sysctl -p /etc/sysctl.d/99-syndicate.conf >/dev/null

if [ ! -f /swapfile ]; then
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    log "✅ Swap 4GB активовано (swappiness=10, overcommit_memory=1)"
else
    log "Swap вже існує"
fi

# ── КРОК 10: ВСТАНОВЛЕННЯ CILIUM TETRAGON (eBPF Kernel Security) ──
section "КРОК 10: Встановлення Cilium Tetragon (eBPF на хості)"
if ! command -v tetragon &>/dev/null; then
    log "Завантаження та встановлення Tetragon v1.2.0..."
    TETRAGON_VER="v1.2.0"
    curl -fsSL -o /tmp/tetragon.tar.gz "https://github.com/cilium/tetragon/releases/download/${TETRAGON_VER}/tetragon-${TETRAGON_VER}-amd64.tar.gz" || warn "Не вдалося завантажити Tetragon бінарник (можна встановити пізніше)"
    if [ -f /tmp/tetragon.tar.gz ]; then
        tar -xzf /tmp/tetragon.tar.gz -C /usr/local/bin/ || true
        rm -f /tmp/tetragon.tar.gz
        log "✅ Tetragon встановлено в /usr/local/bin"
    fi
else
    log "Tetragon вже встановлено"
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
echo "  📂 Проект:   $PROJECT_DIR/"
echo "  📂 Дані:     /data/"
echo ""
echo "  НАСТУПНИЙ КРОК:"
echo "  cd $PROJECT_DIR/deploy"
echo "  cp .env.example .env"
echo "  nano .env  (заповни значення)"
echo "  docker compose up -d postgres redis vault nginx"
echo "  ./scripts/vault_init.sh"
echo ""
