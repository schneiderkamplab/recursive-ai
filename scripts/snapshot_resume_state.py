#!/usr/bin/env python3
"""Create a local, Git-ignored checkpoint of non-reconstructible audit state."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIRECTORY = ROOT / "resume_state"
MODEL_LOCK = ROOT / "model-locks" / "gemma4-26b-ollama.lock.json"
STATE_FILES = (
    ROOT / "classification" / "gemma4_26b_a4b_audit_v5_extension_levels.jsonl",
    ROOT
    / "classification"
    / "gemma4_26b_a4b_audit_v5_extension_levels_errors.jsonl",
    ROOT / "classification" / "manually_reviewed_clear_examples.jsonl",
    ROOT / "classification" / "manually_reviewed_potential_examples.jsonl",
    ROOT / "classification" / "manually_reviewed_none_examples.jsonl",
)


def _complete_jsonl_snapshot(path: Path) -> tuple[bytes, int]:
    """Read only the complete JSON lines present at the initial file size."""
    initial_size = path.stat().st_size
    with path.open("rb") as source:
        payload = source.read(initial_size)

    if payload and not payload.endswith(b"\n"):
        payload = payload.rsplit(b"\n", 1)[0] + b"\n" if b"\n" in payload else b""

    line_count = 0
    for line_count, line in enumerate(payload.splitlines(), 1):
        try:
            json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON in {path} at line {line_count}") from error
    return payload, line_count


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _git_commit() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _write_private(path: Path, payload: bytes) -> None:
    path.write_bytes(payload)
    path.chmod(0o600)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help=f"Local checkpoint directory (default: {DEFAULT_OUTPUT_DIRECTORY})",
    )
    args = parser.parse_args()

    missing = [path for path in (*STATE_FILES, MODEL_LOCK) if not path.exists()]
    if missing:
        names = ", ".join(str(path) for path in missing)
        raise SystemExit(f"Missing required resume-state files: {names}")

    output_directory = args.output_directory.resolve()
    output_directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone()
    snapshot_name = timestamp.strftime("v5-resume-%Y%m%dT%H%M%S%z")
    archive = output_directory / f"{snapshot_name}.tar.gz"
    if archive.exists():
        raise SystemExit(f"Refusing to overwrite existing checkpoint: {archive}")

    records = []
    with tempfile.TemporaryDirectory(prefix="recursive-ai-resume-") as temporary:
        staging = Path(temporary) / snapshot_name
        staging.mkdir()
        for source_path in STATE_FILES:
            payload, lines = _complete_jsonl_snapshot(source_path)
            destination = staging / source_path.name
            _write_private(destination, payload)
            records.append(
                {
                    "file": source_path.name,
                    "bytes": len(payload),
                    "json_lines": lines,
                    "sha256": _sha256(payload),
                }
            )

        model_payload = MODEL_LOCK.read_bytes()
        _write_private(staging / MODEL_LOCK.name, model_payload)
        records.append(
            {
                "file": MODEL_LOCK.name,
                "bytes": len(model_payload),
                "sha256": _sha256(model_payload),
            }
        )

        manifest = {
            "created_at": timestamp.isoformat(timespec="seconds"),
            "git_commit": _git_commit(),
            "contains_record_level_research_data": True,
            "handling": "Keep outside Git and do not publish without research-team review.",
            "files": records,
        }
        manifest_payload = (json.dumps(manifest, indent=2) + "\n").encode()
        _write_private(staging / "resume-manifest.json", manifest_payload)

        with tarfile.open(archive, "w:gz") as target:
            target.add(staging, arcname=snapshot_name)

    archive.chmod(0o600)
    print(
        json.dumps(
            {
                "archive": str(archive),
                "bytes": archive.stat().st_size,
                "sha256": _sha256(archive.read_bytes()),
                "files": records,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
