"""User-configured model provider adapters.

Credentials are read only from environment variables. This module never loads
dotenv files or persists credentials.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import quote


class ModelConfigError(ValueError):
    pass


@dataclass(frozen=True)
class ModelConfig:
    chat_provider: str
    embed_provider: str
    chat_model: str
    embed_model: str
    chat_base_url: str | None
    embed_base_url: str | None
    chat_api_key: str | None
    embed_api_key: str | None
    timeout: int = 20

    @classmethod
    def from_env(cls) -> "ModelConfig":
        provider = os.getenv("AGENT_COURSE_PROVIDER", "").strip().lower()
        chat_provider = os.getenv("AGENT_COURSE_CHAT_PROVIDER", provider).strip().lower()
        embed_provider = os.getenv("AGENT_COURSE_EMBED_PROVIDER", provider).strip().lower()
        chat_model = os.getenv("AGENT_COURSE_CHAT_MODEL", "").strip()
        embed_model = os.getenv("AGENT_COURSE_EMBED_MODEL", "").strip()
        if not chat_provider or not embed_provider:
            raise ModelConfigError("set AGENT_COURSE_PROVIDER or separate chat/embed provider variables")
        if not chat_model or not embed_model:
            raise ModelConfigError("set AGENT_COURSE_CHAT_MODEL and AGENT_COURSE_EMBED_MODEL")
        supported = {"ollama", "openai", "openai-compatible", "openrouter", "anthropic", "gemini", "google"}
        unknown = {value for value in (chat_provider, embed_provider) if value not in supported}
        if unknown:
            raise ModelConfigError(f"unsupported model provider: {sorted(unknown)[0]}")
        return cls(
            chat_provider=chat_provider,
            embed_provider=embed_provider,
            chat_model=chat_model,
            embed_model=embed_model,
            chat_base_url=os.getenv("AGENT_COURSE_CHAT_BASE_URL") or os.getenv("AGENT_COURSE_BASE_URL"),
            embed_base_url=os.getenv("AGENT_COURSE_EMBED_BASE_URL") or os.getenv("AGENT_COURSE_BASE_URL"),
            chat_api_key=os.getenv("AGENT_COURSE_CHAT_API_KEY") or os.getenv("AGENT_COURSE_API_KEY") or None,
            embed_api_key=os.getenv("AGENT_COURSE_EMBED_API_KEY") or os.getenv("AGENT_COURSE_API_KEY") or None,
        )

    def _base(self, provider: str, explicit: str | None) -> str:
        if explicit:
            return explicit.rstrip("/")
        defaults = {
            "ollama": "http://127.0.0.1:11434",
            "openai": "https://api.openai.com/v1",
            "openai-compatible": "http://127.0.0.1:8000/v1",
            "openrouter": "https://openrouter.ai/api/v1",
            "anthropic": "https://api.anthropic.com",
            "gemini": "https://generativelanguage.googleapis.com/v1beta",
            "google": "https://generativelanguage.googleapis.com/v1beta",
        }
        return defaults[provider]

    def chat_request(self) -> tuple[str, dict, dict]:
        provider = self.chat_provider
        base = self._base(provider, self.chat_base_url)
        tool = {"name": "lookup_note", "description": "Find a named note",
                "parameters": {"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"]}}
        if provider == "ollama":
            return f"{base}/api/chat", {
                "model": self.chat_model, "stream": False,
                "messages": [{"role": "user", "content": "Use lookup_note to find an agent foundations note; do not answer directly."}],
                "tools": [{"type": "function", "function": tool}],
                "options": {"temperature": 0, "num_predict": 96},
            }, {}
        if provider in {"openai", "openai-compatible", "openrouter"}:
            return f"{base}/chat/completions", {
                "model": self.chat_model, "temperature": 0, "max_tokens": 96,
                "messages": [{"role": "user", "content": "Use lookup_note to find an agent foundations note; do not answer directly."}],
                "tools": [{"type": "function", "function": tool}], "tool_choice": "required",
            }, self._bearer(self.chat_api_key)
        if provider == "anthropic":
            anthropic_tool = {"name": tool["name"], "description": tool["description"], "input_schema": tool["parameters"]}
            return f"{base}/v1/messages", {
                "model": self.chat_model, "max_tokens": 96,
                "messages": [{"role": "user", "content": "Use lookup_note to find an agent foundations note; do not answer directly."}],
                "tools": [anthropic_tool],
            }, self._anthropic_headers(self.chat_api_key)
        model = quote(self.chat_model, safe="")
        return f"{base}/models/{model}:generateContent", {
            "contents": [{"role": "user", "parts": [{"text": "Use lookup_note to find an agent foundations note; do not answer directly."}]}],
            "tools": [{"function_declarations": [tool]}],
        }, self._google_headers(self.chat_api_key)

    def embed_request(self) -> tuple[str, dict, dict]:
        provider = self.embed_provider
        base = self._base(provider, self.embed_base_url)
        if provider == "ollama":
            return f"{base}/api/embed", {"model": self.embed_model, "input": "agent model tools memory routing"}, {}
        if provider in {"openai", "openai-compatible", "openrouter"}:
            return f"{base}/embeddings", {"model": self.embed_model, "input": "agent model tools memory routing"}, self._bearer(self.embed_api_key)
        if provider in {"gemini", "google"}:
            model = quote(self.embed_model, safe="")
            return f"{base}/models/{model}:embedContent", {"content": {"parts": [{"text": "agent model tools memory routing"}]}}, self._google_headers(self.embed_api_key)
        raise ModelConfigError("Anthropic does not provide embeddings; set AGENT_COURSE_EMBED_PROVIDER")

    def _bearer(self, api_key: str | None) -> dict:
        return {"Authorization": f"Bearer {api_key}"} if api_key else {}

    def _anthropic_headers(self, api_key: str | None) -> dict:
        headers = {"anthropic-version": "2023-06-01"}
        if api_key:
            headers["x-api-key"] = api_key
        return headers

    def _google_headers(self, api_key: str | None) -> dict:
        return {"x-goog-api-key": api_key} if api_key else {}
