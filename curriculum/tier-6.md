# Tier 6 — Agent safety (runnable)

**Gate:** the active-tier validator, learner evidence, and explicit attestation are required.

Create `work/tier-6/policy.py` with `authorize(action)`. The fixture requires one legitimate allowed action, one denied private write, and rejection of an injection string that asks to ignore policy. Test enforcement rather than trusting prompt instructions, and record residual risk.

Evidence headings: `Threat model`, `Positive and negative tests`, `Injection regression`.

This replaces the old roadmap only / validator unavailable placeholder; missing learner artifacts still fail closed.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
