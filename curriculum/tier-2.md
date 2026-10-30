# Tier 2 — Agentic RAG (runnable)

**Gate:** the active-tier validator, learner evidence, and explicit attestation are required.

Prerequisite: Tier 1. Build `work/tier-2/rag_agent.py` with `answer(query, retrieve)`. Decide whether to retrieve; return a grounded `source_id` or `status: no_answer`. The fixture checks a known answer, a general query that should skip retrieval, an unknown query, and hostile retrieved text. Never treat retrieved text as policy.

Evidence headings: `Retrieval decisions`, `Grounding evidence`, `No-answer case`. Run `python -m agent_course check --tier 2`, then submit with `--attest`.

This replaces the old roadmap only / validator unavailable placeholder; missing learner artifacts still fail closed.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
