import unittest
from pathlib import Path

from agent_course.catalog import TIERS


ROOT = Path(__file__).resolve().parent.parent


class CurriculumTests(unittest.TestCase):
    def test_catalog_is_complete_and_contiguous(self):
        self.assertEqual([t["id"] for t in TIERS], list(range(8)))
        self.assertEqual([t["implemented"] for t in TIERS], [True, True] + [False] * 6)
        self.assertEqual(len({t["lesson"] for t in TIERS}), 8)

    def test_every_tier_has_original_lesson_and_honest_readiness(self):
        for tier in TIERS:
            with self.subTest(tier=tier["id"]):
                path = ROOT / tier["lesson"]
                self.assertTrue(path.is_file(), path)
                text = path.read_text(encoding="utf-8").lower()
                self.assertIn(f"tier {tier['id']}", text)
                self.assertIn("gate", text)
                self.assertIn("made with", text)
                if tier["implemented"]:
                    self.assertIn("runnable", text)
                else:
                    self.assertIn("roadmap only", text)
                    self.assertIn("validator unavailable", text)

    def test_readme_explains_no_keys_and_sequential_promotion(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        for term in ("zero api keys", "tier 0", "tier 7", "python -m agent_course status",
                     "python -m agent_course check", "python -m agent_course submit", "locked"):
            self.assertIn(term, readme)
        for secret_name in ("tavily_api_key", "nvidia_api_key", "openai_api_key"):
            self.assertNotIn(secret_name, readme)


if __name__ == "__main__":
    unittest.main()
