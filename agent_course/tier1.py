"""Fixture-based, learner-owned Tier 1 assessment (no answer implementation)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from .checks import CheckResult


def validate_report(report: object, search_results: object, search_calls: object,
                    model_calls: object) -> tuple[bool, tuple[str, ...]]:
    """Check observed tool use, bounded provenance, and safe abstention."""
    if type(search_calls) is not int or search_calls < 1:
        return False, ("missing search call",)
    if not isinstance(report, dict):
        return False, ("report must be an object",)
    if not isinstance(search_results, list):
        return False, ("search results must be a list",)
    sources = report.get("sources")
    sections = report.get("sections")
    outline = report.get("outline")
    if not isinstance(sources, list) or not isinstance(sections, list) or not isinstance(outline, list):
        return False, ("report needs outline, sections and sources lists",)
    if not search_results:
        safe = report.get("status") == "insufficient_sources" and not sources and not sections
        return (True, ()) if safe else (False, ("no-source report must abstain without citations or sections",))
    if type(model_calls) is not int or model_calls < 1:
        return False, ("missing model call",)
    if report.get("status") != "ok":
        return False, ("sourced report status must be ok",)
    if not outline or any(not isinstance(item, str) or not item.strip() for item in outline):
        return False, ("outline requires headings",)
    if not sections or not sources:
        return False, ("sourced report needs sections and sources",)
    allowed = {item.get("url") for item in search_results if isinstance(item, dict) and isinstance(item.get("url"), str)}
    declared: set[str] = set()
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("title"), str) or not source["title"].strip():
            return False, ("invalid declared source",)
        url = source.get("url")
        if not isinstance(url, str) or url not in allowed:
            return False, ("unverified declared source URL",)
        declared.add(url)
    cited: set[str] = set()
    for section in sections:
        if not isinstance(section, dict) or section.get("heading") not in outline:
            return False, ("section heading must match outline",)
        if not isinstance(section.get("text"), str) or not section["text"].strip():
            return False, ("section text is empty",)
        urls = section.get("source_urls")
        if not isinstance(urls, list) or not urls or any(not isinstance(url, str) for url in urls):
            return False, ("section has no source URLs",)
        cited.update(urls)
    if not cited <= allowed or not cited <= declared:
        return False, ("unverified source URL in section",)
    return True, ()


def safe_child_env(root: Path) -> dict[str, str]:
    """Pass an allowlist, never the parent's credential-bearing environment."""
    return {"PATH": os.defpath, "HOME": str(root), "PYTHONDONTWRITEBYTECODE": "1", "LC_ALL": "C.UTF-8"}


def check_tier_one(root: Path, *, timeout: float = 15) -> CheckResult:
    root = root.resolve()
    student_dir = root / "work" / "tier-1"
    student_path = student_dir / "report_agent.py"
    if not student_path.is_file() or not student_path.resolve().is_relative_to(student_dir.resolve()):
        return CheckResult(False, "", ("Create work/tier-1/report_agent.py before checking Tier 1",))
    runner = Path(__file__).with_name("tier1_runner.py")
    try:
        process = subprocess.run(
            [sys.executable, "-I", "-B", str(runner), str(student_path)],
            cwd=root, env=safe_child_env(root), capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return CheckResult(False, "", ("Tier 1 learner run hit the timeout",))
    except OSError as exc:
        return CheckResult(False, "", (f"Could not launch Tier 1 runner: {type(exc).__name__}",))
    try:
        payload = json.loads(process.stdout)
    except (json.JSONDecodeError, TypeError):
        return CheckResult(False, "", ("Tier 1 runner returned invalid JSON",))
    if not isinstance(payload, dict):
        return CheckResult(False, "", ("Tier 1 runner returned malformed payload",))
    if process.returncode != 0:
        return CheckResult(False, "", (f"Tier 1 learner run failed ({payload.get('error', 'unknown error')})",))
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 2:
        return CheckResult(False, "", ("Tier 1 runner returned incomplete scenarios",))
    for label, scenario in zip(("sourced", "empty-search"), scenarios):
        if not isinstance(scenario, dict):
            return CheckResult(False, "", (f"Tier 1 {label} scenario malformed",))
        passed, issues = validate_report(scenario.get("report"), scenario.get("search_results"),
                                         scenario.get("search_calls"), scenario.get("model_calls"))
        if not passed:
            return CheckResult(False, "", tuple(f"{label}: {issue}" for issue in issues))
    return CheckResult(True, "fixture", ())
