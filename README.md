# Recursive AI-Extended Self Audit

This repository contains the reproducible computational and qualitative method
for studying recursive self-extension in public consumer–AI conversations. It
does **not** contain source transcripts, normalized conversations, automated
classifications, manual evidence records, model files, or generated research
artifacts.

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
   python download_datasets.py --list
   python download_datasets.py
   ```

2. Compute the complete source turn distributions:

   ```bash
   python analyze_turn_distributions.py
   ```

3. Normalize records and retain conversations with at least ten user and ten
   assistant messages:

   ```bash
   python prepare_long_conversations.py
   ```

4. Start Ollama with the required model available, then run the v5 audit:

   ```bash
   python audit_long_conversations_gemma.py --model gemma4:26b --workers 4
   ```

   The production configuration uses four parallel 131,072-token contexts,
   temperature 0, seed `20260824`, and compact schema-constrained JSON. It was
   operated under a 60 GB memory ceiling. Do not run two processes that append
   to the same output file.

5. Human reviewers adjudicate all automated `clear` and `potential` candidates
   according to [`wiki/workflow/manual-review.md`](wiki/workflow/manual-review.md).
   Automated output alone does not reproduce the qualitative findings.

6. After manual evidence files exist, generate a current PRISMA-style flow:

   ```bash
   python generate_process_diagram.py
   ```

All generated paths are documented in `raw/README.md`,
`classification/README.md`, and `results/README.md`. They are intentionally
ignored by Git.

## Preserve resumable research state

The automated audit checkpoint and three canonical human-adjudication files are
costly or impossible to reconstruct mechanically. Capture them in a local,
Git-ignored archive with complete-line validation and SHA-256 checksums:

```bash
python snapshot_resume_state.py
```

The archive is written under `resume_state/`, marked as record-level research
data, and must be transferred only through an appropriately governed private
storage channel. It also includes the tracked Gemma build identity lock at
`model-locks/gemma4-26b-ollama.lock.json`; the approximately 18 GB model blob
itself remains outside Git.

## Data and credential policy

Public conversation corpora can contain personal or sensitive material. Do not
commit transcripts or record-level derivatives. Do not commit Hugging Face
tokens, API keys, model blobs, runtime logs, or temporary review files. Use
conversation IDs instead of usernames and avoid unnecessary quotation in
research documentation.

## Reproducibility limits

Pinned source revisions and deterministic inference settings improve
reproducibility but cannot guarantee bit-identical output across different
Ollama versions, quantizations, model builds, or hardware. Manual adjudication
is an interpretive research stage and must be documented separately from the
automated retrieval instrument.
