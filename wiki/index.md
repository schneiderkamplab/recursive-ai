---
okf_version: "0.2"
---

# Recursive AI-Extended Self Audit

This Open Knowledge Format bundle documents the concepts, prompts, data, implementation, and interpretive decisions for the recursive AI-extended-self audit of public consumer–AI conversation corpora.

## Start here

* [Research program](overview.md) - Purpose, research question, and unit of analysis.
* [Ontology](ontology/) - Extension levels, recursive stages, consumer scope, labels, and boundaries.
* [Prompts](prompts/) - Exact v5 audit rubric, output schema, and continuation protocol.
* [Workflow](workflow/) - Corpus construction, automated classification, and human review.
* [Evidence](evidence/) - Manually adjudicated clear, potential, and negative cases.
* [Decisions](decisions/) - Methodological choices and their consequences.
* [References](references/) - Canonical code, datasets, outputs, and external standards.

## Bundle status

The v5 automated audit is running toward the 44,142-conversation corpus with zero recorded errors. Line 42,034 is the latest fully reconciled reporting boundary: automated screening retrieved 5,834 clear or potential candidates, all of which were manually adjudicated exactly once. Manual campaign outcomes there are 337 clear, 5,274 potential, and 223 none; their level distribution is L0=223, L1=2,635, L2=2,221, L3=464, L4=193, and L5=98. The separate calibration record is excluded. Process figures, the manuscript draft, and the complete clear L3–L5 appendices are frozen consistently at line 42,034; records appended after that line require later manual reconciliation and regeneration.

## Provenance

This bundle follows [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md). Concepts derived from project files identify those files in `sources`; interpretive concepts remain `draft` until the research team verifies them.
