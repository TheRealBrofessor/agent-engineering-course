# Tier 2 — Agentic RAG

**Status: roadmap only; validator unavailable.** Prerequisite: Tier 1 gate passed. Promotion from Tier 2 is disabled until its lab/validator is implemented and tested.

## Concept and cumulative project
A retrieval assistant should decide **whether** to retrieve, select relevant local documents, and cite exactly the passages it used. Extend the Tier 1 report agent into an IT help-desk assistant using a local embedding model and a local FAISS index. Contrast a direct-answer route with a retrieval route; avoid needless retrieval when a query asks only for general workflow guidance. Untrusted retrieved text must not override the user's task or tool policy.

## Planned learner artifact
An index over an intentionally small, non-sensitive help-desk corpus; a retrieval tool returning source IDs/snippets; an answer function that cites returned IDs; an abstention when no relevant passage exists. The future lab will include a fixture for a known answer, an unrelated query, and a prompt-injection-bearing document.

## Gate target
Before Tier 3 unlocks, the learner must show correct retrieval decisions, grounded source IDs, a no-answer case, tests against unseen questions, and a written explanation of one retrieved false positive. The grader is **not shipped** in this release; adding notes or code alone cannot promote Tier 2. The embedding provider and model must be recorded for reproducibility.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
