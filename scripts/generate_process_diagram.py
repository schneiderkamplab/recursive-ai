#!/usr/bin/env python3
"""Generate a PRISMA-style Mermaid diagram from the current campaign state."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION = ROOT / "classification"
RESULTS = ROOT / "results"

TURN_DISTRIBUTION = RESULTS / "turn_distribution.json"
CORPUS_MANIFEST = CLASSIFICATION / "long_conversations_manifest.json"
AUTOMATED_AUDIT = CLASSIFICATION / "gemma4_26b_a4b_audit_v5_extension_levels.jsonl"
AUTOMATED_ERRORS = CLASSIFICATION / "gemma4_26b_a4b_audit_v5_extension_levels_errors.jsonl"
MANUAL_FILES = {
    "clear": CLASSIFICATION / "manually_reviewed_clear_examples.jsonl",
    "potential": CLASSIFICATION / "manually_reviewed_potential_examples.jsonl",
    "none": CLASSIFICATION / "manually_reviewed_none_examples.jsonl",
}
DEFAULT_OUTPUT = RESULTS / "prisma_process_diagram.md"

DATASET_ORDER = (
    "WildChat-1M",
    "LMSYS-Chat-1M",
    "ThoughtTrace",
    "ChatGPT-RealUser-2.2M-preview",
)
DATASET_LABELS = {
    "WildChat-1M": "WildChat",
    "LMSYS-Chat-1M": "LMSYS",
    "ThoughtTrace": "ThoughtTrace",
    "ChatGPT-RealUser-2.2M-preview": "RealUser preview",
}
LEVEL_LABELS = {
    0: "L0 instrumental",
    1: "L1 capability",
    2: "L2 project/possession",
    3: "L3 representation",
    4: "L4 reflexivity",
    5: "L5 enacted/possible self",
}


def _read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _read_jsonl(path: Path, *, allow_trailing_partial: bool = False) -> list[dict]:
    records = []
    if not path.exists():
        return records
    with path.open(encoding="utf-8") as handle:
        lines = handle.readlines()
        for line_number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                if allow_trailing_partial and line_number == len(lines) and not line.endswith("\n"):
                    # The production audit appends and flushes one JSON line at a
                    # time. A concurrent snapshot may observe the last write in
                    # progress; excluding that incomplete record is consistent
                    # with reporting the last fully committed audit line.
                    continue
                raise ValueError(f"Invalid JSON in {path} at line {line_number}") from error
    return records


def _raw_counts() -> dict[str, int]:
    summaries = _read_json(TURN_DISTRIBUTION)["summaries"]
    source_counts = {item["dataset"]: int(item["total_conversations"]) for item in summaries}
    return {
        "WildChat-1M": source_counts["WildChat-1M"],
        "LMSYS-Chat-1M": source_counts["LMSYS-Chat-1M"],
        "ThoughtTrace": source_counts["ThoughtTrace"],
        "ChatGPT-RealUser-2.2M-preview": source_counts["ChatGPT-RealUser-2.2M"],
    }


def _format_source_counts(counts: dict[str, int], *, omit_zero: bool = False) -> str:
    parts = []
    for dataset in DATASET_ORDER:
        count = int(counts.get(dataset, 0))
        if omit_zero and count == 0:
            continue
        parts.append(f"{DATASET_LABELS[dataset]}: {count:,}")
    return "<br/>".join(parts) if parts else "None"


def _format_levels(counts: Counter[int], levels: tuple[int, ...]) -> str:
    return "<br/>".join(f"{LEVEL_LABELS[level]}: {counts[level]:,}" for level in levels)


def _manual_snapshot(candidate_ids: set[str]) -> tuple[Counter[str], dict[str, Counter[int]], set[str]]:
    outcomes: Counter[str] = Counter()
    levels = {label: Counter() for label in MANUAL_FILES}
    reviewed_ids: set[str] = set()

    for file_label, path in MANUAL_FILES.items():
        for record in _read_jsonl(path):
            conversation_id = record["conversation_id"]

            # Deliberately exclude calibration or other manually reviewed records
            # that the automated v5 audit did not classify as clear/potential.
            if conversation_id not in candidate_ids:
                continue
            if conversation_id in reviewed_ids:
                raise ValueError(f"Duplicate candidate manual review: {conversation_id}")

            assessment = record["assessment"]
            manual_label = assessment["classification"]
            if manual_label != file_label:
                raise ValueError(
                    f"Manual label/file mismatch for {conversation_id}: "
                    f"{manual_label!r} in {path.name}"
                )
            reviewed_ids.add(conversation_id)
            outcomes[manual_label] += 1
            levels[manual_label][int(assessment["extension_level"])] += 1

    return outcomes, levels, reviewed_ids


def _snapshot(*, audit_cutoff: int | None = None) -> dict:
    raw = _raw_counts()
    manifest = _read_json(CORPUS_MANIFEST)
    included = {dataset: int(manifest["counts"][dataset]) for dataset in DATASET_ORDER}
    excluded = {dataset: raw[dataset] - included[dataset] for dataset in DATASET_ORDER}

    automated = _read_jsonl(AUTOMATED_AUDIT, allow_trailing_partial=True)
    if audit_cutoff is not None:
        if audit_cutoff < 0:
            raise ValueError("audit cutoff must be nonnegative")
        if audit_cutoff > len(automated):
            raise ValueError(
                f"audit cutoff {audit_cutoff:,} exceeds {len(automated):,} committed records"
            )
        automated = automated[:audit_cutoff]
    automated_by_source = Counter(item["dataset"] for item in automated)
    recursive_counts = Counter(item["recursive_extension"] for item in automated)
    candidate_ids = {
        item["id"] for item in automated if item["recursive_extension"] in {"clear", "potential"}
    }
    if len(candidate_ids) != recursive_counts["clear"] + recursive_counts["potential"]:
        raise ValueError("Duplicate automated candidate IDs detected")

    not_audited = {
        dataset: included[dataset] - automated_by_source[dataset] for dataset in DATASET_ORDER
    }
    if any(value < 0 for value in not_audited.values()):
        raise ValueError("Automated audit count exceeds the normalized corpus manifest")

    manual_outcomes, manual_levels, reviewed_ids = _manual_snapshot(candidate_ids)
    unreviewed_ids = candidate_ids - reviewed_ids
    error_count = len(_read_jsonl(AUTOMATED_ERRORS, allow_trailing_partial=True))

    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "raw": raw,
        "raw_total": sum(raw.values()),
        "excluded": excluded,
        "excluded_total": sum(excluded.values()),
        "included": included,
        "included_total": int(manifest["total_conversations"]),
        "automated_total": len(automated),
        "automated_by_source": dict(automated_by_source),
        "not_audited": not_audited,
        "not_audited_total": sum(not_audited.values()),
        "automated_none": len(automated) - len(candidate_ids),
        "automated_clear": recursive_counts["clear"],
        "automated_potential": recursive_counts["potential"],
        "candidate_total": len(candidate_ids),
        "error_count": error_count,
        "manual_outcomes": manual_outcomes,
        "manual_levels": manual_levels,
        "manual_total": len(reviewed_ids),
        "manual_pending": len(unreviewed_ids),
    }


def _diagram(snapshot: dict) -> str:
    manual_outcomes: Counter[str] = snapshot["manual_outcomes"]
    manual_levels: dict[str, Counter[int]] = snapshot["manual_levels"]
    reviewed_total = snapshot["manual_total"]

    lines = [
        "# Consumer–AI Corpus Screening and Review Flow",
        "",
        f"Snapshot generated: `{snapshot['generated_at']}`",
        "",
        "```mermaid",
        "flowchart TB",
        '    subgraph ID["IDENTIFICATION AND CORPUS CONSTRUCTION"]',
        '        A["Public conversation records collected'
        f'<br/><b>n = {snapshot["raw_total"]:,}</b><br/><br/>{_format_source_counts(snapshot["raw"])}"]',
        '        X1["Excluded: fewer than 10 user–assistant exchanges'
        f'<br/><b>n = {snapshot["excluded_total"]:,}</b>"]',
        '        B["Normalized ≥10-user + ≥10-assistant corpus'
        f'<br/><b>n = {snapshot["included_total"]:,}</b><br/><br/>{_format_source_counts(snapshot["included"])}"]',
        "        A --> B",
        "        A -.-> X1",
        "    end",
        "",
        '    subgraph AS["AUTOMATED GEMMA V5 SCREENING"]',
        '        C["Conversations audited to date'
        f'<br/><b>n = {snapshot["automated_total"]:,} / {snapshot["included_total"]:,}</b>'
        f'<br/><br/>{_format_source_counts(snapshot["automated_by_source"], omit_zero=True)}'
        f'<br/>Recorded errors: {snapshot["error_count"]:,}"]',
        '        X2["Not yet automatically audited'
        f'<br/><b>n = {snapshot["not_audited_total"]:,}</b><br/><br/>{_format_source_counts(snapshot["not_audited"], omit_zero=True)}"]',
        '        D["Automated none—not selected for candidate review'
        f'<br/><b>n = {snapshot["automated_none"]:,}</b>"]',
        '        E["Automated clear or potential candidates'
        f'<br/><b>n = {snapshot["candidate_total"]:,}</b>'
        f'<br/><br/>Potential: {snapshot["automated_potential"]:,}'
        f'<br/>Clear: {snapshot["automated_clear"]:,}"]',
        "        B --> C",
        "        B -.-> X2",
        "        C --> D",
        "        C --> E",
        "    end",
        "",
        '    subgraph MR["FULL-TRANSCRIPT MANUAL REVIEW"]',
        '        F["Automated candidates manually adjudicated'
        f'<br/><b>n = {reviewed_total:,}</b>'
        '<br/><br/>Complete conversation read'
        '<br/>Strongest coherent chain reconstructed'
        '<br/>Artifact recursion separated from self-extension"]',
        '        X3["Automated candidates awaiting manual review'
        f'<br/><b>n = {snapshot["manual_pending"]:,}</b>"]',
        "        E --> F",
        "        E -.-> X3",
        "    end",
        "",
        '    subgraph OUT["MANUALLY ADJUDICATED OUTCOMES"]',
        '        I["Clear recursive self-extension'
        f'<br/><b>n = {manual_outcomes["clear"]:,}</b><br/><br/>'
        f'{_format_levels(manual_levels["clear"], (3, 4, 5))}"]',
        '        J["Potential extension'
        f'<br/><b>n = {manual_outcomes["potential"]:,}</b><br/><br/>'
        f'{_format_levels(manual_levels["potential"], (1, 2, 3, 4, 5))}"]',
        '        K["None / hard negative'
        f'<br/><b>n = {manual_outcomes["none"]:,}</b><br/><br/>'
        f'{_format_levels(manual_levels["none"], (0,))}"]',
        "        F --> I",
        "        F --> J",
        "        F --> K",
        "    end",
        "",
        "    classDef corpus fill:#e8f1fb,stroke:#3973ac,color:#172b3a,stroke-width:1.5px;",
        "    classDef automated fill:#fff1d6,stroke:#b7791f,color:#3d2a09,stroke-width:1.5px;",
        "    classDef manual fill:#eee8f8,stroke:#7655a6,color:#291b40,stroke-width:1.5px;",
        "    classDef clear fill:#ddf4e5,stroke:#2f855a,color:#173c29,stroke-width:2px;",
        "    classDef potential fill:#fff5cc,stroke:#b88a00,color:#433400,stroke-width:1.5px;",
        "    classDef none fill:#f3e2e2,stroke:#a65353,color:#481f1f,stroke-width:1.5px;",
        "    classDef excluded fill:#f1f1f1,stroke:#777,color:#333,stroke-dasharray:5 4;",
        "",
        "    class A,B corpus;",
        "    class C,D,E automated;",
        "    class F manual;",
        "    class I clear;",
        "    class J potential;",
        "    class K none;",
        "    class X1,X2,X3 excluded;",
        "```",
        "",
        "Manual counts include only records selected by the automated v5 audit as "
        "`clear` or `potential`; calibration negatives and other manually inspected "
        "automated-none records are excluded.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Markdown output path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Also print the generated Markdown to standard output.",
    )
    parser.add_argument(
        "--audit-cutoff",
        type=int,
        help=(
            "Freeze the diagram at the first N committed automated-audit records; "
            "omit to snapshot the complete current file."
        ),
    )
    args = parser.parse_args()

    snapshot = _snapshot(audit_cutoff=args.audit_cutoff)
    rendered = _diagram(snapshot)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    if args.stdout:
        print(rendered, end="")
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "automated": snapshot["automated_total"],
                "automated_candidates": snapshot["candidate_total"],
                "manually_reviewed_candidates": snapshot["manual_total"],
                "awaiting_manual_review": snapshot["manual_pending"],
                "calibration_records_included": 0,
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
