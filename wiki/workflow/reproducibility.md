---
type: How-to
title: Reproducing the V5 Audit
description: Files, parameters, and invocation needed to reconstruct the normalized corpus and resume the v5 audit.
tags: [reproducibility, command, audit, corpus]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: draft
sources:
  - id: preparation-script
    resource: ../../scripts/prepare_long_conversations.py
    title: Corpus preparation implementation
  - id: audit-script
    resource: ../../scripts/audit_long_conversations_gemma.py
    title: Gemma v5 audit implementation
---

# Prerequisites

Use Python 3.10 or newer and install the pinned Python dependency with `python -m pip install -r requirements.txt`. Ollama 0.20 or newer must serve the v5 `gemma4:26b` model build at `http://127.0.0.1:11434`.

# Download the source releases

```bash
python scripts/download_datasets.py --list
python scripts/download_datasets.py
```

The raw files are pinned by Hugging Face revision and downloaded under `raw/`. The RealUser input is the public 600-conversation preview, not the unavailable full corpus. LMSYS may require prior acceptance of its terms and a token supplied through `HF_EPHEMERAL_TOKEN` or `HF_TOKEN`.

# Build the normalized corpus

```bash
python scripts/prepare_long_conversations.py
```

# Run or resume the audit

```bash
python scripts/audit_long_conversations_gemma.py \
  --model gemma4:26b \
  --workers 4 \
  --schedule length
```

The default output and error paths are documented in [source files](/references/source-files.md). Existing completed IDs are skipped. `length` is the default and deterministically schedules the longest normalized records first; use `--schedule source` to reproduce the earlier corpus order.

# Targeted calibration

Use repeatable `--id CONVERSATION_ID` arguments and separate `--output` and `--errors` paths when testing cases. Do not reuse the production output for prompt experiments.

# Preserve a resume checkpoint

```bash
python scripts/snapshot_resume_state.py
```

This captures complete JSON lines from the live production output and the three canonical manual-adjudication files, records SHA-256 checksums, and includes the exact Gemma model identity lock. The resulting `resume_state/*.tar.gz` archive is record-level research data, is ignored by Git, and must not be published through the public repository. The model blob itself must be retained or reacquired separately and verified against the lock.

# Generate the current process diagram

```bash
python scripts/generate_process_diagram.py
```

The default output is `results/prisma_process_diagram.md`. Use `--output PATH` to write elsewhere or `--stdout` to also print the Mermaid Markdown. Use `--audit-cutoff N` to reproduce a frozen reporting boundary while the append-only audit continues; omission reads every currently committed audit record. Manual diagram counts are restricted to conversations labeled `clear` or `potential` by the selected automated v5 snapshot, so deliberately reviewed calibration negatives are excluded.

# Generate the paper and evidence appendices

Pause the audit if a frozen reporting checkpoint is required. Translate all
non-English clear L3–L5 evidence with the full local 26B production model, then
generate the manuscript and appendices:

```bash
python scripts/translate_appendix_conversations.py
python scripts/generate_paper.py
```

The generator reads the current append-only audit, error ledger, manual evidence,
manifest, normalized corpus, and translation cache. It writes
`paper/draft.docx`, `paper/appendix-l5.docx`, `paper/appendix-l4.docx`, and
`paper/appendix-l3.docx`. These generated artifacts include research data and
are ignored by Git.

# Reproducibility limits

Deterministic temperature and seed reduce sampling variation but do not guarantee bit-identical results across Ollama, model quantization, runtime, hardware, or model-build changes. The Git repository excludes raw and normalized conversations but tracks the production automated checkpoint and canonical manual adjudications so completed computational and qualitative work can be resumed directly.
