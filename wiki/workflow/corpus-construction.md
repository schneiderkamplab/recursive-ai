---
type: Data Pipeline
title: Long-Conversation Corpus Construction
description: Normalization and inclusion pipeline producing 44,142 conversations with at least ten user and ten assistant messages.
tags: [corpus, data-pipeline, wildchat, lmsys, thoughttrace, realuser]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: stable
sources:
  - id: preparation-script
    resource: ../../prepare_long_conversations.py
    title: Corpus preparation implementation
  - id: corpus-manifest
    resource: ../../classification/long_conversations_manifest.json
    title: Generated corpus manifest
---

# Inclusion rule

A record is included when the source reports at least ten exchanges and normalization yields user and assistant messages. The resulting research corpus is described as ≥10 user + ≥10 assistant turns (`10x10`).[^preparation-script]

# Reproducible download

The four publicly obtainable source releases are downloaded by [download_datasets.py](../../download_datasets.py) into the exact `raw/` layout consumed by the preparation script. Downloads are pinned to full Hugging Face commit revisions, resume from `.part` files, and verify the expected byte size before atomic completion. The script uses Python's standard library; access tokens, when required, are read only from `HF_EPHEMERAL_TOKEN` or `HF_TOKEN`.

The RealUser source is the public 600-conversation preview, not the unavailable full 2.2-million-conversation corpus. LMSYS access can depend on the current upstream access policy and the user's acceptance of its dataset terms.

# Sources and counts

| Dataset | Conversations | Characters | Maximum characters |
|---|---:|---:|---:|
| WildChat-1M | 24,498 | 524,899,120 | 546,717 |
| LMSYS-Chat-1M | 19,556 | 334,004,117 | 6,640,848 |
| ThoughtTrace | 66 | 1,412,430 | 77,565 |
| ChatGPT-RealUser-2.2M preview | 22 | 614,347 | 85,276 |
| **Total** | **44,142** | **860,930,014** | — |

These are corpus-build counts, not estimates for the full RealUser dataset.[^corpus-manifest]

# Normalization

Only `user` and `assistant` messages are retained. Content is coerced to strings. Each normalized record contains dataset, source identifier, exchange and turn counts, character count, messages, and available source metadata such as model, language, source file, or user ID.

# Stable identifier

The audit ID is the first 24 hexadecimal characters of SHA-256 over `dataset + NUL + source_id`. It permits cross-file joins without replacing the source identifier.

# Output

The normalized corpus is [long_conversations_10x10.jsonl.gz](../../classification/long_conversations_10x10.jsonl.gz); summary metadata is [long_conversations_manifest.json](../../classification/long_conversations_manifest.json).

[^preparation-script]: Corpus preparation implementation
[^corpus-manifest]: Generated corpus manifest
