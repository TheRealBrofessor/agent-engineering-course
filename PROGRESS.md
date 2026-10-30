# Course progress — verified state

**Date:** 2026-10-30. **Branch:** `feat/user-configurable-models`.

Tier 0 and Tier 1 behavior is preserved. Tiers 2–7 now ship provider-neutral, stdlib-first learner contracts, deterministic fixture validators, bounded child runners, and evidence headings. Validators never read `.env`, persist credentials, or run during `status`; only the active tier can run. Learner artifacts remain under gitignored `work/` and every promotion still requires explicit `--attest`.

The full suite is the source of truth for the current count. No learner completion is recorded by development.
