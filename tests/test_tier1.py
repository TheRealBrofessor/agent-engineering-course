import os
import tempfile
import unittest
from pathlib import Path

from agent_course.tier1 import check_tier_one, validate_report, safe_child_env


SOURCE = {"title": "Agent patterns", "url": "https://example.org/agent-patterns", "snippet": "Tools give evidence."}
REPORT = {
    "status": "ok",
    "outline": ["Tool evidence"],
    "sections": [{"heading": "Tool evidence", "text": "The report identifies the source of its claim.",
                  "source_urls": [SOURCE["url"]]}],
    "sources": [{"title": SOURCE["title"], "url": SOURCE["url"]}],
}


class TierOneValidationTests(unittest.TestCase):
    def test_valid_structure_and_observed_calls_pass(self):
        passed, issues = validate_report(REPORT, [SOURCE], 1, 1)
        self.assertTrue(passed, issues)

    def test_fabricated_url_is_rejected(self):
        fabricated = {**REPORT, "sections": [{**REPORT["sections"][0], "source_urls": ["https://invented.invalid"]}]}
        passed, issues = validate_report(fabricated, [SOURCE], 1, 1)
        self.assertFalse(passed)
        self.assertIn("source", " ".join(issues).lower())

    def test_missing_model_or_search_call_is_rejected(self):
        self.assertFalse(validate_report(REPORT, [SOURCE], 0, 1)[0])
        self.assertFalse(validate_report(REPORT, [SOURCE], 1, 0)[0])

    def test_empty_source_case_must_abstain_without_sources_or_sections(self):
        safe = {"status": "insufficient_sources", "outline": [], "sections": [], "sources": []}
        self.assertTrue(validate_report(safe, [], 1, 0)[0])
        fabricated = {**safe, "sources": [{"title": "Made up", "url": "https://fake.invalid"}]}
        self.assertFalse(validate_report(fabricated, [], 1, 0)[0])
        hallucinated = {**safe, "sections": [{"heading":"Guess", "text":"Unverified claim", "source_urls":[]}]}
        self.assertFalse(validate_report(hallucinated, [], 1, 0)[0])

    def test_missing_outline_or_unsourced_section_is_rejected(self):
        no_outline = {**REPORT, "outline": []}
        self.assertFalse(validate_report(no_outline, [SOURCE], 1, 1)[0])
        no_citation = {**REPORT, "sections": [{**REPORT["sections"][0], "source_urls": []}]}
        self.assertFalse(validate_report(no_citation, [SOURCE], 1, 1)[0])

    def test_declared_sources_must_match_observed_results(self):
        invented = {**REPORT, "sources": [{"title":"Other","url":"https://invented.invalid"}]}
        self.assertFalse(validate_report(invented, [SOURCE], 1, 1)[0])

    def test_malformed_report_is_failure_not_exception(self):
        for value in (None, "report", {}, {"status": "ok", "outline": ["x"], "sections": "text", "sources": []}):
            self.assertFalse(validate_report(value, [SOURCE], 1, 1)[0])


class TierOneRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.student_dir = self.root / "work" / "tier-1"
        self.student_dir.mkdir(parents=True)

    def test_missing_learner_file_fails_without_importing_anything(self):
        result = check_tier_one(self.root)
        self.assertFalse(result.ok)
        self.assertIn("report_agent.py", " ".join(result.issues))
        self.assertFalse((self.root / ".course" / "state.json").exists())

    def test_learner_code_times_out_without_recording_completion(self):
        (self.student_dir / "report_agent.py").write_text(
            "import time\ndef build_report(topic, search, model):\n    time.sleep(5)\n")
        result = check_tier_one(self.root, timeout=0.3)
        self.assertFalse(result.ok)
        self.assertIn("timeout", " ".join(result.issues).lower())
        self.assertFalse((self.root / ".course" / "state.json").exists())

    def test_learner_code_cannot_see_parent_secret_env(self):
        os.environ["COURSE_TEST_SECRET_KEY"] = "secret-value-not-for-output"
        try:
            self.assertNotIn("COURSE_TEST_SECRET_KEY", safe_child_env(self.root))
        finally:
            del os.environ["COURSE_TEST_SECRET_KEY"]
        file = self.student_dir / "report_agent.py"
        file.write_text(
            "import os\ndef build_report(topic, search, model):\n"
            "    if os.environ.get('COURSE_TEST_SECRET_KEY'):\n"
            "        raise RuntimeError('secret leaked into runner')\n"
            "    search(topic)\n"
            "    return {'status':'insufficient_sources','outline':[],'sections':[],'sources':[]}\n"
        )
        old = os.environ.get("COURSE_TEST_SECRET_KEY")
        os.environ["COURSE_TEST_SECRET_KEY"] = "secret-value-not-for-output"
        try:
            result = check_tier_one(self.root)
        finally:
            if old is None: del os.environ["COURSE_TEST_SECRET_KEY"]
            else: os.environ["COURSE_TEST_SECRET_KEY"] = old
        self.assertFalse(result.ok)
        self.assertNotIn("leaked", " ".join(result.issues).lower())


if __name__ == "__main__":
    unittest.main()
