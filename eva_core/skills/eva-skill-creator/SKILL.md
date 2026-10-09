---
name: eva-skill-creator
description: Draft a narrow, testable agent skill and an evaluation plan for human review.
status: draft
---

# Eva Skill Creator

## Required design record
For each proposed skill, prepare:
- Name, purpose, non-goals, intended user request, and examples
- Required inputs and expected output format
- Data sources and provenance requirements
- Tool/capability needs stated separately from the skill text
- Sensitive-data handling and failure behavior
- At least one normal, ambiguous, adversarial, and refusal test
- Known limitations and upstream/license references, if any

## Process
1. Ask what task the skill should improve and how success will be judged.
2. Draft the smallest reusable instruction set that meets that goal.
3. Add tests for factuality, prompt-injection resistance, permission boundaries, and regressions.
4. Identify instructions that conflict with the Eva core prompt or platform policy; the higher-level policy wins.
5. Present the file, tests, provenance, and unresolved risks for Andrii's review.

## Hard boundaries
- A skill is an instruction aid, never an authorization grant.
- Never activate, install, update, or self-modify a skill without separate human approval.
- Do not copy third-party skill text or code unless its license and attribution are verified.
- Do not place secrets, personal records, or live credentials in examples or tests.
