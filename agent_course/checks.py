"""Fail-closed validators for the active local course tier."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

from .sources import source_route


OLLAMA_BASE = "http://127.0.0.1:11434"


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    mode: str
    issues: tuple[str, ...]


def _post_json(url: str, payload: dict) -> dict:
    request = Request(url, data=json.dumps(payload).encode("utf-8"),
                      headers={"Content-Type": "application/json"}, method="POST")
    with build_opener(ProxyHandler({})).open(request, timeout=20) as response:
        return json.load(response)


def check_tool_response(response: dict) -> bool:
    try:
        calls = response.get("message", {}).get("tool_calls", [])
        return any(item.get("function", {}).get("name") == "lookup_note" for item in calls)
    except (AttributeError, TypeError):
        return False


def check_embedding_response(response: dict) -> bool:
    try:
        vector = response["embeddings"][0]
        return bool(vector) and all(type(value) in (float, int) and math.isfinite(value) for value in vector)
    except (KeyError, IndexError, TypeError, ValueError):
        return False


def check_tier_zero(root: Path, *, post=None, search=None) -> CheckResult:
    """Verify local tool calling + local embeddings + a labeled source route."""
    post = post or _post_json
    search = search or source_route
    chat_payload = {
        "model": "qwen3:4b-instruct", "stream": False,
        "messages": [{"role": "user", "content": "Use lookup_note to find an agent foundations note; do not answer directly."}],
        "tools": [{"type": "function", "function": {"name": "lookup_note", "description": "Find a named note",
                  "parameters": {"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"]}}}],
        "options": {"temperature": 0, "num_predict": 96},
    }
    try:
        chat = post(OLLAMA_BASE + "/api/chat", chat_payload)
    except (OSError, ValueError, TypeError) as exc:
        return CheckResult(False, "", (f"Local Ollama chat unavailable: {type(exc).__name__}",))
    if not check_tool_response(chat):
        return CheckResult(False, "", ("Local Ollama model did not make a tool call to lookup_note",))
    try:
        embedding = post(OLLAMA_BASE + "/api/embed", {
            "model": "nomic-embed-text:latest", "input": "agent model tools memory routing",
        })
    except (OSError, ValueError, TypeError) as exc:
        return CheckResult(False, "", (f"Local Ollama embedding unavailable: {type(exc).__name__}",))
    if not check_embedding_response(embedding):
        return CheckResult(False, "", ("Local embedding response was empty or invalid",))
    try:
        mode, sources = search("AI agent model tools memory routing")
    except (OSError, ValueError, TypeError) as exc:
        return CheckResult(False, "", (f"Source route unavailable: {type(exc).__name__}",))
    if mode not in ("online", "offline") or not isinstance(sources, list) or not sources:
        return CheckResult(False, "", ("No usable public or bundled source route",))
    return CheckResult(True, mode, ())


def notes_ok(tier: int, path: Path) -> tuple[bool, str]:
    if tier != 0:
        return False, f"Tier {tier} evidence validator unavailable"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False, "Cannot read Tier 0 notes"
    headings = list(re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*$", text))
    sections = {}
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections[match.group(1).strip().casefold()] = text[match.end():end].strip()
    for title in ("Concepts", "Local observations", "Source route", "Limits"):
        if not sections.get(title.casefold()):
            return False, f"Missing or empty {title} section"
    return True, ""


def run_check(tier: int, root: Path) -> CheckResult:
    if tier == 0:
        return check_tier_zero(root)
    return CheckResult(False, "", (f"Tier {tier} validator unavailable",))
