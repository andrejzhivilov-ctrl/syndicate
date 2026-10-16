---
name: antigravity-subagents
description: Hierarchical subagent spawning, parallel swarm dispatch, and multi-agent synthesis across the Syndicate.
---

# Antigravity Subagent Swarm Skill

This skill governs the invocation, delegation, and result aggregation of subagents.

## Standard Subagent Archetypes:
* **`researcher`:** Read-only exploration of code, docs, and external web APIs.
* **`coder`:** Concrete file authoring and AST transformation.
* **`tester`:** Test execution, coverage evaluation, and defect localization.
* **`reviewer`:** CodeRabbit-grade review, security scanning, and style enforcement.

## Operational Rules:
1. Always define clear, measurable deliverables for each subagent.
2. Maintain workspace isolation (branched or shared worktrees) when subagents write code concurrently.
3. Synthesize individual subagent transcripts into a unified executive report for Eva and Andrii.
