"""Runnable curriculum order; lesson files are never learner submissions."""

TIERS = (
    {"id": 0, "title": "Model-provider foundations", "lesson": "curriculum/tier-0.md", "implemented": True},
    {"id": 1, "title": "Build a research agent", "lesson": "curriculum/tier-1.md", "implemented": True},
    # ``implemented`` is retained as the historical release flag for callers;
    # advanced validators are nevertheless runnable and selected by checks.py.
    {"id": 2, "title": "Agentic RAG", "lesson": "curriculum/tier-2.md", "implemented": False},
    {"id": 3, "title": "Evaluation", "lesson": "curriculum/tier-3.md", "implemented": False},
    {"id": 4, "title": "Customization", "lesson": "curriculum/tier-4.md", "implemented": False},
    {"id": 5, "title": "Deep agents", "lesson": "curriculum/tier-5.md", "implemented": False},
    {"id": 6, "title": "Safety", "lesson": "curriculum/tier-6.md", "implemented": False},
    {"id": 7, "title": "Harnesses and skills", "lesson": "curriculum/tier-7.md", "implemented": False},
)
