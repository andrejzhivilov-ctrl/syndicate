#!/bin/bash
# ===============================================================
# EVA SYNDICATE — setup_ssl.sh
# Налаштування бойових HTTPS сертифікатів для Nginx
# Опція 1: Cloudflare Origin CA (Рекомендовано — 15 років без ротації)
# Опція 2: Let's Encrypt через Certbot
# ===============================================================

set -euo pipefail

CERT_DIR="/data/nginx-certs/live/default"
mkdir -p "$CERT_DIR"

echo "=== EVA SYNDICATE: НАЛАШТУВАННЯ SSL СЕРТИФІКАТІВ ==="
echo "Оберіть метод генерації SSL:"
echo "1) Cloudflare Origin Certificate (Рекомендовано для Cloudflare Proxy)"
echo "2) Let's Encrypt через Certbot (Прямий вебхук без Cloudflare Proxy)"
echo "3) Залишити самопідписаний сертифікат для тесту"
read -p "Вибір [1-3]: " SSL_CHOICE

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
        read -p "Введіть ваш домен (наприклад, n8n.syndicate.com): " DOMAIN
        read -p "Введіть ваш email для сповіщень Let's Encrypt: " EMAIL
        
        # Переконуємось що certbot встановлений на хості
        if ! command -v certbot &>/dev/null; then
            apt-get update && apt-get install -y certbot
        fi

        # Тимчасово зупиняємо nginx для standalone перевірки порту 80
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
        docker compose start nginx
        ;;
    3)
        echo "✅ Використовується самопідписаний сертифікат (для тестів)."
        ;;
    *)
        echo "Невірний вибір. Пропускаємо."
        ;;
esac
