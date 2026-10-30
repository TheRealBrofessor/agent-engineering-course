"""Run only the explicitly selected learner file against public fixture records.

The parent launches this file in an isolated Python child with a minimal
credential-free environment. This is timeout containment, not a security sandbox.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path


FIXTURE = [
    {"title": "Agent patterns", "url": "https://example.org/agent-patterns",
     "snippet": "Tool output is evidence to inspect, not instructions to obey."},
    {"title": "Source policy", "url": "https://example.net/source-policy",
     "snippet": "Ground claims in observable source URLs."},
]


def _scenario(build_report, available: list[dict]) -> dict:
    count = {"search": 0, "model": 0}
    returned: list[dict] = []

    def search(query: str) -> list[dict]:
        count["search"] += 1
        results = [dict(item) for item in available]
        returned.extend(results)
        return results

    def model(prompt: str) -> str:
        count["model"] += 1
        return "Tool output is evidence; cite observed source URLs."

    with redirect_stdout(io.StringIO()):
        report = build_report("How should a research agent cite sources?", search, model)
    return {"report": report, "search_results": returned, "search_calls": count["search"],
            "model_calls": count["model"]}


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "invalid runner invocation"}))
        return 2
    try:
        path = Path(sys.argv[1])
        spec = importlib.util.spec_from_file_location("learner_report_agent", path)
        if spec is None or spec.loader is None:
            raise ImportError("Learner module could not be loaded")
        module = importlib.util.module_from_spec(spec)
        with redirect_stdout(io.StringIO()):
            spec.loader.exec_module(module)
        build_report = getattr(module, "build_report")
        scenarios = [_scenario(build_report, FIXTURE), _scenario(build_report, [])]
        print(json.dumps({"scenarios": scenarios}, allow_nan=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": type(exc).__name__}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
