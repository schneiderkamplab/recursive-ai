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

The v5 automated audit resumed from the append-only 33,346-of-44,142 checkpoint on 2026-09-07 with zero recorded errors, using the refactored production script under `scripts/`. The latest fully reconciled reporting boundary is line 32,747: all 5,054 automated clear or potential candidates through that boundary have been manually adjudicated exactly once. The 599 conversations screened between that boundary and the restart checkpoint add 54 candidates awaiting review. Manual outcomes remain 280 clear, 4,622 potential, and 152 none; the separate calibration record is excluded. The current paper and appendices deliberately use the frozen 33,346-record audit state, while the resumed audit continues append-only toward corpus completion.

## Provenance

This bundle follows [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md). Concepts derived from project files identify those files in `sources`; interpretive concepts remain `draft` until the research team verifies them.
