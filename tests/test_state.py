import hashlib
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

from agent_course.state import CourseStateError, read_state, record_completion


class CourseStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / ".course" / "state.json"
        self.note = self.root / "notes.md"
        self.note.write_text("My own observations about a local model and sources.\n")

    def test_missing_state_starts_at_tier_zero_without_writing(self):
        self.assertEqual(read_state(self.path), [])
        self.assertFalse(self.path.exists())

    def test_cannot_skip_tier_zero(self):
        with self.assertRaisesRegex(CourseStateError, "active tier is 0"):
            record_completion(self.path, 1, self.note, "offline")
        self.assertFalse(self.path.exists())

    def test_completion_saves_hash_and_private_atomic_file(self):
        records = record_completion(self.path, 0, self.note, "offline")
        self.assertEqual([r["tier"] for r in records], [0])
        self.assertEqual(records[0]["sha256"], hashlib.sha256(self.note.read_bytes()).hexdigest())
        self.assertEqual(records[0]["mode"], "offline")
        self.assertIn("T", records[0]["checked_at"])
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
        self.assertEqual(read_state(self.path), records)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), ["state.json"])

    def test_replay_does_not_change_existing_state(self):
        record_completion(self.path, 0, self.note, "offline")
        original = self.path.read_bytes()
        with self.assertRaisesRegex(CourseStateError, "active tier is 1"):
            record_completion(self.path, 0, self.note, "offline")
        self.assertEqual(self.path.read_bytes(), original)

    def test_rejects_missing_or_empty_evidence(self):
        with self.assertRaises(CourseStateError):
            record_completion(self.path, 0, self.root / "missing.md", "offline")
        self.note.write_text(" \n ")
        with self.assertRaises(CourseStateError):
            record_completion(self.path, 0, self.note, "offline")
        self.assertFalse(self.path.exists())

    def test_rejects_gapped_or_duplicate_history(self):
        self.path.parent.mkdir()
        for ids in ([0, 2], [0, 0]):
            self.path.write_text(json.dumps({"schema_version": 1, "completed": [
                {"tier": t, "sha256": "a" * 64, "mode": "offline", "checked_at": "2026-10-25T12:00:00+00:00"}
                for t in ids
            ]}))
            with self.assertRaises(CourseStateError):
                read_state(self.path)

    def test_rejects_malformed_state_without_repairing_it(self):
        self.path.parent.mkdir()
        self.path.write_text("{not json")
        original = self.path.read_bytes()
        with self.assertRaises(CourseStateError):
            read_state(self.path)
        self.assertEqual(self.path.read_bytes(), original)

    def test_rejects_unknown_schema_and_finished_course(self):
        self.path.parent.mkdir()
        self.path.write_text(json.dumps({"schema_version": 99, "completed": []}))
        with self.assertRaises(CourseStateError):
            read_state(self.path)
        self.path.unlink()
        for tier in range(8):
            record_completion(self.path, tier, self.note, "fixture")
        with self.assertRaisesRegex(CourseStateError, "complete"):
            record_completion(self.path, 8, self.note, "fixture")


if __name__ == "__main__":
    unittest.main()
