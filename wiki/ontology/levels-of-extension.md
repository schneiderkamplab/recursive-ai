---
type: Taxonomy
title: Levels of Extending With AI
description: Six-level ontology distinguishing task iteration, capability, projects and possessions, representation, reflexivity, and enactment.
tags: [ontology, ai-extended-self, levels, coding-rubric]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: draft
sources:
  - id: audit-rubric
    resource: ../../audit_long_conversations_gemma.py
    title: Gemma v5 audit rubric and normalization logic
---

# Principle

Levels describe proximity to self, not quality, desirability, moral value, or intensity of AI use. The assigned level is the highest locus directly evidenced in any contiguous topic segment.

| Level | Code | Name | Defining evidence |
|---:|---|---|---|
| L0 | `none` | Instrumental task | AI completes or iterates a task or artifact without transforming an evidenced self or identity-bearing owned project. |
| L1 | `capability` | Capability extension | AI augments what this particular user can learn, analyze, write, design, or do, grounded in disclosed aspirations or capabilities. |
| L2 | `owned_project` | Project/possession extension | AI recursively co-creates an explicitly or compellingly owned venture, possession, creative production, or consequential project bearing the user's purposes or identity. |
| L3 | `self_representation` | Representational extension | AI represents the actual user's identity, relationship, aspiration, voice, or possible self symbolically, and the user negotiates that representation. |
| L4 | `self_assessment` | Reflexive extension | An AI-produced assessment or formulation feeds back into how the user understands abilities, preferences, identity, needs, or possible self. |
| L5 | `possible_self_enactment` | Enacted extension | An AI-configured possible self or self-understanding recursively organizes consequential intended choices or actions in lived or marketplace arrangements. |

# L0 — Instrumental task

Typical cases include code debugging, fictional storytelling, generic rewriting, translation, or work on an externally supplied advertising brief. Iterative revision can produce [artifact recursion](/ontology/artifact-recursion.md) without extension of self.

# L1 — Capability extension

The user must be particularized through an aspiration, existing capability, learning need, or consequential task. AI scaffolds agency or competence, but the interaction lacks a sufficiently evidenced identity-bearing project or recursive self-representation.

Example: iterative troubleshooting of the user's news-labeling website is an L1 potential because AI becomes part of what the user can build and repair, while no identity representation is negotiated.

# L2 — Project/possession extension

Ownership or a compelling user–project link must be evidenced; merely requesting an artifact is insufficient. A project can be entrepreneurial, occupational, educational, technological, or creative. Fictional or client work remains L0 without evidence that it is also the user's identity-bearing project.

Example: recursively configuring the user's multi-device workstation and evaluating components is a strong L2 case.

# L3 — Representational extension

The symbolic object must represent the actual user, relationship, aspiration, voice, or possible self. A fictional character is not the user without explicit evidence.

Example: negotiating a wedding image of the user, spouse, and cat is L3.

# L4 — Reflexive extension

The AI does more than represent: its interpretation becomes an input to the consumer's self-understanding. The user must respond to the assessment as being about them, rather than merely requesting a profile or quiz result.

# L5 — Enacted extension

The AI-configured self becomes consequential for intended real-world arrangements such as housing, mobility, relationships, finance, health, or lifestyle. The current rubric permits clearly intended decisions and actions; completed behavior need not be externally verified, but lack of enactment should be noted during human review.

Example: the Manila conversation uses an AI-configured independent LGBTQ+ urban possible self to organize neighborhood, affordability, mobility, social-belonging, and family-communication decisions.

# Boundary rule

L0–L2 can be recursive and theoretically important, but under v5 only L3–L5 are eligible for the `clear` label. See [classification labels](/ontology/classification-labels.md).

# Outlook beyond v5

The current ontology and production instrument end at L5. A prospective **L6 delegated/agentic extension** is documented separately as an [outlook for future developments](l6-agentic-extension-outlook.md). L6 is not a v5 code, no current case should be assigned to it, and adding it would require a new measurement version.
