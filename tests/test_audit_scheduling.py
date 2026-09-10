from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_long_conversations_gemma.py"
SPEC = importlib.util.spec_from_file_location("audit_long_conversations_gemma", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def _record(identifier: str, dataset: str, characters: int) -> dict:
    return {"id": identifier, "dataset": dataset, "characters": characters}


def test_length_schedule_orders_largest_first_with_deterministic_ties() -> None:
    records = [
        _record("z", "beta", 20),
        _record("b", "alpha", 10),
        _record("a", "alpha", 10),
        _record("a", "beta", 10),
    ]

    scheduled = AUDIT._scheduled(records, "length")

    observed = [
        (record["characters"], record["dataset"], record["id"])
        for record in scheduled
    ]
    assert observed == [
        (20, "beta", "z"),
        (10, "alpha", "a"),
        (10, "alpha", "b"),
        (10, "beta", "a"),
    ]
    assert records[0]["id"] == "z"


def test_source_schedule_preserves_input_order_and_identity() -> None:
    records = [_record("b", "source", 20), _record("a", "source", 10)]

    assert AUDIT._scheduled(records, "source") is records
