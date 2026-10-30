"""Validated, ordered completion ledger for the local course."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .catalog import TIERS


class CourseStateError(ValueError):
    """The ledger or proposed transition is invalid."""


def read_state(path: Path) -> list[dict]:
    """Return validated contiguous completions; a missing ledger is empty."""
    path = Path(path)
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    except OSError as exc:
        raise CourseStateError(f"Cannot read course state: {exc}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CourseStateError("Malformed course state JSON") from exc
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "completed"}:
        raise CourseStateError("Invalid course state structure")
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        raise CourseStateError("Unsupported course state schema")
    records = payload["completed"]
    if not isinstance(records, list) or len(records) > len(TIERS):
        raise CourseStateError("Invalid completion list")
    for expected, record in enumerate(records):
        if not isinstance(record, dict) or set(record) != {"tier", "sha256", "mode", "checked_at"}:
            raise CourseStateError("Invalid completion record")
        if type(record["tier"]) is not int or record["tier"] != expected:
            raise CourseStateError("Completion history must be contiguous from Tier 0")
        digest = record["sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise CourseStateError("Invalid evidence checksum")
        if record["mode"] not in ("online", "offline", "fixture"):
            raise CourseStateError("Invalid source mode")
        try:
            checked_at = datetime.fromisoformat(record["checked_at"])
            if checked_at.tzinfo is None:
                raise ValueError("Timestamp requires timezone")
        except (ValueError, TypeError):
            raise CourseStateError("Invalid completion timestamp") from None
    return records


def record_completion(path: Path, tier: int, evidence_path: Path, mode: str) -> list[dict]:
    """Atomically append only the active tier after nonempty evidence exists."""
    path, evidence_path = Path(path), Path(evidence_path)
    records = read_state(path)
    active = len(records)
    if active == len(TIERS):
        raise CourseStateError("Course complete; no further tier exists")
    if type(tier) is not int or tier != active:
        raise CourseStateError(f"Locked: active tier is {active}")
    if mode not in ("online", "offline", "fixture"):
        raise CourseStateError("Invalid source mode")
    try:
        if not evidence_path.is_file():
            raise CourseStateError("Evidence file is missing or not a regular file")
        data = evidence_path.read_bytes()
    except OSError as exc:
        raise CourseStateError(f"Cannot read evidence file: {exc}") from exc
    if not data.strip():
        raise CourseStateError("Evidence file is empty")
    records.append({
        "tier": tier,
        "sha256": hashlib.sha256(data).hexdigest(),
        "mode": mode,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    })
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(prefix=".state-", suffix=".json", dir=path.parent)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump({"schema_version": 1, "completed": records}, stream, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
    except OSError as exc:
        raise CourseStateError(f"Cannot save course state: {exc}") from exc
    return records
