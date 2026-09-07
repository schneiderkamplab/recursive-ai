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

The v5 automated audit is running again from the fully reconciled 34,389-record checkpoint toward the 44,142-conversation corpus, with zero recorded errors at restart verification. Through line 34,389, automated screening retrieved 5,185 clear or potential candidates, all of which were manually adjudicated exactly once. Manual campaign outcomes at that boundary are 299 clear, 4,719 potential, and 167 none; their level distribution is L0=167, L1=2,418, L2=1,943, L3=408, L4=166, and L5=83. The separate calibration record is excluded. The process figures report this fully reconciled boundary; records appended after it require later candidate review and figure regeneration. The current paper and appendices remain deliberately frozen at the earlier 33,346-record state and should be regenerated when a new manuscript checkpoint is desired.

## Provenance

This bundle follows [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md). Concepts derived from project files identify those files in `sources`; interpretive concepts remain `draft` until the research team verifies them.
