#!/usr/bin/env bash
#
# SYNDICATE — всі ворота якості однією командою.
#
# Запускай ПЕРЕД кожним комітом і ПЕРЕД мерджем у main:
#     bash tools/check.sh
#
# Вихід 0 = усе зелене. Будь-який інший код = не коміть.
#
# Залежності:  pip install -r requirements.txt -r requirements-dev.txt
#
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Віртуальне оточення: використовуємо .venv, якщо воно є, інакше системний python.
if [ -x ".venv/bin/python" ]; then
    PY=".venv/bin/python"
    RUFF=".venv/bin/ruff"
else
    PY="${PYTHON:-python3}"
    RUFF="ruff"
fi

FAILED=0
step() {
    printf '\n\033[1m─── %s ──────────────────────────────────────────\033[0m\n' "$1"
}

run() {
    local label="$1"; shift
    local out rc
    out="$("$@" 2>&1)"
    rc=$?
    if [ $rc -eq 0 ]; then
        printf '  \033[32m✅ PASS\033[0m  %s\n' "$label"
    else
        printf '  \033[31m❌ FAIL\033[0m  %s\n' "$label"
        echo "$out" | tail -40 | sed 's/^/        /'
        FAILED=1
    fi
    return 0
}

# Легасі-сьюти друкують свій власний банер і завжди завершуються з кодом 0,
# навіть коли всередині були помилки. Тому перевіряємо саме банер.
run_suite() {
    local label="$1"; local script="$2"; local banner="$3"
    local out
    out="$("$PY" "$script" 2>&1)"
    if echo "$out" | grep -q "$banner"; then
        printf '  \033[32m✅ PASS\033[0m  %s\n' "$label"
    else
        printf '  \033[31m❌ FAIL\033[0m  %s\n' "$label"
        echo "$out" | grep -iE "error|fail|traceback|❌" | tail -25 | sed 's/^/        /'
        FAILED=1
    fi
    return 0
}

step "SYNDICATE — перевірка перед комітом"
echo "  python: $PY"

step "Тести"
run "pytest (усі тести каталогу tests/)" "$PY" -m pytest tests/ -q
run_suite "10 поверхів (наскрізний suite)" tests/test_10floors_architecture.py "ALL 10 SUITES"
run_suite "Sandbox (наскрізний suite)"      tests/sandbox_test.py              "ALL 8 SANDBOX"

step "Лінтер"
run "ruff F,E9,B (логіка й безпека)" "$RUFF" check --select F,E9,B --ignore E501,B008,B904 src deploy tests tools
run "ruff E,W    (стиль/пробіли)"    "$RUFF" check --select E,W   --ignore E501             src deploy tests tools
run "ruff C901   (складність)"       "$RUFF" check --select C901                           src deploy tests tools

step "Контракт API (клієнтська частина)"
run "api-contract.yaml відповідає коду" "$PY" tools/export_openapi.py --check

step "Vault (політики й скрипти)"
# Політики генеруються з src/vault_paths.py. Застарілий файл = агент отримає
# 403 на секреті, який читає на старті, — тому це ворота, а не побажання.
run "політики відповідають коду" "$PY" tools/vault_policies.py --check
run "vault_init.sh / vault_unseal.sh — синтаксис" bash -n deploy/scripts/vault_init.sh deploy/scripts/vault_unseal.sh

step "PostgreSQL (жива схема й SQL-шляхи)"
# SQL-гілки в src/ позначені "needs live DB": без справжньої бази вони не
# перевіряються взагалі. CI піднімає pgvector/pgvector:pg16 і задає
# EVA_TEST_DATABASE_URL (+ EVA_REQUIRE_LIVE_DB=1, щоб skip став помилкою).
# Локально ту саму роль виконує pgserver з requirements-dev.txt.
if [ -n "${EVA_TEST_DATABASE_URL:-}" ]; then
    run "жива схема + SQL-шляхи (EVA_TEST_DATABASE_URL)" "$PY" -m pytest tests/test_postgres_paths.py -q
elif [ -z "${EVA_SKIP_PGSERVER:-}" ] && "$PY" -c "import pgserver" >/dev/null 2>&1; then
    run "жива схема + SQL-шляхи (вбудований pgserver)" "$PY" -m pytest tests/test_postgres_paths.py -q
else
    printf '  \033[33mℹ️  INFO\033[0m  живого PostgreSQL немає (ані EVA_TEST_DATABASE_URL, ані pgserver)\n'
    printf '        SQL-шляхи в цій сесії не перевірено. CI: pgvector/pgvector:pg16 + EVA_REQUIRE_LIVE_DB=1\n'
fi

step "Гігієна репозиторію"
if [ -f docker-compose.yml ] && [ -f deploy/docker-compose.yml ]; then
    if cmp -s docker-compose.yml deploy/docker-compose.yml; then
        printf '  \033[32m✅ PASS\033[0m  docker-compose.yml синхронізований\n'
    else
        printf '  \033[31m❌ FAIL\033[0m  docker-compose.yml розійшовся з deploy/docker-compose.yml\n'
        FAILED=1
    fi
fi

if git rev-parse --git-dir >/dev/null 2>&1; then
    dirty="$(git status --porcelain --untracked-files=no)"
    if [ -z "$dirty" ]; then
        printf '  \033[33mℹ️  INFO\033[0m  робоча тека чиста\n'
    else
        printf '  \033[33mℹ️  INFO\033[0m  є незакомічені зміни:\n'
        echo "$dirty" | sed 's/^/        /'
    fi
fi

step "Підсумок"
if [ $FAILED -eq 0 ]; then
    printf '\n\033[32m🏆 УСІ ВОРОТА ЗЕЛЕНІ — можна комітити.\033[0m\n\n'
    exit 0
fi
printf '\n\033[31m⛔ Є ПРОВАЛИ — виправ перед комітом.\033[0m\n'
printf '   Не «лагодь» тест під себе: кожен тест фіксує реальний виправлений дефект.\n\n'
exit 1
