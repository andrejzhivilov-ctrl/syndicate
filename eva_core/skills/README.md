# Eva skills — deployment drafts

These are original, reviewable skill drafts. They are not installed or activated in Hermes yet.
The profile grants no tool capabilities; a skill cannot add its own permissions or enable a service.

- `eva-humanizer`: an original local draft for truthful style editing; upstream provenance and licensing have not been verified, and no upstream implementation is included. It excludes impersonation, fabricated feelings/experience, and detector-evasion goals. Verify any future upstream source and its license before reuse.
- `eva-summary`: grounded summaries with decisions, tasks, risks, open questions, and provenance.
- `eva-deep-research`: source-led research with citations, conflict handling, and confidence labels; references Hermes `grounded-citations` without copying its implementation.
- `eva-skill-creator`: draft-only skill design and evaluation; no self-activation or privilege changes.
- `eva-prompt-lab`: prompt design and test cases; no secrets in prompts.

The separate n8n workflow-author skill is deferred to the Architect phase. No Architect profile or permissions are created in this Eva package.
