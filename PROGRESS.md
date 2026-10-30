# Course progress — verified state

**Date:** 2026-10-30. **Course root:** `/home/professor/agent-engineering-course`. **Branch:** `feat/user-configurable-models`. The active feature adds user-configured provider adapters without changing the learner ledger. **Authoritative learner ledger:** `.course/state.json` (gitignored, absent until the learner submits a tier). The old cloned workshop is reference only; its credentials must not be used here.

## Course release state
- Tier 0 model preflight and evidence gate: **implemented**. Chat and embeddings are configured independently through environment variables and support Ollama, OpenAI-compatible endpoints including OpenRouter, Anthropic, and Gemini. No learner Tier 0 submission was made.
- Tier 1 learner-owned report-agent contract and fixture validator: **implemented**, but **locked** until Tier 0 passes. Unit checks cover fabricated citations, missing tool calls, no-source abstention, subprocess timeout, and a minimal child environment. No learner implementation or live report exists yet.
- Tier 2–7: **roadmap only**. Their validators are unavailable and promotion fails closed. No GPU-specific or NVIDIA-hosted lab has been run.
- Final unit suite: `python -m unittest discover -s tests -v` showed **46 tests, 0 failures**. `python -m compileall -q agent_course tests` and `git diff --check` passed.
- End-to-end keyless check with credential-like environment variable names removed: real `status` showed Tier 0 active; `check --tier 1` returned exit 2 (locked); `check --tier 0` returned exit 0, `PASS (online)`. The real `.course/state.json` remained absent.
- Disposable-root simulation (not Professor's work): Tier 0 `submit --attest` passed, created mode-0600 contiguous ledger; Tier 1 became active; `check --tier 2` returned exit 2; `check --tier 1` failed because no learner `report_agent.py` exists. The temporary root was deleted, and the real learner ledger remained absent.
- Source audit of `agent_course/` found configurable provider URLs, public DuckDuckGo/Wikimedia URLs, and fixture domains; **no `.env` read, credential persistence, or fallback model selection**.
- User-approved global Hermes compression threshold was restored from the temporary `0.75` to its verified prior `0.5` using `hermes config set`; the saved setting read back `0.5`. A reliable live context occupancy meter was not available, so **70% is not claimed**.

## Gates and evidence
- The manager begins with Tier 0 active; Tier 1+ are locked. `status` does not contact network, import learner code, or write a ledger.
- Promotion requires the active tier's validator, a learner-authored evidence file under `work/tier-N/`, and `--attest`. Automated checks are structural; Professor reviews understanding before attesting.
- The course never reads `.env` or saved hosted-model credentials. Public search is best effort; an offline bundled note is labeled `offline` and is not misrepresented as a live source.

## Current next action
Professor reads `curriculum/tier-0.md`, configures their own providers/models, runs `python -m agent_course status` and `python -m agent_course check --tier 0`, writes their own `work/tier-0/notes.md`, and personally submits only after reviewing the four required sections. No tier was marked complete by the assistant. For future development, Tier 2–7 labs need separate approved specifications and validators. The reference clone remains unchanged apart from historical learning/handoff notes.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
