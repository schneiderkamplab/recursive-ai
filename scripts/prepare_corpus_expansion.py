#!/usr/bin/env python3
"""Normalize ShareGPT-X, PRISM, and ShareChat into a deduplicated 10x10 expansion.

The expansion is deliberately separate from the frozen corpus used by the v5
audit. Exact normalized transcripts already present in that corpus, or repeated
within the expansion, are counted in the manifest and omitted from the output.
"""

from __future__ import annotations

import argparse
import ast
import csv
import gzip
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Iterable, Iterator
from pathlib import Path

import ijson


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
EXISTING = ROOT / "classification" / "long_conversations_10x10.jsonl.gz"
OUTPUT = ROOT / "classification" / "corpus_expansion_10x10.jsonl.gz"
MANIFEST = ROOT / "classification" / "corpus_expansion_manifest.json"
MIN_MESSAGES_PER_ROLE = 10
csv.field_size_limit(sys.maxsize)


def _clean_messages(
    messages: Iterable[dict], role_key: str = "role", content_key: str = "content"
) -> list[dict[str, str]]:
    role_map = {
        "human": "user",
        "gpt": "assistant",
        "model": "assistant",
        "llm": "assistant",
    }
    cleaned: list[dict[str, str]] = []
    for message in messages:
        role = role_map.get(str(message.get(role_key)), message.get(role_key))
        if role not in {"user", "assistant"}:
            continue
        cleaned.append(
            {"role": str(role), "content": str(message.get(content_key) or "")}
        )
    return cleaned


def _role_counts(messages: list[dict[str, str]]) -> tuple[int, int]:
    return (
        sum(message["role"] == "user" for message in messages),
        sum(message["role"] == "assistant" for message in messages),
    )


def _transcript_hash(messages: list[dict[str, str]]) -> str:
    payload = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def _record(
    dataset: str, source_id: str, messages: list[dict[str, str]], **metadata: object
) -> dict:
    user_messages, assistant_messages = _role_counts(messages)
    stable_id = hashlib.sha256(f"{dataset}\0{source_id}".encode()).hexdigest()[:24]
    return {
        "id": stable_id,
        "dataset": dataset,
        "source_id": source_id,
        "exchanges": min(user_messages, assistant_messages),
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "message_turns": len(messages),
        "characters": sum(len(message["content"]) for message in messages),
        "messages": messages,
        **metadata,
    }


def _qualifies(messages: list[dict[str, str]]) -> bool:
    user_messages, assistant_messages = _role_counts(messages)
    return (
        user_messages >= MIN_MESSAGES_PER_ROLE
        and assistant_messages >= MIN_MESSAGES_PER_ROLE
    )


def _existing_transcript_hashes(path: Path) -> set[str]:
    hashes: set[str] = set()
    with gzip.open(path, "rt", encoding="utf-8") as source:
        for line in source:
            record = json.loads(line)
            hashes.add(_transcript_hash(record["messages"]))
    return hashes


def _sharegpt_x_records(path: Path) -> Iterator[dict]:
    with path.open("rb") as source:
        for row in ijson.items(source, "item"):
            messages = _clean_messages(
                row.get("conversations") or [], role_key="from", content_key="value"
            )
            if _qualifies(messages):
                yield _record(
                    "ShareGPT-X",
                    str(row["id"]),
                    messages,
                    model=row.get("$modelId"),
                    language=row.get("language"),
                    consecutive_turns=row.get("consecutive_turns"),
                )


def _prism_records(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8") as source:
        for line in source:
            row = json.loads(line)
            history = row.get("conversation_history") or []
            # PRISM presents several model alternatives at each exchange. Only
            # the response selected by the participant belongs to the realized
            # conversational path.
            path_messages = [
                item
                for item in history
                if item.get("role") == "user"
                or (item.get("role") == "model" and item.get("if_chosen") is True)
            ]
            messages = _clean_messages(path_messages)
            if _qualifies(messages):
                yield _record(
                    "PRISM-alignment",
                    str(row["conversation_id"]),
                    messages,
                    user_id=str(row.get("user_id")) if row.get("user_id") else None,
                    conversation_type=row.get("conversation_type"),
                )


def _parse_conversation(value: str) -> list[dict]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = ast.literal_eval(value)
    if not isinstance(parsed, list):
        raise ValueError("ShareChat conversation field is not a list")
    return parsed


def _sharechat_conversation_rows(path: Path, platform: str) -> Iterator[dict]:
    with path.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            messages = _clean_messages(_parse_conversation(row["conversation"]))
            if _qualifies(messages):
                source_id = row.get("conversation_id") or row.get("url")
                if not source_id:
                    source_id = _transcript_hash(messages)
                yield _record(
                    "ShareChat",
                    str(source_id),
                    messages,
                    platform=row.get("platform") or platform,
                    language=row.get("language"),
                    fine_grained_topic=row.get("fine_grained_topic"),
                    high_level_category=row.get("high_level_category"),
                )


def _sharechat_turn_rows(path: Path, platform: str) -> Iterator[dict]:
    block_counts: Counter[str] = Counter()
    current_key: str | None = None
    current_source_id: str | None = None
    current_rows: list[dict] = []

    def emit(rows: list[dict]) -> dict | None:
        if not rows:
            return None
        messages = _clean_messages(
            [
                {
                    "role": row.get("role"),
                    "content": row.get("plain_text") or row.get("content") or "",
                }
                for row in sorted(
                    rows,
                    key=lambda row: int(
                        row.get("message_index") or row.get("turn") or 0
                    ),
                )
            ]
        )
        if not _qualifies(messages):
            return None
        first = rows[0]
        return _record(
            "ShareChat",
            str(current_source_id),
            messages,
            platform=first.get("platform") or platform,
            language=first.get("detected_language_final") or first.get("language"),
            fine_grained_topic=first.get("fine_grained_topic"),
            high_level_category=first.get("high_level_category"),
            topic=first.get("topic"),
        )

    with path.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            key = row.get("conversation_id") or row.get("url")
            if not key:
                raise ValueError(f"No conversation key in {path}")
            if current_key is None:
                current_key = key
                block_counts[key] += 1
                current_source_id = key
            if key != current_key:
                record = emit(current_rows)
                if record:
                    yield record
                current_key, current_rows = key, []
                block_counts[key] += 1
                current_source_id = (
                    key
                    if block_counts[key] == 1
                    else f"{key}#occurrence={block_counts[key]}"
                )
            current_rows.append(row)
        record = emit(current_rows)
        if record:
            yield record


def _sharechat_records(directory: Path) -> Iterator[dict]:
    for path in sorted(directory.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as source:
            fields = csv.DictReader(source).fieldnames or []
        if "conversation" in fields:
            yield from _sharechat_conversation_rows(path, path.stem)
        else:
            yield from _sharechat_turn_rows(path, path.stem)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW)
    parser.add_argument("--existing", type=Path, default=EXISTING)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    args = parser.parse_args()

    existing_hashes = _existing_transcript_hashes(args.existing)
    seen_hashes = set(existing_hashes)
    included: Counter[str] = Counter()
    qualifying: Counter[str] = Counter()
    existing_duplicates: Counter[str] = Counter()
    expansion_duplicates: Counter[str] = Counter()
    characters: Counter[str] = Counter()
    sharechat_qualifying_by_platform: Counter[str] = Counter()
    sharechat_included_by_platform: Counter[str] = Counter()
    sources = (
        (
            "ShareGPT-X",
            _sharegpt_x_records(
                args.raw_dir / "sharegpt_x" / "ChatGPT-Simple_ShareGPT_Full.json"
            ),
        ),
        (
            "PRISM-alignment",
            _prism_records(args.raw_dir / "prism" / "conversations.jsonl"),
        ),
        ("ShareChat", _sharechat_records(args.raw_dir / "sharechat")),
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(args.output, "wt", encoding="utf-8", compresslevel=6) as target:
        for dataset, records in sources:
            for record in records:
                qualifying[dataset] += 1
                if dataset == "ShareChat":
                    sharechat_qualifying_by_platform[str(record.get("platform"))] += 1
                transcript_hash = _transcript_hash(record["messages"])
                if transcript_hash in existing_hashes:
                    existing_duplicates[dataset] += 1
                    continue
                if transcript_hash in seen_hashes:
                    expansion_duplicates[dataset] += 1
                    continue
                seen_hashes.add(transcript_hash)
                target.write(json.dumps(record, ensure_ascii=False) + "\n")
                included[dataset] += 1
                if dataset == "ShareChat":
                    sharechat_included_by_platform[str(record.get("platform"))] += 1
                characters[dataset] += record["characters"]

    manifest = {
        "minimum_user_messages": MIN_MESSAGES_PER_ROLE,
        "minimum_assistant_messages": MIN_MESSAGES_PER_ROLE,
        "frozen_v5_corpus_modified": False,
        "existing_exact_transcript_hashes": len(existing_hashes),
        "qualifying_before_deduplication": dict(qualifying),
        "excluded_as_exact_duplicate_of_existing_corpus": dict(existing_duplicates),
        "excluded_as_exact_duplicate_within_expansion": dict(expansion_duplicates),
        "included": dict(included),
        "sharechat_qualifying_by_platform": dict(sharechat_qualifying_by_platform),
        "sharechat_included_by_platform": dict(sharechat_included_by_platform),
        "characters": dict(characters),
        "total_included": sum(included.values()),
        "output": str(args.output),
    }
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
