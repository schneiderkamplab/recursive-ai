# Prompts

* [V5 audit prompt](v5-audit-prompt.md) - Exact rubric supplied to Gemma 4 26B.
* [Output contract](output-contract.md) - Compact model keys, normalized JSONL fields, and consistency rules.
* [Chunking and continuation](chunking-and-continuation.md) - How conversations exceeding the context budget are assessed progressively.

The source of truth is [audit_long_conversations_gemma.py](../../audit_long_conversations_gemma.py). If prose documentation and executable code diverge, record the discrepancy in [log.md](/log.md) and treat the run-specific script as authoritative for reproducing that run.
