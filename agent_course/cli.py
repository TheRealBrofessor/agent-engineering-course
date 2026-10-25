"""Read-only status and explicit evidence-gated course commands."""

from __future__ import annotations

import argparse
from pathlib import Path

from .catalog import TIERS
from .checks import notes_ok, run_check
from .state import CourseStateError, read_state, record_completion


DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Original keyless agent-engineering course")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="course root (use a disposable root for tests)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="show active and locked tiers without running exercises")
    check = commands.add_parser("check", help="run only the active tier's validator")
    check.add_argument("--tier", type=int, required=True)
    submit = commands.add_parser("submit", help="attest evidence and unlock the next tier")
    submit.add_argument("--tier", type=int, required=True)
    submit.add_argument("--evidence", type=Path, required=True)
    submit.add_argument("--attest", action="store_true", help="confirm the work and explanation are yours")
    return parser


def require_active(requested: int, records: list[dict]) -> None:
    active = len(records)
    if requested != active:
        if active == len(TIERS):
            raise CourseStateError("Course complete; no active tier")
        raise CourseStateError(f"Locked: active tier is {active}")


def _evidence_in_tier(root: Path, tier: int, evidence: Path) -> Path:
    allowed = (root / "work" / f"tier-{tier}").resolve()
    candidate = evidence if evidence.is_absolute() else root / evidence
    resolved = candidate.resolve()
    if not resolved.is_relative_to(allowed):
        raise CourseStateError(f"Evidence must be under work/tier-{tier}/")
    if not resolved.is_file():
        raise CourseStateError("Evidence file is missing or not a regular file")
    return resolved


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    try:
        records = read_state(root / ".course" / "state.json")
        active = len(records)
        if args.command == "status":
            for tier in TIERS:
                number = tier["id"]
                if number < active:
                    label = "complete"
                elif number == active:
                    label = "active"
                else:
                    label = "locked"
                location = f" — {tier['lesson']}" if number == active else ""
                print(f"Tier {number}: {tier['title']} [{label}]{location}")
            if active == len(TIERS):
                print("All tiers complete")
            return 0
        require_active(args.tier, records)
        evidence: Path | None = None
        if args.command == "submit":
            if not args.attest:
                raise CourseStateError("Use --attest to confirm your own work and reflection")
            evidence = _evidence_in_tier(root, args.tier, args.evidence)
        result = run_check(args.tier, root)
        if not result.ok:
            for issue in result.issues:
                print(f"Tier {args.tier} FAIL: {issue}")
            return 1
        if args.command == "check":
            print(f"Tier {args.tier} check PASS ({result.mode})")
            return 0
        assert evidence is not None
        valid, reason = notes_ok(args.tier, evidence)
        if not valid:
            print(f"Tier {args.tier} FAIL: {reason}")
            return 1
        record_completion(root / ".course" / "state.json", args.tier, evidence, result.mode)
        print(f"Tier {args.tier} completed ({result.mode}); Tier {args.tier + 1} unlocked" if args.tier + 1 < len(TIERS)
              else f"Tier {args.tier} completed; course finished")
        return 0
    except CourseStateError as exc:
        print(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
