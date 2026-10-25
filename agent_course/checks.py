"""Tier validators default to unavailable until their tested modules ship."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    mode: str
    issues: tuple[str, ...]


def run_check(tier: int, root: Path) -> CheckResult:
    return CheckResult(False, "", (f"Tier {tier} validator unavailable",))


def notes_ok(tier: int, path: Path) -> tuple[bool, str]:
    return False, f"Tier {tier} evidence validator unavailable"
