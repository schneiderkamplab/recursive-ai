# Raw source data

This directory is populated by `scripts/download_datasets.py` and is ignored by Git.
The expected layout is:

```text
raw/
├── wildchat/          # 14 Parquet shards
├── lmsys/             # 6 Parquet shards
├── thoughttrace/      # ThoughtTrace.jsonl
├── realuser_preview/  # ChatGPT-RealUser-2.2M-preview.csv
├── wildchat_4_8m/     # 86 Parquet shards; expansion/overlap assessment
├── sharegpt_x/        # Streaming JSON release
├── prism/             # Conversations plus participant metadata and survey
└── sharechat/         # Five platform-specific turn-level CSV files
```

Run `python scripts/download_datasets.py --list` to inspect the pinned revisions and
expected sizes without downloading anything.
