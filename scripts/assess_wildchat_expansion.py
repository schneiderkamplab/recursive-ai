#!/usr/bin/env python3
"""Measure new >=10x10 WildChat-4.8M conversations beyond the v5 corpus.

The comparison reports both upstream ``conversation_hash`` overlap and an exact
hash of normalized role/content sequences. It does not alter the frozen v5
corpus or audit.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

import pyarrow.parquet as parquet


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXISTING = ROOT / "classification" / "long_conversations_10x10.jsonl.gz"
DEFAULT_NEW = ROOT / "raw" / "wildchat_4_8m"
DEFAULT_REPORT = ROOT / "results" / "wildchat_4_8m_10x10_overlap.json"


def _messages(raw_messages: list[dict] | None) -> list[dict[str, str]]:
    return [
        {"role": message["role"], "content": str(message.get("content") or "")}
        for message in (raw_messages or [])
        if message.get("role") in {"user", "assistant"}
    ]


def _transcript_hash(messages: list[dict[str, str]]) -> str:
    payload = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def _existing_keys(path: Path) -> tuple[set[str], set[str], int]:
    source_ids: set[str] = set()
    transcripts: set[str] = set()
    count = 0
    with gzip.open(path, "rt", encoding="utf-8") as source:
        for line in source:
            record = json.loads(line)
            if record["dataset"] != "WildChat-1M":
                continue
            count += 1
            source_ids.add(str(record["source_id"]))
            transcripts.add(_transcript_hash(record["messages"]))
    return source_ids, transcripts, count


def _assess(
    directory: Path, existing_ids: set[str], existing_transcripts: set[str]
) -> dict:
    totals: Counter[str] = Counter()
    new_ids: set[str] = set()
    new_transcripts: set[str] = set()
    seen_ids: set[str] = set()
    seen_transcripts: set[str] = set()

    paths = sorted(directory.glob("*.parquet"))
    if not paths:
        raise FileNotFoundError(f"No Parquet shards found in {directory}")

    for index, path in enumerate(paths, start=1):
        parquet_file = parquet.ParquetFile(path)
        for batch in parquet_file.iter_batches(
            columns=["conversation_hash", "conversation", "turn"], batch_size=2048
        ):
            for row in batch.to_pylist():
                totals["release_rows"] += 1
                if int(row["turn"] or 0) < 10:
                    continue
                messages = _messages(row["conversation"])
                user_count = sum(message["role"] == "user" for message in messages)
                assistant_count = sum(
                    message["role"] == "assistant" for message in messages
                )
                if user_count < 10 or assistant_count < 10:
                    totals["reported_turn_ge_10_but_not_10x10"] += 1
                    continue

                totals["qualifying_10x10_rows"] += 1
                source_id = str(row["conversation_hash"])
                transcript = _transcript_hash(messages)
                if source_id in seen_ids:
                    totals["duplicate_source_id_rows_within_4_8m"] += 1
                else:
                    seen_ids.add(source_id)
                if transcript in seen_transcripts:
                    totals["duplicate_exact_transcript_rows_within_4_8m"] += 1
                else:
                    seen_transcripts.add(transcript)

                if source_id in existing_ids:
                    totals["rows_overlapping_v5_by_source_id"] += 1
                else:
                    totals["rows_new_by_source_id"] += 1
                    new_ids.add(source_id)
                if transcript in existing_transcripts:
                    totals["rows_overlapping_v5_by_exact_transcript"] += 1
                else:
                    totals["rows_new_by_exact_transcript"] += 1
                    new_transcripts.add(transcript)
        print(f"[{index}/{len(paths)}] {path.name}", flush=True)

    return {
        **totals,
        "unique_qualifying_source_ids_in_4_8m": len(seen_ids),
        "unique_qualifying_exact_transcripts_in_4_8m": len(seen_transcripts),
        "unique_new_source_ids_beyond_v5": len(new_ids),
        "unique_new_exact_transcripts_beyond_v5": len(new_transcripts),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--existing", type=Path, default=DEFAULT_EXISTING)
    parser.add_argument("--new-directory", type=Path, default=DEFAULT_NEW)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    existing_ids, existing_transcripts, existing_count = _existing_keys(args.existing)
    report = {
        "criterion": "at least 10 user and at least 10 assistant messages after normalization",
        "existing_corpus": str(args.existing),
        "existing_wildchat_1m_10x10_rows": existing_count,
        "existing_wildchat_1m_unique_source_ids": len(existing_ids),
        "existing_wildchat_1m_unique_exact_transcripts": len(existing_transcripts),
        "new_release_directory": str(args.new_directory),
        "comparison": _assess(args.new_directory, existing_ids, existing_transcripts),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
