#!/usr/bin/env python3
"""
SYNDICATE — Antigravity Identity Repository Synchronizer & Practical Arsenal Installer.

What this tool does:
1. Installs & upgrades Antigravity's active global skills (`~/.gemini/config/skills`)
   from the repository's curated skill libraries (`skills/vendor/*`, `kodex_core/skills/*`,
   `marshal_core/skills/*`, `tyler_core/skills/*`, and `knowledge_pools/*`).
2. Mirrors Antigravity's complete identity directly into the tracked repository folder
   `antigravity_identity/`:
   - `antigravity_identity/rules/`      -> Active SOP, architectural, and identity rules
   - `antigravity_identity/skills/`     -> Complete practical skill arsenal (SKILL.md + references)
   - `antigravity_identity/prompts/`    -> Structured prompt catalog & task brief templates
   - `antigravity_identity/mcp/`        -> Curated MCP practical config & 70-category index
   - `antigravity_identity/memory/`     -> Core architectural memory, Boardroom map & decisions
   - `antigravity_identity/IDENTITY_MANIFEST.json` -> Cryptographic SHA-256 inventory
3. Enforces Zero-Trust Secret Scrubbing (`PIIRedactor` + token regexes) before writing
   any file into the repository so no API keys or credentials can ever leak into Git.
4. Supports `--restore-to <path>` to hydrate a fresh VM or workstation directly from the Git repo.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if sys.platform == "win32" and __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.pii import PIIRedactor  # noqa: E402

DEFAULT_GEMINI_CONFIG = Path(os.environ.get("ANTIGRAVITY_CONFIG_DIR", Path.home() / ".gemini" / "config"))
REPO_IDENTITY_DIR = REPO_ROOT / "antigravity_identity"

# Practical skills from the repository to install into Antigravity's active skill arsenal
REPO_SKILL_SOURCES: Dict[str, str] = {
    "api-and-interface-design": "skills/vendor/addyosmani/agent-skills/skills/api-and-interface-design",
    "context-engineering": "skills/vendor/addyosmani/agent-skills/skills/context-engineering",
    "debugging-and-error-recovery": "skills/vendor/addyosmani/agent-skills/skills/debugging-and-error-recovery",
    "documentation-and-adrs": "skills/vendor/addyosmani/agent-skills/skills/documentation-and-adrs",
    "planning-and-task-breakdown": "skills/vendor/addyosmani/agent-skills/skills/planning-and-task-breakdown",
    "source-driven-development": "skills/vendor/addyosmani/agent-skills/skills/source-driven-development",
    "test-driven-development": "skills/vendor/addyosmani/agent-skills/skills/test-driven-development",
    "agent-security-hardening": "skills/vendor/affaan-m/ECC/skills/agent-security-hardening",
    "brand-voice": "skills/vendor/affaan-m/ECC/skills/brand-voice",
    "content-engine": "skills/vendor/affaan-m/ECC/skills/content-engine",
    "market-research": "skills/vendor/affaan-m/ECC/skills/market-research",
    "internal-comms": "skills/vendor/anthropics/skills/skills/internal-comms",
    "online-store-legitimacy-checks": "skills/vendor/HinkoK/agent-skills/skills/online-store-legitimacy-checks",
    "behavioral-finance": "skills/vendor/HKUDS/Vibe-Trading/agent/src/skills/behavioral-finance",
    "replica-recon": "skills/vendor/Jakeschincariol/replica-skill/replica-recon",
    "replica-test": "skills/vendor/Jakeschincariol/replica-skill/replica-test",
    "scientific-critical-thinking": "skills/vendor/K-Dense-AI/scientific-agent-skills/skills/scientific-critical-thinking",
    "grill-me": "skills/vendor/mattpocock/skills/skills/productivity/grill-me",
    "grilling": "skills/vendor/mattpocock/skills/skills/productivity/grilling",
    "handoff": "skills/vendor/mattpocock/skills/skills/productivity/handoff",
    "kodex-notebooklm": "kodex_core/skills/kodex-notebooklm",
    "kodex-obsidian": "kodex_core/skills/kodex-obsidian",
    "kodex-prompt-catalog": "kodex_core/skills/kodex-prompt-catalog",
    "kodex-skill-research": "kodex_core/skills/kodex-skill-research",
    "kodex-mcp-connector-scout": "kodex_core/skills/kodex-mcp-connector-scout",
    "marshal-skill-scout": "marshal_core/skills/marshal-skill-scout",
    "marshal-mcp-connector-review": "marshal_core/skills/marshal-mcp-connector-review",
    "tyler-price-compare": "tyler_core/skills/tyler-price-compare",
    "tyler-supplier-research": "tyler_core/skills/tyler-supplier-research",
    "tyler-store-legitimacy-review": "tyler_core/skills/tyler-store-legitimacy-review",
    "tyler-listing-draft": "tyler_core/skills/tyler-listing-draft",
}

# Secret patterns that must never be written to the tracked git identity directory
_SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-proj-[A-Za-z0-9_-]{20,}"),
    re.compile(r"gsk_[A-Za-z0-9_-]{20,}"),
    re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"),
]


def _normalize_lf_and_scrub(text: str, redactor: PIIRedactor) -> str:
    """Normalize CRLF -> LF, strip trailing spaces, and redact any live tokens."""
    scrubbed, _ = redactor.redact(text)
    for pat in _SECRET_PATTERNS:
        scrubbed = pat.sub("[REDACTED_SECRET]", scrubbed)
    lines = [line.rstrip() for line in scrubbed.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    result = "\n".join(lines).rstrip("\n") + "\n"
    return result


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def install_repo_skills_to_live_config(
    repo_root: Path = REPO_ROOT,
    gemini_config_dir: Path = DEFAULT_GEMINI_CONFIG,
) -> List[str]:
    """Install all curated repository skills into Antigravity's active global config."""
    skills_target_root = gemini_config_dir / "skills"
    skills_target_root.mkdir(parents=True, exist_ok=True)
    installed: List[str] = []

    # Shared references from addyosmani/agent-skills
    addy_refs = repo_root / "skills" / "vendor" / "addyosmani" / "agent-skills" / "references"

    for skill_id, rel_source in sorted(REPO_SKILL_SOURCES.items()):
        src_dir = repo_root / rel_source
        if not src_dir.exists():
            continue
        dst_dir = skills_target_root / skill_id
        dst_dir.mkdir(parents=True, exist_ok=True)
        for item in src_dir.rglob("*"):
            if item.is_file():
                rel = item.relative_to(src_dir)
                target_file = dst_dir / rel
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target_file)
        # If this is an addyosmani skill, also copy its checklist references
        if "addyosmani/agent-skills" in rel_source and addy_refs.exists():
            ref_dst = dst_dir / "references"
            ref_dst.mkdir(parents=True, exist_ok=True)
            for ref_file in addy_refs.glob("*.md"):
                shutil.copy2(ref_file, ref_dst / ref_file.name)
        installed.append(skill_id)

    return installed


def _build_core_memory_markdown() -> str:
    """Generate the canonical persistent memory & architectural context for Antigravity."""
    return """# 🧠 Antigravity (Аліса) — Ядро Пам'яті та Архітектурний Контекст SYNDICATE

> **Статус:** Активний 24/7 R&D Супер-Агент та Головний Інженер Синдикату
> **Командир:** Андрій
> **Режим синхронізації:** Двосторонній (Локальний ПК ↔ Віртуальна Машина ↔ Git `antigravity_identity/`)

---

## 1. Стандартний Порядок Роботи (SOP)
Кожне завдання виконується виключно у такій послідовності:
1. **Аналіз фактичного стану** (перевірка реальних файлів, логів, конфігів; попередні звіти не є доказом).
2. **Робочий код і права у дозволеній зоні** (жодних TODO, порожніх файлів або заглушок).
3. **Реальні тести на успішні й відмовні сценарії** (mock-тести не видаються за live-перевірки).
4. **Фактичні перевірки** (`pytest`, `git diff --check`, перевірка політик Vault та матриці прав).
5. **Звіт і фіксація результату** (коміт, пуш, оновлення снапшотів).

---

## 2. Архітектура SYNDICATE: Радіальна Рада Директорів та Нейронне Ядро
Ми повністю відмовились від старої системи поверхів. Архітектура побудована як **Радіальний Круглий Стіл (Boardroom Round Table)** навколо **Центрального Нейронного Ядра**:

### Центральне Нейронне Ядро:
- `EvaOrchestrator` (LangGraph координація, 139 маршрутів завдань)
- `MemoryManager` (PostgreSQL + `pgvector` + Redis)
- `HashiCorp Vault` (Shamir 3-of-5, AppRole для кожного агента, 13 ACL-політик)
- `Sentinel Zero-Trust` (Lethal Trifecta guard, command safety, slopsquatting radar, PII redactor)

### Рада Директорів (12 Спеціалізованих Вузлових Агентів + Antigravity):
1. **Єва (`eva`)** — Chief of Staff. Ранковий (07:30) та вечірній (21:00) брифінги. У кінці кожного ранкового звіту обов'язково фіксує: `🛡️ Статус безпеки: Бекап знаходиться у стані готовності до вигрузки на флеш носій (Disaster Recovery Ready).`
2. **Кодекс (`kodex`)** — Головний Архіваріус та Шлюз Великих Масивів Даних. Завантажує масиви з хмарних сховищ і Telegram, керує дедуплікацією, очищує тимчасові блокноти NotebookLM та проводить ревізію Павутини Завдань в Obsidian (`Review` → `Completed`).
3. **Архітектор (`architect`)** — CTO. Проєктування та лінтинг n8n workflow (`FlowLint`), ADR, компілятор самовідновлення (`Compiler-in-the-Loop`), GitOps.
4. **Маршал (`marshal`)** — CSO. Командувач протоколу Sentinel Zero-Trust, аудит скілів (`skillspector`) та MCP-конекторів.
5. **Фін (`fin`)** — CFO. Фінансовий аналіз, runway, податковий радар ФОП, перевірка кошика покупок Єви (`funds_check`), генерація PDF/Excel звітів.
6. **Сем (`sam`)** — Quant & Markets. Confluence Engine, оцінка сетапів, ризик-менеджмент портфеля, суворий HITL-гейт.
7. **Джек (`jack`)** — Chief Sports Betting & Probabilistic Quant. Спеціалізується на виграшних ставках (PariMatch, Vbet, Pinnacle): очищення маржі букмекера (Vig removal), пошук $+EV$ Value Bets, дробовий критерій Келлі, anti-tilt блокер.
8. **Док (`doc`)** — Chief Medical Officer. Виключно клінічна медицина: біомаркери, календар скринінгів, медична картка (`emergency_card`), індекс ранкової готовності (HRV/сон), відновлення нервової системи. Жодних вигаданих метрик.
9. **Тренер (`trainer`)** — Physical Performance Director. Тренувальні протоколи, періодизація, розрахунок КБЖУ за формулою Міффліна — Сан-Жеора (`Mifflin-St Jeor`), плани харчування, списки покупок, трекер звичок.
10. **Кіра (`kira`)** — Dean of Academy. 4-ступеневий сократівський тютор (`clarify` → `nudge` → `scaffold` → `reveal`), мікро-квізи, синтез історії та коду.
11. **Оскар (`oscar`)** — Creative Director. Вірусні короткі відео, сценарії, караоке-субтитри, реліз-паки (`Humanizer` + `VideoPromptEnhancer`).
12. **Тайлер (`tyler`)** — Director of Operations & Commerce. Перевірка постачальників та інтернет-магазинів, порівняння цін, POD-мокапи, антидетект-профілі.
13. **Antigravity / Аліса (`antigravity`)** — Зовнішній 24/7 R&D Супер-Агент на виділеній Віртуальній Машині. Має ізольований канал під кожного директора (`channel-oscar`, `channel-architect`, `channel-jack` тощо) через `AntigravityContractorGateway` із автокомпакцією контексту.

---

## 3. Хмарна Інфраструктура, Другий Мозок та Бекапи
- **Хмара Командира (Андрія):** **Nextcloud** + **Immich** (особисті фото, відео, документи з міткою `andrii_protected`).
- **Хмара Агентів:** **Seafile** (високошвидкісне блокове сховище з дедуплікацією для робочих масивів агентів).
- **Другий Мозок (NotebookLM ↔ Obsidian):**
  - Всі агенти мають міст `NotebookLMObsidianBridge` (`src/integrations/notebooklm_obsidian_bridge.py`).
  - Джерела опрацьовуються у NotebookLM, стискаються у структуровані картки з YAML-фронтматером і `[[backlinks]]` та вивантажуються в Obsidian (`01_Knowledge_Base/<agent>/`), після чого тимчасові блокноти NotebookLM очищуються.
  - У `04_Tasks_Web/` діє Павутина Завдань (`Inbox` → `In_Progress` → `Review` → `Completed` / `Blocked`).
- **Система Бекапів (3-2-1-1):**
  - Щоночі о `02:00` — шифрований дедуплікований снепшот **BorgBackup** (`AES-256`).
  - О `03:00` — підготовка холодного Disaster Recovery бандлу (`tools/export_cold_recovery_bundle.py`) для вигрузки на фізичний USB/SSD флеш-носій.
  - О `07:30` — Єва у ранковому звіті підтверджує готовність бекапу до вигрузки на флеш-носій.

---

## 4. Візуальна Концепція Додатків (Desktop & Smartphone Cockpit)
- **Стилістика:** **NeuroFlow Dark Glass** (`#0a0b10` обсидіановий фон, напівпрозорі скляні панелі `backdrop-filter: blur(20px)`, акцентний неоновий помаранчевий `#ff5500`, смарагдовий `#00e676`, ціановий `#00e5ff`).
- **Компоновка:** Радіальний селектор Ради Директорів навколо Нейронного Ядра, Bento-сітка телеметрії, інтерактивний чат із виділеним каналом кожного агента, мобільний PWA/адаптивний режим.
- **Клонування Додатків:** Пайплайн `syndicate-app-cloner` (`replica-recon` + `rea-reverse-engineering` + `replica-test`) готовий до прийому посилань та APK із Google Play для розбору екранів (`S01..Sxx`), флоу (`F01..Fxx`) та переносу найкращих механік у наш додаток.
"""


def _build_mcp_practical_arsenal(repo_root: Path) -> Dict[str, Any]:
    """Build a structured MCP practical configuration & category summary from mcp_servers/."""
    categories_dir = repo_root / "mcp_servers" / "categories"
    categories_list: List[str] = []
    if categories_dir.exists():
        categories_list = sorted(f.stem for f in categories_dir.glob("*.md"))

    return {
        "schema_version": 1,
        "owner": "antigravity",
        "description": "Curated practical MCP server configurations and 70-category index for Antigravity (24/7 VM & Workstation)",
        "total_catalog_records": 18789,
        "total_categories": len(categories_list),
        "categories": categories_list,
        "practical_servers": {
            "time": {
                "package": "mcp-server-time==2026.10.10",
                "transport": "stdio",
                "command": "python",
                "args": ["-m", "mcp_server_time", "--local-timezone=Europe/Kyiv"],
                "purpose": "Deterministic UTC / Europe/Kyiv time & timezone conversion",
            },
            "filesystem": {
                "package": "@modelcontextprotocol/server-filesystem",
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "${SYNDICATE_WORKSPACE_ROOT}"],
                "purpose": "Sandboxed filesystem access for repository and Obsidian Second Brain",
            },
            "git": {
                "package": "mcp-server-git",
                "transport": "stdio",
                "command": "python",
                "args": ["-m", "mcp_server_git", "--repository", "${SYNDICATE_REPO_ROOT}"],
                "purpose": "Git history, diff verification, branch & commit management",
            },
            "postgres": {
                "package": "@modelcontextprotocol/server-postgres",
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-postgres", "${POSTGRES_READONLY_DSN}"],
                "purpose": "Schema inspection & pgvector memory diagnostics",
            },
            "playwright": {
                "package": "@playwright/mcp",
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@playwright/mcp@latest", "--headless"],
                "purpose": "E2E browser automation, UI cloning reconnaissance, and visual verification",
            },
            "firecrawl": {
                "package": "firecrawl-mcp",
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "firecrawl-mcp"],
                "env_vars_required": ["FIRECRAWL_API_KEY"],
                "purpose": "Deep web scraping & documentation extraction into clean LLM Markdown",
            },
        },
    }


def sync_identity_to_repo(
    gemini_config_dir: Path = DEFAULT_GEMINI_CONFIG,
    repo_identity_dir: Path = REPO_IDENTITY_DIR,
    repo_root: Path = REPO_ROOT,
    install_repo_skills: bool = True,
) -> Dict[str, Any]:
    """
    Synchronize Antigravity's rules, skills, prompts, MCP config, and core memory
    into `antigravity_identity/` inside the repository.
    """
    redactor = PIIRedactor()

    if install_repo_skills:
        install_repo_skills_to_live_config(repo_root=repo_root, gemini_config_dir=gemini_config_dir)

    rules_dst = repo_identity_dir / "rules"
    skills_dst = repo_identity_dir / "skills"
    prompts_dst = repo_identity_dir / "prompts"
    mcp_dst = repo_identity_dir / "mcp"
    memory_dst = repo_identity_dir / "memory"

    for d in (rules_dst, skills_dst, prompts_dst, mcp_dst, memory_dst):
        d.mkdir(parents=True, exist_ok=True)

    synced_files: Dict[str, str] = {}

    def _write_tracked(target: Path, text: str) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        clean_bytes = _normalize_lf_and_scrub(text, redactor).encode("utf-8")
        target.write_bytes(clean_bytes)
        rel = target.relative_to(repo_identity_dir).as_posix()
        synced_files[rel] = _sha256_bytes(clean_bytes)

    # 1. Sync Rules from ~/.gemini/config/rules
    rules_src = gemini_config_dir / "rules"
    rules_count = 0
    if rules_src.exists():
        for rule_file in sorted(rules_src.glob("*.md")):
            _write_tracked(rules_dst / rule_file.name, rule_file.read_text(encoding="utf-8", errors="replace"))
            rules_count += 1

    # 2. Sync Skills from ~/.gemini/config/skills (SKILL.md + markdown/yaml/txt references)
    skills_src = gemini_config_dir / "skills"
    skills_list: List[str] = []
    if skills_src.exists():
        for skill_dir in sorted(skills_src.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            skills_list.append(skill_dir.name)
            for item in sorted(skill_dir.rglob("*")):
                if not item.is_file():
                    continue
                # Sync SKILL.md, markdown references, YAML/JSON/CSV/TS templates, and LICENSE files
                if item.suffix.lower() in {".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".ts"}:
                    rel_in_skill = item.relative_to(skill_dir)
                    _write_tracked(
                        skills_dst / skill_dir.name / rel_in_skill,
                        item.read_text(encoding="utf-8", errors="replace"),
                    )

    # 3. Sync Prompts & Knowledge Pool Templates from repo `knowledge_pools/`
    kp_dir = repo_root / "knowledge_pools"
    prompts_count = 0
    if kp_dir.exists():
        for kp_file in sorted(kp_dir.rglob("*.md")):
            rel_kp = kp_file.relative_to(kp_dir)
            _write_tracked(prompts_dst / rel_kp, kp_file.read_text(encoding="utf-8", errors="replace"))
            prompts_count += 1

    # 4. Sync MCP Practical Arsenal
    mcp_arsenal = _build_mcp_practical_arsenal(repo_root)
    _write_tracked(
        mcp_dst / "mcp_practical_arsenal.json",
        json.dumps(mcp_arsenal, indent=2, ensure_ascii=False),
    )

    # 5. Write Core Memory & Architectural Context
    _write_tracked(memory_dst / "CORE_IDENTITY_AND_MEMORY.md", _build_core_memory_markdown())

    # 6. Write README.md and IDENTITY_MANIFEST.json
    readme_text = f"""# 🛡️ Antigravity (Аліса) — Репозиторний Бекап Ідентичності, Скілів та Пам'яті

Ця директорія (`antigravity_identity/`) є живим, версіонованим у Git зліпком ідентичності **Antigravity (Аліси)** — головного R&D супер-агента та інженерного підрядника **SYNDICATE**.

## 📂 Структура
- `rules/` — Бойові правила та регламенти роботи ({rules_count} правил, включно зі Стандартним Порядком Роботи SOP та Архітектурою Круглого Столу).
- `skills/` — Повний арсенал практичних навичок ({len(skills_list)} скілів: розробка, клонування додатків `replica-recon`/`replica-test`, реверс-інжиніринг, дизайн, безпека, n8n, NotebookLM, Obsidian, квантова аналітика).
- `prompts/` — Бібліотека структурованих промптів, шаблонів ТЗ та скілів із `knowledge_pools/` ({prompts_count} шаблонів).
- `mcp/` — Практичний конфіг MCP-серверів (`mcp_practical_arsenal.json`) та індекс 70 категорій (18 789 серверів).
- `memory/CORE_IDENTITY_AND_MEMORY.md` — Довгострокова архітектурна пам'ять, карта директорів, хмарна схема та дизайн-система NeuroFlow.
- `IDENTITY_MANIFEST.json` — Криптографічний реєстр (SHA-256) усіх файлів ідентичності.

## 🔄 Команди синхронізації та відновлення
- Оновити бекап ідентичності в репозиторії:
  ```bash
  python tools/sync_antigravity_identity_repo.py --sync
  ```
- Перевірити цілісність та відсутність секретів (CI/Audit gate):
  ```bash
  python tools/sync_antigravity_identity_repo.py --check
  ```
- Відновити ідентичність із репозиторію на новій Віртуальній Машині чи ПК:
  ```bash
  python tools/sync_antigravity_identity_repo.py --restore-to ~/.gemini/config
  ```
"""
    _write_tracked(repo_identity_dir / "README.md", readme_text)

    manifest = {
        "schema_version": 1,
        "agent_id": "antigravity",
        "alias": "alice",
        "role": "External 24/7 VM Super-Agent & Chief R&D Contractor of SYNDICATE",
        "commander": "andrii",
        "rules_count": rules_count,
        "skills_count": len(skills_list),
        "skills": sorted(skills_list),
        "prompts_count": prompts_count,
        "mcp_categories_indexed": mcp_arsenal["total_categories"],
        "mcp_servers_cataloged": mcp_arsenal["total_catalog_records"],
        "files_count": len(synced_files),
        "files": dict(sorted(synced_files.items())),
    }
    manifest_bytes = _normalize_lf_and_scrub(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        redactor,
    ).encode("utf-8")
    (repo_identity_dir / "IDENTITY_MANIFEST.json").write_bytes(manifest_bytes)

    return manifest


def restore_identity_from_repo(
    target_config_dir: Path,
    repo_identity_dir: Path = REPO_IDENTITY_DIR,
) -> Dict[str, Any]:
    """Restore Antigravity's rules, skills, and MCP config from `antigravity_identity/` to a target config dir."""
    manifest_path = repo_identity_dir / "IDENTITY_MANIFEST.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Identity manifest not found at {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target_config_dir = Path(target_config_dir)
    target_config_dir.mkdir(parents=True, exist_ok=True)

    restored_count = 0
    for subdir in ("rules", "skills", "prompts", "mcp", "memory"):
        src_sub = repo_identity_dir / subdir
        if not src_sub.exists():
            continue
        dst_sub = target_config_dir / subdir
        for item in src_sub.rglob("*"):
            if item.is_file():
                rel = item.relative_to(src_sub)
                out_file = dst_sub / rel
                out_file.parent.mkdir(parents=True, exist_ok=True)
                out_file.write_bytes(item.read_bytes())
                restored_count += 1

    return {
        "status": "restored",
        "target_config_dir": str(target_config_dir),
        "restored_files_count": restored_count,
        "skills_count": manifest.get("skills_count", 0),
        "rules_count": manifest.get("rules_count", 0),
    }


def verify_repo_identity(repo_identity_dir: Path = REPO_IDENTITY_DIR) -> Tuple[bool, List[str]]:
    """Verify SHA-256 checksums and ensure zero secret leaks in `antigravity_identity/`."""
    errors: List[str] = []
    manifest_path = repo_identity_dir / "IDENTITY_MANIFEST.json"
    if not manifest_path.exists():
        return False, [f"Missing manifest: {manifest_path}"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_files: Dict[str, str] = manifest.get("files", {})

    for rel_path, expected_sha in expected_files.items():
        fpath = repo_identity_dir / rel_path
        if not fpath.exists():
            errors.append(f"Missing tracked file: {rel_path}")
            continue
        raw = fpath.read_bytes()
        actual_sha = _sha256_bytes(raw)
        if actual_sha != expected_sha:
            errors.append(f"SHA-256 mismatch for {rel_path}: expected {expected_sha}, got {actual_sha}")
        text = raw.decode("utf-8", errors="replace")
        for pat in _SECRET_PATTERNS:
            if pat.search(text):
                errors.append(f"Secret pattern detected in {rel_path}")

    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize Antigravity identity with the repository.")
    parser.add_argument("--sync", action="store_true", help="Install repo skills and sync identity into antigravity_identity/")
    parser.add_argument("--check", action="store_true", help="Verify SHA-256 manifest and secret scrubbing in antigravity_identity/")
    parser.add_argument("--restore-to", type=str, default=None, help="Restore identity from repo into target config directory")
    args = parser.parse_args()

    if args.restore_to:
        res = restore_identity_from_repo(Path(args.restore_to))
        print(f"✅ Restored {res['restored_files_count']} identity files ({res['skills_count']} skills, {res['rules_count']} rules) to {res['target_config_dir']}")
        return 0

    if args.check:
        ok, errs = verify_repo_identity()
        if not ok:
            for e in errs:
                print(f"❌ {e}", file=sys.stderr)
            return 1
        manifest = json.loads((REPO_IDENTITY_DIR / "IDENTITY_MANIFEST.json").read_text(encoding="utf-8"))
        print(
            f"✅ Antigravity Identity verified: {manifest['skills_count']} skills, "
            f"{manifest['rules_count']} rules, {manifest['files_count']} tracked files (0 secret leaks)."
        )
        return 0

    manifest = sync_identity_to_repo()
    print(
        f"✅ Antigravity Identity synced to {REPO_IDENTITY_DIR.relative_to(REPO_ROOT)}: "
        f"{manifest['skills_count']} skills, {manifest['rules_count']} rules, "
        f"{manifest['prompts_count']} prompt/skill templates, {manifest['files_count']} total files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
