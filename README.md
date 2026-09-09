# Recursive AI-Extended Self Audit

This repository contains the reproducible computational and qualitative method
for studying recursive self-extension in public consumer–AI conversations. It
also contains the canonical automated v5 audit and human-adjudication JSONLs so
the campaign can be resumed without repeating completed computational or human
work. It does **not** contain source transcripts, normalized conversations,
model files, or generated research artifacts.

The navigable project documentation starts at
[`wiki/index.md`](wiki/index.md). It records the construct ontology, exact v5
prompt, chunking and classification logic, human-review protocol, evidence
summaries, methodological decisions, and limitations.

## Data sources

The pipeline uses pinned releases of:

- WildChat-1M;
- LMSYS-Chat-1M;
- ThoughtTrace; and
- the public 600-conversation ChatGPT-RealUser-2.2M preview.

The v5 campaign is expanded with ShareGPT-X, PRISM Alignment, ShareChat, and
the non-overlapping portion of WildChat-4.8M. The canonical normalized corpus
contains 91,590 exact-deduplicated conversations. The original 44,142 records
remain its prefix, so their completed automated and manual results remain valid.

The unavailable full RealUser-2.2M corpus is not used. Dataset licenses, terms,
and access controls remain those of the upstream publishers. LMSYS may require
accepting its terms and supplying a Hugging Face token through the process
environment. The downloader never persists or prints that token.

## Prerequisites

- Python 3.10 or newer;
- the dependency in `requirements.txt`;
- Ollama 0.20 or newer for automated screening; and
- the `gemma4:26b` model build used by the v5 instrument (25.8B parameters,
  Q4_K_M quantization, 262,144-token native context).

Create an isolated Python environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Reproduce the corpus and audit

1. Inspect and download the pinned source inventory:

   ```bash
   python scripts/download_datasets.py --list
   python scripts/download_datasets.py
   ```

2. Compute the complete source turn distributions:

   ```bash
   python scripts/analyze_turn_distributions.py
   ```

3. Normalize records and retain conversations with at least ten user and ten
   assistant messages:

   ```bash
   python scripts/prepare_long_conversations.py
   ```

   To assess the successor WildChat release and expand the canonical v5 corpus:

   ```bash
   python scripts/download_datasets.py --dataset sharegpt-x --dataset prism --dataset sharechat --workers 4
   python scripts/download_datasets.py --dataset wildchat-4.8m --workers 4
   python scripts/assess_wildchat_expansion.py
   python scripts/prepare_corpus_expansion.py
   ```

4. Start Ollama with the required model available, then run the v5 audit:

   ```bash
   python scripts/audit_long_conversations_gemma.py --model gemma4:26b --workers 4
   ```

   The production configuration uses four parallel 131,072-token contexts,
   temperature 0, seed `20260824`, and compact schema-constrained JSON. It was
   operated under a 60 GB memory ceiling. Do not run two processes that append
   to the same output file.

   The default command resumes the same append-only v5 JSONL. It recognizes the
   44,142 completed IDs and processes only pending additions. A genuinely
   alternate `--input` still requires explicit separate output and error paths.

5. Human reviewers adjudicate all automated `clear` and `potential` candidates
   according to [`wiki/workflow/manual-review.md`](wiki/workflow/manual-review.md).
   Automated output alone does not reproduce the qualitative findings.

6. After manual evidence files exist, generate a current PRISMA-style flow:

   ```bash
   python scripts/generate_process_diagram.py
   ```

All generated paths are documented in `raw/README.md`,
`classification/README.md`, and `results/README.md`. They are intentionally
ignored by Git.

## Generate the manuscript and evidence appendices

The paper generator reads the live audit and canonical manual-review JSONLs at
runtime, so campaign counts in the manuscript reflect the exact checkpoint used
for generation. Complete clear L3, L4, and L5 conversations are written to
separate appendices. Missing non-English conversations are automatically
translated locally with the same 26B Gemma model used by the audit. Translation
requests join the existing Ollama queue without stopping the audit or unloading
the model. The ignored JSONL cache appends newly translated conversations,
atomically rewrites the file when an existing translation changes, and uses
advisory read/write and single-translator locks.

```bash
python scripts/generate_paper.py --audit-cutoff 38289
```

Outputs are `paper/draft.docx`, `paper/appendix-l5.docx`,
`paper/appendix-l4.docx`, and `paper/appendix-l3.docx`. Use `--draft-only` to
regenerate only the manuscript or repeat `--appendix-level LEVEL` to select one
or more of levels 3, 4, and 5. Appendix generation is incremental by default:
unchanged complete appendices are left untouched, while changed documents reuse
cached case fragments and rebuild only new or modified cases. Use
`--rebuild-appendix-cache` after deliberately changing appendix formatting.
Use `--no-auto-translate` to retain fail-fast behavior when Ollama is
intentionally unavailable.
Generated Word files and their local cache contain source transcripts and
therefore stay outside Git.

## Preserve resumable research state

The tracked automated audit checkpoint and three canonical human-adjudication
files are costly or impossible to reconstruct mechanically. They can also be
captured in a local, Git-ignored archive with complete-line validation and
SHA-256 checksums:

```bash
python scripts/snapshot_resume_state.py
```

The archive is written under `resume_state/`, marked as record-level research
data, and must be transferred only through an appropriately governed private
storage channel. It also includes the tracked Gemma build identity lock at
`model-locks/gemma4-26b-ollama.lock.json`; the approximately 18 GB model blob
itself remains outside Git.

## Data and credential policy

Public conversation corpora can contain personal or sensitive material. Do not
commit transcripts. The only tracked record-level derivatives are the named v5
automated audit, error ledger, and three canonical manual-adjudication JSONLs in
`classification/`. Do not commit other classification runs, Hugging Face tokens,
API keys, model blobs, runtime logs, or temporary review files. Use conversation
IDs instead of usernames and avoid unnecessary quotation in research
documentation.

## Reproducibility limits

Pinned source revisions and deterministic inference settings improve
reproducibility but cannot guarantee bit-identical output across different
Ollama versions, quantizations, model builds, or hardware. Manual adjudication
is an interpretive research stage and must be documented separately from the
automated retrieval instrument.
