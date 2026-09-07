---
type: Data Pipeline
title: Automated Gemma V5 Audit
description: Exhaustive local classification workflow using Gemma 4 26B through Ollama with four parallel workers.
tags: [gemma, ollama, classification, jsonl, automation]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: draft
sources:
  - id: audit-script
    resource: ../../audit_long_conversations_gemma.py
    title: Gemma v5 audit implementation
  - id: audit-output
    resource: ../../classification/gemma4_26b_a4b_audit_v5_extension_levels.jsonl
    title: Live v5 audit output
---

# Runtime

The active audit uses local Ollama model `gemma4:26b`, four worker threads, four 131,072-token contexts, temperature 0, seed `20260824`, thinking disabled, and schema-constrained JSON output. Requests keep the model alive for 30 minutes, allow 1,800 seconds, and retry up to three times with exponential backoff.[^audit-script]

# Pipeline

1. Read each normalized conversation not already present in the output.
2. Render stable user and assistant turn labels.
3. Apply the [v5 prompt](/prompts/v5-audit-prompt.md) using the [chunking protocol](/prompts/chunking-and-continuation.md).
4. Validate evidence roles and existence.
5. Normalize levels, stages, recursive labels, and review priority according to the [output contract](/prompts/output-contract.md).
6. Append one compact JSON object per completed conversation and flush immediately.
7. Append request failures to a separate error JSONL for later retry.

# Resumption

At startup, the script reads completed IDs from the output and skips them. This makes interrupted runs resumable, although appending from two concurrent instances to the same output is unsupported.

# Snapshot

At 2026-08-24T22:37:07Z, the live file contained 149 completed records: 123 `none`, 25 `potential`, and one automated `clear`, with zero recorded errors. The single automated clear had already been manually downgraded, so automated counts must not be presented as adjudicated findings. The run continues; this snapshot will become stale.

# Resource envelope

During the run, the Ollama runner has used approximately 44 GB resident memory. The agreed operating ceiling is 60 GB on a 96 GB host.

[^audit-script]: Gemma v5 audit implementation
