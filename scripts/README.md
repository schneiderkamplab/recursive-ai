# Research Scripts

The project root is reserved for orientation, policy, and dependency files.
Executable research utilities live here.

## Current workflow

- `download_datasets.py` downloads pinned public source releases.
- `analyze_turn_distributions.py` profiles the raw datasets.
- `prepare_long_conversations.py` normalizes and selects the 10-by-10 corpus.
- `audit_long_conversations_gemma.py` runs or resumes the production v5 audit.
- `generate_process_diagram.py` derives the current screening and review flow.
- `snapshot_resume_state.py` creates a private integrity-checked checkpoint.
- `translate_appendix_conversations.py` builds a locked, resumable 26B Gemma
  JSONL translation cache for non-English clear L3 through L5 evidence. New
  records append; changed records trigger an atomic compacting rewrite.
- `generate_paper.py` creates the live manuscript, figures, and separate L3,
  L4, and L5 appendices. It incrementally caches conversation-level Word XML,
  skips unchanged appendix outputs, and selectively rebuilds invalidated cases.

## Historical instruments

`classify_long_conversations_gemma.py` and
`screen_long_conversations_gemma.py` preserve earlier instrument development.
Their outputs must not be merged with v5 results as if they used one measure.

Run scripts from the project root so documented relative commands and generated
paths remain easy to compare. Every script resolves its inputs and outputs from
the project directory rather than from the caller's current directory.
