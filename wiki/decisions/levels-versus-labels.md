---
type: Decision
title: Separate Extension Level From Recursive Label
description: Code self proximity and evidential completeness as distinct analytic dimensions.
tags: [decision, ontology, labels]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: stable
sources:
  - id: audit-rubric
    resource: ../../scripts/audit_long_conversations_gemma.py
    title: Gemma v5 audit rubric
---

# Decision

Assign L0–L5 independently from `none`/`potential`/`clear`.

# Rationale

A case may exhibit strong recursive co-construction at L1 or L2 without representing the consumer's self. Conversely, a plausible L3 or L4 moment may be theoretically valuable while missing observable re-entry. A single ordinal label would confound what is being extended with how completely the process is observed.

# Consequence

Lower-level potentials become comparison cases for theorizing gradations of AI extension rather than being discarded as noise.
