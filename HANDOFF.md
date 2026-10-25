# Agent Engineering Course — fresh-session handoff

**Read first:** `/home/professor/agent-engineering-course/README.md`, `PROGRESS.md`, the design and plan in `docs/superpowers/`, then the active lesson. This is Professor's original course—not the separate NVIDIA reference clone. Stay on `feat/keyless-course-engine` unless Professor chooses integration. Never read or reuse the old clone's `secrets.env`.

## Non-negotiable rules
- No API keys for model inference, embeddings, or public search; local Ollama and public anonymous search with clearly labeled offline corpus fallback.
- Tier 0→Tier 7 are strictly sequential. A gate must run and learner evidence must be personally attested; no skipped tiers or assistant-written exercise answers.
- `status` is read-only. Tier 2–7 docs are roadmap-only and validators fail closed. Do not claim these labs completed.
- Keep `work/` and `.course/` gitignored; never paste credentials, private tokens, or learner secrets into notes or chat.
- Before claiming a build passed, run the full suite, live keyless Tier 0 check, locked-tier negative, and confirm no real learner completion was written.

## Context and temporary global setting
Professor asked for a fresh-session handoff near **70% context occupancy** if a trustworthy meter is available. With explicit approval, this run changed `hermes config get compression.threshold` from `0.5` to `0.75`; a running session may have cached its old value. **Restore before handoff:** `hermes config set compression.threshold 0.5`, then verify `hermes config get compression.threshold` says `0.5`. In-place compression is not a fresh session. Never assert 70% reached without a live reading; at an unmeasurable threshold, hand off after a verified substantial work unit.

## Prompt for a fresh session
> Continue Professor's original, zero-API-key Agent Engineering Course at `/home/professor/agent-engineering-course`. Read `README.md`, `PROGRESS.md`, `HANDOFF.md`, and the design/plan in `docs/superpowers/`. Verify git branch, full tests, `python -m agent_course status`, and actual local Ollama/source behavior before work. Tier 0 is learner-owned; do not fill exercise answers or mark completion. Tier 2–7 are roadmap-only until their labs/validators are built. Keep strict sequential gates, no credential use, and preserve the separate reference clone. If the prior run temporarily changed Hermes compression, ensure it was restored to 0.5. Report exact results and one next action; do not claim an unmeasured context percentage.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
