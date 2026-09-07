---
type: Process Model
title: Recursive Extension Stages
description: Ordered evidence model for identifying recursive AI-mediated extension processes.
tags: [recursion, process, evidence-chain, coding]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: draft
sources:
  - id: audit-rubric
    resource: ../../audit_long_conversations_gemma.py
    title: Gemma v5 audit rubric and evidence validation
---

# Ordered process

```text
User externalization → AI reflection → user uptake → recursive re-entry
```

For a `clear` case, all four stages require direct, distinct, ordered turn evidence.

# 1. Externalization

A user turn supplies a strong anchor: identity, values, aspirations, history, relationships, embodied condition, capabilities, education, possible self, consequential intended action, owned possession, creative production, or owned venture/project.

An externally supplied task, fictional character, generic campaign, pasted text, or unowned hypothetical is not a strong anchor. Hidden identity must not be inferred from unusual content.

# 2. AI reflection

An assistant turn transforms that anchor into a user-grounded capability assessment, recommendation, plan, project identity, representation, or possible-self formulation. Mere compliance with an artifact request is insufficient.

# 3. User uptake

A later user turn accepts, rejects, corrects, recognizes, adopts, or substantively elaborates the AI-produced output in relation to the anchor. A generic request for more is insufficient.

# 4. Recursive re-entry

The accepted or revised AI formulation or identity-bearing project becomes material or a premise for a later request, decision, action, or self-description.

# Additional indicators

`delegation=true` when AI is asked to decide, remember, plan, judge, choose, create, speak, or represent in a capacity materially tied to the anchor.

`artifact_recursion=true` tracks iterative transformation of an artifact independently of self-extension. See [artifact recursion](/ontology/artifact-recursion.md).

# Evidence labels

The classifier uses `U1`, `U2`, … for user turns and `A1`, `A2`, … for assistant turns. Evidence roles are constrained:

| Stage | Key | Required role |
|---|---|---|
| Externalization | `he` | User |
| AI reflection | `ae` | Assistant |
| User uptake | `ue` | User |
| Recursive re-entry | `xe` | User |

The implementation validates labels against actual turns and enforces chronological ordering before granting `clear`.
