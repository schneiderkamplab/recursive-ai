#!/usr/bin/env python3
"""Compute conversation-length distributions for downloaded consumer–AI corpora."""

from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter
from datetime import date
from pathlib import Path
from statistics import mean

import pyarrow.parquet as parquet


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
RESULTS = ROOT / "results"
QUESTION_RE = re.compile(r"['\"]user_question['\"]\s*:")
RESPONSE_RE = re.compile(r"['\"]AI_response['\"]\s*:")


def _quantile_from_counter(counts: Counter[int], probability: float) -> int:
    target = max(1, math.ceil(sum(counts.values()) * probability))
    cumulative = 0
    for turns in sorted(counts):
        cumulative += counts[turns]
        if cumulative >= target:
            return turns
    raise ValueError("Cannot calculate a quantile from an empty distribution")


def _summarize(
    name: str,
    scope: str,
    status: str,
    counts: Counter[int],
    validation: dict[str, int | str],
    source_url: str,
) -> dict[str, object]:
    total = sum(counts.values())
    weighted_sum = sum(turns * frequency for turns, frequency in counts.items())
    return {
        "dataset": name,
        "scope": scope,
        "status": status,
        "total_conversations": total,
        "min_turns": min(counts) if counts else None,
        "max_turns": max(counts) if counts else None,
        "mean_turns": weighted_sum / total if total else None,
        "median_turns": _quantile_from_counter(counts, 0.5) if total else None,
        "p95_turns": _quantile_from_counter(counts, 0.95) if total else None,
        "p99_turns": _quantile_from_counter(counts, 0.99) if total else None,
        "one_turn_conversations": counts.get(1, 0),
        "one_turn_share": counts.get(1, 0) / total if total else None,
        "five_plus_conversations": sum(v for k, v in counts.items() if k >= 5),
        "five_plus_share": sum(v for k, v in counts.items() if k >= 5) / total if total else None,
        "ten_plus_conversations": sum(v for k, v in counts.items() if k >= 10),
        "ten_plus_share": sum(v for k, v in counts.items() if k >= 10) / total if total else None,
        "zero_turn_conversations": counts.get(0, 0),
        "validation": validation,
        "source_url": source_url,
    }


def analyze_wildchat() -> tuple[Counter[int], dict[str, int | str]]:
    counts: Counter[int] = Counter()
    checked = 0
    mismatches = 0
    incomplete = 0
    files = sorted((RAW / "wildchat").glob("*.parquet"))
    if len(files) != 14:
        raise RuntimeError(f"Expected 14 WildChat shards, found {len(files)}")

    for path in files:
        parquet_file = parquet.ParquetFile(path)
        for batch in parquet_file.iter_batches(columns=["turn"], batch_size=131_072):
            counts.update(int(value) for value in batch.column(0).to_pylist() if value is not None)

        # Validate 200 records per shard against the underlying message roles.
        sample = parquet_file.read_row_group(0, columns=["conversation", "turn"]).slice(0, 200)
        for row in sample.to_pylist():
            roles = [message.get("role") for message in (row["conversation"] or [])]
            user_messages = roles.count("user")
            assistant_messages = roles.count("assistant")
            checked += 1
            mismatches += int(user_messages != row["turn"])
            incomplete += int(user_messages != assistant_messages)

    return counts, {
        "records_checked": checked,
        "turn_field_vs_user_message_mismatches": mismatches,
        "unequal_user_assistant_counts": incomplete,
        "note": "All rows counted from the corpus's native turn field; 200 records per shard validated against message roles.",
    }


def analyze_lmsys() -> tuple[Counter[int], dict[str, int | str]]:
    counts: Counter[int] = Counter()
    checked = 0
    mismatches = 0
    incomplete = 0
    files = sorted((RAW / "lmsys").glob("*.parquet"))
    if len(files) != 6:
        raise RuntimeError(f"Expected 6 LMSYS shards, found {len(files)}")

    for path in files:
        parquet_file = parquet.ParquetFile(path)
        for batch in parquet_file.iter_batches(columns=["turn"], batch_size=131_072):
            counts.update(int(value) for value in batch.column(0).to_pylist() if value is not None)

        sample = parquet_file.read_row_group(0, columns=["conversation", "turn"]).slice(0, 500)
        for row in sample.to_pylist():
            roles = [message.get("role") for message in (row["conversation"] or [])]
            user_messages = roles.count("user")
            assistant_messages = roles.count("assistant")
            checked += 1
            mismatches += int(user_messages != row["turn"])
            incomplete += int(user_messages != assistant_messages)

    return counts, {
        "records_checked": checked,
        "turn_field_vs_user_message_mismatches": mismatches,
        "unequal_user_assistant_counts": incomplete,
        "note": "All rows counted from the corpus's native turn field; 500 records per shard validated against message roles.",
    }


def analyze_thoughttrace() -> tuple[Counter[int], dict[str, int | str]]:
    counts: Counter[int] = Counter()
    unequal = 0
    nonalternating = 0
    path = RAW / "thoughttrace" / "ThoughtTrace.jsonl"
    with path.open(encoding="utf-8") as source:
        for line in source:
            record = json.loads(line)
            roles = [message.get("type") for message in record.get("messages", [])]
            users = roles.count("user")
            assistants = roles.count("assistant")
            counts[users] += 1
            unequal += int(users != assistants)
            expected = [role for pair in (("user", "assistant"),) * users for role in pair]
            nonalternating += int(roles != expected)
    return counts, {
        "records_checked": sum(counts.values()),
        "unequal_user_assistant_counts": unequal,
        "nonalternating_role_sequences": nonalternating,
        "note": "Turns counted as user messages; every record's role sequence was checked.",
    }


def analyze_realuser_preview() -> tuple[Counter[int], dict[str, int | str]]:
    counts: Counter[int] = Counter()
    checked = 0
    question_mismatches = 0
    response_mismatches = 0
    path = RAW / "realuser_preview" / "ChatGPT-RealUser-2.2M-preview.csv"
    with path.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            turns = int(row["num_turns"])
            conversation = row["conversation"]
            counts[turns] += 1
            checked += 1
            question_mismatches += int(len(QUESTION_RE.findall(conversation)) != turns)
            response_mismatches += int(len(RESPONSE_RE.findall(conversation)) != turns)
    return counts, {
        "records_checked": checked,
        "num_turns_vs_question_count_mismatches": question_mismatches,
        "num_turns_vs_response_count_mismatches": response_mismatches,
        "note": "All rows counted from num_turns and validated against serialized question/response keys.",
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    analyses = [
        (
            "WildChat-1M",
            "Full public post-cleaning release",
            "Downloaded and analyzed",
            *analyze_wildchat(),
            "https://huggingface.co/datasets/allenai/WildChat-1M",
        ),
        (
            "ThoughtTrace",
            "Full public release",
            "Downloaded and analyzed",
            *analyze_thoughttrace(),
            "https://huggingface.co/datasets/SCAI-JHU/ThoughtTrace",
        ),
        (
            "ChatGPT-RealUser-2.2M",
            "Public preview only (600 conversations)",
            "Preview downloaded and analyzed; full corpus unavailable",
            *analyze_realuser_preview(),
            "https://huggingface.co/datasets/Gata-community/ChatGPT-RealUser-2.2M-preview",
        ),
        (
            "LMSYS-Chat-1M",
            "Full official release",
            "Downloaded and analyzed using authorized access",
            *analyze_lmsys(),
            "https://huggingface.co/datasets/lmsys/lmsys-chat-1m",
        ),
    ]

    summaries: list[dict[str, object]] = []
    distributions: list[dict[str, object]] = []
    for name, scope, status, counts, validation, source_url in analyses:
        summaries.append(_summarize(name, scope, status, counts, validation, source_url))
        positive_max = max((turns for turns in counts if turns >= 1), default=0)
        total = sum(counts.values())
        for turns in range(1, positive_max + 1):
            frequency = counts.get(turns, 0)
            distributions.append(
                {
                    "dataset": name,
                    "scope": scope,
                    "n_turns": turns,
                    "conversations": frequency,
                    "share": frequency / total if total else None,
                }
            )

    payload = {
        "analysis_date": date.today().isoformat(),
        "turn_definition": "One user prompt and its corresponding assistant response; native turn fields were used where supplied and validated against message records.",
        "summaries": summaries,
        "distribution": distributions,
    }
    (RESULTS / "turn_distribution.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    with (RESULTS / "turn_distribution.csv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=["dataset", "scope", "n_turns", "conversations", "share"],
        )
        writer.writeheader()
        writer.writerows(distributions)

    print(json.dumps({"analysis_date": payload["analysis_date"], "summaries": summaries}, indent=2))


if __name__ == "__main__":
    main()
