import tempfile
import unittest
from pathlib import Path

from agent_course.advanced import (
    check_tier_two, check_tier_three, check_tier_four, check_tier_five,
    check_tier_six, check_tier_seven,
)


ARTIFACTS = {
    2: """def answer(q, retrieve):
    if q == 'reset-password':
        row = retrieve(q)[0]
        return {'source_id': row['source_id'], 'text': row['snippet']}
    if q == 'general greeting':
        return {'status': 'ok', 'text': 'Follow normal workflow.'}
    retrieve(q)
    return {'status': 'no_answer'}
""",
    3: """def evaluate(cases):
    return {'metrics': {'citation_coverage': 0.5, 'answer_support': 0.5, 'abstention_rate': 0.5},
            'failures': ['wrong citation', 'missed abstention'],
            'comparison': {'baseline': 0.25, 'customized': 0.5}}
""",
    4: """def baseline(task): return task == 'summarize'
def customized(task): return True
def approve(command): return command.startswith('cat ')
""",
    5: """import json
def deny(): pass
def run(task, budget):
    with open(budget['memory'], 'w') as f: json.dump({'task': task}, f)
    return {'trace': [{'event': 'plan'}, {'event': 'delegate'}, {'event': 'memory_write'}, {'event': 'denied'}],
            'within_budget': True, 'denied': True}
""",
    6: """def authorize(action):
    return action == 'read_fixture'
""",
    7: """def tool_one(): pass
def tool_two(): pass
def tool_three(): pass
def tool_four(): pass
TOOLS = [tool_one, tool_two, tool_three, tool_four]
def run(task, harnesses=()):
    return {'tool_count': 4, 'bounded': True, 'eager_tokens': 100, 'lazy_tokens': 40,
            'portable': set(harnesses) == {'alpha', 'beta'}}
""",
}


class AdvancedFixtureTests(unittest.TestCase):
    def test_all_advanced_contracts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for tier, source in ARTIFACTS.items():
                folder = root / "work" / f"tier-{tier}"
                folder.mkdir(parents=True)
                name = {2: "rag_agent.py", 3: "evaluate.py", 4: "customize.py",
                        5: "deep_agent.py", 6: "policy.py", 7: "harness.py"}[tier]
                (folder / name).write_text(source)
            checks = [check_tier_two, check_tier_three, check_tier_four,
                      check_tier_five, check_tier_six, check_tier_seven]
            for tier, check in zip(range(2, 8), checks):
                with self.subTest(tier=tier):
                    self.assertTrue(check(root).ok, check(root).issues)

    def test_missing_artifact_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            result = check_tier_two(Path(directory))
        self.assertFalse(result.ok)
        self.assertIn("unavailable", " ".join(result.issues))


if __name__ == "__main__":
    unittest.main()
