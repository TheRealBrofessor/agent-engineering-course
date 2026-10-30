# Agent Engineering Course

Professor's **original, sequential agent-building course**. Each learner supplies their own model provider and model names. Zero API keys are required when using Ollama; hosted providers use the learner's own credentials. The separate NVIDIA workshop clone is background reference only; this project neither imports it nor reads its saved credentials.

## Progression

Only the active tier can be checked or submitted; later tiers remain **locked**. The path runs from **Tier 0** through **Tier 7** in order. Completing one tier with a validator, learner-created evidence, and explicit attestation unlocks the next; you cannot skip or replay a tier. The ledger is a local learning workflow, not an anti-tamper/security system. A passing automated gate checks mechanics, not conceptual mastery—review your own work.

| Tier | Focus | Release status |
|---|---|---|
| 0 | Local foundations: model, tools, memory, routing | Runnable preflight and notes gate |
| 1 | Build a sourced research agent | Runnable learner lab and fixture grader |
| 2 | Agentic RAG | Roadmap only; validator unavailable |
| 3 | Evaluation | Roadmap only; validator unavailable |
| 4 | Customization | Roadmap only; validator unavailable |
| 5 | Deep agents | Roadmap only; validator unavailable |
| 6 | Safety | Roadmap only; validator unavailable |
| 7 | Harnesses and skills | Roadmap only; validator unavailable |

**Roadmap only means promotion fails closed**, even if you write a file for that tier. Future labs are separate builds, not falsely marked done.

## Start (Tier 0)

Prerequisites: Python 3.12+ and a chat model with tool calling plus an embedding model exposed by your chosen provider. The preflight checks a real tool call and embedding. Search tries anonymous public websites, then a clearly marked bundled offline note if the websites fail. Public search sends a **static, non-sensitive course topic**, never your private notes. Credentials are supplied through environment variables; the course never reads `.env` files.

Configure the models before checking Tier 0. `openrouter` and `openai-compatible` use OpenAI-style APIs; Anthropic and Gemini use their native request formats. Chat and embeddings may use different providers:

```bash
export AGENT_COURSE_CHAT_PROVIDER=openrouter
export AGENT_COURSE_CHAT_MODEL=your-provider/model-id
export AGENT_COURSE_EMBED_PROVIDER=openai-compatible
export AGENT_COURSE_EMBED_MODEL=your-embedding-model
export AGENT_COURSE_API_KEY=your-key
```

Supported providers are `ollama`, `openai`, `openai-compatible`, `openrouter`, `anthropic`, and `gemini`/`google`. Use `AGENT_COURSE_CHAT_BASE_URL`, `AGENT_COURSE_EMBED_BASE_URL`, or `AGENT_COURSE_BASE_URL` for compatible gateways and self-hosted endpoints. Ollama requires no key; hosted providers generally do.

From this folder:

```bash
python -m unittest discover -s tests -v
python -m agent_course status
python -m agent_course check --tier 0
```

Read `curriculum/tier-0.md`. Write your own `work/tier-0/notes.md` with the required headings; `work/` and `.course/` are private gitignored learner state. Then, **only after you verify your answers**:

```bash
python -m agent_course submit --tier 0 --evidence work/tier-0/notes.md --attest
python -m agent_course status
```

Tier 1 unlocks only when that submit passes. Read its lesson when active. `check` never records completion; `submit` reruns validation before it writes a mode-0600 ledger with evidence hash. If a provider is unavailable, verify its endpoint, model IDs, and environment configuration. Offline source fallback does not replace the model requirement.

## Safety and limits

The Tier 1 grader executes **your own** Python file in a short-lived child with a timeout and minimal environment; it is not a hard sandbox against intentionally hostile code. Do not run an untrusted downloaded exercise as your learner file. Public search is best-effort and may fail or be rate limited; the course labels the offline path honestly. The model can still hallucinate; automatic structural checks do not verify every factual sentence. No Tier 2–7 lab completion is claimed.

Implementation evidence and a new-session prompt live in `PROGRESS.md` and `HANDOFF.md`. The [design](docs/superpowers/specs/2026-10-25-keyless-tiered-course-design.md) and [plan](docs/superpowers/plans/2026-10-25-keyless-tiered-course.md) explain the current scope.

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
