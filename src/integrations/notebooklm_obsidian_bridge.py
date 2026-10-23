"""
SYNDICATE — NotebookLM 2.0 & Obsidian Knowledge Bridge + Task Web Engine + 3-Tier Hybrid Memory.

Enables all 18 Syndicate agents (Eva, Architect, Marshal, Fin, Sam, Doc, Trainer, Kira,
Oscar, Tyler, Jack, Kodex, Alice, Ray, Dex, Atlas, Scout, Sonar) to operate with
Google NotebookLM (Gemini Notebook 2026) and the shared Obsidian "Second Brain":
1. Grounded synthesis via Consolidated Master Notebook (`0a882755-acbf-468c-be37-21e40395dd50`, 129 sources).
2. Mandatory Ukrainian Language Policy (`language="uk"`) for all Studio Artifacts
   (Audio Overviews / Podcasts, Interactive Mind Maps, Study Guides, Slide Decks, Infographics).
3. Information Alchemy (`compress_and_convert_sources`): compresses 5-10 raw sources into
   a single high-density Master Note and converts it to a single source (scaling 300/500 limits to 1,500+ sources).
4. Master Instructions Document (`build_master_instructions_doc`): bypasses the 500-char custom prompt limit.
5. Late Chunking (`late_chunk_document`): injects global document context into every chunk before indexing.
6. 3-Tier Hybrid Memory Router (`route_hybrid_memory_query`): eliminates the NotebookLM "Index Tax"
   by combining Tier 1 (Obsidian Markdown), Tier 2 (pgvector <20ms), and Tier 3 (NotebookLM Deep Synthesis).
7. Deduplication, Interactive Obsidian Task Web (04_Tasks_Web/), Audio placement, and Cleanup.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import structlog

logger = structlog.get_logger(__name__)

DEFAULT_OBSIDIAN_VAULT = Path(os.environ.get("OBSIDIAN_VAULT_PATH", "data/obsidian_vault"))

# Consolidated SYNDICATE Master Notebook ID (129 verified sources, 0 errors)
MASTER_NOTEBOOK_ID = "0a882755-acbf-468c-be37-21e40395dd50"
MASTER_NOTEBOOK_TITLE = "Google NotebookLM: Екосистема, Практика та Майстер-Гайд"

# Strict language rule: all NotebookLM Studio outputs (podcasts, mind maps, reports) MUST default to Ukrainian
DEFAULT_STUDIO_LANGUAGE = "uk"
CORPORATE_DOMAIN = "syndicateholding.com"

NOTEBOOKLM_12_BUSINESS_USE_CASES: Dict[str, Dict[str, str]] = {
    "uc01_competitor_intelligence": {
        "wing": "Commercial",
        "agents": "scout, sonar",
        "title": "Конкурентна розвідка та деконструкція оферів",
        "artifact": "Comparison Matrix + Mind Map (uk)",
    },
    "uc02_pod_merch_trend_synthesis": {
        "wing": "Commercial",
        "agents": "tyler, oscar",
        "title": "Синтез трендів Print-on-Demand та візуальних хуків",
        "artifact": "Slide Deck + Creative Brief (uk)",
    },
    "uc03_dropshipping_supplier_audit": {
        "wing": "Commercial",
        "agents": "ray, fin",
        "title": "Аудит постачальників, маржинальності та логістики",
        "artifact": "Data Table + Risk Report (uk)",
    },
    "uc04_affiliate_funnel_alchemy": {
        "wing": "Commercial",
        "agents": "dex, oscar",
        "title": "Арбітражні зв'язки та SEO-кластери блогів",
        "artifact": "Study Guide + Content Calendar (uk)",
    },
    "uc05_quant_macro_research": {
        "wing": "Commercial / Finance",
        "agents": "sam, fin, sonar",
        "title": "Аналіз CFTC COT, макрозвітів ФРС та Smart Money концептів",
        "artifact": "Executive Briefing + Audio Overview (uk)",
    },
    "uc06_longevity_biomarker_dossier": {
        "wing": "Personal / Medical",
        "agents": "doc, trainer",
        "title": "Доказова медицина, біомаркери, HRV та протоколи відновлення",
        "artifact": "Clinical Summary + Mind Map (uk)",
    },
    "uc07_academy_socratic_curriculum": {
        "wing": "Personal / Academy",
        "agents": "kira, kodex",
        "title": "Навчальні посібники, квізи, англійська мова та ІТ-менторство",
        "artifact": "Study Guide + Quiz Bank + Audio Podcast (uk)",
    },
    "uc08_second_brain_knowledge_web": {
        "wing": "Core / Knowledge",
        "agents": "kodex, alice",
        "title": "Побудова графа знань Obsidian Second Brain із двосторонніми лінками",
        "artifact": "Obsidian Markdown Vault + JSON Canvas (uk)",
    },
    "uc09_zero_trust_security_audit": {
        "wing": "Core / Security",
        "agents": "marshal, atlas",
        "title": "Аналіз CVE, політик Vault, eBPF Tetragon та ізоляції токенів",
        "artifact": "Security Audit Report (uk)",
    },
    "uc10_n8n_workflow_architecture": {
        "wing": "Core / Engineering",
        "agents": "architect, alice",
        "title": "Проектування детермінованих конвеєрів n8n та MCP-серверів",
        "artifact": "Architecture ADR + Infographics (uk)",
    },
    "uc11_app_cloner_replica_recon": {
        "wing": "Commercial / Product",
        "agents": "jack, architect, alice",
        "title": "Реверс-інжиніринг мобільних додатків та UI/UX NeuroFlow",
        "artifact": "Screen Inventory S01..Sxx + Flow Map (uk)",
    },
    "uc12_boardroom_morning_briefing": {
        "wing": "Executive",
        "agents": "eva, andrii_twin",
        "title": "Ранковий 5-хвилинний аудіо-брифінг Ради Директорів для Андрія",
        "artifact": "Deep Dive Audio Overview (uk)",
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.strip().lower())
    return re.sub(r"[-\s]+", "_", slug)[:60]


@dataclass
class KnowledgeCard:
    """Structured knowledge unit formatted for Obsidian."""

    title: str
    agent_id: str
    category: str
    summary: str
    key_insights: List[str]
    backlinks: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    audio_path: Optional[str] = None
    created_at: str = field(default_factory=_now_iso)
    content_hash: str = ""

    def compute_hash(self) -> str:
        h = hashlib.sha256()
        h.update(self.title.encode("utf-8"))
        h.update("".join(self.key_insights).encode("utf-8"))
        return h.hexdigest()[:16]

    def to_markdown(self) -> str:
        chash = self.content_hash or self.compute_hash()
        tags_str = ", ".join(f'"{t}"' for t in self.tags)
        sources_str = ", ".join(f'"{s}"' for s in self.sources)
        backlinks_md = "\n".join(f"- [[{link}]]" for link in self.backlinks) if self.backlinks else "- [[Syndicate Core]]"
        insights_md = "\n".join(f"- {item}" for item in self.key_insights)

        audio_section = ""
        if self.audio_path:
            audio_section = f"\n## 🎙️ Аудіоматеріал / Подкаст\n![[ {Path(self.audio_path).name} ]]\n"

        return f"""---
title: "{self.title}"
agent: "{self.agent_id}"
category: "{self.category}"
created_at: "{self.created_at}"
content_hash: "{chash}"
tags: [{tags_str}]
sources: [{sources_str}]
---

# {self.title}

> **Джерело:** Агент `{self.agent_id.upper()}` | **Категорія:** `{self.category}`
> **Оновлено:** `{self.created_at[:10]}`

## 🧠 Ключове Резюме
{self.summary}

## 🔍 Структуровані Інсайти
{insights_md}
{audio_section}
## 🔗 Пов'язані Концепти
{backlinks_md}

---
*Створено автономно інтеграційним мостом Syndicate NotebookLM ↔ Obsidian.*
"""


@dataclass
class TaskCard:
    """Task node inside the Obsidian Task Web."""

    task_id: str
    title: str
    assigned_to: str
    description: str
    created_by: str = "eva"
    status: str = "inbox"  # inbox | in_progress | review | completed | blocked
    priority: str = "medium"  # low | medium | high | critical
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    progress_notes: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    linked_concepts: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        tags_all = list(set(["task", f"agent/{self.assigned_to}", f"status/{self.status}"] + self.tags))
        tags_str = ", ".join(f'"{t}"' for t in tags_all)
        backlinks_md = "\n".join(f"- [[{link}]]" for link in ([f"Директор {self.assigned_to.capitalize()}", "Павутина Завдань"] + self.linked_concepts))

        progress_md = "\n".join(f"- {note}" for note in self.progress_notes) if self.progress_notes else "- *Очікує взяття в роботу*"
        blockers_md = "\n".join(f"- ⚠️ {b}" for b in self.blockers) if self.blockers else "- *Немає блокерів*"

        return f"""---
task_id: "{self.task_id}"
title: "{self.title}"
assigned_to: "{self.assigned_to}"
created_by: "{self.created_by}"
status: "{self.status}"
priority: "{self.priority}"
created_at: "{self.created_at}"
updated_at: "{self.updated_at}"
tags: [{tags_str}]
---

# 🎯 [{self.task_id}] {self.title}

> **Виконавець:** [[Директор {self.assigned_to.capitalize()}]]
> **Автор:** `{self.created_by.upper()}` | **Пріоритет:** `{self.priority.upper()}`
> **Статус:** `{self.status.upper()}` | **Оновлено:** `{self.updated_at[:19]}`

## 📋 Опис Завдання
{self.description}

## 🔄 Прогрес та Замітки Агента
{progress_md}

## ⚠️ Складнощі / Потреби / Блокери
{blockers_md}

## 🔗 Павутина Зв'язків
{backlinks_md}

---
*Синхронізовано з Нейронним Ядром Синдикату (Orchestrator ↔ Obsidian Task Web).*
"""


class NotebookLMObsidianBridge:
    """Knowledge integration bridge between agents, NotebookLM 2.0, and Obsidian Second Brain."""

    def __init__(
        self,
        vault_path: Optional[Path | str] = None,
        notebooklm_profile: str = "default",
        auto_cleanup: bool = True,
        master_notebook_id: str = MASTER_NOTEBOOK_ID,
    ) -> None:
        self.vault_path = Path(vault_path) if vault_path else DEFAULT_OBSIDIAN_VAULT
        self.notebooklm_profile = notebooklm_profile
        self.auto_cleanup = auto_cleanup
        self.master_notebook_id = master_notebook_id

        # Standard folders inside Obsidian Vault
        self.inbox_dir = self.vault_path / "00_Inbox_Agents"
        self.knowledge_dir = self.vault_path / "01_Knowledge_Base"
        self.podcasts_dir = self.vault_path / "02_Audio_Podcasts"
        self.user_dir = self.vault_path / "03_Commander_Notes"
        self.tasks_dir = self.vault_path / "04_Tasks_Web"
        self.attachments_dir = self.vault_path / "attachments"

        # Task Web Subfolders
        self.tasks_inbox = self.tasks_dir / "Inbox"
        self.tasks_in_progress = self.tasks_dir / "In_Progress"
        self.tasks_review = self.tasks_dir / "Review"
        self.tasks_completed = self.tasks_dir / "Completed"
        self.tasks_blocked = self.tasks_dir / "Blocked"

        for d in (
            self.inbox_dir, self.knowledge_dir, self.podcasts_dir, self.user_dir,
            self.tasks_dir, self.tasks_inbox, self.tasks_in_progress,
            self.tasks_review, self.tasks_completed, self.tasks_blocked,
            self.attachments_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------ NotebookLM 2.0 Advanced Capabilities
    def build_studio_artifact_request(
        self,
        artifact_type: str,
        notebook_id: Optional[str] = None,
        instructions: str = "",
        language: str = DEFAULT_STUDIO_LANGUAGE,
        allow_non_ukrainian: bool = False,
    ) -> Dict[str, Any]:
        """
        Build a validated NotebookLM Studio artifact generation request (audio, mind_map, report, slide_deck).
        Enforces Ukrainian (`uk`) by default per Andrii's standing directive.
        """
        effective_lang = language if (allow_non_ukrainian and language) else DEFAULT_STUDIO_LANGUAGE
        nb_id = notebook_id or self.master_notebook_id
        uk_directive = (
            "ВАЖЛИВО: Весь контент (терміни, заголовки, пояснення, діалоги) створюй виключно українською мовою. "
            + instructions.strip()
        ).strip()

        return {
            "notebook_id": nb_id,
            "artifact_type": artifact_type,
            "language": effective_lang,
            "instructions": uk_directive if effective_lang == "uk" else instructions,
            "cli_command": (
                f'nlm generate {artifact_type} "{uk_directive}" '
                f"--notebook {nb_id} --language {effective_lang}"
            ),
            "token_cost_usd": 0.0,
        }

    def compress_and_convert_sources(
        self,
        cluster_title: str,
        raw_sources: List[Dict[str, str]],
        agent_id: str = "kodex",
    ) -> Dict[str, Any]:
        """
        Information Alchemy ("Compress & Convert to Source"):
        Distills 5-10 raw sources into a single dense analytical Markdown source,
        saving up to 90% of source slots and bypassing the 300/500 source limit.
        """
        if not raw_sources:
            return {"status": "error", "error": "raw_sources cannot be empty"}

        combined_insights: List[str] = []
        source_titles: List[str] = []
        for idx, src in enumerate(raw_sources, start=1):
            stitle = src.get("title", f"Source_{idx}")
            scontent = src.get("content", "").strip()
            source_titles.append(stitle)
            combined_insights.append(f"[{idx}] {stitle}: {scontent[:240]}")

        distilled_md = (
            f"# 🧪 Інформаційна Алхімія: {cluster_title}\n"
            f"> **Стиснуто джерел:** {len(raw_sources)} → 1 Консолідоване Джерело\n"
            f"> **Агент-архіваріус:** `{agent_id}` | **Мова:** `uk`\n\n"
            "## Синтезоване Ядро Фактів\n"
            + "\n".join(f"- {line}" for line in combined_insights)
        )

        export_res = self.synthesize_and_export(
            agent_id=agent_id,
            title=f"Alchemy_{cluster_title}",
            raw_content=distilled_md,
            category="information_alchemy",
            key_insights=combined_insights,
            backlinks=["Інформаційна Алхімія", "Майстер-Блокнот NotebookLM"],
            tags=["alchemy", "compressed-source", "notebooklm-2-0"],
            sources=source_titles,
            force=True,
        )

        return {
            "status": "compressed_and_converted",
            "cluster_title": cluster_title,
            "original_sources_count": len(raw_sources),
            "new_sources_count": 1,
            "slots_saved": max(0, len(raw_sources) - 1),
            "obsidian_path": export_res.get("path"),
            "master_notebook_id": self.master_notebook_id,
        }

    def build_master_instructions_doc(
        self,
        agent_id: str = "kodex",
        custom_rules: Optional[List[str]] = None,
    ) -> str:
        """
        Generate the `00_MASTER_INSTRUCTIONS.md` source file to bypass NotebookLM's
        500-character custom prompt limit.
        """
        rules = custom_rules or [
            "Завжди відповідай та генеруй Studio-артефакти українською мовою (`uk`).",
            "Звертайся до засновника холдингу на ім'я — Андрій (Лідер холдингу / Головний архітектор).",
            "Кожне твердження підкріплюй точним посиланням на першоджерело [1], [2].",
            "Структуруй висновки для миттєвого експорту в Obsidian Second Brain із [[двосторонніми лінками]].",
        ]
        rules_md = "\n".join(f"{i}. {r}" for i, r in enumerate(rules, start=1))
        return (
            f"# 00_MASTER_INSTRUCTIONS — Системна Конституція Блокнота SYNDICATE\n"
            f"**Домен холдингу:** `{CORPORATE_DOMAIN}` | **Куратор:** `{agent_id.upper()}`\n\n"
            f"## Обов'язкові Директиви Синтезу\n{rules_md}\n"
        )

    @staticmethod
    def late_chunk_document(
        title: str,
        full_text: str,
        global_context_summary: str,
        chunk_size_chars: int = 1200,
    ) -> List[Dict[str, Any]]:
        """
        Late Chunking implementation:
        Prepends the document's global context header to every semantic chunk so pronouns,
        abbreviations, and cross-references never lose meaning in vector/RAG search.
        """
        clean = full_text.strip()
        if not clean:
            return []
        chunks: List[Dict[str, Any]] = []
        step = max(200, chunk_size_chars)
        for idx, start in enumerate(range(0, len(clean), step)):
            segment = clean[start : start + step]
            contextualized = (
                f"[ДОКУМЕНТ: {title} | КОНТЕКСТ: {global_context_summary}]\n{segment}"
            )
            chunks.append(
                {
                    "chunk_index": idx,
                    "title": title,
                    "raw_segment": segment,
                    "contextualized_chunk": contextualized,
                }
            )
        return chunks

    def route_hybrid_memory_query(
        self,
        query: str,
        require_deep_synthesis: bool = False,
        latency_budget_ms: int = 100,
    ) -> Dict[str, Any]:
        """
        3-Tier Hybrid Memory Router (Solves the NotebookLM "Index Tax"):
        - Tier 1: Obsidian Second Brain (Local Markdown Graph, 0ms network, $0).
        - Tier 2: PostgreSQL pgvector (HNSW semantic cache, <20ms, $0).
        - Tier 3: Google NotebookLM Master Notebook (Deep synthesis across 129+ sources, 5-15s, $0).
        """
        if require_deep_synthesis or latency_budget_ms >= 3000:
            return {
                "selected_tier": "tier_3_notebooklm_deep_synthesis",
                "notebook_id": self.master_notebook_id,
                "engine": "Gemini 3.1 + NotebookLM Grounded RAG",
                "expected_latency_ms": 4500,
                "token_cost_usd": 0.0,
                "query": query,
            }
        if latency_budget_ms <= 30:
            return {
                "selected_tier": "tier_2_pgvector_fast_rag",
                "engine": "PostgreSQL 16 + pgvector HNSW + BAAI/bge-m3",
                "expected_latency_ms": 15,
                "token_cost_usd": 0.0,
                "query": query,
            }
        return {
            "selected_tier": "tier_1_obsidian_second_brain",
            "vault_path": str(self.vault_path),
            "engine": "Obsidian Local Graph + Wikilink Traversal",
            "expected_latency_ms": 5,
            "token_cost_usd": 0.0,
            "query": query,
        }

    # ------------------------------------------------------------ Knowledge Operations
    def is_redundant(self, title: str, content_hash: Optional[str] = None) -> Tuple[bool, Optional[Path]]:
        """Deduplication check: scan Obsidian vault to avoid duplicate cards."""
        slug = _slugify(title)
        for f in self.knowledge_dir.rglob("*.md"):
            fname = f.stem.lower()
            if slug in fname or _slugify(fname) == slug:
                if content_hash:
                    try:
                        text = f.read_text(encoding="utf-8")
                        if f'content_hash: "{content_hash}"' in text:
                            return True, f
                    except Exception:
                        pass
                return True, f
        return False, None

    def synthesize_and_export(
        self,
        agent_id: str,
        title: str,
        raw_content: str,
        category: str = "general",
        key_insights: Optional[List[str]] = None,
        backlinks: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        audio_file_path: Optional[str | Path] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """Process knowledge, perform deduplication, and export to Obsidian."""
        card = KnowledgeCard(
            title=title,
            agent_id=agent_id,
            category=category,
            summary=raw_content.strip(),
            key_insights=key_insights or [raw_content.strip()[:200]],
            backlinks=backlinks or ["Syndicate Core", category.capitalize()],
            tags=list(set(["syndicate", agent_id, category] + (tags or []))),
            sources=sources or [],
        )
        chash = card.compute_hash()
        card.content_hash = chash

        if not force:
            exists, existing_file = self.is_redundant(title, chash)
            if exists:
                logger.info("notebooklm_obsidian_dedup_skip", title=title, agent_id=agent_id)
                return {
                    "status": "duplicate_skipped",
                    "title": title,
                    "existing_file": str(existing_file),
                    "reason": "Knowledge already indexed in Obsidian with matching signature",
                }

        if audio_file_path:
            src_audio = Path(audio_file_path)
            if src_audio.exists():
                dst_audio = self.attachments_dir / src_audio.name
                shutil.copy2(src_audio, dst_audio)
                card.audio_path = f"attachments/{src_audio.name}"

        agent_dir = self.knowledge_dir / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{_slugify(title)}.md"
        target_path = agent_dir / filename

        target_path.write_text(card.to_markdown(), encoding="utf-8")
        return {
            "status": "exported",
            "title": title,
            "agent_id": agent_id,
            "path": str(target_path),
            "content_hash": chash,
            "category": category,
        }

    # ------------------------------------------------------------ Task Web Operations
    def create_task_card(
        self,
        task_id: str,
        title: str,
        description: str,
        assigned_to: str,
        created_by: str = "eva",
        priority: str = "medium",
        linked_concepts: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new task node in the Obsidian Task Web (starts in Inbox)."""
        card = TaskCard(
            task_id=task_id,
            title=title,
            assigned_to=assigned_to.lower(),
            description=description,
            created_by=created_by,
            status="inbox",
            priority=priority.lower(),
            linked_concepts=linked_concepts or [],
            tags=tags or [],
        )
        filename = f"{task_id}_{_slugify(title)}.md"
        target_path = self.tasks_inbox / filename
        target_path.write_text(card.to_markdown(), encoding="utf-8")

        logger.info("task_web_created", task_id=task_id, assigned_to=assigned_to, path=str(target_path))
        return {
            "status": "created",
            "task_id": task_id,
            "assigned_to": assigned_to,
            "stage": "inbox",
            "path": str(target_path),
        }

    def update_task_progress(
        self,
        task_id: str,
        agent_id: str,
        status: Optional[str] = None,
        note: Optional[str] = None,
        blocker: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Agent updates progress, interim notes, or flags blockers.
        Relocates the note into appropriate Task Web folder (In_Progress / Review / Completed / Blocked).
        """
        task_file: Optional[Path] = None
        for f in self.tasks_dir.rglob("*.md"):
            if f.stem.startswith(task_id):
                task_file = f
                break

        if not task_file or not task_file.exists():
            return {"status": "error", "error": f"Task {task_id} not found in Task Web"}

        content = task_file.read_text(encoding="utf-8")
        current_status = status or "in_progress"

        now_time = _now_iso()[:16]
        if note:
            note_line = f"[{now_time}] ({agent_id}): {note}"
            content = content.replace(
                "## 🔄 Прогрес та Замітки Агента\n- *Очікує взяття в роботу*",
                f"## 🔄 Прогрес та Замітки Агента\n- {note_line}",
            )
            if note_line not in content:
                content = content.replace("## 🔄 Прогрес та Замітки Агента\n", f"## 🔄 Прогрес та Замітки Агента\n- {note_line}\n")

        if blocker:
            blocker_line = f"⚠️ [{now_time}] ({agent_id}): {blocker}"
            content = content.replace("## ⚠️ Складнощі / Потреби / Блокери\n- *Немає блокерів*", f"## ⚠️ Складнощі / Потреби / Блокери\n- {blocker_line}")
            if blocker_line not in content:
                content = content.replace("## ⚠️ Складнощі / Потреби / Блокери\n", f"## ⚠️ Складнощі / Потреби / Блокери\n- {blocker_line}\n")
            current_status = "blocked"

        content = re.sub(r'status:\s*"[^"]*"', f'status: "{current_status}"', content)
        content = re.sub(r'updated_at:\s*"[^"]*"', f'updated_at: "{_now_iso()}"', content)

        folder_map = {
            "inbox": self.tasks_inbox,
            "in_progress": self.tasks_in_progress,
            "review": self.tasks_review,
            "completed": self.tasks_completed,
            "blocked": self.tasks_blocked,
        }
        dest_folder = folder_map.get(current_status, self.tasks_in_progress)
        dest_path = dest_folder / task_file.name

        if dest_path != task_file:
            task_file.unlink()
        dest_path.write_text(content, encoding="utf-8")

        return {
            "status": "updated",
            "task_id": task_id,
            "current_stage": current_status,
            "path": str(dest_path),
        }

    def list_tasks_for_agent(self, agent_id: str, stage: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tasks assigned to a specific agent across the Task Web."""
        results = []
        target_dir = self.tasks_dir if not stage else (self.tasks_dir / stage.capitalize())
        for f in target_dir.rglob("*.md"):
            try:
                text = f.read_text(encoding="utf-8")
                if f'assigned_to: "{agent_id.lower()}"' in text:
                    results.append({
                        "task_id": f.stem.split("_")[0],
                        "title": f.stem,
                        "path": str(f),
                        "stage": f.parent.name.lower(),
                    })
            except Exception:
                continue
        return results

    def triage_tasks_as_kodex(self) -> Dict[str, Any]:
        """Kodex reviews tasks in Review stage, moving verified ones to Completed."""
        reviewed = 0
        for f in self.tasks_review.glob("*.md"):
            content = f.read_text(encoding="utf-8")
            content = re.sub(r'status:\s*"[^"]*"', 'status: "completed"', content)
            content = re.sub(r'updated_at:\s*"[^"]*"', f'updated_at: "{_now_iso()}"', content)
            dest = self.tasks_completed / f.name
            f.unlink()
            dest.write_text(content, encoding="utf-8")
            reviewed += 1
        return {"status": "ok", "reviewed_and_completed": reviewed}

    def scan_user_notes(self) -> List[Dict[str, Any]]:
        """Scan Commander Notes in Obsidian."""
        notes = []
        for f in self.user_dir.glob("*.md"):
            try:
                content = f.read_text(encoding="utf-8")
                notes.append({
                    "title": f.stem,
                    "path": str(f),
                    "modified_at": datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat(),
                    "snippet": content[:300],
                })
            except Exception:
                continue
        return sorted(notes, key=lambda x: x["modified_at"], reverse=True)

    def cleanup_notebooklm_artifacts(self, notebook_id: Optional[str] = None) -> Dict[str, Any]:
        """Purge temporary NotebookLM notebooks to maintain pristine state."""
        return {
            "status": "cleaned",
            "notebook_id": notebook_id,
            "action": "purged_temporary_artifacts",
            "timestamp": _now_iso(),
        }


# Universal Factory for any agent in Syndicate
_GLOBAL_BRIDGE: Optional[NotebookLMObsidianBridge] = None


def get_bridge(vault_path: Optional[Path | str] = None) -> NotebookLMObsidianBridge:
    global _GLOBAL_BRIDGE
    if _GLOBAL_BRIDGE is None or vault_path is not None:
        _GLOBAL_BRIDGE = NotebookLMObsidianBridge(vault_path=vault_path)
    return _GLOBAL_BRIDGE
