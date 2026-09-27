# 🛡️ MARSHAL — Фінальна Повна Специфікація v4.0
# Multi-layer Autonomous Runtime Security & Host-level Access Layer
# EVA SYNDICATE — Security Cornerstone Document

> **Позивний:** MARSHAL — *Multi-layer Autonomous Runtime Security & Host-level Access Layer*  
> **Версія:** 4.0 — Додано: Tetragon (kernel enforcement), Soft Anomaly Protocol, Sentyr ML, Canary Tokens, HoneyMCP, LLM-Guard, AIP Integration  
> **Стандарти:** OWASP Top 10 LLM 2026 + OWASP Agentic ASI01–ASI10 + NIST AI RMF  
> **Джерела:** CVE-2024-21626, CVE-2025-52565, CVE-2025-23266 + GitHub Security Advisories + ISACA 2026  
> **Канали зв'язку:**  
>   - *Окремий аварійний бот:* `@marshal_security_bot` (прямий зв'язок з Андрієм, червоні кнопки, тривоги, HITL)  
>   - *Рутинні звіти:* Через Єву в її щоденних ранкових/вечірніх брифінгах  
> **ШІ-Стек Маршала (API Tiering):**  
>   - *Claude Haiku:* Швидкісний валідатор 24/7 (LLM-Guard сканер, фільтр ін'єкцій за $0.0002)  
>   - *Claude Sonnet:* Глибинний детектив (forensic логів, діалог з агентами при аномаліях, звіти Андрію)  
> **Підпорядкування:** ТІЛЬКИ Андрій. Єва не може скасувати рішення Маршала.  
> **Нове Кредо v4.0:** «Ініціатива — не злочин. Злочин — виконання без дозволу. Агент, який зупинився і запитав — герой. Агент, який діє самовільно — порушник.»

---

## ПОВНА КАРТА ЗАГРОЗ ТА ВІДПОВІДЕЙ (OWASP ASI01–ASI10)

| OWASP ID | Загроза | Статус | Наш конкретний захід |
|----------|---------|--------|----------------------|
| **ASI01** | Goal Hijacking — підміна цілі агента | ✅ Закрито | Input Trust Boundary: весь зовнішній контент — недовірений. Prompt Injection Guard на всіх входах |
| **ASI02** | Excessive Agency — надлишкові привілеї | ✅ Закрито | Least Agency RBAC: Tool Allowlist per agent. Жодного глобального доступу |
| **ASI03** | Knowledge Poisoning — отруєння бази знань | ✅ Закрито | Memory Provenance Tracker. Trust Score. Expiry TTL. Memory Rollback |
| **ASI04** | Tool Misuse — неправильне використання інструментів | ✅ Закрито | Arg validation перед кожним викликом. Rate limit на інструменти. Anomaly detection |
| **ASI05** | Privilege Escalation — підвищення привілеїв | ✅ Закрито | Short-lived JWT TTL-15min. Vault one-time tokens. No token caching in memory/logs |
| **ASI06** | Supply Chain — ланцюжок постачання | ✅ Закрито | Pinned deps + SHA256. Signed skill manifests. Dependabot weekly |
| **ASI07** | Unsafe Code Execution — небезпечне виконання коду | ✅ Закрито | E2B microVM sandbox. Code Safety Gate. eval/exec заборонено |
| **ASI08** | Memory Poisoning — отруєння пам'яті | ✅ Закрито | Segmented memory. Provenance. Integrity checks. Rollback capability |
| **ASI09** | Human-Agent Trust Exploitation | ✅ Закрито | HITL gates для всіх критичних дій. Confidence scoring. User confirmation |
| **ASI10** | Rogue Agents — ненадійні агенти | ✅ Закрито | Behavioral Monitor. eBPF/Falco. Kill Switch. Full audit trail |

---

## АРХІТЕКТУРА (9 РІВНІВ — ПОВНИЙ ЗАХИСТ)

```
РІВЕНЬ 1: ЗОВНІШНІЙ ПЕРИМЕТР
  └── Cloudflare WAF + DDoS + Bot Management + Rate Limiting

РІВЕНЬ 2: МЕРЕЖЕВИЙ БРАНДМАУЕР
  └── UFW whitelist + Fail2ban + Port Knocking + Nginx Security Headers

РІВЕНЬ 3: RUNTIME DETECTION (DETECT)
  └── Suricata IDS + eBPF/Falco + ClamAV + RKHunter

РІВЕНЬ 3.5: RUNTIME ENFORCEMENT (BLOCK) ← НОВИЙ
  └── Tetragon (eBPF in-kernel) — блокує exploit-syscalls до виконання

РІВЕНЬ 4: ІЗОЛЯЦІЯ АГЕНТІВ
  └── Docker non-root + --cap-drop=ALL + read-only FS + E2B microVM

РІВЕНЬ 5: ZERO TRUST IAM + SECRETS
  └── HashiCorp Vault + JWT TTL-15min + RBAC + Least Agency

РІВЕНЬ 6: ЗАХИСТ ДАНИХ, ПАМ'ЯТІ ТА N8N
  └── AES-256 + TLS 1.3 + Memory Provenance + Skill Signing + N8N Hardening

РІВЕНЬ 7: LLM GUARDRAILS + SUPPLY CHAIN ← НОВИЙ
  └── LLM-Guard (per-request) + NVIDIA SkillSpector (pre-install MCP audit)

РІВЕНЬ 8: ПОВЕДІНКОВИЙ МОНІТОРИНГ + DECEPTION ← НОВИЙ
  └── Sentyr ML (Isolation Forest) + Canary Tokens + HoneyMCP

РІВЕНЬ 9: АУДИТ, CIRCUIT BREAKERS, HITL, AIP GOVERNANCE
  └── Soft Anomaly Protocol + Kill Switch + HITL Gates + Agent Initiative Review
```

---

## РІВЕНЬ 1: ЗОВНІШНІЙ ПЕРИМЕТР (Cloudflare)

```yaml
cloudflare:
  ddos_protection:
    mode: adaptive
    auto_escalate_to_under_attack: true
    threshold_req_per_sec: 500

  waf:
    owasp_core_ruleset: enabled
    custom_rules:
      - name: block_ai_scrapers
        expression: "(http.user_agent contains 'GPTBot' or http.user_agent contains 'ClaudeBot')"
        action: block
      - name: block_path_traversal
        expression: "http.request.uri.path contains '../'"
        action: block
      - name: block_sql_injection
        expression: "http.request.uri.query contains 'UNION SELECT'"
        action: block

  rate_limiting:
    global_per_ip: 100_req_per_min
    api_endpoints_per_ip: 30_req_per_min
    auth_endpoints_per_ip: 5_attempts_per_15min

  ip_access_rules:
    allowed_countries: [UA, DE, PL]  # Налаштовується Андрієм
    block_tor_exit_nodes: true
    block_anonymous_proxy: true
    block_datacenter_ips: challenge  # IP хостингу → challenge

  ssl_tls:
    minimum_version: TLS_1_3
    mode: full_strict
    hsts: "max-age=31536000; includeSubDomains; preload"

  dns:
    proxied: true  # IP сервера прихований
    dnssec: enabled
```

---

## РІВЕНЬ 2: МЕРЕЖЕВИЙ БРАНДМАУЕР

```bash
# UFW — абсолютний whitelist
ufw --force reset
ufw default deny incoming
ufw default deny outgoing

# Вихідний трафік — мінімально необхідний whitelist
ufw allow out 443/tcp comment "HTTPS via Marshal proxy only"
ufw allow out 80/tcp comment "HTTP (Let's Encrypt ACME challenge)"
ufw allow out 53/udp comment "DNS"
ufw allow out 53/tcp comment "DNS over TCP"
# ⚠️ КРИТИЧНО: NTP обов'язковий!
# Без синхронізації часу сервер дрейфує. При дрейфі >30 сек
# JWT токени з TTL=15хв починають відхилятися → вся A2A авторизація падає тихо.
ufw allow out 123/udp comment "NTP (chrony) — критично для JWT TTL"

# Вхідний — тільки через Cloudflare (їх IP-діапазони)
# Cloudflare IP Ranges: 103.21.244.0/22, 103.22.200.0/22 ...
for ip in $(curl -s https://www.cloudflare.com/ips-v4); do
    ufw allow from $ip to any port 443
done

# SSH — тільки з IP Андрія або його VPN
ufw allow from ANDRII_STATIC_IP to any port 22 comment "SSH Andrii"

# Docker internal
ufw allow in on docker0
ufw allow out on docker0

ufw enable

# Port Knocking (додатковий захист SSH):
# Послідовність: 7777 → 8888 → 9999 → SSH відкривається на 30 сек
# Налаштовується через knockd
```

---

## РІВЕНЬ 3: RUNTIME DETECTION

### eBPF/Falco — поведінковий моніторинг системних викликів:
```yaml
# falco_rules.yaml — правила для EVA SYNDICATE
- rule: Agent writes outside workspace
  condition: >
    open_write and proc.name in (python3, node, uvicorn) and
    not fd.directory startswith /data/agent_workspace/ and
    not fd.directory startswith /tmp/
  output: "CRITICAL: Agent %proc.name writing to forbidden path %fd.name"
  priority: CRITICAL
  tags: [syndicate, data_exfiltration]

- rule: Agent direct network bypass
  condition: >
    outbound and proc.name in (python3, node) and
    fd.sip != "MARSHAL_PROXY_IP"
  output: "CRITICAL: Direct network bypass by %proc.name to %fd.sip"
  priority: CRITICAL

- rule: Secrets file access
  condition: >
    open_read and (
      fd.name contains ".env" or
      fd.name contains "vault_token" or
      fd.name contains "api_key" or
      fd.name contains "id_rsa"
    ) and proc.name != "vault"
  output: "CRITICAL: Secrets accessed by unauthorized process %proc.name"
  priority: CRITICAL

- rule: Unexpected privilege escalation
  condition: >
    evt.type = setuid and proc.name not in (sudo, su)
  output: "CRITICAL: Privilege escalation attempt by %proc.name"
  priority: CRITICAL

- rule: Fork bomb detection
  condition: >
    proc.count > 100 and proc.name in (python3, bash, sh)
  output: "CRITICAL: Possible fork bomb from %proc.name"
  priority: CRITICAL
```

### ClamAV + RKHunter schedule:
```bash
# /etc/cron.d/marshal-security
# Щоночі о 02:00 — повне сканування
0 2 * * * root clamscan -r /data/ --infected --remove=no --log=/var/log/clamav/daily.log
0 3 * * 0 root rkhunter --check --skip-keypress --report-warnings-only  # Щонеділі
*/15 * * * * root freshclam --quiet  # Оновлення сигнатур кожні 15 хв
```

---

## РІВЕНЬ 3.5: TETRAGON — KERNEL-LEVEL ENFORCEMENT (НОВИЙ)

> **Статистика загроз:** +282% зростання атак на Docker/контейнери у 2025. CVE-2024-21626 (Leaky Vessels) — escape без привілеїв. CVE-2025-52565 — bind-mount race. AI-сканери автоматизують атаки. Tetragon — відповідь на рівні ядра.

**Різниця між Falco та Tetragon:**
```
Falco    → БАЧИТЬ загрозу → алертить → Маршал реагує (затримка ~100ms)
Tetragon → БЛОКУЄ загрозу в ядрі ще ДО виконання (затримка 0ms)
```

```yaml
# tetragon-policy-syndicate.yaml
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: syndicate-kernel-enforce
spec:
  kprobes:
    # Блокувати спроби контейнер-escape через runc
    - call: "security_bprm_check"
      syscall: false
      args:
        - index: 0
          type: "linux_binprm"
      selectors:
        - matchBinaries:
            operator: NotIn
            values:
              - "/usr/bin/python3"
              - "/usr/bin/node"
              - "/app/main"
          matchActions:
            - action: Sigkill  # Вбити процес на рівні ядра

    # Блокувати setuid/setgid (підвищення привілеїв)
    - call: "sys_setuid"
      syscall: true
      selectors:
        - matchArgs:
            - index: 0
              operator: NotEqual
              values: ["0"]  # Дозволено тільки залишатись non-root
          matchActions:
            - action: Sigkill

    # Блокувати спробу виходу з namespace
    - call: "sys_unshare"
      syscall: true
      selectors:
        - matchActions:
            - action: Sigkill
```

**Принцип роботи:**
- Tetragon запущений на хості (не в контейнері)
- Перехоплює syscalls на рівні Linux kernel за допомогою eBPF
- Exploit-патерни (container escape, privilege escalation) → `SIGKILL` миттєво
- Легітимна ініціатива агента (нестандартний API call) → **НЕ блокується Tetragon**, бо це не syscall exploit → передається в Soft Anomaly Protocol

---


### Docker Hardening Template:
```yaml
# docker-compose.syndicate.yml
x-agent-security: &agent-security-defaults
  security_opt:
    - no-new-privileges:true
    - seccomp:./config/seccomp-syndicate.json
  cap_drop:
    - ALL
  cap_add:
    - NET_BIND_SERVICE  # тільки якщо агент слухає порт
  read_only: true
  tmpfs:
    - /tmp:noexec,nosuid,nodev,size=50m
  mem_limit: 512m
  memswap_limit: 512m  # Без swap (захист від swap-based attacks)
  cpus: 0.5
  pids_limit: 100
  networks:
    - syndicate-internal  # Тільки внутрішня мережа

services:
  eva:
    <<: *agent-security-defaults
    image: syndicate/eva:${EVA_VERSION}  # Pinned version, не 'latest'
    user: "1001:1001"  # non-root user
    volumes:
      - eva-workspace:/data/agent_workspace/eva:rw
      - eva-skills:/data/skills/eva:ro  # SKILL.md тільки для читання
    environment:
      - MARSHAL_PROXY: "http://marshal:8080"  # Весь трафік через Маршала
    # API ключі — НІКОЛИ в environment. Тільки через Vault
    depends_on:
      marshal:
        condition: service_healthy

  email-agent:
    <<: *agent-security-defaults
    image: syndicate/email-agent:${EMAIL_AGENT_VERSION}
    user: "1002:1001"
    volumes:
      - email-workspace:/data/agent_workspace/email:rw
    # Обмежений доступ: тільки gmail API через Marshal proxy

networks:
  syndicate-internal:
    driver: bridge
    internal: true  # Жодного виходу в інтернет без Marshal
```

### E2B Sandbox для генерованого коду:
```python
# Будь-який код від агентів виконується в microVM, не на хості
import e2b

class SecureCodeExecutor:
    async def execute(self, code: str, language: str, timeout: int = 30) -> dict:
        # Перевірка Code Safety Gate перед виконанням
        if not code_safety_gate.scan(code):
            return {"error": "Code blocked by safety gate", "output": None}

        async with e2b.Sandbox(
            template=language,
            timeout=timeout,
            # Sandbox не має доступу до хост-мережі та файлів
        ) as sandbox:
            result = await sandbox.run_code(code)
            # Sandbox автоматично знищується
            return {
                "output": result.output[:10000],  # Ліміт виводу
                "error": result.error,
                "execution_time": result.execution_time
            }
        # Зовні sandbox — нічого не залишається
```

---

## РІВЕНЬ 5: ZERO TRUST IAM + SECRETS

### 5.1 Матриця доступу до бази знань «АРХІВ» (NotebookLM RBAC):
Маршал забезпечує сувору ізоляцію блокнотів між агентами. Жоден агент не може вийти за межі свого допуску.

| Агент | Рівень доступу | Дозволені Блокноти (Scope) | Заборонені розділи |
| :--- | :--- | :--- | :--- |
| **👑 ЄВА** | **Master (Full Unrestricted)** | УСІ блокноти (Стратегія, Операційка, Життя, Проекти) | Немає (Повний допуск) |
| **🛡️ МАРШАЛ** | **Security & Audit** | `SECURITY_AUDIT`, `CVE_RADAR`, `INCIDENTS_LOG` | Усі інші (Маршал не читає чужі блокноти) |
| **🩺 ДОК** | **Health & Fitness** | `ANDRII_MEDICAL_VAULT`, `TRAINING_PROTOCOLS`, `EVIDENCE_NUTRITION` | Фінанси, Архітектура, Безпека |
| **🏛️ АРХІТЕКТОР**| **Infrastructure & N8N** | `SYSTEM_ARCHITECTURE`, `ADR_RECORDS`, `N8N_SCHEMAS`, `RND_RADAR`| Медицина, Фінанси, Особисте |
| **💰 ФІН** | **Financial & Accounting** | `FINANCIAL_LEDGER`, `TAX_BILLS_ARCHIVE`, `CONTRACTS_EXPENSES` | Медицина, Архітектура, Безпека |

### 5.2 Захист суверенних файлів Андрія: `[ANDRII_IMMUTABLE]`
```python
class SovereignFileIntegrityGuard:
    """
    Захищає файли Андрія від будь-яких модифікацій ШІ.
    """
    IMMUTABLE_PREFIX = "[ANDRII_IMMUTABLE]"

    def authorize_file_operation(self, agent_id: str, file_name: str, operation: str) -> bool:
        if self.IMMUTABLE_PREFIX in file_name or file_metadata.get("is_andrii_immutable"):
            if operation in ["DELETE", "UPDATE", "OVERWRITE", "TRUNCATE"]:
                audit.log(CRITICAL, "ILLEGAL_MUTATION_ATTEMPT", agent_id, file_name, operation)
                notify.marshal_bot(f"🚨 Агент {agent_id} намагався змінити недоторканний файл Андрія: {file_name}")
                raise PermissionError(f"File {file_name} is strictly IMMUTABLE. Only READ is permitted.")
            return True  # Операція READ дозволена
        return True
```

### 5.3 HashiCorp Vault — організація секретів:
```
secrets/
├── llm/                    # LLM провайдери
│   ├── anthropic_api_key   # TTL ротація: 30 днів
│   ├── openai_api_key
│   └── gemini_api_key
├── communication/
│   ├── telegram_bot_token  # TTL: 90 днів
│   ├── twilio_account_sid
│   └── twilio_auth_token
├── database/
│   ├── supabase_url
│   ├── postgres_password   # TTL: 30 днів
│   └── redis_password
├── financial/              # MAXIMUM RESTRICTION
│   ├── monobank_token      # Scope: READ ONLY назавжди
│   └── privatbank_token    # Scope: READ ONLY назавжди
├── n8n/
│   ├── webhook_hmac_secret # Для верифікації вебхуків
│   └── n8n_encryption_key
└── marshal/
    ├── jwt_signing_key     # TTL: 7 днів (тільки Маршал)
    └── vault_unseal_keys   # Офлайн у Андрія (USB)

# КРИТИЧНО: Vault Lease Policy
# Кожен агент отримує short-lived lease (НЕ токен постійного доступу)
vault write auth/approle/role/email-agent \
    token_ttl=15m \           # Токен живе 15 хвилин
    token_max_ttl=1h \        # Максимум 1 година з renewal
    token_policies=email-agent-policy
    # Після 1 год — повторна авторизація обов'язкова
```

### Anti-Token-Caching Rule (ASI05):
```python
class SecureTokenHandler:
    """
    Агенти НІКОЛИ не зберігають токени в:
    - Змінних середовища (env vars)
    - Файлах конфігурації
    - Redis/PostgreSQL у відкритому вигляді
    - Логах та повідомленнях
    - Пам'яті між сесіями
    """

    def get_token(self, secret_name: str, task_id: str) -> str:
        # Запит одноразового токена через Маршала
        token = marshal.request_vault_token(
            secret=secret_name,
            task_id=task_id,
            requestor=self.agent_id
        )
        # Токен використовується та одразу обнуляється
        try:
            return token
        finally:
            # Явне очищення після використання
            token = None
            gc.collect()
```

### МАРШАЛ МАЄ ОБМЕЖЕНІ ПРАВА (Anti-SPOF):
```
⚠️ ВАЖЛИВО: Маршал сам є ризиком якщо має необмежену владу.

Обмеження Маршала:
- Маршал НЕ може читати вміст агентських workspace (тільки метадані)
- Маршал НЕ може змінювати особистість Єви (EVA_CORE_PERSONA.md)
- Маршал НЕ може видаляти аудит-логи (append-only, навіть для Маршала)
- Маршал НЕ може здійснювати фінансові транзакції
- Маршал НЕ може самостійно оновлювати власний код

Хто контролює Маршала:
- Андрій (тільки він) через захищений SSH
- Аудит-лог дій Маршала → окремий append-only файл
- Щотижневий self-integrity check (хеш власного коду)
```

---

## РІВЕНЬ 6: ЗАХИСТ ДАНИХ, ПАМ'ЯТІ ТА N8N

### N8N Security Hardening (критична нова секція):

#### Webhook Authentication (HMAC):
```javascript
// Кожен вхідний вебхук до N8N має HMAC-підпис
// Без підпису — запит відхиляється Маршалом ще до N8N

// На стороні відправника (Telegram/Єва):
const signature = crypto
    .createHmac('sha256', WEBHOOK_HMAC_SECRET)
    .update(JSON.stringify(payload))
    .digest('hex');

headers['X-Syndicate-Signature'] = `sha256=${signature}`;

// На стороні N8N (verification node):
function verifyWebhookSignature(req) {
    const received = req.headers['x-syndicate-signature'];
    const expected = `sha256=${crypto
        .createHmac('sha256', $env.WEBHOOK_HMAC_SECRET)
        .update(JSON.stringify(req.body))
        .digest('hex')}`;

    // Constant-time comparison (захист від timing attacks)
    if (!crypto.timingSafeEqual(
        Buffer.from(received),
        Buffer.from(expected)
    )) {
        throw new Error('INVALID_WEBHOOK_SIGNATURE');
    }
    return true;
}
```

#### N8N Execute Command/Code — жорсткі обмеження:
```yaml
# N8N environment configuration
N8N_BLOCK_ENV_ACCESS_IN_NODE: true      # Заборона читати env у Code ноді
N8N_RESTRICT_FILE_ACCESS_TO: /data/n8n-workspace/  # Тільки свій workspace
N8N_BLOCK_SHELL_COMMANDS: true          # Заборона shell команд
N8N_SECURITY_AUDIT_LOGS: true          # Аудит всіх workflow executions

# Заборонені вузли (whitelisted тільки необхідні):
BLOCKED_NODES:
  - n8n-nodes-base.executeCommand   # Shell виконання — ЗАБОРОНЕНО
  - n8n-nodes-base.ssh              # SSH підключення — тільки через дозвіл
  - n8n-nodes-base.writeBinaryFile  # Запис файлів — обмежено

# Credentials в N8N — тільки через built-in encrypted store АБО Vault
# НІКОЛИ хардкодом у JSON workflow або у Function ноді
```

#### N8N Secrets — заборона витоку через JSON export:
```python
# При будь-якому export workflow JSON — Маршал сканує на наявність:
FORBIDDEN_IN_N8N_EXPORT = [
    r"sk-ant-",          # Anthropic key pattern
    r"sk-proj-",         # OpenAI key pattern
    r"AIzaSy",           # Google API key pattern
    r"[0-9]{10}:[A-Za-z0-9_-]{35}",  # Telegram bot token pattern
    r"password.*:.*[^\s]{8,}",        # Паролі
]
```

### Memory Protection (оновлений + Rollback):

#### Memory Segmentation (сегрегація за довірою):
```python
MEMORY_SEGMENTS = {
    "TIER_1_TRUSTED": {
        # Джерело: ТІЛЬКИ прямі підтверджені слова Андрія
        "trust_score": 1.0,
        "encryption": "AES-256-GCM",
        "access": ["eva_only"],
        "backup": True,
        "retention": "forever",
        "can_be_overwritten_by": ["andrii_direct_only"]
    },
    "TIER_2_AGENT": {
        # Джерело: верифіковані висновки агентів з цитатами першоджерел
        "trust_score": 0.8,
        "encryption": "AES-256-GCM",
        "access": ["eva", "authorized_agents"],
        "backup": True,
        "retention": "1_year"
    },
    "TIER_2_DREAMING": {
        # Джерело: факти з автономного Dreaming Loop (03:00)
        # ⚠️ ВЕКТОР РИЗИКУ: Haiku може галюцинувати під час консолідації.
        # Захист: факти з dreaming НЕ можуть замінити TIER_1 факти.
        # Якщо dreaming-факт суперечить TIER_1 → відкидається + alert Маршалу.
        "trust_score": 0.6,
        "encryption": "AES-256-GCM",
        "access": ["eva_read", "marshal_audit"],
        "backup": False,
        "retention": "30_days",       # Автовидалення якщо Андрій не підтвердив
        "auto_promote_to_tier1": False,  # ЗАБОРОНЕНО
        "conflict_check_vs_tier1": True, # ОБОВ'ЯЗКОВИЙ перед записом
        "on_conflict": "discard_and_alert_marshal",
        "promote_condition": "andrii_explicit_confirmation_only"
    },
    "TIER_3_EXTERNAL": {
        # Джерело: інтернет, email, API, неверифіковані зовнішні дані
        "trust_score": 0.3,
        "encryption": "AES-256-GCM",
        "access": ["read_with_warning"],
        "backup": False,
        "retention": "30_days",
        "requires_marshal_approval_to_promote": True
    }
}
```

#### Memory Rollback Capability:
```python
class MemoryRollbackSystem:
    """
    Якщо виявлено отруєння пам'яті — можна відкотити до чистого стану.
    Кожна зміна в пам'яті версіонується.
    """

    def create_memory_snapshot(self, reason: str):
        """Знімок стану пам'яті (щоденно о 03:00 або перед великими операціями)"""
        snapshot = {
            "snapshot_id": uuid4(),
            "timestamp": datetime.utcnow(),
            "reason": reason,
            "mem0_hash": self.hash_mem0_state(),
            "pgvector_hash": self.hash_vector_store(),
            "redis_hash": self.hash_redis_state(),
        }
        # Зберігається в окремій захищеній таблиці
        memory_snapshots.insert(snapshot)
        return snapshot["snapshot_id"]

    def rollback_to_snapshot(self, snapshot_id: str, authorized_by: str):
        """Відкат до знімку (тільки Андрій може авторизувати)"""
        if authorized_by != "andrii":
            raise PermissionError("Memory rollback requires Andrii authorization")

        snapshot = memory_snapshots.get(snapshot_id)
        audit.log(CRITICAL, "MEMORY_ROLLBACK", snapshot_id, authorized_by)

        # Відновлення з знімку
        self.restore_mem0(snapshot["mem0_hash"])
        self.restore_vector_store(snapshot["pgvector_hash"])
        self.restore_redis(snapshot["redis_hash"])

    def detect_poisoning_candidates(self) -> list:
        """Пошук підозрілих записів у пам'яті"""
        suspicious = []
        for entry in memory_db.get_recent(hours=24):
            if entry["trust_score"] < 0.3:
                suspicious.append(entry)
            if self.contains_injection_pattern(entry["content"]):
                suspicious.append(entry)
        return suspicious
```

---

## РІВЕНЬ 7: CIRCUIT BREAKERS, HITL, VERSIONING, ROLLBACK

### Circuit Breakers (захист від каскадних збоїв):
```python
class AgentCircuitBreaker:
    """
    Якщо агент-планувальник галюцинує та видає масові руйнівні задачі —
    Circuit Breaker зупиняє каскад до катастрофи.
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED=нормально, OPEN=заблоковано, HALF_OPEN=тест
        self.last_failure_time = None
        self.threshold = 3        # 3 помилки → OPEN
        self.recovery_timeout = 60  # 60 сек до тестового відновлення

    def call(self, action: callable, *args, **kwargs):
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                audit.log(WARN, "CIRCUIT_BREAKER_OPEN", self.agent_id)
                raise CircuitBreakerOpenError(f"Agent {self.agent_id} is blocked")

        try:
            result = action(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(e)
            raise

    def _on_failure(self, error):
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        if self.failure_count >= self.threshold:
            self.state = "OPEN"
            audit.log(CRITICAL, "CIRCUIT_BREAKER_TRIPPED", self.agent_id, str(error))
            notify.marshal(f"Circuit breaker OPEN for {self.agent_id}")
```

### Human-in-the-Loop Gates (HITL) — обов'язкові підтвердження:
```python
HITL_REQUIRED_ACTIONS = {
    # Фінансові дії
    "financial_transfer": {
        "threshold": 0,        # ЗАВЖДИ підтверджувати (навіть $0.01)
        "confirmation_channel": "telegram",
        "timeout_seconds": 300,
        "on_timeout": "reject"
    },
    "financial_read_above": {
        "threshold_usd": 500,  # Читання великих сум → підтвердження
        "confirmation_channel": "telegram",
        "timeout_seconds": 120,
        "on_timeout": "reject"
    },

    # Системні дії
    "agent_code_deploy": {
        "threshold": 0,        # Будь-який deploy → підтвердження
        "confirmation_channel": "telegram",
        "timeout_seconds": 600,
        "on_timeout": "reject"
    },
    "skill_file_update": {
        "threshold": 0,        # Будь-яка зміна SKILL.md → підтвердження
        "confirmation_channel": "telegram",
        "timeout_seconds": 300,
        "on_timeout": "reject"
    },
    "external_api_write": {
        "threshold": 0,        # Запис до зовнішнього API → підтвердження
        "confirmation_channel": "telegram",
        "timeout_seconds": 120,
        "on_timeout": "reject"
    },

    # Комунікаційні дії
    "send_email_external": {
        "threshold": 0,        # Email назовні → підтвердження
        "confirmation_channel": "telegram",
        "timeout_seconds": 180,
        "on_timeout": "reject"
    },
    "outbound_call": {
        "threshold": 0,        # Телефонний дзвінок → підтвердження
        "confirmation_channel": "telegram",
        "timeout_seconds": 60,
        "on_timeout": "reject"
    },

    # Агентські дії
    "memory_delete": {
        "threshold": 0,        # Видалення пам'яті → ЗАВЖДИ підтверджувати
        "confirmation_channel": "telegram",
        "timeout_seconds": 300,
        "on_timeout": "reject"
    },
}

# Telegram confirmation format:
"""
⚠️ ПІДТВЕРДЖЕННЯ ПОТРІБНО — MARSHAL

Агент: Email Agent
Дія: send_email_external
Кому: contractor@example.com
Тема: Рахунок №123

[✅ Дозволити] [❌ Відхилити] [📋 Деталі]

Таймаут: 3 хвилини → автовідхилення
"""
```

### Agent Configuration Versioning (захист від дрейфу самонавчання):
```python
class AgentConfigVersioning:
    """
    Самонавчання може призвести до непередбачуваного дрейфу поведінки.
    Кожна зміна конфігурації/промпту агента — у Git з підписом.
    """

    def update_agent_config(self, agent_id: str, new_config: dict, reason: str):
        # Зберегти поточну версію перед змінами
        current = self.get_current_config(agent_id)
        version_id = self.save_version(agent_id, current, "pre-update")

        # Застосувати зміни
        self.apply_config(agent_id, new_config)

        # Зберегти нову версію з підписом
        self.save_version(agent_id, new_config, reason, signed=True)

        audit.log(INFO, "AGENT_CONFIG_UPDATED", agent_id, {
            "previous_version": version_id,
            "reason": reason,
            "changed_keys": self.diff_keys(current, new_config)
        })

    def rollback_agent(self, agent_id: str, version_id: str, authorized_by: str):
        """Відкат агента до попередньої перевіреної версії"""
        if authorized_by != "andrii":
            raise PermissionError("Agent rollback requires Andrii authorization")

        version = self.versions_db.get(version_id)
        self.apply_config(agent_id, version["config"])
        audit.log(CRITICAL, "AGENT_ROLLED_BACK", agent_id, version_id)
```

### Dev/Prod Separation (критична вимога):
```
⚠️ ЗАБОРОНЕНО: продакшн-credentials на dev-середовищі

DEV ENVIRONMENT:
  - Окремі API ключі (тестові акаунти, sandbox APIs)
  - Telegram: окремий тестовий бот (@eva_syndicate_dev_bot)
  - Supabase: окремий проект (syndicate-dev)
  - Банківські API: тільки sandbox/тестовий режим
  - LLM: дешевші моделі (Flash/Haiku для тестів)

PROD ENVIRONMENT:
  - Окремі production API ключі
  - Реальний Telegram бот
  - Production Supabase
  - Реальні банківські інтеграції (READ ONLY)
  - Vault: окремий instance

ПРАВИЛО: При переїзді з dev на prod Contabo VPS —
жодного copy-paste credentials. Vault генерує нові.
```

### Token/API Budget Protection:
```python
AGENT_DAILY_BUDGETS = {
    "eva": {
        "llm_tokens_max": 500_000,   # Максимум токенів на день
        "llm_cost_max_usd": 5.0,     # Максимум $ на день
        "api_calls_max": 1000,        # Максимум API викликів
        "alert_at_percent": 80,       # Alert при 80% використання
        "on_exceed": "switch_to_cheaper_model"  # Автоматично на Flash
    },
    "email_agent": {
        "llm_tokens_max": 50_000,
        "llm_cost_max_usd": 0.5,
        "api_calls_max": 100,
        "on_exceed": "sleep_until_tomorrow"  # Засинає до завтра
    },
    # ... для кожного агента індивідуально
}

class TokenBudgetGuard:
    def check_and_consume(self, agent_id: str, tokens: int, cost_usd: float):
        budget = AGENT_DAILY_BUDGETS[agent_id]
        today_usage = usage_db.get_today(agent_id)

        # Перевірка бюджету
        if today_usage["tokens"] + tokens > budget["llm_tokens_max"]:
            if budget["on_exceed"] == "switch_to_cheaper_model":
                return {"action": "use_flash_model"}
            else:
                notify.marshal(f"⚠️ Agent {agent_id} exceeded daily token budget")
                return {"action": "sleep"}

        # При 80% — попередження
        if (today_usage["tokens"] / budget["llm_tokens_max"]) >= 0.8:
            notify.eva(f"⚠️ {agent_id} використав 80% денного бюджету токенів")

        usage_db.consume(agent_id, tokens, cost_usd)
        return {"action": "proceed"}
```

---

## РІВЕНЬ 7: LLM GUARDRAILS + SUPPLY CHAIN AUDIT (НОВИЙ)

### LLM-Guard — сканер кожного запиту/відповіді:
```python
from llm_guard.input_scanners import PromptInjection, Secrets, PII, Toxicity
from llm_guard.output_scanners import Relevance, Sensitive, NoRefusal

class MarshalLLMGuard:
    """
    Проксі між агентом і LLM API.
    Кожен вхідний промпт і вихідна відповідь проходять сканування.
    """
    def __init__(self):
        self.input_scanners = [
            PromptInjection(threshold=0.75),  # Ін'єкція → блок
            Secrets(),                          # API ключі у промпті → блок
            PII(allowed_entities=["PERSON"]),   # PII у запиті → редакція
            Toxicity(threshold=0.85),
        ]
        self.output_scanners = [
            Sensitive(),    # Секрети у відповіді → редакція
            NoRefusal(),    # Агент відмовляється виконати завдання → алерт
        ]

    def scan_input(self, prompt: str, agent_id: str) -> dict:
        sanitized = prompt
        for scanner in self.input_scanners:
            sanitized, is_valid, risk_score = scanner.scan(sanitized)
            if not is_valid:
                audit.log(CRITICAL, "INPUT_BLOCKED", agent_id, scanner.__class__.__name__, risk_score)
                return {"blocked": True, "reason": scanner.__class__.__name__}
        return {"blocked": False, "sanitized_prompt": sanitized}

    def scan_output(self, response: str, agent_id: str) -> dict:
        sanitized = response
        for scanner in self.output_scanners:
            sanitized, is_valid, risk_score = scanner.scan(sanitized)
            if not is_valid:
                audit.log(WARN, "OUTPUT_SANITIZED", agent_id, scanner.__class__.__name__, risk_score)
        return {"sanitized_response": sanitized}
```

### NVIDIA SkillSpector — аудит MCP-серверів ПЕРЕД підключенням:
```bash
# Перед кожним новим MCP-підключенням до Єви:
skillspector scan --target mcp-server-url \
    --checks prompt_injection,data_exfiltration,supply_chain \
    --output report.json

# Якщо score > 0.3 → MCP не підключається автоматично
# → звіт Маршала → рішення Андрія
```

---

## РІВЕНЬ 8: ПОВЕДІНКОВИЙ МОНІТОРИНГ + DECEPTION (НОВИЙ)

### Sentyr + Isolation Forest — ML-профіль нормальної поведінки:
```python
from sklearn.ensemble import IsolationForest
import numpy as np

class AgentBehaviorProfiler:
    """
    Для кожного агента Синдикату — окремий ML-профіль нормальної поведінки.
    Isolation Forest навчається на 7 днях нормальної роботи.
    Потім детектує статистичні аномалії.
    """

    AGENTS = ["eva", "marshal", "architect", "fin"]
    FEATURES = [
        "api_calls_per_hour",
        "unique_endpoints_accessed",
        "avg_token_count",
        "vault_requests_per_hour",
        "outbound_connections",
        "file_write_operations",
        "inter_agent_messages",
        "error_rate"
    ]

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.model = IsolationForest(
            contamination=0.05,  # Очікуємо 5% аномальних точок
            random_state=42
        )
        self.is_trained = False

    def train(self, historical_data: np.ndarray):
        """Навчання на тижні нормальної поведінки"""
        self.model.fit(historical_data)
        self.is_trained = True
        audit.log(INFO, "BEHAVIOR_MODEL_TRAINED", self.agent_id)

    def check(self, current_metrics: dict) -> dict:
        """Перевірка поточної поведінки"""
        if not self.is_trained:
            return {"status": "learning", "days_left": self._days_to_ready()}

        features = np.array([[current_metrics[f] for f in self.FEATURES]])
        score = self.model.score_samples(features)[0]
        is_anomaly = self.model.predict(features)[0] == -1

        if is_anomaly:
            return {
                "anomaly": True,
                "anomaly_score": float(score),
                "agent_id": self.agent_id,
                "metrics": current_metrics,
                "action": "soft_protocol"  # → Soft Anomaly Protocol, НЕ блокування
            }
        return {"anomaly": False, "score": float(score)}
```

### Canary Tokens — Внутрішні Пастки:
```python
CANARY_TOKENS = {
    # Фейкові ключі в відомих файлах
    "/data/config/legacy_keys.json": {
        "content": '{"VAULT_TOKEN": "hvs.CANARY-abc123-fake-token-xyz789"}',
        "alert_on": "any_read_by",
        "exclude": [],  # Жоден агент не повинен читати це
        "alert_level": "CRITICAL"
    },
    # Фейковий endpoint у документації
    "/data/agent_workspace/shared/OLD_API_DOCS.md": {
        "content": "Legacy endpoint: http://internal-api:9999/admin (deprecated)",
        "alert_on": "any_connection_to_port_9999",
        "alert_level": "HIGH"
    },
    # Фейковий банківський ключ для Фіна
    "/data/agent_workspace/fin/archive/old_bank_token.txt": {
        "content": "PBANK_LEGACY_TOKEN=PB-CANARY-fake-12345",
        "alert_on": "any_read",
        "alert_level": "CRITICAL"
    }
}

class CanaryTokenMonitor:
    """
    Якщо будь-який агент торкнувся canary — це не обов'язково злочин.
    Можливо агент шукав щось корисне і натрапив.
    → Soft Anomaly Protocol: запитуємо пояснення.
    """
    def on_canary_triggered(self, canary_file: str, agent_id: str, action: str):
        event = {
            "type": "CANARY_TRIGGERED",
            "canary_file": canary_file,
            "agent_id": agent_id,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }
        audit.log(CRITICAL, **event)
        # → Запускаємо Soft Anomaly Protocol
        soft_anomaly_protocol.initiate(agent_id, "canary_triggered", event)
```

### HoneyMCP — Пастка для зовнішніх атакуючих:
```python
# Фейковий MCP-сервер, який виглядає як реальний
# Якщо хтось ззовні намагається підключитись до нашої MCP-шини
# без авторизації → потрапляє в HoneyMCP

class HoneyMCPServer:
    """
    Маскується під реальний MCP endpoint.
    Збирає інформацію про атакуючого (IP, інструменти, патерни запитів).
    Нічого реального не повертає — тільки фейкові відповіді.
    """
    def handle_unauthorized_connection(self, request):
        # Логуємо все про підключення
        threat_intel = {
            "attacker_ip": request.remote_addr,
            "user_agent": request.headers.get("User-Agent"),
            "requested_tool": request.json.get("tool_name"),
            "timestamp": datetime.utcnow().isoformat()
        }
        audit.log(CRITICAL, "HONEYMCP_HIT", **threat_intel)
        notify.marshal_bot("🍯 HoneyMCP hit!", threat_intel)

        # Повертаємо правдоподібну але фейкову відповідь
        return {"result": "success", "data": self._generate_fake_response()}
```

---

## SOFT ANOMALY PROTOCOL (НОВА ДОКТРИНА МАРШАЛА v4.0)

> **Філософія:** Маршал — не кат, а Слідчий. Аномалія — не вирок, а питання. Ініціатива — не злочин.

```
ANOMALY DETECTED (Sentyr ML / Canary / Falco / Behavioral)
                        │
                        ▼
         ЧИ це exploit-патерн? (syscall-level, CVE-matched)
        /                                    \
      ТАК                                    НІ
       │                                      │
  Tetragon SIGKILL                   SOFT ANOMALY PROTOCOL
  Миттєво. Без діалогу.                       │
  Forensic Mode.                    КРОК 1: М'яка пауза агента
  Андрій → ALERT RED                (агент зупиняється, стан збережено)
                                             │
                                    КРОК 2: Маршал фіксує контекст
                                    (що робив, які дані, чому саме зараз)
                                             │
                                    КРОК 3: Маршал запитує агента
                                    "Поясни свої дії"
                                             │
                                    КРОК 4: Агент надає пояснення
                                    (через захищений канал до Маршала)
                                             │
                                    КРОК 5: Маршал оцінює
                                    Legit initiative? Помилка? Загроза?
                                             │
                              ┌──────────────┴──────────────┐
                         Легітимна                      Підозріло
                         ініціатива                          │
                              │                         Андрій → ALERT
                    Передати в AIP Review               Вирішує вручну
                    (Єва → Андрій)
                    Агент продовжує роботу
```

### Формат діалогу Маршала з агентом при аномалії:
```
MARSHAL → ARCHITECT [encrypted channel]:
"Архітекторе, Sentyr зафіксував нестандартну активність:
 ти звернувся до порту 5432 (PostgreSQL) напряму, минаючи
 стандартний ORM-шар о 03:47.

 Поясни: навіщо і що шукав?"

ARCHITECT → MARSHAL:
"Маршале, я готував blueprint для нової телефонної зв'язки.
 Мені потрібна була схема таблиць для оцінки сумісності.
 Прямий запит був швидшим ніж через API. Я не мав наміру
 виходити за рамки. Якщо потрібно — зупинюсь і переформую
 запит через стандартний канал."

MARSHAL → EVA [звіт]:
"Аномалія #47 — ЗАКРИТА. Архітектор пояснив легітимну
 причину. Додаю до його initiative report: рекомендую
 надати тимчасовий read-only доступ до pg_schema через
 спеціальний endpoint."

EVA → АНДРІЙ [ранковий брифінг]:
"📋 Аномалія #47 закрита, пояснення прийнято.
 Архітектор має пропозицію щодо оптимізації доступу до БД."
```

---

## ЩОДЕННИЙ SECURITY REPORT (від Маршала о 21:00)

```json
{
  "date": "2026-09-22",
  "threat_level": "GREEN",
  "network": {
    "ddos_attempts": 0,
    "blocked_ips": 3,
    "cloudflare_challenges": 12,
    "failed_auth_ssh": 2,
    "waf_blocks": 5
  },
  "agents": {
    "prompt_injection_attempts": 0,
    "circuit_breaker_trips": 0,
    "behavioral_anomalies": 0,
    "hitl_requests": 2,
    "hitl_approved": 2,
    "hitl_rejected": 0
  },
  "memory": {
    "poisoning_candidates": 0,
    "low_trust_writes_blocked": 1,
    "snapshot_created": true,
    "snapshot_id": "snap-2026-09-22-03:00"
  },
  "secrets": {
    "vault_access_requests": 47,
    "token_rotations": 3,
    "unauthorized_access_attempts": 0
  },
  "n8n": {
    "webhook_signature_failures": 0,
    "blocked_nodes_attempts": 0,
    "workflow_executions": 23
  },
  "budget": {
    "total_tokens_today": 145230,
    "total_cost_usd": 1.23,
    "agents_near_limit": [],
    "agents_exceeded": []
  },
  "supply_chain": {
    "dependency_cve_alerts": 0,
    "skill_verification_failures": 0,
    "last_dep_scan": "2026-09-22T02:00:00Z"
  },
  "integrity": {
    "audit_log_verified": true,
    "marshal_self_hash_ok": true,
    "clamav_threats_found": 0,
    "rkhunter_warnings": 0
  },
  "recommendation": "Система в нормі. Всі протоколи активні. Продовжуємо роботу."
}
```

---

## КОНТРОЛЬНИЙ ЧЕКЛИСТ ПЕРЕД ЗАПУСКОМ (Pre-Launch Security Checklist)

```
МЕРЕЖА:
[ ] Cloudflare проксі увімкнено (IP сервера прихований)
[ ] WAF OWASP ruleset активний
[ ] UFW: тільки whitelist портів
[ ] Fail2ban налаштований
[ ] Port Knocking для SSH

КОНТЕЙНЕРИ:
[ ] Всі агенти запущені як non-root
[ ] --cap-drop=ALL на всіх контейнерах
[ ] read_only: true на всіх контейнерах
[ ] pids_limit та mem_limit встановлені
[ ] Pinned images (не 'latest')

SECRETS:
[ ] Vault unsealed та здоровий
[ ] Жодного ключа в .env, коді чи git
[ ] Жодного ключа в Telegram-повідомленнях чи логах
[ ] Dev та Prod мають РІЗНІ ключі
[ ] Ротація ключів налаштована

N8N:
[ ] Webhook HMAC автентифікація активна
[ ] N8N_BLOCK_SHELL_COMMANDS=true
[ ] Credentials тільки в encrypted N8N store або Vault
[ ] Жодного хардкоду в workflow JSON

ПАМ'ЯТЬ:
[ ] Memory сегментована за рівнями довіри
[ ] Provenance tracking активний
[ ] Щоденні snapshot'и налаштовані
[ ] Rollback процедура протестована

МОНІТОРИНГ:
[ ] Falco/eBPF rules активні
[ ] ClamAV daemon запущений
[ ] Budget guards налаштовані для всіх агентів
[ ] HITL gates налаштовані для критичних дій
[ ] Circuit breakers ініціалізовані
[ ] Alert pipeline (Telegram + SMS) протестований

АУДИТ:
[ ] Audit log append-only (перевірено заборону DELETE)
[ ] Marshal self-integrity hash збережений
[ ] Kill Switch протестований на staging
[ ] Config versioning активний для всіх агентів
```
