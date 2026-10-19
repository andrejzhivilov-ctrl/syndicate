# Shared knowledge pools — offline intake

## Scope and status

This change creates a local, read-only foundation for skill and prompt pools from the ten attachments provided by the operator. The original large files remain outside Git. The checked-in corpus consists only of short original summaries, taxonomies, review metadata, and SHA-256 fingerprints; it does not reproduce the courses, transcripts, site code, or 2,330 prompt texts.

Every derived item is `review_pending` and `review_only`. No item has been approved or published to all agents. Rights and attribution for every attachment remain unverified. Structural headings and counts were reviewed; the source code/templates and individual prompt bodies were not manually audited.

## Pool layout

- Hash-pinned policy/registry manifest: `config/knowledge_pool_catalog.json`.
- Source inventory and attachment hashes: `config/knowledge_source_registry.json`.
- Separate registries: `config/skill_pool_registry.json`, `config/prompt_pool_registry.json`, `config/knowledge_reference_registry.json`.
- Proposed ServiceHub grants (not loaded/applied): `config/knowledge_pool_grants.json`.
- Short skill drafts: `knowledge_pools/skills/`.
- Prompt templates and taxonomy/index (not the raw prompt corpus): `knowledge_pools/prompts/`.
- Course/model reference maps: `knowledge_pools/references/`.
- Read/search boundary: `src/agent_platform/knowledge_pool.py`.
- Optional host integration: `knowledge.search` / `knowledge.read` in `src/integrations/service_hub.py`; these are unavailable unless a host explicitly supplies those grants.

Search returns ranked metadata only. Reading is a separate item-ID operation, returns one bounded Markdown file, verifies SHA-256, rejects symlinks/path traversal, and never executes content. Catalog target-agent tags are discovery hints, not grants. The host must provide an authenticated, registered agent identity; callers cannot change it through payload fields.

## Review and publication control

- `review_pending` metadata is addressed to KODEX and Marshal reviewers, but `KnowledgePool` defaults to zero authorized readers. Host-supplied review allowlists **and** explicit ServiceHub grants are both required to read; neither reviewer runtime is activated by this catalog.
- Proposed grant set is explicit: KODEX and Marshal each receive only `knowledge.search` + `knowledge.read`, with their own ID in `review_agents` and `shared_agents=[]`. These proposals are recorded in `config/knowledge_pool_grants.json` and each profile; they are `proposed_not_applied`, not loaded by ServiceHub/Vault, and do not activate either runtime. No write, approve, publish, or permission-expansion grant is proposed.
- No approval/publish operation is exposed. A future shared read requires both `status=approved` / `visibility=shared` and a valid detached Marshal HMAC attestation bound to item ID, exact content digest, version, review ID, scan status and time.
- The HMAC key is host-owned and must come from Vault/runtime configuration, never Git or a prompt. Without the key or a valid attestation, even an item whose metadata is manually changed to `approved` remains unreadable to shared agents.
- Static scan pass is necessary but not sufficient: Marshal must independently review content, provenance, rights and domain risk. Rejected or incomplete checks stay quarantined. No attestation is present in the current catalog.
- Reference content cannot change identities, system prompts, capabilities, grants, tools, model selection or live service state.

## Provisional routing (not authorization)

| Pool content | Discovery targets | Guardrails |
|---|---|---|
| Prompt/agent engineering and prompt catalog | KODEX; Alice/Architect for technical reference | Drafts only; untrusted prompt text never becomes system policy. |
| n8n and Make automation | Architect, Dex, KODEX | Design-only; no live n8n/Make grants, credentials, workflows or activation. |
| React/Tailwind examples | Alice, Architect, Dex, Oscar | Review code, dependencies, external calls, assets and licenses before reuse. |
| Video/editing and business-content outlines | Oscar, Dex, Tyler, Eva | No claim of performance; rights and claims must be checked. |
| AI model/provider guides | Ray, KODEX, Alice, Architect | Volatile information; verify against official current sources before decisions. |
| Travel / learning / health / finance / legal prompt categories | Atlas / Kira / Doc-Trainer / Fin-Sam where relevant | Routing tags only. Health, finance and legal content is not verified advice; Russian-jurisdiction tax/legal examples must not be applied in Ukraine without official Ukrainian-source review. |

## Intake findings to preserve

- The master manifest claims 100% completion and 4,700+ files; this was not independently substantiated.
- The PRO XML prompt attachment has 26 visible categories, whose heading counts total 1,729; internal references state 1,703; the manifest claims 61 categories.
- The React/Tailwind attachment has about 60 named top-level template headings while the manifest claims 343. Source code and linked assets require individual security/license review.
- The business-course attachment's body does not substantiate crypto/arbitrage course material; those terms appear as metadata tags only. Do not route it as financial instruction.
- The 2,330 prompt catalog has 30 visible categories and matching heading totals. Individual prompts, safety and reuse rights remain unreviewed.
- The 18-lesson video file is a transcript collection with unconfirmed rights. The 31-lesson n8n / 24-lesson Make course versions and examples require current-version checks.

## Deferred work

No live web fetch, n8n workflow, runtime activation, grant application, source-code execution, prompt bulk import or source publication was performed. Later attachments can be added to the source registry with hashes and review status, then summarized into small derived records after rights and risk checks.
