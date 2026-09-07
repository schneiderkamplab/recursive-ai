---
type: Reference
title: Canonical Project Files
description: Navigable inventory of the code, data, outputs, and evidence underlying the recursive AI-extension audit.
tags: [reference, provenance, files, reproducibility]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: stable
---

# Executable methods

* [download_datasets.py](../../scripts/download_datasets.py) - Downloads all four public source releases at pinned Hugging Face revisions, resumes partial transfers, and verifies expected byte sizes without persisting credentials.
* [prepare_long_conversations.py](../../scripts/prepare_long_conversations.py) - Normalizes source corpora and selects ≥10×10 conversations.
* [audit_long_conversations_gemma.py](../../scripts/audit_long_conversations_gemma.py) - Live v5 exhaustive audit, exact rubric, schemas, chunking, and post-processing.
* [generate_process_diagram.py](../../scripts/generate_process_diagram.py) - Generates a current PRISMA-style Mermaid flow from the corpus, audit, errors, and manual-evidence files while excluding manual calibration records that were not automated candidates.
* [apply_manual_decisions.py](../../scripts/apply_manual_decisions.py) - Validates a frozen pending-candidate set against staged one-by-one decisions and safely appends canonical records while refusing duplicate IDs or inconsistent label-level pairs.
* [snapshot_resume_state.py](../../scripts/snapshot_resume_state.py) - Creates an integrity-checked, Git-ignored local archive of the production checkpoint, error ledger, canonical manual adjudications, and model identity lock.
* [screen_long_conversations_gemma.py](../../scripts/screen_long_conversations_gemma.py) - Earlier short-context screening implementation; not the v5 production method.
* [translate_appendix_conversations.py](../../scripts/translate_appendix_conversations.py) - Resumably translates every non-English manually clear L3–L5 conversation with local Gemma 4 26B under a strict full-fidelity prompt.
* [generate_paper.py](../../scripts/generate_paper.py) - Generates a campaign-state-aware manuscript, its process figure, and separate complete clear L3, L4, and L5 evidence appendices.

# Model identity

* [gemma4-26b-ollama.lock.json](../../model-locks/gemma4-26b-ollama.lock.json) - Exact manifest and layer digests for the local Gemma build used by v5. The model blob is not stored in Git.

# Corpus

Generated corpus files are documented in [classification/README.md](../../classification/README.md) and intentionally excluded from Git.

* `long_conversations_manifest.json` - Counts and character totals.
* `long_conversations_10x10.jsonl.gz` - Normalized transcripts.

# Production output

* `gemma4_26b_a4b_audit_v5_extension_levels.jsonl` - Append-only live audit output.
* `gemma4_26b_a4b_audit_v5_extension_levels_errors.jsonl` - Failures preserved for retry.
* `results/prisma_process_diagram.md` - Regenerable current-state screening and review flow.
* `results/prisma_process_diagram.svg` and `results/prisma_process_diagram.png` - Rendered versions of the current flow.
* `paper/campaign_screening_process.png` - Compact manuscript-ready campaign flow generated from the same canonical state.

# Manual evidence

* `manually_reviewed_clear_examples.jsonl` - Confirmed clear cases.
* `manually_reviewed_potential_examples.jsonl` - Lower-level and incomplete-chain candidates.
* `manually_reviewed_none_examples.jsonl` - Hard negatives.

The production v5 audit, error ledger, and three canonical manual-evidence files are tracked to preserve campaign continuity. Raw and normalized transcripts, historical classifier outputs, calibrations, and runtime records remain excluded.

# Superseded calibration outputs

Files whose names contain `superseded`, earlier rubric versions, and calibration sets remain useful for prompt-development history but must not be combined with v5 production labels as if they share one measurement instrument.
