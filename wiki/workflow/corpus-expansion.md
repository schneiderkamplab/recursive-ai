---
type: Data Pipeline
title: Versioned Corpus Expansion
description: Provenance-preserving integration of four additional source releases into the canonical v5 corpus.
tags: [corpus, expansion, sharegpt-x, prism, sharechat, wildchat]
generated: { by: codex/gpt-5, at: "2026-09-09T00:00:00Z" }
status: stable
sources:
  - id: downloader
    resource: ../../scripts/download_datasets.py
    title: Pinned resumable acquisition
  - id: expansion-preparation
    resource: ../../scripts/prepare_corpus_expansion.py
    title: Expansion normalization and deduplication
  - id: wildchat-assessment
    resource: ../../scripts/assess_wildchat_expansion.py
    title: WildChat overlap assessment
---

# Relationship to v5

The additional sources expand the same v5 campaign because the prompt, schema, model, post-processing rules, and manual-review protocol are unchanged. The canonical normalized corpus now contains 91,590 conversations. Its first 44,142 records are the original completed tranche, whose automated and manual results remain unchanged; the 47,448 appended records are pending automated screening.

# Integrated sources

The pinned downloader acquires ShareGPT-X, PRISM Alignment, and ShareChat. Normalization counts actual retained `user` and `assistant` messages and requires at least ten of each.

* ShareGPT-X is streamed from its ShareGPT-format JSON array and maps `human`/`gpt` to `user`/`assistant`.
* PRISM is an experimental interaction corpus that presents multiple candidate model replies. Only the model reply marked `if_chosen: true` at each turn is retained in the realized participant path; unchosen alternatives do not count as assistant turns.
* ShareChat is streamed from five platform-specific, turn-level CSV files. Its `llm` role is normalized to `assistant`. Repeated non-contiguous URL blocks retain explicit occurrence provenance.

Exact SHA-256 hashes of normalized role/content sequences exclude transcripts already in the original four-source corpus and duplicates encountered earlier in the expansion. Source records and provenance otherwise remain distinct.

# Observed 10×10 yield

| Source | Qualifying before deduplication | Exact duplicates excluded | Included |
|---|---:|---:|---:|
| ShareGPT-X | 8,910 | 0 | 8,910 |
| PRISM Alignment | 76 | 0 | 76 |
| ShareChat | 12,721 | 40 | 12,681 |
| **Total** | **21,707** | **40** | **21,667** |

None of these exact transcripts duplicated a record in the original 44,142-conversation tranche. These counts describe corpus construction, not automated or manual classification.

# WildChat-4.8M assessment

WildChat-4.8M is assessed before integration because it is a successor release to an existing v5 source. The comparison reports both upstream `conversation_hash` overlap and exact normalized role/content overlap. Only records with at least ten actual user and ten actual assistant messages qualify. The preparation script then appends only non-overlapping records to the canonical v5 corpus.

The pinned release contains 3,199,860 conversation rows. Of these, 47,563 rows qualify as 10×10. Exactly 21,781 match the original WildChat-1M partition by both source ID and exact normalized transcript. The remaining 25,782 rows contain one duplicate, leaving **25,781 unique qualifying conversations not already covered**. The agreement between ID-based and exact-transcript comparisons provides a useful cross-check; it is not assumed in the implementation.

# Reproduction

```bash
python scripts/download_datasets.py --dataset sharegpt-x --dataset prism --dataset sharechat --workers 4
python scripts/download_datasets.py --dataset wildchat-4.8m --workers 4
python scripts/assess_wildchat_expansion.py
python scripts/prepare_long_conversations.py
python scripts/prepare_corpus_expansion.py
```

The normal preparation sequence first recreates the original four-source prefix and then atomically replaces it with the expanded canonical corpus. Rerunning the expansion step against an already-expanded corpus is idempotent: previously appended source records are discarded and reconstructed from the pinned raw releases.

The unchanged v5 instrument resumes against the expanded canonical input and existing append-only output:

```bash
python scripts/audit_long_conversations_gemma.py --model gemma4:26b --workers 4
```

The completed-ID check leaves the first 44,142 audit records untouched and selects the 47,448 new records as pending work.
