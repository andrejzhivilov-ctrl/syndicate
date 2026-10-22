# 3-Layer Agent Architecture & Self-Annealing Engine

> Based on the proven Antigravity architecture pattern (by Duncan Rogoff & Anthropic best practices).

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas business logic and code execution are deterministic.

## The 3 Layers

### Layer 1: Directive (What to do)
- Standard Operating Procedures (SOPs) written in Markdown, living in `directives/`.
- Defines the goals, inputs, tools/scripts to use, outputs, and edge cases.
- Natural language instructions formatted for autonomous execution.

### Layer 2: Orchestration (Decision Making)
- This is the agent (Antigravity).
- Intelligent routing: reads directives, calls execution scripts in the right order, handles errors, and updates directives with learnings.
- Do not perform complex multi-step work directly in chat if it can be offloaded to deterministic scripts.

### Layer 3: Execution (Doing the work)
- Deterministic Python/Node scripts in `execution/`.
- Environment variables and API keys stored in `.env`.
- Handles API calls, web scraping, data transformations, and file operations.
- Fast, testable, repeatable.

## Self-Annealing Loop (Self-Healing)
Errors are learning opportunities. When a script or process fails:
1. Read the exact error message and stack trace.
2. Fix the script in `execution/` and test it immediately.
3. Update the corresponding `directives/` SOP with the newfound constraint (API rate limits, timeouts, schema updates).
4. System is now permanently stronger.
