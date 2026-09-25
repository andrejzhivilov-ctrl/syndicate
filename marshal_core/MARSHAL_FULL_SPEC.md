# 🛡️ MARSHAL — Фінальна Повна Специфікація v3.1
# Multi-layer Autonomous Runtime Security & Host-level Access Layer
# EVA SYNDICATE — Security Cornerstone Document

> **Позивний:** MARSHAL — *Multi-layer Autonomous Runtime Security & Host-level Access Layer*  
> **Версія:** 3.1 (додано виділений бот та двоярусний AI-рушій Haiku/Sonnet)  
> **Стандарти:** OWASP Top 10 LLM 2026 + OWASP Agentic ASI01–ASI10 + NIST AI RMF  
> **Джерела:** Реальні CVE (OpenClaw, Hermes Agent, LiteLLM, EchoLeak) + GitHub Security Advisories + ISACA 2026  
> **Канали зв'язку:**  
>   - *Окремий аварійний бот:* `@marshal_security_bot` (прямий зв'язок з Андрієм, червоні кнопки, тривоги, HITL)  
>   - *Рутинні звіти:* Через Єву в її щоденних ранкових/вечірніх брифінгах  
> **ШІ-Стек Маршала (API Tiering):**  
>   - *Claude Haiku:* Швидкісний валідатор 24/7 (сканування ін'єкцій, миттєвий фільтр за $0.0002)  
>   - *Claude Sonnet:* Глибинний детектив (розбір складних атак, forensic логів, алерти для Андрія)  
> **Підпорядкування:** ТІЛЬКИ Андрій. Єва не може скасувати рішення Маршала.  
> **Кредо:** «Не довіряй нікому. Перевіряй все. Блокуй при найменшому сумніві.»

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

## АРХІТЕКТУРА (7 РІВНІВ + НОВІ КРИТИЧНІ БЛОКИ)

```
РІВЕНЬ 1: ЗОВНІШНІЙ ПЕРИМЕТР
  └── Cloudflare WAF + DDoS + Bot Management + Rate Limiting

РІВЕНЬ 2: МЕРЕЖЕВИЙ БРАНДМАУЕР
  └── UFW whitelist + Fail2ban + Port Knocking + Nginx Security Headers

РІВЕНЬ 3: RUNTIME DETECTION
  └── Suricata IDS + eBPF/Falco + ClamAV + RKHunter

РІВЕНЬ 4: ІЗОЛЯЦІЯ АГЕНТІВ
  └── Docker non-root + --cap-drop=ALL + read-only FS + E2B microVM

РІВЕНЬ 5: ZERO TRUST IAM + SECRETS
  └── HashiCorp Vault + JWT TTL-15min + RBAC + Least Agency

РІВЕНЬ 6: ЗАХИСТ ДАНИХ, ПАМ'ЯТІ ТА N8N
  └── AES-256 + TLS 1.3 + Memory Provenance + Skill Signing + N8N Hardening

РІВЕНЬ 7: АУДИТ, CIRCUIT BREAKERS, HITL, ROLLBACK
  └── Behavioral Monitor + Kill Switch + HITL Gates + Config Versioning
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

# Вихідний трафік — тільки через проксі Маршала
ufw allow out 443/tcp comment "HTTPS via Marshal proxy only"
ufw allow out 53/udp comment "DNS"

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

## РІВЕНЬ 4: ІЗОЛЯЦІЯ АГЕНТІВ

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

### HashiCorp Vault — організація секретів:
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
        # Джерело: прямі повідомлення Андрія
        "trust_score": 1.0,
        "encryption": "AES-256-GCM",
        "access": ["eva_only"],
        "backup": True,
        "retention": "forever"
    },
    "TIER_2_AGENT": {
        # Джерело: висновки агентів
        "trust_score": 0.8,
        "encryption": "AES-256-GCM",
        "access": ["eva", "authorized_agents"],
        "backup": True,
        "retention": "1_year"
    },
    "TIER_3_EXTERNAL": {
        # Джерело: інтернет, email, API
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
