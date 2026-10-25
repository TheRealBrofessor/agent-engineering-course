# Course progress — verified state

**Date:** 2026-10-25. **Course root:** `/home/professor/agent-engineering-course`. **Branch:** `feat/keyless-course-engine`. **Authoritative learner ledger:** `.course/state.json` (gitignored, absent until the learner submits a tier). The old cloned workshop is reference only; its credentials must not be used here.

## Course release state
- Tier 0 local preflight and evidence gate: **implemented**. With credential-variable names scrubbed from the child environment, `python -m agent_course check --tier 0` returned `Tier 0 check PASS (online)` and exit 0. This checked an actual local Ollama tool call, an actual local embedding, and an anonymous public source route. No learner Tier 0 submission was made.
- Tier 1 learner-owned report-agent contract and fixture validator: **implemented**, but **locked** until Tier 0 passes. Unit checks cover fabricated citations, missing tool calls, no-source abstention, subprocess timeout, and a minimal child environment. No learner implementation or live report exists yet.
- Tier 2–7: **roadmap only**. Their validators are unavailable and promotion fails closed. No GPU-specific or NVIDIA-hosted lab has been run.
- Most recent completed suite before curriculum files were added: `python -m unittest discover -s tests -v` showed 40 tests, 0 failures. Re-run after current docs changes before claiming final green.

## Gates and evidence
- The manager begins with Tier 0 active; Tier 1+ are locked. `status` does not contact network, import learner code, or write a ledger.
- Promotion requires the active tier's validator, a learner-authored evidence file under `work/tier-N/`, and `--attest`. Automated checks are structural; Professor reviews understanding before attesting.
- The course never reads `.env` or saved hosted-model credentials. Public search is best effort; an offline bundled note is labeled `offline` and is not misrepresented as a live source.

## Current next action
Finish curriculum self-tests and end-to-end negative/positive gate checks in a disposable root, then verify the real learner state is still Tier 0. Update this file with fresh counts and exact results. At a safe handoff, restore the user-approved temporary Hermes `compression.threshold` from 0.75 to its verified prior 0.5, and confirm the saved value.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
