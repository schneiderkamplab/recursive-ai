---
type: Review Protocol
title: Human-Guided Manual Review
description: Procedure for adjudicating automated candidates and preserving qualitative evidence in JSONL.
tags: [manual-review, qualitative-analysis, adjudication, evidence]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: draft
sources:
  - id: clear-evidence
    resource: ../../classification/manually_reviewed_clear_examples.jsonl
    title: Manually reviewed clear examples
  - id: potential-evidence
    resource: ../../classification/manually_reviewed_potential_examples.jsonl
    title: Manually reviewed potential examples
  - id: negative-evidence
    resource: ../../classification/manually_reviewed_none_examples.jsonl
    title: Manually reviewed negative examples
---

# Review sequence

1. Retrieve the complete source conversation rather than relying on truncated previews or model evidence labels.
2. Segment topic shifts so a later unrelated segment neither erases nor falsely completes an earlier chain.
3. Reconstruct the best stage sequence from the transcript.
4. Distinguish user uptake from generic continuation and self/project reflection from mere compliance.
5. Assign the highest defensible [extension level](/ontology/levels-of-extension.md).
6. Apply the [recursive label rules](/ontology/classification-labels.md).
7. Record uncertainty, alternate interpretations, and theoretically valuable boundary features.

# Evidence record

Each manually reviewed JSONL record should include:

* conversation, dataset, and source identifiers;
* corpus and automated-audit references;
* automated and manual labels;
* level, locus, context, confidence, and review priority;
* a brief summary;
* stage-by-stage evidence and interpretation;
* reasons for the classification;
* reasons it is or is not self-extension;
* comments about ambiguity, factual errors, topic discontinuities, or theoretical use.

# Interpretive authority

Manual labels override automated labels for reported case findings. The automated record remains unchanged to preserve model-performance evidence. Corrections are added to the manual evidence files and summarized in the [evidence wiki](/evidence/).

# Privacy and inference restraint

Do not infer latent identity, sexuality, health, fetish, or other sensitive attributes from unusual requested content alone. Report only what is necessary for the analytic construct, using conversation IDs rather than usernames.
