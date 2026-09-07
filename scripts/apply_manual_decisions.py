#!/usr/bin/env python3
"""Validate staged one-by-one decisions and append canonical manual records."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "classification" / "long_conversations_10x10.jsonl.gz"
AUDIT = ROOT / "classification" / "gemma4_26b_a4b_audit_v5_extension_levels.jsonl"
LEDGERS = {
    "clear": ROOT / "classification" / "manually_reviewed_clear_examples.jsonl",
    "potential": ROOT / "classification" / "manually_reviewed_potential_examples.jsonl",
    "none": ROOT / "classification" / "manually_reviewed_none_examples.jsonl",
}
LEVELS = {
    0: ("instrumental_task", "none"),
    1: ("capability_extension", "capability"),
    2: ("project_possession_extension", "owned_project"),
    3: ("representational_extension", "self_representation"),
    4: ("reflexive_extension", "self_understanding"),
    5: ("enacted_extension", "possible_self_enactment"),
}
STAGES = ("externalization", "ai_reflection", "user_uptake", "recursive_reentry")
TURN_RE = re.compile(r"\b[UA]\d+(?:[–-][UA]?\d+)?(?:\s*(?:,|and)\s*[UA]\d+(?:[–-][UA]?\d+)?)?")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _stage_record(stage: str, description: str) -> dict[str, str]:
    turns = TURN_RE.findall(description)
    turn = ", ".join(dict.fromkeys(turns)) if turns else "not directly evidenced"
    return {
        "turn": turn,
        "evidence": (
            "Complete source conversation reviewed; turn references are retained "
            "without unnecessarily duplicating sensitive transcript text."
        ),
        "interpretation": description,
    }


def _canonical(decision: dict[str, Any], source: dict[str, Any], cutoff: int) -> dict[str, Any]:
    label = decision["classification"]
    level = int(decision["extension_level"])
    level_name, locus = LEVELS[level]
    audit = source["audit"]
    if label == "clear":
        conclusion = "Four distinct and chronologically ordered stages survive within one coherent process."
    elif label == "potential":
        conclusion = (
            "The case is lower-level or has an incomplete higher-level chain and therefore does not "
            "meet the precision threshold for clear."
        )
    else:
        conclusion = (
            "The apparent process is impersonal, fictional, fragmented, or otherwise lacks defensible "
            "evidence of extension beyond L0."
        )
    return {
        "conversation_id": decision["conversation_id"],
        "dataset": audit["dataset"],
        "source_id": audit["source_id"],
        "source_reference": {
            "corpus_file": str(CORPUS),
            "automated_audit_file": str(AUDIT),
            "automated_label": audit["recursive_extension"],
            "automated_level": audit["extension_level"],
            "automated_audit_line": audit["_audit_line"],
            "manual_label": label,
            "manual_review_cutoff": cutoff,
        },
        "assessment": {
            "classification": label,
            "consumption_related": True,
            "context": decision["context"],
            "extension_level": level,
            "extension_level_name": level_name,
            "extension_locus": locus,
            "qualitative_review_priority": "high" if label == "clear" or level >= 3 else "medium",
            "confidence": "moderate" if decision["confidence"] == "medium" else decision["confidence"],
        },
        "brief_summary": decision["summary"],
        "evidence_chain": {
            stage: _stage_record(stage, decision["evidence"][stage]) for stage in STAGES
        },
        "reasons_for_assessment": [
            "The complete normalized conversation was reviewed as one individual unit, including all topic segments.",
            "The strongest coherent process was distinguished from unrelated later topics and from mere artifact iteration.",
            conclusion,
        ],
        "comments": [
            f"Frozen-boundary one-by-one full-conversation adjudication at automated cutoff {cutoff}; manual classification overrides the automated label for substantive reporting.",
            "Occupational, educational, entrepreneurial, creative, relational, personal, and health AI use was treated as consumption rather than excluded by domain.",
            "The full transcript remains in the normalized corpus; sensitive text is not unnecessarily duplicated here.",
            decision["boundary"],
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pending", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--audit-cutoff", type=int, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    pending = _read_jsonl(args.pending)
    decisions = _read_jsonl(args.decisions)
    sources = {item["audit"]["id"]: item for item in pending}
    decision_ids = [item["conversation_id"] for item in decisions]
    if len(decision_ids) != len(set(decision_ids)):
        raise SystemExit("Duplicate conversation IDs in staged decisions")
    if set(decision_ids) != set(sources):
        raise SystemExit("Staged decisions and pending source IDs do not match exactly")

    existing: dict[str, str] = {}
    for label, path in LEDGERS.items():
        for record in _read_jsonl(path):
            cid = record["conversation_id"]
            if cid in existing:
                raise SystemExit(f"Canonical duplicate {cid} in {existing[cid]} and {label}")
            existing[cid] = label
    overlap = sorted(set(decision_ids) & set(existing))
    if overlap:
        raise SystemExit(f"Refusing to append {len(overlap)} already canonical IDs: {overlap[:5]}")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision in decisions:
        label = decision["classification"]
        level = int(decision["extension_level"])
        if label not in LEDGERS or level not in LEVELS:
            raise SystemExit(f"Invalid label/level for {decision['conversation_id']}")
        if (label == "clear" and level < 3) or (label == "none" and level != 0):
            raise SystemExit(f"Inconsistent label/level for {decision['conversation_id']}")
        grouped[label].append(_canonical(decision, sources[decision["conversation_id"]], args.audit_cutoff))

    print(json.dumps({label: len(grouped[label]) for label in LEDGERS}, sort_keys=True))
    if args.dry_run:
        return
    for label, path in LEDGERS.items():
        with path.open("a", encoding="utf-8") as handle:
            for record in grouped[label]:
                handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())


if __name__ == "__main__":
    main()
