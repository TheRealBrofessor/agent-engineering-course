# Tier 1 — Build a research agent

**Status:** runnable learner exercise; available only after Tier 0 is submitted. **Time:** plan roughly 1–2 hours, then extra time for debugging. Your Tier 0 preflight proves local resources work; it does not solve this challenge.

## What you will learn
- Separate a model from tools, memory/state, and routing decisions.
- Make a report agent search first, plan an outline, write sections, and track exact source provenance.
- Treat retrieved text as untrusted evidence, not as an instruction to follow.
- Abstain when the source tool returns nothing instead of inventing citations.

## Build contract (your code, not ours)
Create `work/tier-1/report_agent.py` with a function:

```python
def build_report(topic: str, search, model) -> dict:
    ...
```

`search(query)` returns a list of `{"title": str, "url": str, "snippet": str}` records. `model(prompt)` returns plain text. Both are injected by the checker; do not require an API key or import a hosted SDK. Your result must be a dict with:

- `status`: `"ok"` when it uses sources, or `"insufficient_sources"` when it cannot.
- `outline`: list of nonempty headings.
- `sections`: list of `{"heading": str, "text": str, "source_urls": [str, ...]}`. Every heading must appear in the outline and every sourced section needs observed URLs.
- `sources`: list of `{"title": str, "url": str}`. URLs must come from records actually returned by `search`.

When search returns no records, use `status="insufficient_sources"` with empty `sections` and `sources`. Do not fabricate sources or silently substitute model memory. The checker runs your function against one sourced fixture and one empty-search fixture in a credential-free child process. Its deterministic fixtures are **tests of the interface**, not live research. It has a 15-second timeout. This is not a security sandbox for hostile code.

## Your sequence
1. In your own words, write a small flow sketch for search → outline → sections → provenance. Identify which steps require the model and which can be deterministic.
2. Implement the function in your own file. Keep source URLs as data from `search`; never ask the model to invent URLs.
3. Run `python -m agent_course check --tier 1` after Tier 0 unlocks. Inspect failed checks and revise your code. The checker does not write a completion record.
4. Run your agent once with your own adapters to **local Ollama** (`qwen3:4b-instruct`) and a public no-key search from `agent_course.sources`, or choose an explicitly labeled local-corpus run. A public search sends its query to a public site; use a non-sensitive practice topic. Do not call a hosted endpoint or reuse keys from the reference workshop.
5. Write `work/tier-1/notes.md` with nonempty headings `# Live run`, `# Failure analysis`, and `# Reflection`. Describe observed outputs, source URLs or `course://` IDs, and one failure you corrected. Write your own analysis, not an assistant's answer.
6. After reviewing both test results and your notes, submit your own work: `python -m agent_course submit --tier 1 --evidence work/tier-1/notes.md --attest`. Tier 2 remains locked if any check fails.

## Hints (open progressively)
- **Hint 1:** Count how many times your function asks `search` and `model` for help. Is the information used in the returned report?
- **Hint 2:** Compare every cited URL to the set of URLs from `search`. A URL that merely *looks plausible* is not evidence.
- **Hint 3:** Simulate an empty result list before drafting prose. Can your function return without constructing a confident report?

## Promotion rubric
The automatic gate checks observed search/model use, a nonempty sourced outline and section, exact source-URL provenance, and no-source abstention. Your notes must contain the three headings above. You must personally judge clarity, relevance, factual accuracy, and whether your live run really used the source route you described; a structural fixture test cannot guarantee these.

**Next:** Tier 2 introduces retrieval from a local knowledge base, but its lab/validator is a later milestone. The roadmap is visible; promotion to Tier 2 will fail closed until that lab exists.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
