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

The v5 automated audit is stopped at a validated 36,285-record append-only checkpoint out of the 44,142-conversation corpus, with zero recorded errors. This is also the latest fully reconciled reporting boundary: automated screening retrieved 5,344 clear or potential candidates, all of which were manually adjudicated exactly once. Manual campaign outcomes are 312 clear, 4,847 potential, and 185 none; their level distribution is L0=185, L1=2,466, L2=2,015, L3=420, L4=173, and L5=85. The separate calibration record is excluded. Process figures are frozen consistently at line 36,285. The manuscript and complete L3–L5 appendices remain at their earlier documented generation boundary and must be regenerated before their numerical claims are treated as current.

## Provenance

This bundle follows [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md). Concepts derived from project files identify those files in `sources`; interpretive concepts remain `draft` until the research team verifies them.
