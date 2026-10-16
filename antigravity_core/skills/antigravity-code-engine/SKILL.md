---
name: antigravity-code-engine
description: Autonomous code synthesis, AST refactoring, isolated sandbox testing, and test-driven development (TDD) for the Syndicate.
---

# Antigravity Code Engine Skill

This skill governs autonomous code development within the EVA SYNDICATE repository.

## Capabilities & Workflows:
1. **Source-Driven Development:** Always inspect existing interfaces, types, and schemas before writing new code.
2. **Test-Driven Verification:** Every generated component must include corresponding pytest test cases in `tests/`.
3. **AST Refactoring:** Make surgical, atomic edits using file replace tools rather than replacing full files blindly.
4. **Linting & Safety:** Enforce PEP 8, ruff compliance, and zero hardcoded credentials. All secrets must route through Vault.
