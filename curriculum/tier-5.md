# Tier 5 — Deep agents

**Status: roadmap only; validator unavailable.** Prerequisite: Tier 4 gate passed. Promotion remains closed.

## Concept and cumulative project
Turn a single-loop agent into a bounded multi-step worker: explicit plan, delegated subtask, file-backed notes, and a stop condition. Delegation should reduce complexity, not multiply unverified claims. Count steps, tool calls, and context use; test an aborted run and a resumption from saved state.

## Planned learner artifact
A small coordinator with one specialist worker, a durable task log, a per-task budget, and an isolated runner for code tools. Local container isolation is an option only after its actual policies are verified; a process boundary alone is not a sandbox. Keep the local model on loopback.

## Gate target
Show a trace of bounded planning and delegation, verify that a disallowed sandbox action is denied, and recover from a forced interruption without silently repeating a consequential action. The Tier 5 lab/validator is **not shipped**; no isolation guarantee is claimed yet.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
