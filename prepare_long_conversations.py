#!/usr/bin/env python3
"""Create a compressed, normalized corpus of conversations with >=10 exchanges."""

from __future__ import annotations

import ast
import csv
import gzip
import hashlib
import json
from pathlib import Path
from typing import Iterable

import pyarrow.parquet as parquet


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
OUTPUT = ROOT / "classification" / "long_conversations_10x10.jsonl.gz"
MANIFEST = ROOT / "classification" / "long_conversations_manifest.json"
MIN_EXCHANGES = 10


def _clean_messages(messages: Iterable[dict], role_key: str = "role") -> list[dict[str, str]]:
    cleaned = []
    for message in messages:
        role = message.get(role_key) or message.get("type")
        if role not in {"user", "assistant"}:
            continue
        cleaned.append({"role": role, "content": str(message.get("content") or "")})
    return cleaned


def _record(dataset: str, source_id: str, exchanges: int, messages: list[dict[str, str]], **metadata) -> dict:
    stable_id = hashlib.sha256(f"{dataset}\0{source_id}".encode()).hexdigest()[:24]
    return {
        "id": stable_id,
        "dataset": dataset,
        "source_id": source_id,
        "exchanges": exchanges,
        "message_turns": len(messages),
        "characters": sum(len(message["content"]) for message in messages),
        "messages": messages,
        **metadata,
    }


def _parquet_records(dataset: str, directory: Path, id_column: str) -> Iterable[dict]:
    for path in sorted(directory.glob("*.parquet")):
        parquet_file = parquet.ParquetFile(path)
        columns = [id_column, "conversation", "turn", "model", "language"]
        for batch in parquet_file.iter_batches(columns=columns, batch_size=1024):
            for row in batch.to_pylist():
                exchanges = int(row["turn"])
                if exchanges < MIN_EXCHANGES:
                    continue
                messages = _clean_messages(row["conversation"] or [])
                yield _record(
                    dataset,
                    str(row[id_column]),
                    exchanges,
                    messages,
                    model=row.get("model"),
                    language=row.get("language"),
                    source_file=path.name,
                )


def _thoughttrace_records() -> Iterable[dict]:
    path = RAW / "thoughttrace" / "ThoughtTrace.jsonl"
    with path.open(encoding="utf-8") as source:
        for line in source:
            row = json.loads(line)
            messages = _clean_messages(row.get("messages", []), role_key="type")
            exchanges = sum(message["role"] == "user" for message in messages)
            if exchanges >= MIN_EXCHANGES:
                yield _record(
                    "ThoughtTrace",
                    str(row["id"]),
                    exchanges,
                    messages,
                    model=row.get("model_name"),
                    language="English",
                    task_summary=row.get("task_summary"),
                )


def _realuser_records() -> Iterable[dict]:
    path = RAW / "realuser_preview" / "ChatGPT-RealUser-2.2M-preview.csv"
    with path.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            exchanges = int(row["num_turns"])
            if exchanges < MIN_EXCHANGES:
                continue
            pairs = ast.literal_eval(row["conversation"])
            messages = []
            for pair in pairs:
                messages.extend(
                    [
                        {"role": "user", "content": str(pair.get("user_question") or "")},
                        {"role": "assistant", "content": str(pair.get("AI_response") or "")},
                    ]
                )
            yield _record(
                "ChatGPT-RealUser-2.2M-preview",
                str(row["conversation_id"]),
                exchanges,
                messages,
                model=row.get("LLM_type"),
                language=None,
                user_id=str(row.get("user_id")),
            )


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sources = [
        _parquet_records("WildChat-1M", RAW / "wildchat", "conversation_hash"),
        _parquet_records("LMSYS-Chat-1M", RAW / "lmsys", "conversation_id"),
        _thoughttrace_records(),
        _realuser_records(),
    ]
    counts: dict[str, int] = {}
    characters: dict[str, int] = {}
    maxima: dict[str, int] = {}
    with gzip.open(OUTPUT, "wt", encoding="utf-8", compresslevel=6) as target:
        for records in sources:
            for record in records:
                target.write(json.dumps(record, ensure_ascii=False) + "\n")
                dataset = record["dataset"]
                counts[dataset] = counts.get(dataset, 0) + 1
                characters[dataset] = characters.get(dataset, 0) + record["characters"]
                maxima[dataset] = max(maxima.get(dataset, 0), record["characters"])

    manifest = {
        "minimum_user_messages": MIN_EXCHANGES,
        "minimum_assistant_messages": MIN_EXCHANGES,
        "counts": counts,
        "characters": characters,
        "maximum_characters": maxima,
        "total_conversations": sum(counts.values()),
        "total_characters": sum(characters.values()),
        "output": str(OUTPUT),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
