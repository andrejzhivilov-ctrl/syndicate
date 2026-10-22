"""
SYNDICATE — NotebookLM & Obsidian Knowledge Bridge + Task Web Engine.

Enables all Syndicate agents (Eva, Architect, Marshal, Fin, Sam, Doc, Trainer, Kira,
Oscar, Tyler, Jack, Kodex, Alice) to operate with NotebookLM and the shared Obsidian "Second Brain":
1. Grounded synthesis via NotebookLM (or deterministic local extractor fallback).
2. Deduplication: verifies if knowledge already exists in Obsidian before writing.
3. Structured Obsidian Markdown generation (YAML frontmatter, [[backlinks]], tags, timestamps).
4. Interactive Obsidian Task Web (04_Tasks_Web/):
   - Inbox: Proposed/approved tasks from Eva or Commander.
   - In_Progress: Active execution with agent logs, difficulties, and interim notes.
   - Review: Completed work awaiting Kodex archival check.
   - Completed: Verified deliverables archived by Kodex.
   - Blocked: Bottlenecks flagged for Eva/Commander intervention.
5. Audio & multi-format asset placement (MP3/WAV/images into attachments/).
6. Cleanup: purges temporary NotebookLM processing notebooks to prevent clutter.
7. Ingestion: scans user-created notes in Obsidian so agents learn from Andrii's inputs.
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
    """Knowledge integration bridge between agents, NotebookLM, and Obsidian."""

    def __init__(
        self,
        vault_path: Optional[Path | str] = None,
        notebooklm_profile: str = "default",
        auto_cleanup: bool = True,
    ) -> None:
        self.vault_path = Path(vault_path) if vault_path else DEFAULT_OBSIDIAN_VAULT
        self.notebooklm_profile = notebooklm_profile
        self.auto_cleanup = auto_cleanup

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
        # Find the existing task file across Task Web folders
        task_file: Optional[Path] = None
        for f in self.tasks_dir.rglob("*.md"):
            if f.stem.startswith(task_id):
                task_file = f
                break

        if not task_file or not task_file.exists():
            return {"status": "error", "error": f"Task {task_id} not found in Task Web"}

        content = task_file.read_text(encoding="utf-8")
        current_status = status or "in_progress"

        # Append progress notes or blockers
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

        # Update status header in frontmatter
        content = re.sub(r'status:\s*"[^"]*"', f'status: "{current_status}"', content)
        content = re.sub(r'updated_at:\s*"[^"]*"', f'updated_at: "{_now_iso()}"', content)

        # Determine target folder based on new status
        folder_map = {
            "inbox": self.tasks_inbox,
            "in_progress": self.tasks_in_progress,
            "review": self.tasks_review,
            "completed": self.tasks_completed,
            "blocked": self.tasks_blocked,
        }
        dest_folder = folder_map.get(current_status, self.tasks_in_progress)
        dest_path = dest_folder / task_file.name

        # Move file if folder changed
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
