# Agent Engineering Course — fresh-session handoff

**Read first:** `/home/professor/agent-engineering-course/README.md`, `PROGRESS.md`, the design and plan in `docs/superpowers/`, then the active lesson. This is Professor's original course—not the separate NVIDIA reference clone. Stay on `feat/keyless-course-engine` unless Professor chooses integration. Never read or reuse the old clone's `secrets.env`.

## Non-negotiable rules
- No API keys for model inference, embeddings, or public search; local Ollama and public anonymous search with clearly labeled offline corpus fallback.
- Tier 0→Tier 7 are strictly sequential. A gate must run and learner evidence must be personally attested; no skipped tiers or assistant-written exercise answers.
- `status` is read-only. Tier 2–7 docs are roadmap-only and validators fail closed. Do not claim these labs completed.
- Keep `work/` and `.course/` gitignored; never paste credentials, private tokens, or learner secrets into notes or chat.
- Before claiming a build passed, run the full suite, live keyless Tier 0 check, locked-tier negative, and confirm no real learner completion was written.

## Context and temporary global setting
Professor asked for a fresh-session handoff near **70% context occupancy** if a trustworthy meter is available. This run temporarily changed `compression.threshold` from `0.5` to `0.75` with explicit approval, then **restored and read back `0.5`** before handoff. A reliable live occupancy meter was unavailable; 70% was **not** measured or claimed. The verified course release is a substantial safe checkpoint. A fresh session is distinct from in-place compression; recheck the saved setting if continuing configuration work.

## Prompt for a fresh session
> Continue Professor's original, zero-API-key Agent Engineering Course at `/home/professor/agent-engineering-course`. Read `README.md`, `PROGRESS.md`, `HANDOFF.md`, and the design/plan in `docs/superpowers/`. Verify git branch, full tests, `python -m agent_course status`, and actual local Ollama/source behavior before work. Tier 0 is learner-owned; do not fill exercise answers or mark completion. Tier 2–7 are roadmap-only until their labs/validators are built. Keep strict sequential gates, no credential use, and preserve the separate reference clone. If the prior run temporarily changed Hermes compression, ensure it was restored to 0.5. Report exact results and one next action; do not claim an unmeasured context percentage.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
