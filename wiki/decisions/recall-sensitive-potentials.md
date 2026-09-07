---
type: Decision
title: Prefer Recall for Potential Candidates
description: Bias automated retrieval toward false positives rather than false negatives while preserving precision for clear cases.
tags: [decision, recall, precision, screening]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: stable
sources:
  - id: audit-rubric
    resource: ../../scripts/audit_long_conversations_gemma.py
    title: Gemma v5 audit rubric
---

# Decision

Use a permissive `potential` category and a restrictive `clear` category.

# Rationale

The automated model is a candidate-retrieval instrument for qualitative research. Missing an unusual mechanism is costlier than manually rejecting an overinclusive potential. However, an inflated clear set would corrupt theoretical claims and model evaluation.

# Consequence

Potential cases require human adjudication and should not be reported as confirmed prevalence estimates.
