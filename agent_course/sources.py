"""Best-effort public search with a clearly labeled local-corpus fallback."""

from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from urllib.request import ProxyHandler, Request, build_opener


class _AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items: list[tuple[str, str]] = []
        self.href: str | None = None
        self.text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag != "a" or self.href is not None:
            return
        attributes = dict(attrs)
        if "result__a" in (attributes.get("class") or "").split():
            self.href = attributes.get("href", "")
            self.text = []

    def handle_data(self, data):
        if self.href is not None:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            self.items.append((self.href, " ".join(" ".join(self.text).split())))
            self.href = None
            self.text = []


class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data):
        self.parts.append(data)


def _plain_text(html: str) -> str:
    parser = _TextParser()
    parser.feed(html)
    return " ".join(" ".join(parser.parts).split())


def parse_ddg(body: bytes) -> list[dict]:
    parser = _AnchorParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    results: list[dict] = []
    seen: set[str] = set()
    for href, title in parser.items:
        if href.startswith("//"):
            href = "https:" + href
        parsed = urlparse(href)
        if parsed.hostname and parsed.hostname.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
            href = unquote(parse_qs(parsed.query).get("uddg", [""])[0])
            parsed = urlparse(href)
        if parsed.scheme not in ("http", "https") or not parsed.hostname or not title or href in seen:
            continue
        seen.add(href)
        results.append({"title": title[:160], "url": href, "snippet": ""})
        if len(results) == 5:
            break
    return results


def _fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "AgentEngineeringCourse/0.1 (local educational search)"})
    with build_opener(ProxyHandler({})).open(request, timeout=8) as response:
        return response.read(1_000_000)


def source_route(query: str, *, fetch=None, corpus_path: Path | None = None) -> tuple[str, list[dict]]:
    """Return (online/offline, sources), never presenting corpus as live web."""
    fetch = fetch or _fetch
    try:
        ddg_url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query)
        results = parse_ddg(fetch(ddg_url))
        if results:
            return "online", results
    except (OSError, ValueError, UnicodeError):
        pass
    try:
        wiki_url = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=" + quote_plus(query) + "&format=json"
        data = json.loads(fetch(wiki_url))
        results = []
        for item in data.get("query", {}).get("search", [])[:5]:
            pageid = item.get("pageid")
            if type(pageid) is not int or pageid <= 0:
                continue
            title = str(item.get("title", "")).strip()[:160]
            if title:
                results.append({"title": title, "url": f"https://en.wikipedia.org/?curid={pageid}",
                                "snippet": _plain_text(str(item.get("snippet", "")))[:240]})
        if results:
            return "online", results
    except (OSError, ValueError, TypeError, KeyError):
        pass
    corpus_path = corpus_path or Path(__file__).parent / "corpus" / "agent-basics.md"
    try:
        content = corpus_path.read_text(encoding="utf-8").strip()
    except OSError:
        return "", []
    if not content:
        return "", []
    return "offline", [{"title": "Bundled agent basics", "url": "course://corpus/agent-basics",
                        "snippet": " ".join(content.split())[:240]}]
