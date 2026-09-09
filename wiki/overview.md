---
type: Research Program
title: Recursive AI-Extended Self Audit
description: Research design for detecting levels and recursive patterns of consumer self-extension in public consumer–AI conversations.
tags: [consumer-research, ai-extended-self, recursive-extension, qualitative-research, machine-learning]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: draft
sources:
  - id: audit-script
    resource: ../scripts/audit_long_conversations_gemma.py
    title: Gemma v5 exhaustive audit implementation
  - id: corpus-manifest
    resource: ../classification/long_conversations_manifest.json
    title: Normalized long-conversation corpus manifest
---

# Purpose

The project asks whether naturally occurring, extended interactions with generative AI reveal processes in which consumers distribute, negotiate, revise, or enact aspects of self through AI. It connects Belk's extended-self tradition and later digital extensions with interactional evidence from consumer–AI transcripts.

# Unit of analysis

The unit is one normalized conversation containing at least ten user messages and ten assistant messages. A conversation may contain multiple topic segments. Each contiguous segment is considered independently, and the conversation receives the highest directly evidenced [level of extension](/ontology/levels-of-extension.md). A later unrelated topic does not erase a completed earlier process.

# Analytic distinction

Three dimensions must remain separate:

1. **Consumer relevance** describes whether the interaction is substantively analyzable as consumption, service use, learning, prosumption, marketplace practice, identity work, or AI use.
2. **Extension level** describes the proximity of the AI-mediated process to the consumer's self, from instrumental task performance to enacted possible selves.
3. **Recursive label** describes the evidential completeness of a process, not its level or importance.

See [consumer scope](/ontology/consumer-scope.md), [levels](/ontology/levels-of-extension.md), and [labels](/ontology/classification-labels.md).

# Research orientation

Automated screening is recall-oriented for `potential` cases and precision-oriented for `clear` cases. Human-guided qualitative analysis remains authoritative for theoretical interpretation, boundary adjudication, and reconstruction of evidence chains. The model is a retrieval and triage instrument, not the final theorist.

# Current corpus

The expanded canonical v5 corpus contains 91,590 conversations and 3,971,371,212 characters. Its original 44,142-record tranche comes from WildChat-1M, LMSYS-Chat-1M, ThoughtTrace, and the ChatGPT-RealUser-2.2M preview; 47,448 exact-deduplicated additions come from ShareGPT-X, PRISM Alignment, ShareChat, and the non-overlapping portion of WildChat-4.8M.[^corpus-manifest]

[^corpus-manifest]: Normalized long-conversation corpus manifest

# Related concepts

* [Recursive stages](/ontology/recursive-stages.md)
* [Artifact recursion](/ontology/artifact-recursion.md)
* [Automated audit](/workflow/automated-audit.md)
* [Manual review](/workflow/manual-review.md)
* [Methodological decisions](/decisions/)
