---
type: Coding Standard
title: Classification and Review Labels
description: Operational rules for none, potential, clear, and qualitative-review priority.
tags: [labels, classification, qualitative-review, screening]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: draft
sources:
  - id: audit-rubric
    resource: ../../audit_long_conversations_gemma.py
    title: Gemma v5 audit rubric and post-processing
---

# Recursive-extension label

| Label | Operational rule |
|---|---|
| `clear` | L3–L5 and all four ordered stages have valid direct evidence. |
| `potential` | L1–L2 with a strong anchor plus AI reflection or delegation, or a plausible L3–L5 process with an incomplete chain. |
| `none` | No qualifying nonzero level or insufficient evidence for `potential`. |

The design intentionally preserves precision in `clear` and sensitivity in `potential`.

# Software normalization

Model output is not accepted uncritically. The script:

1. validates evidence labels and expected speaker roles;
2. requires a strong anchor for any nonzero level;
3. requires ordered evidence for `clear`;
4. downgrades internally inconsistent outputs;
5. promotes review priority from `no` to `maybe` when a non-`none` recursive label survives normalization.

# Qualitative-review label

| Label | Meaning |
|---|---|
| `yes` | Theoretically rich clear case, important level boundary, or illuminating resistance, contested personalization, authorship, delegation, identity threat, or task/self ambiguity. |
| `maybe` | Relevant ambiguity that human analysis may resolve. |
| `no` | Routine, thin, or nonqualifying case. |

# Manual adjudication

Human review may override the automated level, label, evidence chain, or theoretical construct. Both automated and manual labels are retained for auditability. See [manual review](/workflow/manual-review.md) and [evidence](/evidence/).
