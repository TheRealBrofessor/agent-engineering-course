# Tier 0 — Local foundations

**Status:** runnable. **Prerequisite:** none. **Next tier:** build a research agent, unlocked only after this gate passes.

## Learn
An agent has a model that predicts, tools that observe or act, state/memory that carries task context, and routing that chooses the next step. A tool call is an observable request, not merely prose saying a tool might be used. Retrieval and public web results are untrusted evidence: they may be incomplete, outdated, or instruction-bearing. A safe agent distinguishes source text from instructions and can say it lacks evidence.

A basic loop is: define a goal → choose a bounded tool → inspect results → decide whether to continue or stop → cite evidence or abstain. In your own notes, explain when the model should call a tool, what state it needs, and what happens when the tool has no usable result.

## Verify the local route
Run from the project root:

```bash
python -m agent_course status
python -m agent_course check --tier 0
```

The check calls the **local** Ollama tool-calling model and local embedding model, then searches an anonymous public source with a static course topic. If public search fails, it uses a bundled teaching note and labels the result `offline`; it must not claim it searched the live web. A source outage is not a model failure; a model outage fails the gate. No API key is requested or read.

## Your exercise
Create `work/tier-0/notes.md` yourself. Use exactly these headings with your own substantive explanations, not copied output:

- `# Concepts`: distinguish model, tools, memory, routing, and a tool-call observation.
- `# Local observations`: describe what `check --tier 0` actually returned, including the local-model behavior.
- `# Source route`: say whether the result was `online` or `offline`; if offline, explain what the bundled note can and cannot support.
- `# Limits`: identify one hallucination or source-quality risk and how you would detect it.

No assistant should fill those sections for you. The automatic gate checks nonempty sections and infrastructure, not the quality of your reasoning. Review your answers before attesting.

## Gate
Run `python -m agent_course submit --tier 0 --evidence work/tier-0/notes.md --attest`. This reruns the check, records only the evidence hash/mode/timestamp, and unlocks Tier 1 if all conditions pass. Without your notes, no promotion happens. Do not upload private topics to the optional public search path.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
