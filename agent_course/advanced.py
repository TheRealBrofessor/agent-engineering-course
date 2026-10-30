"""Deterministic, provider-neutral fixture contracts for Tiers 2 through 7.

The learner owns the files under ``work/``.  These checks execute them in a
short-lived child with an allowlisted environment; they never load credentials
or run while displaying status.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from .checks import CheckResult


def _child_env(root: Path) -> dict[str, str]:
    return {"PATH": os.defpath, "HOME": str(root), "PYTHONDONTWRITEBYTECODE": "1", "LC_ALL": "C.UTF-8"}


def _run(root: Path, tier: int, timeout: float = 10) -> tuple[dict[str, Any] | None, str | None]:
    artifact = root / "work" / f"tier-{tier}" / {
        2: "rag_agent.py", 3: "evaluate.py", 4: "customize.py",
        5: "deep_agent.py", 6: "policy.py", 7: "harness.py",
    }[tier]
    if not artifact.is_file() or not artifact.resolve().is_relative_to((root / "work" / f"tier-{tier}").resolve()):
        return None, f"Create work/tier-{tier}/{artifact.name} before checking Tier {tier}; validator unavailable until the learner artifact exists"
    runner = Path(__file__).with_name("advanced_runner.py")
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(runner), str(tier), str(artifact)],
            cwd=root, env=_child_env(root), capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None, f"Tier {tier} learner run hit the timeout"
    except OSError as exc:
        return None, f"Could not launch Tier {tier} runner: {type(exc).__name__}"
    try:
        payload = json.loads(proc.stdout)
    except (json.JSONDecodeError, TypeError):
        return None, f"Tier {tier} runner returned invalid JSON"
    if proc.returncode:
        return None, f"Tier {tier} learner run failed ({payload.get('error', 'unknown error')})"
    if not isinstance(payload, dict):
        return None, f"Tier {tier} runner returned malformed payload"
    return payload, None


def check_tier_two(root: Path) -> CheckResult:
    payload, error = _run(root, 2)
    if error:
        return CheckResult(False, "", (error,))
    if payload.get("retrieval_decisions") != ["retrieve", "skip", "retrieve"]:
        return CheckResult(False, "", ("Tier 2 must retrieve, skip, then retrieve for the fixture queries",))
    if payload.get("grounded") is not True:
        return CheckResult(False, "", ("Tier 2 answer contains an unknown or fabricated source ID",))
    if payload.get("no_answer") is not True:
        return CheckResult(False, "", ("Tier 2 must abstain when no fixture passage supports the answer",))
    return CheckResult(True, "fixture", ())


def check_tier_three(root: Path) -> CheckResult:
    payload, error = _run(root, 3)
    if error:
        return CheckResult(False, "", (error,))
    if payload.get("deterministic") is not True:
        return CheckResult(False, "", ("Tier 3 metrics must be deterministic across repeated runs",))
    metrics = payload.get("metrics")
    if not isinstance(metrics, dict) or not {"citation_coverage", "answer_support", "abstention_rate"} <= set(metrics):
        return CheckResult(False, "", ("Tier 3 must report citation coverage, answer support, and abstention rate",))
    if len(payload.get("failures", [])) < 2:
        return CheckResult(False, "", ("Tier 3 must retain at least two measured held-out failures",))
    if not isinstance(payload.get("comparison"), dict) or not {"baseline", "customized"} <= set(payload["comparison"]):
        return CheckResult(False, "", ("Tier 3 must include a baseline/customized comparison",))
    return CheckResult(True, "fixture", ())


def check_tier_four(root: Path) -> CheckResult:
    payload, error = _run(root, 4)
    if error:
        return CheckResult(False, "", (error,))
    if not payload.get("baseline") or not payload.get("customized"):
        return CheckResult(False, "", ("Tier 4 must expose baseline and customized results",))
    if payload.get("approval") != {"safe": True, "dangerous": False}:
        return CheckResult(False, "", ("Tier 4 command approval must allow read-only and deny state-changing commands",))
    if payload.get("customized_score", 0) <= payload.get("baseline_score", 0):
        return CheckResult(False, "", ("Tier 4 customization must improve the fixture score or document a measurable result",))
    return CheckResult(True, "fixture", ())


def check_tier_five(root: Path) -> CheckResult:
    payload, error = _run(root, 5)
    if error:
        return CheckResult(False, "", (error,))
    trace = payload.get("trace", [])
    if not isinstance(trace, list) or not {"plan", "delegate", "memory_write"} <= {x.get("event") for x in trace if isinstance(x, dict)}:
        return CheckResult(False, "", ("Tier 5 trace must show a plan, delegation, and file-backed memory",))
    if payload.get("within_budget") is not True or payload.get("memory_exists") is not True or payload.get("denied") is not True:
        return CheckResult(False, "", ("Tier 5 must enforce budgets and deny the sandbox action",))
    return CheckResult(True, "fixture", ())


def check_tier_six(root: Path) -> CheckResult:
    payload, error = _run(root, 6)
    if error:
        return CheckResult(False, "", (error,))
    if payload.get("positive") is not True or payload.get("negative") is not True:
        return CheckResult(False, "", ("Tier 6 requires both an allowed and a denied policy test",))
    if payload.get("injection_blocked") is not True:
        return CheckResult(False, "", ("Tier 6 prompt-injection regression was not blocked",))
    return CheckResult(True, "fixture", ())


def check_tier_seven(root: Path) -> CheckResult:
    payload, error = _run(root, 7)
    if error:
        return CheckResult(False, "", (error,))
    if payload.get("tool_count") != 4 or payload.get("bounded") is not True:
        return CheckResult(False, "", ("Tier 7 must provide exactly four bounded tools",))
    if payload.get("lazy_tokens", 0) >= payload.get("eager_tokens", 0):
        return CheckResult(False, "", ("Tier 7 must measure lower eager-vs-lazy context cost",))
    if payload.get("portable") is not True:
        return CheckResult(False, "", ("Tier 7 skill must run under both fixture harnesses",))
    return CheckResult(True, "fixture", ())
