---
type: How-to
title: Generating the Paper and Evidence Appendices
description: Reproducible creation of the live manuscript and complete clear L3 through L5 conversation appendices.
tags: [paper, appendix, translation, docx, reproducibility]
generated: { by: codex/gpt-5, at: "2026-09-08T00:00:00Z" }
status: draft
sources:
  - id: paper-generator
    resource: ../../scripts/generate_paper.py
    title: Paper and appendix generator
  - id: translation-pipeline
    resource: ../../scripts/translate_appendix_conversations.py
    title: Appendix translation pipeline
---

# Inputs and frozen campaign state

The generator reads the corpus manifest, normalized 10-by-10 corpus, append-only
v5 audit and error ledger, and all three canonical manual-evidence JSONLs. It
derives automated totals, provisional labels, candidate retrieval, pending
manual review, final manual labels, and level counts at generation time. Pass
`--audit-cutoff N` to freeze counts, candidate membership, and appendix evidence
at a fully reconciled reporting boundary while the production audit continues.

# Translation

Every non-English manually clear L3, L4, or L5 conversation is translated by the
local `gemma4:26b` model with four concurrent 32,768-token contexts, temperature
zero, and a schema requiring one English string per source item. Batches are
contiguous and conservatively capped at 4,000 source characters and eight items,
with individual pieces capped at 3,000 characters. The prompt
requires complete translation without summarizing, censoring, explaining, or
improving the research data. Source turns confidently detected as already
English bypass generation and are copied exactly.

Paper generation ensures these translations automatically for the clear cases
selected by its requested audit cutoff and appendix levels. The audit and
translator use the same `gemma4:26b` model and port-11434 Ollama service.
Translation requests therefore enter Ollama's queue alongside audit requests
and consume only the configured four parallel contexts; generation neither
stops the audit nor unloads or duplicates the resident model. Audit throughput
may temporarily decrease while translations occupy contexts. Use
`--no-auto-translate` only when Ollama is intentionally unavailable and missing
translations should cause a fail-fast appendix error.

Single-item retries use a plain-text response with explicit source-data delimiters,
which prevents the model from treating embedded requests as instructions or
echoing the batch schema. The pipeline rejects implausible translation expansion
and schema-commentary artifacts and retries failed records from the resumable
cache. The ignored cache is JSONL with one complete conversation record per
line. Each record contains the conversation ID, source language, model
provenance, a SHA-256 hash of the complete source-message array, and one
translation per original message. A newly completed conversation is appended
and flushed to disk. Replacing, repairing, or invalidating an existing
translation triggers an atomic full-file rewrite, which also compacts any prior
duplicate IDs. A final partial line from an interrupted append is ignored on
recovery.

A dedicated advisory data lock protects every read, append, migration, and
rewrite. Readers, including the paper generator, take a shared lock; writers
take an exclusive lock. A second nonblocking run lock prevents two translator
processes from generating the same pending work concurrently. Locks are held
only for cache access rather than during model inference, so appendix generation
can read completed translations while a long translation run continues.

The current keyed JSON cache migrates automatically and losslessly to JSONL on
the first translator invocation; the legacy JSON remains as a local safety copy
but is ignored once JSONL exists. The paper generator rejects stale hashes,
wrong turn counts, empty translated turns, and records not produced by a 26B
model. Translation failures are written to a separate ignored JSONL and remain
eligible for a later resumable run.

# Outputs

`scripts/generate_paper.py` creates the following ignored local artifacts:

* `paper/draft.docx`, including the frozen campaign-process figure, current
  counts, findings, level table, and theoretical model;
* `paper/appendix-l5.docx` for all manually clear L5 conversations;
* `paper/appendix-l4.docx` for all manually clear L4 conversations; and
* `paper/appendix-l3.docx` for all manually clear L3 conversations.

Each appendix case starts with its manual summary and the contributing turns for
externalization, AI reflection, user uptake, and recursive re-entry. English
transcripts use chat-style bubbles. Non-English transcripts use a two-column
original-and-English table. Two XML-forbidden source control characters in the
current evidence base are represented by explicit Unicode code-point markers
rather than silently deleted.

The original-language column uses an explicit broad-Unicode typeface so CJK
and other non-Latin source text remains visible in Word and rendered QA.

# Incremental appendix generation

Appendix generation is incremental at both the document and conversation
levels. For each clear conversation, the generator computes a SHA-256
fingerprint over the normalized source record, canonical manual adjudication,
validated translation when present, and an explicit fragment-format version.
It stores the resulting relationship-free WordprocessingML body fragment under
the ignored `paper/.appendix-cache/` directory. New or changed cases alone are
rendered into new fragments; unchanged fragments are reused during assembly.

Case headings and ordinal numbers are added during assembly rather than stored
inside fragments. A newly inserted case can therefore change later case numbers
without invalidating later transcript fragments. Removed cases disappear and
level changes move cases automatically because each output is assembled from
the current canonical clear-case membership.

Each level also has a manifest containing its ordered case fingerprints and the
SHA-256 hash of the completed DOCX. If both the manifest and DOCX are current,
the generator leaves the entire appendix untouched. If any case changed, it
reassembles the DOCX from cached fragments and rebuilds only invalid fragments.
Writes to fragments and manifests are atomic. Use `--rebuild-appendix-cache`
when appendix rendering code or formatting is deliberately changed; increment
`APPENDIX_FRAGMENT_FORMAT_VERSION` whenever such a change must invalidate all
existing fragments. Multiple requested levels share one normalized-corpus scan
and one translation-cache load.

# Rendering and verification

Generated Word documents are rendered to page images before delivery. Visual QA
checks title hierarchy, chat and bilingual layouts, table splitting, figure
legibility, page numbering, blank pages, clipping, and source-turn continuity.
The Word files contain complete public-corpus transcripts and therefore remain
outside the public Git repository.

The current local documents were generated with `--audit-cutoff 36773`. They
contain 65 clear L5, 42 clear L4, and 206 clear L3 conversations. The translation
cache contains 114 complete, validated non-English clear conversations at this
boundary. No new translation was required for this regeneration because the
latest review round added no clear case.

The verified render comprises 23 manuscript pages, 935 L5-appendix pages, 794
L4-appendix pages, and 2,693 L3-appendix pages. All 4,445 pages have consistent
dimensions, no blank page, and no content touching the render boundary.
