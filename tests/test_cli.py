import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from agent_course.cli import main
from agent_course.checks import CheckResult
from agent_course.state import read_state


class CourseCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.note = self.root / "work" / "tier-0" / "notes.md"
        self.note.parent.mkdir(parents=True)
        self.note.write_text("# Concepts\nMy answer\n# Local observations\nLocal model\n# Source route\nOffline corpus\n# Limits\nSmall model\n")
        self.state_path = self.root / ".course" / "state.json"

    def invoke(self, *args):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root), *args])
        return code, output.getvalue()

    def test_status_starts_at_tier_zero_and_hides_locked_paths(self):
        with patch("agent_course.cli.run_check") as check:
            code, output = self.invoke("status")
        self.assertEqual(code, 0)
        self.assertIn("Tier 0", output)
        self.assertIn("Tier 1", output)
        self.assertIn("locked", output.lower())
        self.assertNotIn("curriculum/tier-1.md", output)
        self.assertFalse(self.state_path.exists())
        check.assert_not_called()

    def test_locked_check_never_runs_validator(self):
        with patch("agent_course.cli.run_check") as check:
            code, output = self.invoke("check", "--tier", "2")
        self.assertEqual(code, 2)
        self.assertIn("active tier is 0", output)
        check.assert_not_called()

    def test_submit_requires_explicit_attestation(self):
        with patch("agent_course.cli.run_check") as check:
            code, output = self.invoke("submit", "--tier", "0", "--evidence", str(self.note))
        self.assertEqual(code, 2)
        self.assertIn("attest", output)
        check.assert_not_called()
        self.assertFalse(self.state_path.exists())

    def test_failed_check_does_not_record_progress(self):
        with patch("agent_course.cli.run_check", return_value=CheckResult(False, "", ("model offline",))):
            code, output = self.invoke("submit", "--tier", "0", "--evidence", str(self.note), "--attest")
        self.assertNotEqual(code, 0)
        self.assertIn("model offline", output)
        self.assertFalse(self.state_path.exists())

    def test_submit_requires_evidence_within_own_tier(self):
        outside = self.root / "elsewhere.md"
        outside.write_text("unrelated")
        with patch("agent_course.cli.run_check") as check:
            code, output = self.invoke("submit", "--tier", "0", "--evidence", str(outside), "--attest")
        self.assertEqual(code, 2)
        self.assertIn("work/tier-0", output)
        check.assert_not_called()

    def test_successful_tier_zero_unlocks_tier_one_without_finishing_it(self):
        with patch("agent_course.cli.run_check", return_value=CheckResult(True, "offline", ())), \
             patch("agent_course.cli.notes_ok", return_value=(True, "")):
            code, output = self.invoke("submit", "--tier", "0", "--evidence", str(self.note), "--attest")
        self.assertEqual(code, 0, output)
        self.assertEqual([r["tier"] for r in read_state(self.state_path)], [0])
        code, status = self.invoke("status")
        self.assertEqual(code, 0)
        self.assertIn("Tier 1", status)
        self.assertIn("active", status.lower())
        self.assertIn("Tier 2", status)
        self.assertIn("locked", status.lower())
        with patch("agent_course.cli.run_check") as check:
            code, output = self.invoke("submit", "--tier", "0", "--evidence", str(self.note), "--attest")
        self.assertEqual(code, 2)
        check.assert_not_called()

    def test_bad_notes_cannot_promote_even_with_positive_model_check(self):
        with patch("agent_course.cli.run_check", return_value=CheckResult(True, "online", ())), \
             patch("agent_course.cli.notes_ok", return_value=(False, "missing Limits")):
            code, output = self.invoke("submit", "--tier", "0", "--evidence", str(self.note), "--attest")
        self.assertNotEqual(code, 0)
        self.assertIn("missing Limits", output)
        self.assertFalse(self.state_path.exists())


if __name__ == "__main__":
    unittest.main()
