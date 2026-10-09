# Marshal — каталог кандидатів (GitHub / скіли / знання)

**Статус:** огляд 2026-10-09. Нічого з цього не встановлено, не ingest, не в `skills` / `services_enabled`.
**Правило:** новий скіл лише через картку HITL. «Погодити» ≠ grant. Живі red-team payload не ганяти на Синдикаті.

Пошук був за scanner’ами скілів, guardrail LLM, secret leak, OWASP agentic. Нижче — що варто тримати в голові, і що **не** тягнути.

## Брати як чергу (коли Андрій скаже «так» на конкретний пункт)

| # | Кандидат | Навіщо Маршалу | Як чіпати | Не робити зараз |
|---|---|---|---|---|
| 1 | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | Скан `SKILL.md` / MCP **перед** карткою «підключити скіл». Статичний прохід `--no-llm` (AST, taint, secret, injection). Оновлюється (коміти 2026-10-09). | Окремий HITL на *встановлення сканера*; далі Marshal запускає scan і кладе score в пропозицію | Не `pip install` у цей профіль; LLM-pass SkillSpector не вмикати (токени + ключ) |
| 2 | [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) (MIT) | Zero-token шар A: секрет у outbound/дифі/промпті → **червоний** (це вже критичне, не «вийшов в інтернет») | Окремий HITL; сканувати метадані/текст, не слати знайдений секрет у Telegram | Не verify live API (це вже використання вкраденого ключа) |
| 3 | OWASP LLM Top 10 + OWASP Agentic ASI01–ASI10 | Read-only корпус знань Маршала | Коли буде ingest: рядок у `SOURCES.yaml` з ліцензією й датою | Не копіювати FULL_SPEC «✅ Закрито»; `sources: []` лишається |
| 4 | Власний regex-шар (вже в дусі репо: `sk-`, `ghp_`, `xoxb-`, `AIza`) | Дешевий observe без нових залежностей | Можна колись винести в host-owned helper; не LLM | Не вважати це «LLM-Guard» |

## Не ставити / не пакувати оптом

| Репозиторій | Чому ні |
|---|---|
| [protectai/llm-guard](https://github.com/protectai/llm-guard) | Архів **2026-07-09**, read-only. У FULL_SPEC згаданий як живий стек — застаріло. Не dependency. |
| [screem500/prompt-injection-auditor](https://github.com/screem500/prompt-injection-auditor) | Корисний defensive skill + каталог атак, але всередині **authorized live payloads**. Без окремого «так» не клонувати й не ганяти проти агентів. |
| Великі паки на кшталт «800+ cybersecurity skills» | Supply chain: 26% скілів у дослідженні SkillSpector з вразливостями. Оптом не ставити. |
| TruffleHog як бібліотека в runtime | AGPL + live verification секретів. Для observe досить Gitleaks/regex. |
| Tetragon / Falco | Фаза 2, хост. Не скіл Маршала. |
| Випадкові форки «LLM Guard» | Не плутати з Protect AI; не вендорити. |

## Як це лягає на вже погоджену модель

- Пошук в інтернеті за командою Андрія — як і було: observe, без HITL.
- SkillSpector / Gitleaks — інструменти **для критичного** (витік, новий скіл), не пропускник URL.
- Картка `SKILL_PROPOSAL` коли з’явиться сканер: додати поле `scan: skillspector --no-llm` (score + findings), без тіл секретів.
- Knowledge ingest ≠ клон репо в `marshal_core/knowledge/`. Спочатку рядок у SOURCES, потім HITL.

## Що я свідомо не додаю в пакет зараз

- Нових рядків у `config/agents/marshal.profile.json` → `skills`.
- Submodule / vendor цих репо.
- Моделі, бота, n8n, Drive.
