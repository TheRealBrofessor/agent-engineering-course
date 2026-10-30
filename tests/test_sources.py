import tempfile
import unittest
from pathlib import Path
from urllib.error import URLError

from agent_course.sources import parse_ddg, source_route


class SourceRouteTests(unittest.TestCase):
    def test_extracts_titles_and_decodes_redirects(self):
        html = b'''<html><body>
        <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.org%2Fintro">Agent primer</a>
        <a class="result__a" href="https://docs.example.net/guide">Practical guide</a>
        <a class="result__a" href="javascript:alert(1)">Not a source</a>
        </body></html>'''
        items = parse_ddg(html)
        self.assertEqual([x["url"] for x in items], ["https://example.org/intro", "https://docs.example.net/guide"])
        self.assertEqual(items[0]["title"], "Agent primer")

    def test_no_web_route_uses_labeled_bundled_corpus(self):
        with tempfile.TemporaryDirectory() as d:
            corpus = Path(d) / "intro.md"
            corpus.write_text("Agent components: model, tools, memory, routing.")
            def broken_fetch(url):
                raise URLError("offline")
            mode, items = source_route("public topic", fetch=broken_fetch, corpus_path=corpus)
        self.assertEqual(mode, "offline")
        self.assertEqual(items[0]["url"], "course://corpus/agent-basics")
        self.assertTrue(items[0]["snippet"])

    def test_no_route_or_corpus_returns_no_sources(self):
        with tempfile.TemporaryDirectory() as d:
            def broken_fetch(url):
                raise URLError("offline")
            mode, items = source_route("topic", fetch=broken_fetch, corpus_path=Path(d)/"missing.md")
        self.assertEqual((mode, items), ("", []))

    def test_public_ddg_route_is_labeled_online(self):
        def fetch(url):
            if "duckduckgo" in url:
                return b'<a class="result__a" href="https://example.org/source">Public source</a>'
            raise AssertionError("Wikipedia should not run after DDG success")
        mode, items = source_route("agent basics", fetch=fetch)
        self.assertEqual(mode, "online")
        self.assertEqual(items[0]["url"], "https://example.org/source")

    def test_wikipedia_route_used_when_ddg_empty(self):
        def fetch(url):
            if "duckduckgo" in url:
                return b"<html>empty</html>"
            return b'{"query":{"search":[{"title":"Agent","pageid":42,"snippet":"An <b>agent</b>"}]}}'
        mode, items = source_route("agents", fetch=fetch)
        self.assertEqual(mode, "online")
        self.assertEqual(items[0]["url"], "https://en.wikipedia.org/?curid=42")
        self.assertNotIn("<b>", items[0]["snippet"])


if __name__ == "__main__":
    unittest.main()
