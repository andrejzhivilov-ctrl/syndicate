#!/bin/bash
# ===============================================================
# SYNDICATE — setup_ssl.sh (v4.1 Verified)
# Налаштування HTTPS сертифікатів для Nginx (/data/nginx-certs/live/default)
# Опція 1: Cloudflare Origin CA (15 років без ротації)
# Опція 2: Let's Encrypt через Certbot
# Опція 3: Генерація 4096-bit Self-Signed сертифіката через openssl
# Підтримує неінтерактивний запуск: ./setup_ssl.sh --self-signed
# ===============================================================

set -euo pipefail

CERT_DIR="/data/nginx-certs/live/default"
mkdir -p "$CERT_DIR"

generate_self_signed() {
    echo "--- ГЕНЕРАЦІЯ 4096-BIT SELF-SIGNED СЕРТИФІКАТА ---"
    openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
        -keyout "$CERT_DIR/privkey.pem" \
        -out "$CERT_DIR/fullchain.pem" \
        -subj "/C=UA/ST=Kyiv/L=Kyiv/O=EvaSyndicate/CN=localhost"
    chmod 600 "$CERT_DIR/privkey.pem"
    chmod 644 "$CERT_DIR/fullchain.pem"
    echo "✅ Самопідписаний сертифікат згенеровано у $CERT_DIR"
}

if [[ "${1:-}" == "--self-signed" ]]; then
    generate_self_signed
    exit 0
fi

echo "=== SYNDICATE: НАЛАШТУВАННЯ SSL СЕРТИФІКАТІВ ==="
echo "Оберіть метод генерації SSL:"
echo "1) Cloudflare Origin Certificate (Рекомендовано для Cloudflare Proxy)"
echo "2) Let's Encrypt через Certbot (Прямий вебхук без Cloudflare Proxy)"
echo "3) Згенерувати самопідписаний сертифікат (для тесту / першого старту)"
read -r -p "Вибір [1-3]: " SSL_CHOICE

case "$SSL_CHOICE" in
    1)
        echo ""
        echo "--- ВСТАНОВЛЕННЯ CLOUDFLARE ORIGIN CERTIFICATE ---"
        echo "1. Відкрийте Cloudflare Dashboard -> SSL/TLS -> Origin Server -> Create Certificate"
        echo "2. Скопіюйте Origin Certificate та Private Key."
        echo ""
        echo "Вставте ваш Origin Certificate (завершіть Ctrl+D):"
        cat > "$CERT_DIR/fullchain.pem"
        echo "Вставте ваш Private Key (завершіть Ctrl+D):"
        cat > "$CERT_DIR/privkey.pem"
        chmod 600 "$CERT_DIR/privkey.pem"
        chmod 644 "$CERT_DIR/fullchain.pem"
        echo "✅ Cloudflare Origin Certificate встановлено у $CERT_DIR"
        docker compose restart nginx || true
        ;;
    2)
        echo ""
        echo "--- ОТРИМАННЯ LET'S ENCRYPT ЧЕРЕЗ CERTBOT ---"
        read -r -p "Введіть ваш домен (наприклад, n8n.syndicate.com): " DOMAIN
        read -r -p "Введіть ваш email для сповіщень Let's Encrypt: " EMAIL

        if ! command -v certbot &>/dev/null; then
            apt-get update && apt-get install -y certbot
        fi

        docker compose stop nginx || true
        certbot certonly --standalone \
            --preferred-challenges http \
            -d "$DOMAIN" \
            --email "$EMAIL" \
            --agree-tos \
            --non-interactive

        cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$CERT_DIR/fullchain.pem"
        cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$CERT_DIR/privkey.pem"
        chmod 600 "$CERT_DIR/privkey.pem"
        chmod 644 "$CERT_DIR/fullchain.pem"
        echo "✅ Let's Encrypt сертифікат отримано та скопійовано у $CERT_DIR"
        docker compose start nginx || true
        ;;
    3)
        generate_self_signed
        docker compose restart nginx || true
        ;;
    *)
        echo "Невірний вибір. Генеруємо самопідписаний сертифікат за замовчуванням..."
        generate_self_signed
        ;;
esac
