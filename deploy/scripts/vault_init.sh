#!/bin/bash
# ===============================================================
# vault_init.sh — Ініціалізація HashiCorp Vault (Production Mode)
# EVA SYNDICATE — ВИКОНУЄТЬСЯ ОДИН РАЗ після першого запуску Vault
# ===============================================================
# Shamir Secret Sharing: 5 ключів, потрібно 3 для unsealing
# Unseal keys + Root token → зберегти ОФЛАЙН на USB Андрія
# ===============================================================

set -euo pipefail
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log() { echo -e "${GREEN}[VAULT]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
export VAULT_ADDR

log "Перевірка з'єднання з Vault..."
vault status 2>/dev/null | grep -q "Initialized" || error "Vault недоступний. Запустити: docker compose up -d vault"

# Перевірка чи Vault вже ініціалізований
if vault status 2>/dev/null | grep -q "Initialized.*true"; then
    warn "Vault вже ініціалізований. Якщо потрібно unsealing — запусти vault_unseal.sh"
    exit 0
fi

# ── ІНІЦІАЛІЗАЦІЯ (ВИКОНУЄТЬСЯ ОДИН РАЗ) ──────────────────────
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE} Vault Production Init — Shamir 3-of-5 ${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}\n"

INIT_OUTPUT=$(vault operator init \
    -key-shares=5 \
    -key-threshold=3 \
    -format=json)

# Зберегти вивід у захищений файл (тільки root читає)
KEYS_FILE="./secrets/vault_keys_OFFLINE_BACKUP.json"
echo "$INIT_OUTPUT" > "$KEYS_FILE"
chmod 600 "$KEYS_FILE"

ROOT_TOKEN=$(echo "$INIT_OUTPUT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['root_token'])")
UNSEAL_KEY_1=$(echo "$INIT_OUTPUT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['unseal_keys_b64'][0])")
UNSEAL_KEY_2=$(echo "$INIT_OUTPUT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['unseal_keys_b64'][1])")
UNSEAL_KEY_3=$(echo "$INIT_OUTPUT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['unseal_keys_b64'][2])")

echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║  ⚠️  КРИТИЧНО: СКОПІЮЙ ЦІ КЛЮЧІ НА USB ПРЯМО ЗАРАЗ!     ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Root Token:    $ROOT_TOKEN"
echo ""
echo "Unseal Key 1:  $UNSEAL_KEY_1"
echo "Unseal Key 2:  $UNSEAL_KEY_2"
echo "Unseal Key 3:  $UNSEAL_KEY_3"
echo "Unseal Key 4:  $(echo "$INIT_OUTPUT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['unseal_keys_b64'][3])")"
echo "Unseal Key 5:  $(echo "$INIT_OUTPUT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['unseal_keys_b64'][4])")"
echo ""
warn "Файл також збережено у: $KEYS_FILE"
warn "Після копіювання на USB — ВИДАЛИ цей файл з сервера!"
echo ""

read -p "Натисни Enter після збереження ключів на USB..."

# ── UNSEALING ─────────────────────────────────────────────────
log "Розпечатування Vault (потрібно 3 з 5 ключів)..."
vault operator unseal "$UNSEAL_KEY_1"
vault operator unseal "$UNSEAL_KEY_2"
vault operator unseal "$UNSEAL_KEY_3"

export VAULT_TOKEN="$ROOT_TOKEN"

log "✅ Vault розпечатано! Починаємо конфігурацію..."

# ── БАЗОВА КОНФІГУРАЦІЯ ────────────────────────────────────────
log "Активація KV Secrets Engine v2..."
vault secrets enable -path=secrets kv-v2 2>/dev/null || warn "KV вже активовано"

log "Активація AppRole auth для агентів..."
vault auth enable approle 2>/dev/null || warn "AppRole вже активовано"

# ── ПОЛІТИКИ ДЛЯ АГЕНТІВ ─────────────────────────────────────
log "Створення політик доступу агентів..."

# Політика ЄВИ — широкий доступ (крім marshal та root секретів)
vault policy write eva-policy - <<'POLICY'
path "secrets/data/llm/*" { capabilities = ["read"] }
path "secrets/data/communication/*" { capabilities = ["read"] }
path "secrets/data/google/*" { capabilities = ["read"] }
path "secrets/data/integrations/*" { capabilities = ["read"] }
path "secrets/data/database/*" { capabilities = ["read"] }
path "secrets/data/n8n/*" { capabilities = ["read"] }
path "secrets/data/github/*" { capabilities = ["read"] }
POLICY

# Політика МАРШАЛА — тільки JWT ключі та security секрети
vault policy write marshal-policy - <<'POLICY'
path "secrets/data/marshal/*" { capabilities = ["read", "create", "update"] }
path "secrets/data/database/*" { capabilities = ["read"] }
path "auth/approle/role/*/secret-id" { capabilities = ["create", "update"] }
POLICY

# Політика АРХІТЕКТОРА — infrastructure secrets
vault policy write architect-policy - <<'POLICY'
path "secrets/data/github/*" { capabilities = ["read"] }
path "secrets/data/database/*" { capabilities = ["read"] }
path "secrets/data/n8n/*" { capabilities = ["read"] }
path "secrets/data/llm/*" { capabilities = ["read"] }
POLICY

# Політика ФІНА — тільки фінансові (READ-ONLY)
vault policy write fin-policy - <<'POLICY'
path "secrets/data/financial/*" { capabilities = ["read"] }
path "secrets/data/llm/*" { capabilities = ["read"] }
POLICY

# Політика ДОКА — медична та LLM секрети
vault policy write doc-policy - <<'POLICY'
path "secrets/data/llm/*" { capabilities = ["read"] }
path "secrets/data/integrations/perplexity*" { capabilities = ["read"] }
POLICY

# Політика СЕМА — трейдинг, біржі, LLM
vault policy write sam-policy - <<'POLICY'
path "secrets/data/llm/*" { capabilities = ["read"] }
path "secrets/data/trading/*" { capabilities = ["read"] }
path "secrets/data/communication/telegram_sam_bot" { capabilities = ["read"] }
POLICY

# ── APPROLE ДЛЯ КОЖНОГО АГЕНТА ────────────────────────────────
for AGENT in eva marshal architect fin doc sam; do
    POLICY_NAME="${AGENT}-policy"
    log "Створення AppRole для ${AGENT}..."
    vault write "auth/approle/role/${AGENT}" \
        token_policies="$POLICY_NAME" \
        token_ttl=15m \
        token_max_ttl=1h \
        token_no_default_policy=false

    ROLE_ID=$(vault read -field=role_id "auth/approle/role/${AGENT}/role-id")
    SECRET_ID=$(vault write -f -field=secret_id "auth/approle/role/${AGENT}/secret-id")

    echo ""
    log "  ${AGENT^^} VAULT CREDENTIALS:"
    echo "    ROLE_ID:    $ROLE_ID"
    echo "    SECRET_ID:  $SECRET_ID"
    echo "    → Додай до .env: ${AGENT^^}_VAULT_ROLE_ID та ${AGENT^^}_VAULT_SECRET_ID"
done

# ── ЗАВАНТАЖЕННЯ БАЗОВИХ СЕКРЕТІВ ─────────────────────────────
echo ""
log "Завантаження API ключів у Vault..."
echo "Введи API ключі вручну (або натисни Enter щоб пропустити):"

read -p "Anthropic API Key (sk-ant-...): " ANTHROPIC_KEY
[[ -n "$ANTHROPIC_KEY" ]] && vault kv put secrets/llm/anthropic_api_key value="$ANTHROPIC_KEY"

read -p "Gemini API Key (AIzaSy...): " GEMINI_KEY
[[ -n "$GEMINI_KEY" ]] && vault kv put secrets/llm/gemini_api_key value="$GEMINI_KEY"

read -p "Groq API Key (gsk_...): " GROQ_KEY
[[ -n "$GROQ_KEY" ]] && vault kv put secrets/llm/groq_api_key value="$GROQ_KEY"

read -p "Perplexity API Key (pplx-...): " PERPLEXITY_KEY
[[ -n "$PERPLEXITY_KEY" ]] && vault kv put secrets/llm/perplexity_api_key value="$PERPLEXITY_KEY"

read -p "Telegram EVA Bot Token: " TG_EVA
[[ -n "$TG_EVA" ]] && vault kv put secrets/communication/telegram_eva_bot value="$TG_EVA"

read -p "Telegram Marshal Bot Token: " TG_MARSHAL
[[ -n "$TG_MARSHAL" ]] && vault kv put secrets/communication/telegram_marshal_bot value="$TG_MARSHAL"

read -p "Telegram Sam Bot Token: " TG_SAM
[[ -n "$TG_SAM" ]] && vault kv put secrets/communication/telegram_sam_bot value="$TG_SAM"

read -p "Nova Poshta API Key: " NP_KEY
[[ -n "$NP_KEY" ]] && vault kv put secrets/integrations/nova_poshta value="$NP_KEY"

read -p "GitHub Token (ghp_...): " GH_TOKEN
[[ -n "$GH_TOKEN" ]] && vault kv put secrets/github/token value="$GH_TOKEN"

# ── НАРЕШТІ: ВИДАЛИ ФАЙЛ КЛЮЧІВ ───────────────────────────────
echo ""
warn "⚠️  Видаляємо файл з ключами з сервера..."
read -p "Підтверди видалення (yes): " CONFIRM
[[ "$CONFIRM" == "yes" ]] && rm -f "$KEYS_FILE" && log "✅ Файл видалено. Ключі залишились тільки на USB." || warn "Файл НЕ видалено — зроби це вручну: rm -f $KEYS_FILE"

echo ""
log "✅ Vault успішно ініціалізовано та налаштовано!"
log "   Наступний крок: docker compose up -d n8n eva"
