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

The v5 automated audit is stopped at 34,389 of 44,142 conversations with zero recorded errors. The append-only output contains 34,389 unique, parseable conversation IDs with no duplicates. Automated screening has provisionally retrieved 5,185 clear or potential candidates. The latest fully reconciled reporting boundary is line 32,747: all 5,054 candidates through that boundary have been manually adjudicated exactly once; 131 later candidates await review. Manual campaign outcomes remain 280 clear, 4,622 potential, and 152 none, with the separate calibration record excluded. The current paper and appendices deliberately use the earlier frozen 33,346-record state and should be regenerated when a new reporting checkpoint is desired.

## Provenance

This bundle follows [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md). Concepts derived from project files identify those files in `sources`; interpretive concepts remain `draft` until the research team verifies them.
