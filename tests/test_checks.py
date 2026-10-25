import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_course.checks import check_tier_zero, check_tool_response, check_embedding_response, notes_ok, run_check


class TierZeroChecksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.note = self.root / "notes.md"

    @staticmethod
    def responses(url, payload):
        if url.endswith("/api/chat"):
            return {"message": {"tool_calls": [{"function": {"name": "lookup_note", "arguments": {"topic": "agents"}}}]}}
        if url.endswith("/api/embed"):
            return {"embeddings": [[0.1, 0.2, 0.3]]}
        raise AssertionError(f"Unexpected endpoint: {url}")

    def test_tool_call_must_be_real_and_named(self):
        self.assertTrue(check_tool_response(self.responses("http://127.0.0.1:11434/api/chat", {})))
        self.assertFalse(check_tool_response({"message": {"content": "I would call lookup_note"}}))
        self.assertFalse(check_tool_response({"message": {"tool_calls": [{"function": {"name": "other"}}]}}))

    def test_embed_requires_nonempty_numeric_vector(self):
        self.assertTrue(check_embedding_response({"embeddings": [[0.1, 0.2]]}))
        self.assertFalse(check_embedding_response({"embeddings": [[]]}))
        self.assertFalse(check_embedding_response({"embeddings": [["not a vector"]]}))

    def test_successful_online_check_does_not_require_key_or_notes(self):
        seen = []
        def post(url, payload):
            seen.append(payload)
            return self.responses(url, payload)
        result = check_tier_zero(self.root, post=post,
                                 search=lambda query: ("online", [{"title": "Source", "url": "https://example.org", "snippet": "public"}]))
        self.assertTrue(result.ok, result.issues)
        self.assertEqual(result.mode, "online")
        self.assertEqual(len(seen), 2)
        self.assertTrue(all("api_key" not in payload for payload in seen))
        self.assertFalse(self.note.exists())

    def test_offline_fallback_is_labeled_offline(self):
        result = check_tier_zero(self.root, post=self.responses,
                                 search=lambda query: ("offline", [{"title": "Local", "url": "course://corpus/intro", "snippet": "offline"}]))
        self.assertTrue(result.ok)
        self.assertEqual(result.mode, "offline")

    def test_model_failure_blocks_gate_even_when_corpus_is_available(self):
        def post(url, payload):
            if url.endswith("/api/chat"):
                return {"message": {"content": "no tool used"}}
            return self.responses(url, payload)
        result = check_tier_zero(self.root, post=post,
                                 search=lambda query: ("offline", [{"title": "Local", "url": "course://corpus/intro", "snippet": "offline"}]))
        self.assertFalse(result.ok)
        self.assertTrue(any("tool" in issue for issue in result.issues))

    def test_missing_embed_or_source_blocks_gate(self):
        def missing_embed(url, payload):
            return {"embeddings": [[]]} if url.endswith("/api/embed") else self.responses(url, payload)
        result = check_tier_zero(self.root, post=missing_embed, search=lambda query: ("online", [{"title":"Web","url":"https://example.org","snippet":""}]))
        self.assertFalse(result.ok)
        self.assertTrue(any("embedding" in issue for issue in result.issues))
        result = check_tier_zero(self.root, post=self.responses, search=lambda query: ("", []))
        self.assertFalse(result.ok)
        self.assertTrue(any("source" in issue for issue in result.issues))

    def test_unavailable_model_error_is_actionable_and_no_key_suggested(self):
        def unavailable(url, payload):
            raise OSError("connection refused")
        result = check_tier_zero(self.root, post=unavailable,
                                 search=lambda query: ("offline", [{"title": "Local", "url": "course://corpus/intro", "snippet": ""}]))
        self.assertFalse(result.ok)
        self.assertIn("Ollama", " ".join(result.issues))
        self.assertNotIn("API key", " ".join(result.issues))

    def test_notes_require_four_headings_with_nonempty_learner_text(self):
        self.note.write_text("# Concepts\nOwn reasoning\n# Local observations\nObservations\n# Source route\nLocal corpus\n")
        ok, why = notes_ok(0, self.note)
        self.assertFalse(ok)
        self.assertIn("Limits", why)
        self.note.write_text(self.note.read_text() + "# Limits\nCPU limits and source failure.\n")
        self.assertTrue(notes_ok(0, self.note)[0])
        self.note.write_text(self.note.read_text().replace("CPU limits and source failure.", "   "))
        self.assertFalse(notes_ok(0, self.note)[0])

    def test_tier_one_notes_require_live_run_failure_analysis_and_reflection(self):
        self.note.write_text("# Live run\nLocal test.\n# Failure analysis\nSources missing.\n")
        self.assertFalse(notes_ok(1, self.note)[0])
        self.note.write_text(self.note.read_text() + "# Reflection\nI would improve citation checks.\n")
        self.assertTrue(notes_ok(1, self.note)[0])

    def test_future_tier_validator_fails_closed(self):
        result = run_check(2, self.root)
        self.assertFalse(result.ok)
        self.assertIn("unavailable", " ".join(result.issues))


if __name__ == "__main__":
    unittest.main()
