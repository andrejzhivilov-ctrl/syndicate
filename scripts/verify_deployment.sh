#!/usr/bin/env bash
# SYNDICATE — Deployment Verification Script

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0
FAIL=0
WARN=0

green() { echo -e "\033[32m✓ $*\033[0m"; }
red()   { echo -e "\033[31m✗ $*\033[0m"; }
yellow(){ echo -e "\033[33m⚠ $*\033[0m"; }

# NOTE: use $((x+1)) assignment (not ((x++))) — post-increment returns the old
# value, which is 0 on the first call and would trip `set -e`.
pass() { green "$*"; PASS=$((PASS+1)); }
fail() { red "$*";   FAIL=$((FAIL+1)); }
warn() { yellow "$*"; WARN=$((WARN+1)); }

echo "========================================"
echo "  SYNDICATE Deployment Verification"
echo "========================================"

# 1. Docker Compose syntax validation
echo ""
echo "[ Docker Compose Validation ]"
# Load real .env if present; otherwise provide harmless placeholders so the
# required-variable guards (${VAR:?required}) do not abort a pure syntax check.
# Paths inside the compose file are relative to the repo root, so we pin the
# project directory accordingly.
COMPOSE_ENV_ARGS=()
if [[ -f "${REPO_ROOT}/.env" ]]; then
    COMPOSE_ENV_ARGS=(--env-file "${REPO_ROOT}/.env")
fi
if docker compose -f "${REPO_ROOT}/deploy/docker-compose.yml" \
        --project-directory "${REPO_ROOT}" \
        "${COMPOSE_ENV_ARGS[@]}" config -q >/dev/null 2>&1; then
    pass "docker-compose.yml syntax is valid"
elif env POSTGRES_PASSWORD=placeholder REDIS_PASSWORD=placeholder \
        VAULT_ROLE_ID=placeholder VAULT_SECRET_ID=placeholder \
        N8N_USER=placeholder N8N_PASSWORD=placeholder N8N_ENCRYPTION_KEY=placeholder \
        docker compose -f "${REPO_ROOT}/deploy/docker-compose.yml" \
        --project-directory "${REPO_ROOT}" config -q >/dev/null 2>&1; then
    pass "docker-compose.yml syntax is valid (validated with placeholder env vars)"
else
    fail "docker-compose.yml has syntax errors"
fi

# 2. Check for hardcoded secrets
echo ""
echo "[ Secret Scanning ]"
SECRET_PATTERNS=(
    "sk-[a-zA-Z0-9]{40,}"
    "password\s*=\s*['\"][^'\"]{4,}"
    "api_key\s*=\s*['\"][^'\"]{10,}"
    "secret\s*=\s*['\"][^'\"]{10,}"
    "eyJ[A-Za-z0-9_-]{20,}"
)

SECRETS_FOUND=false
for pattern in "${SECRET_PATTERNS[@]}"; do
    matches=$(grep -rE "$pattern" "${REPO_ROOT}" \
        --exclude-dir=".git" \
        --exclude="*.example" \
        --exclude="*.md" \
        --exclude="verify_deployment.sh" \
        2>/dev/null || true)
    if [[ -n "$matches" ]]; then
        fail "Potential secret found matching pattern: $pattern"
        echo "$matches" | head -5
        SECRETS_FOUND=true
    fi
done
if [[ "$SECRETS_FOUND" == "false" ]]; then
    pass "No hardcoded secrets detected"
fi

# 3. Check .env.example exists
echo ""
echo "[ Required Files ]"
REQUIRED_FILES=(
    ".env.example"
    "deploy/docker-compose.yml"
    "docker/Dockerfile.agent"
    "config/vault/vault.hcl"
    "config/redis/redis.conf"
    "config/postgres/init.sql"
    "config/nginx/nginx.conf"
    "deploy/runtime/agent_runner.py"
    "deploy/scripts/server_bootstrap.sh"
    "deploy/scripts/vault_init.sh"
    "deploy/scripts/vault_unseal.sh"
    "requirements.txt"
)
for f in "${REQUIRED_FILES[@]}"; do
    if [[ -f "${REPO_ROOT}/${f}" ]]; then
        pass "Found: $f"
    else
        fail "Missing: $f"
    fi
done

# 4. Check .env is NOT committed
echo ""
echo "[ Git Security ]"
if git -C "${REPO_ROOT}" ls-files --error-unmatch .env &>/dev/null 2>&1; then
    fail ".env file is tracked by git — REMOVE IT IMMEDIATELY"
else
    pass ".env is not tracked by git"
fi

if [[ -f "${REPO_ROOT}/.gitignore" ]]; then
    if grep -q "^\.env$" "${REPO_ROOT}/.gitignore"; then
        pass ".env is in .gitignore"
    else
        warn ".env not found in .gitignore — add it"
    fi
fi

# 5. Dockerfile security checks
echo ""
echo "[ Dockerfile Security ]"
if grep -q "USER 1001" "${REPO_ROOT}/docker/Dockerfile.agent" 2>/dev/null; then
    pass "Dockerfile uses non-root user (1001)"
else
    fail "Dockerfile does not use non-root user"
fi

if grep -q "FROM.*AS builder" "${REPO_ROOT}/docker/Dockerfile.agent" 2>/dev/null; then
    pass "Dockerfile uses multi-stage build"
else
    warn "Dockerfile does not use multi-stage build"
fi

if grep -qi "root" "${REPO_ROOT}/docker/Dockerfile.agent" 2>/dev/null | grep -v "#" &>/dev/null; then
    warn "Dockerfile may reference root — review"
fi

# 6. Summary
echo ""
echo "========================================"
echo "  Results: $PASS passed | $WARN warnings | $FAIL failed"
echo "========================================"

if [[ $FAIL -gt 0 ]]; then
    echo "DEPLOYMENT BLOCKED: Fix $FAIL critical issues before deploying."
    exit 1
elif [[ $WARN -gt 0 ]]; then
    echo "DEPLOYMENT ALLOWED WITH WARNINGS: Review $WARN warnings."
    exit 0
else
    echo "ALL CHECKS PASSED. Ready for deployment."
    exit 0
fi
