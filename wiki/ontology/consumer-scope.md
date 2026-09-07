---
type: Concept
title: Consumer Scope
description: Broad consumer-research relevance is a descriptive domain tag and never a gate on extension classification.
tags: [consumer-relevance, jcr, inclusion, domain]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: draft
sources:
  - id: audit-rubric
    resource: ../../scripts/audit_long_conversations_gemma.py
    title: Gemma v5 audit rubric
---

# Definition

`consumption=yes` applies when an interaction contains a substantively analyzable consumption, service-use, learning, prosumption, marketplace, identity, or AI-use process beyond a purely impersonal fact request.[^audit-rubric]

The scope deliberately includes consumption of:

* AI services and AI-generated outputs;
* education, learning, and capability scaffolding;
* marketplace information, products, brands, and platforms;
* advice and expert systems;
* creative systems and prosumption;
* personal, relational, entrepreneurial, occupational, and health-related resources.

Professional or educational contexts are not excluded merely because the activity occurs at work or in study. They are coded as contexts, not as disqualifiers.

# Crucial non-equivalence

Consumer relevance does not imply self-extension. Mere AI use, repeated prompting, or consumption of a service can remain [L0 instrumental task](/ontology/levels-of-extension.md#l0--instrumental-task). The `consumption` field never determines the recursive label.

# Context tags

The v5 classifier assigns one primary context: `personal`, `relational`, `educational`, `entrepreneurial`, `occupational`, `creative`, `health`, `mixed`, or `other`. `mixed` is used when two or more contexts are equally central.

[^audit-rubric]: Gemma v5 audit rubric
