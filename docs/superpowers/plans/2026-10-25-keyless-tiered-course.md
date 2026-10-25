# Keyless Tiered Agent Course Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Professor's original, no-API-key agent course with sequential promotion gates, live local Tier 0 checks, a Tier 1 learner lab/validator, and an honest Tier 0–7 roadmap.

**Architecture:** A small Python stdlib CLI reads an immutable curriculum catalog and a local JSON completion ledger. Each `submit` reruns the active tier's check and validates learner evidence before atomically recording completion; future tiers reject promotion until their validators exist. Ollama and optional public search are accessed directly with finite timeouts, with an explicitly labeled offline corpus fallback.

**Tech Stack:** Python 3.12+ stdlib (`argparse`, `unittest`, `urllib.request`, `html.parser`, `subprocess`), local Ollama at 127.0.0.1:11434, no API keys.

**Spec:** `docs/superpowers/specs/2026-10-25-keyless-tiered-course-design.md`

## Global Constraints
- Start implementation on a new `feat/keyless-course-engine` branch, not `main`; the spec and plan remain committed on `main`.
- Project root: `/home/professor/agent-engineering-course`; the NVIDIA reference clone is never a dependency or edit target.
- No API keys, `.env` reads, fake key strings, or hosted-model fallback; model calls stay on loopback.
- Tier 0 is available initially; Tier 1 requires Tier 0 completion; Tier 2–7 validators are unavailable and fail closed.
- Learner writes all exercise answers, code, and reflective evidence; never insert a passing example solution into the learner's work directory.
- `status` never runs learner code, writes state, or contacts network. `check`/`submit` only act on the active tier.
- Default state `.course/state.json` is gitignored, atomic, mode 0600, and rejects malformed/gapped progress.
- Timeouts and source-route labels are explicit; no network or Ollama error can promote a tier unless the documented offline route applies to search only.
- Before any completion claim, run full unit tests and a real Tier 0 preflight with credential variables scrubbed, then show active Tier 0 still uncompleted.

---

### Task 1: Catalog and durable sequential state

**Files:** Create `agent_course/__init__.py`, `agent_course/catalog.py`, `agent_course/state.py`, `tests/test_state.py`, `.gitignore`.

**Interfaces:** `catalog.TIERS` is an ordered tuple of eight title dicts. `state.read_state(path: Path) -> list[dict]`; `state.record_completion(path: Path, tier: int, evidence_path: Path, mode: str) -> list[dict]`; `state.CourseStateError` is a user-facing error. No network dependencies.

- [ ] **Step 1: RED test first.** Test a missing state file returns `[]`, tier 1 cannot complete first, tier 0 evidence is hashed and persisted mode-0600, repeat tier 0 fails, and manually written `[0,2]` state raises `CourseStateError`.

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from agent_course.state import CourseStateError, read_state, record_completion

def test_no_skip():
    with TemporaryDirectory() as d:
        path = Path(d)/'state.json'
        note = Path(d)/'notes.md'; note.write_text('my own observations')
        try: record_completion(path, 1, note, 'offline')
        except CourseStateError: pass
        else: raise AssertionError('skipped tier must fail')
        assert read_state(path) == []
```

- [ ] **Step 2: Run `python -m unittest discover -s tests -p 'test_state.py' -v`; verify RED is a missing import/function, not a test typo.**
- [ ] **Step 3: Implement the minimal catalog/state functions.** Validate schema `{ "schema_version": 1, "completed": [...] }`, contiguous IDs `0..len-1`, nonempty evidence file, and active tier equality; write JSON to a sibling tempfile with `os.open(..., 0o600)` + `os.replace`, and sha256 over evidence bytes. Ignore `.course/`, `work/`, `__pycache__/`, `.venv/` in `.gitignore`.

```python
def record_completion(path, tier, evidence_path, mode):
    records = read_state(path)
    if tier != len(records):
        raise CourseStateError(f'active tier is {len(records)}')
    data = evidence_path.read_bytes()
    if not data.strip():
        raise CourseStateError('evidence is empty')
    record = {'tier': tier, 'sha256': hashlib.sha256(data).hexdigest(),
              'mode': mode, 'checked_at': datetime.now(timezone.utc).isoformat()}
    records.append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix='.state-', suffix='.json')
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump({'schema_version': 1, 'completed': records}, f)
            f.flush(); os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp): os.unlink(temp)
    return records
```

- [ ] **Step 4: Run the same unittest target; require GREEN.**
- [ ] **Step 5: Commit `feat: add ordered course state` after a fresh test run.**

### Task 2: CLI status and guarded transitions

**Files:** Create `agent_course/cli.py`, `agent_course/__main__.py`, `agent_course/checks.py` (initial fail-closed checker boundary), `tests/test_cli.py`; use Task 1 interfaces.

**Interfaces:** `cli.main(argv: list[str] | None = None) -> int`; CLI has `--root PATH` for isolated tests and subcommands `status`, `check --tier N`, `submit --tier N --evidence PATH --attest`. `checks.run_check(tier: int, root: Path) -> CheckResult` initially returns `validator unavailable` for every tier so Task 2 is independently testable; Task 3 implements Tier 0, Task 4 implements Tier 1. Tests patch this boundary only.

- [ ] **Step 1: RED tests.** `status` on empty root says Tier 0 active and Tier 1 locked; `check --tier 2` rejects before calling checker; `submit` without `--attest` rejects; a failed checker leaves state absent; successful Tier 0 checker with valid notes records Tier 0 and reveals Tier 1; replay rejects.

```python
def test_locked_tier_check_does_not_execute_checker(self):
    with patch('agent_course.cli.run_check') as check:
        rc = main(['--root', str(self.root), 'check', '--tier', '2'])
    self.assertNotEqual(rc, 0)
    check.assert_not_called()
```

- [ ] **Step 2: Run `python -m unittest discover -s tests -p 'test_cli.py' -v`; verify expected RED.**
- [ ] **Step 3: Implement parse/dispatch and a fail-closed checker boundary.** Compute active tier as `len(read_state(...))`, reject nonactive tiers before network/learner imports; validate evidence path stays inside `root/work/tier-N/` and is a regular file; require `--attest`; call `run_check`; on success call `record_completion`. Print failures without writing progress. `status` only reads state/catalog. Until Task 3, `checks.run_check` returns `CheckResult(False, '', ('validator unavailable',))` for all tiers.

```python
def require_active(requested: int, records: list[dict]) -> None:
    active = len(records)
    if requested != active:
        raise CourseStateError(f'Locked: active tier is {active}')
```

- [ ] **Step 4: Run state and CLI test files; require GREEN.**
- [ ] **Step 5: Commit `feat: gate CLI transitions`.**

### Task 3: Keyless local Tier 0 preflight and source routes

**Files:** Create `agent_course/checks.py`, `agent_course/sources.py`, `agent_course/corpus/agent-basics.md`, `tests/test_checks.py`, `tests/test_sources.py`.

**Interfaces:** `checks.CheckResult(ok: bool, mode: str, issues: tuple[str, ...])`; `checks.run_check(tier: int, root: Path) -> CheckResult`; `sources.source_route(query: str) -> tuple[str, list[dict]]` returns `online` or `offline` with title/url/snippet. `checks.notes_ok(tier, path) -> tuple[bool,str]` validates required learner headings.

- [ ] **Step 1: RED tests.** A local fake HTTP responder returns an Ollama `message.tool_calls` response and nonempty embeddings; a missing `tool_calls` or embeddings fails. Search HTML fixture exposes two `result__a` links and URL/title/summaries; both web routes failing yields `offline` only when bundled corpus is nonempty. Notes missing any of the four headings fail; populated headings pass. Tier 2 returns `validator unavailable`.

```python
def test_model_response_must_really_call_tool(self):
    result = check_tool_response({'message': {'content': 'I can call it'}})
    self.assertFalse(result)

def test_tier_two_fails_closed(self):
    self.assertIn('unavailable', ' '.join(run_check(2, self.root).issues))
```

- [ ] **Step 2: Run `python -m unittest discover -s tests -p 'test_checks.py' -v` and `test_sources.py`; verify RED.**
- [ ] **Step 3: Implement minimal urllib JSON requests to `http://127.0.0.1:11434/api/chat` and `/api/embed`, check actual tool name and positive embedding length, timeouts <= 20 s per call.** Search only a static public topic during preflight; parse DDG result anchors, then Wikimedia JSON if DDG has no usable results, then a named `course://corpus/agent-basics` source. Scrub redirect wrappers, cap result counts, never send private prompts in preflight. Distinguish `online` and `offline` in result. Validate Tier 0 notes headings (`Concepts`, `Local observations`, `Source route`, `Limits`) with nonempty text.

```python
@dataclass(frozen=True)
class CheckResult:
    ok: bool
    mode: str
    issues: tuple[str, ...]

def run_check(tier, root):
    if tier == 0:
        return check_tier_zero(root)
    return CheckResult(False, '', ('validator unavailable',))
```

- [ ] **Step 4: Run all tests; require GREEN.**
- [ ] **Step 5: Commit `feat: verify local keyless foundations`.**

### Task 4: Tier 1 learner contract and deterministic validator

**Files:** Create `agent_course/tier1.py`, `agent_course/tier1_runner.py`, `tests/test_tier1.py`, `curriculum/tier-1.md`.

**Interfaces:** `tier1.validate_report(report: dict, search_results: list[dict], search_calls: int, model_calls: int) -> tuple[bool, tuple[str,...]]`; `tier1.check_tier_one(root: Path) -> CheckResult`; `work/tier-1/report_agent.py` is learner-created and defines `build_report(topic, search, model)` according to spec. Runner is a child process with short timeout and a minimal, keyless environment.

- [ ] **Step 1: RED tests.** Construct in-memory response data (not a full solution) to prove the validator rejects non-source URLs, missing model/search use, and fabricated citations on empty search; structurally sourced response passes `validate_report`. A missing learner script fails `check_tier_one` without executing anything. A subprocess timeout returns a failed gate and no state write.

```python
def test_fabricated_url_rejected(self):
    report = {'status':'ok','outline':['Intro'], 'sections':[{'heading':'Intro','text':'Claim','source_urls':['https://invented.invalid']}], 'sources':[{'title':'Invented','url':'https://invented.invalid'}]}
    passed, issues = validate_report(report, [{'url':'https://real.invalid','title':'Real','snippet':'Text'}], 1, 1)
    self.assertFalse(passed)
```

- [ ] **Step 2: Run `python -m unittest discover -s tests -p 'test_tier1.py' -v`; verify RED.**
- [ ] **Step 3: Implement a bounded subprocess runner that imports only the explicitly selected learner file, injects fake search/model callbacks, runs both a sourced fixture and an empty-search fixture, serializes each report with returned search results plus call counts to JSON, and strips credential-like environment variables.** Keep `status` import-free. Validate `status`, outline/sections, source provenance, no-source abstention, and learner notes. Add original concepts, inputs/outputs, hints in three levels, and a non-spoiler failure-analysis rubric to `curriculum/tier-1.md`.

```python
def validate_report(report, search_results, search_calls, model_calls):
    if search_calls < 1:
        return False, ('missing search call',)
    allowed = {r['url'] for r in search_results}
    cited = {url for sec in report.get('sections', []) for url in sec.get('source_urls', [])}
    if not search_results:
        safe = report.get('status') == 'insufficient_sources' and not cited and not report.get('sources')
        return (True, ()) if safe else (False, ('no-source report fabricated citations',))
    if model_calls < 1:
        return False, ('missing model call',)
    if not cited or not cited <= allowed:
        return False, ('unverified source URL',)
    return True, ()
```

- [ ] **Step 4: Run full unit suite; require GREEN.**
- [ ] **Step 5: Commit `feat: add learner-owned Tier 1 gate`.**

### Task 5: Original curriculum and precise status docs

**Files:** Create `README.md`, `curriculum/tier-0.md`, `curriculum/tier-2.md` through `curriculum/tier-7.md`, `PROGRESS.md`, `HANDOFF.md`, `tests/test_curriculum.py`. Keep Tier 1 lesson from Task 4.

**Interfaces:** catalog entries link to existing lesson files for available tiers; later tiers' files explicitly say `roadmap only / validator unavailable`. README gives exact CLI invocation, no-key requirements, course progression and limits. PROGRESS records only verified checks; HANDOFF records safe next action and how to restore global compression before handoff.

- [ ] **Step 1: RED test that all eight curriculum paths exist, Tier 0/1 are labeled runnable/learner-owned, Tier 2–7 are labeled roadmap-only, and the catalog has exact contiguous IDs.**

```python
def test_catalog_order_and_lessons_exist(self):
    self.assertEqual([t['id'] for t in TIERS], list(range(8)))
    for t in TIERS:
        self.assertTrue((ROOT/t['lesson']).is_file())
```

- [ ] **Step 2: Run `python -m unittest discover -s tests -p 'test_curriculum.py' -v`; verify RED from missing lessons.**
- [ ] **Step 3: Author concise original Tier 0–7 lessons/outcomes, explicit rubrics, readiness labels, and no-credential setup in README.** Tier 0 notes are prompts only; do not prefill work files. Tier 2 is Agentic RAG (retrieval decisions, grounded sources, no-answer); Tier 3 is Evaluation (held-out set and two measured failures); Tier 4 is Customization (baseline-vs-skill/tool comparison and command approval); Tier 5 is Deep Agents (bounded delegation and denied sandbox action); Tier 6 is Safety (policy positive/negative plus injection regression); Tier 7 is Harnesses/Skills (four bounded tools, context cost, portable skill). Tier 2–7 are roadmap-only until their graders ship; no fake PASS state.

```markdown
# Tier 2 — Agentic RAG (roadmap only)
Prerequisite: Tier 1 gate passed.
Gate target: retrieval decision, grounded source IDs, no-answer case.
Status: validator unavailable; promotion remains closed.
```

- [ ] **Step 4: Run full unit suite; require GREEN.**
- [ ] **Step 5: Commit `docs: publish original gated curriculum`.**

### Task 6: Live integration, OPSEC, and safe checkpoint

**Files:** Update `PROGRESS.md`, `HANDOFF.md` and historical reference notes only to point at the new course; do not modify reference lessons/answer keys. Add a regression test if any live check reveals a bug; follow RED→GREEN again.

- [ ] **Step 1: Run `python -m unittest discover -s tests -v`; read full output and exit code.**
- [ ] **Step 2: Run a real `python -m agent_course status`, `check --tier 1` (must deny), and `check --tier 0` from a subprocess with environment keys removed, not printed. Verify Ollama tool call, embed, and online/offline source label, and absence of `.course/state.json`.**

```python
import os, subprocess, sys
safe = {k:v for k,v in os.environ.items() if not any(s in k.upper() for s in ('KEY','TOKEN','SECRET','PASSWORD'))}
for args in (['status'], ['check','--tier','1'], ['check','--tier','0']):
    p = subprocess.run([sys.executable,'-m','agent_course',*args], env=safe, capture_output=True, text=True, timeout=75)
    print(args, p.returncode, p.stdout[:500], p.stderr[:200])
```

- [ ] **Step 3: Exercise a complete Tier 0→1 transition in a temporary root with temporary learner evidence only, then reject a Tier 2 skip and prove no real learner state changed. Do not fabricate Professor's actual answers.**
- [ ] **Step 4: Review git diff for secrets, verify `git status`, write evidence and precise limitations in PROGRESS/HANDOFF. Restore the user-approved temporary Hermes compression threshold from 0.75 to the verified prior 0.5 before a fresh-session handoff and verify with `hermes config get compression.threshold`.**
- [ ] **Step 5: Commit the verified release; report exact pass/fail status and the first learner action.**

Made with ❤️ by Kool Kat Moe D 🐾🏴‍☠️❤️🏴‍☠️
