---
name: syndicate-n8n-and-prompts
description: Practical guide and toolkit for designing FlowLint-verified n8n workflows, structured agent task briefs, and NotebookLM/Obsidian automation pipelines in SYNDICATE. Synthesizes knowledge_pools/skills/n8n-workflow-design, automation-platform-translation, prompt-catalog-taxonomy, and Kodex bridges.
---

# Syndicate n8n Workflow & Prompt Engineering (`syndicate-n8n-and-prompts`)

## 1. FlowLint-Compliant n8n Workflow Design
When designing or generating n8n workflows for Syndicate (`src/n8n_templates.py` or `ArchitectAgent`):
1. **Contract First:** Define trigger source (Telegram webhook, Cron schedule, Nextcloud/Seafile file watcher, Obsidian Task Web hook), input JSON schema, and output schema.
2. **Zero Hardcoded Secrets:** Never embed API keys, tokens, or chat IDs in workflow JSON. Pull credentials from Vault/environment at runtime.
3. **HMAC & Allowlist Enforcement:**
   - All inbound webhooks (`/webhook/telegram`, `/webhook/error`) must verify `X-Webhook-Signature` (HMAC-SHA256).
   - Enforce sender allowlists (`EVA_TELEGRAM_ALLOWED_CHAT_IDS`, `KODEX_TELEGRAM_ALLOWED_CHAT_IDS`).
4. **Error Routing (DLQ):** Every workflow must attach an `errorTrigger` path routing failures to `/webhook/error` (`ErrorCollector` with SHA-256 deduplication and PII scrubbing).
5. **Human-in-the-Loop (HITL) Gates:** Any workflow involving financial transactions (`fin`, `sam`, `jack`), external publishing (`oscar`, `tyler`), or protected file deletion (`kodex` with `andrii_protected`) must pause for explicit approval by Andrii.

## 2. NotebookLM ↔ Obsidian Second Brain Automation
- **Ingestion:** Agents push raw sources (PDF, DOCX, YouTube transcripts, audio notes, web research) into NotebookLM via `NotebookLMObsidianBridge`, extract grounded insights, and auto-purge temporary NotebookLM notebooks (`cleanup_notebooklm_artifacts`).
- **Deduplication:** Check `is_redundant(title, content_hash)` before writing to Obsidian (`01_Knowledge_Base/<agent_id>/`).
- **Obsidian Task Web (`04_Tasks_Web/`):**
  - `Inbox/` -> `In_Progress/` -> `Review/` -> `Completed/` (or `Blocked/`).
  - Agents append timestamped progress notes and blockers directly to task Markdown cards with `[[backlinks]]`.
  - **Kodex** triages `Review/` cards and moves verified deliverables into `Completed/`.

## 3. Structured Task Brief Template
Use this structure when formulating cross-agent orders or contractor dispatches (`AntigravityContractorGateway`):
```text
Завдання: [чіткий очікуваний результат]
Замовник (Директор): [agent_id] -> Канал: channel-[agent_id]
Вхідні факти та джерела: [перевірені дані / шляхи до файлів]
Обмеження безпеки: [Zero-Trust / без витоку PII / тільки у дозволеній зоні]
Критерії приймання (DoD): [успішні + відмовні тести, git diff --check]
```
