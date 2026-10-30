"""Fail-closed validators for the active local course tier."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

from .sources import source_route
from .models import ModelConfig, ModelConfigError


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    mode: str
    issues: tuple[str, ...]


def _post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
    request = Request(url, data=json.dumps(payload).encode("utf-8"),
                      headers={"Content-Type": "application/json", **(headers or {})}, method="POST")
    with build_opener(ProxyHandler({})).open(request, timeout=20) as response:
        return json.load(response)


def _call_post(post, url: str, payload: dict, headers: dict) -> dict:
    if post is _post_json:
        return post(url, payload, headers)
    try:
        return post(url, payload, headers)
    except TypeError:
        return post(url, payload)


def check_tool_response(response: dict) -> bool:
    try:
        ollama_calls = response.get("message", {}).get("tool_calls", [])
        openai_calls = response.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])
        anthropic_calls = response.get("content", [])
        gemini_calls = response.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        return (
            any(item.get("function", {}).get("name") == "lookup_note" for item in ollama_calls)
            or any(item.get("function", {}).get("name") == "lookup_note" for item in openai_calls)
            or any(item.get("type") == "tool_use" and item.get("name") == "lookup_note" for item in anthropic_calls)
            or any(item.get("functionCall", {}).get("name") == "lookup_note" for item in gemini_calls)
        )
    except (AttributeError, TypeError):
        return False


def check_embedding_response(response: dict) -> bool:
    try:
        vector = response.get("embeddings", [None])[0]
        if vector is None:
            vector = response.get("data", [{}])[0].get("embedding")
        if vector is None:
            vector = response.get("embedding", {}).get("values")
        return bool(vector) and all(type(value) in (float, int) and math.isfinite(value) for value in vector)
    except (KeyError, IndexError, TypeError, ValueError):
        return False


def check_tier_zero(root: Path, *, post=None, search=None) -> CheckResult:
    """Verify local tool calling + local embeddings + a labeled source route."""
    post = post or _post_json
    search = search or source_route
    try:
        config = ModelConfig.from_env()
        chat_url, chat_payload, chat_headers = config.chat_request()
        embed_url, embed_payload, embed_headers = config.embed_request()
    except ModelConfigError as exc:
        return CheckResult(False, "", (f"Model configuration unavailable: {exc}",))
    try:
        chat = _call_post(post, chat_url, chat_payload, chat_headers)
    except (OSError, ValueError, TypeError) as exc:
        provider_name = "Ollama" if config.chat_provider == "ollama" else config.chat_provider
        return CheckResult(False, "", (f"{provider_name} chat unavailable: {type(exc).__name__}",))
    if not check_tool_response(chat):
        return CheckResult(False, "", ("Local Ollama model did not make a tool call to lookup_note",))
    try:
        embedding = _call_post(post, embed_url, embed_payload, embed_headers)
    except (OSError, ValueError, TypeError) as exc:
        provider_name = "Ollama" if config.embed_provider == "ollama" else config.embed_provider
        return CheckResult(False, "", (f"{provider_name} embedding unavailable: {type(exc).__name__}",))
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
    required = {
        0: ("Concepts", "Local observations", "Source route", "Limits"),
        1: ("Live run", "Failure analysis", "Reflection"),
    }.get(tier)
    if required is None:
        return False, f"Tier {tier} evidence validator unavailable"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False, f"Cannot read Tier {tier} notes"
    headings = list(re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*$", text))
    sections = {}
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections[match.group(1).strip().casefold()] = text[match.end():end].strip()
    for title in required:
        if not sections.get(title.casefold()):
            return False, f"Missing or empty {title} section"
    return True, ""


def run_check(tier: int, root: Path) -> CheckResult:
    if tier == 0:
        return check_tier_zero(root)
    if tier == 1:
        from .tier1 import check_tier_one
        return check_tier_one(root)
    return CheckResult(False, "", (f"Tier {tier} validator unavailable",))
