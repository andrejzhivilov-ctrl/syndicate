# SYNDICATE shared knowledge pools

Це компактні похідні reference-матеріали, індекси та політики доступу — не копія повних зовнішніх курсів. Джерельні вкладення лишаються поза Git; у каталозі є SHA-256, назва файла та статус перевірки. Не включати сюди secrets, персональні/медичні записи або необмежені dump-и акаунтів.

- Політики й hash-pinned посилання на реєстри: `config/knowledge_pool_catalog.json`.
- Реєстр джерел і SHA-256 вкладень: `config/knowledge_source_registry.json`.
- Окремі реєстри: `config/skill_pool_registry.json`, `config/prompt_pool_registry.json`, `config/knowledge_reference_registry.json`.
- Grant-план для KODEX/Marshal: `config/knowledge_pool_grants.json`; лише `proposed_not_applied`, кодом/ Vault не завантажується.
- Код пошуку/читання: `src/agent_platform/knowledge_pool.py`.
- Кожен матеріал зараз `review_pending`: адресати перевірки — KODEX і Marshal, але код не надає їм runtime-доступу самостійно; потрібні окремі host grants та allowlist. Після перевірки shared-read так само потребуватиме явного host grant.
- Пошук локальний, лексичний і обмежений top-k; повний текст читається тільки окремим викликом за item ID. Вміст не виконується. `KnowledgePool()` без host allowlist повертає порожні результати й відмовляє в читанні.
- Публікація в `shared` вимагає окремого Marshal HMAC, прив'язаного до точного хешу, review ID і результату сканування; ключ має бути host-owned із Vault. Writer/approval endpoint не створений, підписаних матеріалів наразі немає.
- Рольові/system prompts, профілі, grants, мережеві дії та live workflow не є вмістом пулів.

n8n може згодом оркеструвати асинхронні перевірки/повідомлення; синхронний пошук лишається прямим read-only викликом. Жоден live n8n workflow тут не створено або активовано.
