---
type: Schema Reference
title: Audit Output Contract
description: Compact Gemma response keys and normalized JSONL record structure for the v5 audit.
tags: [json, schema, output, audit]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: stable
sources:
  - id: audit-script
    resource: ../../audit_long_conversations_gemma.py
    title: FIRST_SCHEMA, FOLLOW_SCHEMA, and normalization implementation
---

# Model response keys

| Key | Type | Meaning |
|---|---|---|
| `c` | enum | Consumer relevance: `yes`, `no`, `uncertain`. |
| `k` | enum | Primary context. |
| `g` | enum | Highest extension locus. |
| `h` | enum | Anchor strength: `absent`, `weak`, `strong`. |
| `he` | string | Best user-turn anchor evidence. |
| `e` | boolean | Externalization detected. |
| `a`, `ae` | boolean, string | AI reflection and best assistant-turn evidence. |
| `u`, `ue` | boolean, string | User uptake and best user-turn evidence. |
| `x`, `xe` | boolean, string | Recursive re-entry and best user-turn evidence. |
| `d` | boolean | Delegation tied to the anchor. |
| `z` | boolean | Artifact recursion. |
| `r` | enum | Model label: `none`, `potential`, `clear`. |
| `q` | enum | Review priority: `yes`, `maybe`, `no`. |

Continuation responses add `f`: `confirm`, `reject`, or `mixed`.

# Enumerations

Extension loci map to levels as follows: `none`→0, `capability`→1, `owned_project`→2, `self_representation`→3, `self_assessment`→4, and `possible_self_enactment`→5.

Context values are `personal`, `relational`, `educational`, `entrepreneurial`, `occupational`, `creative`, `health`, `mixed`, and `other`.

# Normalized JSONL record

The script emits identifying metadata; consumption and context; normalized level and locus; stage booleans; stage evidence; any validated clear chain; recursive and review labels; and an `audit` object containing classifier, rubric version, raw model labels, consistency adjustment, context/chunk information, timing, and token counts.

# Output economy

The first response is capped at 288 generated tokens and later responses at 320. Schema-constrained compact JSON minimizes generation time while preserving one auditable line per conversation.
