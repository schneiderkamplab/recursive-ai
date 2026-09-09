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

The canonical v5 corpus now contains 91,590 conversations. Its original 44,142-record tranche has been screened with zero recorded errors: automated screening retrieved 6,006 clear or potential candidates, and every one was manually adjudicated exactly once. Outcomes for that completed tranche are 344 clear, 5,426 potential, and 236 none; their level distribution is L0=236, L1=2,726, L2=2,273, L3=469, L4=200, and L5=102. The separate calibration record is excluded. The 47,448 exact-deduplicated additions are pending automated v5 screening and subsequent manual adjudication; they must not yet be included in substantive campaign outcome counts.

## Provenance

This bundle follows [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md). Concepts derived from project files identify those files in `sources`; interpretive concepts remain `draft` until the research team verifies them.
