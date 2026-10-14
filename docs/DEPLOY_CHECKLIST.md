# Чеклист серверного розгортання SYNDICATE

Планова дата старту: **2026-10-15**. Створено заново 2026-10-14 за доступним
кодом; це **не** відновлений файл із недоступного локального коміта `5e96a86`.
Чекбокси не заповнені: жодне серверне розгортання цією сесією не виконано.

## Gate 0 — рішення власника (STOP, доки не погоджено)

- [ ] Сервер/хост/SSH-користувач із sudo та SSH-доступ передано захищеним каналом.
- [ ] Домашній ПК не використовується; підтверджено ресурси й резерв диска сервера.
- [ ] Обрано A/B: один існуючий eva-agent чи реалізація окремих Hermes-контейнерів.
- [ ] Якщо обрано B — окремий план/live Hermes adapter погоджено; зараз його немає.
- [ ] Домен/DNS/TLS погоджено; без домену — тільки закритий тестовий доступ.
- [ ] Явний список agent IDs, grants, capabilities, scopes, egress domains і бюджетів.
- [ ] Порожній Telegram allowlist відмовляє всім; дозволені тільки ID Андрія.
- [ ] Рішення про production deployment отримано окремо. Merge PR не означає deployment.

## Gate 1 — код і документація

- [ ] PR перевірено, `gh pr checks N` зелені, PR злито в main.
- [ ] Блокер `5e96a86` розв'язано: отримано patch/bundle або окремо погоджено нову реалізацію голосу.
- [ ] Прочитано `DEPLOYMENT_RUNBOOK.md`, `docs/DEPLOY_SYNDICATE.md`, цей чеклист.
- [ ] `bash tools/check.sh` exit 0; у CI PostgreSQL + pgvector пройшов із live DB.
- [ ] `python tools/export_permissions.py` і `python tools/vault_policies.py --check` актуальні.
- [ ] Обидва compose-файли ідентичні; `docker compose config -q` пройшов на сервері.
- [ ] Перевірено версії/вразливості образів; старі pinned tags не вважати автоматично безпечними.

## Gate 2 — сервер, дані та секрети

- [ ] Вручну перевірено bootstrap-скрипт перед sudo-запуском; SSH не буде заблоковано.
- [ ] Firewall: назовні тільки погоджені SSH/80/443; DB/Redis/Vault не публічні.
- [ ] Приватні каталоги/volumes з правильними UID; не chmod 777.
- [ ] EVA_DATA_DIR/KODEX_DATA_DIR поза Git; персональні дані й media не у apps/.
- [ ] `.env` mode 0600, не tracked; значення не друкуються в логи чи shell history.
- [ ] Vault initialized/unsealed; unseal-матеріал у захищених окремих місцях.
- [ ] Справжні DB/Redis значення збігаються з контейнерами; placeholders відсутні.
- [ ] AppRole scope перевірено; root-token після налаштування відкликано.
- [ ] Ризик union policy eva-agent прийнято/усунено: один процес бачить секрети кількох агентів.
- [ ] OpenRouter key лише у `api-keys`/`openrouter_api_key`; реалізація цього voice-path ще відсутня в доступній базі.
- [ ] Не додано Google cookies/пароль або API key, замаскований під підписку Google One.

## Gate 3 — TLS та мінімальний запуск

- [ ] Сертифікат доступний nginx за `/etc/nginx/certs/live/default/` усередині контейнера.
- [ ] Хост-каталог `${DATA_ROOT:-/data}/nginx-certs`; погоджено renewal і перевірено копіювання оновленого cert.
- [ ] Self-signed використовується лише в закритому тесті, не як production TLS.
- [ ] Запущено тільки postgres/redis/vault, перевірено health, потім мінімально погоджені сервіси.
- [ ] Запуск eva-agent не вважається безпечним «статусом»: він створює наявний orchestrator/конектори.
- [ ] `/health`: healthy, vault_connected, memory_ready; semantic_search_enabled перевірено згідно з обраним режимом.
- [ ] Неавторизовані `/cockpit`, `/floors`, `/api/execute`, HITL відмовляють.
- [ ] Device token з read не виконує задач і не підтверджує HITL.
- [ ] CORS/origin allowlist не wildcard; proxy довіряє лише погодженим джерелам.

## Gate 4 — функціональний smoke test лише дозволених функцій

- [ ] Telegram: сторонній chat ID і порожній allowlist відхилено; токени тільки Vault.
- [ ] Голос: доступний endpoint/model/voice/cost перевірено, український тест погоджено, consumer підключено окремо.
- [ ] KODEX: andrii_protected лише read-only, видалення захищеного файлу відмовлено, немічені дії в журналі.
- [ ] Вечірній звіт Єви о 21:00 Europe/Kyiv містить реальні файлові дії.
- [ ] Antigravity: `status`, `init`, task/packet/receive, HTML/PNG, MP4 з FFmpeg на локальних даних.
- [ ] Приватна історія: лише reviewed копія, без медичного архіву, локальний пошук з source_hash; не надсилалась у Google автоматично.
- [ ] Немає live Hermes/LangGraph dispatcher, API spending чи автоматичного deployment без окремого погодження.

## Gate 5 — backup/restore, спостереження та приймання

- [ ] Backup DB + Vault + bootstrap перевірено; файл manifest і SHA-256 збережено приватно.
- [ ] Окремо backup KODEX, EVA_DATA_DIR, Antigravity workspace та n8n; snapshots консистентні.
- [ ] Відновлення виконано на окремому тестовому стенді без overwrite production.
- [ ] Є контроль health, диска, expiry TLS, Vault seal, backup age та витрат.
- [ ] Визначено stop/rollback: зупинити погоджені services без `down -v`; DB migrations відновлюються з тестованого backup.
- [ ] Андрій прийняв результати; лише після цього говоримо «систему розгорнуто».
