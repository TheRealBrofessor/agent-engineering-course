# Agent Engineering Course — design

## Purpose and ownership
This is Professor's **original** agent-engineering course. The previously cloned NVIDIA workshop is topic inspiration only, not the product or a runtime dependency. No lessons, notebooks, answer keys, branded text, or saved credentials are copied into this project. Use `/home/professor/agent-engineering-course` as the new course root.

The course teaches one cumulative assistant project through ordered tiers. **Tier 0 must pass before Tier 1 unlocks; Tier n must pass before Tier n+1 unlocks.** A tier's availability is not evidence that its learner exercise has been done. The assistant builds teaching materials, validators, and infrastructure; Professor writes and interprets exercise work.

## Curriculum and promotion outcomes
| Tier | Focus | Learner artifact and gate target |
|---|---|---|
| 0 | Local, keyless foundations | Explain model/tools/memory/routing; verify local tool-calling model, local embeddings, and a working research-source route. Record observations in `work/tier-0/notes.md`. |
| 1 | Build a research agent | Implement a report agent that uses search, plans sections, records source URLs, and abstains when sourcing fails. Pass fixture-based checks and record one live run plus reflection. |
| 2 | Agentic RAG | Add retrieval decisions, local embeddings, FAISS, citations, and no-answer behavior. |
| 3 | Evaluation | Build a held-out question set, deterministic RAG metrics, local judge comparison, and failure analysis. |
| 4 | Customization | Compare prompts, tools, and portable skills first; optionally train a CPU-sized model only if feasible, never imply NVIDIA GRPO ran. |
| 5 | Deep agents | Add planning, delegation, file-backed memory, explicit budgets, and isolated execution. |
| 6 | Safety | Test access boundaries, source prompt injection, network/filesystem policy, and red-team regression cases locally. |
| 7 | Harnesses and skills | Build a small harness, measure context overhead, and demonstrate a portable skill with governance checks. |

The Tier 2–7 promotion rubrics are: Tier 2, choose retrieval only when needed and ground every answer in retrieved source IDs (including an abstention case); Tier 3, measure the Tier 2 system on a held-out set and explain at least two measured failures; Tier 4, compare a baseline with a skill/tool customization on the same tests, including a command-approval check; Tier 5, show bounded planning/delegation and a denied sandbox action; Tier 6, demonstrate a negative/positive policy test pair plus a prompt-injection regression; Tier 7, demonstrate a harness with four bounded tools, measure eager-vs-lazy context cost, and run a portable skill under two harnesses. These are published targets, **not** executable graders in the first release. Tier 2–7 labs/validators are separate follow-on builds. **Promotion fails closed for a tier without a validator.** Do not present an outline as a completed or runnable lab.

## First implementation slice
Create a standalone Python 3.12+ stdlib-first course manager with `python -m agent_course status`, `check --tier N`, and `submit --tier N --evidence PATH --attest`. The default local state is `.course/state.json` (gitignored); tests can pass a temporary state path. State stores schema version and a contiguous, ordered list of completed tiers with evidence hash and check timestamp. Loading rejects malformed, duplicate, out-of-range, or gapped state. Writes are atomic and mode 0600. `status` shows the active tier and hides locked content paths; `check` and `submit` reject any tier other than the active one. A learner attests after reading the result and writing evidence; text-presence checks and attestation are workflow safeguards, **not proof of conceptual mastery**.

Tier 0 checks local Ollama's native `POST /api/chat` tool call with `qwen3:4b-instruct` and `POST /api/embed` with `nomic-embed-text`, using finite timeouts and no key/header. A source route must exist: public unauthenticated search (DuckDuckGo HTML, then Wikimedia search) **or** a bundled local corpus for offline practice. The result explicitly labels `online` or `offline`; it never silently passes a failed public search as live research. Do not read `.env`, send private workspace contents to public sites, or require NVIDIA/Tavily/OpenAI credentials. Tier 0 notes live at `work/tier-0/notes.md` with four nonempty headings: `Concepts`, `Local observations`, `Source route`, and `Limits`. Presence checks are not a quality grade. Tier 0 submit reruns the preflight and checks the notes, then unlocks Tier 1.

Tier 1 publishes original concept notes, a report-agent exercise contract, fixture data, and deterministic validation of a learner-authored implementation at `work/tier-1/report_agent.py`. The required interface is `build_report(topic: str, search: Callable[[str], list[dict]], model: Callable[[str], str]) -> dict`. `search` results contain `title`, `url`, `snippet`; the return object contains `status` (`ok` or `insufficient_sources`), `outline` (list of headings), `sections` (list of heading/text/source_urls objects), and `sources` (list of title/url objects). The grader injects local fake adapters and checks that search and model were used, cited URLs came from actual search results, a sourced outline/section was produced, and an empty result cannot fabricate citations. A real local-model/search run is documented by the learner in `work/tier-1/notes.md` as evidence; the assistant does not fill in the exercise. Tier 1 submit requires its validator and nonempty learner notes, and otherwise leaves Tier 2 locked.

## Boundaries and error handling
The manager is a learning workflow, not a security boundary against someone editing files by hand. It never grants access to secrets, executes untrusted source URLs as code, or runs learner scripts with elevated privileges. Learner-created Python is a trusted local exercise and must not be run automatically on mere `status`; it runs only when the learner explicitly invokes `check` or `submit`. Tier 1 validator reports failure without recording completion. Any Ollama outage, model mismatch, malformed tool response, network timeout, missing notes, or unavailable validator produces a specific failed gate and no state change. The offline corpus can support practice, but cannot be described as live web research.

## Verification and handoff
Use red→green TDD for each manager behavior. Test first-run state, sequential promotion, skip/replay rejection, corrupted state, atomic persistence, offline/online labeling, negative Tier 0 preflight, and Tier 1 fixture checks without solving the learner implementation. Run the full manager test suite, then a live Tier 0 preflight with credential variables scrubbed; verify no completion is recorded on the real learner state. Document exact commands and observed output in `PROGRESS.md` plus a `HANDOFF.md` with the next action. The owner requested a fresh-session handoff near 70% context usage if measurable; any temporary global Hermes compression change approved for this run must be restored before handoff.

## Scope of this release
Deliver a working course engine, a live-tested keyless Tier 0 check, an original Tier 1 lab and its validation contract, and coherent Tier 0–7 roadmap/rubrics. Do **not** claim Tier 2–7 labs or any learner exercise completed. Later tiers are separate implementation milestones with the same strict progression gate.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
