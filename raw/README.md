# Raw source data

This directory is populated by `scripts/download_datasets.py` and is ignored by Git.
The expected layout is:

```text
raw/
├── wildchat/          # 14 Parquet shards
├── lmsys/             # 6 Parquet shards
├── thoughttrace/      # ThoughtTrace.jsonl
└── realuser_preview/  # ChatGPT-RealUser-2.2M-preview.csv
```

Run `python scripts/download_datasets.py --list` to inspect the pinned revisions and
expected sizes without downloading anything.
