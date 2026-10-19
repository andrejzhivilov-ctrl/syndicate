# Review: HinkoK/agent-skills

**Reviewed source:** [`HinkoK/agent-skills`](https://github.com/HinkoK/agent-skills), commit `2fb9337c53bd164c2c8d6bad04894ea3d6846e18` (2026-06-14), MIT. The checkout was read-only. The six skill entry points, their README/reference files and scripts were statically reviewed; scripts, installers, API calls and model-provider calls were not run.

## Decisions

| Skill | Decision | Findings |
|---|---|---|
| `online-store-legitimacy-checks` | **Selected for Tyler, adapted and registered as reference-only.** | The entry point and its single `spelexperten-example.md` reference are static guidance; no executable script, network call or secret requirement. The example is Denmark/EU-specific, so the local Tyler version explicitly prohibits transferring those legal assumptions to Ukraine, entering checkout/account flows, handling payment data, contacting sellers or guaranteeing safety. Upstream files and MIT license are retained under `skills/vendor/HinkoK/agent-skills/`. |
| `obsidian-vault` | **Deferred; not copied.** | Filesystem-first workflow overlaps KODEX's existing Obsidian reference and describes creating, editing, moving and renaming vault content. No new vault path or filesystem grant is introduced. |
| `aftercall` | **Rejected for current scope; not copied or run.** | Includes therapy/coaching, personal-support and emotionally sensitive recordings/transcripts, plus optional transcription and Telegram/Obsidian exports. The helper script only formats a prompt, but the workflow handles sensitive material and is not appropriate for this task. The bundled `aftercall.skill` archive is not byte-identical to the folder's README/SKILL.md (its references and helper script match); the archive was not installed. No audio or medical data was opened or processed. |
| `deep` | **Rejected; not copied or run.** | Requires `PARALLEL_API_KEY`; `deep.sh` sources an environment file, and `deep_research.py` sends the question in a POST to `api.parallel.ai`, polls for a result, and returns the raw response. This would disclose task content to an external provider and may incur provider usage. No key was read or sent; no API call was made. |
| `troitsa` | **Deferred; not copied or used.** | Recommends GPT/DeepSeek/Gemini or other provider/CLI calls and a multi-model workflow that overlaps existing role-based review. It is not permission to select models, transmit prompts or spend provider budget. |
| `webd` | **Deferred; not copied.** | UI/landing-page design guidance and a catalogue of external component libraries are outside the selected non-`apps/` scope. Library freshness/licenses and implementation costs are not verified by the skill; several conversion/performance claims lack citations in the bundled references. |

## Installed/adapted item

- Local Tyler adapter: `tyler_core/skills/tyler-store-legitimacy-review/SKILL.md`.
- Provenance is registered in `config/skill_library.json` and assigned via Tyler's read-only `reference_skills` list. Exact upstream files remain in Git for audit/hash verification but are not exposed as selectable runtime resources; Tyler receives only the local adaptation.
- `tyler` remains `prepared_not_enabled`; no capability, service, grant or external research access was added.
- The upstream MIT license and selected source files are preserved. `SkillLibrary.verify()` confirms the registered file hashes; the loader marks all content as untrusted reference material and executes no scripts.

This review does not certify the upstream repository or its recommendations. Imported text is subordinate to SYNDICATE policy and the user's instructions.
