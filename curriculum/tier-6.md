# Tier 6 — Agent safety

**Status: roadmap only; validator unavailable.** Prerequisite: Tier 5 gate passed. Promotion remains closed.

## Concept and cumulative project
Autonomy needs boundaries outside the model's own promises. Threat-model tool calls, private files, network egress, source prompt injection, and approval bypass. Compare prompt-level instructions with actual filesystem and process policies. Test allowed and denied actions under the same policy. Red-team probes must target only the local lab, with no credentials or unrelated hosts.

## Planned learner artifact
A minimal access policy, local negative/positive test pair, a prompt-injection fixture, a regression suite, and a report distinguishing observed enforcement from intended enforcement. Optional Linux isolation features are verified on the actual host before claiming they work.

## Gate target
Demonstrate one legitimate allowed action, one denied action, and a failed injection attempt while preserving relevant logs and noting residual risk. The Tier 6 validator is **not shipped**; no kernel-level safety claim or hosted privacy router is implied.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
